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

"""Conversation checkpointer for the knowledge QA agent."""

from __future__ import annotations

import logging
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Any

from knowledge.config import get_settings

LOGGER = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_checkpointer() -> Any:
    """Return a process-lifetime checkpointer (SQLite when configured, else memory)."""
    settings = get_settings()
    path = (settings.knowledge_checkpoint_path or "").strip()

    if not path or path == ":memory:":
        from langgraph.checkpoint.memory import InMemorySaver

        LOGGER.info("Knowledge checkpointer: InMemorySaver")
        return InMemorySaver()

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        from langgraph.checkpoint.memory import InMemorySaver

        LOGGER.warning(
            "langgraph-checkpoint-sqlite not installed; falling back to InMemorySaver"
        )
        return InMemorySaver()

    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()
    LOGGER.info("Knowledge checkpointer: SqliteSaver (%s)", db_path)
    return saver


def clear_checkpointer_cache() -> None:
    get_checkpointer.cache_clear()
