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

"""Screenshot regression comparison using Pillow."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from agents.common.models import RegressionDiff

try:
    from PIL import Image, ImageChops
except ImportError:
    Image = None  # type: ignore


def _diff_percent(img1: "Image.Image", img2: "Image.Image") -> float:
    diff = ImageChops.difference(img1, img2)
    pixels = list(diff.getdata())
    total = len(pixels) * 3
    changed = sum(sum(p) for p in pixels)
    return (changed / (total * 255)) * 100 if total else 0.0


def compare_screenshots(
    baseline_dir: str | Path,
    current_dir: str | Path,
    diff_dir: str | Path | None = None,
    threshold: float = 1.0,
    update_baselines: bool = False,
) -> list[RegressionDiff]:
    """
    Compare screenshots between baseline and current runs.

    If a baseline is missing and update_baselines=True, copy current as baseline.
    """
    if Image is None:
        return [
            RegressionDiff(
                file="*",
                status="fail",
                message="Pillow is required for screenshot regression. pip install Pillow",
            )
        ]

    baseline_dir = Path(baseline_dir)
    current_dir = Path(current_dir)
    diff_dir = Path(diff_dir or current_dir.parent / "diffs")
    diff_dir.mkdir(parents=True, exist_ok=True)
    baseline_dir.mkdir(parents=True, exist_ok=True)

    if not current_dir.exists():
        return []

    diffs: list[RegressionDiff] = []

    for current in sorted(current_dir.glob("*.png")):
        baseline = baseline_dir / current.name
        diff_path = diff_dir / f"diff-{current.name}"

        if os.environ.get("ENABLE_RUST_PROCESSOR", "false").lower() == "true":
            from agents.regression.rust_bridge import compare_with_rust, rust_diff_available

            if rust_diff_available() and baseline.exists():
                diffs.append(
                    compare_with_rust(baseline, current, diff_path, threshold)
                )
                continue

        if not baseline.exists():
            if update_baselines or os.environ.get("UPDATE_BASELINES", "false").lower() == "true":
                shutil.copy2(current, baseline)
                diffs.append(
                    RegressionDiff(
                        file=current.name,
                        status="new_baseline",
                        message=f"Created baseline: {baseline}",
                    )
                )
            else:
                diffs.append(
                    RegressionDiff(
                        file=current.name,
                        status="fail",
                        message=f"No baseline for {current.name}. Run with UPDATE_BASELINES=true",
                    )
                )
            continue

        img_base = Image.open(baseline).convert("RGB")
        img_curr = Image.open(current).convert("RGB")

        if img_base.size != img_curr.size:
            img_curr = img_curr.resize(img_base.size)

        pct = _diff_percent(img_base, img_curr)
        diff_image = ImageChops.difference(img_base, img_curr)
        diff_path = diff_dir / f"diff-{current.name}"
        diff_image.save(diff_path)

        if pct > threshold:
            diffs.append(
                RegressionDiff(
                    file=current.name,
                    status="fail",
                    diff_percent=round(pct, 3),
                    diff_image_path=str(diff_path),
                    message=f"Visual diff {pct:.2f}% exceeds threshold {threshold}%",
                )
            )
        else:
            diffs.append(
                RegressionDiff(
                    file=current.name,
                    status="pass",
                    diff_percent=round(pct, 3),
                    diff_image_path=str(diff_path),
                )
            )

    return diffs


def collect_screenshots_from_test_results(test_results_dir: str | Path) -> list[Path]:
    """Collect PNG screenshots from Playwright test-results output.

    Skips Playwright native snapshot dirs (``*-snapshots``) so ``toHaveScreenshot``
    baselines are not double-diffed by the Pillow/Rust regression pipeline.
    """
    root = Path(test_results_dir)
    if not root.exists():
        return []
    out: list[Path] = []
    for png in root.rglob("*.png"):
        parts = {p.lower() for p in png.parts}
        joined = str(png).lower()
        if any(p.endswith("-snapshots") or p == "snapshots" for p in parts):
            continue
        if "-snapshots" in joined or "/snapshots/" in joined:
            continue
        out.append(png)
    return out
