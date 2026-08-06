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

"""Fetch requirements from GitHub or local specs."""

from __future__ import annotations

import os
from pathlib import Path

from orchestrator.coverage_config import coverage_expansion_enabled
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def fetch_requirements(state: PipelineState) -> PipelineState:
    """Fetch spec files based on source."""
    source = state.get("source", "local")
    spec_paths: list[str] = list(state.get("spec_paths", []))
    spec_contents: list[str] = []
    metadata = dict(state.get("metadata", {}))

    if source == "github":
        repo = state.get("repo_full_name") or os.environ.get("ZYVOR_PRODUCT_REPO", "")
        if not repo:
            return {**state, "error": "ZYVOR_PRODUCT_REPO is not set"}

        from github_integration.client import GitHubClient

        client = GitHubClient()
        if not client.available:
            return {**state, "error": "GitHub token required. Set GITHUB_TOKEN or run `gh auth login`."}

        output_dir = _repo_root() / "tests" / "fixtures" / "fetched"
        requested = [p for p in spec_paths if not Path(p).exists()]
        try:
            if requested:
                spec_paths = client.download_files_to_local(repo, requested, output_dir)
            else:
                spec_paths = client.download_spec_to_local(repo, output_dir)
        except Exception as exc:
            return {**state, "error": f"Failed to fetch spec from GitHub: {exc}"}

        pr_number = state.get("pr_number")
        if pr_number:
            try:
                pr_body = client.fetch_pr_body(repo, pr_number)
                if pr_body.strip():
                    pr_path = output_dir / f"pr-{pr_number}-body.md"
                    pr_path.write_text(f"# PR #{pr_number}\n\n{pr_body}", encoding="utf-8")
                    spec_paths.append(str(pr_path))
                    metadata["pr_body_fetched"] = True
            except Exception:
                pass

            if not metadata.get("changed_files"):
                try:
                    metadata["changed_files"] = client.fetch_pr_changed_files(repo, pr_number)
                except Exception:
                    metadata["changed_files"] = []

        if coverage_expansion_enabled(state):
            code_dir = output_dir / "code"
            scope_paths = metadata.get("changed_files") or None
            try:
                local_paths, repo_paths = client.download_discovery_files_to_local(
                    repo,
                    code_dir,
                    scope_paths=scope_paths,
                )
                metadata["discovered_paths"] = repo_paths
                metadata["discovered_local_paths"] = local_paths
            except Exception as exc:
                metadata["discovery_error"] = str(exc)

    for path in spec_paths:
        p = Path(path)
        if p.exists():
            spec_contents.append(p.read_text(encoding="utf-8"))

    if not spec_paths and source == "local":
        default_spec = _repo_root() / "prompts" / "examples" / "vm-create.md"
        if default_spec.exists():
            spec_paths = [str(default_spec)]
            spec_contents = [default_spec.read_text(encoding="utf-8")]

    return {
        **state,
        "spec_paths": spec_paths,
        "spec_contents": spec_contents,
        "repo_full_name": state.get("repo_full_name") or os.environ.get("ZYVOR_PRODUCT_REPO"),
        "metadata": metadata,
    }
