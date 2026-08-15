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

"""Deterministic query understanding for product routing and multi-query retrieval."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

Intent = Literal[
    "troubleshooting",
    "installation",
    "api",
    "migration",
    "configuration",
    "comparison",
    "general",
]


class QueryUnderstanding(BaseModel):
    intent: Intent = "general"
    products: list[str] = Field(default_factory=list)
    versions: list[str] = Field(default_factory=list)
    error_messages: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    requires_live_data: bool = False
    rewritten_question: str = ""


_VERSION_RE = re.compile(r"\b(?:v)?(\d+\.\d+(?:\.\d+)?)\b", re.IGNORECASE)
_LIVE_HINTS = re.compile(
    r"\b(right now|currently|is .+ running|live|this cluster|our cluster|pod status|"
    r"hubble.?relay|virt-handler|ceph health|node capacity)\b",
    re.IGNORECASE,
)
_FOLLOWUP_HINTS = re.compile(
    r"\b(that|this|the other cluster|same issue|fix it|there)\b",
    re.IGNORECASE,
)
_ERROR_PATTERN = re.compile(
    r"(?:error|failed|failure|timeout|timed?\s*out|timing\s+out|exception|denied|unreachable)[^\n]{0,180}",
    re.IGNORECASE,
)

_PRODUCT_ALIASES = {
    "packetwolf": ["packet wolf", "cilium", "hubble", "network policy"],
    "hypersdk": ["hyper sdk", "vmware migration", "hyper2kvm"],
    "zeus os": ["zeusos", "zeus-os", "kubevirt"],
    "guestkit": ["guest kit", "qcow2 inspection", "vmdk inspection"],
    "machina": ["libvirt", "kvm management"],
    "veyron": ["vm command center", "kubevirt vm"],
    "aether": ["runtime portability", "podman kubernetes kubevirt"],
}

_PRODUCT_DISPLAY = {
    "packetwolf": "PacketWolf",
    "hypersdk": "HyperSDK",
    "zeus os": "Zeus OS",
    "guestkit": "GuestKit",
    "machina": "Machina",
    "veyron": "Veyron",
    "aether": "Aether",
}

_INTENT_RULES: list[tuple[Intent, re.Pattern[str]]] = [
    ("migration", re.compile(r"\b(migrat|hyper2kvm|vmware|vmdk|qcow2|cutover)\b", re.I)),
    ("api", re.compile(r"\b(api|endpoint|crd|openapi|/apis/)\b", re.I)),
    (
        "troubleshooting",
        re.compile(r"\b(timeout|error|fail|crash|deny|unreachable|troubleshoot|why)\b", re.I),
    ),
    ("installation", re.compile(r"\b(install|deploy|bootstrap|helm|operator)\b", re.I)),
    (
        "configuration",
        re.compile(r"\b(configur|policy|egress|ingress|networkpolicy|cilium)\b", re.I),
    ),
    ("comparison", re.compile(r"\b(vs\.?|versus|compare|difference between)\b", re.I)),
]


def _detect_products(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for key, aliases in _PRODUCT_ALIASES.items():
        terms = [key, *aliases]
        if any(term in lowered for term in terms):
            found.append(_PRODUCT_DISPLAY.get(key, key.title()))
    return list(dict.fromkeys(found))


def _detect_intent(text: str) -> Intent:
    for intent, pattern in _INTENT_RULES:
        if pattern.search(text):
            return intent
    return "general"


def understand_query(
    question: str,
    *,
    product: str | None = None,
    conversation_hint: str | None = None,
) -> QueryUnderstanding:
    """Transform a user question into routing + multi-query retrieval hints.

    Pure heuristics (no LLM) so offline tests and production stay deterministic.
    Optional conversation_hint rewrites vague follow-ups like \"fix that\".
    """
    # Lazy import avoids a circular dependency with knowledge.retrieval.
    from knowledge.retrieval import expand_queries

    raw = " ".join(question.strip().split())
    rewritten = raw
    if conversation_hint and _FOLLOWUP_HINTS.search(raw) and len(raw.split()) <= 12:
        rewritten = f"{raw} (context: {conversation_hint.strip()})"

    products = _detect_products(rewritten)
    if product and product not in products:
        products = [product, *products]

    errors = [m.group(0).strip() for m in _ERROR_PATTERN.finditer(rewritten)]
    versions = list(dict.fromkeys(_VERSION_RE.findall(rewritten)))
    intent = _detect_intent(rewritten)
    primary_product = products[0] if products else product
    search_queries = expand_queries(rewritten, primary_product)
    for err in errors[:2]:
        if err not in search_queries:
            search_queries.append(err)
    search_queries = search_queries[:5]

    return QueryUnderstanding(
        intent=intent,
        products=products,
        versions=versions,
        error_messages=errors[:3],
        search_queries=search_queries,
        requires_live_data=bool(_LIVE_HINTS.search(rewritten)),
        rewritten_question=rewritten,
    )
