"""Explainability and briefing output invariants.

These guard the property that matters most for the GenAI component: every
sentence shown to a banker is derived from a computed field, never invented.
"""

from __future__ import annotations

import pytest

from ai import llm
from models.explainability import (
    PITCH_BY_PILLAR,
    add_explainability_fields,
    build_briefing_payload,
    explain_client,
    pillar_gaps,
)


def test_pillar_gaps_returns_the_three_pillars(wallet_df):
    gaps = pillar_gaps(wallet_df.iloc[0])
    assert set(gaps) == {"Transactional", "FX", "Trade Finance"}


def test_pillar_gaps_are_non_negative(wallet_df):
    for _, row in wallet_df.iterrows():
        assert all(v >= 0 for v in pillar_gaps(row).values())


def test_explain_client_contains_client_name(wallet_df):
    row = wallet_df[wallet_df["client_id"] == "C001"].iloc[0]
    assert "Acme Mining Ltd" in explain_client(row)


def test_explain_client_reports_the_share_percentage(wallet_df):
    row = wallet_df.iloc[0]
    expected = f"{row['syn_share'] * 100:.1f}%"
    assert expected in explain_client(row)


def test_explain_client_names_the_largest_gap_pillar(wallet_df):
    row = wallet_df.iloc[0]
    top_pillar = max(pillar_gaps(row), key=pillar_gaps(row).get)
    assert top_pillar in explain_client(row)


def test_add_explainability_fields_populates_every_row(scored_df):
    enriched = add_explainability_fields(scored_df)
    assert enriched["why_signal"].str.len().gt(0).all()
    assert enriched["what_to_pitch"].str.len().gt(0).all()


def test_briefing_payload_has_the_shape_the_api_returns(wallet_df):
    payload = build_briefing_payload(wallet_df.iloc[0])
    assert set(payload) >= {
        "clientId",
        "summary",
        "keySignals",
        "recommendedAgenda",
        "risk",
        "sources",
    }
    assert payload["keySignals"]
    assert payload["recommendedAgenda"]


def test_briefing_pitch_matches_the_top_gap_pillar(wallet_df):
    row = wallet_df.iloc[0]
    top_pillar = max(pillar_gaps(row), key=pillar_gaps(row).get)
    payload = build_briefing_payload(row)
    assert payload["recommendedAgenda"][0] == PITCH_BY_PILLAR[top_pillar]


def test_briefing_cites_grounding_sources(wallet_df):
    payload = build_briefing_payload(wallet_df.iloc[0])
    assert any(s.startswith("client_id=") for s in payload["sources"])
    assert any(s.startswith("gap=") for s in payload["sources"])


# --- GenAI grounding guard ------------------------------------------------
#
# The point of the guard is to catch a model inventing a plausible-looking rand
# figure. These tests pin that behaviour without needing a live provider.

def test_grounding_accepts_figures_that_came_from_the_evidence():
    facts = "Estimated share of wallet: 2.3%\nUncaptured flow gap: R647.67B"
    text = "Syn Bank holds an estimated 2.3% of this client, leaving R647.67B uncaptured."
    assert llm.verify_grounding(text, facts) == []


def test_grounding_flags_an_invented_figure():
    facts = "Estimated share of wallet: 2.3%\nUncaptured flow gap: R647.67B"
    text = "Share is 2.3%, and we expect to win R99.9B within twelve months."
    assert "R99.9B" in llm.verify_grounding(text, facts)


def test_grounding_flags_a_silently_altered_percentage():
    facts = "Estimated share of wallet: 2.3%"
    text = "Syn Bank already holds 23% of this client."
    assert "23%" in llm.verify_grounding(text, facts)


def test_grounding_ignores_spacing_differences():
    facts = "Uncaptured flow gap: R647.67B"
    assert llm.verify_grounding("The gap is R 647.67B.", facts) == []


def test_no_provider_configured_raises_so_callers_can_fall_back(monkeypatch):
    for name in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GENAI_PROVIDER", "")
    assert llm.active_provider() == "none"
    with pytest.raises(llm.LLMUnavailable):
        llm.generate("system", "prompt")


def test_briefing_falls_back_to_deterministic_without_a_provider(monkeypatch):
    """The dashboard must still produce a usable briefing with no API key."""
    for name in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GENAI_PROVIDER", "")

    from ai.briefing import generate_briefing

    payload = generate_briefing("E09")
    assert payload["generatedBy"] == "deterministic"
    assert payload["summary"]
    assert payload["keySignals"]
    # The internal row must never reach the API response.
    assert "_row" not in payload
