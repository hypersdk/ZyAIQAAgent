"""Report generation and notification delivery."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm
from agents.common.models import PipelineReport, TestResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def generate_summary_llm(test_results: TestResult, failure_analysis: str | None = None) -> str:
    """Generate plain-English summary via LLM."""
    try:
        llm = get_llm()
        payload = {
            "passed": test_results.passed,
            "failed": test_results.failed,
            "total": test_results.total,
            "cases": [c.model_dump() for c in test_results.cases],
            "failure_analysis": failure_analysis,
        }
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Summarize Playwright test results for a GitHub PR comment. "
                        "Be concise, actionable, 2-4 sentences."
                    )
                ),
                HumanMessage(content=json.dumps(payload, indent=2)),
            ]
        )
        return response.content
    except Exception:
        return (
            f"QA run complete: {test_results.passed} passed, "
            f"{test_results.failed} failed out of {test_results.total} tests."
        )


def generate_summary_stub(test_results: TestResult) -> str:
    """Fallback summary without LLM."""
    status = "PASSED" if test_results.all_passed else "FAILED"
    return (
        f"**Zyvor QA Report** — {status}\n\n"
        f"- Passed: {test_results.passed}\n"
        f"- Failed: {test_results.failed}\n"
        f"- Total: {test_results.total}\n"
    )


def render_html_report(
    test_results: TestResult,
    summary: str,
    source: str = "local",
    failure_analysis: str | None = None,
    output_path: str | Path | None = None,
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
    failure_analysis: str | None = None,
    use_llm: bool = False,
) -> PipelineReport:
    """Build full pipeline report."""
    if use_llm:
        summary = generate_summary_llm(test_results, failure_analysis)
    else:
        summary = generate_summary_stub(test_results)

    html_path = render_html_report(
        test_results=test_results,
        summary=summary,
        source=source,
        failure_analysis=failure_analysis,
    )

    return PipelineReport(
        summary=summary,
        passed=test_results.passed,
        failed=test_results.failed,
        total=test_results.total,
        failure_analysis=failure_analysis,
        html_path=str(html_path),
    )
