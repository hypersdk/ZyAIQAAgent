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

from langchain_core.documents import Document

from knowledge.retrieval import expand_queries, rerank


def test_expand_queries_adds_product_aliases() -> None:
    queries = expand_queries(
        "How do I block internet access?",
        product="PacketWolf",
    )
    assert len(queries) >= 2
    assert any("cilium" in query.lower() for query in queries)


def test_reranker_prefers_matching_content() -> None:
    matching = Document(
        page_content="Use a default deny egress network policy and allow DNS.",
        metadata={"product": "PacketWolf", "updated_at": "2026-07-30"},
    )
    unrelated = Document(
        page_content="Convert a VMware disk to qcow2.",
        metadata={"product": "HyperSDK", "updated_at": "2026-07-30"},
    )
    ranked = rerank(
        "PacketWolf default deny egress DNS",
        [(unrelated, 0.5), (matching, 0.5)],
        product="PacketWolf",
        limit=2,
    )
    assert ranked[0].document is matching
