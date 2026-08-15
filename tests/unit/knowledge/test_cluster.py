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

"""Tests for read-only live cluster diagnostics (mocked; no real cluster)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from knowledge.cluster import (
    get_cluster_summary,
    get_pod_status,
    resolve_namespace,
)
from knowledge.config import clear_settings_cache
from knowledge.live_tools import LIVE_TOOL_NAMES, get_cluster_summary as tool_summary


def test_resolve_namespace_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGE_LIVE_NAMESPACES", "apps,kube-system")
    clear_settings_cache()
    ns, err = resolve_namespace("apps")
    assert ns == "apps" and err is None
    ns, err = resolve_namespace("evil")
    assert ns is None and err and "allowlist" in err
    clear_settings_cache()


def test_invalid_namespace_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGE_LIVE_NAMESPACES", "default")
    clear_settings_cache()
    ns, err = resolve_namespace("../etc")
    assert ns is None and err
    clear_settings_cache()


def test_live_tools_disabled_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_LIVE_CLUSTER_TOOLS", "false")
    clear_settings_cache()
    text = tool_summary.invoke({"namespace": "default"})
    assert "disabled" in text.lower()
    clear_settings_cache()


def test_get_cluster_summary_uses_mock_clients(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_LIVE_CLUSTER_TOOLS", "true")
    monkeypatch.setenv("KNOWLEDGE_LIVE_NAMESPACES", "demo")
    clear_settings_cache()

    pod = SimpleNamespace(
        metadata=SimpleNamespace(name="web-0"),
        status=SimpleNamespace(
            phase="Running",
            container_statuses=[SimpleNamespace(ready=True)],
        ),
        spec=SimpleNamespace(containers=[SimpleNamespace(name="app")]),
    )
    dep = SimpleNamespace(
        metadata=SimpleNamespace(name="web"),
        status=SimpleNamespace(ready_replicas=1),
        spec=SimpleNamespace(replicas=1),
    )
    clients = {
        "core": SimpleNamespace(list_namespaced_pod=lambda ns: SimpleNamespace(items=[pod])),
        "apps": SimpleNamespace(
            list_namespaced_deployment=lambda ns: SimpleNamespace(items=[dep])
        ),
        "custom": SimpleNamespace(),
    }
    monkeypatch.setattr("knowledge.cluster._clients", lambda: clients)
    monkeypatch.setattr(
        "orchestrator.dashboard.k8s.get_namespace",
        lambda: "demo",
    )

    payload = get_cluster_summary("demo")
    assert payload["available"] is True
    assert payload["read_only"] is True
    assert payload["pod_count"] == 1
    assert payload["deployments"][0]["name"] == "web"
    clear_settings_cache()


def test_pod_status_rejects_bad_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGE_LIVE_NAMESPACES", "demo")
    clear_settings_cache()
    payload = get_pod_status("bad name!", "demo")
    assert payload["available"] is False
    clear_settings_cache()


def test_packetwolf_policy_lists_network_policies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_LIVE_CLUSTER_TOOLS", "true")
    monkeypatch.setenv("KNOWLEDGE_LIVE_NAMESPACES", "demo")
    clear_settings_cache()

    class FakeNet:
        def list_namespaced_network_policy(self, ns):
            assert ns == "demo"
            return SimpleNamespace(
                items=[
                    SimpleNamespace(
                        to_dict=lambda: {
                            "metadata": {"name": "deny-egress", "namespace": "demo"},
                            "spec": {"egress": [], "policyTypes": ["Egress"]},
                        }
                    )
                ]
            )

        def read_namespaced_network_policy(self, name, ns):
            raise AssertionError("should list")

    class FakeCustom:
        def get_namespaced_custom_object(self, *args, **kwargs):
            raise RuntimeError("no crd")

        def list_namespaced_custom_object(self, *args, **kwargs):
            raise RuntimeError("no crd")

    monkeypatch.setattr(
        "knowledge.cluster._clients",
        lambda: {"core": SimpleNamespace(), "apps": SimpleNamespace(), "custom": FakeCustom()},
    )
    monkeypatch.setattr(
        "kubernetes.client.NetworkingV1Api",
        lambda: FakeNet(),
    )

    from knowledge.cluster import get_packetwolf_policy

    payload = get_packetwolf_policy(namespace="demo")
    assert payload["available"] is True
    assert payload["network_policies"][0]["name"] == "deny-egress"
    clear_settings_cache()


def test_live_tool_names_are_read_only_verbs() -> None:
    assert "get_cluster_summary" in LIVE_TOOL_NAMES
    assert "get_packetwolf_policy" in LIVE_TOOL_NAMES
    assert "get_vm_migration_status" in LIVE_TOOL_NAMES
    assert "get_guestkit_report" in LIVE_TOOL_NAMES
    assert all(name.startswith("get_") for name in LIVE_TOOL_NAMES)
    assert not any(
        "delete" in name or "patch" in name or "apply" in name for name in LIVE_TOOL_NAMES
    )


