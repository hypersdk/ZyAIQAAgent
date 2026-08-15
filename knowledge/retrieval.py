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

import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from langchain_core.documents import Document

from knowledge.config import get_settings
from knowledge.context import current_context
from knowledge.schemas import SourceArtifact


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_.:/-]+")
ERROR_PATTERN = re.compile(
    r"(?:error|failed|failure|timeout|timed?\s*out|timing\s+out|exception|denied|unreachable)[^\n]{0,180}",
    re.IGNORECASE,
)

PRODUCT_ALIASES = {
    "packetwolf": ["packet wolf", "cilium", "hubble", "network policy"],
    "hypersdk": ["hyper sdk", "vmware migration", "hyper2kvm"],
    "zeus os": ["zeusos", "zeus-os", "kubevirt"],
    "guestkit": ["guest kit", "qcow2 inspection", "vmdk inspection"],
    "machina": ["libvirt", "kvm management"],
    "veyron": ["vm command center", "kubevirt vm"],
    "aether": ["runtime portability", "podman kubernetes kubevirt"],
}


@dataclass
class RankedDocument:
    document: Document
    score: float


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text) if len(token) > 1}


def expand_queries(question: str, product: str | None = None) -> list[str]:
    queries = [question.strip()]
    lowered = question.lower()

    error_match = ERROR_PATTERN.search(question)
    if error_match:
        queries.append(error_match.group(0).strip())

    effective_product = product.lower() if product else None
    if effective_product:
        aliases = PRODUCT_ALIASES.get(effective_product, [])
        if aliases:
            queries.append(f"{question} {' '.join(aliases[:3])}")
    else:
        for product_name, aliases in PRODUCT_ALIASES.items():
            terms = [product_name, *aliases]
            if any(term in lowered for term in terms):
                queries.append(f"{question} {product_name} {' '.join(aliases[:2])}")
                break

    result: list[str] = []
    seen: set[str] = set()
    for query in queries:
        normalized = " ".join(query.split())
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result[:3]


def _freshness_score(updated_at: object) -> float:
    if not isinstance(updated_at, str) or not updated_at:
        return 0.0
    try:
        parsed = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            parsed = date.fromisoformat(updated_at)
        except ValueError:
            return 0.0

    age_days = max((date.today() - parsed).days, 0)
    return math.exp(-age_days / 730.0)


def rerank(
    question: str,
    merged: Iterable[tuple[Document, float]],
    *,
    product: str | None,
    limit: int,
) -> list[RankedDocument]:
    items = list(merged)
    if not items:
        return []

    raw_scores = [score for _, score in items]
    minimum = min(raw_scores)
    maximum = max(raw_scores)
    spread = maximum - minimum

    question_tokens = _tokens(question)
    ranked: list[RankedDocument] = []

    for document, raw_score in items:
        normalized_vector_score = 1.0 if spread == 0 else (raw_score - minimum) / spread
        content_tokens = _tokens(document.page_content)
        overlap = len(question_tokens & content_tokens) / max(len(question_tokens), 1)
        freshness = _freshness_score(document.metadata.get("updated_at"))
        product_match = 0.0
        if product and str(document.metadata.get("product", "")).lower() == product.lower():
            product_match = 1.0

        final_score = (
            0.68 * normalized_vector_score
            + 0.20 * overlap
            + 0.07 * freshness
            + 0.05 * product_match
        )
        ranked.append(RankedDocument(document=document, score=round(final_score, 6)))

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:limit]


class KnowledgeRetriever:
    def retrieve(
        self,
        query: str,
        *,
        product: str | None = None,
        document_type: str | None = None,
    ) -> list[SourceArtifact]:
        # Lazy imports keep offline unit tests free of Qdrant/FastEmbed.
        from knowledge.vectorstore import get_vector_store, qdrant_filter

        settings = get_settings()
        context = current_context()
        effective_product = context.product or product
        effective_document_type = context.document_type or document_type

        query_filter = qdrant_filter(
            tenant_id=context.tenant_id,
            access_levels=context.access_levels,
            product=effective_product,
            document_type=effective_document_type,
        )

        # Reciprocal-rank fusion across deterministic query expansions /
        # optional query-understanding rewrites.
        search_queries = expand_queries(query, effective_product)
        if settings.enable_query_understanding:
            from knowledge.query_understanding import understand_query

            understood = understand_query(query, product=effective_product)
            search_queries = understood.search_queries or search_queries
            if not effective_product and understood.products:
                effective_product = understood.products[0]
                query_filter = qdrant_filter(
                    tenant_id=context.tenant_id,
                    access_levels=context.access_levels,
                    product=effective_product,
                    document_type=effective_document_type,
                )

        fused: dict[str, tuple[Document, float]] = {}
        for expanded_query in search_queries:
            results = get_vector_store().similarity_search_with_score(
                expanded_query,
                k=settings.retrieval_fetch_k,
                filter=query_filter,
            )
            for rank, (document, raw_score) in enumerate(results, start=1):
                document_id = str(
                    document.metadata.get("document_id")
                    or document.metadata.get("_id")
                    or document.id
                )
                rrf = 1.0 / (60 + rank)
                existing = fused.get(document_id)
                if existing is None:
                    fused[document_id] = (document, rrf + float(raw_score) * 0.001)
                else:
                    fused[document_id] = (
                        existing[0],
                        existing[1] + rrf + float(raw_score) * 0.001,
                    )

        ranked = rerank(
            query,
            fused.values(),
            product=effective_product,
            limit=settings.retrieval_k,
        )

        artifacts: list[SourceArtifact] = []
        for item in ranked:
            metadata = item.document.metadata
            artifacts.append(
                SourceArtifact(
                    document_id=str(
                        metadata.get("document_id")
                        or metadata.get("_id")
                        or item.document.id
                    ),
                    title=str(metadata.get("title") or "Untitled"),
                    source=str(metadata.get("source") or "documentation"),
                    section=(
                        str(metadata["section"]) if metadata.get("section") is not None else None
                    ),
                    url=str(metadata["url"]) if metadata.get("url") else None,
                    product=str(metadata["product"]) if metadata.get("product") else None,
                    version=str(metadata["version"]) if metadata.get("version") else None,
                    tenant_id=str(metadata.get("tenant_id") or "unknown"),
                    access_level=str(metadata.get("access_level") or "unknown"),
                    updated_at=(
                        str(metadata["updated_at"]) if metadata.get("updated_at") else None
                    ),
                    score=item.score,
                    content=item.document.page_content,
                )
            )
        return artifacts
