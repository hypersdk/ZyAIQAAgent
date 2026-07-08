"""API response validation from Playwright HAR and sidecar logs."""

from __future__ import annotations

import json
import re
from pathlib import Path

from agents.common.models import ApiValidationResult, TestCaseResult, TestResult

# Default expectations for zyvor.dev marketing site
DEFAULT_EXPECTATIONS = [
    {"url_pattern": r"zyvor\.dev", "method": "GET", "expected_status": 200},
]


def validate_api_from_case(case: TestCaseResult) -> list[ApiValidationResult]:
    """Validate API calls recorded in a test case."""
    results: list[ApiValidationResult] = []

    for failure in case.api_failures:
        match = re.match(r"(\d+) (\w+) (.+)", failure)
        if match:
            status, method, url = int(match.group(1)), match.group(2), match.group(3)
            results.append(
                ApiValidationResult(
                    url=url,
                    method=method,
                    expected_status=200,
                    actual_status=status,
                    passed=status < 400,
                    error=failure if status >= 400 else None,
                )
            )

    for error in case.network_errors:
        match = re.match(r"(\d+) (\w+) (.+)", error)
        if match:
            status, method, url = int(match.group(1)), match.group(2), match.group(3)
            results.append(
                ApiValidationResult(
                    url=url,
                    method=method,
                    expected_status=200,
                    actual_status=status,
                    passed=False,
                    error=error,
                )
            )

    return results


def validate_test_results(test_results: TestResult) -> list[ApiValidationResult]:
    """Run API validation across all test cases."""
    all_validations: list[ApiValidationResult] = []
    for case in test_results.cases:
        all_validations.extend(validate_api_from_case(case))
    return all_validations


def load_har_validations(har_path: str | Path) -> list[ApiValidationResult]:
    """Parse a HAR file and validate response status codes."""
    path = Path(har_path)
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    results: list[ApiValidationResult] = []

    for entry in data.get("log", {}).get("entries", []):
        req = entry.get("request", {})
        resp = entry.get("response", {})
        url = req.get("url", "")
        method = req.get("method", "GET")
        status = resp.get("status", 0)

        if "zyvor.dev" in url or re.search(r"zyvor\.dev", url):
            results.append(
                ApiValidationResult(
                    url=url,
                    method=method,
                    expected_status=200,
                    actual_status=status,
                    passed=status < 400,
                    error=None if status < 400 else f"HTTP {status} for {url}",
                )
            )

    return results
