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

"""API validation node."""

from __future__ import annotations

import os
from pathlib import Path

from agents.api_validation.validator import load_har_validations, validate_test_results
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def api_validate(state: PipelineState) -> PipelineState:
    """Validate API responses when ENABLE_API_VALIDATION=true.

    Runs in parallel with regression/log_analyze/v8_coverage (all read-only
    on `test_results`), so it must return only the key it changes rather than
    a full state spread — `merge_results` is the sole node that writes the
    aggregated fields back onto `test_results` after the fan-in.
    """
    if os.environ.get("ENABLE_API_VALIDATION", "false").lower() != "true":
        return {}

    test_results = state.get("test_results")
    if not test_results:
        return {}

    validations = validate_test_results(test_results)

    har_dir = _repo_root() / "traces"
    for har in har_dir.glob("*.har"):
        validations.extend(load_har_validations(har))

    return {"api_validations": validations}
