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

"""Fail-closed Slack slash-command request verification.

Mirrors `orchestrator/security/webhook.py`'s GitHub HMAC verification, adapted
to Slack's signing scheme: https://api.slack.com/authentication/verifying-requests
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass

MAX_REQUEST_AGE_SECONDS = 300


class SlackSecurityError(ValueError):
    pass


@dataclass(frozen=True)
class SlackVerification:
    accepted: bool


def verify_slack_request(
    body: bytes,
    signature: str | None,
    timestamp: str | None,
    secret: str,
    *,
    now: float | None = None,
) -> SlackVerification:
    """Verify a Slack request's `X-Slack-Signature` / `X-Slack-Request-Timestamp`.

    Unlike GitHub webhook verification there is no unsigned-request escape
    hatch — an inbound command that can enqueue jobs must always be verified.
    """
    if not secret:
        raise SlackSecurityError("SLACK_SIGNING_SECRET is required")
    if not signature or not signature.startswith("v0="):
        raise SlackSecurityError("missing or invalid X-Slack-Signature")
    if not timestamp or not timestamp.lstrip("-").isdigit():
        raise SlackSecurityError("missing or invalid X-Slack-Request-Timestamp")

    current = now if now is not None else time.time()
    if abs(current - int(timestamp)) > MAX_REQUEST_AGE_SECONDS:
        raise SlackSecurityError("stale Slack request timestamp")

    base_string = b"v0:" + timestamp.encode() + b":" + body
    expected = "v0=" + hmac.new(secret.encode(), base_string, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise SlackSecurityError("invalid Slack request signature")

    return SlackVerification(accepted=True)
