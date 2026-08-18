# Copyright 2026 ZyvorAI Labs Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LangGraph pipeline definition."""

from __future__ import annotations

import functools
import os
from typing import Callable

from langgraph.graph import END, StateGraph

from orchestrator.nodes.analyze import analyze_failures_node
from orchestrator.nodes.api_validate import api_validate
from orchestrator.nodes.apply_autofix import apply_autofix_node
from orchestrator.nodes.autofix import autofix_node
from orchestrator.nodes.discover import discover_coverage
from orchestrator.nodes.evaluate_quality import evaluate_quality
from orchestrator.nodes.execute import execute_tests
from orchestrator.nodes.fetch import fetch_requirements
from orchestrator.nodes.gap_analyze import gap_analyze
from orchestrator.nodes.generate import generate_tests
from orchestrator.nodes.learn_skills import learn_skills_node
from orchestrator.nodes.log_analyze import log_analyze
from orchestrator.nodes.merge_results import merge_results
from orchestrator.nodes.notify import notify_channels
from orchestrator.nodes.parse import parse_requirements
from orchestrator.nodes.regression import regression_check
from orchestrator.nodes.report import generate_report
from orchestrator.nodes.v8_coverage import collect_v8_coverage_node
from orchestrator.observability.tracing import set_span_error, start_span
from orchestrator.state import PipelineState


def _traced(name: str, node: Callable[[PipelineState], PipelineState]) -> Callable[[PipelineState], PipelineState]:
    """Wraps a node function in a span named "pipeline.<name>" -- a no-op
    when tracing is disabled (see observability/tracing.py). Applied once
    per node here in build_graph() rather than inside each of the ~17 node
    modules, so none of them need to know tracing exists."""

    @functools.wraps(node)
    def wrapped(state: PipelineState) -> PipelineState:
        had_error = bool(state.get("error"))
        with start_span(f"pipeline.{name}") as span:
            result = node(state)
            new_error = result.get("error") if isinstance(result, dict) else None
            if new_error and not had_error:
                set_span_error(span, new_error)
            return result

    return wrapped


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
    metadata = state.get("metadata", {})
    max_retries = int(os.environ.get("AUTOFIX_MAX_RETRIES", "2"))
    if metadata.get("autofix_retries", 0) >= max_retries:
        return "report"
    if os.environ.get("ENABLE_AUTOFIX", "false").lower() == "true":
        return "autofix"
    return "report"


def route_after_apply_autofix(state: PipelineState) -> str:
    """Re-execute tests when patches were applied and retries remain."""
    if os.environ.get("ENABLE_AUTOFIX_APPLY", "false").lower() != "true":
        return "report"

    metadata = state.get("metadata", {})
    if not metadata.get("autofix_patches_applied"):
        return "report"

    max_retries = int(os.environ.get("AUTOFIX_MAX_RETRIES", "2"))
    if metadata.get("autofix_retries", 0) > max_retries:
        return "report"

    test_results = state.get("test_results")
    if test_results and test_results.all_passed:
        return "report"

    return "execute"


def build_graph() -> StateGraph:
    """Build and compile the QA pipeline graph."""
    graph = StateGraph(PipelineState)

    graph.add_node("fetch", _traced("fetch", fetch_requirements))
    graph.add_node("discover", _traced("discover", discover_coverage))
    graph.add_node("gap_analyze", _traced("gap_analyze", gap_analyze))
    graph.add_node("parse", _traced("parse", parse_requirements))
    graph.add_node("evaluate_quality", _traced("evaluate_quality", evaluate_quality))
    graph.add_node("generate", _traced("generate", generate_tests))
    graph.add_node("execute", _traced("execute", execute_tests))
    graph.add_node("regression", _traced("regression", regression_check))
    graph.add_node("api_validate", _traced("api_validate", api_validate))
    graph.add_node("log_analyze", _traced("log_analyze", log_analyze))
    graph.add_node("v8_coverage", _traced("v8_coverage", collect_v8_coverage_node))
    graph.add_node("merge_results", _traced("merge_results", merge_results))
    graph.add_node("analyze", _traced("analyze", analyze_failures_node))
    graph.add_node("autofix", _traced("autofix", autofix_node))
    graph.add_node("apply_autofix", _traced("apply_autofix", apply_autofix_node))
    graph.add_node("learn_skills", _traced("learn_skills", learn_skills_node))
    graph.add_node("report", _traced("report", generate_report))
    graph.add_node("notify", _traced("notify", notify_channels))

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "discover")
    graph.add_edge("discover", "gap_analyze")
    graph.add_edge("gap_analyze", "parse")
    graph.add_edge("parse", "evaluate_quality")
    graph.add_edge("evaluate_quality", "generate")
    graph.add_edge("generate", "execute")
    # regression/api_validate/log_analyze/v8_coverage each analyze a
    # different, independent slice of the same completed test run
    # (screenshots, HAR/network, console logs, JS coverage) — fan them out
    # in parallel instead of chaining them, then join at merge_results
    # before routing on the combined pass/fail state.
    graph.add_edge("execute", "regression")
    graph.add_edge("execute", "api_validate")
    graph.add_edge("execute", "log_analyze")
    graph.add_edge("execute", "v8_coverage")
    graph.add_edge("regression", "merge_results")
    graph.add_edge("api_validate", "merge_results")
    graph.add_edge("log_analyze", "merge_results")
    graph.add_edge("v8_coverage", "merge_results")
    graph.add_conditional_edges(
        "merge_results",
        route_on_results,
        {"pass": "learn_skills", "fail": "analyze"},
    )
    graph.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {"autofix": "autofix", "report": "report"},
    )
    graph.add_edge("autofix", "apply_autofix")
    graph.add_conditional_edges(
        "apply_autofix",
        route_after_apply_autofix,
        {"execute": "execute", "report": "learn_skills"},
    )
    graph.add_edge("learn_skills", "report")
    graph.add_edge("report", "notify")
    graph.add_edge("notify", END)

    return graph


def get_compiled_graph():
    """Return compiled LangGraph application."""
    return build_graph().compile()
