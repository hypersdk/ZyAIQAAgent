---
sidebar_position: 2
title: Quickstart
description: Get started with HyperSDK Platform in 5 minutes — install, configure, export, convert, and verify your first VM migration.
---

# Quickstart

Get your first VM migration running in under 5 minutes. This guide walks you through installing HyperSDK Platform, configuring a provider, exporting a VM, converting it with hyper2kvm, and verifying the result.

## Prerequisites

- Linux host (Ubuntu 22.04+, Fedora 38+, or RHEL 9+)
- Root or sudo access
- At least one VM provider configured (vCenter, Proxmox, oVirt, etc.)
- 10 GB free disk space for exported images

## Step 1: Install HyperSDK Platform

Download and install the latest release:

```bash
curl -fsSL https://zyvor.dev/install | sudo bash
```

Verify the installation:

```bash
hypersdk version
```

Expected output:

```
HyperSDK Platform CLI v2.4.0 "Zeus"
Build: 2026-04-01
Go: go1.22.2
Platform: linux/amd64
```

## Step 2: Configure a Provider

Initialize your configuration and add a provider. This example uses a vCenter connection:

```bash
hypersdk init
hypersdk provider add vcenter \
  --host vcenter.example.com \
  --username admin@vsphere.local \
  --password "${VCENTER_PASSWORD}" \
  --datacenter DC1
```

Verify the provider connection:

```bash
hypersdk provider list
```

Expected output:

```
NAME       TYPE      STATUS      VMs    HOST
vcenter1   vcenter   connected   47     vcenter.example.com
```

## Step 3: Export a VM

List available VMs from your provider and export one:

```bash
hypersdk vm list --provider vcenter1
```

```
NAME              PROVIDER    STATUS    CPU   MEMORY   DISK
web-server-01     vcenter1    running   4     8 GB     80 GB
db-server-01      vcenter1    running   8     32 GB    500 GB
app-worker-03     vcenter1    stopped   2     4 GB     40 GB
```

Export the VM:

```bash
hypersdk vm export web-server-01 --provider vcenter1 --output ./exports/
```

```
Exporting web-server-01...
  Snapshot created: snap-20260410-001
  Downloading disk: web-server-01-disk0.vmdk (80 GB)
  Progress: [========================================] 100%
  Export complete: ./exports/web-server-01/

Export Summary:
  VM:       web-server-01
  Disks:    1 (80 GB)
  Format:   VMDK
  Duration: 3m 42s
```

## Step 4: Convert with hyper2kvm

Convert the exported VM image from VMDK to qcow2 format for use with KVM/QEMU:

```bash
hyper2kvm convert ./exports/web-server-01/web-server-01-disk0.vmdk \
  --format qcow2 \
  --output ./converted/
```

```
Converting web-server-01-disk0.vmdk -> qcow2...
  Source format:  VMDK (80 GB)
  Target format:  qcow2
  Virtio drivers: injected
  Network config:  preserved
  Progress: [========================================] 100%
  Output: ./converted/web-server-01-disk0.qcow2

Conversion Summary:
  Input:     80 GB (VMDK)
  Output:    24 GB (qcow2, compressed)
  Duration:  1m 18s
```

## Step 5: Verify the Migration

Run the built-in verification to confirm the converted image is healthy:

```bash
hypersdk verify ./converted/web-server-01-disk0.qcow2
```

```
Verifying web-server-01-disk0.qcow2...
  Format:           qcow2 (valid)
  Boot sector:      OK
  Filesystem:       ext4 (clean)
  Virtio drivers:   present
  Network config:   eth0 (DHCP)
  Guest agent:      compatible

Verification: PASSED
```

You can also do a test boot to confirm the VM starts correctly:

```bash
hypersdk vm test-boot ./converted/web-server-01-disk0.qcow2 --timeout 60
```

```
Test boot: web-server-01-disk0.qcow2
  BIOS:     OK
  Kernel:   loaded (5.15.0-generic)
  Init:     systemd reached default.target
  Network:  eth0 UP
  SSH:      listening on port 22
  Duration: 28s

Test boot: PASSED
```

## Next Steps

You have successfully exported, converted, and verified your first VM. Here is where to go next:

- **[Platform Overview](/docs/intro)** — Full architecture and concepts
- **[Providers](/docs/providers)** — Configure additional providers (Proxmox, oVirt, major public clouds, and more)
- **[hyper2kvm Reference](/docs/hyper2kvm)** — Advanced conversion options, batch mode, driver injection
- **[Migration Guide](/docs/migration-guide)** — Plan and execute large-scale migrations
- **[Dashboard](/docs/dashboard)** — Monitor migrations via the web UI
- **[API Reference](/docs/api)** — Automate migrations with the REST API

## Downloads

- [Quickstart & POC Guide](pathname:///presentations/standard/10-quickstart-poc/10-quickstart-poc.pdf) -- step-by-step deployment walkthrough
- [Training & Onboarding](pathname:///presentations/standard/20-training-onboarding/20-training-onboarding.pdf) -- team onboarding materials
