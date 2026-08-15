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

from pathlib import Path

import pytest

pytest.importorskip("langchain_text_splitters")
pytest.importorskip("pypdf")

from knowledge.documents import load_and_chunk_file, parse_front_matter


def test_parse_front_matter() -> None:
    metadata, body = parse_front_matter(
        "---\nproduct: PacketWolf\nversion: '2.0'\n---\n# Title\nBody"
    )
    assert metadata["product"] == "PacketWolf"
    assert body.startswith("# Title")


def test_chunking_preserves_security_metadata(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text(
        "---\ntitle: Guide\nproduct: PacketWolf\ntenant_id: acme\n"
        "access_level: customer\n---\n# Guide\n" + ("content " * 500),
        encoding="utf-8",
    )
    docs = load_and_chunk_file(
        path,
        tmp_path,
        defaults={"source": "manual"},
        chunk_size=300,
        chunk_overlap=30,
    )
    assert len(docs) > 1
    assert all(doc.metadata["tenant_id"] == "acme" for doc in docs)
    assert all(doc.metadata["access_level"] == "customer" for doc in docs)
    assert len({doc.metadata["document_id"] for doc in docs}) == len(docs)
