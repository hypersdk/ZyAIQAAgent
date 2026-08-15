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

import pytest
from fastapi import HTTPException

from knowledge.config import clear_settings_cache
from knowledge.security import (
    ACCESS_PATTERN,
    TENANT_PATTERN,
    _token_claims,
    _validate_levels,
    resolve_identity,
)


def test_tenant_pattern() -> None:
    assert TENANT_PATTERN.fullmatch("acme-prod_01")
    assert not TENANT_PATTERN.fullmatch("../other-tenant")
    assert not TENANT_PATTERN.fullmatch("tenant with spaces")


def test_access_pattern() -> None:
    assert ACCESS_PATTERN.fullmatch("customer")
    assert ACCESS_PATTERN.fullmatch("support_engineer")
    assert not ACCESS_PATTERN.fullmatch("Admin Root")


def test_empty_access_levels_are_rejected() -> None:
    with pytest.raises(HTTPException):
        _validate_levels(())


def _reset_caches() -> None:
    clear_settings_cache()
    _token_claims.cache_clear()


def test_client_tenant_header_rejected_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """No AUTH_TOKENS_JSON configured and header-trust not opted into: a client
    must not be able to pick its own tenant_id via X-Tenant-ID."""
    monkeypatch.delenv("AUTH_TOKENS_JSON", raising=False)
    monkeypatch.delenv("APP_API_KEY", raising=False)
    monkeypatch.delenv("TRUST_CLIENT_TENANT_HEADER", raising=False)
    _reset_caches()
    try:
        with pytest.raises(HTTPException) as exc_info:
            resolve_identity(x_api_key=None, x_tenant_id="someone-elses-tenant", x_access_levels=None)
        assert exc_info.value.status_code == 401
    finally:
        _reset_caches()


def test_client_tenant_header_allowed_when_explicitly_trusted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Legacy internal-only behavior stays available, but only via explicit opt-in."""
    monkeypatch.delenv("AUTH_TOKENS_JSON", raising=False)
    monkeypatch.delenv("APP_API_KEY", raising=False)
    monkeypatch.setenv("TRUST_CLIENT_TENANT_HEADER", "true")
    _reset_caches()
    try:
        identity = resolve_identity(x_api_key=None, x_tenant_id="acme", x_access_levels=None)
        assert identity.tenant_id == "acme"
    finally:
        _reset_caches()


def test_mapped_tenant_still_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_TOKENS_JSON", '{"secret-token": {"tenant_id": "acme", "access_levels": ["public"]}}')
    _reset_caches()
    try:
        with pytest.raises(HTTPException) as exc_info:
            resolve_identity(x_api_key=None, x_tenant_id="public", x_access_levels=None)
        assert exc_info.value.status_code == 401

        identity = resolve_identity(x_api_key="secret-token", x_tenant_id="public", x_access_levels=None)
        assert identity.tenant_id == "acme"
    finally:
        _reset_caches()
