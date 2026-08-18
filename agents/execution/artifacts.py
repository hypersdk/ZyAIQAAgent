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

"""Collect and persist Playwright failure artifacts (video, screenshot, trace)."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from agents.common.models import TestCaseResult, TestResult


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "test"


def _find_video_attachment(attachments: list) -> str | None:
    for att in attachments:
        name = (att.get("name") or "").lower()
        content_type = (att.get("contentType") or "").lower()
        path = att.get("path")
        if path and (name == "video" or content_type.startswith("video/")):
            return path
    return None


def _copy_if_exists(src: str | None, dest: Path) -> str | None:
    if not src:
        return None
    source = Path(src)
    if not source.exists():
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return str(dest.resolve())


def persist_failure_artifacts(
    test_results: TestResult,
    *,
    artifacts_dir: Path | None = None,
) -> TestResult:
    """Copy failure videos/screenshots/traces to reports/artifacts and update paths."""
    repo_root = _repo_root()
    artifacts_dir = artifacts_dir or (repo_root / "reports" / "artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Also mirror to top-level folders for CI upload conventions
    videos_dir = repo_root / "videos"
    screenshots_dir = repo_root / "screenshots"
    traces_dir = repo_root / "traces"
    for directory in (videos_dir, screenshots_dir, traces_dir):
        directory.mkdir(parents=True, exist_ok=True)

    updated_cases: list[TestCaseResult] = []
    for case in test_results.cases:
        if case.status == "passed":
            updated_cases.append(case)
            continue

        slug = _slugify(case.title)
        case_dir = artifacts_dir / slug
        case_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = _copy_if_exists(
            case.screenshot_path,
            case_dir / "screenshot.png",
        ) or _copy_if_exists(case.screenshot_path, screenshots_dir / f"{slug}.png")

        video_path = _copy_if_exists(
            case.video_path,
            case_dir / "video.webm",
        ) or _copy_if_exists(case.video_path, videos_dir / f"{slug}.webm")

        trace_path = _copy_if_exists(
            case.trace_path,
            case_dir / "trace.zip",
        ) or _copy_if_exists(case.trace_path, traces_dir / f"{slug}.zip")

        updated_cases.append(
            case.model_copy(
                update={
                    "screenshot_path": screenshot_path or case.screenshot_path,
                    "video_path": video_path or case.video_path,
                    "trace_path": trace_path or case.trace_path,
                }
            )
        )

    return test_results.model_copy(update={"cases": updated_cases})


def discover_videos_from_output_dir(
    test_results: TestResult,
    test_results_dir: Path,
) -> TestResult:
    """Fallback: match video.webm files in test-results when JSON attachment path is missing."""
    if not test_results_dir.exists():
        return test_results

    video_files = list(test_results_dir.rglob("video.webm"))
    if not video_files:
        return test_results

    updated_cases: list[TestCaseResult] = []
    used_videos: set[Path] = set()

    for case in test_results.cases:
        if case.status == "passed" or case.video_path:
            updated_cases.append(case)
            continue

        slug = _slugify(case.title)
        matched = None
        for video in video_files:
            if video in used_videos:
                continue
            folder = video.parent.name.lower()
            if slug in folder or slug.replace("-", "") in folder.replace("-", ""):
                matched = video
                break

        if not matched:
            for video in video_files:
                if video not in used_videos:
                    matched = video
                    break

        if matched:
            used_videos.add(matched)
            updated_cases.append(case.model_copy(update={"video_path": str(matched.resolve())}))
        else:
            updated_cases.append(case)

    return test_results.model_copy(update={"cases": updated_cases})
