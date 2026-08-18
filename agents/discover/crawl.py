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

"""Browser-based live site crawl for coverage discovery."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from agents.common.models import CoverageCandidate


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def live_crawl_enabled() -> bool:
    return os.environ.get("ENABLE_LIVE_CRAWL", "false").lower() == "true"


def crawl_live_site(base_url: str | None = None) -> list[CoverageCandidate]:
    """Crawl the live site and return coverage candidates."""
    if not live_crawl_enabled():
        return []

    repo_root = _repo_root()
    script = repo_root / "playwright" / "scripts" / "crawl-site.mjs"
    if not script.exists():
        return []

    env = {**os.environ}
    url = base_url or os.environ.get("ZYVOR_BASE_URL", "https://zyvor.dev")
    env["ZYVOR_BASE_URL"] = url

    cmd = ["node", str(script), url]
    result = subprocess.run(
        cmd,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=int(os.environ.get("CRAWL_TIMEOUT_SECONDS", "120")),
    )

    if result.returncode != 0:
        inventory_path = repo_root / "reports" / "crawl-inventory.json"
        if inventory_path.exists():
            raw = json.loads(inventory_path.read_text(encoding="utf-8"))
            return [CoverageCandidate.model_validate(item) for item in raw]
        return []

    stdout = result.stdout.strip()
    if not stdout:
        return []

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return []

    return [CoverageCandidate.model_validate(item) for item in data]


def merge_candidates(
    existing: list[CoverageCandidate],
    crawled: list[CoverageCandidate],
) -> list[CoverageCandidate]:
    """Merge and dedupe coverage candidates."""
    seen: set[str] = set()
    merged: list[CoverageCandidate] = []
    for candidate in existing + crawled:
        key = f"{candidate.kind}:{candidate.path}:{candidate.title}"
        if key in seen:
            continue
        seen.add(key)
        merged.append(candidate)
    return merged
