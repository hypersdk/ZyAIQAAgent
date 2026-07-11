"""Analyze coverage gaps against existing Playwright tests."""

from __future__ import annotations

from agents.coverage.gap import analyze_gaps
from orchestrator.coverage_config import coverage_expansion_enabled
from orchestrator.state import PipelineState


def gap_analyze(state: PipelineState) -> PipelineState:
    """Find uncovered routes/pages/docs from the discovery inventory."""
    if state.get("error"):
        return state

    inventory = state.get("coverage_inventory", [])
    if not coverage_expansion_enabled(state) and not inventory:
        return {**state, "coverage_gaps": []}

    gaps, covered = analyze_gaps(inventory)

    metadata = dict(state.get("metadata", {}))
    metadata["coverage_gaps_remaining"] = len(gaps)
    metadata["coverage_covered_count"] = len(covered)

    return {
        **state,
        "coverage_gaps": gaps,
        "metadata": metadata,
    }
