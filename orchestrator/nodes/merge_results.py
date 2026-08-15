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

"""Join point for the parallel post-execution analysis fan-out.

regression/api_validate/log_analyze/v8_coverage all run concurrently off of
`execute` and each write only their own top-level list. This node is the
single place that copies those lists onto the shared `test_results` object,
so downstream code (routing, reporter, analyzer) can keep reading
`test_results.regression_diffs` / `.api_validations` / `.log_issues` as
before.
"""

from __future__ import annotations

from orchestrator.state import PipelineState


def merge_results(state: PipelineState) -> PipelineState:
    """Copy the parallel analysis outputs onto `test_results`."""
    test_results = state.get("test_results")
    if not test_results:
        return {}

    test_results.regression_diffs = state.get("regression_diffs", [])
    test_results.api_validations = state.get("api_validations", [])
    test_results.log_issues = state.get("log_issues", [])
    return {"test_results": test_results}
