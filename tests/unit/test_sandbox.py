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

"""Unit tests for orchestrator/security/sandbox.py.

No live Kubernetes cluster is available in this test environment — the
Job-orchestration happy path is exercised against a mocked kubernetes
client (matching the request/response shapes the real client returns),
not a real cluster. See docs on `run_python` for what that leaves
unverified (RBAC, CNI enforcement, image pull) versus what this proves
(the orchestration logic: Job/ConfigMap lifecycle, status polling, cleanup
ordering, fail-closed behavior when unconfigured)."""

from __future__ import annotations

from unittest.mock import MagicMock

import orchestrator.dashboard.k8s as k8s_module
import orchestrator.security.sandbox as sandbox


def test_available_false_without_namespace_env(monkeypatch):
    monkeypatch.delenv("ZYVOR_SANDBOX_NAMESPACE", raising=False)
    assert sandbox.available() is False


def test_available_false_when_namespace_set_but_no_cluster(monkeypatch):
    monkeypatch.setenv("ZYVOR_SANDBOX_NAMESPACE", "zyvor-qa-sandbox")
    monkeypatch.setattr(k8s_module, "_load_clients", lambda: None)
    assert sandbox.available() is False


def test_available_true_when_namespace_set_and_cluster_reachable(monkeypatch):
    monkeypatch.setenv("ZYVOR_SANDBOX_NAMESPACE", "zyvor-qa-sandbox")
    monkeypatch.setattr(k8s_module, "_load_clients", lambda: {"core": object(), "batch": object()})
    assert sandbox.available() is True


def test_run_python_raises_sandbox_unavailable_without_namespace(monkeypatch):
    monkeypatch.delenv("ZYVOR_SANDBOX_NAMESPACE", raising=False)
    try:
        sandbox.run_python("print('hi')")
        assert False, "expected SandboxUnavailable"
    except sandbox.SandboxUnavailable:
        pass


def test_resolve_egress_cidrs_dedupes_and_skips_ipv6(monkeypatch):
    def fake_getaddrinfo(host, port):
        return [
            (2, 1, 6, "", ("93.184.216.34", 0)),
            (2, 1, 6, "", ("93.184.216.34", 0)),  # duplicate
            (10, 1, 6, "", ("2606:2800:220:1::", 0, 0, 0)),  # IPv6, skipped
        ]

    monkeypatch.setattr(sandbox.socket, "getaddrinfo", fake_getaddrinfo)
    cidrs = sandbox._resolve_egress_cidrs(["example.com"])
    assert cidrs == ["93.184.216.34/32"]


def test_resolve_egress_cidrs_skips_unresolvable_host(monkeypatch):
    import socket as real_socket

    def fake_getaddrinfo(host, port):
        raise real_socket.gaierror("nope")

    monkeypatch.setattr(sandbox.socket, "getaddrinfo", fake_getaddrinfo)
    assert sandbox._resolve_egress_cidrs(["does-not-resolve.invalid"]) == []


class _FakeStatus:
    def __init__(self, succeeded=None, failed=None):
        self.succeeded = succeeded
        self.failed = failed


class _FakeJobStatusResponse:
    def __init__(self, status):
        self.status = status


class _FakeTerminatedState:
    def __init__(self, exit_code):
        self.exit_code = exit_code


class _FakeContainerState:
    def __init__(self, exit_code):
        self.terminated = _FakeTerminatedState(exit_code)


class _FakeContainerStatus:
    def __init__(self, exit_code):
        self.state = _FakeContainerState(exit_code)


class _FakePodStatus:
    def __init__(self, exit_code):
        self.container_statuses = [_FakeContainerStatus(exit_code)]


class _FakePod:
    def __init__(self, name, exit_code):
        self.metadata = MagicMock(name=name)
        self.status = _FakePodStatus(exit_code)


class _FakePodList:
    def __init__(self, pods):
        self.items = pods


def test_run_python_happy_path_creates_and_cleans_up_job(monkeypatch):
    monkeypatch.setenv("ZYVOR_SANDBOX_NAMESPACE", "zyvor-qa-sandbox")

    fake_batch = MagicMock()
    fake_batch.read_namespaced_job_status.return_value = _FakeJobStatusResponse(_FakeStatus(succeeded=1))
    fake_core = MagicMock()
    fake_core.list_namespaced_pod.return_value = _FakePodList([_FakePod("zyvor-poc-abc-xyz", 0)])
    fake_core.read_namespaced_pod_log.return_value = "VERIFIED: true - status code differs\n"

    monkeypatch.setattr(k8s_module, "_load_clients", lambda: {"core": fake_core, "batch": fake_batch})

    result = sandbox.run_python("print('hi')", timeout_s=10)

    assert result.exit_code == 0
    assert "VERIFIED: true" in result.stdout
    assert result.timed_out is False
    # Job + ConfigMap were created, and both cleaned up in the finally block.
    assert fake_batch.create_namespaced_job.call_count == 1
    assert fake_core.create_namespaced_config_map.call_count == 1
    assert fake_batch.delete_namespaced_job.call_count == 1
    assert fake_core.delete_namespaced_config_map.call_count == 1


