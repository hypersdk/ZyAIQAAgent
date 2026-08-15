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

"""FastAPI routes for the Zyvor knowledge QA API (mountable + standalone)."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import ORJSONResponse

from knowledge.agent import answer_question, stream_answer_question
from knowledge.config import get_settings
from knowledge.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    RemediationRequest,
    RemediationResumeRequest,
)
from knowledge.security import AuthIdentity, resolve_identity

LOGGER = logging.getLogger(__name__)


def _qdrant_health() -> HealthResponse:
    settings = get_settings()
    try:
        from knowledge.vectorstore import get_qdrant_client

        get_qdrant_client().get_collections()
        qdrant_status = "reachable"
        status: str = "ok"
    except Exception as exc:
        LOGGER.warning("Qdrant health check failed: %s", exc)
        qdrant_status = "unreachable"
        status = "degraded"

    return HealthResponse(
        status=status,  # type: ignore[arg-type]
        service=settings.app_name,
        qdrant=qdrant_status,
    )


def create_knowledge_router() -> APIRouter:
    """Router for /v1/qa and /v1/knowledge/health — mount on the main serve app."""
    router = APIRouter(tags=["knowledge"])

    @router.get("/v1/knowledge/health", response_model=HealthResponse)
    def knowledge_health() -> HealthResponse:
        return _qdrant_health()

    @router.post("/v1/qa", response_model=QueryResponse)
    def qa(
        request: QueryRequest,
        identity: AuthIdentity = Depends(resolve_identity),
        user_agent: str | None = Header(default=None),
    ) -> QueryResponse:
        del user_agent
        try:
            return answer_question(
                question=request.question,
                tenant_id=identity.tenant_id,
                access_levels=identity.access_levels,
                product=request.product,
                document_type=request.document_type,
                thread_id=request.thread_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            LOGGER.exception("QA request failed")
            raise HTTPException(
                status_code=503, detail="QA service temporarily unavailable"
            ) from exc

    @router.post("/v1/remediation")
    def remediation(
        request: RemediationRequest,
        identity: AuthIdentity = Depends(resolve_identity),
    ) -> dict:
        """Separate HITL remediation planner — disabled unless explicitly enabled."""
        del identity
        from knowledge.remediation import plan_remediation, remediation_enabled

        if not remediation_enabled():
            raise HTTPException(
                status_code=501,
                detail=(
                    "Remediation agent is disabled. "
                    "Set ENABLE_REMEDIATION_AGENT=true to enable the separate HITL planner."
                ),
            )
        try:
            return plan_remediation(issue=request.issue, thread_id=request.thread_id)
        except Exception as exc:
            LOGGER.exception("Remediation request failed")
            raise HTTPException(
                status_code=503, detail="Remediation service temporarily unavailable"
            ) from exc

    @router.post("/v1/remediation/resume")
    def remediation_resume(
        request: RemediationResumeRequest,
        identity: AuthIdentity = Depends(resolve_identity),
    ) -> dict:
        del identity
        from knowledge.remediation import remediation_enabled, resume_remediation

        if not remediation_enabled():
            raise HTTPException(status_code=501, detail="Remediation agent is disabled")
        try:
            return resume_remediation(
                thread_id=request.thread_id,
                decision=request.decision,
                message=request.message,
            )
        except Exception as exc:
            LOGGER.exception("Remediation resume failed")
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @router.post("/v1/qa/stream")
    def qa_stream(
        request: QueryRequest,
        identity: AuthIdentity = Depends(resolve_identity),
    ):
        import json

        from fastapi.responses import StreamingResponse

        def event_gen():
            try:
                for event in stream_answer_question(
                    question=request.question,
                    tenant_id=identity.tenant_id,
                    access_levels=identity.access_levels,
                    product=request.product,
                    document_type=request.document_type,
                    thread_id=request.thread_id,
                ):
                    yield f"data: {json.dumps(event, default=str)}\n\n"
            except ValueError as exc:
                yield f"data: {json.dumps({'event': 'error', 'detail': str(exc)})}\n\n"
            except Exception:
                LOGGER.exception("QA stream failed")
                yield (
                    "data: "
                    + json.dumps({"event": "error", "detail": "QA stream unavailable"})
                    + "\n\n"
                )

        return StreamingResponse(event_gen(), media_type="text/event-stream")

    return router


def create_standalone_app() -> FastAPI:
    """Standalone FastAPI app (optional: `uvicorn knowledge.api:app`)."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        default_response_class=ORJSONResponse,
    )

    @application.middleware("http")
    async def request_metrics(request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return _qdrant_health()

    application.include_router(create_knowledge_router())
    return application


app = create_standalone_app()


def run() -> None:
    import uvicorn

    uvicorn.run("knowledge.api:app", host="0.0.0.0", port=8080)


if __name__ == "__main__":
    run()
