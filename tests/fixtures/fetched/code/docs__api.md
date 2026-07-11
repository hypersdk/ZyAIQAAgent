---
sidebar_position: 6
title: REST API
---

# REST API

HyperSDK Platform exposes 2,000+ REST API endpoints across all products for full automation and integration.

## Base URL

```
https://your-server:5080/api/v1/
```

All endpoints are prefixed with `/api/v1/`. Legacy paths (without prefix) are also supported for backward compatibility.

## Authentication

```bash
# Login
curl -sk -X POST https://your-server:5080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'

# Use the returned token
curl -sk -H "Authorization: Bearer TOKEN" \
  https://your-server:5080/api/v1/jobs
```

## Core Endpoints

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | List all jobs |
| POST | `/jobs` | Create a new export/migration job |
| GET | `/jobs/{id}` | Get job status |
| DELETE | `/jobs/{id}` | Cancel a job |
| GET | `/jobs/{id}/logs` | Stream job logs |

### VMs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vms/list` | List VMs from connected provider |
| POST | `/vms/browse` | Browse VM details |
| POST | `/vms/compare` | Compare source and target VMs |
| POST | `/vms/deploy` | Deploy a converted VM |

### Providers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/providers` | List configured providers |
| POST | `/providers/connect` | Connect to a cloud provider |
| GET | `/providers/capabilities` | Detect provider capabilities |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/system/health` | Detailed system metrics |
| GET | `/system/alerts` | Active alerts |
| GET | `/metrics` | Prometheus-format metrics |
| GET | `/readiness` | Migration readiness checks |

### Upload & Download

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload/init` | Initialize chunked upload |
| POST | `/upload/chunk` | Upload a chunk (10 MB) |
| POST | `/upload/complete` | Finalize upload |
| GET | `/upload/status/{id}` | Check upload progress |
| GET | `/download` | Download a VM disk image |
| GET | `/browse/files` | Browse server filesystem |

### Scheduling

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/schedules` | List scheduled jobs |
| POST | `/schedules` | Create a schedule (cron format) |
| DELETE | `/schedules/{id}` | Remove a schedule |

### Carbon-Aware

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/carbon/intensity` | Current grid carbon intensity |
| GET | `/carbon/schedule` | Optimal low-carbon time windows |

### Libvirt VM Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libvirt/domains` | List all libvirt domains |
| POST | `/libvirt/domain/start` | Start a domain |
| POST | `/libvirt/domain/shutdown` | Graceful shutdown |
| POST | `/libvirt/domain/destroy` | Force stop |
| POST | `/libvirt/domain/reboot` | Reboot |
| POST | `/libvirt/domain/pause` | Pause |
| POST | `/libvirt/domain/resume` | Resume |
| POST | `/libvirt/domain/delete` | Delete domain |
| POST | `/libvirt/domain/clone` | Clone a domain |
| POST | `/libvirt/domain/create` | Create new domain |
| POST | `/libvirt/domain/resize` | Resize vCPUs and memory |
| GET | `/libvirt/domain/xml` | Domain XML definition |
| GET | `/libvirt/domain/guest-info` | Guest agent info (OS, hostname, IPs) |
| GET | `/libvirt/domain/processes` | Running processes via guest agent |
| GET | `/libvirt/domain/security` | Security exposure analysis |
| GET | `/libvirt/domain/recommendations` | Smart recommendations |
| GET | `/libvirt/stats` | Domain resource stats |

### Hardware Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libvirt/domain/hardware` | Full hardware config (CPU, memory, disks, NICs, TPM, boot) |
| POST | `/libvirt/domain/cpu/set` | Set vCPU count and topology |
| POST | `/libvirt/domain/memory/set` | Set current and max memory |
| POST | `/libvirt/domain/disk/add` | Create and attach a disk |
| POST | `/libvirt/domain/disk/remove` | Detach a disk |
| POST | `/libvirt/domain/interface/add` | Attach a network interface |
| POST | `/libvirt/domain/interface/remove` | Detach a network interface |
| POST | `/libvirt/domain/cdrom/set` | Insert or eject CDROM ISO |
| POST | `/libvirt/domain/tpm/add` | Add TPM device (offline) |
| POST | `/libvirt/domain/boot/set` | Set boot order and firmware |

