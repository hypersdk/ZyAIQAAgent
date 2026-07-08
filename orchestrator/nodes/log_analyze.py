"""Browser log analysis node."""

from __future__ import annotations

from agents.logs.analyzer import analyze_test_results
from orchestrator.state import PipelineState


def log_analyze(state: PipelineState) -> PipelineState:
    """Analyze console and network logs from test results."""
    test_results = state.get("test_results")
    if not test_results:
        return state

    issues = analyze_test_results(test_results)
    test_results.log_issues = issues
    return {**state, "test_results": test_results, "log_issues": issues}
