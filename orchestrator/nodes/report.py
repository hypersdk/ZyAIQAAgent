"""Generate QA report."""

from __future__ import annotations

import os

from agents.reporter.agent import build_report
from orchestrator.state import PipelineState


def generate_report(state: PipelineState) -> PipelineState:
    """Build HTML and text report from test results."""
    test_results = state.get("test_results")
    if not test_results:
        return {**state, "error": "No test results to report"}

    use_llm = os.environ.get("ENABLE_LLM_REPORT", "true").lower() == "true"
    report = build_report(
        test_results=test_results,
        source=state.get("source", "local"),
        failure_analysis=state.get("failure_analysis"),
        autofix_suggestions=state.get("autofix_suggestions"),
        use_llm=use_llm,
    )

    return {
        **state,
        "report_path": report.html_path,
        "report_summary": report.summary,
    }
