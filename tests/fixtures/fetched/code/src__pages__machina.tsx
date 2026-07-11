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
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import {machina} from '../data/platform-stats';
import Link from '@docusaurus/Link';

function TrialSection(): ReactNode {
  return (
    <div style={{textAlign: 'center', padding: '4rem 1.5rem', maxWidth: 860, margin: '0 auto'}}>
      <SectionHeader
        eyebrow="30-Day Trial"
        title="Get Full Access — Request Your Trial"
        subtitle="Run Machina on your KVM host with full REST API, web dashboard, TUI, console access, and optional OpenStack integration. Onboarding included."
      />
      <Link
        to="/contact?intent=trial&product=machina"
        style={{
          display: 'inline-block',
          margin: '1.5rem 0 2.5rem',
          padding: '0.85rem 2.25rem',
          borderRadius: 8,
          background: 'linear-gradient(135deg, #14b8a6, #22c55e)',
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
            desc: 'All 60+ API endpoints, VNC/SPICE/SSH/serial consoles, TUI, scheduled actions, webhooks, and OpenStack integration — nothing gated.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'Single Binary Install',
            desc: 'One Rust binary, one systemd unit. Runs on any Linux host with libvirt. Listening at https://localhost:5092 in minutes.',
          },
          {
            title: 'Onboarding Session',
            desc: 'A 45-minute walkthrough with the Zyvor team to configure PAM/LDAP auth, fleet peering, and optional OpenStack wiring.',
          },
          {
            title: 'After the Trial',
            desc: 'Move to a commercial licence with no data loss. VM inventory, snapshots, and scheduled actions carry forward.',
          },
        ]}
      />
      <div style={{marginTop: '2rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center'}}>
        {['Linux x86-64', 'libvirt 10+', 'QEMU/KVM', 'PAM auth', 'OpenStack optional'].map((pill) => (
          <span
            key={pill}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: 999,
              background: 'rgba(20,184,166,0.12)',
              color: '#5eead4',
              fontSize: '0.8rem',
              fontWeight: 600,
            }}
          >
            {pill}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function Machina(): ReactNode {
  return (
    <ProductPage
      themeId="machina"
      title="Machina -- Linux Hypervisor Host Management"
      description="Machina is Linux hypervisor host management for QEMU/KVM under libvirt: Rust daemon with REST and WebSocket APIs, React web UI, terminal TUI, full console access, and enterprise-grade auth."
    >
      <PageHero
        themeId="machina"
        variant="split"
        eyebrow="Product"
        gradientWord="Machina"
        title=""
        subtitle="Enterprise Linux Hypervisor Platform"
        description="Manage libvirt VMs, storage, networks, and consoles from one web or terminal interface."
        primaryCta={{label: 'Request 30-Day Trial', to: '/contact?intent=trial&product=machina'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/machina'}}
      />

      <PageContent>
        <StatGrid
          stats={[
            {value: machina.endpoints, label: 'API Endpoints'},
            {value: String(machina.consoleTypes), label: 'Consoles'},
            {value: 'OpenStack', label: 'Nova + Glance'},
            {value: 'PAM + RBAC', label: 'Enterprise Auth'},
          ]}
          columns={4}
        />

        <ProductConceptSections productId="machina" />

        <SectionHeader
          eyebrow="Key Capabilities"
          title="Full-Stack VM Management"
          subtitle="Every interface your team needs to operate libvirt infrastructure at scale, from browser-based dashboards to keyboard-driven terminal workflows."
        />
        <BentoGrid
          items={[
            {
              title: 'Web UI with Full Console',
              desc: 'React dashboard with integrated noVNC, SPICE, and xterm.js consoles. Access any VM directly from your browser with zero client software.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Terminal TUI',
              desc: 'A rich terminal interface built on ratatui for operators who prefer keyboard-driven workflows. Full VM lifecycle management without leaving the terminal.',
            },
            {
              title: 'Multi-Protocol Console Access',
              desc: 'VNC, SPICE, serial, and SSH console access from a single platform. Connect to any VM regardless of guest OS or display configuration.',
            },
            {
              title: 'Live Metrics and Alerting',
              desc: 'Real-time CPU, memory, disk, and network metrics with Prometheus integration. Configurable alerts and webhooks for proactive incident response.',
            },
            {
              title: 'OpenStack without Horizon',
              desc: 'Nova instances, Glance images, and qcow2 upload from the same dashboard as libvirt. Credentials on the daemon host via clouds.yaml or Packstack wire script.',
              span: 'wide',
              accent: true,
            },
          ]}
        />

        <SectionHeader
          eyebrow="Private cloud"
          title="OpenStack on the hypervisor host"
          subtitle="Day-2 Nova and Glance management co-located with libvirt — pair with HyperSDK Platform for bulk migrations into the same cloud."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Keystone on the host',
              desc: 'Auth URL, project, and region in machina config or clouds.yaml — never stored in the browser.',
            },
            {
              title: 'Instance lifecycle',
              desc: 'List, start, stop, reboot, and create Nova instances from /openstack/instances when the cloud is wired.',
            },
            {
              title: 'Glance upload',
              desc: 'Push golden qcow2 images to Glance from Disk Images — native Keystone + Glance v2 in machina-daemon.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Enterprise Operations"
          title="Automate and Secure Your Virtualization Layer"
          subtitle="Scheduled actions, webhook integrations, and role-based access control built in from day one."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Scheduled Actions',
              desc: 'Automate VM lifecycle operations on a schedule. Snapshots, backups, and maintenance windows without manual intervention.',
            },
            {
              title: 'Webhook Integrations',
              desc: 'Push real-time VM events to your incident management, ChatOps, and automation pipelines via configurable webhooks.',
            },
            {
              title: 'PAM + RBAC Security',
              desc: 'Native PAM authentication with fine-grained role-based access control. Integrate with your existing identity infrastructure.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Console Experience"
          title="Cinema and Studio — VM consoles, reimagined"
          subtitle="ConsoleHub gives operators a full-screen player HUD for display protocols and a split-pane engineer layout for recovery work — plus a fleet-wide live preview wall."
        />
        <BentoGrid
          items={[
            {
              title: 'Machina Cinema',
              desc: 'Full-screen VNC/SPICE/WebRTC display where the VM canvas fills the viewport. Auto-hiding control strip with power, scale modes (Fit/Fill/Native/Scroll/Stretch), screenshot, and a ⌘K console command palette.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Machina Studio',
              desc: 'Engineer layout with a Display · Serial · Shell · AI lens bar, recovery cards, and an Ops Shelf slide-over for port forwards, health, and the event timeline. Serial-recommended VMs auto-route here.',
            },
            {
              title: 'Mission Control Live Wall',
              desc: 'A fleet preview grid of live console thumbnails so one operator can watch many hypervisors at once from a single launchpad.',
            },
            {
              title: 'Recording and Break-Glass',
              desc: 'Optional session recording captures the console to .webm on exit with a Rec badge and per-user watermark. Break-glass starts a mandatory audited, recorded session for emergency access.',
            },
            {
              title: 'Spectator and Share Links',
              desc: 'Mint time-limited, read-only console links so teammates can watch a session live — collaborative troubleshooting without handing over credentials.',
              span: 'wide',
              accent: true,
            },
          ]}
        />

        <SectionHeader
          eyebrow="SOC Integration"
          title="Stream normalized security events to your SIEM"
          subtitle="Machina's built-in SOC normalizes audit, firewall, and PacketWolf events into ECS-shaped records, runs detection rules, and forwards them to the SIEM you already run."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Splunk HEC',
              desc: 'Forward to an HTTP Event Collector with dedicated sourcetypes for events, alerts, and health checks. Test the connection from the SOC integrations page.',
            },
            {
              title: 'Elastic Security',
              desc: 'Bulk-index ECS documents into an Elasticsearch data stream with an API key — ready for Kibana detections and dashboards.',
            },
            {
              title: 'Microsoft Sentinel',
              desc: 'Push to a Data Collection Endpoint via a DCR stream using an Entra app registration or a pre-issued bearer token.',
            },
            {
              title: 'IBM QRadar',
              desc: 'Deliver events to a QRadar log source over the REST API with a scoped security token.',
            },
          ]}
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'ECS normalization',
              desc: 'Every source maps to Elastic Common Schema fields — event.dataset, event.severity, MITRE tags — so detections and correlation work across firewall, audit, and network data.',
            },
            {
              title: 'SOAR playbooks',
              desc: 'A built-in notify-on-critical playbook fires webhooks on high/critical alerts. Build your own with severity triggers and webhook or notify steps from the Playbooks tab.',
            },
            {
              title: 'Replay and triage',
              desc: 'Re-export events not yet shipped with a single replay call, and work alerts in an inbox with linked events, assignees, and Ack/Close.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Deep Telemetry"
          title="Kernel-level Linux host observability"
          subtitle="Beyond VM metrics, Machina surfaces the host signals that predict trouble — pressure stall, disk health, thermals, and per-VM cgroup accounting — and exports them wherever your observability stack lives."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'PSI, SMART, thermal, cgroups',
              desc: 'One host observability endpoint returns Pressure Stall Information (CPU/memory/IO), /proc/diskstats block I/O, SMART disk health, hwmon thermals, cgroup v2 stats, and per-VM cgroup accounting — plus a bpftool eBPF summary.',
            },
            {
              title: 'OTLP export',
              desc: 'Ship metrics, logs, and traces over OTLP to an OpenTelemetry Collector or Grafana Alloy. API responses carry a W3C traceparent header for end-to-end correlation.',
            },
            {
              title: 'Prometheus remote_write receiver',
              desc: 'Accept Prometheus remote_write 1.0 and 2.0 (Snappy protobuf) into the metrics-history ring, or scrape host, VM, and fleet-wide series — one fleet job labels every peer.',
            },
            {
              title: 'Tamper-evident audit log',
              desc: 'Sign each audit line with a sha256 prefix for tamper detection, rotate and ship to syslog or an HTTP webhook, and export the full trail as NDJSON to your SIEM.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="machina" />

        <ClientPresentationSection productId="machina" />
        <TrialSection />
        <SuiteProductFooter
          productId="machina"
          ctaTitle="Ready to modernize your libvirt management?"
          ctaSubtitle="See how Machina delivers browser and terminal access to your entire libvirt infrastructure with enterprise-grade security."
          secondaryCta={{label: 'Request Trial', to: '/contact?intent=trial&product=machina'}}
        />
      </PageContent>
    </ProductPage>
  );
}
