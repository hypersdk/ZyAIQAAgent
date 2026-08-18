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

"""Report generation and notification delivery."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import content_to_text, get_llm
from agents.common.models import AutofixSuggestion, PipelineReport, TestResult, V8CoverageSummary
from agents.reporter.pdf import html_to_pdf


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


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
        return content_to_text(response.content)
    except Exception:
        return generate_summary_stub(test_results)


def generate_summary_stub(test_results: TestResult) -> str:
    """Fallback summary without LLM."""
    status = "PASSED" if test_results.all_passed else "FAILED"
    lines = [
        f"**Zyvor Argus Report** — {status}",
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


def _artifact_href(report_dir: Path, artifact_path: Optional[str]) -> Optional[str]:
    """Convert absolute artifact path to a report-relative href."""
    if not artifact_path:
        return None
    path = Path(artifact_path)
    if not path.exists():
        return None
    try:
        return str(path.relative_to(report_dir))
    except ValueError:
        try:
            return str(path.relative_to(report_dir.parent))
        except ValueError:
            return str(path)


def _cases_for_report(test_results: TestResult, report_dir: Path) -> list[dict]:
    cases = []
    for case in test_results.cases:
        data = case.model_dump()
        data["video_href"] = _artifact_href(report_dir, case.video_path)
        data["screenshot_href"] = _artifact_href(report_dir, case.screenshot_path)
        data["trace_href"] = _artifact_href(report_dir, case.trace_path)
        cases.append(data)
    return cases


def render_html_report(
    test_results: TestResult,
    summary: str,
    source: str = "local",
    failure_analysis: Optional[str] = None,
    autofix_suggestions: Optional[List[AutofixSuggestion]] = None,
    v8_coverage: Optional[V8CoverageSummary] = None,
    output_path: Optional[str | Path] = None,
) -> Path:
    """Render HTML report from template."""
    repo_root = _repo_root()
    env = Environment(loader=FileSystemLoader(repo_root / "templates"), autoescape=True)
    template = env.get_template("report.html.j2")

    if output_path is None:
        output_path = repo_root / "reports" / "qa-summary.html"
    output_path = Path(output_path)
    report_dir = output_path.parent

    html = template.render(
        generated_at=datetime.now(timezone.utc).isoformat(),
        source=source,
        passed=test_results.passed,
        failed=test_results.failed,
        total=test_results.total,
        summary=summary,
        failure_analysis=failure_analysis,
        cases=_cases_for_report(test_results, report_dir),
        regression_diffs=[d.model_dump() for d in test_results.regression_diffs],
        api_validations=[v.model_dump() for v in test_results.api_validations],
        log_issues=[i.model_dump() for i in test_results.log_issues],
        autofix_suggestions=[s.model_dump() for s in (autofix_suggestions or [])],
        v8_coverage=v8_coverage.model_dump() if v8_coverage else None,
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
    v8_coverage: Optional[V8CoverageSummary] = None,
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
        v8_coverage=v8_coverage,
    )

    pdf_path: Optional[Path] = None
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf_path = html_to_pdf(html_path)

    return PipelineReport(
        summary=summary,
        passed=test_results.passed,
        failed=test_results.failed,
        total=test_results.total,
        failure_analysis=failure_analysis,
        autofix_suggestions=[s.suggested_selector for s in (autofix_suggestions or [])],
        html_path=str(html_path),
        pdf_path=str(pdf_path) if pdf_path else None,
        v8_coverage_percentage=v8_coverage.percentage if v8_coverage else None,
    )
