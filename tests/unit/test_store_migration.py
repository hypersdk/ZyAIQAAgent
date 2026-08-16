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

"""Unit tests for the schema-v1 -> v2 migration (engagements table, findings.category)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from orchestrator.persistence.store import MissionControlStore


def _create_v1_findings_table(db_path: Path) -> None:
    """Recreates the pre-migration (schema v1) `findings` table shape."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT,
            source TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT,
            url TEXT,
            location TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            occurrences INTEGER NOT NULL DEFAULT 1
        )"""
    )
    conn.execute(
        "INSERT INTO findings (source, severity, title, status, first_seen, last_seen) VALUES (?,?,?,?,?,?)",
        ("legacy", "high", "pre-existing finding", "open", "2025-01-01T00:00:00+00:00", "2025-01-01T00:00:00+00:00"),
    )
    conn.commit()
    conn.close()


def test_migration_adds_category_column_to_preexisting_findings_table(tmp_path):
    db_path = tmp_path / "legacy.db"
    _create_v1_findings_table(db_path)

    store = MissionControlStore(db_path)  # constructor runs migrate()

    result = store.list_findings()
    assert result["total"] == 1
    assert result["findings"][0]["category"] == ""


def test_migration_is_idempotent(tmp_path):
    db_path = tmp_path / "legacy.db"
    _create_v1_findings_table(db_path)
    MissionControlStore(db_path)
    MissionControlStore(db_path)  # a second migrate() pass must not error


def test_engagements_crud(tmp_path):
    store = MissionControlStore(tmp_path / "fresh.db")
    engagement = store.create_engagement(
        "example.com", "authorized pentest of our own staging", "active_recon", authorized_by="admin"
    )
    assert engagement["target_pattern"] == "example.com"
    assert engagement["revoked_at"] is None

    assert store.get_engagement(engagement["id"]) == engagement
    assert len(store.list_engagements()) == 1

    assert store.revoke_engagement(engagement["id"], revoked_by="admin") is True
    revoked = store.get_engagement(engagement["id"])
    assert revoked["revoked_at"] is not None
    assert revoked["revoked_by"] == "admin"
    # revoking an already-revoked engagement is a no-op, not an error
    assert store.revoke_engagement(engagement["id"], revoked_by="admin") is False


def test_add_finding_persists_category(tmp_path):
    store = MissionControlStore(tmp_path / "findings.db")
    store.add_finding("misconfig_scan", "high", "exposed .env", url="https://x.io", category="admin-panel-exposure")
    result = store.list_findings()
    assert result["findings"][0]["category"] == "admin-panel-exposure"
