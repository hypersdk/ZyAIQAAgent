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

"""Read-only live infrastructure tools for the Zyvor knowledge agent."""

from __future__ import annotations

from langchain.tools import tool

from knowledge import cluster


def _guard() -> str | None:
    if not cluster.live_diagnostics_enabled():
        return (
            "Live cluster diagnostics are disabled. "
            "Set ENABLE_LIVE_CLUSTER_TOOLS=true on the server to enable read-only tools."
        )
    return None


@tool
def get_cluster_summary(namespace: str | None = None) -> str:
    """Read-only summary of pods and deployments in an allowed namespace."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "Cluster summary",
        cluster.get_cluster_summary(namespace),
    )


@tool
def get_recent_events(namespace: str | None = None, limit: int = 25) -> str:
    """Read-only recent Kubernetes events for an allowed namespace."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "Recent events",
        cluster.get_recent_events(namespace, limit=limit),
    )


@tool
def get_pod_status(name: str, namespace: str | None = None) -> str:
    """Read-only status for a single pod in an allowed namespace."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "Pod status",
        cluster.get_pod_status(name, namespace),
    )


@tool
def get_kubevirt_vm_status(name: str | None = None, namespace: str | None = None) -> str:
    """Read-only KubeVirt VirtualMachine status (list or one VM) in an allowed namespace."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "KubeVirt VM status",
        cluster.get_kubevirt_vm_status(name, namespace),
    )


@tool
def get_cilium_status(namespace: str | None = "kube-system") -> str:
    """Read-only Cilium agent pod health in an allowed namespace (usually kube-system)."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "Cilium status",
        cluster.get_cilium_status(namespace),
    )


@tool
def get_hubble_health(namespace: str | None = "kube-system") -> str:
    """Read-only Hubble Relay pod/service health in an allowed namespace."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "Hubble health",
        cluster.get_hubble_health(namespace),
    )


@tool
def get_ceph_health(namespace: str | None = "rook-ceph") -> str:
    """Read-only Rook/Ceph related pod presence in an allowed namespace."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "Ceph health (pod presence)",
        cluster.get_ceph_health(namespace),
    )


@tool
def get_node_capacity() -> str:
    """Read-only node allocatable capacity and Ready condition."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload("Node capacity", cluster.get_node_capacity())


@tool
def get_packetwolf_policy(name: str | None = None, namespace: str | None = None) -> str:
    """Read-only PacketWolf / Cilium / Kubernetes NetworkPolicy inventory for a namespace."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "PacketWolf / network policies",
        cluster.get_packetwolf_policy(name, namespace),
    )


@tool
def get_vm_migration_status(name: str | None = None, namespace: str | None = None) -> str:
    """Read-only KubeVirt VirtualMachineInstanceMigration status."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "VM migration status",
        cluster.get_vm_migration_status(name, namespace),
    )


@tool
def get_guestkit_report(name: str | None = None, namespace: str | None = None) -> str:
    """Read-only GuestKit inspection Jobs, ConfigMaps and CR inventory (never triggers conversion)."""

    blocked = _guard()
    if blocked:
        return blocked
    return cluster.format_live_payload(
        "GuestKit report inventory",
        cluster.get_guestkit_report(name, namespace),
    )


LIVE_TOOLS = [
    get_cluster_summary,
    get_recent_events,
    get_pod_status,
    get_kubevirt_vm_status,
    get_cilium_status,
    get_hubble_health,
    get_ceph_health,
    get_node_capacity,
    get_packetwolf_policy,
    get_vm_migration_status,
    get_guestkit_report,
]

LIVE_TOOL_NAMES = [tool_obj.name for tool_obj in LIVE_TOOLS]
