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

"""Checkpoint helper tests (offline)."""

from __future__ import annotations

from pathlib import Path

import pytest

from knowledge.checkpoint import clear_checkpointer_cache, get_checkpointer
from knowledge.config import clear_settings_cache


def test_memory_checkpointer_when_path_is_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGE_CHECKPOINT_PATH", ":memory:")
    clear_settings_cache()
    clear_checkpointer_cache()
    saver = get_checkpointer()
    assert saver.__class__.__name__ == "InMemorySaver"
    clear_checkpointer_cache()
    clear_settings_cache()


def test_sqlite_checkpointer_when_package_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pytest.importorskip("langgraph.checkpoint.sqlite")
    db = tmp_path / "checkpoints.sqlite"
    monkeypatch.setenv("KNOWLEDGE_CHECKPOINT_PATH", str(db))
    clear_settings_cache()
    clear_checkpointer_cache()
    saver = get_checkpointer()
    assert saver.__class__.__name__ == "SqliteSaver"
    assert db.exists()
    clear_checkpointer_cache()
    clear_settings_cache()
