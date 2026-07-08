"""Execute Playwright tests."""

from __future__ import annotations

import os
from pathlib import Path

from agents.execution.runner import run_playwright
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def execute_tests(state: PipelineState) -> PipelineState:
    """Run Playwright test suite."""
    if state.get("error"):
        return state

    base_url = os.environ.get("ZYVOR_BASE_URL", "https://zyvor.dev")
    generated = state.get("generated_tests", [])

    test_dirs: list[str] = [str(_repo_root() / "tests" / "manual")]
    if generated:
        test_dirs.append(str(_repo_root() / "tests" / "generated"))

    test_results = run_playwright(test_dirs=test_dirs, base_url=base_url)
    return {**state, "test_results": test_results}
