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

"""End-to-end check of POST /webhook/slack/command: signature verification,
the dashboard-auth bypass, and the slash-command reply — through the real
FastAPI app rather than the gateway function in isolation."""

from __future__ import annotations

import hashlib
import hmac

from fastapi.testclient import TestClient

import orchestrator.dashboard.durable_jobs as durable_jobs
from orchestrator.webhook import create_app

SECRET = "route-test-secret"


def _signed_headers(body: bytes, timestamp: str, secret: str = SECRET) -> dict[str, str]:
    base_string = b"v0:" + timestamp.encode() + b":" + body
    signature = "v0=" + hmac.new(secret.encode(), base_string, hashlib.sha256).hexdigest()
    return {"X-Slack-Signature": signature, "X-Slack-Request-Timestamp": timestamp}


def test_valid_command_enqueues_and_replies(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", SECRET)

    class _FakeService:
        def enqueue(self, kind, params, *, requested_by=""):
            return {"id": "job-abc", "kind": kind, "status": "queued"}

    monkeypatch.setattr(durable_jobs, "get_service", lambda: _FakeService())

    client = TestClient(create_app())
    body = "command=%2Fzyvor&text=run+smoke&user_name=alice".encode()
    headers = _signed_headers(body, "1000000000")
    monkeypatch.setattr("time.time", lambda: 1000000000)

    response = client.post(
        "/webhook/slack/command",
        content=body,
        headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["response_type"] == "in_channel"
    assert "job-abc" in payload["text"]


def test_invalid_signature_is_rejected(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", SECRET)
    client = TestClient(create_app())
    body = b"command=%2Fzyvor&text=run+smoke"

    response = client.post(
        "/webhook/slack/command",
        content=body,
        headers={
            "X-Slack-Signature": "v0=deadbeef",
            "X-Slack-Request-Timestamp": "1000000000",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    assert response.status_code == 401


def test_missing_signing_secret_is_rejected(monkeypatch):
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    client = TestClient(create_app())

    response = client.post(
        "/webhook/slack/command",
        content=b"text=run+smoke",
        headers={
            "X-Slack-Signature": "v0=anything",
            "X-Slack-Request-Timestamp": "1000000000",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    assert response.status_code == 401
