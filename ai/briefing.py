"""Briefing generation grounded strictly in computed wallet/opportunity tables."""

from __future__ import annotations

from ai.retrieval import retrieve_briefing


def generate_briefing(client_identifier: str) -> dict:
    payload, sources = retrieve_briefing(client_identifier)
    if payload is None:
        return {
            "clientId": client_identifier,
            "summary": "No grounded briefing is available for this client identifier.",
            "keySignals": [],
            "recommendedAgenda": [],
            "risk": None,
            "sources": [],
        }

    payload["sources"] = sources
    return payload
