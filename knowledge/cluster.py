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

"""Read-only live cluster diagnostics for the knowledge QA agent.

Mutating APIs (delete/patch/create) are intentionally absent. All tools degrade
to structured unavailable payloads when the cluster or feature is unreachable.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from knowledge.config import get_settings

LOGGER = logging.getLogger(__name__)

_NAMESPACE_RE = re.compile(r"^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$")


def live_diagnostics_enabled() -> bool:
    return bool(get_settings().enable_live_cluster_tools)


def allowed_namespaces() -> tuple[str, ...]:
    settings = get_settings()
    configured = settings.knowledge_live_namespaces
    if configured:
        return configured
    # Default: Mission Control namespace only.
    try:
        from orchestrator.dashboard.k8s import get_namespace

        return (get_namespace(),)
    except Exception:
        return ("default",)


def resolve_namespace(requested: str | None) -> tuple[str | None, str | None]:
    """Return (namespace, error). Error is set when the request is denied."""
    allowed = allowed_namespaces()
    if requested is None or not str(requested).strip():
        return allowed[0], None
    name = str(requested).strip().lower()
    if not _NAMESPACE_RE.fullmatch(name):
        return None, f"Invalid namespace name: {requested!r}"
    if name not in allowed and "*" not in allowed:
        return None, (
            f"Namespace {name!r} is not in the live-diagnostics allowlist "
            f"({', '.join(allowed)})."
        )
    return name, None


def _clients() -> dict[str, Any] | None:
    from orchestrator.dashboard.k8s import _load_clients

    return _load_clients()


def _unavailable(reason: str, **extra: Any) -> dict[str, Any]:
    payload = {"available": False, "read_only": True, "error": reason}
    payload.update(extra)
    return payload


def get_cluster_summary(namespace: str | None = None) -> dict[str, Any]:
    ns, err = resolve_namespace(namespace)
    if err or not ns:
        return _unavailable(err or "namespace denied")

    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    from orchestrator.dashboard import k8s as dash_k8s

    # Temporarily observe the requested namespace via existing helpers by
    # overriding DASHBOARD_NAMESPACE is fragile; query directly instead.
    try:
        pods = clients["core"].list_namespaced_pod(ns)
        deployments = clients["apps"].list_namespaced_deployment(ns)
    except Exception as exc:
        return _unavailable(str(exc), namespace=ns)

    phases: dict[str, int] = {}
    not_ready: list[str] = []
    for pod in pods.items:
        phase = pod.status.phase or "Unknown"
        phases[phase] = phases.get(phase, 0) + 1
        ready = sum(1 for s in (pod.status.container_statuses or []) if s.ready)
        total = len(pod.spec.containers or [])
        if total and ready < total:
            not_ready.append(pod.metadata.name)

    dep_rows = []
    for dep in deployments.items:
        dep_rows.append(
            {
                "name": dep.metadata.name,
                "ready": dep.status.ready_replicas or 0,
                "desired": dep.spec.replicas or 0,
            }
        )

    return {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "pod_count": len(pods.items),
        "pod_phases": phases,
        "not_ready_pods": not_ready[:20],
        "deployments": dep_rows[:40],
        "dashboard_namespace": dash_k8s.get_namespace(),
    }


def get_recent_events(namespace: str | None = None, limit: int = 25) -> dict[str, Any]:
    ns, err = resolve_namespace(namespace)
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    try:
        result = clients["core"].list_namespaced_event(ns)
    except Exception as exc:
        return _unavailable(str(exc), namespace=ns)

    events: list[dict[str, Any]] = []
    for ev in result.items:
        when = ev.last_timestamp or ev.event_time or (
            ev.metadata.creation_timestamp if ev.metadata else None
        )
        events.append(
            {
                "type": ev.type,
                "reason": ev.reason,
                "object": (
                    f"{ev.involved_object.kind}/{ev.involved_object.name}"
                    if ev.involved_object
                    else ""
                ),
                "message": (ev.message or "")[:240],
                "count": ev.count or 1,
                "at": when.isoformat() if when else None,
            }
        )
    events.sort(key=lambda item: item["at"] or "", reverse=True)
    return {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "events": events[: max(1, min(limit, 100))],
    }


def get_pod_status(name: str, namespace: str | None = None) -> dict[str, Any]:
    ns, err = resolve_namespace(namespace)
    if err or not ns:
        return _unavailable(err or "namespace denied")
    if not name or not re.fullmatch(r"[A-Za-z0-9]([-A-Za-z0-9_.]{0,251}[A-Za-z0-9])?", name):
        return _unavailable(f"Invalid pod name: {name!r}", namespace=ns)

    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    try:
        pod = clients["core"].read_namespaced_pod(name, ns)
    except Exception as exc:
        return _unavailable(str(exc), namespace=ns, name=name)

    containers = []
    for status in pod.status.container_statuses or []:
        state = "unknown"
        if status.state and status.state.running:
            state = "running"
        elif status.state and status.state.waiting:
            state = f"waiting:{status.state.waiting.reason or 'unknown'}"
        elif status.state and status.state.terminated:
            state = f"terminated:{status.state.terminated.reason or 'unknown'}"
        containers.append(
            {
                "name": status.name,
                "ready": bool(status.ready),
                "restarts": status.restart_count or 0,
                "state": state,
                "image": status.image,
            }
        )

    return {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "name": pod.metadata.name,
        "phase": pod.status.phase,
        "node": pod.spec.node_name,
        "pod_ip": pod.status.pod_ip,
        "labels": dict(pod.metadata.labels or {}),
        "containers": containers,
    }


def get_kubevirt_vm_status(
    name: str | None = None,
    namespace: str | None = None,
) -> dict[str, Any]:
    ns, err = resolve_namespace(namespace)
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    custom = clients["custom"]
    try:
        if name:
            vm = custom.get_namespaced_custom_object(
                "kubevirt.io", "v1", ns, "virtualmachines", name
            )
            items = [vm]
        else:
            listed = custom.list_namespaced_custom_object(
                "kubevirt.io", "v1", ns, "virtualmachines"
            )
            items = listed.get("items", [])
    except Exception as exc:
        return _unavailable(
            f"KubeVirt API unavailable: {exc}",
            namespace=ns,
            hint="Install KubeVirt CRDs or check RBAC for virtualmachines",
        )

    vms = []
    for item in items[:40]:
        meta = item.get("metadata", {})
        status = item.get("status", {})
        vms.append(
            {
                "name": meta.get("name"),
                "printable_status": status.get("printableStatus") or status.get("phase"),
                "ready": status.get("ready"),
                "created": bool((item.get("spec") or {}).get("running", True)),
            }
        )
    return {"available": True, "read_only": True, "namespace": ns, "virtualmachines": vms}


def get_cilium_status(namespace: str | None = "kube-system") -> dict[str, Any]:
    # Cilium usually lives in kube-system; still enforce allowlist.
    ns, err = resolve_namespace(namespace or "kube-system")
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    try:
        pods = clients["core"].list_namespaced_pod(
            ns, label_selector="k8s-app=cilium"
        )
        if not pods.items:
            pods = clients["core"].list_namespaced_pod(ns, label_selector="app.kubernetes.io/name=cilium-agent")
    except Exception as exc:
        return _unavailable(str(exc), namespace=ns)

    agents = []
    for pod in pods.items[:30]:
        ready, total = 0, len(pod.spec.containers or [])
        ready = sum(1 for s in (pod.status.container_statuses or []) if s.ready)
        agents.append(
            {
                "name": pod.metadata.name,
                "phase": pod.status.phase,
                "ready": f"{ready}/{total}",
                "node": pod.spec.node_name,
            }
        )
    return {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "cilium_agent_pods": agents,
        "agent_count": len(agents),
    }


def get_hubble_health(namespace: str | None = "kube-system") -> dict[str, Any]:
    ns, err = resolve_namespace(namespace or "kube-system")
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    try:
        pods = clients["core"].list_namespaced_pod(ns, label_selector="k8s-app=hubble-relay")
        if not pods.items:
            pods = clients["core"].list_namespaced_pod(
                ns, label_selector="app.kubernetes.io/name=hubble-relay"
            )
        svc = None
        try:
            svc = clients["core"].read_namespaced_service("hubble-relay", ns)
        except Exception:
            svc = None
    except Exception as exc:
        return _unavailable(str(exc), namespace=ns)

    relay_pods = []
    for pod in pods.items[:20]:
        ready = sum(1 for s in (pod.status.container_statuses or []) if s.ready)
        total = len(pod.spec.containers or [])
        relay_pods.append(
            {
                "name": pod.metadata.name,
                "phase": pod.status.phase,
                "ready": f"{ready}/{total}",
            }
        )

    ports = []
    if svc is not None:
        for port in svc.spec.ports or []:
            ports.append({"name": port.name, "port": port.port, "target": port.target_port})

    return {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "hubble_relay_pods": relay_pods,
        "service_ports": ports,
        "healthy": bool(relay_pods) and all(p["phase"] == "Running" for p in relay_pods),
    }


def get_ceph_health(namespace: str | None = "rook-ceph") -> dict[str, Any]:
    ns, err = resolve_namespace(namespace or "rook-ceph")
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    try:
        pods = clients["core"].list_namespaced_pod(ns, label_selector="app=rook-ceph-tools")
        if not pods.items:
            pods = clients["core"].list_namespaced_pod(ns, label_selector="app=rook-ceph-operator")
    except Exception as exc:
        return _unavailable(str(exc), namespace=ns)

    rows = [
        {
            "name": pod.metadata.name,
            "phase": pod.status.phase,
            "labels": dict(pod.metadata.labels or {}),
        }
        for pod in pods.items[:20]
    ]
    return {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "pods": rows,
        "note": "Ceph HEALTH_OK detail requires rook toolbox exec; this tool only reports pod presence.",
    }


def get_node_capacity() -> dict[str, Any]:
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable")
    try:
        nodes = clients["core"].list_node()
    except Exception as exc:
        return _unavailable(str(exc))

    rows = []
    for node in nodes.items[:100]:
        allocatable = node.status.allocatable or {}
        conditions = {
            c.type: c.status for c in (node.status.conditions or []) if c.type
        }
        rows.append(
            {
                "name": node.metadata.name,
                "cpu": allocatable.get("cpu"),
                "memory": allocatable.get("memory"),
                "pods": allocatable.get("pods"),
                "ready": conditions.get("Ready"),
            }
        )
    return {"available": True, "read_only": True, "nodes": rows}


def _summarize_policy_item(item: dict[str, Any]) -> dict[str, Any]:
    meta = item.get("metadata") or {}
    spec = item.get("spec") or {}
    return {
        "name": meta.get("name"),
        "namespace": meta.get("namespace"),
        "labels": dict(meta.get("labels") or {}),
        "has_ingress": "ingress" in spec,
        "has_egress": "egress" in spec,
        "policy_types": spec.get("policyTypes"),
        "spec_keys": sorted(spec.keys())[:20],
    }


def get_packetwolf_policy(
    name: str | None = None,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Read-only network policy inventory (PacketWolf CR, Cilium, K8s NetworkPolicy)."""
    ns, err = resolve_namespace(namespace)
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    custom = clients["custom"]
    found: dict[str, Any] = {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "packetwolf_policies": [],
        "cilium_network_policies": [],
        "network_policies": [],
        "errors": [],
    }

    try:
        if name:
            item = custom.get_namespaced_custom_object(
                "networking.packetwolf.io",
                "v1alpha1",
                ns,
                "networkpolicies",
                name,
            )
            found["packetwolf_policies"] = [_summarize_policy_item(item)]
        else:
            listed = custom.list_namespaced_custom_object(
                "networking.packetwolf.io",
                "v1alpha1",
                ns,
                "networkpolicies",
            )
            found["packetwolf_policies"] = [
                _summarize_policy_item(item) for item in listed.get("items", [])[:40]
            ]
    except Exception as exc:
        found["errors"].append(f"packetwolf: {exc}")

    try:
        listed = custom.list_namespaced_custom_object(
            "cilium.io", "v2", ns, "ciliumnetworkpolicies"
        )
        items = listed.get("items", [])
        if name:
            items = [i for i in items if (i.get("metadata") or {}).get("name") == name]
        found["cilium_network_policies"] = [_summarize_policy_item(i) for i in items[:40]]
    except Exception as exc:
        found["errors"].append(f"cilium: {exc}")

    try:
        import importlib

        client_mod = importlib.import_module("kubernetes.client")
        net = client_mod.NetworkingV1Api()
        if name:
            pol = net.read_namespaced_network_policy(name, ns)
            items = [pol.to_dict()]
        else:
            items = [p.to_dict() for p in net.list_namespaced_network_policy(ns).items]
        found["network_policies"] = [_summarize_policy_item(i) for i in items[:40]]
    except Exception as exc:
        found["errors"].append(f"networkpolicy: {exc}")

    total = (
        len(found["packetwolf_policies"])
        + len(found["cilium_network_policies"])
        + len(found["network_policies"])
    )
    if total == 0 and found["errors"]:
        found["available"] = False
        found["error"] = "; ".join(found["errors"][:3])
    return found


