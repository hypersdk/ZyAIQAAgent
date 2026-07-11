---
sidebar_position: 8
title: Migration Guide
---

# VM Migration Guide

Step-by-step guide to migrating virtual machines with HyperSDK Platform.

## VMware to KVM

The most common migration path. Typical timeline: **1-2 days for 100 VMs**.

### 1. Connect to vCenter

From the dashboard, go to **Providers** and add your vSphere connection:
- vCenter URL
- Username and password
- Datacenter (optional — auto-discovered if omitted)

Or via API:
```bash
curl -sk -X POST https://your-server:5080/api/v1/providers/connect \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vsphere",
    "url": "vcenter.example.com",
    "username": "admin@vsphere.local",
    "password": "secret"
  }'
```

### 2. Browse and select VMs

The dashboard shows all discovered VMs with CPU, memory, disk, and OS details. Select VMs individually or use batch select.

### 3. Export

Export creates a manifest-tracked job that downloads the VM disk(s) in OVF/OVA format:

```bash
curl -sk -X POST https://your-server:5080/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "export",
    "provider": "vsphere",
    "vm_name": "web-server-01",
    "format": "ova"
  }'
```

### 4. Convert with hyper2kvm

hyper2kvm handles the conversion pipeline automatically:

```bash
hyper2kvm convert --input web-server-01.ova --output /var/lib/libvirt/images/
```

This runs the 7-stage pipeline:
1. **Fetch** — Acquire source VM disks
2. **Flatten** — Collapse snapshot chains into single files
3. **Inspect** — Detect OS, firmware, bootloader, partition layout
4. **Plan** — Determine required fixes based on guest OS
5. **Fix** — Apply offline fixes (fstab, initramfs, GRUB, network, VirtIO injection)
6. **Convert** — Transform disk format (VMDK to QCOW2)
7. **Validate** — Boot test verification

### 5. Deploy

The converted VM is registered with libvirt and ready to start:

```bash
virsh start web-server-01
```

Or deploy to KubeVirt:
```bash
kubectl apply -f web-server-01-kubevirt.yaml
```

## Cloud to On-Prem (Repatriation)

### AWS EC2 to KVM

1. Connect AWS credentials (Access Key + Secret Key + Region)
2. Browse EC2 instances
3. Export AMI as VMDK/VHD
4. Convert with hyper2kvm
5. Deploy locally

### Azure to KVM

1. Connect Azure credentials (Tenant ID + Client ID + Secret)
2. Browse VMs
3. Export managed disk as VHD
4. Convert and deploy

## Code & Config Migration

Beyond VM disks, HyperSDK Platform can translate your application stack to Kubernetes:

| Source | Target |
|--------|--------|
| Docker Compose | Kubernetes Deployments, Services, PVCs |
| systemd services | Containerized workloads or init containers |
| VM-based workloads | KubeVirt VirtualMachine resources |

Environment variables, volumes, networking, and dependencies are preserved automatically.

## Windows VMs

Windows migrations are auto-detected and handled:

- VirtIO driver injection (viostor, netkvm, balloon, qxl)
- Registry modifications for boot controller
- Supported: Windows Server 2016/2019/2022, Windows 10/11

## Linux VMs

- fstab rewritten to UUID/LABEL references
- initramfs regenerated with virtio modules
- GRUB updated for KVM boot parameters
- VMware tools removed automatically
- Supported: RHEL 7-10, Ubuntu 20-24, Debian 11-13, SUSE, Fedora

## Post-Migration Checklist

- [ ] VM boots successfully on first try
- [ ] Network connectivity verified
- [ ] All services running
- [ ] Storage mounted correctly
- [ ] Performance baseline established
- [ ] Backup configured on new platform
- [ ] DNS/load balancer updated
- [ ] Old VM decommissioned

## Troubleshooting

### VM Won't Boot After Conversion

**Symptom:** The converted VM fails to start or drops into an emergency shell / BSOD.

**Cause:** Missing VirtIO drivers. The source VM was using VMware paravirtual (PVSCSI) or IDE controllers that do not exist in KVM.

**Fix:** Re-run the conversion with forced VirtIO driver injection:

```bash
hyper2kvm convert --input web-server-01.ova \
  --output /var/lib/libvirt/images/ \
  --force-virtio
```

For Windows VMs, ensure the correct VirtIO ISO is available. hyper2kvm downloads the latest stable ISO automatically, but air-gapped environments must place it manually at `/var/lib/hyper2kvm/drivers/virtio-win.iso`.

