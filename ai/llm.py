"""Provider-agnostic LLM access with a deterministic fallback.

Three design constraints drove this:

1. **Grounding.** The model is never asked to supply a number. Every figure is
   computed by the wallet engine, passed in as a fact block, and the model is
   instructed to reuse those figures verbatim. It is doing language, not
   arithmetic. `verify_grounding` checks the output afterwards.

2. **It must never break a live demo.** If no provider is configured, the key is
   wrong, or the network is down, callers fall back to deterministic templates
   rather than showing an error. Judging happens on a laptop in a room with
   unknown wifi.

3. **Latency.** One of the brief's bonus areas is reducing the latency that
   orchestration layers introduce. Responses are cached by prompt hash, so a
   repeated question on stage is instant, and the whole path is a single call
   rather than an agent hierarchy.
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parents[1]
PROMPT_LOG_DIR = ROOT / "prompts" / "logs"


class LLMUnavailable(RuntimeError):
    """No provider is configured, or the call failed. Callers fall back."""


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    latency_ms: float
    cached: bool = False
    grounding_warnings: list[str] = field(default_factory=list)


def _load_dotenv() -> None:
    """Read .env without requiring python-dotenv to be importable."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

_CACHE: dict[str, LLMResponse] = {}

# Cache survives process restarts. Gemini's free tier is quota'd per model per
# DAY, so re-running the dashboard or the notebook would otherwise exhaust the
# allowance on answers we already have. Disk cache also means a demo keeps
# working after the quota is gone.
CACHE_DIR = ROOT / "prompts" / "cache"


def _cache_key(system: str, prompt: str, model: str) -> str:
    return hashlib.sha256(f"{model}\x00{system}\x00{prompt}".encode()).hexdigest()


def _disk_cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def _read_disk_cache(key: str) -> LLMResponse | None:
    import json

    path = _disk_cache_path(key)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return LLMResponse(
            text=payload["text"],
            provider=payload["provider"],
            model=payload["model"],
            latency_ms=float(payload.get("latency_ms", 0.0)),
            cached=True,
            grounding_warnings=payload.get("grounding_warnings", []),
        )
    except (OSError, ValueError, KeyError):
        return None


