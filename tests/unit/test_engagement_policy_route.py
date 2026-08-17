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

"""HTTP-level tests for GET /api/v2/engagement-policy."""

from __future__ import annotations

from fastapi.testclient import TestClient

from orchestrator.dashboard.jobs import ELEVATED_RISK_KINDS
from orchestrator.webhook import create_app


def test_engagement_policy_defaults_to_required():
    client = TestClient(create_app())
    resp = client.get("/api/v2/engagement-policy")
    assert resp.status_code == 200
    body = resp.json()
    assert body["enforcement"] == "required"
    assert body["elevated_risk_kinds"] == ELEVATED_RISK_KINDS


def test_engagement_policy_reflects_disabled_enforcement(monkeypatch):
    monkeypatch.setenv("ZYVOR_ENGAGEMENT_ENFORCEMENT", "disabled")
    client = TestClient(create_app())
    resp = client.get("/api/v2/engagement-policy")
    assert resp.status_code == 200
    assert resp.json()["enforcement"] == "disabled"
