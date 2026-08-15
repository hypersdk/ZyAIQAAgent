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

"""Regression-check for the parallel post-execution analysis fan-out.

regression/api_validate/log_analyze/v8_coverage run concurrently off of
`execute` (see orchestrator/graph.py) and join at `merge_results`. LangGraph
raises InvalidUpdateError if two nodes in the same superstep both write the
same state key without a reducer — these tests exercise the real subgraph to
prove the parallel branch is conflict-free and that results land correctly
on the shared `test_results` object afterwards.
"""

from __future__ import annotations

from unittest.mock import patch

from langgraph.graph import END, START, StateGraph

from agents.common.models import (
    ApiValidationResult,
    LogIssue,
    RegressionDiff,
    TestCaseResult,
    TestResult,
)
from orchestrator.nodes.api_validate import api_validate
from orchestrator.nodes.log_analyze import log_analyze
from orchestrator.nodes.merge_results import merge_results
from orchestrator.nodes.regression import regression_check
from orchestrator.nodes.v8_coverage import collect_v8_coverage_node
from orchestrator.state import PipelineState


def _build_fanout_graph():
    """Rebuild just the execute -> {analysis nodes} -> merge_results slice."""
    graph = StateGraph(PipelineState)
    graph.add_node("regression", regression_check)
    graph.add_node("api_validate", api_validate)
    graph.add_node("log_analyze", log_analyze)
    graph.add_node("v8_coverage", collect_v8_coverage_node)
    graph.add_node("merge_results", merge_results)
    graph.add_edge(START, "regression")
    graph.add_edge(START, "api_validate")
    graph.add_edge(START, "log_analyze")
    graph.add_edge(START, "v8_coverage")
    graph.add_edge("regression", "merge_results")
    graph.add_edge("api_validate", "merge_results")
    graph.add_edge("log_analyze", "merge_results")
    graph.add_edge("v8_coverage", "merge_results")
    graph.add_edge("merge_results", END)
    return graph.compile()


def test_fanout_runs_without_conflicting_writes_and_merges_results(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_REGRESSION", "true")
    monkeypatch.setenv("ENABLE_API_VALIDATION", "true")

    test_results = TestResult(
        passed=1, failed=0, total=1, cases=[TestCaseResult(title="t", status="passed")]
    )
    regression_diffs = [RegressionDiff(file="a.png", status="fail", diff_percent=5.0)]
    api_validations = [ApiValidationResult(url="/x", passed=False)]
    log_issues = [LogIssue(test_title="t", severity="error", source="console", message="boom")]

    with patch("orchestrator.nodes.regression._repo_root", return_value=tmp_path), patch(
        "orchestrator.nodes.regression.collect_screenshots_from_test_results", return_value=[]
    ), patch(
        "orchestrator.nodes.regression.compare_screenshots", return_value=regression_diffs
    ), patch(
        "orchestrator.nodes.api_validate._repo_root", return_value=tmp_path
    ), patch(
        "orchestrator.nodes.api_validate.validate_test_results", return_value=api_validations
    ), patch(
        "orchestrator.nodes.log_analyze.analyze_test_results", return_value=log_issues
    ), patch(
        "orchestrator.nodes.v8_coverage.collect_v8_coverage", return_value=None
    ):
        graph = _build_fanout_graph()
        final_state = graph.invoke({"test_results": test_results, "metadata": {}})

    merged = final_state["test_results"]
    assert merged.regression_diffs == regression_diffs
    assert merged.api_validations == api_validations
    assert merged.log_issues == log_issues


def test_fanout_defaults_to_empty_lists_when_analysis_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_REGRESSION", "false")
    monkeypatch.setenv("ENABLE_API_VALIDATION", "false")

    test_results = TestResult(
        passed=1, failed=0, total=1, cases=[TestCaseResult(title="t", status="passed")]
    )

    with patch(
        "orchestrator.nodes.log_analyze.analyze_test_results", return_value=[]
    ), patch("orchestrator.nodes.v8_coverage.collect_v8_coverage", return_value=None):
        graph = _build_fanout_graph()
        final_state = graph.invoke({"test_results": test_results, "metadata": {}})

    merged = final_state["test_results"]
    assert merged.regression_diffs == []
    assert merged.api_validations == []
    assert merged.log_issues == []
