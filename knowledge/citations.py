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

"""Citation allow-list validation and evidence-based confidence scoring."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from knowledge.schemas import Citation, QAResponse, SourceArtifact

Confidence = Literal["high", "medium", "low"]


def _freshness(updated_at: str | None) -> float:
    if not updated_at:
        return 0.35
    try:
        parsed = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            parsed = date.fromisoformat(updated_at)
        except ValueError:
            return 0.35
    age_days = max((date.today() - parsed).days, 0)
    if age_days <= 90:
        return 1.0
    if age_days <= 365:
        return 0.7
    if age_days <= 730:
        return 0.4
    return 0.2


def compute_confidence(
    *,
    artifacts: list[SourceArtifact],
    validated_citations: list[Citation],
    insufficient_context: bool,
) -> tuple[Confidence, float]:
    """Derive confidence from retrieval quality — not from the model alone.

    Combines top retrieval score, citation coverage, source freshness and
    multi-source agreement; penalises empty/weak evidence.
    """
    if not artifacts or not validated_citations:
        return "low", 0.0

    top_score = max(item.score for item in artifacts)
    cited_ids = {c.document_id for c in validated_citations}
    cited_artifacts = [a for a in artifacts if a.document_id in cited_ids]
    coverage = len(validated_citations) / max(min(len(artifacts), 3), 1)
    freshness = sum(_freshness(a.updated_at) for a in cited_artifacts) / max(
        len(cited_artifacts), 1
    )
    products = {a.product for a in cited_artifacts if a.product}
    agreement = 1.0 if len(products) <= 1 else 0.55

    composite = (
        0.45 * min(max(top_score, 0.0), 1.0)
        + 0.25 * min(coverage, 1.0)
        + 0.15 * freshness
        + 0.15 * agreement
    )
    if insufficient_context:
        composite *= 0.5

    if composite >= 0.72 and len(validated_citations) >= 1 and top_score >= 0.35:
        return "high", round(composite, 4)
    if composite >= 0.4:
        return "medium", round(composite, 4)
    return "low", round(composite, 4)


def validate_response(
    response: QAResponse,
    artifacts: list[SourceArtifact],
) -> QAResponse:
    allowed = {artifact.document_id: artifact for artifact in artifacts}
    validated: list[Citation] = []
    seen: set[str] = set()

    for citation in response.citations:
        source = allowed.get(citation.document_id)
        if source is None or citation.document_id in seen:
            continue
        seen.add(citation.document_id)
        validated.append(
            Citation(
                document_id=source.document_id,
                title=source.title,
                source=source.source,
                section=source.section,
                url=source.url,
            )
        )

    response.citations = validated

    if not artifacts:
        response.confidence = "low"
        response.insufficient_context = True
        if "No relevant source was retrieved." not in response.missing_information:
            response.missing_information.append("No relevant source was retrieved.")
        return response

    if not validated:
        response.confidence = "low"
        response.insufficient_context = True
        if "The generated answer did not contain a valid retrieved citation." not in (
            response.missing_information
        ):
            response.missing_information.append(
                "The generated answer did not contain a valid retrieved citation."
            )
        return response

    confidence, _score = compute_confidence(
        artifacts=artifacts,
        validated_citations=validated,
        insufficient_context=response.insufficient_context,
    )
    # Never allow the model to claim higher confidence than evidence supports.
    order = {"low": 0, "medium": 1, "high": 2}
    if order.get(response.confidence, 0) > order[confidence]:
        response.confidence = confidence
    else:
        # Also raise low model confidence when evidence is strong? Keep conservative:
        response.confidence = confidence

    if confidence == "low":
        response.insufficient_context = True

    return response
