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

"""Unit tests for orchestrator.nodes.analyze."""

from __future__ import annotations

from agents.common.models import TestResult
import orchestrator.nodes.analyze as analyze_module
from orchestrator.nodes.analyze import analyze_failures_node


def test_no_test_results_clears_failure_analysis():
    result = analyze_failures_node({})
    assert result["failure_analysis"] is None


def test_all_passed_clears_failure_analysis():
    state = {"test_results": TestResult(passed=1, failed=0, total=1)}
    result = analyze_failures_node(state)
    assert result["failure_analysis"] is None


def test_analyzes_real_failures(monkeypatch, tmp_path):
    monkeypatch.setattr(analyze_module, "_repo_root", lambda: tmp_path)
    calls = []
    monkeypatch.setattr(
        analyze_module, "analyze_failures",
        lambda test_results, *, artifact_dir, use_llm: calls.append((artifact_dir, use_llm)) or "root cause: timeout",
    )

    state = {"test_results": TestResult(passed=0, failed=1, total=1)}
    result = analyze_failures_node(state)

    assert result["failure_analysis"] == "root cause: timeout"
    assert calls[0][0] == tmp_path / "test-results"


def test_respects_disable_llm_analysis_env_var(monkeypatch, tmp_path):
    monkeypatch.setattr(analyze_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setenv("ENABLE_LLM_ANALYSIS", "false")
    calls = []
    monkeypatch.setattr(
        analyze_module, "analyze_failures",
        lambda test_results, *, artifact_dir, use_llm: calls.append(use_llm),
    )

    state = {"test_results": TestResult(passed=0, failed=1, total=1)}
    analyze_failures_node(state)
    assert calls == [False]
