"""Failure analysis agent with full artifact ingestion."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm, load_prompt
from agents.common.models import TestResult


def _collect_artifact_context(
    test_results: TestResult,
    artifact_dir: Path | None,
) -> dict:
    """Build rich context from test results and artifact files."""
    context: dict = {
        "summary": {
            "passed": test_results.passed,
            "failed": test_results.failed,
            "total": test_results.total,
        },
        "failed_cases": [],
        "regression_diffs": [d.model_dump() for d in test_results.regression_diffs],
        "api_validations": [v.model_dump() for v in test_results.api_validations],
        "log_issues": [i.model_dump() for i in test_results.log_issues],
        "artifacts": [],
    }

    for case in test_results.cases:
        if case.status != "passed":
            case_data = case.model_dump()
            context["failed_cases"].append(case_data)

            for field in ("screenshot_path", "trace_path", "video_path"):
                path = case_data.get(field)
                if path and Path(path).exists():
                    context["artifacts"].append({"type": field, "path": path})

    if artifact_dir and artifact_dir.exists():
        for trace in artifact_dir.rglob("trace.zip"):
            context["artifacts"].append({"type": "trace", "path": str(trace)})
        for png in artifact_dir.rglob("*.png"):
            context["artifacts"].append({"type": "screenshot", "path": str(png)})

    return context


def analyze_failures_stub(test_results: TestResult) -> str:
    """Echo Playwright errors without LLM."""
    if test_results.all_passed:
        return "All tests passed. No failures to analyze."

    lines = ["## Failure Summary\n"]
    for case in test_results.cases:
        if case.status != "passed":
            lines.append(f"- **{case.title}** ({case.browser or 'chromium'}): {case.status}")
            if case.error_message:
                lines.append(f"  Error: {case.error_message}")

    if test_results.regression_diffs:
        lines.append("\n### Visual Regressions")
        for d in test_results.regression_diffs:
            if d.status == "fail":
                lines.append(f"- {d.file}: {d.message}")

    if test_results.api_validations:
        failed = [v for v in test_results.api_validations if not v.passed]
        if failed:
            lines.append("\n### API Failures")
            for v in failed:
                lines.append(f"- {v.method} {v.url}: {v.actual_status}")

    if test_results.log_issues:
        errors = [i for i in test_results.log_issues if i.severity == "error"]
        if errors:
            lines.append("\n### Log Issues")
            for i in errors[:10]:
                lines.append(f"- [{i.source}] {i.message}")

    return "\n".join(lines)


def analyze_failures_llm(
    test_results: TestResult,
    artifact_dir: str | Path | None = None,
) -> str:
    """Full LLM-powered failure analysis with artifact context."""
    if test_results.all_passed:
        return "All tests passed."

    llm = get_llm()
    system = load_prompt("analyzer")
    artifact_path = Path(artifact_dir) if artifact_dir else None
    context = _collect_artifact_context(test_results, artifact_path)

    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(
                content=(
                    "Analyze these test failures and provide root cause, affected area, "
                    "suggested fix, and flake assessment:\n\n"
                    f"{json.dumps(context, indent=2)}"
                )
            ),
        ]
    )
    return response.content


def analyze_failures(
    test_results: TestResult,
    artifact_dir: str | Path | None = None,
    use_llm: bool = True,
) -> str:
    """Analyze failures — LLM by default in Phase 3, stub fallback on error."""
    if use_llm:
        try:
            return analyze_failures_llm(test_results, artifact_dir)
        except Exception as exc:
            stub = analyze_failures_stub(test_results)
            return f"{stub}\n\n(LLM analysis unavailable: {exc})"
    return analyze_failures_stub(test_results)
