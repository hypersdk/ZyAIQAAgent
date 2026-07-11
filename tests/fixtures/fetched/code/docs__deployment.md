---
sidebar_position: 5
title: Deployment Guide
---

# Deployment Guide

Deploy HyperSDK Platform and the marketing website to your infrastructure.

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | RHEL 8+ / Fedora 38+ / Ubuntu 22.04+ | Fedora 42+ |
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Disk** | 50 GB | 200+ GB (for VM storage) |
| **Kernel** | 5.4+ with KVM support | 6.x+ |

## HyperSDK Platform Daemon

### Install from source

```bash
curl -sSL https://zyvor.dev/install | bash
```

### Start the service

```bash
sudo systemctl enable --now hypervisord
```

HyperSDK Platform serves the dashboard over HTTPS on `:5080` when TLS is enabled. For production, install a **CA-issued** certificate (see [SSL Certificate Errors](#ssl-certificate-errors) below) or set `HYPERSDK_TLS=0` and reverse-proxy with a proper TLS edge. Access the dashboard at `https://your-server:5080/web/dashboard/`.

To disable in-daemon TLS (e.g. terminate TLS only at nginx or another proxy):
```bash
# In /etc/systemd/system/hypervisord.service.d/override.conf
[Service]
Environment=HYPERSDK_TLS=0
```

### Configuration

HyperSDK Platform searches for config in order:
1. `./hypersdk.yaml`
2. `~/.config/hypersdk/config.yaml`
3. `/etc/hypersdk/config.yaml`

## Website Deployment

### One-Shot Container (recommended)

One command handles everything — build, sync, SSL, container:

```bash
REMOTE_USER=sus ./scripts/deploy.sh your-server-ip
```

This automatically:
1. Builds the website locally (`npm run build`)
2. Builds the Linux `website-server` binary locally (`go build`)
3. Syncs the static build, binary, SSL assets, and optional `contact-mailer.env` to the remote server
4. Reuses the real certificate chain and private key already installed on the server (must match the public hostname, e.g. `zyvor.dev`)
5. Builds and starts a podman container on ports `80` and `443`

Options:
```bash
REMOTE_USER=sus ./scripts/deploy.sh your-server-ip --skip-build  # Use existing build/
REMOTE_USER=sus ./scripts/deploy.sh your-server-ip --bare        # Bare nginx (no container)
./scripts/deploy.sh --help                                        # All options
```

### K3s cluster (`deploy-k8s.sh`)

Run the marketing site **inside K3s** on a node: the script builds locally, builds a Podman image on the host, **imports it into K3s containerd** (no image registry), applies the manifests, and mounts TLS from a Kubernetes secret.

**On the K3s node you need:** K3s with `k3s kubectl` (the script uses `sudo /usr/local/bin/k3s kubectl`), **Podman** to build the image, a full **TLS chain** + matching key (same rules as other deploy paths: `ssl/fullchain.crt` locally, or cert/key under `/etc/ssl/hypersdk/` on the server), and optional `contact-mailer.env` for SMTP.

**Deploy**

```bash
./scripts/deploy-k8s.sh user@K3S_NODE_IP
# or
make deploy-k8s SERVER=K3S_NODE_IP REMOTE_USER=user
```

Useful options and environment (see `./scripts/deploy-k8s.sh --help`):

```bash
./scripts/deploy-k8s.sh user@host --skip-build
REBUILD_FULLCHAIN=1 ./scripts/deploy-k8s.sh user@host
TLS_VERIFY_SNI=zyvor.dev ./scripts/deploy-k8s.sh user@NODE_IP   # SNI when testing over the node IP
```

**What the script does (summary):** `npm run build` → cross-compile `website-server` (linux/amd64) → rsync `build/`, binary, and `k8s/` to the node → ensure `ssl/fullchain.crt` (full Sectigo chain) and key on the node → `podman build` + `k3s ctr images import` → create/update `Secret` `website-tls` → `kubectl apply -k` (namespace `hypersdk`, `Deployment` + `LoadBalancer` `Service`) → rollout restart → optional OpenSSL check to `:443` using `TLS_VERIFY_SNI`.

**Important:** Running only `kubectl apply -k k8s/` from your laptop **does not** deploy a working site by itself — the cluster must already have the image `localhost/hypersdk-website:latest` imported and TLS secrets created; use **`deploy-k8s.sh`** for the full flow.

**Architecture:** `website-server` terminates **HTTPS inside the pod** (ports 80/443). The `Service` is type **LoadBalancer**; on K3s, **klipper-lb** binds the node’s 80/443 to the pod. There is **no Ingress** in the default `kustomization` (see `k8s/README.md`).

**TLS:** The deployment uses **one** TLS secret; the PEM must match the public hostname (**`zyvor.dev`** / **`www.zyvor.dev`**) and **`dashboard.zyvor.dev`** if you terminate those on the same pod.

#### Disable Traefik on K3s (usually required)

K3s ships **Traefik**, which often binds **:80** and **:443** with its own default certificate. That prevents the website `LoadBalancer` from owning those ports and serving your CA chain.

On the **K3s server as root**, run once:

```bash
sudo bash scripts/disable-k3s-traefik.sh
```

Or over SSH:

```bash
ssh sus@your-server 'sudo bash -s' < scripts/disable-k3s-traefik.sh
```

Re-run `./scripts/deploy-k8s.sh user@host` after K3s restarts. New installs can skip Traefik with `INSTALL_K3S_EXEC='--disable traefik'` when installing K3s.

### Website Contact Mail

The marketing website contact form posts to the same origin:

```text
POST /api/v1/contact
```

In container mode that request is handled by the `website-server` binary, which sends mail over SMTP using `contact-mailer.env`.

Create the SMTP file from the template:

```bash
cp contact-mailer.env.example contact-mailer.env
```

Required values:

```env
SMTP_HOST=...
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_FROM=info@zyvor.dev
CONTACT_TO=info@zyvor.dev
SMTP_USE_TLS=true
```

Verify live contact wiring:

```bash
curl -k https://your-server/healthz
curl -k -X POST https://your-server/api/v1/contact \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test","email":"you@example.com","company":"Example","message":"hello"}'
```

### Managing the Website Container

Use podman directly on the remote server:

```bash
ssh sus@your-server-ip "sudo podman ps --filter name=hypersdk-website"
ssh sus@your-server-ip "sudo podman restart hypersdk-website"
ssh sus@your-server-ip "sudo podman logs hypersdk-website --tail 50"
```

### Makefile shortcuts

```bash
make deploy SERVER=your-server-ip           # Container (default)
make deploy-bare SERVER=your-server-ip      # Bare nginx
make deploy-k8s SERVER=your-server-ip       # K3s (see above)
make deploy-all SERVER=your-server-ip       # Website + HyperSDK Platform + hyper2kvm
```

### Build customization

Override the site URL and dashboard link at build time:

```bash
SITE_URL=https://zyvor.dev \
DASHBOARD_URL=https://dashboard.example.com/ \
npm run build
```

## Firewall

Open these ports on your server:

| Port | Service |
|------|---------|
| 80 | Website (HTTP, redirects to HTTPS) |
| 443 | Website (HTTPS, Sectigo SSL, served by `website-server`) |
| 5080 | HyperSDK Platform dashboard (HTTPS, auto cert) |
| 5070 | hyper2kvm dashboard (HTTPS, auto cert) |

## Verify

```bash
# Website
curl -s -o /dev/null -w "%{http_code}" http://your-server/

# Website health
curl -sk https://your-server/healthz

# K3s (on the node)
sudo k3s kubectl -n hypersdk get pods,svc
sudo k3s kubectl -n hypersdk rollout status deployment/hypersdk-website

# HyperSDK Platform API
curl -sk https://your-server:5080/api/v1/health
```

## Troubleshooting

### Port 5080 Already in Use

**Symptom:** `hypervisord` fails to start with "address already in use" on port 5080.

**Fix:**

1. Find the process occupying the port:
   ```bash
   sudo ss -tlnp | grep 5080
   ```
2. Stop the conflicting service, or configure HyperSDK Platform to use a different port:
   ```yaml
   # /etc/hypersdk/config.yaml
   server:
     port: 5090
   ```
3. Restart the daemon:
   ```bash
   sudo systemctl restart hypervisord
   ```

### SSL Certificate Errors

**Symptom:** Browser shows `ERR_CERT_AUTHORITY_INVALID` or API clients fail with "certificate verify failed".

**Fix:**

- **Production website (zyvor.dev):** Deploy `ssl/fullchain.crt` (or your CA bundle) and the matching private key from your CA.
- **HyperSDK Platform dashboard on :5080:** Install a CA-issued cert and key (or disable TLS and use a reverse proxy with a trusted cert):
  ```bash
  sudo mkdir -p /etc/hypersdk/tls
  sudo cp fullchain.pem /etc/hypersdk/tls/cert.pem
  sudo cp privkey.pem /etc/hypersdk/tls/key.pem
  ```
  Then set the environment variables:
  ```ini
  # In /etc/systemd/system/hypervisord.service.d/override.conf
  [Service]
  Environment=HYPERSDK_TLS_CERT=/etc/hypersdk/tls/cert.pem
  Environment=HYPERSDK_TLS_KEY=/etc/hypersdk/tls/key.pem
  ```
  Reload and restart:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl restart hypervisord
  ```

### Permission Denied on /var/lib/hypersdk

**Symptom:** The daemon logs `permission denied` when writing to `/var/lib/hypersdk` or the upload directory.

**Fix:**

1. Ensure the directory exists and is owned by the correct user:
   ```bash
   sudo mkdir -p /var/lib/hypersdk
   sudo chown hypersdk:hypersdk /var/lib/hypersdk
   sudo chmod 750 /var/lib/hypersdk
   ```
2. If running as root, check that SELinux is not blocking access:
   ```bash
   sudo ausearch -m avc -ts recent
   sudo setsebool -P httpd_sys_rw_content_t 1
   ```
3. Verify the `hypervisord` systemd unit is not using `ProtectSystem=strict` without the proper `ReadWritePaths=` override.

### Dashboard Not Loading

**Symptom:** Navigating to `https://your-server:5080/web/dashboard/` shows a blank page, a 502 error, or a CORS error in the browser console.

**Fix:**

1. **Check that hypervisord is running:**
   ```bash
   sudo systemctl status hypervisord
   journalctl -u hypervisord --no-pager -n 50
   ```
2. **If using an external reverse proxy**, ensure the proxy configuration passes WebSocket upgrades:
   ```nginx
   location /ws {
       proxy_pass https://127.0.0.1:5080;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```
3. **CORS errors:** If the dashboard and API are on different origins, set the allowed origin in the config:
   ```yaml
   # /etc/hypersdk/config.yaml
   server:
     cors_origins:
       - "https://dashboard.example.com"
   ```
4. **Clear browser cache** and hard-reload (`Ctrl+Shift+R`) to pick up updated assets after an upgrade.

### API Returning 401 Unauthorized

**Symptom:** API requests that previously worked now return `{"error": "unauthorized", "status": 401}`.

**Fix:**

1. **JWT token expired:** The default session expiry is 30 minutes. Re-authenticate to obtain a fresh token:
   ```bash
   curl -sk -X POST https://your-server:5080/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "secret"}'
   ```
2. **RBAC role changed:** If an administrator modified your role while you were logged in, the existing token may lack the required permissions. Log out and log back in.
3. **API key revoked:** If using an API key for automation, verify the key has not been rotated or disabled. Check active keys at `GET /api/v1/auth/keys`.
4. **Clock skew:** JWT validation requires the server and client clocks to be in sync. Ensure NTP is configured on both ends.

---

## Downloads

- [Quickstart & POC Guide](pathname:///presentations/standard/10-quickstart-poc/10-quickstart-poc.pdf) -- step-by-step deployment for proof of concept
- [Technical Architecture](pathname:///presentations/standard/02-technical-architecture/02-technical-architecture.pdf) -- architecture diagrams and deployment topology

---

[Contact us](/contact) if you need help with your deployment.
