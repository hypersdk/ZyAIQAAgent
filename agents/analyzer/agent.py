"""Failure analysis agent — Phase 1 pass-through stub, Phase 3 full LLM analysis."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm, load_prompt
from agents.common.models import TestResult


def analyze_failures_stub(test_results: TestResult) -> str:
    """Phase 1: echo Playwright errors without LLM."""
    if test_results.all_passed:
        return "All tests passed. No failures to analyze."

    lines = ["## Failure Summary (Phase 1 stub)\n"]
    for case in test_results.cases:
        if case.status != "passed":
            lines.append(f"- **{case.title}**: {case.status}")
            if case.error_message:
                lines.append(f"  Error: {case.error_message}")
    return "\n".join(lines)


def analyze_failures_llm(test_results: TestResult, artifact_dir: str | Path | None = None) -> str:
    """Phase 3: full LLM-powered failure analysis."""
    if test_results.all_passed:
        return "All tests passed."

    llm = get_llm()
    system = load_prompt("analyzer")

    context = {
        "summary": test_results.model_dump(),
        "artifact_dir": str(artifact_dir) if artifact_dir else None,
    }
    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=f"Analyze these test failures:\n\n{json.dumps(context, indent=2)}"),
        ]
    )
    return response.content


def analyze_failures(
    test_results: TestResult,
    artifact_dir: str | Path | None = None,
    use_llm: bool = False,
) -> str:
    """Analyze failures — stub by default, LLM when use_llm=True."""
    if use_llm:
        return analyze_failures_llm(test_results, artifact_dir)
    return analyze_failures_stub(test_results)
