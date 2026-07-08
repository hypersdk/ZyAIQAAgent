"""Report generation and notification delivery."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm
from agents.common.models import AutofixSuggestion, PipelineReport, TestResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def generate_summary_llm(
    test_results: TestResult,
    failure_analysis: Optional[str] = None,
    autofix_suggestions: Optional[List[AutofixSuggestion]] = None,
) -> str:
    """Generate plain-English summary via LLM."""
    try:
        llm = get_llm()
        payload = {
            "passed": test_results.passed,
            "failed": test_results.failed,
            "total": test_results.total,
            "regression_diffs": [d.model_dump() for d in test_results.regression_diffs],
            "api_validations": [v.model_dump() for v in test_results.api_validations],
            "log_issues": [i.model_dump() for i in test_results.log_issues],
            "cases": [c.model_dump() for c in test_results.cases],
            "failure_analysis": failure_analysis,
            "autofix_suggestions": [s.model_dump() for s in (autofix_suggestions or [])],
        }
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Summarize Playwright test results for a GitHub PR comment. "
                        "Include regression, API, and log findings if present. "
                        "Be concise, actionable, 2-4 sentences."
                    )
                ),
                HumanMessage(content=json.dumps(payload, indent=2)),
            ]
        )
        return response.content
    except Exception:
        return generate_summary_stub(test_results)


def generate_summary_stub(test_results: TestResult) -> str:
    """Fallback summary without LLM."""
    status = "PASSED" if test_results.all_passed else "FAILED"
    lines = [
        f"**Zyvor QA Report** — {status}",
        "",
        f"- Passed: {test_results.passed}",
        f"- Failed: {test_results.failed}",
        f"- Total: {test_results.total}",
    ]

    reg_fail = [d for d in test_results.regression_diffs if d.status == "fail"]
    if reg_fail:
        lines.append(f"- Visual regressions: {len(reg_fail)}")

    api_fail = [v for v in test_results.api_validations if not v.passed]
    if api_fail:
        lines.append(f"- API failures: {len(api_fail)}")

    log_err = [i for i in test_results.log_issues if i.severity == "error"]
    if log_err:
        lines.append(f"- Log errors: {len(log_err)}")

    return "\n".join(lines)


def render_html_report(
    test_results: TestResult,
    summary: str,
    source: str = "local",
    failure_analysis: Optional[str] = None,
    autofix_suggestions: Optional[List[AutofixSuggestion]] = None,
    output_path: Optional[str | Path] = None,
) -> Path:
    """Render HTML report from template."""
    repo_root = _repo_root()
    env = Environment(loader=FileSystemLoader(repo_root / "templates"))
    template = env.get_template("report.html.j2")

    html = template.render(
        generated_at=datetime.now(timezone.utc).isoformat(),
        source=source,
        passed=test_results.passed,
        failed=test_results.failed,
        total=test_results.total,
        summary=summary,
        failure_analysis=failure_analysis,
        cases=[c.model_dump() for c in test_results.cases],
        regression_diffs=[d.model_dump() for d in test_results.regression_diffs],
        api_validations=[v.model_dump() for v in test_results.api_validations],
        log_issues=[i.model_dump() for i in test_results.log_issues],
        autofix_suggestions=[s.model_dump() for s in (autofix_suggestions or [])],
    )

    if output_path is None:
        output_path = repo_root / "reports" / "qa-summary.html"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def build_report(
    test_results: TestResult,
    source: str = "local",
    failure_analysis: Optional[str] = None,
    autofix_suggestions: Optional[List[AutofixSuggestion]] = None,
    use_llm: bool = False,
) -> PipelineReport:
    """Build full pipeline report."""
    if use_llm:
        summary = generate_summary_llm(test_results, failure_analysis, autofix_suggestions)
    else:
        summary = generate_summary_stub(test_results)

    html_path = render_html_report(
        test_results=test_results,
        summary=summary,
        source=source,
        failure_analysis=failure_analysis,
        autofix_suggestions=autofix_suggestions,
    )

    return PipelineReport(
        summary=summary,
        passed=test_results.passed,
        failed=test_results.failed,
        total=test_results.total,
        failure_analysis=failure_analysis,
        autofix_suggestions=[s.suggested_selector for s in (autofix_suggestions or [])],
        html_path=str(html_path),
    )
