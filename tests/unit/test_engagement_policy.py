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

"""Unit tests for orchestrator/security/engagement_policy.py."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

import orchestrator.persistence.store as store_module
from orchestrator.security.engagement_policy import EngagementPolicy


class _FakeStore:
    def __init__(self, engagement: dict | None):
        self._engagement = engagement
        self.audit_calls: list[dict] = []

    def get_engagement(self, engagement_id):
        return self._engagement if engagement_id == "eng-1" else None

    def audit(self, action, **kwargs):
        self.audit_calls.append({"action": action, **kwargs})


def _engagement(**overrides) -> dict:
    base = {
        "id": "eng-1",
        "target_pattern": "example.com",
        "scope_statement": "authorized test",
        "tier": "active_recon",
        "authorized_by": "admin",
        "created_at": "2026-01-01T00:00:00+00:00",
        "expires_at": None,
        "revoked_at": None,
        "revoked_by": None,
    }
    base.update(overrides)
    return base


def _policy() -> EngagementPolicy:
    return EngagementPolicy(enforcement="required")


def test_disabled_enforcement_skips_check(monkeypatch):
    monkeypatch.setattr(store_module, "get_store", lambda: _FakeStore(None))
    EngagementPolicy(enforcement="disabled").require(
        target_url="https://example.com", min_tier="active_recon", engagement_id=None
    )


def test_missing_engagement_id_rejected(monkeypatch):
    monkeypatch.setattr(store_module, "get_store", lambda: _FakeStore(None))
    with pytest.raises(ValueError, match="requires an authorized security engagement"):
        _policy().require(target_url="https://example.com", min_tier="active_recon", engagement_id=None)


def test_unknown_engagement_id_rejected(monkeypatch):
    monkeypatch.setattr(store_module, "get_store", lambda: _FakeStore(None))
    with pytest.raises(ValueError, match="unknown engagement_id"):
        _policy().require(target_url="https://example.com", min_tier="active_recon", engagement_id="eng-1")


def test_revoked_engagement_rejected(monkeypatch):
    fake = _FakeStore(_engagement(revoked_at="2026-01-02T00:00:00+00:00"))
    monkeypatch.setattr(store_module, "get_store", lambda: fake)
    with pytest.raises(ValueError, match="revoked"):
        _policy().require(target_url="https://example.com", min_tier="active_recon", engagement_id="eng-1")


def test_expired_engagement_rejected(monkeypatch):
    expired = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    fake = _FakeStore(_engagement(expires_at=expired))
    monkeypatch.setattr(store_module, "get_store", lambda: fake)
    with pytest.raises(ValueError, match="expired"):
        _policy().require(target_url="https://example.com", min_tier="active_recon", engagement_id="eng-1")


def test_future_expiry_is_allowed(monkeypatch):
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    fake = _FakeStore(_engagement(expires_at=future))
    monkeypatch.setattr(store_module, "get_store", lambda: fake)
    _policy().require(target_url="https://example.com", min_tier="active_recon", engagement_id="eng-1")
    assert fake.audit_calls[0]["action"] == "engagement.use"


def test_insufficient_tier_rejected(monkeypatch):
    fake = _FakeStore(_engagement(tier="active_recon"))
    monkeypatch.setattr(store_module, "get_store", lambda: fake)
    with pytest.raises(ValueError, match="insufficient"):
        _policy().require(target_url="https://example.com", min_tier="exploit", engagement_id="eng-1")


def test_target_pattern_mismatch_rejected(monkeypatch):
    fake = _FakeStore(_engagement(target_pattern="only-this.example.com"))
    monkeypatch.setattr(store_module, "get_store", lambda: fake)
    with pytest.raises(ValueError, match="outside engagement scope"):
        _policy().require(target_url="https://other.example.com", min_tier="active_recon", engagement_id="eng-1")


def test_wildcard_target_pattern_matches(monkeypatch):
    fake = _FakeStore(_engagement(target_pattern="*.example.com"))
    monkeypatch.setattr(store_module, "get_store", lambda: fake)
    _policy().require(target_url="https://sub.example.com", min_tier="active_recon", engagement_id="eng-1")


def test_dashboard_ask_sentinel_target_matches_by_literal_pattern(monkeypatch):
    fake = _FakeStore(_engagement(target_pattern="dashboard_ask"))
    monkeypatch.setattr(store_module, "get_store", lambda: fake)
    _policy().require(target_url="dashboard_ask", min_tier="active_recon", engagement_id="eng-1")


def test_from_env_defaults_to_required(monkeypatch):
    monkeypatch.delenv("ZYVOR_ENGAGEMENT_ENFORCEMENT", raising=False)
    assert EngagementPolicy.from_env().enforcement == "required"


def test_from_env_reads_disabled(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENGAGEMENT_ENFORCEMENT", "disabled")
    assert EngagementPolicy.from_env().enforcement == "disabled"
    os.environ.pop("ZYVOR_ENGAGEMENT_ENFORCEMENT", None)
