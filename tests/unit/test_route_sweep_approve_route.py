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

"""HTTP-level tests for POST /api/v2/jobs/{job_id}/route-sweep/approve --
promoting one screenshot from a route_sweep job's own result to the saved
baseline it's diffed against."""

from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from orchestrator.dashboard.jobs import _repo_root
from orchestrator.persistence.store import get_store
from orchestrator.webhook import create_app


@pytest.fixture()
def sweep_shot():
    """A real screenshot file under reports/artifacts/route-sweep/, matching
    where _job_route_sweep actually writes them, cleaned up (including any
    baseline it got copied to) after the test regardless of outcome."""
    rel_dir = _repo_root() / "reports" / "artifacts" / "route-sweep" / "test-fixture-sweep"
    rel_dir.mkdir(parents=True, exist_ok=True)
    path = rel_dir / "home-desktop.png"
    path.write_bytes(b"fake png bytes")
    href = "/reports/artifacts/route-sweep/test-fixture-sweep/home-desktop.png"
    baseline_path = _repo_root() / "reports" / "artifacts" / "route-baselines" / "home-desktop.png"
    yield href
    shutil.rmtree(rel_dir, ignore_errors=True)
    baseline_path.unlink(missing_ok=True)


def _seed_sweep_job(href: str) -> str:
    store = get_store()
    job = store.enqueue_job("route_sweep", {"url": "https://example.test", "routes": ["/"], "viewports": ["desktop"]})
    store.finish_job(
        job["id"],
        result={
            "url": "https://example.test",
            "sweep_rows": [{"route": "/", "viewport": "desktop", "status": "fail", "diff": 4.2, "cur": href}],
            "fail_count": 1,
        },
    )
    return job["id"]


def test_approve_copies_the_screenshot_to_the_baseline_path(sweep_shot):
    job_id = _seed_sweep_job(sweep_shot)
    client = TestClient(create_app())
    resp = client.post(
        f"/api/v2/jobs/{job_id}/route-sweep/approve", json={"route": "/", "viewport": "desktop"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"approved": True, "route": "/", "viewport": "desktop", "job_id": job_id}

    baseline_path = _repo_root() / "reports" / "artifacts" / "route-baselines" / "home-desktop.png"
    assert baseline_path.read_bytes() == b"fake png bytes"


def test_approve_records_an_audit_entry(sweep_shot):
    job_id = _seed_sweep_job(sweep_shot)
    client = TestClient(create_app())
    client.post(f"/api/v2/jobs/{job_id}/route-sweep/approve", json={"route": "/", "viewport": "desktop"})

    events = get_store().list_audit(limit=5)
    match = next((e for e in events if e["action"] == "route_sweep.baseline_approved"), None)
    assert match is not None
    assert match["resource_id"] == job_id


def test_approve_404s_for_a_route_viewport_not_in_this_job(sweep_shot):
    job_id = _seed_sweep_job(sweep_shot)
    client = TestClient(create_app())
    resp = client.post(
        f"/api/v2/jobs/{job_id}/route-sweep/approve", json={"route": "/pricing", "viewport": "desktop"}
    )
    assert resp.status_code == 404


def test_approve_400s_for_a_job_that_isnt_a_route_sweep(sweep_shot):
    store = get_store()
    job = store.enqueue_job("smoke", {})
    store.finish_job(job["id"], result={"cases": []})
    client = TestClient(create_app())
    resp = client.post(
        f"/api/v2/jobs/{job['id']}/route-sweep/approve", json={"route": "/", "viewport": "desktop"}
    )
    assert resp.status_code == 400


def test_approve_404s_for_missing_job():
    client = TestClient(create_app())
    resp = client.post(
        "/api/v2/jobs/does-not-exist/route-sweep/approve", json={"route": "/", "viewport": "desktop"}
    )
    assert resp.status_code == 404


def test_route_sweep_screenshot_is_streamable_through_the_artifact_route(sweep_shot):
    """GET /jobs/{id}/artifact originally only recognized cases[].video/trace
    hrefs -- a route_sweep job's sweep_rows[].cur screenshots weren't in its
    known-hrefs whitelist at all, so every "View" link 404'd even though the
    file genuinely existed on disk. Caught live in the browser, not review."""
    job_id = _seed_sweep_job(sweep_shot)
    client = TestClient(create_app())
    resp = client.get(f"/api/v2/jobs/{job_id}/artifact", params={"href": sweep_shot})
    assert resp.status_code == 200
    assert resp.content == b"fake png bytes"
