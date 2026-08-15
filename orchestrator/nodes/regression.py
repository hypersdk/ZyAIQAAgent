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
    """Compare screenshots against baselines when ENABLE_REGRESSION=true.

    Runs in parallel with api_validate/log_analyze/v8_coverage (all read-only
    on `test_results`), so it must return only the key it changes rather than
    a full state spread — `merge_results` is the sole node that writes the
    aggregated fields back onto `test_results` after the fan-in.
    """
    if os.environ.get("ENABLE_REGRESSION", "false").lower() != "true":
        return {}

    test_results = state.get("test_results")
    if not test_results:
        return {}

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

    return {"regression_diffs": diffs}
