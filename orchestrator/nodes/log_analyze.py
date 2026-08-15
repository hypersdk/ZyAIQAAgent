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

"""Browser log analysis node."""

from __future__ import annotations

from agents.logs.analyzer import analyze_test_results
from orchestrator.state import PipelineState


def log_analyze(state: PipelineState) -> PipelineState:
    """Analyze console and network logs from test results.

    Runs in parallel with regression/api_validate/v8_coverage (all read-only
    on `test_results`), so it must return only the key it changes rather than
    a full state spread — `merge_results` is the sole node that writes the
    aggregated fields back onto `test_results` after the fan-in.
    """
    test_results = state.get("test_results")
    if not test_results:
        return {}

    issues = analyze_test_results(test_results)
    return {"log_issues": issues}
