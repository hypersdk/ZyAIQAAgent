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

"""Versioned enterprise API for durable jobs, schedules, findings and audit."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, Request, Response

from orchestrator.dashboard.durable_jobs import get_service
from orchestrator.observability.metrics import render
from orchestrator.persistence.store import get_store
from orchestrator.security.rbac import require_scope
from orchestrator.security.target_policy import TargetPolicyError

router = APIRouter(prefix="/api/v2", tags=["mission-control-v2"])


def _request_context(request: Request) -> tuple[str, str, str]:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    forwarded = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "")
    return request_id, client_ip, request.url.path


@router.post("/jobs", status_code=202)
async def enqueue_job(request: Request, payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    identity = require_scope(request, "jobs:write")
    kind = str(payload.get("kind", "")).strip()
    params = payload.get("params") or {}
    if not isinstance(params, dict):
        raise HTTPException(status_code=400, detail="params must be an object")
    try:
        return get_service().enqueue(
            kind,
            params,
            requested_by=identity.subject,
            idempotency_key=request.headers.get("idempotency-key") or payload.get("idempotency_key"),
            priority=max(1, min(int(payload.get("priority") or 100), 1000)),
        )
    except (ValueError, TargetPolicyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs")
async def list_jobs(request: Request, limit: int = Query(50, ge=1, le=500)) -> dict[str, Any]:
    require_scope(request, "jobs:read")
    return {"jobs": get_store().list_jobs(limit)}


@router.get("/jobs/{job_id}")
async def get_job(request: Request, job_id: str) -> dict[str, Any]:
    require_scope(request, "jobs:read")
    job = get_store().get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@router.post("/jobs/{job_id}/cancel", status_code=202)
async def cancel_job(request: Request, job_id: str) -> dict[str, Any]:
    identity = require_scope(request, "jobs:write")
    changed = get_store().cancel_job(job_id)
    get_store().audit(
        "job.cancel", actor=identity.subject, resource_type="job", resource_id=job_id,
        outcome="success" if changed else "ignored",
    )
    if not changed:
        raise HTTPException(status_code=409, detail="job is absent or already complete")
    return {"cancel_requested": True, "job_id": job_id}


@router.get("/schedules")
async def list_schedules(request: Request) -> dict[str, Any]:
    require_scope(request, "schedules:read")
    return {"schedules": get_store().list_schedules()}


@router.post("/schedules", status_code=201)
async def add_schedule(request: Request, payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    identity = require_scope(request, "schedules:write")
    kind = str(payload.get("kind", "")).strip()
    params = payload.get("params") or {}
    if not isinstance(params, dict):
        raise HTTPException(status_code=400, detail="params must be an object")
    try:
        # Validate through the same durable enqueue service without actually enqueueing.
        from orchestrator.dashboard import jobs
        from orchestrator.dashboard.durable_jobs import _validation_view

        jobs._validate(kind, _validation_view(params))
        schedule = get_store().add_schedule(
            kind, params, int(payload.get("interval_s") or 300), requested_by=identity.subject
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    get_store().audit(
        "schedule.create", actor=identity.subject, resource_type="schedule",
        resource_id=schedule["id"], detail={"kind": kind, "interval_s": schedule["interval_s"]},
    )
    return schedule


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(request: Request, schedule_id: str) -> dict[str, Any]:
    identity = require_scope(request, "schedules:write")
    removed = get_store().remove_schedule(schedule_id)
    get_store().audit(
        "schedule.delete", actor=identity.subject, resource_type="schedule",
        resource_id=schedule_id, outcome="success" if removed else "ignored",
    )
    if not removed:
        raise HTTPException(status_code=404, detail="schedule not found")
    return {"removed": True}


@router.get("/engagements")
async def list_engagements(request: Request) -> dict[str, Any]:
    require_scope(request, "engagements:read")
    return {"engagements": get_store().list_engagements()}


@router.post("/engagements", status_code=201)
async def create_engagement(request: Request, payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    identity = require_scope(request, "engagements:write")
    target_pattern = str(payload.get("target_pattern", "")).strip()
    scope_statement = str(payload.get("scope_statement", "")).strip()
    tier = str(payload.get("tier", "")).strip()
    if not target_pattern:
        raise HTTPException(status_code=400, detail="target_pattern is required")
    if not scope_statement:
        raise HTTPException(status_code=400, detail="scope_statement is required")
    if tier not in ("active_recon", "exploit"):
        raise HTTPException(status_code=400, detail="tier must be 'active_recon' or 'exploit'")
    engagement = get_store().create_engagement(
        target_pattern,
        scope_statement,
        tier,
        authorized_by=identity.subject,
        expires_at=payload.get("expires_at"),
    )
    get_store().audit(
        "engagement.create", actor=identity.subject, resource_type="engagement",
        resource_id=engagement["id"], detail={"target_pattern": target_pattern, "tier": tier},
    )
    return engagement


@router.delete("/engagements/{engagement_id}")
async def revoke_engagement(request: Request, engagement_id: str) -> dict[str, Any]:
    identity = require_scope(request, "engagements:write")
    revoked = get_store().revoke_engagement(engagement_id, revoked_by=identity.subject)
    get_store().audit(
        "engagement.revoke", actor=identity.subject, resource_type="engagement",
        resource_id=engagement_id, outcome="success" if revoked else "ignored",
    )
    if not revoked:
        raise HTTPException(status_code=404, detail="engagement not found or already revoked")
    return {"revoked": True}


@router.get("/engagement-policy")
async def engagement_policy(request: Request) -> dict[str, Any]:
    """Read-only status for the engagement gate itself -- enforcement is set
    once, from ZYVOR_ENGAGEMENT_ENFORCEMENT at process start
    (EngagementPolicy.from_env()), so there is nothing to write here; an
    admin who wants it changed has to change the env var and restart."""
    require_scope(request, "engagements:read")
    from orchestrator.dashboard.jobs import ELEVATED_RISK_KINDS
    from orchestrator.security.engagement_policy import EngagementPolicy

    return {
        "enforcement": EngagementPolicy.from_env().enforcement,
        "elevated_risk_kinds": ELEVATED_RISK_KINDS,
    }


@router.get("/findings")
async def list_findings(
    request: Request,
    limit: int = Query(200, ge=1, le=500),
    severity: str = Query(""),
) -> dict[str, Any]:
    require_scope(request, "findings:read")
    return get_store().list_findings(limit, severity or None)


@router.delete("/findings")
async def close_findings(request: Request) -> dict[str, Any]:
    identity = require_scope(request, "findings:write")
    count = get_store().clear_findings()
    get_store().audit("findings.close_all", actor=identity.subject, detail={"count": count})
    return {"closed": count}


@router.get("/audit")
async def audit_events(request: Request, limit: int = Query(200, ge=1, le=1000)) -> dict[str, Any]:
    require_scope(request, "audit:read")
    return {"events": get_store().list_audit(limit)}


@router.get("/metrics", include_in_schema=False)
async def metrics(request: Request) -> Response:
    require_scope(request, "audit:read")
    return Response(render(), media_type="text/plain; version=0.0.4")
