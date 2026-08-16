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

"""Write reports/summary.json — the stable, CI-facing result contract.

External CI systems (GitHub Actions, GitLab, CircleCI, Jenkins, Azure
Pipelines) need one small machine-readable file to gate on, independent of
Playwright's own reporter schema. This is that file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def write_ci_summary(
    *,
    command: str,
    target_url: str | None,
    passed: int,
    failed: int,
    total: int,
    exit_code: int,
    started_at: str,
    duration_s: float,
    skipped: int = 0,
    artifacts: dict[str, str | None] | None = None,
    extra: dict[str, Any] | None = None,
    findings_by_severity: dict[str, int] | None = None,
    max_severity: str | None = None,
) -> Path:
    """Write reports/summary.json and return its path.

    `findings_by_severity`/`max_severity` are optional — only commands that
    raise findings (audit, misconfig_scan, cve_lookup, llm_redteam) populate
    them; `zyvor-qa <cmd> --fail-on <severity>` reads `max_severity` back to
    decide whether to exit non-zero.
    """
    summary = {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "target_url": target_url,
        "started_at": started_at,
        "duration_s": round(duration_s, 3),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": total,
        "exit_code": exit_code,
        "status": "passed" if failed == 0 and exit_code == 0 else "failed",
        "artifacts": artifacts or {},
        "findings_by_severity": findings_by_severity or {},
        "max_severity": max_severity,
        "extra": extra or {},
    }
    reports_dir = _repo_root() / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / "summary.json"
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return path
