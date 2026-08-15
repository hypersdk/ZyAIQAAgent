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

"""Unit tests for specialised knowledge tools (no Qdrant required)."""

from __future__ import annotations

import pytest

pytest.importorskip("langchain.tools")

from knowledge.schemas import SourceArtifact
from knowledge.tools import (
    KNOWLEDGE_TOOL_NAMES,
    TOOL_DOCUMENT_TYPES,
    format_artifacts,
)


def test_specialised_tools_are_registered() -> None:
    expected = {
        "search_zyvor_knowledge",
        "search_product_manuals",
        "search_api_reference",
        "search_github_code",
        "search_migration_guides",
        "search_known_issues",
        "search_customer_runbooks",
    }
    assert expected == set(KNOWLEDGE_TOOL_NAMES)
    assert TOOL_DOCUMENT_TYPES["search_product_manuals"] == "customer-manual"
    assert TOOL_DOCUMENT_TYPES["search_migration_guides"] == "migration-guide"
    assert TOOL_DOCUMENT_TYPES["search_zyvor_knowledge"] is None


def test_format_artifacts_empty() -> None:
    content, artifacts = format_artifacts([])
    assert "Do not guess" in content
    assert artifacts == []


def test_format_artifacts_includes_document_id() -> None:
    source = SourceArtifact(
        document_id="doc-1",
        title="Guide",
        source="customer-manual",
        section="Egress",
        url="https://example.invalid",
        product="PacketWolf",
        version="2.0",
        tenant_id="public",
        access_level="public",
        updated_at="2026-07-30",
        score=0.9,
        content="default deny",
    )
    content, artifacts = format_artifacts([source])
    assert "document_id: doc-1" in content
    assert artifacts[0]["document_id"] == "doc-1"
