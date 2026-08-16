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

"""Loads and validates the curated adversarial-prompt battery
(`agents/redteam/prompts/llm_redteam_battery.yaml`)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

VALID_CATEGORIES = {
    "prompt_injection",
    "system_prompt_exfiltration",
    "excessive_agency",
    "jailbreak",
    "pii_secret_exfiltration",
}
VALID_SEVERITIES = {"critical", "high", "medium", "low"}

# OWASP LLM Top 10 (2025) tag for each battery category — populates the
# `category` field on findings this job raises.
OWASP_CATEGORY_MAP: dict[str, str] = {
    "prompt_injection": "LLM01",
    "system_prompt_exfiltration": "LLM07",
    "excessive_agency": "LLM06",
    "jailbreak": "LLM01",
    "pii_secret_exfiltration": "LLM02",
}

_BATTERY_PATH = Path(__file__).resolve().parent / "prompts" / "llm_redteam_battery.yaml"


@dataclass(frozen=True)
class AttackPrompt:
    id: str
    category: str
    severity_if_failed: str
    prompt: str
    judge_rubric: str


def load_battery(categories: set[str] | None = None, *, path: Path | None = None) -> list[AttackPrompt]:
    """Load battery entries, optionally filtered to `categories`.

    Raises ValueError on a malformed file — this is config validated at job
    param time (`orchestrator/dashboard/jobs.py`'s `_validate()`), not
    something a caller's YAML edit should silently degrade."""
    target = path or _BATTERY_PATH
    raw = yaml.safe_load(target.read_text(encoding="utf-8")) or []
    if not isinstance(raw, list):
        raise ValueError("llm_redteam_battery.yaml must be a list of entries")

    prompts: list[AttackPrompt] = []
    seen_ids: set[str] = set()
    for entry in raw:
        entry_id = str(entry.get("id", "")).strip()
        category = str(entry.get("category", "")).strip()
        severity = str(entry.get("severity_if_failed", "")).strip()
        if not entry_id or entry_id in seen_ids:
            raise ValueError(f"battery entry missing a unique id: {entry!r}")
        seen_ids.add(entry_id)
        if category not in VALID_CATEGORIES:
            raise ValueError(f"unknown category {category!r} in entry {entry_id!r}")
        if severity not in VALID_SEVERITIES:
            raise ValueError(f"unknown severity_if_failed {severity!r} in entry {entry_id!r}")
        if not entry.get("prompt") or not entry.get("judge_rubric"):
            raise ValueError(f"entry {entry_id!r} is missing prompt/judge_rubric")
        if categories is not None and category not in categories:
            continue
        prompts.append(
            AttackPrompt(
                id=entry_id,
                category=category,
                severity_if_failed=severity,
                prompt=str(entry["prompt"]).strip(),
                judge_rubric=str(entry["judge_rubric"]).strip(),
            )
        )
    return prompts
