"""Screenshot regression node."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from agents.regression.compare_screenshots import (
    collect_screenshots_from_test_results,
    compare_screenshots,
)
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def regression_check(state: PipelineState) -> PipelineState:
    """Compare screenshots against baselines when ENABLE_REGRESSION=true."""
    if os.environ.get("ENABLE_REGRESSION", "false").lower() != "true":
        return state

    test_results = state.get("test_results")
    if not test_results:
        return state

    repo = _repo_root()
    baseline_dir = repo / "screenshots" / "baselines"
    current_dir = repo / "screenshots" / "current"
    current_dir.mkdir(parents=True, exist_ok=True)

    test_results_dir = repo / "test-results"
    for png in collect_screenshots_from_test_results(test_results_dir):
        dest = current_dir / png.name
        shutil.copy2(png, dest)

    for case in test_results.cases:
        if case.screenshot_path and Path(case.screenshot_path).exists():
            safe_name = case.title.replace(" ", "-").replace("/", "-") + ".png"
            shutil.copy2(case.screenshot_path, current_dir / safe_name)

    threshold = float(os.environ.get("REGRESSION_THRESHOLD", "1.0"))
    diffs = compare_screenshots(
        baseline_dir=baseline_dir,
        current_dir=current_dir,
        diff_dir=repo / "screenshots" / "diffs",
        threshold=threshold,
    )

    test_results.regression_diffs = diffs
    return {**state, "test_results": test_results, "regression_diffs": diffs}
