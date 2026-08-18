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

"""Apply autofix suggestions to Playwright test source files."""

from __future__ import annotations

import re
from pathlib import Path

from agents.common.models import AutofixSuggestion


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def _test_search_dirs() -> list[Path]:
    root = _repo_root()
    return [root / "tests" / "manual", root / "tests" / "generated"]


def find_test_file(test_title: str) -> Path | None:
    """Locate the spec file containing a given test title."""
    patterns = [
        re.compile(rf"test(?:\.(?:only|skip))?\(\s*['\"]{re.escape(test_title)}['\"]"),
        re.compile(rf"test(?:\.(?:only|skip))?\(\s*`{re.escape(test_title)}`"),
    ]
    for directory in _test_search_dirs():
        if not directory.exists():
            continue
        for path in directory.rglob("*.spec.ts"):
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if any(p.search(content) for p in patterns):
                return path
    return None


def _replacement_candidates(suggestion: AutofixSuggestion) -> list[tuple[str, str]]:
    """Build ordered (old, new) replacement pairs for a suggestion."""
    original = suggestion.original_selector.strip()
    suggested = suggestion.suggested_selector.strip()
    pairs: list[tuple[str, str]] = []

    if original and original != "unknown" and suggested:
        pairs.append((original, suggested))

    if suggested.startswith("page."):
        pairs.append((f"page.{original}", suggested))
        pairs.append((f"await page.{original}", f"await {suggested}"))

    for pattern in (
        rf"getByText\(['\"]{re.escape(original)}['\"]\)",
        rf"getByRole\([^)]*name:\s*['\"]{re.escape(original)}['\"][^)]*\)",
        rf"locator\(['\"]{re.escape(original)}['\"]\)",
    ):
        if original and original != "unknown":
            match = re.search(pattern, suggested)
            if not match and "getBy" in suggested:
                pairs.append((pattern.replace(re.escape(original), original), suggested))

    return pairs


def apply_suggestion_to_file(path: Path, suggestion: AutofixSuggestion) -> bool:
    """Apply a single autofix suggestion to a test file. Returns True if modified."""
    if suggestion.confidence == "low" and suggestion.original_selector in {"unknown", ""}:
        return False

    content = path.read_text(encoding="utf-8")
    updated = content

    for old, new in _replacement_candidates(suggestion):
        if old and old in updated:
            updated = updated.replace(old, new, 1)
            break

    if updated != content:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def apply_autofix_patches(
    suggestions: list[AutofixSuggestion],
) -> tuple[list[AutofixSuggestion], list[str]]:
    """Apply autofix suggestions to test files.

    Returns updated suggestions (with applied flag in explanation) and patched file paths.
    """
    patched_files: list[str] = []
    updated: list[AutofixSuggestion] = []

    for suggestion in suggestions:
        path = find_test_file(suggestion.test_title)
        if not path:
            updated.append(suggestion)
            continue

        applied = apply_suggestion_to_file(path, suggestion)
        if applied:
            patched_files.append(str(path))
            updated.append(
                suggestion.model_copy(
                    update={
                        "explanation": (
                            f"{suggestion.explanation} [applied to {path.name}]".strip()
                        ),
                        "confidence": "high",
                    }
                )
            )
        else:
            updated.append(suggestion)

    return updated, patched_files
