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

"""Durable, deduplicated findings store preserving the existing dashboard API."""

from __future__ import annotations

import hashlib
from typing import Any

from orchestrator.persistence.store import get_store

SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def _fingerprint(source: str, title: str, url: str, where: str) -> str:
    raw = "\x1f".join((source, title.strip().lower(), url.strip().lower(), where.strip().lower()))
    return hashlib.sha256(raw.encode()).hexdigest()


def add(
    source: str,
    severity: str,
    title: str,
    detail: str = "",
    url: str = "",
    where: str = "",
    category: str = "",
) -> None:
    sev = severity if severity in SEVERITY_RANK else "medium"
    get_store().add_finding(
        source, sev, title, detail, url, where,
        fingerprint=_fingerprint(source, title, url, where),
        category=category,
    )


def record_batch(source: str, url: str, items: list[dict[str, Any]]) -> int:
    for item in items:
        add(
            source,
            item.get("severity", "medium"),
            item.get("title", ""),
            item.get("detail", ""),
            url,
            item.get("where", ""),
            item.get("category", ""),
        )
    return len(items)


def listing(limit: int = 200, severity: str | None = None) -> dict[str, Any]:
    return get_store().list_findings(limit, severity)


def clear() -> int:
    return get_store().clear_findings()
