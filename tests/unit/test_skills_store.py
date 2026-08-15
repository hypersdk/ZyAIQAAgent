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

from __future__ import annotations

from agents.common.models import AutofixSuggestion, Skill
from agents.skills.store import find_skill, load_skills, record_confirmed_fix, save_skills


def test_round_trip(tmp_path):
    path = tmp_path / "skills.json"
    skill = Skill(
        id="s1",
        original_selector="#old-btn",
        suggested_selector="page.getByRole('button')",
        test_title="t1",
    )
    save_skills([skill], path=path)
    assert load_skills(path=path) == [skill]


def test_load_missing_file_returns_empty(tmp_path):
    assert load_skills(path=tmp_path / "missing.json") == []


def test_find_skill_prefers_specific_test_title():
    generic = Skill(id="g", original_selector="#x", suggested_selector="A")
    specific = Skill(id="s", original_selector="#x", suggested_selector="B", test_title="t1")
    assert find_skill([generic, specific], "#x", "t1") is specific


def test_find_skill_falls_back_to_generic_match():
    generic = Skill(id="g", original_selector="#x", suggested_selector="A")
    assert find_skill([generic], "#x", "other-test") is generic


def test_find_skill_returns_none_for_unknown_selector():
    assert find_skill([], "unknown", "t1") is None


def test_record_confirmed_fix_dedupes_and_bumps_count():
    suggestion = AutofixSuggestion(
        test_title="t1",
        original_selector="#old-btn",
        suggested_selector="page.getByRole('button')",
        confidence="high",
        explanation="fix [applied to x]",
    )
    skills = record_confirmed_fix([], suggestion, run_id="run-1")
    assert len(skills) == 1
    assert skills[0].times_confirmed == 1
    assert skills[0].created_run == "run-1"

    skills = record_confirmed_fix(skills, suggestion, run_id="run-2")
    assert len(skills) == 1
    assert skills[0].times_confirmed == 2
    assert skills[0].last_confirmed_run == "run-2"


def test_record_confirmed_fix_skips_unknown_selector():
    suggestion = AutofixSuggestion(
        test_title="t1",
        original_selector="unknown",
        suggested_selector="x",
    )
    assert record_confirmed_fix([], suggestion) == []
