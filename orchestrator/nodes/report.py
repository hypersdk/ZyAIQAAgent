"""Generate QA report."""

from __future__ import annotations

import os

from agents.reporter.agent import build_report
from orchestrator.state import PipelineState


def generate_report(state: PipelineState) -> PipelineState:
    """Build HTML and text report from test results."""
    if state.get("error") and not state.get("test_results"):
        return state

    test_results = state.get("test_results")
    if not test_results:
        return {**state, "error": state.get("error") or "No test results to report"}

    use_llm = os.environ.get("ENABLE_LLM_REPORT", "true").lower() == "true"
    report = build_report(
        test_results=test_results,
        source=state.get("source", "local"),
        failure_analysis=state.get("failure_analysis"),
        autofix_suggestions=state.get("autofix_suggestions"),
        v8_coverage=state.get("v8_coverage"),
        use_llm=use_llm,
    )

    return {
        **state,
        "report_path": report.html_path,
        "pdf_report_path": report.pdf_path,
        "report_summary": report.summary,
    }
