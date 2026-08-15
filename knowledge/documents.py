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

import hashlib
import json
import logging
import re
import uuid
from pathlib import Path
from typing import Any, Iterable

import yaml
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from pypdf import PdfReader

LOGGER = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {
    ".md",
    ".markdown",
    ".txt",
    ".rst",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".py",
    ".rs",
    ".html",
    ".htm",
    ".pdf",
}

NAMESPACE = uuid.UUID("f494d61f-63e8-4ed4-9e8a-e20ba3f292ad")
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def iter_supported_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        if path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path
        return

    for candidate in sorted(path.rglob("*")):
        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES:
            yield candidate


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"\n\n## PDF Page {index}\n\n{text}")
    return "".join(pages)


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8", errors="replace")


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text

    raw = yaml.safe_load(match.group(1)) or {}
    if not isinstance(raw, dict):
        raise ValueError("YAML front matter must be an object")
    return raw, text[match.end() :]


def _normalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            normalized[str(key)] = value
        elif isinstance(value, (list, tuple)):
            normalized[str(key)] = [str(item) for item in value]
        else:
            normalized[str(key)] = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return normalized


def _separators_for(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return ["\nclass ", "\ndef ", "\nasync def ", "\n\n", "\n", " ", ""]
    if suffix == ".rs":
        return ["\nimpl ", "\npub struct ", "\npub enum ", "\npub fn ", "\nfn ", "\n\n", "\n", " ", ""]
    if suffix in {".yaml", ".yml"}:
        return ["\n---\n", "\napiVersion:", "\nkind:", "\n\n", "\n", " ", ""]
    if suffix == ".json":
        return ["\n  },", "\n  ],", "\n", " ", ""]
    return ["\n\n", "\n", ". ", " ", ""]


def _base_metadata(
    path: Path,
    root: Path,
    front_matter: dict[str, Any],
    defaults: dict[str, Any],
) -> dict[str, Any]:
    merged = {**defaults, **front_matter}
    relative = str(path.relative_to(root)) if root.is_dir() else path.name

    title = str(merged.get("title") or path.stem.replace("_", " ").replace("-", " ").title())
    product = str(merged.get("product") or defaults.get("product") or "general")
    tenant_id = str(merged.get("tenant_id") or defaults.get("tenant_id") or "public")
    access_level = str(merged.get("access_level") or defaults.get("access_level") or "public")
    source = str(merged.get("source") or defaults.get("source") or "documentation")

    merged.update(
        {
            "title": title,
            "product": product,
            "product_key": product.lower(),
            "tenant_id": tenant_id,
            "access_level": access_level.lower(),
            "source": source,
            "source_path": relative,
            "file_type": path.suffix.lower().lstrip("."),
        }
    )
    return _normalize_metadata(merged)


def load_and_chunk_file(
    path: Path,
    root: Path,
    defaults: dict[str, Any],
    chunk_size: int = 1400,
    chunk_overlap: int = 180,
) -> list[Document]:
    raw_text = read_text(path)
    front_matter, body = parse_front_matter(raw_text)
    metadata = _base_metadata(path, root, front_matter, defaults)

    sections: list[Document]
    if path.suffix.lower() in {".md", ".markdown"}:
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
                ("####", "h4"),
            ],
            strip_headers=False,
        )
        sections = header_splitter.split_text(body)
    else:
        sections = [Document(page_content=body, metadata={})]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=_separators_for(path),
        length_function=len,
    )

    result: list[Document] = []
    chunk_index = 0

    for section in sections:
        section_metadata = {**metadata, **section.metadata}
        heading = " / ".join(
            str(section.metadata[key])
            for key in ("h1", "h2", "h3", "h4")
            if section.metadata.get(key)
        )
        if heading:
            section_metadata["section"] = heading

        parent_material = f"{section_metadata.get('source_path')}:{heading}:{section.page_content[:200]}"
        parent_id = str(uuid.uuid5(NAMESPACE, parent_material))

        for chunk in splitter.split_documents(
            [Document(page_content=section.page_content, metadata=section_metadata)]
        ):
            content = chunk.page_content.strip()
            if not content:
                continue
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            document_id = str(
                uuid.uuid5(
                    NAMESPACE,
                    f"{metadata['tenant_id']}:{metadata['source_path']}:{chunk_index}:{content_hash}",
                )
            )
            chunk.metadata.update(
                {
                    "document_id": document_id,
                    "parent_id": parent_id,
                    "chunk_index": chunk_index,
                    "content_hash": content_hash,
                }
            )
            result.append(
                Document(
                    id=document_id,
                    page_content=content,
                    metadata=chunk.metadata,
                )
            )
            chunk_index += 1

    return result


def load_corpus(
    path: Path,
    *,
    tenant_id: str,
    access_level: str,
    product: str | None = None,
    source: str = "documentation",
    chunk_size: int = 1400,
    chunk_overlap: int = 180,
) -> tuple[list[Document], int]:
    defaults: dict[str, Any] = {
        "tenant_id": tenant_id,
        "access_level": access_level,
        "source": source,
    }
    if product:
        defaults["product"] = product

    documents: list[Document] = []
    failed = 0
    for file_path in iter_supported_files(path):
        try:
            documents.extend(
                load_and_chunk_file(
                    file_path,
                    path,
                    defaults,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
            )
        except Exception:
            failed += 1
            LOGGER.exception("Failed to load %s", file_path)

    return documents, failed
