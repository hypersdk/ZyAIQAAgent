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

"""HTTP-level tests for GET /api/v2/jobs/{job_id}/artifact -- authenticated
artifact streaming, gated on the href being one this job's own result
actually recorded (not an arbitrary client-supplied path)."""

from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from orchestrator.dashboard.jobs import _repo_root
from orchestrator.persistence.store import get_store
from orchestrator.webhook import create_app


@pytest.fixture()
def artifact_file():
    """A real file under reports/artifacts/, matching where _persist_artifacts
    actually writes them, cleaned up after the test regardless of outcome."""
    rel_dir = _repo_root() / "reports" / "artifacts" / "videos" / "test-fixture-run"
    rel_dir.mkdir(parents=True, exist_ok=True)
    path = rel_dir / "sample-test.webm"
    path.write_bytes(b"fake webm bytes")
    href = "/reports/artifacts/videos/test-fixture-run/sample-test.webm"
    yield href
    shutil.rmtree(rel_dir, ignore_errors=True)


def _seed_job_with_artifact(href: str) -> str:
    store = get_store()
    job = store.enqueue_job("smoke", {})
    store.finish_job(
        job["id"],
        result={"cases": [{"title": "sample test", "status": "passed", "video": href, "trace": None}]},
    )
    return job["id"]


def test_get_job_artifact_streams_a_known_href(artifact_file):
    job_id = _seed_job_with_artifact(artifact_file)
    client = TestClient(create_app())
    resp = client.get(f"/api/v2/jobs/{job_id}/artifact", params={"href": artifact_file})
    assert resp.status_code == 200
    assert resp.content == b"fake webm bytes"


def test_get_job_artifact_rejects_an_href_the_job_never_recorded(artifact_file):
    job_id = _seed_job_with_artifact(artifact_file)
    client = TestClient(create_app())
    resp = client.get(
        f"/api/v2/jobs/{job_id}/artifact",
        params={"href": "/reports/artifacts/videos/some-other-run/not-mine.webm"},
    )
    assert resp.status_code == 404


def test_get_job_artifact_404s_for_missing_job(artifact_file):
    client = TestClient(create_app())
    resp = client.get("/api/v2/jobs/does-not-exist/artifact", params={"href": artifact_file})
    assert resp.status_code == 404


def test_get_job_artifact_rejects_path_traversal_even_if_it_matched(artifact_file):
    """Belt-and-suspenders: even if a case dict somehow recorded a
    traversal-shaped href (e.g. a future bug in _persist_artifacts), the
    resolved-path check must still refuse to serve outside reports/."""
    job_id = _seed_job_with_artifact(artifact_file)
    store = get_store()
    store.finish_job(
        job_id,
        result={
            "cases": [
                {
                    "title": "sample test",
                    "status": "passed",
                    "video": "/reports/../../etc/passwd",
                    "trace": None,
                }
            ]
        },
    )
    client = TestClient(create_app())
    resp = client.get(f"/api/v2/jobs/{job_id}/artifact", params={"href": "/reports/../../etc/passwd"})
    assert resp.status_code == 400
