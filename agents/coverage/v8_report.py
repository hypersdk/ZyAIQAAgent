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

"""Aggregate Playwright V8 JS coverage artifacts."""

from __future__ import annotations

import json
import os
from pathlib import Path

from agents.common.models import V8CoverageFile, V8CoverageSummary


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def v8_coverage_enabled() -> bool:
    return os.environ.get("ENABLE_V8_COVERAGE", "false").lower() == "true"


def collect_v8_coverage() -> V8CoverageSummary | None:
    """Aggregate V8 coverage JSON files written during test runs."""
    if not v8_coverage_enabled():
        return None

    coverage_dir = _repo_root() / "reports" / "v8-coverage"
    if not coverage_dir.exists():
        return V8CoverageSummary(total_bytes=0, used_bytes=0, percentage=0.0, files=[])

    total_bytes = 0
    used_bytes = 0
    file_map: dict[str, V8CoverageFile] = {}

    for path in coverage_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        summary = data.get("summary") or data
        total_bytes += int(summary.get("total_bytes", 0))
        used_bytes += int(summary.get("used_bytes", 0))

        for entry in summary.get("files", []):
            url = entry.get("url", "unknown")
            existing = file_map.get(url)
            if existing:
                file_map[url] = V8CoverageFile(
                    url=url,
                    total_bytes=existing.total_bytes + entry.get("total_bytes", 0),
                    used_bytes=existing.used_bytes + entry.get("used_bytes", 0),
                    percentage=0.0,
                )
            else:
                file_map[url] = V8CoverageFile(
                    url=url,
                    total_bytes=entry.get("total_bytes", 0),
                    used_bytes=entry.get("used_bytes", 0),
                    percentage=entry.get("percentage", 0.0),
                )

    files = []
    for item in file_map.values():
        pct = (item.used_bytes / item.total_bytes * 100) if item.total_bytes else 0.0
        files.append(
            V8CoverageFile(
                url=item.url,
                total_bytes=item.total_bytes,
                used_bytes=item.used_bytes,
                percentage=round(pct, 2),
            )
        )
    files.sort(key=lambda f: f.percentage)

    percentage = round((used_bytes / total_bytes * 100), 2) if total_bytes else 0.0
    return V8CoverageSummary(
        total_bytes=total_bytes,
        used_bytes=used_bytes,
        percentage=percentage,
        files=files,
    )
