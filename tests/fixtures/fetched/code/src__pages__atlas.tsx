// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {
  ProductPage,
  PageHero,
  PageContent,
  StatGrid,
  SectionHeader,
  BentoGrid,
  CodePanel,
  PillGroup,
  SuiteProductFooter,
} from '../components/shared';
import {ProductConceptSections} from '../components/ProductConceptSections';

const ACCENT = '#0ea5e9';

function StepLabel({children}: {children: ReactNode}): ReactNode {
  return (
    <p
      style={{
        fontSize: '13px',
        fontWeight: 700,
        color: ACCENT,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        marginBottom: '8px',
        textAlign: 'left',
      }}
    >
      {children}
    </p>
  );
}

const DB_ENGINES: {source: string; aliases: string; target: string; type: 'Homogeneous' | 'Heterogeneous'}[] = [
  {source: 'PostgreSQL', aliases: 'postgres · pg', target: 'CloudNativePG (Postgres)', type: 'Homogeneous'},
  {source: 'MySQL', aliases: 'mysql', target: 'Percona XtraDB (MySQL)', type: 'Homogeneous'},
  {source: 'MariaDB', aliases: 'mariadb · maria', target: 'Percona XtraDB (MySQL)', type: 'Homogeneous'},
  {source: 'Oracle', aliases: 'oracle · ora', target: 'CloudNativePG (Postgres)', type: 'Heterogeneous'},
  {source: 'SQL Server', aliases: 'mssql · sqlserver', target: 'CloudNativePG (Postgres)', type: 'Heterogeneous'},
];