### Advanced Hardware

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libvirt/host/pci-devices` | List GPU/PCI devices for passthrough |
| POST | `/libvirt/domain/gpu/attach` | Attach GPU via PCI passthrough |
| POST | `/libvirt/domain/gpu/detach` | Detach GPU |
| GET | `/libvirt/host/numa` | NUMA topology |
| GET | `/libvirt/domain/cpu-pin` | Get CPU pinning configuration |
| POST | `/libvirt/domain/cpu-pin/set` | Set per-vCPU pinning |
| POST | `/libvirt/domain/numa/set` | Set NUMA memory placement |
| GET | `/libvirt/domain/balloon` | Memory balloon stats |
| POST | `/libvirt/domain/balloon/set` | Adjust balloon memory |
| POST | `/libvirt/domain/live-migrate` | Live migrate to another host |
| GET | `/libvirt/domain/migration-status` | Migration progress |
| GET | `/libvirt/host/sriov-devices` | List SR-IOV capable NICs |
| POST | `/libvirt/domain/sriov/attach` | Attach SR-IOV VF |

### Snapshots & Backups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libvirt/snapshots` | List snapshots |
| POST | `/libvirt/snapshot/create` | Create snapshot |
| POST | `/libvirt/snapshot/revert` | Revert to snapshot |
| POST | `/libvirt/snapshot/delete` | Delete snapshot |
| POST | `/libvirt/backup/create` | Create backup (XML + disks) |
| GET | `/libvirt/backup/list` | List backups |
| POST | `/libvirt/backup/restore` | Restore from backup |

### Storage & Volumes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libvirt/pools` | List storage pools |
| GET | `/libvirt/volumes` | List volumes |
| POST | `/libvirt/volume/create` | Create volume |
| POST | `/libvirt/volume/resize` | Resize volume |
| POST | `/libvirt/volume/delete` | Delete volume |

### KubeVirt

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/kubevirt/vms` | List KubeVirt VMs |
| GET | `/kubevirt/vmis` | List VM Instances |
| POST | `/kubevirt/vms/{ns}/{name}/start` | Start KubeVirt VM |
| POST | `/kubevirt/vms/{ns}/{name}/stop` | Stop KubeVirt VM |
| POST | `/kubevirt/vms/{ns}/{name}/restart` | Restart KubeVirt VM |
| POST | `/kubevirt/vms/{ns}/{name}/migrate` | Live migrate across nodes |
| DELETE | `/kubevirt/vms/{ns}/{name}` | Delete KubeVirt VM |
| POST | `/libvirt/domain/migrate-to-kubevirt` | Migrate libvirt VM to KubeVirt |

### Networks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libvirt/networks` | List networks |
| POST | `/libvirt/network/create` | Create network |
| POST | `/libvirt/network/delete` | Delete network |
| POST | `/libvirt/interface/attach` | Attach interface to VM |
| POST | `/libvirt/interface/detach` | Detach interface |

### Templates & ISOs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libvirt/template/list` | List VM templates |
| POST | `/libvirt/template/create` | Create template from VM |
| POST | `/libvirt/template/deploy` | Deploy VM from template |
| GET | `/libvirt/isos/list` | List available ISOs |
| POST | `/libvirt/isos/upload` | Upload ISO file |
| POST | `/libvirt/domain/attach-iso` | Attach ISO to domain |

### Console

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/console/vnc` | VNC WebSocket proxy |
| GET | `/console/serial` | Serial console |
| GET | `/console/screenshot` | VM screenshot capture |
| POST | `/console/enable-rdp` | Enable RDP access |

### Contact & Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/contact` | Submit contact form (public, no auth) |
| POST | `/admin/login` | Admin login (password: configurable) |
| GET | `/admin/messages` | List contact form submissions |
| PUT | `/admin/messages/read` | Mark message as read |
| DELETE | `/admin/messages/delete` | Delete message |

The public marketing website (**`https://zyvor.dev`**) uses a separate same-origin contact endpoint at **`POST /api/v1/contact`** (full URL: `https://zyvor.dev/api/v1/contact`). That endpoint is handled by the website container and forwards mail over SMTP; it is not part of the HyperSDK Platform daemon API described here.

## WebSocket

```
wss://your-server:5080/ws
```

Real-time updates for job progress, system metrics, and alerts.

## Rate Limiting

API requests are rate-limited per client IP. Default: 100 requests/minute. Authenticated users get higher limits.

## Error Format

All errors return JSON:

```json
{
  "error": "descriptive error message",
  "status": 400
}
```

## Pagination

List endpoints support pagination via `offset` and `limit` query parameters:

```bash
curl -sk -H "Authorization: Bearer TOKEN" \
  "https://your-server:5080/api/v1/jobs?offset=0&limit=20"
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | integer | 0 | Number of records to skip |
| `limit` | integer | 50 | Maximum number of records to return (max 200) |

**Response format:**

All paginated responses include a `pagination` object alongside the data:

```json
{
  "data": [ ... ],
  "pagination": {
    "offset": 0,
    "limit": 20,
    "total": 142,
    "has_more": true
  }
}
```

Use `has_more` to determine whether to fetch the next page. Increment `offset` by `limit` to page forward:

```bash
# Page 1
curl -sk -H "Authorization: Bearer TOKEN" \
  "https://your-server:5080/api/v1/jobs?offset=0&limit=20"

# Page 2
curl -sk -H "Authorization: Bearer TOKEN" \
  "https://your-server:5080/api/v1/jobs?offset=20&limit=20"
