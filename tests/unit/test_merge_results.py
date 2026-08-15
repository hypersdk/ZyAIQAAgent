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

from agents.common.models import ApiValidationResult, LogIssue, RegressionDiff, TestResult
from orchestrator.nodes.merge_results import merge_results


def test_merge_results_copies_parallel_outputs_onto_test_results():
    test_results = TestResult(passed=1, failed=0, total=1, cases=[])
    regression_diffs = [RegressionDiff(file="a.png", status="fail")]
    api_validations = [ApiValidationResult(url="/x", passed=False)]
    log_issues = [LogIssue(test_title="t", severity="error", source="console", message="boom")]

    result = merge_results(
        {
            "test_results": test_results,
            "regression_diffs": regression_diffs,
            "api_validations": api_validations,
            "log_issues": log_issues,
        }
    )

    merged = result["test_results"]
    assert merged is test_results
    assert merged.regression_diffs == regression_diffs
    assert merged.api_validations == api_validations
    assert merged.log_issues == log_issues


def test_merge_results_noop_without_test_results():
    assert merge_results({}) == {}
