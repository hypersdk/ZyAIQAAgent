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

"""Unit tests for the requirement-quality agent's rule-based fallback."""

from __future__ import annotations

from agents.common.models import Requirement, RequirementStep
from agents.requirement_quality.agent import evaluate_requirement_quality
from agents.requirement_quality.rule_fallback import evaluate_requirement_quality_rule_based


def test_no_steps_scores_low_with_named_reason():
    req = Requirement(id="req-1", title="Login works", description="The login flow should work properly.")
    result = evaluate_requirement_quality_rule_based(req)

    assert result.score < 50
    assert result.issues, "a low score must be explained by at least one issue"
    kinds = {issue.kind for issue in result.issues}
    assert "missing_acceptance_criteria" in kinds
    assert "vague_language" in kinds


def test_well_formed_requirement_scores_high_with_no_issues():
    req = Requirement(
        id="req-2",
        title="Login page loads",
        description="Verify the login page renders its form and the SSO button after navigation.",
        steps=[
            RequirementStep(action="navigate", target="/login"),
            RequirementStep(action="assert", target="form#login", assertion="Login form is visible"),
            RequirementStep(action="assert", target="button#sso", assertion="Sign in with SSO button is visible"),
        ],
    )
    result = evaluate_requirement_quality_rule_based(req)

    assert result.score >= 90
    assert result.issues == []


def test_step_without_assertion_is_flagged():
    req = Requirement(
        id="req-3",
        title="Submit form",
        description="Verify the form submits and something checkable happens afterward.",
        steps=[
            RequirementStep(action="navigate", target="/form"),
            RequirementStep(action="click", target="button#submit"),  # no assertion
        ],
    )
    result = evaluate_requirement_quality_rule_based(req)

    assert any(issue.kind == "missing_acceptance_criteria" for issue in result.issues)
    assert result.score < 100


def test_evaluate_requirement_quality_falls_back_without_llm_key(monkeypatch):
    for var in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "AZURE_OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "openai")

    req = Requirement(id="req-4", title="X", description="short")
    result = evaluate_requirement_quality(req)

    assert result.requirement_id == "req-4"
    assert 0.0 <= result.score <= 100.0
