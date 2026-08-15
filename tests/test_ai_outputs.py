"""Explainability and briefing output invariants.

These guard the property that matters most for the GenAI component: every
sentence shown to a banker is derived from a computed field, never invented.
"""

from __future__ import annotations

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
