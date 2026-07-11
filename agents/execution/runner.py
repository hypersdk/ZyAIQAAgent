"""Playwright execution bridge — spawns Node.js subprocess."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

from agents.common.models import TestCaseResult, TestResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_env() -> None:
    load_dotenv(_repo_root() / ".env")


def _find_attachment(results: list, name: str) -> str | None:
    for att in results:
        if att.get("name") == name and att.get("path"):
            return att["path"]
    return None


def _find_video(attachments: list) -> str | None:
    from agents.execution.artifacts import _find_video_attachment

    return _find_video_attachment(attachments)


def _find_screenshot(results: list) -> str | None:
    for att in results:
        if att.get("contentType", "").startswith("image/") and att.get("path"):
            return att["path"]
    return None


def _load_sidecar_log(test_output_dir: Path, filename: str) -> list[str]:
    log_path = test_output_dir / filename
    if log_path.exists():
        return [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return []


def _expand_valid_test_targets(test_dirs: list[str]) -> list[str]:
    """Expand directories to valid spec files, skipping syntactically broken specs."""
    from agents.generator.quality import validate_spec_file

    targets: list[str] = []
    for item in test_dirs:
        path = Path(item)
        if path.is_file() and path.suffix == ".ts":
            if validate_spec_file(path):
                targets.append(str(path))
            continue
        if not path.is_dir():
            continue
        for spec in sorted(path.glob("**/*.spec.ts")):
            if validate_spec_file(spec):
                targets.append(str(spec))
    return targets


def run_playwright(
    test_dirs: list[str] | None = None,
    base_url: str | None = None,
    project: str | None = None,
) -> TestResult:
    """Execute Playwright tests and parse JSON results."""
    _load_env()
    repo_root = _repo_root()
    config = repo_root / "playwright" / "playwright.config.ts"
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    env = {**os.environ}
    if base_url:
        env["ZYVOR_BASE_URL"] = base_url

    if test_dirs:
        targets = _expand_valid_test_targets(test_dirs)
    else:
        targets = _expand_valid_test_targets([str(repo_root / "tests" / "manual")])

    if not targets:
        return TestResult(
            passed=0,
            failed=1,
            total=1,
            cases=[
                TestCaseResult(
                    title="playwright execution",
                    status="failed",
                    error_message="No valid Playwright spec files found to execute",
                )
            ],
        )

    json_path = reports_dir / "results.json"
    cmd = ["npx", "playwright", "test", f"--config={config}", *targets]
    if project:
        cmd.extend(["--project", project])

    result = subprocess.run(cmd, cwd=repo_root, env=env, capture_output=True, text=True)

    if json_path.exists():
        parsed = parse_playwright_json(json_path, repo_root / "test-results")
        if parsed.total > 0:
            from agents.execution.artifacts import discover_videos_from_output_dir, persist_failure_artifacts

            parsed = discover_videos_from_output_dir(parsed, repo_root / "test-results")
            parsed = persist_failure_artifacts(parsed)
            return parsed

    return TestResult(
        passed=0,
        failed=1,
        total=1,
        cases=[
            TestCaseResult(
                title="playwright execution",
                status="failed",
                error_message=result.stderr or result.stdout or "Unknown error",
            )
        ],
    )


def parse_playwright_json(
    json_path: str | Path,
    test_results_dir: str | Path | None = None,
) -> TestResult:
    """Parse Playwright JSON report into TestResult with artifacts and logs."""
    path = Path(json_path)
    if not path.exists():
        return TestResult(passed=0, failed=0, total=0)

    data = json.loads(path.read_text(encoding="utf-8"))
    suites = data.get("suites", [])
    test_results_dir = Path(test_results_dir) if test_results_dir else None

    passed = failed = skipped = 0
    cases: list[TestCaseResult] = []

    def walk_suites(suite_list: list) -> None:
        nonlocal passed, failed, skipped
        for suite in suite_list:
            for spec in suite.get("specs", []):
                for test in spec.get("tests", []):
                    browser = test.get("projectName", "chromium")
                    for result in test.get("results", []):
                        status = result.get("status", "unknown")
                        title = spec.get("title", "unknown")
                        error_msg = None
                        if result.get("errors"):
                            error_msg = result["errors"][0].get("message", "")

                        attachments = result.get("attachments", [])
                        screenshot = _find_screenshot(attachments)
                        trace = _find_attachment(attachments, "trace")
                        video = _find_video(attachments)

                        console_logs: list[str] = []
                        network_errors: list[str] = []

                        for att in attachments:
                            if att.get("name") == "console.log" and att.get("body"):
                                body = att["body"]
                                if isinstance(body, str):
                                    console_logs = [line for line in body.splitlines() if line]
                            if att.get("name") == "network-errors.log" and att.get("body"):
                                body = att["body"]
                                if isinstance(body, str):
                                    network_errors = [line for line in body.splitlines() if line]

                        cases.append(
                            TestCaseResult(
                                title=title,
                                status=status,
                                browser=browser,
                                duration_ms=result.get("duration", 0),
                                error_message=error_msg,
                                screenshot_path=screenshot,
                                trace_path=trace,
                                video_path=video,
                                console_logs=console_logs,
                                network_errors=network_errors,
                            )
                        )
                        if status == "passed":
                            passed += 1
                        elif status == "skipped":
                            skipped += 1
                        else:
                            failed += 1
            walk_suites(suite.get("suites", []))

    walk_suites(suites)

    return TestResult(
        passed=passed,
        failed=failed,
        skipped=skipped,
        total=passed + failed + skipped,
        cases=cases,
        raw_json=data,
    )
