from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Zyvor Technical QA Agent"
    app_env: str = "development"
    log_level: str = "INFO"
    app_api_key: SecretStr | None = None
    auth_tokens_json: SecretStr | None = None
    # Secure by default: when no AUTH_TOKENS_JSON mapping is configured, refuse
    # requests instead of trusting a client-supplied X-Tenant-ID header. Only
    # flip this on for trusted, network-isolated internal deployments (e.g. a
    # single-operator Mission Control instance) — never for anything reachable
    # by tenant-facing/external clients.
    trust_client_tenant_header: bool = False

    llm_model: str = "gpt-5.5"
    llm_api_key: SecretStr = SecretStr("")
    llm_base_url: str | None = None
    llm_temperature: float = 0.0
    llm_timeout_seconds: float = 90.0
    llm_fallback_model: str | None = None
    llm_fallback_api_key: SecretStr | None = None
    llm_fallback_base_url: str | None = None

    # Mission Control dashboard ask defaults (never taken from the browser).
    knowledge_tenant_id: str = "public"
    knowledge_access_levels: Annotated[tuple[str, ...], NoDecode] = ("public", "customer")
    knowledge_checkpoint_path: str = "reports/knowledge-checkpoints.sqlite"
    enable_live_cluster_tools: bool = False
    knowledge_live_namespaces: Annotated[tuple[str, ...], NoDecode] = ()
    enable_remediation_agent: bool = False
    enable_remediation_executor: bool = False
    remediation_restart_namespaces: Annotated[tuple[str, ...], NoDecode] = ()
    remediation_restart_name_prefixes: Annotated[tuple[str, ...], NoDecode] = ()
    enable_query_understanding: bool = True
    enable_ask_streaming: bool = True

    embedding_model: str = "text-embedding-3-small"
    embedding_api_key: SecretStr | None = None
    embedding_base_url: str | None = None
    embedding_dimensions: int | None = None

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None
    qdrant_collection: str = "zyvor_knowledge"
    qdrant_timeout_seconds: float = 30.0

    retrieval_k: int = Field(default=8, ge=1, le=30)
    retrieval_fetch_k: int = Field(default=16, ge=1, le=100)
    max_tool_calls: int = Field(default=8, ge=1, le=20)
    max_query_length: int = Field(default=4000, ge=100, le=20000)
    enable_public_documents: bool = True
    default_access_levels: Annotated[tuple[str, ...], NoDecode] = ("public", "customer")

    @field_validator(
        "llm_base_url",
        "embedding_base_url",
        "llm_fallback_base_url",
        mode="before",
    )
    @classmethod
    def empty_url_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator(
        "default_access_levels",
        "knowledge_access_levels",
        "knowledge_live_namespaces",
        "remediation_restart_namespaces",
        "remediation_restart_name_prefixes",
        mode="before",
    )
    @classmethod
    def parse_access_levels(cls, value: object) -> object:
        if isinstance(value, str):
            return tuple(item.strip().lower() for item in value.split(",") if item.strip())
        return value

    @field_validator(
        "enable_live_cluster_tools",
        "enable_remediation_agent",
        "enable_remediation_executor",
        "enable_query_understanding",
        "enable_ask_streaming",
        "trust_client_tenant_header",
        mode="before",
    )
    @classmethod
    def parse_bool(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return value

    def resolved_embedding_key(self) -> SecretStr:
        return self.embedding_api_key or self.llm_api_key

    def has_llm_credentials(self) -> bool:
        return bool(self.llm_api_key.get_secret_value().strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