def get_vm_migration_status(
    name: str | None = None,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Read-only KubeVirt VirtualMachineInstanceMigration status."""
    ns, err = resolve_namespace(namespace)
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    custom = clients["custom"]
    try:
        if name:
            item = custom.get_namespaced_custom_object(
                "kubevirt.io", "v1", ns, "virtualmachineinstancemigrations", name
            )
            items = [item]
        else:
            listed = custom.list_namespaced_custom_object(
                "kubevirt.io", "v1", ns, "virtualmachineinstancemigrations"
            )
            items = listed.get("items", [])
    except Exception as exc:
        return _unavailable(
            f"KubeVirt migration API unavailable: {exc}",
            namespace=ns,
        )

    migrations = []
    for item in items[:40]:
        meta = item.get("metadata") or {}
        status = item.get("status") or {}
        spec = item.get("spec") or {}
        migrations.append(
            {
                "name": meta.get("name"),
                "vmi_name": spec.get("vmiName"),
                "phase": status.get("phase"),
                "completed": status.get("completed"),
                "failed": status.get("failed"),
            }
        )
    return {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "migrations": migrations,
    }


def get_guestkit_report(
    name: str | None = None,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Read-only GuestKit / disk-inspection related Jobs, ConfigMaps and CR presence."""
    ns, err = resolve_namespace(namespace)
    if err or not ns:
        return _unavailable(err or "namespace denied")
    clients = _clients()
    if not clients:
        return _unavailable("Kubernetes API unavailable", namespace=ns)

    payload: dict[str, Any] = {
        "available": True,
        "read_only": True,
        "namespace": ns,
        "jobs": [],
        "configmaps": [],
        "custom_resources": [],
        "errors": [],
    }

    try:
        jobs = clients["batch"].list_namespaced_job(
            ns, label_selector="app.kubernetes.io/name=guestkit"
        )
        if not jobs.items:
            jobs = clients["batch"].list_namespaced_job(ns)
            items = [
                j
                for j in jobs.items
                if "guestkit" in (j.metadata.name or "").lower()
                or "guestkit" in str(j.metadata.labels or {}).lower()
            ]
        else:
            items = list(jobs.items)
        if name:
            items = [j for j in items if j.metadata.name == name]
        for job in items[:30]:
            payload["jobs"].append(
                {
                    "name": job.metadata.name,
                    "succeeded": (job.status.succeeded or 0),
                    "failed": (job.status.failed or 0),
                    "active": (job.status.active or 0),
                    "completion_time": (
                        job.status.completion_time.isoformat()
                        if job.status.completion_time
                        else None
                    ),
                }
            )
    except Exception as exc:
        payload["errors"].append(f"jobs: {exc}")

    try:
        cms = clients["core"].list_namespaced_config_map(ns)
        for cm in cms.items:
            cname = cm.metadata.name or ""
            labels = str(cm.metadata.labels or {}).lower()
            is_guestkit = "guestkit" in cname.lower() or "guestkit" in labels
            if name:
                if cname != name and not is_guestkit:
                    continue
                if cname != name and name not in cname:
                    continue
            elif not is_guestkit:
                continue
            keys = list((cm.data or {}).keys())[:20]
            payload["configmaps"].append({"name": cname, "keys": keys})
            if len(payload["configmaps"]) >= 30:
                break
    except Exception as exc:
        payload["errors"].append(f"configmaps: {exc}")

    # Best-effort GuestKit CRD probe.
    try:
        listed = clients["custom"].list_namespaced_custom_object(
            "guestkit.zyvor.io", "v1alpha1", ns, "inspectionreports"
        )
        items = listed.get("items", [])
        if name:
            items = [i for i in items if (i.get("metadata") or {}).get("name") == name]
        for item in items[:20]:
            meta = item.get("metadata") or {}
            status = item.get("status") or {}
            payload["custom_resources"].append(
                {
                    "name": meta.get("name"),
                    "phase": status.get("phase") or status.get("state"),
                    "summary": status.get("summary") or status.get("message"),
                }
            )
    except Exception as exc:
        payload["errors"].append(f"guestkit-crd: {exc}")

    total = (
        len(payload["jobs"])
        + len(payload["configmaps"])
        + len(payload["custom_resources"])
    )
    if total == 0 and payload["errors"]:
        # Still available=True with empty inventory when CRD missing but API works —
        # only mark unavailable when we couldn't talk to the cluster at all.
        pass
    payload["note"] = (
        "GuestKit inspection details may live in Job logs or CR status; "
        "this tool is read-only inventory, not a conversion trigger."
    )
    return payload


def format_live_payload(title: str, payload: dict[str, Any]) -> str:
    import json

    body = json.dumps(payload, indent=2, default=str)
    return (
        f"{title}\n"
        "This is observed live cluster state (read-only). "
        "It is not a documentation citation.\n"
        f"{body}"
    )
