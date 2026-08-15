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

"""_collect_artifact_context must bound what goes into the failure-analysis
prompt — unbounded console logs / failed-case counts / stale artifacts have
no reason to grow the prompt without limit."""

from __future__ import annotations

from agents.analyzer.agent import (
    MAX_ARTIFACTS,
    MAX_ERROR_MESSAGE_CHARS,
    MAX_FAILED_CASES,
    MAX_LOG_ISSUES,
    MAX_LOG_LINES_PER_CASE,
    _collect_artifact_context,
    _truncate_list,
    _truncate_text,
)
from agents.common.models import (
    ApiValidationResult,
    LogIssue,
    RegressionDiff,
    TestCaseResult,
    TestResult,
)


def test_truncate_list_keeps_most_recent_and_notes_omission():
    items = [f"line-{i}" for i in range(30)]
    result = _truncate_list(items, 5)
    assert result[0].startswith("...")
    assert result[1:] == items[-5:]


def test_truncate_list_leaves_short_lists_untouched():
    items = ["a", "b"]
    assert _truncate_list(items, 5) == items


def test_truncate_text_caps_length():
    text = "x" * 5000
    result = _truncate_text(text, 100)
    assert result.startswith("x" * 100)
    assert "truncated" in result


def test_truncate_text_passes_through_short_text():
    assert _truncate_text("short", 100) == "short"
    assert _truncate_text(None, 100) is None


def _failing_case(title: str, *, log_lines: int = 0, error_len: int = 0) -> TestCaseResult:
    return TestCaseResult(
        title=title,
        status="failed",
        error_message="e" * error_len if error_len else "boom",
        console_logs=[f"log-{i}" for i in range(log_lines)],
        network_errors=[f"net-{i}" for i in range(log_lines)],
    )


def test_caps_failed_case_count_and_reports_omission():
    cases = [_failing_case(f"case-{i}") for i in range(MAX_FAILED_CASES + 5)]
    test_results = TestResult(passed=0, failed=len(cases), total=len(cases), cases=cases)

    context = _collect_artifact_context(test_results, None)

    assert len(context["failed_cases"]) == MAX_FAILED_CASES
    assert context["failed_cases_omitted"] == 5


def test_compresses_per_case_logs_and_error_message():
    case = _failing_case("chatty", log_lines=100, error_len=MAX_ERROR_MESSAGE_CHARS + 500)
    test_results = TestResult(passed=0, failed=1, total=1, cases=[case])

    context = _collect_artifact_context(test_results, None)

    compressed = context["failed_cases"][0]
    assert len(compressed["console_logs"]) == MAX_LOG_LINES_PER_CASE + 1  # + omission marker
    assert len(compressed["network_errors"]) == MAX_LOG_LINES_PER_CASE + 1
    assert len(compressed["error_message"]) <= MAX_ERROR_MESSAGE_CHARS + 60


def test_filters_to_failing_regression_api_and_log_entries_only():
    case = _failing_case("t")
    test_results = TestResult(
        passed=0,
        failed=1,
        total=1,
        cases=[case],
        regression_diffs=[
            RegressionDiff(file="pass.png", status="pass"),
            RegressionDiff(file="fail.png", status="fail"),
        ],
        api_validations=[
            ApiValidationResult(url="/ok", passed=True),
            ApiValidationResult(url="/bad", passed=False),
        ],
        log_issues=[
            LogIssue(test_title="t", severity="warning", source="console", message="noisy"),
            LogIssue(test_title="t", severity="error", source="console", message="boom"),
        ],
    )

    context = _collect_artifact_context(test_results, None)

    assert [d["file"] for d in context["regression_diffs"]] == ["fail.png"]
    assert [v["url"] for v in context["api_validations"]] == ["/bad"]
    assert [i["message"] for i in context["log_issues"]] == ["boom"]


def test_caps_total_log_issues():
    case = _failing_case("t")
    issues = [
        LogIssue(test_title="t", severity="error", source="console", message=f"e-{i}")
        for i in range(MAX_LOG_ISSUES + 10)
    ]
    test_results = TestResult(passed=0, failed=1, total=1, cases=[case], log_issues=issues)

    context = _collect_artifact_context(test_results, None)

    assert len(context["log_issues"]) == MAX_LOG_ISSUES


def test_caps_total_artifacts(tmp_path):
    # 3 artifact paths (screenshot/trace/video) per case; enough cases to
    # exceed MAX_ARTIFACTS while staying under MAX_FAILED_CASES so the cap
    # under test is the artifact cap, not the failed-case cap.
    num_cases = (MAX_ARTIFACTS // 3) + 3
    assert num_cases < MAX_FAILED_CASES
    cases = []
    for i in range(num_cases):
        case = _failing_case(f"case-{i}")
        for field, suffix in (
            ("screenshot_path", "png"),
            ("trace_path", "zip"),
            ("video_path", "webm"),
        ):
            path = tmp_path / f"{field}-{i}.{suffix}"
            path.write_bytes(b"x")
            setattr(case, field, str(path))
        cases.append(case)
    test_results = TestResult(passed=0, failed=len(cases), total=len(cases), cases=cases)

    context = _collect_artifact_context(test_results, None)

    assert len(context["artifacts"]) == MAX_ARTIFACTS