### Network Not Working Post-Migration

**Symptom:** The VM boots but has no network connectivity. `ip link` shows a different interface name (e.g., `ens3` instead of `ens192`).

**Cause:** Interface names change when moving from VMware virtual NICs (vmxnet3) to VirtIO-net. Network configuration files may reference the old name.

**Fix:**

- **RHEL / CentOS / Fedora:** Edit `/etc/sysconfig/network-scripts/ifcfg-*` or the NetworkManager connection file in `/etc/NetworkManager/system-connections/` and update the `DEVICE=` or `interface-name=` field.
- **Ubuntu / Debian (netplan):** Edit `/etc/netplan/*.yaml` and replace the old interface name with the new one, then run `sudo netplan apply`.
- **Alternatively**, let hyper2kvm handle it by adding the `--fix-network` flag during conversion.

### GRUB Not Found

**Symptom:** The VM fails to boot with "error: no such device" or "GRUB rescue" prompt.

**Cause:** The bootloader configuration references the old disk UUID or device path from the source hypervisor.

**Fix:** Re-run hyper2kvm with bootloader repair:

```bash
hyper2kvm convert --input web-server-01.ova \
  --output /var/lib/libvirt/images/ \
  --fix-bootloader
```

This mounts the disk image, chroots into the guest, and regenerates GRUB configuration with correct UUIDs.

### Disk Space Issues During Conversion

**Symptom:** Conversion fails with "No space left on device" or similar I/O error.

**Cause:** The conversion process needs approximately **2x the source disk size** in free space -- one copy for the source image and one for the converted output.

**Fix:**

1. Free up space on the target volume or point `--output` to a larger filesystem.
2. Use thin-provisioned QCOW2 output to reduce actual space consumption:
   ```bash
   hyper2kvm convert --input vm.ova --output /data/ --format qcow2 --preallocation off
   ```
3. For very large disks, consider streaming mode which avoids writing the intermediate flat image:
   ```bash
   hyper2kvm convert --input vm.ova --output /data/ --stream
   ```

### Windows Activation Issues

**Symptom:** Windows reports "This copy of Windows is not genuine" or activation fails after migration.

**Cause:** Hardware changes (virtual NIC, disk controller, BIOS/UEFI firmware) can trigger Windows re-activation. The behavior depends on the license type.

**Fix:**

- **KMS (Volume licensing):** The VM should re-activate automatically once it can reach the KMS server. Verify connectivity: `slmgr /ato`.
- **MAK (Multiple Activation Key):** You may need to re-enter the product key. Use `slmgr /ipk XXXXX-XXXXX-XXXXX-XXXXX-XXXXX` followed by `slmgr /ato`.
- **OEM licenses:** These are tied to original hardware and cannot be transferred. Contact Microsoft for a new license.

### Slow Conversion Speed

**Symptom:** The conversion takes much longer than expected (e.g., hours for a 100 GB disk).

**Cause:** I/O bottlenecks on the source or target storage, or single-threaded processing of large disks.

**Fix:**

1. Check I/O utilization with `iostat -x 1` during conversion. If `%util` is near 100%, the storage is the bottleneck.
2. Use the parallel flag to process multiple disks concurrently:
   ```bash
   hyper2kvm convert --input vm.ova --output /data/ --parallel 4
   ```
3. Place the source and target on different physical disks or storage systems to avoid I/O contention.
4. Use NVMe or SSD storage for the conversion workspace.
5. For network-attached storage, verify that the link speed and MTU are adequate.

---

## Downloads

- [Multi-Cloud Migration](pathname:///presentations/standard/03-multi-cloud-migration/03-multi-cloud-migration.pdf) -- cross-provider migration strategies
- [Migration Readiness Assessment](pathname:///presentations/standard/24-migration-readiness/24-migration-readiness.pdf) -- pre-migration checklist and planning
- [vSphere Deep Dive](pathname:///presentations/standard/11-vsphere-deep-dive/11-vsphere-deep-dive.pdf) -- VMware-specific migration walkthrough
- [Hyper-V Migration](pathname:///presentations/standard/13-hyperv-migration/13-hyperv-migration.pdf) -- Microsoft Hyper-V migration guide
- [Performance Optimization](pathname:///presentations/standard/18-performance-optimization/18-performance-optimization.pdf) -- tuning for large-scale migrations

---

[Download the full Migration Checklist](/checklist) or [schedule a demo](/contact).
