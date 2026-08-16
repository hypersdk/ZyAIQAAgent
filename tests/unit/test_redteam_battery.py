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

"""Unit tests for agents/redteam/battery.py."""

from __future__ import annotations

import pytest

from agents.redteam.battery import OWASP_CATEGORY_MAP, VALID_CATEGORIES, VALID_SEVERITIES, load_battery


def test_battery_loads_with_enough_entries():
    battery = load_battery()
    assert len(battery) >= 10


def test_all_entries_have_valid_category_and_severity():
    for attack in load_battery():
        assert attack.category in VALID_CATEGORIES
        assert attack.severity_if_failed in VALID_SEVERITIES
        assert attack.prompt.strip()
        assert attack.judge_rubric.strip()


def test_ids_are_unique():
    ids = [a.id for a in load_battery()]
    assert len(ids) == len(set(ids))


def test_category_filter_returns_only_that_category():
    filtered = load_battery({"jailbreak"})
    assert filtered
    assert all(a.category == "jailbreak" for a in filtered)


def test_every_category_has_an_owasp_mapping():
    for category in VALID_CATEGORIES:
        assert category in OWASP_CATEGORY_MAP


def test_malformed_battery_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "- id: x\n  category: not-a-real-category\n  severity_if_failed: high\n  prompt: p\n  judge_rubric: r\n"
    )
    with pytest.raises(ValueError):
        load_battery(path=bad)


def test_duplicate_id_raises(tmp_path):
    dup = tmp_path / "dup.yaml"
    dup.write_text(
        "- id: x\n  category: jailbreak\n  severity_if_failed: low\n  prompt: p\n  judge_rubric: r\n"
        "- id: x\n  category: jailbreak\n  severity_if_failed: low\n  prompt: p2\n  judge_rubric: r2\n"
    )
    with pytest.raises(ValueError):
        load_battery(path=dup)
