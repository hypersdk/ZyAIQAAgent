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

"""Unit tests for the pure/state-management surface of
orchestrator/dashboard/jobs.py: progress logging, live-case tally parsing,
job dispatch/busy-guard, and the small formatting helpers. The ~30
`_job_*` execution functions themselves are thin wrappers around real
subprocess/network calls and are deliberately out of scope here — they're
exercised end-to-end by the dashboard tutorials/manual QA, not unit tests."""

from __future__ import annotations

import os
import time

import pytest

from agents.common.models import TestCaseResult
from orchestrator.dashboard import jobs


@pytest.fixture(autouse=True)
def _reset_job_state():
    """jobs.py keeps its queue state in module globals (matches the
    single-job-at-a-time design) — reset them so tests don't leak into
    each other."""
    with jobs._lock:
        jobs._progress.clear()
        jobs._live_cases.clear()
        jobs._state.update(
            running=False, kind=None, params={}, started_at=None,
            finished_at=None, result=None, error=None,
        )
    jobs._cancel.clear()
    yield
    with jobs._lock:
        jobs._progress.clear()
        jobs._live_cases.clear()
        jobs._state.update(
            running=False, kind=None, params={}, started_at=None,
            finished_at=None, result=None, error=None,
        )
    jobs._cancel.clear()


# ── log_progress / status ────────────────────────────────────────────


def test_log_progress_appends_a_stamped_line():
    jobs.log_progress("hello world")
    assert jobs._progress[-1].endswith("hello world")
    assert jobs._progress[-1].startswith("[")


def test_log_progress_redacts_secrets():
    jobs.log_progress("using password=s3cret-value")
    assert "s3cret-value" not in jobs._progress[-1]


def test_log_progress_caps_history_at_200():
    for i in range(250):
        jobs.log_progress(f"line {i}")
    assert len(jobs._progress) == 200
    assert jobs._progress[-1].endswith("line 249")


def test_status_reflects_progress_and_redacts_params():
    jobs._state["params"] = {"password": "s3cret"}
    jobs.log_progress("working")
    result = jobs.status()
    assert result["params"]["password"] == "***"
    assert result["progress"][-1].endswith("working")


def test_status_live_tally_counts_pass_fail():
    jobs._live_cases.extend(
        [{"title": "a", "status": "passed"}, {"title": "b", "status": "failed"}]
    )
    tally = jobs.status()["live_tally"]
    assert tally == {"passed": 1, "failed": 1}


# ── _stream_line / _stream_line_flow / _stream_line_audit ──────────────


def test_stream_line_parses_passed_case():
    jobs._stream_line("  ✓  1 [chromium] › homepage loads (350ms)")
    assert jobs._live_cases[-1] == {"title": "homepage loads", "status": "passed", "browser": "chromium"}


def test_stream_line_parses_failed_case():
    jobs._stream_line("  ✗  2 [firefox] › login works (1.2s)")
    assert jobs._live_cases[-1]["status"] == "failed"
    assert jobs._live_cases[-1]["browser"] == "firefox"


def test_stream_line_ignores_non_matching_lines():
    jobs._stream_line("Running 3 tests using 2 workers")
    assert jobs._live_cases == []
    # still logged, even though it didn't parse as a case line
    assert jobs._progress[-1].endswith("Running 3 tests using 2 workers")


def test_stream_line_flow_parses_step():
    jobs._stream_line_flow("✓ step 1: navigate to homepage — ok")
    assert jobs._live_cases[-1] == {"title": "navigate to homepage", "status": "passed", "browser": None}


def test_stream_line_flow_failed_step():
    jobs._stream_line_flow("✗ step 2: click submit")
    assert jobs._live_cases[-1]["status"] == "failed"


def test_stream_line_audit_parses_page_result():
    jobs._stream_line_audit("audit: /pricing (HTTP 200)")
    assert jobs._live_cases[-1] == {"title": "/pricing", "status": "passed", "browser": None}


def test_stream_line_audit_treats_4xx_5xx_as_failed():
    jobs._stream_line_audit("audit: /missing (HTTP 404)")
    assert jobs._live_cases[-1]["status"] == "failed"


# ── cancel ───────────────────────────────────────────────────────────


def test_cancel_when_nothing_running_is_a_noop():
    result = jobs.cancel()
    assert result["running"] is False
    assert not jobs._cancel.is_set()


def test_cancel_when_running_sets_the_flag():
    jobs._state["running"] = True
    jobs.cancel()
    assert jobs._cancel.is_set()


# ── _brief / _slug / _explain_failure ───────────────────────────────


def test_brief_reports_error_verbatim():
    assert jobs._brief("smoke", None, "boom") == "boom"


def test_brief_reports_pass_total_when_present():
    assert jobs._brief("smoke", {"passed": 3, "total": 4}, None) == "3/4 passed"


def test_brief_discover_kind():
    assert jobs._brief("discover", {"inventory": 5, "gaps_total": 2}, None) == "5 candidates, 2 gaps"


def test_brief_generate_kind():
    assert jobs._brief("generate", {"generated": ["a.spec.ts", "b.spec.ts"]}, None) == "2 test file(s) generated"


def test_brief_regression_kind():
    assert jobs._brief("regression", {"diffs": [1, 2, 3]}, None) == "3 screenshot(s) compared"


def test_brief_falls_back_to_done():
    assert jobs._brief("ping", {}, None) == "done"


