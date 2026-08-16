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


def _cache_key(system: str, prompt: str, model: str) -> str:
    return hashlib.sha256(f"{model}\x00{system}\x00{prompt}".encode()).hexdigest()


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
        "gemini": "gemini-2.0-flash",
        "anthropic": "claude-sonnet-5",
        "openai": "gpt-4o-mini",
        "ollama": os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
    }.get(provider, "none")


# --- provider implementations -------------------------------------------

def _call_gemini(system: str, prompt: str, model: str, max_tokens: int) -> str:
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    client = genai.GenerativeModel(model, system_instruction=system)
    result = client.generate_content(
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
    if key in _CACHE:
        hit = _CACHE[key]
        return LLMResponse(
            text=hit.text,
            provider=hit.provider,
            model=hit.model,
            latency_ms=hit.latency_ms,
            cached=True,
            grounding_warnings=hit.grounding_warnings,
        )

    started = time.perf_counter()
    try:
        text = _DISPATCH[provider](system, prompt, model, max_tokens)
    except LLMUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001 - any provider error means "fall back"
        raise LLMUnavailable(f"{provider} call failed: {type(exc).__name__}: {exc}") from exc

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
    return {
        "provider": provider,
        "model": _model_for(provider) if provider != "none" else None,
        "live": provider != "none",
        "cachedResponses": len(_CACHE),
    }
