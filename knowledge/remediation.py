"""Separate HITL remediation agent — never mounted into the primary QA agent.

Enable only with ENABLE_REMEDIATION_AGENT=true. Mutating tools interrupt for
human approval. After approval, an optional allowlisted executor may restart pods.
"""

from __future__ import annotations

import logging
import re
import uuid
from functools import lru_cache
from typing import Any, Literal

from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelRetryMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from knowledge.checkpoint import get_checkpointer
from knowledge.config import get_settings

LOGGER = logging.getLogger(__name__)

_POD_NAME_RE = re.compile(r"^[A-Za-z0-9]([-A-Za-z0-9_.]{0,251}[A-Za-z0-9])?$")
_NS_RE = re.compile(r"^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$")


class RemediationResponse(BaseModel):
    plan: str = Field(description="Human-readable remediation plan")
    risk: Literal["low", "medium", "high"] = "medium"
    requires_approval: bool = True
    proposed_actions: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None


REMEDIATION_PROMPT = """
You are the Zyvor Remediation Planner (NOT the primary QA agent).

Rules:
1. Prefer read-only diagnosis and a clear plan a human can execute.
2. Never claim a mutating action completed unless an approved tool returned success.
3. request_pod_restart requires human approval and may be interrupted.
4. Do not delete namespaces, wipe Ceph pools, or change PacketWolf policies.
5. If unsure, set blocked_reason and keep risk=high.
"""


def _restart_allowed(name: str, namespace: str) -> tuple[bool, str]:
    settings = get_settings()
    if not settings.enable_remediation_executor:
        return False, "Remediation executor disabled (ENABLE_REMEDIATION_EXECUTOR=false)"
    if not _POD_NAME_RE.fullmatch(name) or not _NS_RE.fullmatch(namespace):
        return False, "Invalid pod or namespace name"
    allowed_ns = settings.remediation_restart_namespaces
    if allowed_ns and namespace not in allowed_ns and "*" not in allowed_ns:
        return False, f"Namespace {namespace!r} is not in REMEDIATION_RESTART_NAMESPACES"
    prefixes = settings.remediation_restart_name_prefixes
    if prefixes and not any(name.startswith(p) for p in prefixes):
        return False, f"Pod {name!r} does not match REMEDIATION_RESTART_NAME_PREFIXES"
    return True, ""


def execute_approved_pod_restart(name: str, namespace: str) -> dict[str, Any]:
    """Allowlisted pod restart used only after HITL approval (or explicit API)."""
    ok, reason = _restart_allowed(name, namespace)
    if not ok:
        return {"ok": False, "error": reason, "name": name, "namespace": namespace}

    from orchestrator.dashboard.k8s import delete_pod

    # delete_pod uses DASHBOARD_NAMESPACE; temporarily align when needed.
    import os

    previous = os.environ.get("DASHBOARD_NAMESPACE")
    try:
        os.environ["DASHBOARD_NAMESPACE"] = namespace
        from orchestrator.dashboard.k8s import reset_client_cache

        reset_client_cache()
        result = delete_pod(name)
    finally:
        if previous is None:
            os.environ.pop("DASHBOARD_NAMESPACE", None)
        else:
            os.environ["DASHBOARD_NAMESPACE"] = previous
        try:
            from orchestrator.dashboard.k8s import reset_client_cache

            reset_client_cache()
        except Exception:
            pass

    return {
        "ok": bool(result.get("ok")),
        "name": name,
        "namespace": namespace,
        "error": result.get("error"),
        "executed": True,
    }


@tool
def propose_remediation_plan(issue: str, context: str | None = None) -> str:
    """Draft a step-by-step remediation plan without changing cluster state."""

    bits = [f"Issue: {issue.strip()}"]
    if context:
        bits.append(f"Context: {context.strip()}")
    bits.append(
        "Plan outline: (1) verify observed state with read-only tools, "
        "(2) capture evidence, (3) apply the smallest reversible fix, "
        "(4) re-verify. No mutation was performed by this tool."
    )
    return "\n".join(bits)


