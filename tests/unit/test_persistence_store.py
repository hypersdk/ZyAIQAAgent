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

import time
from datetime import datetime, timezone

from orchestrator.persistence.store import MissionControlStore


def _backdate_heartbeat(store: MissionControlStore, job_id: str, seconds_ago: float) -> None:
    stale = datetime.fromtimestamp(time.time() - seconds_ago, timezone.utc).isoformat()
    with store.connect() as conn:
        conn.execute("UPDATE jobs SET heartbeat_at=? WHERE id=?", (stale, job_id))


def test_job_lifecycle(tmp_path):
    store = MissionControlStore(tmp_path / "state.db")
    job = store.enqueue_job("smoke", {"url": "https://zyvor.dev"}, requested_by="tester")
    assert job["status"] == "queued"
    claimed = store.claim_job()
    assert claimed and claimed["id"] == job["id"]
    assert claimed["status"] == "running"
    store.finish_job(job["id"], result={"passed": 4})
    complete = store.get_job(job["id"])
    assert complete and complete["status"] == "succeeded"
    assert complete["result"]["passed"] == 4


def test_idempotency(tmp_path):
    store = MissionControlStore(tmp_path / "state.db")
    first = store.enqueue_job("smoke", {}, idempotency_key="deploy-123")
    second = store.enqueue_job("smoke", {}, idempotency_key="deploy-123")
    assert first["id"] == second["id"]


def test_schedule_persists_and_redacts(tmp_path):
    store = MissionControlStore(tmp_path / "state.db")
    schedule = store.add_schedule(
        "realtime",
        {"token": {"$secret": "env:QA_TOKEN"}, "url": "https://zyvor.dev"},
        60,
    )
    assert schedule["params"]["token"] == "***"
    assert MissionControlStore(tmp_path / "state.db").list_schedules()[0]["id"] == schedule["id"]


def test_findings_are_deduplicated(tmp_path):
    store = MissionControlStore(tmp_path / "state.db")
    first = store.add_finding("audit", "high", "Broken API", fingerprint="api:/v1/x")
    second = store.add_finding("audit", "high", "Broken API", fingerprint="api:/v1/x")
    assert first == second
    rows = store.list_findings()["findings"]
    assert rows[0]["occurrences"] == 2


def test_webhook_delivery_deduplication(tmp_path):
    store = MissionControlStore(tmp_path / "state.db")
    assert store.record_webhook_delivery("d1", "push", "abc")
    assert not store.record_webhook_delivery("d1", "push", "abc")


def test_persisted_job_rejects_raw_token(tmp_path):
    import pytest
    from orchestrator.security.secrets import SecretReferenceError

    store = MissionControlStore(tmp_path / "state.db")
    with pytest.raises(SecretReferenceError):
        store.enqueue_job("realtime", {"token": "raw-secret"})


def test_recover_stale_jobs_requeues_under_attempt_cap(tmp_path):
    store = MissionControlStore(tmp_path / "state.db")
    job = store.enqueue_job("smoke", {})
    store.claim_job()  # attempt -> 1
    _backdate_heartbeat(store, job["id"], 400)

    result = store.recover_stale_jobs(stale_after_s=300)

    assert result == {"requeued": 1, "dead_lettered": 0}
    refreshed = store.get_job(job["id"])
    assert refreshed and refreshed["status"] == "queued"


def test_recover_stale_jobs_dead_letters_at_attempt_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("ZYVOR_JOB_MAX_ATTEMPTS", "2")
    store = MissionControlStore(tmp_path / "state.db")
    job = store.enqueue_job("smoke", {})
    store.claim_job()  # attempt -> 1
    store.requeue_job(job["id"])  # simulate a crashed worker, back to queued
    store.claim_job()  # attempt -> 2, at the cap
    _backdate_heartbeat(store, job["id"], 400)

    result = store.recover_stale_jobs(stale_after_s=300)

    assert result == {"requeued": 0, "dead_lettered": 1}
    dead = store.get_job(job["id"])
    assert dead and dead["status"] == "failed"
    assert "dead-lettered" in dead["error"]
