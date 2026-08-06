from __future__ import annotations

import hmac
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from fastapi import Header, HTTPException, status

from knowledge.config import get_settings


TENANT_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
ACCESS_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


@dataclass(frozen=True)
class AuthIdentity:
    tenant_id: str
    access_levels: tuple[str, ...]


def _validate_tenant(value: str) -> str:
    cleaned = value.strip()
    if not TENANT_PATTERN.fullmatch(cleaned):
        raise HTTPException(status_code=400, detail="Invalid tenant ID")
    return cleaned


def _validate_levels(values: tuple[str, ...]) -> tuple[str, ...]:
    if not values or any(not ACCESS_PATTERN.fullmatch(value) for value in values):
        raise HTTPException(status_code=400, detail="Invalid access levels")
    return tuple(dict.fromkeys(values))


@lru_cache(maxsize=1)
def _token_claims() -> dict[str, AuthIdentity]:
    secret = get_settings().auth_tokens_json
    if secret is None or not secret.get_secret_value().strip():
        return {}

    try:
        raw: Any = json.loads(secret.get_secret_value())
    except json.JSONDecodeError as exc:
        raise RuntimeError("AUTH_TOKENS_JSON is not valid JSON") from exc
    if not isinstance(raw, dict):
        raise RuntimeError("AUTH_TOKENS_JSON must be a JSON object")

    result: dict[str, AuthIdentity] = {}
    for token, claims in raw.items():
        if not isinstance(token, str) or not token or not isinstance(claims, dict):
            raise RuntimeError("Invalid AUTH_TOKENS_JSON entry")
        tenant_id = _validate_tenant(str(claims.get("tenant_id", "")))
        levels_raw = claims.get("access_levels", [])
        if not isinstance(levels_raw, list):
            raise RuntimeError("access_levels must be a JSON array")
        levels = _validate_levels(tuple(str(item).lower() for item in levels_raw))
        result[token] = AuthIdentity(tenant_id=tenant_id, access_levels=levels)
    return result


def resolve_identity(
    x_api_key: str | None = Header(default=None),
    x_tenant_id: str = Header(default="public"),
    x_access_levels: str | None = Header(default=None),
) -> AuthIdentity:
    settings = get_settings()
    mapped_claims = _token_claims()

    if mapped_claims:
        if not x_api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
        # Constant-time comparisons avoid directly indexing with attacker-controlled tokens.
        for token, identity in mapped_claims.items():
            if hmac.compare_digest(x_api_key, token):
                return identity
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    if not settings.trust_client_tenant_header:
        # No AUTH_TOKENS_JSON mapping configured, and header-trust is disabled
        # (the secure default). Refuse rather than let a client dictate its own
        # tenant_id via X-Tenant-ID — that would let any caller read/answer as
        # any tenant. Set AUTH_TOKENS_JSON (preferred) or explicitly opt into
        # TRUST_CLIENT_TENANT_HEADER=true for trusted, network-isolated
        # internal-only deployments.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant identity is not configured (set AUTH_TOKENS_JSON)",
        )

    expected_secret = settings.app_api_key
    if expected_secret is not None:
        expected = expected_secret.get_secret_value()
        if not x_api_key or not hmac.compare_digest(x_api_key, expected):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    tenant_id = _validate_tenant(x_tenant_id)
    allowed = set(settings.default_access_levels)
    if x_access_levels is None:
        levels = settings.default_access_levels
    else:
        requested = tuple(
            item.strip().lower() for item in x_access_levels.split(",") if item.strip()
        )
        levels = _validate_levels(requested)
        forbidden = set(levels) - allowed
        if forbidden:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access levels not permitted: {', '.join(sorted(forbidden))}",
            )
    return AuthIdentity(tenant_id=tenant_id, access_levels=levels)
