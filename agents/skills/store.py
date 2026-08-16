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

"""File-based store for confirmed autofix skills.

Lets the autofix loop reuse a selector fix that was already patched and
confirmed passing in a previous run, instead of asking the LLM to
re-derive it every time the same failure shows up.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Optional

from agents.common.models import AutofixSuggestion, Skill

DEFAULT_SKILLS_PATH = Path(".zyvor-argus/skills.json")
_LEGACY_SKILLS_PATH = Path(".zyvor-qa/skills.json")


def _resolve_path(path: Optional[Path] = None) -> Path:
    if path is not None:
        return Path(path)
    env_path = os.environ.get("SKILLS_PATH")
    return Path(env_path) if env_path else DEFAULT_SKILLS_PATH


def load_skills(path: Optional[Path] = None) -> list[Skill]:
    """Load the skill store, or an empty list if it doesn't exist yet."""
    resolved = _resolve_path(path)
    if (
        not resolved.exists()
        and path is None
        and not os.environ.get("SKILLS_PATH")
        and _LEGACY_SKILLS_PATH.exists()
    ):
        # One-time fallback so skills learned under the old .zyvor-qa/ dir
        # aren't silently lost after the rename to .zyvor-argus/.
        resolved = _LEGACY_SKILLS_PATH
    if not resolved.exists():
        return []
    data = json.loads(resolved.read_text(encoding="utf-8"))
    return [Skill.model_validate(item) for item in data]


def save_skills(skills: list[Skill], path: Optional[Path] = None) -> None:
    """Persist the skill store as JSON."""
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        json.dumps([skill.model_dump() for skill in skills], indent=2),
        encoding="utf-8",
    )


def find_skill(
    skills: list[Skill],
    original_selector: str,
    test_title: Optional[str] = None,
) -> Optional[Skill]:
    """Find a remembered fix for a broken selector.

    Prefers a skill recorded for the same test title over a generic one
    that only matches on the selector text.
    """
    if not original_selector or original_selector.strip().lower() == "unknown":
        return None

    needle = original_selector.strip().lower()
    generic: Optional[Skill] = None
    for skill in skills:
        if skill.original_selector.strip().lower() != needle:
            continue
        if skill.test_title and test_title and skill.test_title == test_title:
            return skill
        if not skill.test_title and generic is None:
            generic = skill
    return generic


def record_confirmed_fix(
    skills: list[Skill],
    suggestion: AutofixSuggestion,
    run_id: Optional[str] = None,
) -> list[Skill]:
    """Upsert a skill from a suggestion that was applied and confirmed passing."""
    original = suggestion.original_selector.strip()
    if not original or original.lower() == "unknown":
        return skills

    needle = original.lower()
    for index, skill in enumerate(skills):
        if (
            skill.original_selector.strip().lower() == needle
            and skill.test_title == suggestion.test_title
        ):
            skills[index] = skill.model_copy(
                update={
                    "suggested_selector": suggestion.suggested_selector,
                    "explanation": suggestion.explanation,
                    "confidence": suggestion.confidence,
                    "times_confirmed": skill.times_confirmed + 1,
                    "last_confirmed_run": run_id,
                }
            )
            return skills

    skills.append(
        Skill(
            id=str(uuid.uuid4()),
            original_selector=original,
            suggested_selector=suggestion.suggested_selector,
            test_title=suggestion.test_title,
            confidence=suggestion.confidence,
            explanation=suggestion.explanation,
            created_run=run_id,
            last_confirmed_run=run_id,
        )
    )
    return skills
