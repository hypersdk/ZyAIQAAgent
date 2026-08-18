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

"""Unit tests for orchestrator.nodes.notify."""

from __future__ import annotations

from agents.common.models import TestResult
import orchestrator.nodes.notify as notify_module
from orchestrator.nodes.notify import notify_channels


def test_no_test_results_is_a_noop():
    state = {}
    assert notify_channels(state) == state


def test_notifies_with_a_real_report(monkeypatch):
    calls = []
    monkeypatch.setattr(notify_module, "notify_all", lambda **kwargs: calls.append(kwargs))

    state = {
        "test_results": TestResult(passed=2, failed=1, total=3),
        "report_summary": "2/3 passed",
        "metadata": {"coverage_inventory_size": 5, "coverage_gaps_remaining": 1},
        "repo_full_name": "org/repo",
        "pr_number": 7,
    }
    result = notify_channels(state)

    assert result is state
    assert len(calls) == 1
    report = calls[0]["report"]
    assert report.summary == "2/3 passed"
    assert report.passed == 2
    assert report.coverage_inventory_size == 5
    assert calls[0]["repo_full_name"] == "org/repo"
    assert calls[0]["pr_number"] == 7
