"""Browser console and network log analysis."""

from __future__ import annotations

import re
from pathlib import Path

from agents.common.models import LogIssue, TestCaseResult, TestResult

IGNORE_PATTERNS = [
    re.compile(r"favicon", re.I),
    re.compile(r"third-party", re.I),
    re.compile(r"analytics", re.I),
    re.compile(r"google-analytics", re.I),
    re.compile(r"Content Security Policy", re.I),
    re.compile(r"cloudflareinsights", re.I),
]


def _should_ignore(message: str) -> bool:
    return any(p.search(message) for p in IGNORE_PATTERNS)


def analyze_case_logs(case: TestCaseResult) -> list[LogIssue]:
    """Analyze console and network logs for a single test case."""
    issues: list[LogIssue] = []

    for log in case.console_logs:
        if _should_ignore(log):
            continue
        if log.startswith("[error]"):
            issues.append(
                LogIssue(
                    test_title=case.title,
                    severity="error",
                    source="console",
                    message=log,
                )
            )
        elif log.startswith("[warning]"):
            issues.append(
                LogIssue(
                    test_title=case.title,
                    severity="warning",
                    source="console",
                    message=log,
                )
            )

    for net_err in case.network_errors:
        if _should_ignore(net_err):
            continue
        match = re.match(r"(\d+)", net_err)
        status = int(match.group(1)) if match else 0
        severity = "error" if status >= 500 else "warning"
        issues.append(
            LogIssue(
                test_title=case.title,
                severity=severity,
                source="network",
                message=net_err,
            )
        )

    return issues


def analyze_test_results(test_results: TestResult) -> list[LogIssue]:
    """Analyze logs across all test cases."""
    issues: list[LogIssue] = []
    for case in test_results.cases:
        issues.extend(analyze_case_logs(case))
    return issues


def load_console_log(path: str | Path) -> list[str]:
    """Load a console.log sidecar file."""
    p = Path(path)
    if not p.exists():
        return []
    return [line for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
