"""Fetch requirements from GitHub or local specs."""

from __future__ import annotations

import os
from pathlib import Path

from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def fetch_requirements(state: PipelineState) -> PipelineState:
    """Fetch spec files based on source."""
    source = state.get("source", "local")
    spec_paths: list[str] = list(state.get("spec_paths", []))
    spec_contents: list[str] = []

    if source == "github":
        repo = os.environ.get("ZYVOR_PRODUCT_REPO", "")
        if not repo:
            return {**state, "error": "ZYVOR_PRODUCT_REPO is not set"}

        from github.client import GitHubClient

        client = GitHubClient()
        if not client.available:
            return {**state, "error": "GITHUB_TOKEN is required for github source"}

        output_dir = _repo_root() / "tests" / "fixtures" / "fetched"
        spec_paths = client.download_spec_to_local(repo, output_dir)

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
        "repo_full_name": os.environ.get("ZYVOR_PRODUCT_REPO"),
    }