def _write_disk_cache(key: str, response: LLMResponse) -> None:
    import json

    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _disk_cache_path(key).write_text(
            json.dumps(
                {
                    "text": response.text,
                    "provider": response.provider,
                    "model": response.model,
                    "latency_ms": response.latency_ms,
                    "grounding_warnings": response.grounding_warnings,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass  # caching must never break a call


def active_provider() -> str:
    """Which provider will be used, given the current environment."""
    declared = os.environ.get("GENAI_PROVIDER", "").strip().lower()

    if declared in {"gemini", "google"} and os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if declared == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if declared == "openai" and os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if declared == "ollama":
        return "ollama"

    # Nothing declared — fall back to whichever key happens to be present.
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "none"


def _model_for(provider: str) -> str:
    override = os.environ.get("GENAI_MODEL", "").strip()
    if override:
        return override
    return {
        # Gemini free tier is quota'd per model per DAY (20/day on the standard
        # flash models), so the choice matters more than it looks. A lite model
        # gets a larger daily allowance and is more than capable of rewriting a
        # supplied fact block. Note that pinned names are also withdrawn on a
        # rolling basis — gemini-2.0-flash and gemini-2.5-flash were both already
        # gone when this was wired up — so check availability before changing it.
        "gemini": "gemini-3.1-flash-lite",
        "anthropic": "claude-sonnet-5",
        "openai": "gpt-4o-mini",
        "ollama": os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
    }.get(provider, "none")


# --- provider implementations -------------------------------------------

def _call_gemini(system: str, prompt: str, model: str, max_tokens: int) -> str:
    """Current google-genai SDK, falling back to the retired one if that is all
    that is installed. google.generativeai is end-of-life and its model names
    (gemini-2.0-flash and earlier) have already been withdrawn."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        # Current Gemini flash models reason before answering, and those thinking
        # tokens are charged against max_output_tokens. A budget that looks ample
        # can therefore be consumed entirely by thinking, returning an empty
        # string with finish_reason=MAX_TOKENS. This task is rewriting supplied
        # facts rather than reasoning, so thinking is switched off: it removes the
        # failure mode, roughly halves latency, and stretches the free-tier quota.
        def build_config(disable_thinking: bool):
            cfg = types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=0.2,
            )
            if disable_thinking:
                try:
                    cfg.thinking_config = types.ThinkingConfig(thinking_budget=0)
                except (AttributeError, TypeError):
                    pass  # older SDK
            return cfg

        try:
            result = client.models.generate_content(
                model=model, contents=prompt, config=build_config(True)
            )
        except Exception as exc:  # noqa: BLE001
            # Some models reject thinking_budget=0 with 400 INVALID_ARGUMENT.
            # Retry letting the model think rather than failing the request.
            if "400" not in str(exc) and "INVALID_ARGUMENT" not in str(exc):
                raise
            result = client.models.generate_content(
                model=model, contents=prompt, config=build_config(False)
            )

        text = (result.text or "").strip()
        if not text and result.candidates:
            reason = getattr(result.candidates[0], "finish_reason", None)
            if reason is not None and "MAX_TOKENS" in str(reason):
                raise LLMUnavailable(
                    f"{model} hit the output limit before producing text "
                    f"(max_tokens={max_tokens}); raise max_tokens."
                )
        return text
    except ImportError:
        import google.generativeai as legacy

        legacy.configure(api_key=os.environ["GEMINI_API_KEY"])
        chat = legacy.GenerativeModel(model, system_instruction=system)
        result = chat.generate_content(
            prompt,
            generation_config={"max_output_tokens": max_tokens, "temperature": 0.2},
        )
        return (result.text or "").strip()


def _call_anthropic(system: str, prompt: str, model: str, max_tokens: int) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.2,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text").strip()


def _call_openai(system: str, prompt: str, model: str, max_tokens: int) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    result = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return (result.choices[0].message.content or "").strip()


def _call_ollama(system: str, prompt: str, model: str, max_tokens: int) -> str:
    """Local model over Ollama's HTTP API — no SDK dependency."""
    import json
    import urllib.request

    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    payload = json.dumps(
        {
            "model": model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": max_tokens},
        }
    ).encode()
    request = urllib.request.Request(
        f"{host}/api/generate", data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read()).get("response", "").strip()


_DISPATCH = {
    "gemini": _call_gemini,
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "ollama": _call_ollama,
}

_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_SECONDS = (4.0, 12.0)

_RATE_LIMIT_MARKERS = (
    "429",
    "rate limit",
    "ratelimit",
    "resource_exhausted",
    "resource exhausted",
    "quota",
    "too many requests",
    "overloaded",
    "503",
)


def _is_rate_limit(exc: Exception) -> bool:
    blob = f"{type(exc).__name__} {exc}".lower()
    return any(marker in blob for marker in _RATE_LIMIT_MARKERS)


# --- grounding check -----------------------------------------------------

_NUMBER_RE = re.compile(r"R\s?[\d][\d,]*\.?\d*\s?(?:T|B|M|bn|m|tn)?|\d+\.?\d*\s?%")


def verify_grounding(text: str, allowed_facts: str) -> list[str]:
    """Flag any figure in the output that did not appear in the fact block.

    This is a guardrail, not a proof: it catches the failure mode we actually
    care about, which is a model inventing a plausible-looking rand amount.
    """
    allowed = set(_NUMBER_RE.findall(allowed_facts))
    normalised_allowed = {a.replace(" ", "").lower() for a in allowed}

    warnings = []
    for found in _NUMBER_RE.findall(text):
        if found.replace(" ", "").lower() not in normalised_allowed:
            warnings.append(found.strip())
    return sorted(set(warnings))


# --- public entry point --------------------------------------------------

def generate(
    system: str,
    prompt: str,
    *,
    max_tokens: int = 900,
    allowed_facts: str | None = None,
    log_name: str | None = None,
) -> LLMResponse:
    """Run one grounded completion. Raises LLMUnavailable so callers can fall back."""
    provider = active_provider()
    if provider == "none":
        raise LLMUnavailable(
            "No GenAI provider configured. Set GENAI_PROVIDER and the matching API "
            "key in .env (see .env.example), or run a local model with "
            "GENAI_PROVIDER=ollama."
        )

    model = _model_for(provider)
    key = _cache_key(system, prompt, model)

    hit = _CACHE.get(key) or _read_disk_cache(key)
    if hit is not None:
        _CACHE[key] = hit
        return LLMResponse(
            text=hit.text,
            provider=hit.provider,
            model=hit.model,
            latency_ms=hit.latency_ms,
            cached=True,
            grounding_warnings=hit.grounding_warnings,
        )

    started = time.perf_counter()
    text = ""
    last_error: Exception | None = None

    # Free tiers rate-limit aggressively per minute, and generating several
    # briefings in a row trips it. A short backoff turns a visible fallback into
    # a slightly slower correct answer, which matters when demoing live.
    for attempt in range(_MAX_ATTEMPTS):
        try:
            text = _DISPATCH[provider](system, prompt, model, max_tokens)
            last_error = None
            break
        except LLMUnavailable:
            raise
        except Exception as exc:  # noqa: BLE001 - any provider error means "retry, then fall back"
            last_error = exc
            if not _is_rate_limit(exc) or attempt == _MAX_ATTEMPTS - 1:
                break
            time.sleep(_RETRY_BACKOFF_SECONDS[attempt])

    if last_error is not None:
        raise LLMUnavailable(
            f"{provider} call failed: {type(last_error).__name__}: {last_error}"
        ) from last_error

    if not text:
        raise LLMUnavailable(f"{provider} returned an empty response")

    response = LLMResponse(
        text=text,
        provider=provider,
        model=model,
        latency_ms=(time.perf_counter() - started) * 1000.0,
        grounding_warnings=verify_grounding(text, allowed_facts) if allowed_facts else [],
    )
    _CACHE[key] = response
    _write_disk_cache(key, response)

    if log_name:
        _log_exchange(log_name, system, prompt, response)
    return response


def _log_exchange(name: str, system: str, prompt: str, response: LLMResponse) -> None:
    """Persist prompt and output. The brief requires evidence of GenAI usage."""
    try:
        PROMPT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
        path = PROMPT_LOG_DIR / f"{safe}.md"
        path.write_text(
            "\n".join(
                [
                    f"# {name}",
                    "",
                    f"- provider: `{response.provider}`",
                    f"- model: `{response.model}`",
                    f"- latency: {response.latency_ms:.0f} ms",
                    f"- grounding warnings: {response.grounding_warnings or 'none'}",
                    "",
                    "## System prompt",
                    "",
                    "```text",
                    system,
                    "```",
                    "",
                    "## User prompt",
                    "",
                    "```text",
                    prompt,
                    "```",
                    "",
                    "## Output",
                    "",
                    response.text,
                    "",
                ]
            ),
            encoding="utf-8",
        )
    except OSError:
        pass  # logging must never break a demo


def provider_status() -> dict:
    """Small diagnostic surfaced in the dashboard so the AI path is visible."""
    provider = active_provider()
    try:
        on_disk = len(list(CACHE_DIR.glob("*.json")))
    except OSError:
        on_disk = 0
    return {
        "provider": provider,
        "model": _model_for(provider) if provider != "none" else None,
        "live": provider != "none",
        "cachedResponses": len(_CACHE),
        "cachedOnDisk": on_disk,
    }
