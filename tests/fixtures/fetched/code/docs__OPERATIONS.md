# Operations

Runbook for the marketing site (`website-server` + Docusaurus `build/`).

## Health and status

| Endpoint | Purpose |
|----------|---------|
| `GET /healthz` | Process liveness (used by deploy probes) |
| `GET /api/v1/health` | JSON health including `smtpConfigured` |
| `GET /api/v1/status` | Public status: probes website `/healthz` and `DASHBOARD_UPSTREAM` |

The `/status` page polls `/api/v1/status` every 30s. Service rows are live probes; uptime history bars remain illustrative.

Optional env on `website-server` (see `contact-mailer.env.crm.example`):

| Variable | Purpose |
|----------|---------|
| `STATUS_UPTIME_LABEL` | Shown in uptime card (e.g. `99.9%`) |
| `STATUS_INCIDENTS_JSON` | JSON array of `{date, title, status, duration?, description?}` — replaces default incident list when set |

## Data directories

Default `DATA_DIR=/var/lib/website-server`:

- `zyvor-store.bolt` — **primary** embedded analytics store (BoltDB; survives redeploys on the mounted volume)
- `analytics.json` — JSON export of aggregates (human-readable backup; auto-written with each persist)
- `visit-log.jsonl` — per-visit IP, country, city, region, ASN, org, source, path (admin drill-down; default 90-day retention)
- `contact-submissions/*.json` — contact form payloads
- `read-status.json` — admin read/unread flags
- `backups/pre-deploy-*` — automatic snapshots before each container deploy (last 10 kept)
- `GeoLite2-Country.mmdb` — optional; enables country resolution when `GEOIP_COUNTRY_DB_PATH` is set

Podman deploy bind-mounts **`/var/lib/hypersdk-website`** on the host → `/var/lib/website-server` in the container (same path as K3s). The deploy workdir `~/.deployments/hypersdk-website/` holds build artifacts and TLS only; a `data` symlink points at the real volume. **Do not delete `/var/lib/hypersdk-website`** — removing only `.deployments` is safe.

### Backup

```bash
# On the server (podman host path)
sudo tar czf hypersdk-website-data-$(date +%Y%m%d).tar.gz \
  /var/lib/hypersdk-website/zyvor-store.bolt \
  /var/lib/hypersdk-website/analytics.json \
  /var/lib/hypersdk-website/visit-log.jsonl \
  /var/lib/hypersdk-website/youtube-cache.json \
  /var/lib/hypersdk-website/youtube-oauth.json \
  /var/lib/hypersdk-website/contact-submissions \
  /var/lib/hypersdk-website/read-status.json
```

`./scripts/deploy-container.sh` runs `scripts/preserve-website-data.sh` before each container restart (copies into `data/backups/pre-deploy-<timestamp>/`, keeps the last 10). Restore from a backup folder or tar before restarting `website-server` if needed. On startup, the server loads Bolt first, then `analytics.json`, then rebuilds from `visit-log.jsonl` if aggregates are missing.

**Restore after accidental data loss** (on the server):

```bash
cd ~/.deployments/hypersdk-website
ls -lt /var/lib/hypersdk-website/backups/pre-deploy-* | head
bash scripts/preserve-website-data.sh /var/lib/hypersdk-website restore pre-deploy-YYYYMMDDHHMMSS
./scripts/webserver.sh <host> restart   # or redeploy — container reloads Bolt + visit log
```

If the volume was empty on first deploy (no backups), older traffic cannot be recovered. Analytics never lives in git; it persists only on `/var/lib/hypersdk-website`.

## Contact pipeline

1. `POST /api/v1/contact` validates and rate-limits per IP.
2. JSON saved under `CONTACT_STORAGE_DIR` (or `DATA_DIR/contact-submissions`).
3. Optional SMTP to routed recipient (`CONTACT_TO_*`, `CONTACT_ROUTING_JSON`).
4. Optional `CRM_WEBHOOK_URL` / `CRM_SLACK_WEBHOOK_URL` (async).
5. Optional `CONTACT_AUTO_REPLY=true` email to submitter.

See `contact-mailer.env.example` for all variables.

