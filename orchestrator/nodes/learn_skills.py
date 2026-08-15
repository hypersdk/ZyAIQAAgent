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

"""Remember autofix patches that were applied and confirmed passing."""

from __future__ import annotations

import os

from agents.skills.store import load_skills, record_confirmed_fix, save_skills
from orchestrator.state import PipelineState


def learn_skills_node(state: PipelineState) -> PipelineState:
    """Persist applied autofix suggestions as skills once a retry passes."""
    metadata = state.get("metadata", {})
    test_results = state.get("test_results")

    if not metadata.get("autofix_patched_files"):
        return state
    if not test_results or not test_results.all_passed:
        return state

    run_id = os.environ.get("GITHUB_RUN_ID")
    skills = load_skills()
    for suggestion in state.get("autofix_suggestions", []):
        if "[applied to" not in suggestion.explanation:
            continue
        skills = record_confirmed_fix(skills, suggestion, run_id=run_id)
    save_skills(skills)

    return state
