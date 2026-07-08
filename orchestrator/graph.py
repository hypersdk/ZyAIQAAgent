"""LangGraph pipeline definition."""

from __future__ import annotations

import os

from langgraph.graph import END, StateGraph

from orchestrator.nodes.analyze import analyze_failures_node
from orchestrator.nodes.api_validate import api_validate
from orchestrator.nodes.autofix import autofix_node
from orchestrator.nodes.execute import execute_tests
from orchestrator.nodes.fetch import fetch_requirements
from orchestrator.nodes.generate import generate_tests
from orchestrator.nodes.log_analyze import log_analyze
from orchestrator.nodes.notify import notify_channels
from orchestrator.nodes.parse import parse_requirements
from orchestrator.nodes.regression import regression_check
from orchestrator.nodes.report import generate_report
from orchestrator.state import PipelineState


def route_on_results(state: PipelineState) -> str:
    """Branch on test pass/fail including regression, API, and log issues."""
    test_results = state.get("test_results")
    if not test_results:
        return "pass"

    has_failures = test_results.failed > 0
    regression_failed = any(d.status == "fail" for d in test_results.regression_diffs)
    api_failed = any(not v.passed for v in test_results.api_validations)
    log_failed = any(i.severity == "error" for i in test_results.log_issues)

    if has_failures or regression_failed or api_failed or log_failed:
        return "fail"
    return "pass"


def route_after_analyze(state: PipelineState) -> str:
    """Optionally run autofix after failure analysis."""
    if os.environ.get("ENABLE_AUTOFIX", "false").lower() == "true":
        return "autofix"
    return "report"


def build_graph() -> StateGraph:
    """Build and compile the QA pipeline graph."""
    graph = StateGraph(PipelineState)

    graph.add_node("fetch", fetch_requirements)
    graph.add_node("parse", parse_requirements)
    graph.add_node("generate", generate_tests)
    graph.add_node("execute", execute_tests)
    graph.add_node("regression", regression_check)
    graph.add_node("api_validate", api_validate)
    graph.add_node("log_analyze", log_analyze)
    graph.add_node("analyze", analyze_failures_node)
    graph.add_node("autofix", autofix_node)
    graph.add_node("report", generate_report)
    graph.add_node("notify", notify_channels)

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "parse")
    graph.add_edge("parse", "generate")
    graph.add_edge("generate", "execute")
    graph.add_edge("execute", "regression")
    graph.add_edge("regression", "api_validate")
    graph.add_edge("api_validate", "log_analyze")
    graph.add_conditional_edges(
        "log_analyze",
        route_on_results,
        {"pass": "report", "fail": "analyze"},
    )
    graph.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {"autofix": "autofix", "report": "report"},
    )
    graph.add_edge("autofix", "report")
    graph.add_edge("report", "notify")
    graph.add_edge("notify", END)

    return graph


def get_compiled_graph():
    """Return compiled LangGraph application."""
    return build_graph().compile()
