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

from __future__ import annotations

import hashlib
import hmac

import pytest

from orchestrator.security.slack import SlackSecurityError, verify_slack_request

SECRET = "slack-signing-secret"


def _sign(body: bytes, timestamp: str, secret: str = SECRET) -> str:
    base_string = b"v0:" + timestamp.encode() + b":" + body
    return "v0=" + hmac.new(secret.encode(), base_string, hashlib.sha256).hexdigest()


def test_valid_signature_is_accepted():
    body = b"command=%2Fzyvor&text=run+smoke"
    timestamp = "1000000000"
    signature = _sign(body, timestamp)
    verification = verify_slack_request(body, signature, timestamp, SECRET, now=1000000000)
    assert verification.accepted


def test_missing_secret_is_rejected():
    with pytest.raises(SlackSecurityError):
        verify_slack_request(b"x", "v0=abc", "1000000000", "", now=1000000000)


def test_missing_signature_is_rejected():
    with pytest.raises(SlackSecurityError):
        verify_slack_request(b"x", None, "1000000000", SECRET, now=1000000000)


def test_missing_timestamp_is_rejected():
    signature = _sign(b"x", "1000000000")
    with pytest.raises(SlackSecurityError, match="X-Slack-Request-Timestamp"):
        verify_slack_request(b"x", signature, None, SECRET, now=1000000000)


def test_non_numeric_timestamp_is_rejected():
    signature = _sign(b"x", "1000000000")
    with pytest.raises(SlackSecurityError, match="X-Slack-Request-Timestamp"):
        verify_slack_request(b"x", signature, "not-a-number", SECRET, now=1000000000)


def test_stale_timestamp_is_rejected():
    body = b"x"
    timestamp = "1000000000"
    signature = _sign(body, timestamp)
    with pytest.raises(SlackSecurityError):
        verify_slack_request(body, signature, timestamp, SECRET, now=1000000000 + 301)


def test_tampered_body_is_rejected():
    timestamp = "1000000000"
    signature = _sign(b"original", timestamp)
    with pytest.raises(SlackSecurityError):
        verify_slack_request(b"tampered", signature, timestamp, SECRET, now=1000000000)