```

## Filtering

Most list endpoints accept query parameters for filtering results. Filters are combined with AND logic.

### Common Filters

| Parameter | Applies To | Example |
|-----------|-----------|---------|
| `status` | Jobs, VMs | `?status=running` |
| `provider` | Jobs, VMs, Providers | `?provider=vsphere` |
| `type` | Jobs | `?type=export` |
| `os` | VMs | `?os=linux` |
| `created_after` | Jobs, Schedules | `?created_after=2025-01-01T00:00:00Z` |
| `created_before` | Jobs, Schedules | `?created_before=2025-12-31T23:59:59Z` |
| `search` | All list endpoints | `?search=web-server` |
| `sort` | All list endpoints | `?sort=created_at&order=desc` |

### Example: Filter jobs by status and provider

```bash
curl -sk -H "Authorization: Bearer TOKEN" \
  "https://your-server:5080/api/v1/jobs?status=completed&provider=vsphere&sort=created_at&order=desc&limit=10"
```

### Example: Search VMs by name

```bash
curl -sk -H "Authorization: Bearer TOKEN" \
  "https://your-server:5080/api/v1/vms/list?search=prod-db&os=linux"
```

## Request and Response Examples

### POST /api/v1/jobs -- Create an Export Job

**Request:**

```bash
curl -sk -X POST https://your-server:5080/api/v1/jobs \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "export",
    "provider": "vsphere",
    "vm_name": "web-server-01",
    "format": "ova",
    "options": {
      "compress": true,
      "include_snapshots": false,
      "destination": "/var/lib/hypersdk/exports/"
    }
  }'
```

**Response (201 Created):**

```json
{
  "id": "job-a1b2c3d4",
  "type": "export",
  "status": "queued",
  "provider": "vsphere",
  "vm_name": "web-server-01",
  "format": "ova",
  "progress": 0,
  "created_at": "2025-06-15T10:30:00Z",
  "updated_at": "2025-06-15T10:30:00Z",
  "estimated_duration": "12m",
  "options": {
    "compress": true,
    "include_snapshots": false,
    "destination": "/var/lib/hypersdk/exports/"
  }
}
```

### GET /api/v1/vms/list -- List Discovered VMs

**Request:**

```bash
curl -sk -H "Authorization: Bearer TOKEN" \
  "https://your-server:5080/api/v1/vms/list?provider=vsphere&limit=5"
```

**Response (200 OK):**

```json
{
  "data": [
    {
      "name": "web-server-01",
      "provider": "vsphere",
      "os": "linux",
      "os_version": "RHEL 9.3",
      "cpu": 4,
      "memory_mb": 8192,
      "disks": [
        {
          "name": "disk-0",
          "size_gb": 100,
          "format": "vmdk",
          "thin_provisioned": true
        }
      ],
      "nics": [
        {
          "name": "nic-0",
          "type": "vmxnet3",
          "network": "VM Network",
          "mac": "00:50:56:ab:cd:ef"
        }
      ],
      "power_state": "poweredOn",
      "tools_status": "running",
      "last_seen": "2025-06-15T10:25:00Z"
    },
    {
      "name": "db-server-01",
      "provider": "vsphere",
      "os": "linux",
      "os_version": "Ubuntu 24.04",
      "cpu": 8,
      "memory_mb": 32768,
      "disks": [
        {
          "name": "disk-0",
          "size_gb": 50,
          "format": "vmdk",
          "thin_provisioned": false
        },
        {
          "name": "disk-1",
          "size_gb": 500,
          "format": "vmdk",
          "thin_provisioned": true
        }
      ],
      "nics": [
        {
          "name": "nic-0",
          "type": "vmxnet3",
          "network": "DB Network",
          "mac": "00:50:56:ab:12:34"
        }
      ],
      "power_state": "poweredOn",
      "tools_status": "running",
      "last_seen": "2025-06-15T10:25:00Z"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 5,
    "total": 87,
    "has_more": true
  }
}
```

### POST /api/v1/vms/deploy -- Deploy a Converted VM

**Request:**

```bash
curl -sk -X POST https://your-server:5080/api/v1/vms/deploy \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server-01",
    "disk_path": "/var/lib/libvirt/images/web-server-01.qcow2",
    "cpu": 4,
    "memory_mb": 8192,
    "network": "default",
    "autostart": true,
    "target": "libvirt"
  }'
```

**Response (201 Created):**

```json
{
  "name": "web-server-01",
  "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "running",
  "target": "libvirt",
  "cpu": 4,
  "memory_mb": 8192,
  "disk_path": "/var/lib/libvirt/images/web-server-01.qcow2",
  "network": "default",
  "mac": "52:54:00:ab:cd:ef",
  "autostart": true,
  "created_at": "2025-06-15T10:45:00Z",
  "vnc_port": 5901
}
```

---

## Downloads

- [API Integration Guide](pathname:///presentations/standard/15-api-integration/15-api-integration.pdf) -- authentication, endpoints, and integration patterns

---

[Schedule a Demo](/contact) to see the API in action.
