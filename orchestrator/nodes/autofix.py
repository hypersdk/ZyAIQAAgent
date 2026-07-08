"""Autofix node — suggest selector repairs after failure analysis."""

from __future__ import annotations

import os

from agents.autofix.agent import suggest_fixes_from_results
from orchestrator.state import PipelineState


def autofix_node(state: PipelineState) -> PipelineState:
    """Generate autofix suggestions when ENABLE_AUTOFIX=true."""
    if os.environ.get("ENABLE_AUTOFIX", "false").lower() != "true":
        return state

    test_results = state.get("test_results")
    if not test_results or test_results.all_passed:
        return state

    suggestions = suggest_fixes_from_results(
        test_results=test_results,
        failure_analysis=state.get("failure_analysis"),
    )
    return {**state, "autofix_suggestions": suggestions}
