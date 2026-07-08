# Administrator creates a VM

**As an** administrator
**I want to** provision a new Ubuntu VM
**So that** I can run workloads on Zyvor infrastructure

## Acceptance Criteria

1. Navigate to the VM management page at `/vm`
2. Click "Create VM" button
3. Enter VM name: `ubuntu-test`
4. Click "Provision"
5. VM status shows "Running" within 60 seconds

## Environment

- Requires staging environment (`ZYVOR_STAGING_URL`)
- Requires authenticated admin user

## Tags

vm, provisioning, smoke
