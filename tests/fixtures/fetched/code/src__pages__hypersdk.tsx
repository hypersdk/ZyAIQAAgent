// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {
  ProductPage,
  PageHero,
  PageContent,
  StatGrid,
  SectionHeader,
  FeatureGrid,
  IntegrationDiagram,
  PillGroup,
  CommunityEditionCallout,
  BentoGrid,
  SectionBand,
  styles,
  SuiteProductFooter,
} from '../components/shared';
import {hypersdk} from '../data/platform-stats';
import {cloudProvidersCompactList} from '../data/cloud-providers';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {ProductReadingPathStrip} from '../components/ProductReadingPathStrip';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';

export default function HyperSDKPage(): ReactNode {
  return (
    <ProductPage
      themeId="hypersdk"
      title="HyperSDK Platform — Multi-Cloud VM Migration"
      description="Export, convert, and deploy VMs across cloud providers — the migration engine in the Zeus OS stack."
      applicationStats={[
        `${hypersdk.apiRoutes} REST API routes`,
        `${hypersdk.dashboardViews} dashboard views`,
        `${hypersdk.connectedClouds} cloud providers`,
      ]}
    >
      <PageHero
        themeId="hypersdk"
        variant="split"
        flagship
        eyebrow="Migration engine"
        gradientWord="HyperSDK"
        title="Platform"
        subtitle="Multi-Cloud VM Migration Platform"
        description="Export, convert, and deploy virtual machines across clouds — then operate fleets in Zeus OS."
        primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
        secondaryCta={{label: 'View Dashboard', to: '/docs/dashboard'}}
      />

      <PageContent>
        <CommunityEditionCallout />

        <BentoGrid
          items={[
            {
              title: 'Connect every platform',
              desc: `${cloudProvidersCompactList} — one interface for all ${hypersdk.connectedClouds} providers.`,
              span: 'wide',
              accent: true,
            },
            {
              title: 'Deploy to private cloud',
              desc: 'Export from any source and land on OpenStack Glance with optional Nova boot — or manage day-2 from Machina on the hypervisor host.',
            },
            {
              title: 'Migrate automatically',
              desc: 'Export, convert disk formats, fix guest OS, and deploy — one pipeline with rollback-safe checkpoints.',
            },
            {
              title: 'Enterprise security',
              desc: 'RBAC, audit logging, rate limiting, and encrypted credential storage — HTTPS by default.',
            },
          ]}
        />

        <SectionBand tone="elevated">
          <SectionHeader
            eyebrow="Architecture"
            title="How it all connects"
            subtitle="A unified API layer for export, convert, and deploy across public clouds and KVM."
          />
          <IntegrationDiagram
            content={`Cloud Providers → HyperSDK Platform API → Dashboard
  vSphere           ↕               ↕
  Nutanix AHV       Export          Monitor
  AWS             Convert         Alerts
  Azure             Deploy          Reports
  GCP               ↕
  Hyper-V           ↕
  OpenStack         ↕
  ...           KVM / KubeVirt / Glance`}
          />
        </SectionBand>

        {/* Key Numbers */}
        <StatGrid
          columns={4}
          stats={[
            {value: hypersdk.connectedClouds, label: 'Cloud Providers'},
            {value: hypersdk.apiRoutes, label: 'API Routes'},
            {value: hypersdk.dashboardViews, label: 'Dashboard Views'},
            {value: hypersdk.reactComponents, label: 'React Components'},
          ]}
        />

        <ProductConceptSections productId="hypersdk" />

        {/* Savings Snapshot */}
        <SectionHeader
          eyebrow="Business Impact"
          title="How Much Teams Save with HyperSDK Platform"
          subtitle="Reduce cloud lock-in costs, avoid expensive replatforming, and move workloads faster with an automated migration pipeline."
        />
        <div className={`${styles.featureGrid} ${styles.featureGridCol3}`}>
          {[
            {
              icon: '💸',
              title: '30-50% Lower Migration Effort',
              desc: 'Automation removes repetitive export, conversion, and guest OS fix work, so teams spend less time per VM and complete projects with smaller migration squads.',
            },
            {
              icon: '📉',
              title: '20-40% Infra Cost Optimization',
              desc: 'Shift workloads to better-priced clouds or KVM targets without manual rebuilds, helping ops teams optimize spend while keeping performance SLAs intact.',
            },
            {
              icon: '⚡',
              title: 'Up to 80% Faster Time-to-Move',
              desc: 'Standardized API workflows cut weeks of one-off scripting. Move from pilot migrations to repeatable factory-style execution in a fraction of the time.',
            },
          ].map((item) => (
            <div key={item.title} className={styles.featureCard}>
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '1rem',
                  fontSize: '1.2rem',
                  background: 'linear-gradient(135deg, rgba(255, 140, 0, 0.16), rgba(255, 140, 0, 0.06))',
                  border: '1px solid rgba(255, 140, 0, 0.25)',
                  boxShadow: '0 8px 26px rgba(240, 88, 58, 0.12)',
                }}
              >
                {item.icon}
              </div>
              <h3 className={styles.featureCardTitle}>{item.title}</h3>
              <p className={styles.featureCardDesc}>{item.desc}</p>
            </div>
          ))}
        </div>

        {/* Platform Logos */}
        <div style={{textAlign: 'center'}}>
          <SectionHeader eyebrow="Supported Platforms" title="Runs on Every Major OS" />
          <PillGroup items={['RHEL', 'Ubuntu', 'Windows Server', 'Debian', 'SUSE', 'Fedora', 'CentOS', 'Photon OS']} />
        </div>

        {/* API Example */}
        <div style={{textAlign: 'center'}}>
          <IntegrationDiagram content={`GET /api/v1/health \u2192 {"status": "healthy"}`} />
          <p
            style={{
              color: 'var(--hs-text-subtle)',
              fontSize: '0.8rem',
              marginTop: '0.75rem',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {hypersdk.apiRoutes} REST endpoints. One consistent API.
          </p>
        </div>

        {/* See It In Action */}
        <SectionHeader
          eyebrow="Demo"
          title="See It In Action"
          subtitle="Watch HyperSDK Platform migrate a VMware VM to KVM in under two minutes with real export, conversion, and boot validation."
        />
        <Link to="/demo" style={{textDecoration: 'none', display: 'block'}}>
          <div
            className={styles.featureCard}
            style={{
              maxWidth: 700,
              margin: '0 auto 5rem',
              textAlign: 'center',
              cursor: 'pointer',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid rgba(255, 140, 0, 0.2)',
              padding: '4rem 2rem',
            }}
          >
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                background: 'var(--hs-gradient-primary)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1.5rem',
                boxShadow: '0 8px 30px rgba(240, 88, 58, 0.3)',
              }}
            >
              <span style={{fontSize: '2rem', color: '#fff', marginLeft: 4}}>{'\u25B6'}</span>
            </div>
            <h3 style={{color: 'var(--hs-text-heading)', fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem'}}>
              Watch 2-Minute Demo
            </h3>
            <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', margin: 0}}>
              See a complete VMware-to-KVM migration -- from export to running VM.
            </p>
          </div>
        </Link>

        {/* Quick Start */}
        <SectionHeader
          eyebrow="Getting Started"
          title="Quick Start"
          subtitle="Three commands. That is all it takes to migrate your first VM."
        />
        <div className={`${styles.featureGrid} ${styles.featureGridCol3}`}>
          {[
            {
              step: '1',
              title: 'Install',
              code: 'curl -sSL https://zyvor.dev/install | bash',
              desc: 'One-line install on any Linux distribution. Sets up hyperctl CLI and dependencies.',
            },
            {
              step: '2',
              title: 'Connect',
              code: 'hyperctl provider add openstack --auth-url https://controller:5000/v3',
              desc: 'Register source hypervisors and private clouds. OpenStack uses Keystone v3; deploy targets include Glance and optional Nova.',
            },
            {
              step: '3',
              title: 'Export',
              code: 'hyperctl export web-server-01 --format qcow2',
              desc: 'Export and convert any VM to KVM-ready format. Drivers, boot config, and OS fixes applied automatically.',
            },
          ].map((item) => (
            <div key={item.step} className={styles.featureCard} style={{position: 'relative', paddingTop: '2.5rem'}}>
              <div
                style={{
                  position: 'absolute',
                  top: -16,
                  left: 24,
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  background: 'var(--hs-gradient-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: '0.9rem',
                  color: '#fff',
                  fontFamily: 'var(--hs-font-mono)',
                }}
              >
                {item.step}
              </div>
              <h3 className={styles.featureCardTitle}>{item.title}</h3>
              <div
                style={{
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--hs-border)',
                  borderRadius: 8,
                  padding: '0.75rem 1rem',
                  marginBottom: '0.75rem',
                  overflow: 'auto',
                }}
              >
                <code
                  style={{
                    fontFamily: 'var(--hs-font-mono)',
                    fontSize: '0.8rem',
                    color: 'var(--hs-accent-light)',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {item.code}
                </code>
              </div>
              <p className={styles.featureCardDesc}>{item.desc}</p>
            </div>
          ))}
        </div>

        {/* Incremental export */}
        <SectionHeader
          eyebrow="Incremental export"
          title="Re-export only the blocks that changed"
          subtitle="Changed Block Tracking turns repeat exports from hours into minutes — HyperSDK enables CBT on the VM, tracks per-disk change IDs, and streams just the delta since the last export."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Changed Block Tracking',
              desc: "Uses vSphere's native CBT API — EnableCBT, QueryChangedDiskAreas, and per-disk change IDs — to identify and transfer only the blocks modified since the previous export.",
            },
            {
              title: 'Smart full-export fallback',
              desc: 'Automatically reverts to a full baseline when disk topology changes, the last export is stale, or no CBT baseline exists — no failed jobs, no silent gaps.',
            },
            {
              title: 'Export history metadata',
              desc: 'Every export writes a timestamped manifest with change IDs and sizes, so each run knows exactly what the previous one captured.',
            },
          ]}
        />
        <IntegrationDiagram
          content={`hyperexport --vm "/Datacenter/vm/web-01" --output /backups --incremental
  changed: 5 GB of 100 GB  →  95% less data, ~88% faster than a full export`}
        />

        {/* Resilient transfers */}
        <SectionHeader
          eyebrow="Resilient transfers"
          title="Built to survive flaky WAN links"
          subtitle="Multi-hundred-gigabyte VM disks rarely move over a perfect network. HyperSDK wraps every export and upload in retry, resume, and throttling so long transfers finish instead of failing halfway."
        />
        <BentoGrid
          items={[
            {
              title: 'Exponential backoff with jitter',
              desc: 'Transient failures — connection resets, HTTP 5xx/429, cloud provider throttling — retry with growing, ±25%-jittered delays, while 4xx and permission errors fail fast instead of looping.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Network-aware pause & resume',
              desc: 'Optionally watches the link and parks in-flight operations when the network drops, resuming automatically the moment it recovers.',
            },
            {
              title: 'Resumable, checkpointed downloads',
              desc: 'Disk downloads checkpoint their progress and resume from the last good byte after an interruption, instead of restarting from zero.',
            },
            {
              title: 'Parallel worker pool',
              desc: 'A configurable download worker pool moves multiple disks and files concurrently, with live per-job speed and progress.',
            },
            {
              title: 'Bandwidth throttling',
              desc: 'Rate-limited readers and writers cap export and upload bandwidth so a migration does not saturate production links.',
            },
          ]}
        />

        {/* Encryption */}
        <SectionHeader
          eyebrow="Encryption"
          title="Encrypted at rest and handled per provider"
          subtitle="Source disks are often encrypted, and exported artifacts often need to be. HyperSDK handles both — decrypting at the source where it can, and optionally re-encrypting the output before it lands."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'AES-256-GCM or GPG at rest',
              desc: 'Encrypt exported disk artifacts with AES-256-GCM (passphrase- or key-file-derived) or GPG, using symmetric or recipient-based keys.',
            },
            {
              title: 'Provider-aware source decryption',
              desc: 'Hyper-V Device Encryption is disabled automatically via an offline registry fix; AWS EBS (KMS), GCP default/CMEK, and KMS-backed vSphere decrypt transparently on export.',
            },
            {
              title: 'Explicit LUKS & ADE handling',
              desc: 'Proxmox LUKS unlocks with a supplied passphrase, and Azure Disk Encryption follows a documented disable-before-export path — no silent, unbootable conversions.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="hypersdk" />

        <ProductReadingPathStrip productId="hypersdk" />
        <ClientPresentationSection productId="hypersdk" />
        <SuiteProductFooter
          productId="hypersdk"
          ctaTitle="Ready to simplify your VM migrations?"
          ctaSubtitle="Join enterprise teams who trust HyperSDK Platform to migrate and manage their virtual machine infrastructure."
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
