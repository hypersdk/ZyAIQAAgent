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
  styles,
} from '../components/shared';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {ProductReadingPathStrip} from '../components/ProductReadingPathStrip';
import {vmspawn} from '../data/platform-stats';

export default function ZyvorFabricPage(): ReactNode {
  return (
    <ProductPage
      themeId="zyvor-fabric"
      title={`${vmspawn.productName} — systemd-native private cloud`}
      description={`${vmspawn.productName} — enterprise VM management on systemd-vmspawn and systemd-machined. CLI, TUI, web dashboard, Kubernetes operator, and Terraform with 480+ REST APIs.`}
    >
      <PageHero
        themeId="zyvor-fabric"
        variant="split"
        eyebrow="Zyvor Fabric"
        gradientWord="Zyvor"
        title="Fabric"
        subtitle="systemd-Native VM Control Plane"
        description="Run Proxmox-class VM operations on systemd-vmspawn with CLI, TUI, web, and Terraform."
        primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
        secondaryCta={{label: 'Product docs', to: '/docs/zyvor-fabric'}}
      />

      <PageContent>
        <StatGrid
          stats={[
            {value: vmspawn.apiEndpoints, label: 'REST endpoints'},
            {value: String(vmspawn.interfaces), label: 'Interfaces'},
            {value: String(vmspawn.rustCrates), label: 'Rust crates'},
            {value: vmspawn.version, label: 'Release'},
          ]}
          columns={4}
        />

        <ProductConceptSections productId="zyvor-fabric" />

        <div
          className={styles.featureCard}
          style={{
            maxWidth: 880,
            margin: '0 auto 3rem',
            padding: '2rem 2.25rem',
            border: '1px solid rgba(45, 212, 191, 0.28)',
            background: 'linear-gradient(165deg, rgba(45, 212, 191, 0.08) 0%, rgba(5, 5, 5, 0.4) 100%)',
          }}
        >
          <p
            style={{
              margin: '0 0 0.75rem',
              fontSize: '0.72rem',
              fontWeight: 700,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: '#5eead4',
            }}
          >
            Built on systemd
          </p>
          <h2 style={{margin: '0 0 0.85rem', fontSize: '1.35rem', color: 'var(--hs-text-heading)'}}>
            Thanks to Lennart Poettering and the systemd project
          </h2>
          <p style={{margin: 0, lineHeight: 1.75, color: 'var(--hs-text-body)'}}>
            Zyvor Fabric is built directly on <strong>systemd-vmspawn</strong> and <strong>systemd-machined</strong> —
            the VM management primitives the systemd community brought to modern Linux. We are grateful to{' '}
            <strong>Lennart Poettering</strong> and everyone who contributes to the{' '}
            <a href="https://systemd.io/" target="_blank" rel="noopener noreferrer">
              systemd project
            </a>{' '}
            for that foundation.
          </p>
        </div>

        <SectionHeader
          eyebrow="Interfaces"
          title="One daemon, five ways to operate"
          subtitle="Operators script with vmctl, live in the TUI, delegate to platform teams via Kubernetes or Terraform, or use the full web dashboard."
        />
        <BentoGrid
          items={[
            {
              title: 'vmctl CLI',
              desc: '15+ command groups with JSON/YAML/table output — lifecycle, policy, firewall, Ceph, monitoring, and networking.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'vmctl-tui',
              desc: 'Eight views with vim keybindings, sparkline metrics, and live API data — k9s-style for systemd VMs.',
            },
            {
              title: 'Web dashboard',
              desc: '37+ pages, command palette (Ctrl/Cmd+K), bulk operations, WebSocket consoles via xterm.js and noVNC.',
            },
            {
              title: 'Kubernetes operator',
              desc: 'VirtualMachine CRDs with auto-reconciliation — same VMs, cluster-native GitOps.',
            },
            {
              title: 'Terraform provider',
              desc: 'Declarative provisioning with full plan/apply workflow for infrastructure-as-code teams.',
              span: 'wide',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Enterprise depth"
          title="Production VM operations"
          subtitle="Security, networking, storage, and HA patterns that teams expect from proprietary hypervisors — on open Linux + systemd."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Security & compliance',
              desc: 'JWT auth, RBAC (Admin/User/Viewer), TLS, encryption at rest, and audit logs exportable as JSON or CSV.',
            },
            {
              title: 'Network intelligence',
              desc: 'Label-based policies, per-VM nftables firewall, WireGuard mesh, QoS shaping, NAT gateway, and packet mirror.',
            },
            {
              title: 'Storage backends',
              desc: 'Local, NFS, LVM, LVM-thin, ZFS, and Ceph/RBD — snapshots, clone, resize, and attach/detach.',
            },
            {
              title: 'High availability',
              desc: 'etcd clustering, leader election, predictive DRS, fault tolerance, and distributed site recovery.',
            },
            {
              title: 'GPU & confidential guests',
              desc: 'NVIDIA, AMD, and Intel GVT-g passthrough; TPM 1.2/2.0 via swtpm; Secure Boot and cloud-init.',
            },
            {
              title: 'Observability',
              desc: 'Prometheus metrics, analytics reports (PDF/CSV), Slack/Teams/webhook notifications, and scheduled jobs.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="systemd-vmspawn v260"
          title="The full vmspawn surface — plus live hot-add"
          subtitle="Every systemd-vmspawn(1) option is a first-class API field, and running VMs grow CPU, memory, disks, and NICs through QMP without a reboot."
        />
        <BentoGrid
          items={[
            {
              title: 'Hot-add & hot-remove',
              desc: 'POST /vms/{name}/hotplug/{cpu,memory,disk,nic} drives QEMU QMP to scale a running VM — the built-in autoscaler uses the same path to grow CPU and RAM on the fly.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Machine identity & isolation',
              desc: 'VSock with CID assignment, SMBIOS Type #11 vendor strings, user namespacing (--private-users), and systemd credentials via --set-credential / --load-credential.',
            },
            {
              title: 'Boot & integration',
              desc: 'Direct kernel boot (--linux/--initrd), firmware selection, journal forwarding to the host, SSH key pass-through, and bind mounts (--bind, --bind-ro).',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Performance"
          title="NUMA-aware placement, CPU pinning, and hugepages"
          subtitle="Zyvor Fabric reads real host topology from sysfs and pins guests to it — no guesswork for latency-sensitive or many-core workloads."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Topology detection',
              desc: 'GET /api/system/cpu/topology reports sockets, cores-per-socket, threads-per-core, and the NUMA node of every logical CPU — surfaced in the CPU Topology view.',
            },
            {
              title: 'NUMA-aware placement',
              desc: '/api/system/numa/topology, /nodes/{id}, and /placement locate a guest on the node whose CPUs and memory keep it local, avoiding cross-socket penalties.',
            },
            {
              title: 'Hugepage memory',
              desc: '2 MB and 1 GB hugepages allocated and reported via /api/system/memory/hugepages for reduced TLB pressure on large-RAM VMs.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Infrastructure Time Machine"
          title="Config snapshots and event retention for RCA"
          subtitle="Capture the whole control plane as a versioned bundle, diff it over time, and correlate incidents — the API foundation Machina's Time Machine consumes."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Config snapshots',
              desc: 'GET /api/config/snapshot returns a versioned JSON bundle — VM inventory, network policies, storage pools, retained event count, and an RFC3339 timestamp — for periodic dumps and configuration diffing.',
            },
            {
              title: 'Tunable event retention',
              desc: 'GET/PUT /api/events/retention sizes the lifecycle-event buffer (default 1000, clamp 100–100000) with background pruning; the SSE stream at /api/events/stream is never interrupted.',
            },
            {
              title: 'Correlation surface',
              desc: '/api/events, /api/audit/logs, and /api/network/topology give a root-cause copilot the lifecycle, operator-action, and topology data to correlate a snapshot diff against.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="zyvor-fabric" />

        <ProductReadingPathStrip productId="zyvor-fabric" />
        <ClientPresentationSection productId="zyvor-fabric" />

        <SuiteProductFooter
          productId="zyvor-fabric"
          ctaTitle={`Ready for ${vmspawn.productName}?`}
          ctaSubtitle={`See how ${vmspawn.productName} delivers Proxmox-class operations on systemd-vmspawn — with HyperSDK migration and GuestKit assurance in the same suite.`}
          secondaryCta={{label: 'Compare Machina', to: '/machina'}}
        />
      </PageContent>
    </ProductPage>
  );
}
