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

"""Unit tests for orchestrator.security.rbac: token identification and scope
enforcement. Previously untested (0% direct coverage, only incidentally
exercised via routes that happen to call through it)."""

from __future__ import annotations

import hashlib
import json

import pytest
from fastapi import HTTPException

from orchestrator.security import rbac


class _FakeRequest:
    def __init__(self, headers=None, cookies=None):
        self.headers = headers or {}
        self.cookies = cookies or {}


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    # identify()'s session/development branches read these; keep every test
    # isolated from whatever the surrounding shell/CI environment has set.
    monkeypatch.delenv("ZYVOR_API_TOKENS_FILE", raising=False)
    monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
    monkeypatch.delenv("ZYVOR_ENV", raising=False)


def test_identity_allows_wildcard_scope():
    identity = rbac.Identity("svc", "admin", frozenset({"*"}), "token")
    assert identity.allows("jobs:write") is True
    assert identity.allows("anything:at:all") is True


def test_identity_allows_exact_scope_only():
    identity = rbac.Identity("svc", "viewer", frozenset({"jobs:read"}), "token")
    assert identity.allows("jobs:read") is True
    assert identity.allows("jobs:write") is False


def test_token_records_empty_when_env_unset():
    assert rbac._token_records() == {}


def test_token_records_missing_file_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("ZYVOR_API_TOKENS_FILE", str(tmp_path / "does-not-exist.json"))
    with pytest.raises(RuntimeError, match="unable to load"):
        rbac._token_records()


def test_token_records_malformed_json_raises(monkeypatch, tmp_path):
    path = tmp_path / "tokens.json"
    path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setenv("ZYVOR_API_TOKENS_FILE", str(path))
    with pytest.raises(RuntimeError, match="unable to load"):
        rbac._token_records()


def test_token_records_non_object_json_raises(monkeypatch, tmp_path):
    path = tmp_path / "tokens.json"
    path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    monkeypatch.setenv("ZYVOR_API_TOKENS_FILE", str(path))
    with pytest.raises(RuntimeError, match="must contain a JSON object"):
        rbac._token_records()


def test_token_records_valid_file_returns_dict(monkeypatch, tmp_path):
    path = tmp_path / "tokens.json"
    records = {"abc123": {"subject": "ci-bot", "role": "operator"}}
    path.write_text(json.dumps(records), encoding="utf-8")
    monkeypatch.setenv("ZYVOR_API_TOKENS_FILE", str(path))
    assert rbac._token_records() == records


def _write_token_file(tmp_path, monkeypatch, records):
    path = tmp_path / "tokens.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    monkeypatch.setenv("ZYVOR_API_TOKENS_FILE", str(path))


def test_identify_valid_bearer_token_maps_role_to_scopes(monkeypatch, tmp_path):
    token = "s3cr3t-token"
    digest = hashlib.sha256(token.encode()).hexdigest()
    _write_token_file(
        tmp_path, monkeypatch,
        {digest: {"subject": "github-actions", "role": "operator"}},
    )
    request = _FakeRequest(headers={"authorization": f"Bearer {token}"})
    identity = rbac.identify(request)
    assert identity.subject == "github-actions"
    assert identity.role == "operator"
    assert identity.auth_type == "token"
    assert identity.allows("jobs:write") is True
    assert identity.allows("engagements:write") is False  # not in operator's set


def test_identify_bearer_token_merges_explicit_extra_scopes(monkeypatch, tmp_path):
    token = "s3cr3t-token"
    digest = hashlib.sha256(token.encode()).hexdigest()
    _write_token_file(
        tmp_path, monkeypatch,
        {digest: {"subject": "narrow-bot", "role": "viewer", "scopes": ["jobs:write"]}},
    )
    request = _FakeRequest(headers={"authorization": f"Bearer {token}"})
    identity = rbac.identify(request)
    # viewer's base scopes plus the one explicit grant
    assert identity.allows("jobs:read") is True
    assert identity.allows("jobs:write") is True
    assert identity.allows("engagements:read") is True
    assert identity.allows("findings:write") is False


def test_identify_bearer_token_unknown_role_falls_back_to_viewer(monkeypatch, tmp_path):
    token = "s3cr3t-token"
    digest = hashlib.sha256(token.encode()).hexdigest()
    _write_token_file(
        tmp_path, monkeypatch,
        {digest: {"subject": "typo-role", "role": "operatorr"}},
    )
    request = _FakeRequest(headers={"authorization": f"Bearer {token}"})
    identity = rbac.identify(request)
    assert identity.role == "operatorr"
    assert identity.allows("jobs:read") is True
    assert identity.allows("jobs:write") is False


def test_identify_bearer_token_no_match_raises_401(monkeypatch, tmp_path):
    _write_token_file(
        tmp_path, monkeypatch,
        {hashlib.sha256(b"some-other-token").hexdigest(): {"role": "viewer"}},
    )
    request = _FakeRequest(headers={"authorization": "Bearer wrong-token"})
    with pytest.raises(HTTPException) as exc_info:
        rbac.identify(request)
    assert exc_info.value.status_code == 401


def test_identify_session_authenticated_yields_admin_identity(monkeypatch):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "Admin@321")
    monkeypatch.setenv("DASHBOARD_USER", "alice")
    from orchestrator.dashboard import auth as auth_mod

    token, _max_age = auth_mod.issue_token()
    request = _FakeRequest(cookies={auth_mod.COOKIE_NAME: token})
    identity = rbac.identify(request)
    assert identity.subject == "alice"
    assert identity.role == "admin"
    assert identity.auth_type == "session"
    assert identity.allows("anything") is True


def test_identify_session_enabled_but_not_authenticated_raises_401(monkeypatch):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "Admin@321")
    request = _FakeRequest()  # no cookie at all
    with pytest.raises(HTTPException) as exc_info:
        rbac.identify(request)
    assert exc_info.value.status_code == 401


def test_identify_no_dashboard_password_outside_production_is_local_dev(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "development")
    request = _FakeRequest()
    identity = rbac.identify(request)
    assert identity.subject == "local-development"
    assert identity.role == "admin"
    assert identity.auth_type == "development"


def test_identify_no_dashboard_password_in_production_raises_401(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "production")
    request = _FakeRequest()
    with pytest.raises(HTTPException) as exc_info:
        rbac.identify(request)
    assert exc_info.value.status_code == 401


def test_require_scope_returns_identity_when_allowed(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "development")
    request = _FakeRequest()
    identity = rbac.require_scope(request, "jobs:write")
    assert identity.subject == "local-development"


def test_require_scope_raises_403_when_denied(monkeypatch, tmp_path):
    token = "viewer-token"
    digest = hashlib.sha256(token.encode()).hexdigest()
    _write_token_file(tmp_path, monkeypatch, {digest: {"subject": "ro-bot", "role": "viewer"}})
    request = _FakeRequest(headers={"authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc_info:
        rbac.require_scope(request, "jobs:write")
    assert exc_info.value.status_code == 403
