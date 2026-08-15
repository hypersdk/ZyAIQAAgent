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

"""Specialised Zyvor knowledge retrieval tools for the QA agent."""

from __future__ import annotations

from typing import Any

from langchain.tools import tool

from knowledge.retrieval import KnowledgeRetriever
from knowledge.schemas import SourceArtifact

RETRIEVER = KnowledgeRetriever()

# Tool name → default metadata.source filter (API/UI filters still win via RequestContext).
TOOL_DOCUMENT_TYPES: dict[str, str | None] = {
    "search_zyvor_knowledge": None,
    "search_product_manuals": "customer-manual",
    "search_api_reference": "api-reference",
    "search_github_code": "github",
    "search_migration_guides": "migration-guide",
    "search_known_issues": "known-issue",
    "search_customer_runbooks": "runbook",
}

SPECIALISED_TOOL_NAMES = tuple(
    name for name in TOOL_DOCUMENT_TYPES if name != "search_zyvor_knowledge"
)


def format_artifacts(artifacts: list[SourceArtifact]) -> tuple[str, list[dict[str, Any]]]:
    if not artifacts:
        return (
            "No authorized, relevant documents were found. Do not guess.",
            [],
        )

    model_context: list[str] = []
    for index, source in enumerate(artifacts, start=1):
        model_context.append(
            "\n".join(
                [
                    f"[SOURCE {index}]",
                    f"document_id: {source.document_id}",
                    f"title: {source.title}",
                    f"source: {source.source}",
                    f"product: {source.product or 'unknown'}",
                    f"version: {source.version or 'unknown'}",
                    f"section: {source.section or 'unknown'}",
                    f"updated_at: {source.updated_at or 'unknown'}",
                    f"url: {source.url or ''}",
                    f"retrieval_score: {source.score}",
                    "content:",
                    source.content,
                ]
            )
        )

    return "\n\n".join(model_context), [artifact.model_dump() for artifact in artifacts]


def _search(
    query: str,
    *,
    product: str | None,
    document_type: str | None,
) -> tuple[str, list[dict[str, Any]]]:
    artifacts = RETRIEVER.retrieve(
        query,
        product=product,
        document_type=document_type,
    )
    return format_artifacts(artifacts)


@tool(response_format="content_and_artifact")
def search_zyvor_knowledge(
    query: str,
    product: str | None = None,
    document_type: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Broad search across authorized Zyvor manuals, APIs, runbooks and docs.

    Prefer a specialised tool when the question clearly targets manuals, APIs,
    GitHub/code, migration guides, known issues or customer runbooks.
    """

    return _search(query, product=product, document_type=document_type)


@tool(response_format="content_and_artifact")
def search_product_manuals(
    query: str,
    product: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Search Zyvor customer product manuals and how-to guides."""

    return _search(query, product=product, document_type="customer-manual")


@tool(response_format="content_and_artifact")
def search_api_reference(
    query: str,
    product: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Search Zyvor API reference docs for endpoints, schemas and operations."""

    return _search(query, product=product, document_type="api-reference")


@tool(response_format="content_and_artifact")
def search_github_code(
    query: str,
    product: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Search indexed Zyvor GitHub / source-code excerpts (symbols, configs, crates)."""

    return _search(query, product=product, document_type="github")


@tool(response_format="content_and_artifact")
def search_migration_guides(
    query: str,
    product: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Search VMware→KubeVirt / HyperSDK and related migration guides."""

    return _search(query, product=product, document_type="migration-guide")


@tool(response_format="content_and_artifact")
def search_known_issues(
    query: str,
    product: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Search known issues, incident notes and troubleshooting bulletins."""

    return _search(query, product=product, document_type="known-issue")


@tool(response_format="content_and_artifact")
def search_customer_runbooks(
    query: str,
    product: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Search customer/support runbooks for operational procedures."""

    return _search(query, product=product, document_type="runbook")


KNOWLEDGE_TOOLS = [
    search_zyvor_knowledge,
    search_product_manuals,
    search_api_reference,
    search_github_code,
    search_migration_guides,
    search_known_issues,
    search_customer_runbooks,
]

KNOWLEDGE_TOOL_NAMES = [tool_obj.name for tool_obj in KNOWLEDGE_TOOLS]
