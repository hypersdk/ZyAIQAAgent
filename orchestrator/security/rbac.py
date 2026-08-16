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

"""Small role/scope layer for Mission Control v2 APIs.

Service tokens are stored as SHA-256 hashes in a JSON file, never as plaintext.
Example file:
{
  "<sha256-of-token>": {"subject": "github-actions", "role": "operator"}
}
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request

ROLE_SCOPES = {
    "viewer": {"jobs:read", "findings:read", "schedules:read", "audit:read", "engagements:read"},
    "operator": {
        "jobs:read", "jobs:write", "findings:read", "findings:write",
        "schedules:read", "schedules:write", "audit:read", "engagements:read",
    },
    "admin": {"*"},
}


@dataclass(frozen=True)
class Identity:
    subject: str
    role: str
    scopes: frozenset[str]
    auth_type: str

    def allows(self, scope: str) -> bool:
        return "*" in self.scopes or scope in self.scopes


def _token_records() -> dict[str, dict[str, Any]]:
    path = os.environ.get("ZYVOR_API_TOKENS_FILE", "").strip()
    if not path:
        return {}
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("unable to load ZYVOR_API_TOKENS_FILE") from exc
    if not isinstance(raw, dict):
        raise RuntimeError("ZYVOR_API_TOKENS_FILE must contain a JSON object")
    return raw


def identify(request: Request) -> Identity:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        token = header[7:].strip()
        digest = hashlib.sha256(token.encode()).hexdigest()
        for expected, record in _token_records().items():
            if hmac.compare_digest(digest, expected):
                role = str(record.get("role", "viewer"))
                scopes = set(ROLE_SCOPES.get(role, ROLE_SCOPES["viewer"]))
                scopes.update(str(v) for v in record.get("scopes", []))
                return Identity(str(record.get("subject", "service-token")), role, frozenset(scopes), "token")
        raise HTTPException(status_code=401, detail="invalid API token")

    # Existing dashboard middleware already authenticated the signed cookie.
    from orchestrator.dashboard import auth

    if auth.enabled() and auth.is_authenticated(request):
        return Identity(auth.username(), "admin", frozenset({"*"}), "session")
    if not auth.enabled() and os.environ.get("ZYVOR_ENV", "development").lower() != "production":
        return Identity("local-development", "admin", frozenset({"*"}), "development")
    raise HTTPException(status_code=401, detail="authentication required")


def require_scope(request: Request, scope: str) -> Identity:
    identity = identify(request)
    if not identity.allows(scope):
        raise HTTPException(status_code=403, detail=f"missing scope: {scope}")
    return identity