## Admin

Set `ADMIN_PASSWORD` in `contact-mailer.env` (synced on deploy). UI: `/admin`. API: `/api/v1/admin/*` with `X-Admin-Token` after `POST /api/v1/admin/login`.

On **successful admin login**, website-server sends an optional SMTP alert to **`general@zyvor.dev`** (override with `ADMIN_LOGIN_ALERT_TO`; set `off`/`false` to disable) with the login IP, country, state/region, city, timezone, and ASN/org when GeoLite2 is configured. Requires the same `SMTP_*` vars as the contact form.

Dashboard includes `leadsByDay` (14 days), `funnel` (high-intent leads vs month page views), **traffic sources**, **visitors by country**, **top cities/states**, **recent visits** (IP + location), UTM campaigns/mediums, custom events, and CSV export.

### Analytics tracking

- **Server-side:** every HTML page GET records path, referrer/UTM source, campaign, medium, and country (when geo DB or `CF-IPCountry` is available).
- **Client-side:** `POST /api/v1/track` (same origin) records SPA route changes after cookie consent; custom marketing events (CTA clicks, etc.) increment event counters without double-counting page views.
- **Visit log:** each page view appends a line to `visit-log.jsonl` (IP, country, city, region, timezone, ASN, org, source, path). Retention defaults to **90 days** (`VISIT_LOG_RETENTION_DAYS`) with optional `VISIT_LOG_MAX_LINES` cap. Admin Analytics tab shows a world map, city/org drill-down, and IP log.
- **Zyvor Pulse:** when `DATABASE_URL` is set (PostgreSQL or SQL Server), visitor profiles, sessions, events (with properties JSON), page views with **country/city/region/ASN**, and intent scores are stored in SQL. Admin **Pulse** tab shows hot leads and per-visitor intelligence. Grafana dashboard: `grafana/dashboards/zyvor-pulse.json` (K8s: `k8s/postgres.yaml` or `k8s/pulse-sqlserver.yaml`, `k8s/grafana-deployment.yaml`).
- Data persists on the mounted data volume — survives container redeploys.

