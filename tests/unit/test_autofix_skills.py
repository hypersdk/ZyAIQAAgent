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

from __future__ import annotations

from unittest.mock import MagicMock

from agents.autofix import agent as autofix_agent
from agents.common.models import Skill, TestCaseResult, TestResult


def _failing_results() -> TestResult:
    case = TestCaseResult(
        title="login button click",
        status="failed",
        error_message="locator('#old-login-btn') not found",
    )
    return TestResult(passed=0, failed=1, total=1, cases=[case])


def test_matched_skill_is_reused_without_calling_llm(monkeypatch):
    skill = Skill(
        id="s1",
        original_selector="#old-login-btn",
        suggested_selector="page.getByRole('button', { name: 'Log in' })",
        test_title="login button click",
        confidence="high",
        explanation="role-based locator",
    )
    monkeypatch.setattr(autofix_agent, "load_skills", lambda: [skill])
    llm_factory = MagicMock(side_effect=AssertionError("LLM should not be called"))
    monkeypatch.setattr(autofix_agent, "get_llm", llm_factory)

    results = autofix_agent.suggest_fixes_from_results(_failing_results())

    assert len(results) == 1
    assert results[0].suggested_selector == skill.suggested_selector
    assert "remembered skill" in results[0].explanation
    llm_factory.assert_not_called()


def test_unmatched_case_falls_back_to_llm(monkeypatch):
    monkeypatch.setattr(autofix_agent, "load_skills", lambda: [])

    response = MagicMock()
    response.content = (
        '[{"test_title":"login button click","original_selector":"#old-login-btn",'
        '"suggested_selector":"page.getByRole(\'button\')","confidence":"medium",'
        '"explanation":"fresh"}]'
    )
    llm = MagicMock()
    llm.invoke.return_value = response
    monkeypatch.setattr(autofix_agent, "get_llm", lambda: llm)

    results = autofix_agent.suggest_fixes_from_results(_failing_results())

    assert len(results) == 1
    assert results[0].explanation == "fresh"
    llm.invoke.assert_called_once()
