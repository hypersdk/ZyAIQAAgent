---
sidebar_position: 3
title: Supported Providers
---

# 10 Cloud Providers, One Platform

HyperSDK Platform connects to all major cloud and virtualization platforms with a unified interface.

## Provider Matrix

| Provider | Export Formats | VM Discovery | Batch Export | Status |
|----------|--------------|-------------|-------------|--------|
| **VMware vSphere** | OVF, OVA, VMDK | ✓ | ✓ | Production |
| **Amazon AWS EC2** | VMDK, VHD, RAW | ✓ | ✓ | Production |
| **Microsoft Azure** | VHD, Image | ✓ | ✓ | Production |
| **Google Cloud** | VMDK, Image | ✓ | ✓ | Production |
| **Microsoft Hyper-V** | VHDX, VHD | ✓ | ✓ | Production |
| **Oracle Cloud (OCI)** | QCOW2, VMDK | ✓ | ✓ | Production |
| **OpenStack** | QCOW2, VMDK, RAW | ✓ | ✓ | Production |
| **Alibaba Cloud** | QCOW2, RAW | ✓ | ✓ | Production |
| **Proxmox VE** | VZDump, VMA | ✓ | ✓ | Production |
| **KubeVirt** | RAW, QCOW2 | ✓ | ✓ | Production |

## Key Capabilities

- **Unified VM Discovery** — Browse VMs across all providers from a single dashboard
- **Cross-Cloud Export** — Export from any provider, deploy to any target
- **Format Conversion** — Automatic format conversion between providers
- **Batch Operations** — Migrate hundreds of VMs with manifest-driven automation
- **Windows & Linux** — Full support for both with auto-detection and driver injection

## OpenStack — source and target

OpenStack is both a **connected provider** (Nova discovery + Glance/Swift export) and a **deploy target** (Glance upload with optional Nova boot via hyper2kvm). **[Machina](/docs/machina)** adds day-2 Nova and Glance management on the hypervisor host — without Horizon.

| Layer | Keystone | Nova | Glance | Swift |
|-------|----------|------|--------|-------|
| **HyperSDK Platform** | Provider auth | Discover / export | Image upload & download | Backup storage |
| **hyper2kvm** | `OS_CLOUD` / openrc | Optional boot after upload | Post-conversion deploy | — |
| **Machina** | Host-side config | Instance lifecycle UI | qcow2 upload & catalog | — |

Full workflow: [OpenStack integration guide](/docs/openstack).

## Deploy Targets

| Target | What You Get |
|--------|-------------|
| **KVM / libvirt** | Production-ready VMs with virtio drivers, network config, and auto-start |
| **KubeVirt** | Kubernetes-native VMs with CRDs, PVC storage, and lifecycle management |
| **OpenStack Glance** | Upload converted QCOW2 to Glance; optional Nova instance boot (flavor, network, keypair) |
| **Local Disk** | Exported disk images for archival, testing, or further processing |

---

## Downloads

- [Public Cloud Providers](pathname:///presentations/standard/12-public-cloud-providers/12-public-cloud-providers.pdf) -- AWS, Azure, GCP, OCI provider details
- [Multi-Cloud Providers](pathname:///presentations/standard/29-multi-cloud-providers/29-multi-cloud-providers.pdf) -- full 10-provider comparison matrix
- [Hyper-V Migration](pathname:///presentations/standard/13-hyperv-migration/13-hyperv-migration.pdf) -- Microsoft Hyper-V specific migration guide

---

[Schedule a Demo](/contact) to discuss your multi-cloud migration needs.
