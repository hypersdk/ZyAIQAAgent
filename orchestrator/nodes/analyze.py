"""Analyze test failures."""

from __future__ import annotations

import os

from agents.analyzer.agent import analyze_failures
from orchestrator.state import PipelineState


def analyze_failures_node(state: PipelineState) -> PipelineState:
    """Run failure analysis on test results."""
    test_results = state.get("test_results")
    if not test_results or test_results.all_passed:
        return {**state, "failure_analysis": None}

    use_llm = os.environ.get("ENABLE_LLM_ANALYSIS", "false").lower() == "true"
    analysis = analyze_failures(test_results, use_llm=use_llm)
    return {**state, "failure_analysis": analysis}
