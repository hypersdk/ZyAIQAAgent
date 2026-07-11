---
sidebar_position: 9
title: Security
---

# Security

HyperSDK Platform is built with enterprise security requirements in mind.

## Authentication

- **PAM-based login** — Uses system accounts (Linux PAM) for authentication
- **Session tokens** — JWT-based session management with configurable expiry
- **Session storage** — Auth state stored in sessionStorage (cleared on browser close)

## Authorization

- **Role-Based Access Control (RBAC)** — Admin, Operator, and Viewer roles
- **Per-resource permissions** — Control access to providers, jobs, and system settings
- **API key support** — Service accounts for CI/CD integration

## Network Security

### TLS

HyperSDK Platform can serve the dashboard and API over HTTPS. For production, install **CA-issued** certificates via `HYPERSDK_TLS_CERT` and `HYPERSDK_TLS_KEY` (or disable in-daemon TLS and terminate at a reverse proxy with a public certificate). **Do not** deploy or rely on locally generated placeholder certificates for public endpoints.

- HTTP/2 may be disabled in some builds to ensure WebSocket compatibility

### Website Security Headers

The website edge server serves with these headers:

| Header | Value |
|--------|-------|
| `X-Frame-Options` | SAMEORIGIN |
| `X-Content-Type-Options` | nosniff |
| `Referrer-Policy` | strict-origin-when-cross-origin |
| `Strict-Transport-Security` | max-age=31536000; includeSubDomains |
| `Content-Security-Policy` | default-src 'self'; … `frame-src` allows YouTube embeds; `img-src` includes `i.ytimg.com` for video thumbnails |

### Rate Limiting

API requests are rate-limited per client IP to prevent abuse.

## Audit Logging

Every API request is logged with:
- Timestamp
- User identity
- Action performed
- Resource affected
- Source IP address
- Request ID for correlation

## Input Validation

- **Path traversal protection** — All file paths validated against directory traversal (`..`)
- **Request size limits** — Configurable maximum request body size
- **Symlink resolution** — File operations resolve symlinks before access checks

## Secrets Management

- Provider credentials encrypted at rest
- Passwords never logged or returned in API responses
- Credentials excluded from export manifests

## Compliance

| Standard | Status |
|----------|--------|
| SOC2 | Ready |
| GDPR | Compliant data handling |
| HIPAA | Audit logging, access controls |
| FedRAMP | Air-gap deployment supported |

## Session Management

### Session Timeout

Sessions expire after **30 minutes** of inactivity by default. The timeout is configurable in `hypersdk.yaml`:

```yaml
auth:
  session_timeout: 30m    # default
  max_session_lifetime: 8h # absolute maximum, regardless of activity
```

When a session expires the dashboard redirects the user to the login screen. API clients receive a `401 Unauthorized` response and must re-authenticate.

### Concurrent Sessions

Each user can have up to **5 concurrent sessions** by default. Older sessions are revoked automatically when the limit is exceeded. Administrators can adjust this limit per role.

## API Key Rotation

API keys are used for service accounts and CI/CD integrations. Best practices:

- **Rotate every 90 days.** Set a calendar reminder or use the built-in schedule:
  ```yaml
  auth:
    api_key_max_age: 90d
    api_key_rotation_warning: 14d  # warn 14 days before expiry
  ```
- **Generate a new key before revoking the old one** to avoid downtime:
  ```bash
  # Create a new key
  curl -sk -X POST https://your-server:5080/api/v1/auth/keys \
    -H "Authorization: Bearer ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name": "ci-pipeline", "role": "operator", "expires_in": "90d"}'

  # Update your CI/CD pipeline with the new key, then revoke the old one
  curl -sk -X DELETE https://your-server:5080/api/v1/auth/keys/OLD_KEY_ID \
    -H "Authorization: Bearer ADMIN_TOKEN"
  ```
- **Never embed API keys in source code.** Use environment variables or a secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.).
- **Scope keys to the minimum required role.** Prefer `operator` or `viewer` over `admin` for automation.

## Network Segmentation Recommendations

For production deployments, isolate HyperSDK Platform components on separate network segments:

| Segment | Components | Access |
|---------|-----------|--------|
| **Management** | HyperSDK Platform daemon (port 5080), hyper2kvm (port 5070) | Administrators only |
| **VM Network** | KVM/libvirt bridges, guest traffic | VMs and required services |
| **Storage** | NFS, iSCSI, Ceph storage backends | HyperSDK Platform daemon and libvirt only |
| **Public** | Website (ports 80/443) | End users |

### Firewall Rules

In addition to opening the required ports, restrict source IPs:

```bash
# Allow management access only from admin VLAN
firewall-cmd --zone=management --add-rich-rule='rule family="ipv4" source address="10.0.1.0/24" port port="5080" protocol="tcp" accept'

# Block all other access to management ports
firewall-cmd --zone=public --remove-port=5080/tcp
```

### Air-Gapped Deployments

HyperSDK Platform supports fully air-gapped installations. In this mode:

- All dependencies are bundled in the release tarball.
- No outbound internet access is required.
- Carbon-aware scheduling uses manually provided grid intensity data.
- VirtIO driver ISOs must be placed on disk manually.

## Backup Encryption

VM disk backups created by the Backup Scheduler can be encrypted at rest:

```yaml
backup:
  encryption:
    enabled: true
    algorithm: aes-256-gcm
    key_source: file        # or "vault" for HashiCorp Vault
    key_path: /etc/hypersdk/backup.key
```

### Generating an Encryption Key

```bash
openssl rand -base64 32 | sudo tee /etc/hypersdk/backup.key
sudo chmod 400 /etc/hypersdk/backup.key
sudo chown hypersdk:hypersdk /etc/hypersdk/backup.key
```

### Restoring Encrypted Backups

Encrypted backups require the same key that was used during creation. Store a copy of the key in a secure, off-site location (e.g., a hardware security module or a sealed envelope in a safe).

```bash
hyper2kvm restore --input backup-2025-01-15.enc.qcow2 \
  --key /etc/hypersdk/backup.key \
  --output /var/lib/libvirt/images/
```

## Confidential computing (Aether + Ragnarok)

For workloads that require **hardware-rooted trust**, the suite provides a confidential fabric across **[Aether](/docs/aether)** and **[Ragnarok](/docs/ragnarok)**:

| Control | Description |
|---------|-------------|
| **TEE types** | AMD SEV-SNP and Intel TDX on KubeVirt; Kata/CoCo pods via RuntimeClasses |
| **Attestation** | Per-workload verify, composite trust scores, and Explain mode for failures |
| **Measured images** | cosign-signed qcow2 catalog with deploy-time digest verification |
| **Attest-gated secrets** | Secrets remain pending until attestation passes; auto-revoke on failure |
| **Confidential migration** | `confidential-blue-green` with re-attestation before cutover on TEE nodes |
| **Sovereign mode** | BYOK signing, offline attestation bundles, and region lock for air-gapped estates |
| **Workload identity** | Optional SPIRE/SPIFFE integration for east-west trust binding |
| **Network policy** | Auto CiliumNetworkPolicy generation and PacketWolf verify annotations |

Full install, spec examples, and cluster prep: **[Confidential computing fabric](/docs/confidential-fabric)**.

GuestKit **`doctor`** and **`migrate-plan`** outputs feed confidential preflight evidence before TEE boot — inspect disks offline without live guest access.

---

## Downloads

- [Security & Compliance](pathname:///presentations/standard/07-security-compliance/07-security-compliance.pdf) -- RBAC, audit logging, HIPAA/FedRAMP/SOC2 compliance details

---

[Contact us](/contact) to discuss your security requirements.
