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

"""Zyvor citation-first technical knowledge QA agent."""

from __future__ import annotations


def knowledge_deps_available() -> bool:
    """Return True when optional [knowledge] extras are importable."""
    try:
        import langchain_qdrant  # noqa: F401
        import qdrant_client  # noqa: F401
        from langchain.agents import create_agent  # noqa: F401
    except ImportError:
        return False
    return True


def knowledge_configured() -> bool:
    """Return True when LLM credentials are present for answering."""
    if not knowledge_deps_available():
        return False
    try:
        from knowledge.config import get_settings

        return get_settings().has_llm_credentials()
    except Exception:
        return False
