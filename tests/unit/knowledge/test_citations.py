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

from knowledge.citations import validate_response
from knowledge.schemas import Citation, QAResponse, SourceArtifact


def source(document_id: str = "doc-1") -> SourceArtifact:
    return SourceArtifact(
        document_id=document_id,
        title="PacketWolf Guide",
        source="manual",
        section="Egress",
        url="https://example.invalid/doc",
        product="PacketWolf",
        version="2.0",
        tenant_id="public",
        access_level="public",
        updated_at="2026-07-30",
        score=0.8,
        content="Use default deny egress.",
    )


def test_hallucinated_citation_is_removed() -> None:
    response = QAResponse(
        answer="Use default deny.",
        confidence="high",
        citations=[
            Citation(
                document_id="made-up",
                title="Wrong",
                source="manual",
            )
        ],
    )
    validated = validate_response(response, [source()])
    assert validated.citations == []
    assert validated.confidence == "low"
    assert validated.insufficient_context is True


def test_citation_metadata_comes_from_retrieval() -> None:
    response = QAResponse(
        answer="Use default deny.",
        confidence="high",
        citations=[
            Citation(
                document_id="doc-1",
                title="Model supplied title",
                source="unknown",
            )
        ],
    )
    validated = validate_response(response, [source()])
    assert validated.citations[0].title == "PacketWolf Guide"
    assert validated.citations[0].section == "Egress"
