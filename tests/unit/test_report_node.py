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

"""Unit tests for orchestrator.nodes.report."""

from __future__ import annotations

from agents.common.models import PipelineReport, TestResult
import orchestrator.nodes.report as report_module
from orchestrator.nodes.report import generate_report


def test_short_circuits_when_error_and_no_results():
    state = {"error": "boom"}
    assert generate_report(state) == state


def test_no_test_results_sets_error_when_none_already_present():
    result = generate_report({})
    assert result["error"] == "No test results to report"


def test_no_test_results_preserves_existing_error():
    result = generate_report({"error": "earlier failure"})
    assert result["error"] == "earlier failure"


def test_builds_report_and_appends_history(monkeypatch):
    report = PipelineReport(
        summary="3/3 passed", passed=3, failed=0, total=3,
        html_path="/tmp/report.html", pdf_path="/tmp/report.pdf",
    )
    build_calls = []
    monkeypatch.setattr(report_module, "build_report", lambda **kwargs: build_calls.append(kwargs) or report)

    append_calls = []
    monkeypatch.setattr(
        "orchestrator.dashboard.history.append_run",
        lambda rep, source: append_calls.append((rep, source)),
    )

    state = {"test_results": TestResult(passed=3, failed=0, total=3), "source": "github"}
    result = generate_report(state)

    assert result["report_path"] == "/tmp/report.html"
    assert result["pdf_report_path"] == "/tmp/report.pdf"
    assert result["report_summary"] == "3/3 passed"
    assert build_calls[0]["source"] == "github"
    assert append_calls == [(report, "github")]


def test_history_append_failure_is_swallowed(monkeypatch):
    report = PipelineReport(summary="ok", passed=1, failed=0, total=1)
    monkeypatch.setattr(report_module, "build_report", lambda **kwargs: report)
    monkeypatch.setattr(
        "orchestrator.dashboard.history.append_run",
        lambda rep, source: (_ for _ in ()).throw(RuntimeError("disk full")),
    )

    state = {"test_results": TestResult(passed=1, failed=0, total=1)}
    result = generate_report(state)
    assert result["report_summary"] == "ok"