Admin API:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/admin/analytics?days=30` | Full analytics (`days`: 7, 14, 30, or 0 for all-time) |
| `GET /api/v1/admin/analytics/visits?days=30&country=IN&city=Frankfurt&region=California&org=microsoft&ip=203.0&limit=100` | Paginated visit log with geo + network fields; `ip` is prefix match |
| `GET /api/v1/admin/analytics/export?days=30&format=csv` | CSV export (includes visit rows with IP, location, visitor_key) |
| `GET /api/v1/admin/pulse/lookup?visitor_key=` | Resolve Pulse visitor id for visit-log → profile deep link |
| `GET /api/v1/admin/pulse/summary?days=30` | Pulse KPIs, funnel, top orgs/products (requires PostgreSQL or SQL Server) |
| `GET /api/v1/admin/pulse/visitors?days=30&status=hot&country=US` | Ranked visitor list with intent scores and geo filter |
| `GET /api/v1/admin/pulse/visitors/{id}` | Single visitor profile (pages, events, interests) |
| `GET /api/v1/admin/pulse/metrics` | Prometheus exposition for Grafana (admin token required) |

### GeoLite2 databases (optional)

Traffic source counts work immediately. Geo enrichment uses MaxMind GeoLite2 (Country, City, ASN) when available.

**Automatic (recommended on deploy):** add to `contact-mailer.env`:

```
MAXMIND_ACCOUNT_ID=your_account_id
MAXMIND_LICENSE_KEY=your_license_key
GEOIP_COUNTRY_DB_PATH=/var/lib/website-server/GeoLite2-Country.mmdb
GEOIP_CITY_DB_PATH=/var/lib/website-server/GeoLite2-City.mmdb
GEOIP_ASN_DB_PATH=/var/lib/website-server/GeoLite2-ASN.mmdb
```

Deploy scripts run [`scripts/update-geolite2.sh`](../scripts/update-geolite2.sh) on the data volume (skips if the DB is newer than 30 days). Podman deploy also passes geo paths when files exist.

**Manual:** download GeoLite2 Country, City, and ASN `.mmdb` files from [MaxMind](https://www.maxmind.com/en/geolite2/signup) and place on `/var/lib/hypersdk-website/` (podman and K3s).

Until databases are present, countries may accumulate as `unknown`. If the site is behind Cloudflare, `CF-IPCountry` is used automatically when the header is present.

### Zyvor Pulse (PostgreSQL or SQL Server, optional)

Hybrid storage: `zyvor-store.bolt` (embedded BoltDB on `DATA_DIR`) keeps durable aggregates across redeploys; `analytics.json` is a parallel export; `visit-log.jsonl` keeps a rolling IP/country audit log. **SQL** stores full visitor intelligence (country, city, org, intent scores) when configured.

**PostgreSQL** (K3s: `k8s/postgres.yaml`):

```
DATABASE_URL=postgres://pulse:password@pulse-postgres:5432/zyvor_pulse?sslmode=disable
PULSE_IP_HASH_SALT=long-random-secret
```

**SQL Server** (Podman on deploy host — [`scripts/run-pulse-sqlserver.sh`](../scripts/run-pulse-sqlserver.sh); K3s: `k8s/pulse-sqlserver.yaml`):

```
DATABASE_DRIVER=sqlserver
DATABASE_URL=sqlserver://sa:YourStrong!Pass@127.0.0.1:1433?database=zyvor_pulse&encrypt=disable
PULSE_IP_HASH_SALT=long-random-secret
PULSE_IMPORT_VISIT_LOG=1
```

`PULSE_IMPORT_VISIT_LOG=1` backfills existing `visit-log.jsonl` rows into Pulse on first startup when `page_views` is empty (disable after migration).

K3s: create secret `pulse-postgres` or `pulse-sqlserver` with `database_url` and `ip_hash_salt`. Migrations run automatically on website-server startup (`cmd/website-server/migrations/001_pulse.sql` or `001_pulse_mssql.sql`).

Client tracking (consent-gated): first-party `zyvor_vid` / `zyvor_sid` cookies, fingerprint fields, time-on-page, and `X-Zyvor-Track: 1` header to avoid double-counting server GET pageviews after consent.

### YouTube public stats (optional)

Public channel metrics are served from `{DATA_DIR}/youtube-cache.json` — refreshed server-side via YouTube Data API v3 (never call Google from the browser).

**Setup** in `contact-mailer.env`:

```
YOUTUBE_API_KEY=your_google_api_key
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxxxxxxxx
YOUTUBE_CACHE_TTL_HOURS=6
YOUTUBE_FEATURED_VIDEO_IDS=9sAl6uhHFQI,ZYCz6HN7bXE
YOUTUBE_FEATURED_PLAYLIST_IDS=PLxxx,PLyyy
```

Enable **YouTube Data API v3** on the Google Cloud project. Restrict the API key to YouTube Data API + your server IP if possible.

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/youtube/public` | Cached subscribers, views, latest/top/featured/migration videos |

Public page: `/analytics/youtube`. Include `youtube-cache.json` and `youtube-oauth.json` in DATA_DIR backups.

**Private analytics (OAuth):** enable YouTube Analytics API on the Google Cloud project. In `/admin` → **YouTube** tab, click **Connect YouTube Analytics** (one-time channel-owner consent). Tokens stored in `{DATA_DIR}/youtube-oauth.json`. Admin API:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/admin/youtube/status` | OAuth + public API configuration |
| `GET /api/v1/admin/youtube/oauth/start` | Returns Google consent URL (admin token required) |
| `GET /api/v1/admin/youtube/analytics?days=30` | Watch time, daily views, traffic sources |

Redirect URI must match Google Cloud console: `https://zyvor.dev/api/v1/admin/youtube/oauth/callback`.

## Smoke tests

```bash
# After local website-server is running with TLS + build/
npm run test:smoke

# Or against production
BASE_URL=https://zyvor.dev npm run test:smoke
```

## Deploy

```bash
npm run build
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o .dist/website-server ./cmd/website-server
./scripts/deploy-container.sh <user@host>
```

Use `SKIP_BUILD=1` when `build/` and binary are already current.
