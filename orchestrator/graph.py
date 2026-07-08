"""LangGraph pipeline definition."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from orchestrator.nodes.analyze import analyze_failures_node
from orchestrator.nodes.execute import execute_tests
from orchestrator.nodes.fetch import fetch_requirements
from orchestrator.nodes.generate import generate_tests
from orchestrator.nodes.notify import notify_channels
from orchestrator.nodes.parse import parse_requirements
from orchestrator.nodes.report import generate_report
from orchestrator.state import PipelineState


def route_on_results(state: PipelineState) -> str:
    """Branch on test pass/fail."""
    test_results = state.get("test_results")
    if test_results and not test_results.all_passed and test_results.failed > 0:
        return "fail"
    return "pass"


def build_graph() -> StateGraph:
    """Build and compile the QA pipeline graph."""
    graph = StateGraph(PipelineState)

    graph.add_node("fetch", fetch_requirements)
    graph.add_node("parse", parse_requirements)
    graph.add_node("generate", generate_tests)
    graph.add_node("execute", execute_tests)
    graph.add_node("analyze", analyze_failures_node)
    graph.add_node("report", generate_report)
    graph.add_node("notify", notify_channels)

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "parse")
    graph.add_edge("parse", "generate")
    graph.add_edge("generate", "execute")
    graph.add_conditional_edges(
        "execute",
        route_on_results,
        {"pass": "report", "fail": "analyze"},
    )
    graph.add_edge("analyze", "report")
    graph.add_edge("report", "notify")
    graph.add_edge("notify", END)

    return graph


def get_compiled_graph():
    """Return compiled LangGraph application."""
    return build_graph().compile()
