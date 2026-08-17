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

import hashlib
import hmac

import pytest

from orchestrator.observability.metrics import inc, render, set_gauge
from orchestrator.persistence.store import MissionControlStore
from orchestrator.security.config import SecurityConfigurationError, validate_runtime_security
from orchestrator.security.webhook import WebhookSecurityError, verify_github_webhook


def test_non_production_config_is_never_checked(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "development")
    for key in ("DASHBOARD_PASSWORD", "DASHBOARD_SECRET", "GITHUB_WEBHOOK_SECRET", "ZYVOR_TARGET_ALLOWLIST"):
        monkeypatch.delenv(key, raising=False)
    validate_runtime_security()  # no exception, even though nothing is configured


def test_production_config_is_fail_closed(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "production")
    for key in ("DASHBOARD_PASSWORD", "DASHBOARD_SECRET", "GITHUB_WEBHOOK_SECRET", "ZYVOR_TARGET_ALLOWLIST"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(SecurityConfigurationError):
        validate_runtime_security()


def test_production_config_accepts_secure_minimum(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "production")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "p" * 16)
    monkeypatch.setenv("DASHBOARD_SECRET", "s" * 32)
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "w" * 32)
    monkeypatch.setenv("ZYVOR_TARGET_ALLOWLIST", "zyvor.dev,*.zyvor.dev")
    monkeypatch.setenv("ZYVOR_AGENT_MODE", "read_only")
    validate_runtime_security()


def test_production_config_rejects_unrestricted_agent_without_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "production")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "p" * 16)
    monkeypatch.setenv("DASHBOARD_SECRET", "s" * 32)
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "w" * 32)
    monkeypatch.setenv("ZYVOR_TARGET_ALLOWLIST", "zyvor.dev")
    monkeypatch.setenv("ZYVOR_AGENT_MODE", "unrestricted")
    monkeypatch.delenv("ZYVOR_ALLOW_UNRESTRICTED_AGENT_IN_PRODUCTION", raising=False)
    with pytest.raises(SecurityConfigurationError, match="unrestricted AI-agent mode"):
        validate_runtime_security()


def test_production_config_allows_unrestricted_agent_with_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "production")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "p" * 16)
    monkeypatch.setenv("DASHBOARD_SECRET", "s" * 32)
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "w" * 32)
    monkeypatch.setenv("ZYVOR_TARGET_ALLOWLIST", "zyvor.dev")
    monkeypatch.setenv("ZYVOR_AGENT_MODE", "unrestricted")
    monkeypatch.setenv("ZYVOR_ALLOW_UNRESTRICTED_AGENT_IN_PRODUCTION", "true")
    validate_runtime_security()


def test_production_config_rejects_disabled_engagement_enforcement(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENV", "production")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "p" * 16)
    monkeypatch.setenv("DASHBOARD_SECRET", "s" * 32)
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "w" * 32)
    monkeypatch.setenv("ZYVOR_TARGET_ALLOWLIST", "zyvor.dev")
    monkeypatch.setenv("ZYVOR_AGENT_MODE", "read_only")
    monkeypatch.setenv("ZYVOR_ENGAGEMENT_ENFORCEMENT", "disabled")
    with pytest.raises(SecurityConfigurationError, match="engagement enforcement"):
        validate_runtime_security()


def test_webhook_signature_and_replay(tmp_path):
    store = MissionControlStore(tmp_path / "state.db")
    payload = b'{"hello":"world"}'
    secret = "webhook-secret"
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    first = verify_github_webhook(
        payload, signature, secret, event="push", delivery_id="delivery-1", store=store
    )
    second = verify_github_webhook(
        payload, signature, secret, event="push", delivery_id="delivery-1", store=store
    )
    assert first.accepted and not first.duplicate
    assert second.duplicate and not second.accepted


def test_webhook_rejects_missing_secret(monkeypatch, tmp_path):
    monkeypatch.delenv("ZYVOR_ALLOW_UNSIGNED_WEBHOOKS", raising=False)
    with pytest.raises(WebhookSecurityError):
        verify_github_webhook(
            b"{}", None, "", event="push", delivery_id="d", store=MissionControlStore(tmp_path / "s.db")
        )


def test_webhook_rejects_missing_signature_header(tmp_path):
    with pytest.raises(WebhookSecurityError, match="missing or invalid"):
        verify_github_webhook(
            b"{}", None, "a-secret", event="push", delivery_id="d",
            store=MissionControlStore(tmp_path / "s.db"),
        )


def test_webhook_rejects_malformed_signature_prefix(tmp_path):
    with pytest.raises(WebhookSecurityError, match="missing or invalid"):
        verify_github_webhook(
            b"{}", "sha1=deadbeef", "a-secret", event="push", delivery_id="d",
            store=MissionControlStore(tmp_path / "s.db"),
        )


def test_webhook_rejects_wrong_signature(tmp_path):
    with pytest.raises(WebhookSecurityError, match="invalid GitHub webhook signature"):
        verify_github_webhook(
            b'{"a":1}', "sha256=" + "0" * 64, "a-secret", event="push", delivery_id="d",
            store=MissionControlStore(tmp_path / "s.db"),
        )


def test_webhook_rejects_missing_delivery_id():
    payload = b'{"hello":"world"}'
    secret = "webhook-secret"
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    with pytest.raises(WebhookSecurityError, match="X-GitHub-Delivery is required"):
        verify_github_webhook(payload, signature, secret, event="push", delivery_id="")


def test_prometheus_metrics_render():
    inc("zyvor_qa_test_counter_total", kind="smoke")
    set_gauge("zyvor_qa_test_gauge", 2, worker="one")
    text = render()
    assert 'zyvor_qa_test_counter_total{kind="smoke"}' in text
    assert 'zyvor_qa_test_gauge{worker="one"} 2' in text
