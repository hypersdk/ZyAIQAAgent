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

"""Rule-based requirement quality scoring — no LLM required.

Structural signals only: it can't judge whether a requirement is *semantically*
ambiguous, only whether it has the shape of a testable one (steps, assertions,
no obviously vague language). This is the honest floor the LLM path improves on.
"""

from __future__ import annotations

from agents.common.models import QualityIssue, Requirement, RequirementQuality

_VAGUE_PHRASES = (
    "should work",
    "work correctly",
    "work properly",
    "handle properly",
    "handle correctly",
    "be fast",
    "be quick",
    "look good",
    "looks good",
    "as expected",
    "appropriately",
)


def evaluate_requirement_quality_rule_based(req: Requirement) -> RequirementQuality:
    issues: list[QualityIssue] = []
    score = 100.0

    if not req.steps:
        issues.append(
            QualityIssue(
                kind="missing_acceptance_criteria",
                severity="high",
                message="No steps at all — nothing here is testable yet.",
            )
        )
        score -= 50
    else:
        unasserted = [s for s in req.steps if s.action not in {"navigate", "wait"} and not s.assertion]
        if unasserted:
            issues.append(
                QualityIssue(
                    kind="missing_acceptance_criteria",
                    severity="medium",
                    message=(
                        f"{len(unasserted)} of {len(req.steps)} step(s) have no assertion — "
                        "an action with no expected outcome can't fail a test."
                    ),
                )
            )
            score -= min(30, 10 * len(unasserted))

    haystack = f"{req.description} " + " ".join(s.assertion or "" for s in req.steps)
    hit_phrases = [phrase for phrase in _VAGUE_PHRASES if phrase in haystack.lower()]
    if hit_phrases:
        issues.append(
            QualityIssue(
                kind="vague_language",
                severity="medium",
                message=f"Unmeasurable language found: {', '.join(sorted(hit_phrases))}.",
            )
        )
        score -= 15

    if len(req.description.strip()) < 15:
        issues.append(
            QualityIssue(
                kind="ambiguous",
                severity="low",
                message="Description is too short to give a reviewer real context.",
            )
        )
        score -= 10

    duplicate_actions = len(req.steps) != len({(s.action, s.target) for s in req.steps})
    if duplicate_actions:
        issues.append(
            QualityIssue(
                kind="contradiction",
                severity="low",
                message="Two or more steps target the same action+element — likely a copy/paste gap.",
            )
        )
        score -= 5

    score = max(0.0, min(100.0, score))
    return RequirementQuality(requirement_id=req.id, score=score, issues=issues)
