"""FastAPI GitHub webhook receiver."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

from orchestrator.graph import get_compiled_graph
from orchestrator.state import PipelineState


def _verify_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _build_state_from_event(event: str, payload: dict[str, Any]) -> PipelineState:
    pr_number = None
    repo_full_name = payload.get("repository", {}).get("full_name")

    if event == "pull_request":
        pr_number = payload.get("pull_request", {}).get("number")
    elif event == "repository_dispatch":
        client_payload = payload.get("client_payload", {})
        pr_number = client_payload.get("pr_number")

    return {
        "source": "github",
        "spec_paths": [],
        "spec_contents": [],
        "requirements": [],
        "generated_tests": [],
        "test_results": None,
        "failure_analysis": None,
        "report_path": None,
        "report_summary": None,
        "pr_number": pr_number,
        "repo_full_name": repo_full_name or os.environ.get("ZYVOR_PRODUCT_REPO"),
        "error": None,
        "metadata": {"event": event},
    }


def create_app() -> FastAPI:
    app = FastAPI(title="Zyvor QA Agent Webhook")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhook/github")
    async def github_webhook(
        request: Request,
        x_github_event: str = Header(None),
        x_hub_signature_256: str = Header(None),
    ) -> dict[str, Any]:
        body = await request.body()
        secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")

        if secret and not _verify_signature(body, x_hub_signature_256, secret):
            raise HTTPException(status_code=401, detail="Invalid signature")

        payload = json.loads(body)
        event = x_github_event or "unknown"

        supported = {"push", "pull_request", "repository_dispatch"}
        if event not in supported:
            return {"status": "ignored", "event": event}

        if event == "repository_dispatch":
            action = payload.get("action", "")
            if action != "staging-deployed":
                return {"status": "ignored", "action": action}

        state = _build_state_from_event(event, payload)
        graph = get_compiled_graph()
        result = graph.invoke(state)

        test_results = result.get("test_results")
        return {
            "status": "completed",
            "event": event,
            "passed": test_results.passed if test_results else 0,
            "failed": test_results.failed if test_results else 0,
            "report_path": result.get("report_path"),
            "error": result.get("error"),
        }

    return app
