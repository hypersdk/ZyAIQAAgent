---
sidebar_position: 10
title: Observability
---

# Observability

Real-time monitoring, alerting, and diagnostics built into the platform.

## Health Score

HyperSDK Platform computes a system health score (0-100) based on:

| Metric | Weight | Source |
|--------|--------|--------|
| CPU usage | 25% | `/proc/stat` |
| Memory usage | 25% | `/proc/meminfo` |
| Disk usage | 25% | `/proc/diskstats` + filesystem stats |
| Network health | 15% | `/proc/net/dev` |
| Service status | 10% | Process monitoring |

The score includes **bottleneck detection** — identifying the top contributing factor when health drops.

## Smart Alerts

Configure threshold-based alerts for:
- CPU usage exceeding threshold
- Memory pressure and swap usage
- Disk space running low
- Network errors or packet loss
- Job failures

Alerts appear in the dashboard and are available via the `/api/v1/system/alerts` endpoint.

## Explain Mode

When a metric is elevated, click **Explain** in the dashboard to see:
- Contributing factors ranked by impact
- Historical trend for the metric
- Recommended actions

Example: "CPU is at 87% — top contributors: migration job (62%), system indexing (15%), other processes (10%)"

## Metrics

### Dashboard Views

The dashboard provides 8 observability views:

| View | What It Shows |
|------|--------------|
| **Health Overview** | System health score with bottleneck indicator |
| **Alerts** | Active and historical alerts |
| **Processes** | Running processes with CPU/memory usage |
| **Containers** | Container status and resource consumption |
| **Security** | Failed logins, rate limit events, audit trail |
| **Debug** | Logs, request tracing, error analysis |
| **Network** | Interface stats, connection counts, bandwidth |
| **Storage** | Pool status, disk I/O, capacity planning |

### Prometheus Export

```bash
curl -sk https://your-server:5080/api/v1/metrics
```

Returns metrics in Prometheus exposition format for integration with Grafana or other monitoring systems.

### WebSocket

Real-time metrics stream via WebSocket:

```javascript
const ws = new WebSocket('wss://your-server:5080/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type: 'metrics', 'alert', 'job_update'
};
```

## Carbon-Aware Scheduling

Schedule migration jobs during low-carbon grid periods:

```bash
curl -sk https://your-server:5080/api/v1/carbon/schedule
```

Returns optimal time windows based on real-time electricity grid carbon intensity data. Typical reduction: **30-50% CO2** per migration batch.

---

## Downloads

- [Monitoring & Observability](pathname:///presentations/standard/16-monitoring-observability/16-monitoring-observability.pdf) -- health scoring, alerts, and dashboards
- [System Observability](pathname:///presentations/standard/22-system-observability/22-system-observability.pdf) -- deep dive into metrics and diagnostics
- [Carbon-Aware Scheduling](pathname:///presentations/standard/09-carbon-aware-scheduling/09-carbon-aware-scheduling.pdf) -- CO2-optimized migration scheduling

---

[Schedule a Demo](/contact) to see observability in action.
