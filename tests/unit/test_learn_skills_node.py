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

from agents.common.models import AutofixSuggestion, TestResult
from agents.skills.store import load_skills
from orchestrator.nodes.learn_skills import learn_skills_node


def _applied_suggestion() -> AutofixSuggestion:
    return AutofixSuggestion(
        test_title="login button click",
        original_selector="#old-login-btn",
        suggested_selector="page.getByRole('button', { name: 'Log in' })",
        confidence="high",
        explanation="role-based locator [applied to login.spec.ts]",
    )


def test_records_skill_when_patched_and_all_passed(tmp_path, monkeypatch):
    monkeypatch.setenv("SKILLS_PATH", str(tmp_path / "skills.json"))
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)

    state = {
        "metadata": {"autofix_patched_files": ["tests/manual/login.spec.ts"]},
        "test_results": TestResult(passed=1, failed=0, total=1, cases=[]),
        "autofix_suggestions": [_applied_suggestion()],
    }

    learn_skills_node(state)

    skills = load_skills()
    assert len(skills) == 1
    assert skills[0].suggested_selector == _applied_suggestion().suggested_selector


def test_noop_when_results_did_not_pass(tmp_path, monkeypatch):
    monkeypatch.setenv("SKILLS_PATH", str(tmp_path / "skills.json"))

    state = {
        "metadata": {"autofix_patched_files": ["tests/manual/login.spec.ts"]},
        "test_results": TestResult(passed=0, failed=1, total=1, cases=[]),
        "autofix_suggestions": [_applied_suggestion()],
    }

    learn_skills_node(state)

    assert not (tmp_path / "skills.json").exists()


def test_noop_when_nothing_was_patched(tmp_path, monkeypatch):
    monkeypatch.setenv("SKILLS_PATH", str(tmp_path / "skills.json"))

    state = {
        "metadata": {},
        "test_results": TestResult(passed=1, failed=0, total=1, cases=[]),
        "autofix_suggestions": [],
    }

    learn_skills_node(state)

    assert not (tmp_path / "skills.json").exists()
