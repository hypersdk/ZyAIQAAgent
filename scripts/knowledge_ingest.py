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

import argparse
import logging
from pathlib import Path

from knowledge.documents import load_corpus
from knowledge.schemas import IngestStats
from knowledge.vectorstore import delete_existing_sources, get_vector_store


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest documents into Zyvor Argus")
    parser.add_argument("path", type=Path)
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--access-level", default="customer")
    parser.add_argument("--product")
    parser.add_argument("--source", default="documentation")
    parser.add_argument("--chunk-size", type=int, default=1400)
    parser.add_argument("--chunk-overlap", type=int, default=180)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = build_parser().parse_args()

    if not args.path.exists():
        raise SystemExit(f"Path not found: {args.path}")
    if args.chunk_overlap >= args.chunk_size:
        raise SystemExit("chunk-overlap must be smaller than chunk-size")

    files_seen = sum(1 for item in args.path.rglob("*") if item.is_file()) if args.path.is_dir() else 1
    documents, failed = load_corpus(
        args.path,
        tenant_id=args.tenant_id,
        access_level=args.access_level,
        product=args.product,
        source=args.source,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    if not documents:
        raise SystemExit("No supported documents were loaded")

    ids = [str(document.metadata["document_id"]) for document in documents]
    delete_existing_sources(documents)
    get_vector_store().add_documents(
        documents=documents,
        ids=ids,
        batch_size=args.batch_size,
    )

    stats = IngestStats(
        files_seen=files_seen,
        documents_indexed=len(documents),
        files_failed=failed,
    )
    print(stats.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