@tool
def request_pod_restart(name: str, namespace: str) -> str:
    """Request a pod restart. Requires human approval via HITL interrupt.

    After approval, restarts only when ENABLE_REMEDIATION_EXECUTOR=true and the
    namespace/name pass the remediation allowlists.
    """

    ok, reason = _restart_allowed(name, namespace)
    if not ok:
        return (
            f"Restart of {namespace}/{name} was approved in the HITL flow but "
            f"the executor refused it: {reason}"
        )

    result = execute_approved_pod_restart(name, namespace)
    if result.get("ok"):
        return f"Executed allowlisted restart of pod {namespace}/{name}."
    return (
        f"Failed to restart {namespace}/{name}: {result.get('error') or 'unknown error'}"
    )


def remediation_enabled() -> bool:
    return bool(get_settings().enable_remediation_agent)


@lru_cache(maxsize=1)
def get_remediation_agent() -> Any:
    settings = get_settings()
    if not settings.enable_remediation_agent:
        raise RuntimeError("Remediation agent is disabled (ENABLE_REMEDIATION_AGENT=false)")
    if not settings.has_llm_credentials():
        raise RuntimeError("LLM_API_KEY is not configured")

    kwargs: dict[str, Any] = {
        "model": settings.llm_model,
        "api_key": settings.llm_api_key,
        "temperature": 0,
        "timeout": settings.llm_timeout_seconds,
    }
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url

    middleware: list[Any] = [
        HumanInTheLoopMiddleware(
            interrupt_on={
                "request_pod_restart": True,
                "propose_remediation_plan": False,
            },
            description_prefix="Remediation tool requires approval",
        ),
        ModelRetryMiddleware(max_retries=2, initial_delay=1.0, max_delay=8.0),
        ToolCallLimitMiddleware(run_limit=4, exit_behavior="end"),
    ]
    return create_agent(
        model=ChatOpenAI(**kwargs),
        tools=[propose_remediation_plan, request_pod_restart],
        system_prompt=REMEDIATION_PROMPT,
        response_format=RemediationResponse,
        checkpointer=get_checkpointer(),
        middleware=middleware,
        name="zyvor-remediation",
    )


def clear_remediation_agent_cache() -> None:
    get_remediation_agent.cache_clear()


def _serialize_result(result: Any, thread_id: str) -> dict[str, Any]:
    if isinstance(result, dict) and result.get("__interrupt__"):
        return {
            "enabled": True,
            "interrupted": True,
            "thread_id": thread_id,
            "interrupt": result.get("__interrupt__"),
            "detail": "Human approval required before continuing",
        }

    structured = result.get("structured_response") if isinstance(result, dict) else None
    if structured is None:
        return {
            "enabled": True,
            "interrupted": False,
            "thread_id": thread_id,
            "plan": str(result),
        }
    if hasattr(structured, "model_dump"):
        payload = structured.model_dump()
    else:
        payload = dict(structured)
    payload["enabled"] = True
    payload["interrupted"] = False
    payload["thread_id"] = thread_id
    return payload


def plan_remediation(*, issue: str, thread_id: str | None = None) -> dict[str, Any]:
    """Invoke the remediation planner. May return an interrupt payload."""
    if not remediation_enabled():
        return {
            "enabled": False,
            "blocked_reason": "ENABLE_REMEDIATION_AGENT is false",
            "plan": None,
        }

    agent = get_remediation_agent()
    tid = thread_id or f"remediation:{uuid.uuid4()}"
    config = {"configurable": {"thread_id": tid}, "recursion_limit": 12}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": issue}]},
        config=config,
    )
    return _serialize_result(result, tid)


def resume_remediation(
    *,
    thread_id: str,
    decision: Literal["approve", "reject"] = "approve",
    message: str | None = None,
) -> dict[str, Any]:
    """Resume an interrupted remediation thread after human approval/rejection."""
    if not remediation_enabled():
        return {
            "enabled": False,
            "blocked_reason": "ENABLE_REMEDIATION_AGENT is false",
        }
    if not thread_id.strip():
        raise ValueError("thread_id is required to resume remediation")

    from langgraph.types import Command

    agent = get_remediation_agent()
    if decision == "approve":
        resume_value: dict[str, Any] = {"decisions": [{"type": "approve"}]}
    else:
        resume_value = {
            "decisions": [
                {
                    "type": "reject",
                    "message": message or "Operator rejected the remediation action",
                }
            ]
        }

    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 12}
    result = agent.invoke(Command(resume=resume_value), config=config)
    return _serialize_result(result, thread_id)
