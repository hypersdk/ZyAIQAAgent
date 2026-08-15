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

"""Autofix agent — LLM-powered selector repair suggestions."""

from __future__ import annotations

import json
import re
from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import content_to_text, get_llm
from agents.common.models import AutofixSuggestion, TestCaseResult, TestResult
from agents.skills.store import find_skill, load_skills


def _extract_selector(error_message: str) -> Optional[str]:
    """Extract a CSS/locator from Playwright error text."""
    patterns = [
        r"locator\(['\"](.+?)['\"]\)",
        r"getByRole\(['\"](.+?)['\"]\)",
        r"getByText\(['\"](.+?)['\"]\)",
        r"selector ['\"](.+?)['\"]",
    ]
    for pattern in patterns:
        match = re.search(pattern, error_message)
        if match:
            return match.group(1)
    return None


def suggest_fixes_llm(
    test_results: TestResult,
    failure_analysis: Optional[str] = None,
) -> List[AutofixSuggestion]:
    """Use LLM to suggest selector fixes for failed tests."""
    failed_cases = [c for c in test_results.cases if c.status != "passed"]
    if not failed_cases:
        return []

    llm = get_llm()
    payload = {
        "failed_cases": [c.model_dump() for c in failed_cases],
        "failure_analysis": failure_analysis,
    }

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a Playwright test repair agent. For each failed test, suggest "
                    "an updated selector using getByRole, getByText, or getByLabel. "
                    "Return JSON array: "
                    '[{"test_title":"...","original_selector":"...","suggested_selector":"...",'
                    '"confidence":"high|medium|low","explanation":"..."}]'
                )
            ),
            HumanMessage(content=json.dumps(payload, indent=2)),
        ]
    )

    text = content_to_text(response.content).strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1)
    data = json.loads(text)
    return [AutofixSuggestion.model_validate(item) for item in data]


def suggest_fixes_stub(test_results: TestResult) -> List[AutofixSuggestion]:
    """Rule-based fallback suggestions without LLM."""
    suggestions: List[AutofixSuggestion] = []
    for case in test_results.cases:
        if case.status == "passed" or not case.error_message:
            continue
        original = _extract_selector(case.error_message) or "unknown"
        suggestions.append(
            AutofixSuggestion(
                test_title=case.title,
                original_selector=original,
                suggested_selector="page.getByRole('button', { name: /.../i })",
                confidence="low",
                explanation="Replace brittle selector with role-based locator (stub suggestion)",
            )
        )
    return suggestions


def _remembered_fix(case: TestCaseResult, skills) -> Optional[AutofixSuggestion]:
    """Look up a previously-confirmed fix for this failure, if one exists."""
    selector = _extract_selector(case.error_message or "") or "unknown"
    skill = find_skill(skills, selector, case.title)
    if not skill:
        return None
    explanation = f"{skill.explanation} [from remembered skill]".strip()
    return AutofixSuggestion(
        test_title=case.title,
        original_selector=skill.original_selector,
        suggested_selector=skill.suggested_selector,
        confidence=skill.confidence,
        explanation=explanation,
    )


def suggest_fixes_from_results(
    test_results: TestResult,
    failure_analysis: Optional[str] = None,
) -> List[AutofixSuggestion]:
    """Generate autofix suggestions — remembered skills first, then LLM/stub."""
    failed_cases = [c for c in test_results.cases if c.status != "passed"]
    if not failed_cases:
        return []

    skills = load_skills()
    remembered: List[AutofixSuggestion] = []
    unresolved_cases: List[TestCaseResult] = []
    for case in failed_cases:
        fix = _remembered_fix(case, skills)
        if fix:
            remembered.append(fix)
        else:
            unresolved_cases.append(case)

    if not unresolved_cases:
        return remembered

    remaining_results = test_results.model_copy(update={"cases": unresolved_cases})
    try:
        fresh = suggest_fixes_llm(remaining_results, failure_analysis)
    except Exception:
        fresh = suggest_fixes_stub(remaining_results)
    return remembered + fresh


def suggest_fixes(failure_output: str) -> list[str]:
    """Legacy stub interface."""
    return [f"Review failure output and update selectors: {failure_output[:200]}..."]
