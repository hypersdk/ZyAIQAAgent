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

"""Provider-agnostic LLM factory via LangChain."""

from __future__ import annotations

import os
from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import SecretStr


class LLMConfigError(ValueError):
    pass


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Return a LangChain chat model based on LLM_PROVIDER env var."""
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    model = os.environ.get("LLM_MODEL", "gpt-4o")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise LLMConfigError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return ChatOpenAI(model=model, api_key=SecretStr(api_key), temperature=0)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMConfigError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        # `model` is the real field (aliased to `model_name`); the stub's alias-keyed
        # overload requires unrelated kwargs it shouldn't, so ignore this one mismatch.
        return ChatAnthropic(model=model, api_key=SecretStr(api_key), temperature=0)  # type: ignore[call-arg]

    if provider == "azure":
        from langchain_openai import AzureChatOpenAI

        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", model)
        if not api_key or not endpoint:
            raise LLMConfigError(
                "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are required when LLM_PROVIDER=azure"
            )
        return AzureChatOpenAI(
            azure_deployment=deployment,
            api_key=SecretStr(api_key),
            azure_endpoint=endpoint,
            temperature=0,
        )

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise LLMConfigError("GOOGLE_API_KEY is required when LLM_PROVIDER=google")
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0)

    if provider == "ollama":
        try:
            # Optional dependency, deliberately not in pyproject's hard requires —
            # mypy can't see its stubs without installing it, which would defeat
            # the point of the try/except below.
            from langchain_community.chat_models import ChatOllama  # type: ignore[import-not-found]
        except ImportError as exc:
            raise LLMConfigError(
                "langchain-community is required for ollama. "
                "Install with: pip install langchain-community"
            ) from exc

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=0)

    raise LLMConfigError(
        f"Unsupported LLM_PROVIDER: {provider}. "
        "Use one of: openai, anthropic, azure, google, ollama"
    )


def content_to_text(content: str | list[str | dict]) -> str:
    """Normalize a LangChain message's `.content` to plain text.

    Chat models type `.content` as `str | list[str | dict]` to allow for
    multimodal/tool-call content blocks, but every caller here only ever
    sends plain-text prompts and expects plain-text responses.
    """
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "".join(parts)


def load_prompt(name: str) -> str:
    """Load a prompt markdown file from prompts/."""
    from orchestrator.paths import repo_root as _shared_repo_root

    repo_root = _shared_repo_root()
    path = repo_root / "prompts" / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")
