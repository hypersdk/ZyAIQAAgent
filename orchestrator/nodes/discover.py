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

"""Discover coverage inventory from fetched code and docs."""

from __future__ import annotations

import os
from pathlib import Path

from agents.discover.agent import discover_from_files
from agents.discover.crawl import crawl_live_site, merge_candidates
from orchestrator.coverage_config import coverage_expansion_enabled
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def discover_coverage(state: PipelineState) -> PipelineState:
    """Build coverage inventory from discovery files."""
    if state.get("error"):
        return state

    metadata = dict(state.get("metadata", {}))
    code_dir = _repo_root() / "tests" / "fixtures" / "fetched" / "code"
    inventory: list = []

    if coverage_expansion_enabled(state):
        repo_paths = metadata.get("discovered_paths", [])
        if repo_paths and code_dir.exists():
            file_map: dict[str, str] = {}
            for repo_path in repo_paths:
                safe_name = repo_path.replace("/", "__")
                local_path = code_dir / safe_name
                if local_path.exists():
                    try:
                        file_map[repo_path] = local_path.read_text(encoding="utf-8")
                    except Exception:
                        continue
            if file_map:
                inventory = discover_from_files(file_map)

    if os.environ.get("ENABLE_LIVE_CRAWL", "false").lower() == "true":
        crawled = crawl_live_site(os.environ.get("ZYVOR_BASE_URL"))
        inventory = merge_candidates(inventory, crawled)
        metadata["live_crawl_count"] = len(crawled)

    metadata["coverage_inventory_size"] = len(inventory)
    return {
        **state,
        "coverage_inventory": inventory,
        "metadata": metadata,
    }
