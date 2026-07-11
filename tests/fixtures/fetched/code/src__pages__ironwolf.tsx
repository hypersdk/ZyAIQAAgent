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
  FeatureGrid,
  BentoGrid,
  SuiteProductFooter,
} from '../components/shared';
import {ironWolf} from '../data/platform-stats';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import Link from '@docusaurus/Link';

function TrialSection(): ReactNode {
  return (
    <div style={{textAlign: 'center', padding: '4rem 1.5rem', maxWidth: 860, margin: '0 auto'}}>
      <SectionHeader
        eyebrow="30-Day Trial"
        title="Get Full Access — Request Your Trial"
        subtitle="Run IronWolf on your bare metal fleet with full lifecycle automation, all 24 CRDs, BMC drivers, and the 66-page dashboard. Onboarding included."
      />
      <Link
        to="/contact?intent=trial&product=ironwolf"
        style={{
          display: 'inline-block',
          margin: '1.5rem 0 2.5rem',
          padding: '0.85rem 2.25rem',
          borderRadius: 8,
          background: 'linear-gradient(135deg, #ef4444, #6b7280)',
          color: '#fff',
          fontWeight: 700,
          fontSize: '1rem',
          textDecoration: 'none',
        }}
      >
        Request 30-Day Trial
      </Link>
      <BentoGrid
        items={[
          {
            title: 'Full Feature Access',
            desc: 'All 24 CRDs, 7 BMC drivers, hardware pool scheduling, and the complete 66-page React dashboard — nothing gated.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'Delivered via Helm',
            desc: 'Deploy the operator and dashboard with a single Helm command into your Kubernetes cluster alongside Metal3.',
          },
          {
            title: 'Onboarding Session',
            desc: 'A 45-minute walkthrough with the Zyvor team to configure BMC access, firmware profiles, and hardware pool policies.',
          },
          {
            title: 'After the Trial',
            desc: 'Move to a commercial licence with no data loss. Hardware pools, firmware profiles, and policies carry forward.',
          },
        ]}
      />
      <div style={{marginTop: '2rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center'}}>
        {['Kubernetes 1.32+', 'Metal3 BareMetalOperator', 'IPMI / Redfish / iDRAC', 'Helm 3.x', 'Go 1.25+'].map(
          (pill) => (
            <span
              key={pill}
              style={{
                padding: '0.35rem 0.85rem',
                borderRadius: 999,
                background: 'rgba(239,68,68,0.12)',
                color: '#fca5a5',
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              {pill}
            </span>
          ),
        )}
      </div>
    </div>
  );
}

export default function IronWolf(): ReactNode {
  return (
    <ProductPage
      themeId="ironwolf"
      title="IronWolf -- Enterprise Bare Metal Infrastructure Operator"
      description="Kubernetes operator for bare metal lifecycle management. 24 Metal3 CRDs (13 IronWolf extensions + Metal3 integration), 66-page dashboard, BMC drivers, and hardware pool scheduling."
    >
      <PageHero
        themeId="ironwolf"
        variant="split"
        eyebrow="Product"
        gradientWord="IronWolf"
        title=""
        subtitle="Bare Metal Lifecycle Operator"
        description="Extend Metal3 with enterprise automation for firmware, power, pools, and remediation."
        primaryCta={{label: 'Request 30-Day Trial', to: '/contact?intent=trial&product=ironwolf'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/ironwolf'}}
      />

      <PageContent>
        <StatGrid
          stats={[
            {value: `${ironWolf.crds} CRDs`, label: 'Custom Resources'},
            {value: `${ironWolf.dashboardPages} Pages`, label: 'React Dashboard'},
            {value: `${ironWolf.bmcProtocols} BMC`, label: 'BMC Drivers'},
            {value: `${ironWolf.scripts} Scripts`, label: 'Operations'},
          ]}
          columns={4}
        />

        <ProductConceptSections productId="ironwolf" />

        <SectionHeader
          eyebrow="Key Capabilities"
          title="Full Host Lifecycle on Kubernetes"
          subtitle="From discovery to decommission — 24 CRDs extending Metal3 Bare Metal Operator."
        />
        <BentoGrid
          items={[
            {
              title: 'Hardware Discovery',
              desc: 'Automatic bare metal host discovery and inventory management with BMC integration via Metal3.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Firmware Automation',
              desc: 'Declarative firmware profiles for BIOS, BMC, and NIC firmware. Schedule upgrades during maintenance windows.',
            },
            {
              title: 'Power Policies',
              desc: 'Kubernetes-native power management with scheduled power states, idle detection, and energy-aware scheduling.',
            },
            {
              title: 'Hardware Pools',
              desc: 'Group hosts by capability, location, or purpose. Three scheduling strategies: binpack, spread, and topology-aware.',
            },
            {
              title: 'Maintenance Windows',
              desc: 'Scheduled maintenance with automatic workload evacuation, cordoning, and post-maintenance validation.',
            },
            {
              title: 'Remediation',
              desc: 'Automatic hardware remediation with configurable strategies, escalation policies, and integration with alerting systems.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Observability"
          title="Full-Stack Bare Metal Visibility"
          subtitle="66-page React dashboard with Grafana integration and multi-channel alerting."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'React Dashboard',
              desc: 'Full-featured web UI for host lifecycle operations with real-time status updates.',
            },
            {
              title: 'Prometheus Metrics',
              desc: 'Built-in Prometheus metrics for hardware health, power consumption, firmware versions, and pool utilization.',
            },
            {
              title: 'Alerting',
              desc: 'Slack, email, and webhook alerting for hardware failures, firmware drift, and maintenance schedule violations.',
            },
          ]}
        />

        <SectionHeader eyebrow="Integration" title="Fits Your Infrastructure Stack" />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Metal3 Native',
              desc: 'Extends the Metal3 Bare Metal Operator. Compatible with existing Metal3 deployments and Ironic integrations.',
            },
            {
              title: 'Terraform & Crossplane',
              desc: 'Provision and manage bare metal hosts from Terraform or Crossplane alongside your cloud infrastructure.',
            },
            {
              title: 'Grafana Dashboards',
              desc: 'Pre-built Grafana dashboards for hardware fleet health, power consumption trends, and capacity planning.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Image Factory"
          title="Build Golden OS Images, Not Just Provision Them"
          subtitle="A GitOps image pipeline in the image.ironwolf.io API group — ImageRecipe → ImageBuild → ImageArtifact — so the OS Metal3 writes to a host is reproducible from source."
        />
        <BentoGrid
          items={[
            {
              title: 'ImageRecipe Templates',
              desc: 'Long-lived build templates pinning OS family, Kubernetes version, provider make-target, node profile, and an embedded security policy. Change the recipe, get a new image.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Pluggable Executors',
              desc: 'ImageBuild runs on auto, lab, or kubernetes executors. Auto picks the right backend; Kubernetes runs the build as an in-cluster Job.',
            },
            {
              title: 'Checksummed Artifacts',
              desc: 'Every ImageBuild records a checksum and a resolved manifest URI, so provisioning references a verifiable, immutable image.',
            },
            {
              title: 'Approval & Promotion',
              desc: 'ImageArtifact catalogs each built golden image with an approval gate and promotion field — only approved images flow to production hosts.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Real-Time BMC Events"
          title="Redfish Event Streaming, Not Polling"
          subtitle="BMCEventSubscription registers against a host's Redfish EventService so the BMC pushes hardware events the moment they happen."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Native Redfish Subscriptions',
              desc: 'Subscribe a BareMetalHost to its BMC EventService. Thermal, power, and hardware fault events arrive as they occur instead of on a poll interval.',
            },
            {
              title: 'Webhook Delivery',
              desc: 'Events post to an HTTPS destination with a per-subscription context tag and optional custom headers loaded from a Kubernetes Secret.',
            },
            {
              title: 'Managed Lifecycle',
              desc: 'The controller creates and reconciles the Redfish subscription ID and cleans it up via finalizer when the resource is deleted.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Hardware DR"
          title="Back Up and Restore BMC & BIOS Config"
          subtitle="HardwareBackup and RestoreJob CRDs treat firmware settings as recoverable state — cron-scheduled capture and point-in-time restore of hardware configuration."
        />
        <BentoGrid
          items={[
            {
              title: 'Scheduled Config Backups',
              desc: 'HardwareBackup runs on a cron schedule across a host label selector, capturing BIOS, BMC, firmware, RAID, network, and partition config with a retention count.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Post-Backup Verification',
              desc: 'Optional verification validates each backup after capture, so a stored backup is known-good before you ever need it.',
            },
            {
              title: 'Selective Restore',
              desc: 'RestoreJob restores a chosen backup to a target host, component by component, with dry-run and force options.',
            },
            {
              title: 'Rollback on Failure',
              desc: 'Restores can roll back automatically if a component fails mid-apply, avoiding a half-configured host.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="ironwolf" />

        <ClientPresentationSection productId="ironwolf" />
        <TrialSection />
        <SuiteProductFooter
          productId="ironwolf"
          ctaTitle="Ready to manage bare metal at scale?"
          ctaSubtitle="See how IronWolf brings Kubernetes-native lifecycle management to your bare metal infrastructure."
          secondaryCta={{label: 'Request Trial', to: '/contact?intent=trial&product=ironwolf'}}
        />
      </PageContent>
    </ProductPage>
  );
}
