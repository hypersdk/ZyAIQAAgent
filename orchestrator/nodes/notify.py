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

"""Send notifications to configured channels."""

from __future__ import annotations

from agents.common.models import PipelineReport
from agents.reporter.notify import notify_all
from orchestrator.state import PipelineState


def notify_channels(state: PipelineState) -> PipelineState:
    """Notify GitHub, Slack, Teams, Email."""
    test_results = state.get("test_results")
    if not test_results:
        return state

    metadata = state.get("metadata", {})
    report = PipelineReport(
        summary=state.get("report_summary") or "",
        passed=test_results.passed,
        failed=test_results.failed,
        total=test_results.total,
        failure_analysis=state.get("failure_analysis"),
        html_path=state.get("report_path"),
        pdf_path=state.get("pdf_report_path"),
        coverage_inventory_size=metadata.get("coverage_inventory_size"),
        coverage_gaps_remaining=metadata.get("coverage_gaps_remaining"),
        coverage_tests_generated=metadata.get("coverage_tests_generated"),
        v8_coverage_percentage=metadata.get("v8_coverage_percentage"),
    )

    notify_all(
        report=report,
        repo_full_name=state.get("repo_full_name"),
        pr_number=state.get("pr_number"),
    )

    return state
