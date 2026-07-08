"""Provider-agnostic LLM factory via LangChain."""

from __future__ import annotations

import os
from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel


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
        return ChatOpenAI(model=model, api_key=api_key, temperature=0)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMConfigError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        return ChatAnthropic(model=model, api_key=api_key, temperature=0)

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
            api_key=api_key,
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
            from langchain_community.chat_models import ChatOllama
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


def load_prompt(name: str) -> str:
    """Load a prompt markdown file from prompts/."""
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "prompts" / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")