def test_run_python_sets_image_pull_policy_if_not_present(monkeypatch):
    """Regression: found live against a real k3s cluster — a custom,
    locally-built/imported image (e.g. host_pentest's paramiko image) tagged
    ':latest' defaults to imagePullPolicy Always, which tries (and fails) to
    pull from a registry even though the image is already on the node."""
    monkeypatch.setenv("ZYVOR_SANDBOX_NAMESPACE", "zyvor-qa-sandbox")

    fake_batch = MagicMock()
    fake_batch.read_namespaced_job_status.return_value = _FakeJobStatusResponse(_FakeStatus(succeeded=1))
    fake_core = MagicMock()
    fake_core.list_namespaced_pod.return_value = _FakePodList([_FakePod("zyvor-poc-abc-xyz", 0)])
    fake_core.read_namespaced_pod_log.return_value = "VERIFIED: true - ok\n"
    monkeypatch.setattr(k8s_module, "_load_clients", lambda: {"core": fake_core, "batch": fake_batch})

    sandbox.run_python("print('hi')", timeout_s=10, image="localhost/custom-image:latest")

    job = fake_batch.create_namespaced_job.call_args[0][1]
    container = job.spec.template.spec.containers[0]
    assert container.image == "localhost/custom-image:latest"
    assert container.image_pull_policy == "IfNotPresent"


def test_run_python_normalizes_str_of_bytes_pod_log(monkeypatch):
    """Regression: found live against a real k3s cluster — the kubernetes
    client sometimes returns a pod log as the *string representation* of a
    bytes object (`"b'...'"`) rather than a decoded str. `orchestrator/
    dashboard/k8s.py::_normalize_log_text` already exists to fix exactly
    this for the dashboard's own pod-log viewer; run_python() must reuse it,
    not read_namespaced_pod_log()'s raw return value."""
    monkeypatch.setenv("ZYVOR_SANDBOX_NAMESPACE", "zyvor-qa-sandbox")

    fake_batch = MagicMock()
    fake_batch.read_namespaced_job_status.return_value = _FakeJobStatusResponse(_FakeStatus(succeeded=1))
    fake_core = MagicMock()
    fake_core.list_namespaced_pod.return_value = _FakePodList([_FakePod("zyvor-poc-abc-xyz", 0)])
    fake_core.read_namespaced_pod_log.return_value = "b'VERIFIED: true - status code differs\\n'"

    monkeypatch.setattr(k8s_module, "_load_clients", lambda: {"core": fake_core, "batch": fake_batch})

    result = sandbox.run_python("print('hi')", timeout_s=10)

    assert result.stdout == "VERIFIED: true - status code differs\n"
    assert "b'" not in result.stdout


def test_run_python_marks_timed_out_when_job_never_completes(monkeypatch):
    monkeypatch.setenv("ZYVOR_SANDBOX_NAMESPACE", "zyvor-qa-sandbox")

    fake_batch = MagicMock()
    fake_batch.read_namespaced_job_status.return_value = _FakeJobStatusResponse(_FakeStatus())  # never finishes
    fake_core = MagicMock()
    fake_core.list_namespaced_pod.return_value = _FakePodList([])

    monkeypatch.setattr(k8s_module, "_load_clients", lambda: {"core": fake_core, "batch": fake_batch})
    monkeypatch.setattr(sandbox.time, "sleep", lambda _s: None)  # don't actually wait in tests

    real_time = sandbox.time.time
    call_count = {"n": 0}

    def fake_time():
        call_count["n"] += 1
        # First call establishes the deadline; subsequent calls jump past it
        # immediately so the poll loop exits on the first iteration.
        return real_time() if call_count["n"] == 1 else real_time() + 1000

    monkeypatch.setattr(sandbox.time, "time", fake_time)

    result = sandbox.run_python("while True: pass", timeout_s=5)
    assert result.timed_out is True
    assert fake_batch.delete_namespaced_job.call_count == 1