function EngineMatrix(): ReactNode {
  return (
    <div style={{overflowX: 'auto', margin: '1.5rem 0'}}>
      <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '14px', minWidth: 520}}>
        <thead>
          <tr>
            {['Source engine', 'Aliases (kind)', 'Edge target', 'Migration'].map((h) => (
              <th
                key={h}
                style={{
                  textAlign: 'left',
                  padding: '10px 14px',
                  borderBottom: `2px solid ${ACCENT}`,
                  fontWeight: 700,
                  whiteSpace: 'nowrap',
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {DB_ENGINES.map((e) => {
            const hetero = e.type === 'Heterogeneous';
            return (
              <tr key={e.source} style={{borderBottom: '1px solid rgba(128,128,128,0.25)'}}>
                <td style={{padding: '10px 14px', fontWeight: 600}}>{e.source}</td>
                <td style={{padding: '10px 14px', fontFamily: 'var(--ifm-font-family-monospace)', opacity: 0.85}}>
                  {e.aliases}
                </td>
                <td style={{padding: '10px 14px'}}>{e.target}</td>
                <td style={{padding: '10px 14px'}}>
                  <span
                    style={{
                      fontSize: '12px',
                      fontWeight: 700,
                      padding: '2px 10px',
                      borderRadius: 999,
                      whiteSpace: 'nowrap',
                      color: hetero ? '#f0583a' : ACCENT,
                      background: hetero ? 'rgba(240,88,58,0.12)' : 'rgba(14,165,233,0.12)',
                    }}
                  >
                    {e.type}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function QuickstartSection(): ReactNode {
  return (
    <div id="quickstart" style={{scrollMarginTop: '80px', padding: '4rem 1.5rem', maxWidth: 860, margin: '0 auto'}}>
      <SectionHeader
        eyebrow="Quickstart"
        title="Run the Control Plane in One Command"
        subtitle="No Ceph, no cluster. The fake driver serves a full inventory locally so you can explore every API before touching real storage."
      />

      <div style={{marginBottom: '2rem'}}>
        <StepLabel>Step 1 — Start the gateway</StepLabel>
        <CodePanel label="make">{`# Fake Ceph driver on 127.0.0.1:5110
make run`}</CodePanel>
      </div>

      <div style={{marginBottom: '2rem'}}>
        <StepLabel>Step 2 — Talk to it with atlasctl</StepLabel>
        <CodePanel label="atlasctl">{`cargo run -p atlas-cli -- health
cargo run -p atlas-cli -- discover   # populate inventory from the driver
cargo run -p atlas-cli -- pools
cargo run -p atlas-cli -- volumes`}</CodePanel>
      </div>

      <div style={{marginBottom: '2rem'}}>
        <StepLabel>Step 3 — Provision by intent (async)</StepLabel>
        <CodePanel label="REST">{`# Returns 202 Accepted + a tracked job id
curl -X POST http://127.0.0.1:5110/api/atlas/v1/volumes \\
  -H 'content-type: application/json' \\
  -d '{"name":"prod-db","size_gib":100,"intent":"production-block"}'

cargo run -p atlas-cli -- jobs   # watch it reconcile`}</CodePanel>
      </div>

      <div style={{marginBottom: '2rem'}}>
        <StepLabel>Step 4 — Open the Storage Center</StepLabel>
        <CodePanel label="ui">{`# Embedded Zeus OS-style React console
open http://127.0.0.1:5110/

# On a cluster: http://<node>:30511/
# Build the UI: make ui   (make ui-dev for hot reload)`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: 'Intent in, backend out',
            desc: 'Products ask for "production block storage" and Atlas maps intent → placement → backend. They never learn a pool name.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'Three real backends',
            desc: 'Ceph, NFS, and ZFS behind one StorageDriver trait — plus a live Kubernetes driver and a fake driver for dev.',
          },
          {
            title: 'Everything async',
            desc: 'Volumes, snapshots, clone/restore, expand, and backups all return 202 + a job id on a durable SQLite-backed worker.',
          },
          {
            title: 'Verified on real Ceph',
            desc: 'Slices 1–5 validated end-to-end on a k3s + Rook Ceph cluster — PVC Bound, snapshot, clone/restore, RGW backups.',
          },
        ]}
      />
      <div style={{marginTop: '16px'}}>
        <PillGroup
          items={['Rust · axum 0.8 · tonic', 'SQLite (sqlx)', 'Ceph · NFS · ZFS', 'kube-rs', 'Prometheus + Grafana']}
        />
      </div>
    </div>
  );
}

export default function Atlas(): ReactNode {
  return (
    <ProductPage
      themeId="atlas"
      title="Atlas — Zyvor Storage Control Plane"
      description="One storage API for the whole Zyvor suite. Products request intent; Atlas maps it to Ceph, NFS, or ZFS and owns inventory, ownership, jobs, and audit."
    >
      <PageHero
        themeId="atlas"
        variant="split"
        eyebrow="Product"
        gradientWord="Atlas"
        title=""
        subtitle="The storage control plane for the Zyvor suite"
        description="Products request intent — 'give me production block storage' — and Atlas maps it to a backend, owns inventory and audit, and keeps every product decoupled from Ceph or any future backend."
        primaryCta={{label: 'Quickstart', to: '/atlas#quickstart'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/atlas'}}
      />

      <PageContent>
        <StatGrid
          columns={4}
          stats={[
            {value: '3', label: 'Storage Backends'},
            {value: 'REST + gRPC', label: 'Gateway API'},
            {value: '5', label: 'Slices Shipped'},
            {value: '5110', label: 'Default Port'},
          ]}
        />

        <ProductConceptSections productId="atlas" />

        {/* Why a control plane */}
        <SectionHeader
          eyebrow="Why a control plane"
          title="Request Intent, Not Pool Internals"
          subtitle="Wiring every product straight to Ceph couples the whole suite to one backend and scatters quotas, ownership, and audit. Atlas puts a stable API in front of storage."
        />
        <BentoGrid
          items={[
            {
              title: 'One API for every product',
              desc: 'Zeus OS, Veyron, Hyper2KVM, GuestKit, PacketWolf, Aether, Ragnarok, Machina, and HyperSDK all call the same Atlas gateway over REST or gRPC.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Decoupled from Ceph',
              desc: 'Products never learn a pool name. Swap in NFS, ZFS, or a future SAN/cloud backend without rewriting a single caller.',
            },
            {
              title: 'Owns the source of truth',
              desc: 'Inventory, ownership bindings, and a full audit log live in one SQLite-backed place — backed by a Ceph PVC for durability.',
            },
            {
              title: 'Intent → placement',
              desc: 'The policy engine turns "production block" into a concrete backend and pool, with idempotency keys and safe-delete guards.',
            },
          ]}
        />

        {/* Backends */}
        <SectionHeader
          eyebrow="Pluggable drivers"
          title="Three Backends Behind One Trait"
          subtitle="Every backend implements the same StorageDriver contract. Ceph was first; NFS and ZFS followed without touching a single product."
        />
        <BentoGrid
          items={[
            {
              title: 'Ceph — RBD, CephFS & RGW',
              desc: 'The flagship driver wraps the ceph/rbd CLI (arg-arrays, never string concat): RBD block, CephFS RWX file, and RGW/S3 object with buckets and quotas.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'NFS & ZFS',
              desc: 'NFS exports and ZFS zpools map to pools; shares and datasets map to filesystem volumes — filters, gauges, and CSV export included.',
            },
            {
              title: 'Live Kubernetes driver',
              desc: 'Read-only StorageClass / PVC / PV listing via kube-rs, so Atlas sees cluster-native storage alongside its own.',
            },
            {
              title: 'Fake driver for dev',
              desc: 'An in-memory Ceph driver serves a full inventory with no cluster — the whole API surface is explorable on a laptop.',
            },
          ]}
        />
        <CodePanel label="backends">{`# Filter volumes by backend and kind
curl "http://127.0.0.1:5110/api/atlas/v1/volumes?backend=ceph&kind=block"

# Fleet rollup across every backend
curl http://127.0.0.1:5110/api/atlas/v1/backends/summary`}</CodePanel>

        {/* Write path */}
        <SectionHeader
          eyebrow="Async write path"
          title="Every Mutation Is a Tracked Job"
          subtitle="Create, snapshot, clone, restore, expand, and back up — all return 202 + a job id on a durable tokio worker, so nothing blocks and nothing is lost on restart."
        />
        <BentoGrid
          items={[
            {
              title: 'Volumes & snapshots',
              desc: 'POST /volumes provisions a Ceph-backed PVC or direct RBD; snapshots clone and restore with a safe-delete guard on dependents.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'RGW backups',
              desc: 'RBD export-diff streamed to RGW (multipart) + verify, keep-N and max-age retention, and presigned downloads.',
            },
            {
              title: 'Idempotent by key',
              desc: 'Idempotency keys deduplicate retries; the PDF §10.5 state machine governs every job transition.',
            },
            {
              title: 'Scheduled ops',
              desc: 'Recurring snapshots and backups run on a schedule, per tenant, with policy overrides.',
            },
          ]}
        />

        {/* Observability */}
        <SectionHeader
          eyebrow="Observability & multi-tenancy"
          title="Prometheus, Forecasts & a Storage Center"
          subtitle="Atlas exposes its own metrics, forecasts days-to-full, introspects Ceph natively, and ships a Zeus OS-style React console embedded in the gateway."
        />
        <BentoGrid
          items={[
            {
              title: 'Embedded Storage Center',
              desc: 'A React/Vite console with live inventory, capacity/health, SSE job progress, alerts, tenants, a Ceph page, and a 6-visualization Observatory — served by the gateway over HTTPS.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Metrics & forecasts',
              desc: '/metrics (Prometheus), /metrics/history, /metrics/forecast (days-to-full), and /metrics/ceph — plus a Grafana bundle in deploy/observability/.',
            },
            {
              title: 'Ceph-native introspection',
              desc: '/ceph/status, /ceph/osd-tree, /ceph/osd-df, and /ceph/df surface cluster health without leaving Atlas.',
            },
            {
              title: 'Per-tenant guardrails',
              desc: 'Quotas, policy overrides, audit log, and service-account JWTs — with a monitor/alerts worker fanning out to webhooks.',
            },
          ]}
        />
        <div style={{marginTop: '16px'}}>
          <PillGroup
            items={[
              '/metrics',
              '/metrics/forecast',
              '/ceph/status',
              '/events',
              '/readyz',
              'SSE job progress',
              'webhook alerts',
            ]}
          />
        </div>

        {/* DataBridge */}
        <SectionHeader
          eyebrow="DataBridge · cloud-to-edge database mobility"
          title="Migrate Managed Cloud Databases to Open Engines at the Edge"
          subtitle="DataBridge runs from Atlas as a migration control plane — reusing its job engine, inventory, gateway, and Zeus OS console — to move RDS/Aurora, Cloud SQL, Azure SQL, and on-prem Oracle onto open engines on Kubernetes, backed by Ceph."
        />
        <StatGrid
          columns={4}
          stats={[
            {value: '5', label: 'Source Engines'},
            {value: 'Debezium', label: 'Continuous CDC'},
            {value: '2 clusters', label: 'Verified on Live Ceph'},
            {value: 'Guarded', label: 'Cutover + Rollback'},
          ]}
        />
        <EngineMatrix />
        <div style={{marginTop: '8px', marginBottom: '24px'}}>
          <PillGroup
            items={[
              'Discover',
              'Assess',
              'Provision',
              'Full-load',
              'CDC (Debezium)',
              'Validate',
              'Cutover',
              'Rollback',
            ]}
          />
        </div>
        <BentoGrid
          items={[
            {
              title: 'Homogeneous & heterogeneous',
              desc: 'Postgres/MySQL/MariaDB migrate like-for-like with a dump→restore full-load, then Debezium streams changes. Oracle and SQL Server go heterogeneous → Postgres, seeded by Debezium’s initial snapshot with the JDBC sink auto-creating tables.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Ceph-backed edge runtime',
              desc: 'CloudNativePG (Postgres) and Percona XtraDB (MySQL) run on the edge with data + WAL on the zyvor-rbd-prod Ceph RBD StorageClass — Ceph is the storage, not the engine.',
            },
            {
              title: 'Continuous replication',
              desc: 'Debezium on Strimzi/Kafka reads WAL/binlog/redo (Postgres, MySQL, MariaDB, Oracle LogMiner, SQL Server) → Aiven JDBC sink → edge DB, health-tracked by the reconciler.',
            },
            {
              title: 'Guarded cutover + rollback',
              desc: 'Cutover is admin-guarded — plan validated, last validation passed, CDC lag under threshold — and rollback is allowed only within the plan’s rollback window.',
            },
            {
              title: 'Fake-first, no cloud creds',
              desc: 'The whole pipeline runs fake-first with canned schemas and inline stages, so you can walk every stage on a laptop; flip a source to driver_mode: real to run it against live infrastructure.',
            },
            {
              title: 'One async job pipeline',
              desc: 'Sources, plans, edge clusters, CDC streams, validations, and cutovers are Atlas read models over REST — discover → cutover is a single pipeline of 202 + job id stages.',
            },
          ]}
        />
        <CodePanel label="databridge">{`# Walk a Postgres source from register → cutover (fake, no cloud/k8s)
B=http://127.0.0.1:5110/api/atlas/v1
SID=$(curl -sX POST $B/databridge/sources -d '{"name":"orders","kind":"postgres","cloud":"rds"}' | jq -r .id)
curl -sX POST $B/databridge/sources/$SID/discover

PID=$(curl -sX POST $B/databridge/plans -d '{"name":"orders","source_id":"'$SID'"}' | jq -r .id)
for stage in assess provision full-load cdc/start validate cutover; do
  curl -sX POST $B/databridge/plans/$PID/$stage
done`}</CodePanel>
        <div style={{marginTop: '16px'}}>
          <PillGroup
            items={['CloudNativePG', 'Percona XtraDB', 'Debezium', 'Strimzi / Kafka', 'Aiven JDBC sink', 'Ceph RBD']}
          />
        </div>

        <QuickstartSection />

        <SuiteProductFooter
          productId="atlas"
          ctaTitle="Ready to give the whole suite one storage API?"
          ctaSubtitle="Run Atlas locally with the fake driver in one command, then point it at real Ceph, NFS, or ZFS. Products request intent — Atlas does the rest."
          secondaryCta={{label: 'Read the Docs', to: '/docs/atlas'}}
        />
      </PageContent>
    </ProductPage>
  );
}
