"""Autofix agent — LLM-powered selector repair suggestions."""

from __future__ import annotations

import json
import re
from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm
from agents.common.models import AutofixSuggestion, TestResult


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

    text = response.content.strip()
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


def suggest_fixes_from_results(
    test_results: TestResult,
    failure_analysis: Optional[str] = None,
) -> List[AutofixSuggestion]:
    """Generate autofix suggestions — LLM with stub fallback."""
    try:
        return suggest_fixes_llm(test_results, failure_analysis)
    except Exception:
        return suggest_fixes_stub(test_results)


def suggest_fixes(failure_output: str) -> list[str]:
    """Legacy stub interface."""
    return [f"Review failure output and update selectors: {failure_output[:200]}..."]
