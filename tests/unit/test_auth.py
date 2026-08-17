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

"""Unit tests for dashboard auth: tokens, credentials, and login rate limiting."""

from __future__ import annotations

import importlib
import time

import pytest


@pytest.fixture()
def auth(monkeypatch):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "Admin@321")
    monkeypatch.setenv("DASHBOARD_USER", "admin")
    from orchestrator.dashboard import auth as auth_mod

    importlib.reload(auth_mod)
    return auth_mod


def test_enabled_when_password_set(auth):
    assert auth.enabled() is True


def test_verify_credentials(auth):
    assert auth.verify_credentials("admin", "Admin@321") is True
    assert auth.verify_credentials("admin", "wrong") is False
    assert auth.verify_credentials("root", "Admin@321") is False


def test_token_roundtrip(auth):
    token, max_age = auth.issue_token()
    assert max_age > 0
    assert auth.validate_token(token) is True


def test_tampered_token_rejected(auth):
    token, _ = auth.issue_token()
    expiry, _sig = token.split(":", 1)
    assert auth.validate_token(f"{expiry}:deadbeef") is False


def test_expired_token_rejected(auth):
    # forge an expiry in the past with a valid signature
    past = 1
    sig = auth._sign(past)
    assert auth.validate_token(f"{past}:{sig}") is False


def test_rate_limit_trips_and_clears(auth):
    ip = "203.0.113.7"
    for _ in range(auth.RL_MAX_FAILURES):
        assert auth.rate_limited(ip) == 0
        auth.record_failure(ip)
    assert auth.rate_limited(ip) > 0
    # a different IP is unaffected
    assert auth.rate_limited("203.0.113.8") == 0
    # success clears the tripped IP's counters (simulate after lockout window in prod)
    auth.record_success(ip)
    assert ip not in auth._rl_locked_until


def test_rate_limit_map_pruned(auth):
    # stale single-failure IPs should be swept, not accumulate forever
    auth._rl_last_prune = 0.0
    auth.record_failure("198.51.100.1")
    assert "198.51.100.1" in auth._rl_failures
    # fast-forward past the window by back-dating the entry, then trigger a prune
    auth._rl_failures["198.51.100.1"][0] = 1.0
    auth._rl_last_prune = 0.0
    auth.record_failure("198.51.100.99")  # any failure triggers the sweep
    assert "198.51.100.1" not in auth._rl_failures


def test_rl_prune_removes_expired_lockout(auth):
    auth._rl_locked_until["1.2.3.4"] = 1.0  # already expired
    auth._rl_last_prune = 0.0
    auth._rl_prune(301.0)  # far enough past _rl_last_prune to trigger the sweep
    assert "1.2.3.4" not in auth._rl_locked_until


def test_rate_limited_clears_a_naturally_expired_lock(auth):
    auth._rl_locked_until["5.6.7.8"] = 1.0  # a timestamp in the distant past
    assert auth.rate_limited("5.6.7.8") == 0
    assert "5.6.7.8" not in auth._rl_locked_until


def test_record_failure_trims_a_stale_entry_inline(auth):
    auth._rl_failures["9.9.9.9"].append(1.0)  # ancient timestamp
    auth._rl_last_prune = time.time()  # keep the periodic sweep from firing this call
    auth.record_failure("9.9.9.9")
    assert len(auth._rl_failures["9.9.9.9"]) == 1  # only the fresh failure remains


def test_secret_uses_explicit_env_when_set(monkeypatch, auth):
    monkeypatch.setenv("DASHBOARD_SECRET", "explicit-secret-value")
    assert auth._secret() == b"explicit-secret-value"


def test_validate_token_rejects_non_numeric_expiry(auth):
    assert auth.validate_token("not-a-number:somesig") is False


def test_is_authenticated_true_when_auth_is_disabled(monkeypatch):
    monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
    from orchestrator.dashboard import auth as auth_mod

    assert auth_mod.is_authenticated(_FakeRequest()) is True


def test_is_authenticated_checks_the_session_cookie_when_enabled(auth):
    token, _ = auth.issue_token()
    assert auth.is_authenticated(_FakeRequest(cookies={auth.COOKIE_NAME: token})) is True
    assert auth.is_authenticated(_FakeRequest(cookies={auth.COOKIE_NAME: "garbage"})) is False


def test_requires_auth_is_false_when_disabled(monkeypatch):
    monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
    from orchestrator.dashboard import auth as auth_mod

    assert auth_mod.requires_auth("/dashboard") is False


def test_requires_auth_paths(auth):
    assert auth.requires_auth("/dashboard") is True
    assert auth.requires_auth("/api/dashboard/jobs") is True
    assert auth.requires_auth("/health") is False
    assert auth.requires_auth("/webhook/github") is False
    assert auth.requires_auth("/api/login") is False


class _FakeRequest:
    def __init__(self, cookies=None, headers=None):
        self.cookies = cookies or {}
        self.headers = headers or {}


def test_csrf_valid_for_matching_token(auth):
    token, _ = auth.issue_token()
    csrf = auth.csrf_token_for(token)
    request = _FakeRequest(
        cookies={auth.COOKIE_NAME: token}, headers={"x-csrf-token": csrf}
    )
    assert auth.csrf_valid(request) is True


def test_csrf_invalid_without_header(auth):
    token, _ = auth.issue_token()
    request = _FakeRequest(cookies={auth.COOKIE_NAME: token})
    assert auth.csrf_valid(request) is False


def test_csrf_invalid_with_wrong_header(auth):
    token, _ = auth.issue_token()
    request = _FakeRequest(
        cookies={auth.COOKIE_NAME: token}, headers={"x-csrf-token": "wrong"}
    )
    assert auth.csrf_valid(request) is False


def test_csrf_invalid_without_a_valid_session_cookie(auth):
    request = _FakeRequest(
        cookies={auth.COOKIE_NAME: "garbage"}, headers={"x-csrf-token": "anything"}
    )
    assert auth.csrf_valid(request) is False