def test_slug_normalizes_and_truncates():
    assert jobs._slug("Login Works!! (v2)") == "login-works-v2"
    assert jobs._slug("") == "test"
    assert len(jobs._slug("x" * 200)) <= 80


def test_explain_failure_matches_known_patterns():
    assert "never appeared" in jobs._explain_failure("Timeout waiting for locator('#submit')")
    assert "Navigation timed out" in jobs._explain_failure("Timeout 30000ms exceeded while navigating to goto")
    assert "matched multiple elements" in jobs._explain_failure("strict mode violation: resolved to 2 elements")
    assert "isn't visible" in jobs._explain_failure("Element is not visible")
    assert "Assertion mismatch" in jobs._explain_failure("Expected 'foo' Received 'bar'")
    assert "Network error" in jobs._explain_failure("net::ERR_CONNECTION_REFUSED")
    assert "syntax error" in jobs._explain_failure("no valid playwright spec found")


def test_explain_failure_defaults_for_unknown_error():
    assert jobs._explain_failure("some completely novel failure") == "Review the trace or video to see the exact step that failed."


def test_explain_failure_empty_string_for_no_error():
    assert jobs._explain_failure("") == ""


# ── _cases_payload ───────────────────────────────────────────────────


class _FakeResults:
    def __init__(self, cases):
        self.cases = cases


def test_cases_payload_builds_hint_and_truncates_logs():
    case = TestCaseResult(
        title="checkout flow",
        status="failed",
        browser="chromium",
        duration_ms=1234.5,
        error_message="Timeout waiting for locator('#pay')",
        console_logs=[f"[error] e{i}" for i in range(20)] + ["[log] noise"],
        network_errors=[f"net error {i}" for i in range(20)],
    )
    payload = jobs._cases_payload(_FakeResults([case]))

    assert len(payload) == 1
    entry = payload[0]
    assert entry["title"] == "checkout flow"
    assert entry["status"] == "failed"
    assert "never appeared" in entry["hint"]
    assert len(entry["console_logs"]) == 8  # filtered to [error] lines, capped
    assert len(entry["network_errors"]) == 8


def test_cases_payload_passed_case_has_no_error_or_hint():
    case = TestCaseResult(title="ok test", status="passed", error_message="should be ignored")
    payload = jobs._cases_payload(_FakeResults([case]))
    assert payload[0]["error"] == ""
    assert payload[0]["hint"] == ""


def test_cases_payload_respects_limit():
    cases = [TestCaseResult(title=f"t{i}", status="passed") for i in range(5)]
    payload = jobs._cases_payload(_FakeResults(cases), limit=2)
    assert len(payload) == 2


# ── _env_overrides ───────────────────────────────────────────────────


def test_env_overrides_sets_and_restores(monkeypatch):
    monkeypatch.delenv("ZYVOR_TEST_OVERRIDE_VAR", raising=False)
    with jobs._env_overrides({"ZYVOR_TEST_OVERRIDE_VAR": "temp"}):
        assert os.environ["ZYVOR_TEST_OVERRIDE_VAR"] == "temp"
    assert "ZYVOR_TEST_OVERRIDE_VAR" not in os.environ


def test_env_overrides_restores_previous_value_after_exception():
    os.environ["ZYVOR_TEST_OVERRIDE_VAR2"] = "original"
    try:
        with pytest.raises(RuntimeError):
            with jobs._env_overrides({"ZYVOR_TEST_OVERRIDE_VAR2": "temp"}):
                assert os.environ["ZYVOR_TEST_OVERRIDE_VAR2"] == "temp"
                raise RuntimeError("boom")
        assert os.environ["ZYVOR_TEST_OVERRIDE_VAR2"] == "original"
    finally:
        os.environ.pop("ZYVOR_TEST_OVERRIDE_VAR2", None)


def test_env_overrides_none_value_unsets_the_var():
    os.environ["ZYVOR_TEST_OVERRIDE_VAR3"] = "was-set"
    try:
        with jobs._env_overrides({"ZYVOR_TEST_OVERRIDE_VAR3": None}):
            assert "ZYVOR_TEST_OVERRIDE_VAR3" not in os.environ
        assert os.environ["ZYVOR_TEST_OVERRIDE_VAR3"] == "was-set"
    finally:
        os.environ.pop("ZYVOR_TEST_OVERRIDE_VAR3", None)


# ── trigger / _run: dispatch and busy-guard ─────────────────────────


def test_trigger_rejects_unknown_kind_without_touching_state():
    with pytest.raises(ValueError):
        jobs.trigger("not_a_real_kind", {})
    assert jobs._state["running"] is False


def test_trigger_refuses_when_already_running():
    jobs._state["running"] = True
    started, current = jobs.trigger("smoke", {})
    assert started is False
    assert current["running"] is True


def test_trigger_starts_and_run_populates_result(monkeypatch):
    monkeypatch.setitem(jobs._JOBS, "smoke", lambda params: {"passed": 2, "total": 2})

    started, current = jobs.trigger("smoke", {})
    assert started is True
    # `current["running"]` is deliberately not asserted here: the fake job
    # below returns instantly, so under heavy parallel test load the
    # background thread can finish before this line even runs — that race
    # doesn't exist in production, where real jobs take seconds+.
    assert current["kind"] == "smoke"

    for _ in range(100):
        if not jobs.status()["running"]:
            break
        time.sleep(0.01)

    final = jobs.status()
    assert final["running"] is False
    assert final["result"] == {"passed": 2, "total": 2}
    assert final["error"] is None
