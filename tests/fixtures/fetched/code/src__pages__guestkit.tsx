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
  FeaturePanels,
  IntegrationDiagram,
  CommunityEditionCallout,
  BentoGrid,
  SuiteProductFooter,
} from '../components/shared';
import {YouTubeEmbed} from '../components/YouTubeEmbed';
import {guestkit, platform} from '../data/platform-stats';
import {GUESTKIT_DEMO_VIDEO} from '../data/product-demo-videos';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {ProductReadingPathStrip} from '../components/ProductReadingPathStrip';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';

export default function GuestKit(): ReactNode {
  return (
    <ProductPage
      themeId="guestkit"
      title="GuestKit — Offline VM Disk Intelligence"
      description="Pure-Rust VM disk toolkit. Inspect, analyze, and fix VM disks without booting them. AI-powered diagnostics for QCOW2, VMDK, VDI, VHD, VHDX, and RAW."
    >
      <PageHero
        themeId="guestkit"
        variant="split"
        eyebrow="Product"
        gradientWord="GuestKit"
        title=""
        subtitle="Offline VM Disk Intelligence"
        description="Inspect and fix VM disk images offline before migration — without powering on guests."
        primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
        secondaryCta={{
          label: 'Download PDF deck',
          to: 'pathname:///presentations/client/guestkit/guestkit-client.pdf',
          staticAsset: true,
        }}
      />

      <PageContent>
        <CommunityEditionCallout />

        <SectionHeader
          eyebrow="Product demo"
          title="See GuestKit in action"
          subtitle="Walkthrough of offline disk inspection, TUI views, and diagnostics — no powered-on VM required."
        />
        <div style={{maxWidth: 960, margin: '0 auto 4rem'}}>
          <YouTubeEmbed videoId={GUESTKIT_DEMO_VIDEO.youtubeId} title={GUESTKIT_DEMO_VIDEO.title} priorityThumb />
          <p style={{textAlign: 'center', marginTop: '0.85rem', marginBottom: 0}}>
            <a
              href={GUESTKIT_DEMO_VIDEO.watchUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{color: 'var(--hs-accent-light)', fontSize: '0.95rem'}}
            >
              Open on YouTube
            </a>
            {' · '}
            <Link to="/demo" style={{color: 'var(--hs-accent-light)', fontSize: '0.95rem'}}>
              More demos
            </Link>
          </p>
        </div>

        {/* Stats */}
        <StatGrid
          columns={4}
          stats={[
            {value: `${guestkit.diskFormats} Formats`, label: 'Disk Support'},
            {value: `${guestkit.inspectionProfiles} Profiles`, label: 'Inspection Modes'},
            {value: `${guestkit.tuiViews} Views`, label: 'TUI Dashboard'},
            {value: String(guestkit.shellCommands), label: 'REPL Commands'},
          ]}
        />

        <ProductConceptSections productId="guestkit" />

        <SuiteProductCapabilities productId="guestkit" />

        {/* What It Does */}
        <SectionHeader
          eyebrow="Deep Inspection"
          title="See Inside Any VM Disk"
          subtitle="Inspect partitions, filesystems, bootloaders, and network configuration -- all without booting the VM."
        />

        <BentoGrid
          items={[
            {
              title: 'Partition & filesystem analysis',
              desc: 'Detect partition tables, filesystem types, and disk layout across all major formats instantly.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Bootloader inspection',
              desc: 'GRUB, systemd-boot, and Windows Boot Manager — catch misconfigurations before boot failures.',
            },
            {
              title: 'Network & OS config',
              desc: 'Extract interfaces, hostname, DNS, and OS release from disk without starting a VM.',
            },
          ]}
        />

        {/* AI Diagnostics */}
        <SectionHeader
          eyebrow="AI-Powered"
          title={'Ask "Why Won\'t This Boot?"'}
          subtitle="Optional AI diagnostics analyze disk state and provide actionable fix plans. Export remediation as bash scripts or Ansible playbooks."
        />

        <FeaturePanels
          panels={[
            {
              title: 'Intelligent Diagnostics',
              items: [
                'Root cause analysis for boot failures',
                'Missing driver and module detection',
                'Filesystem corruption identification',
                'Configuration drift analysis',
              ],
            },
            {
              title: 'Actionable Fix Plans',
              accent: true,
              items: [
                'Export fixes as bash or Ansible',
                'Automated fstab/crypttab rewriting',
                'Security hardening recommendations',
                'Migration-ready configuration patches',
              ],
            },
          ]}
        />

        {/* Live guest agent */}
        <SectionHeader
          eyebrow="Live guest intelligence"
          title="The same engine, now inside the running guest"
          subtitle="GuestKit also ships as an in-guest agent -- zyvor-guest-agent -- that speaks JSON-RPC over virtio-serial and is wire-compatible with the QEMU Guest Agent. It reuses the offline evidence schema and fix-plan format, so live and offline assurance stay in sync."
        />

        <BentoGrid
          items={[
            {
              title: 'JSON-RPC over virtio-serial',
              desc: 'guestkit agent --channel virtio talks to the host over org.qemu.guest_agent.0 with length-prefixed JSON-RPC 2.0 -- and answers QGA guest-ping, guest-exec, and fsfreeze on the same channel for KubeVirt compatibility.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Deep Linux collectors',
              desc: 'systemd D-Bus units and boot timestamps, journald with cursor tracking, /proc process and cgroup data, and PSI pressure from /proc/pressure -- no extra tooling inside the guest.',
            },
            {
              title: 'Scored GuestHealth',
              desc: 'Component scores for boot, systemd, network, DNS, storage, security, and agent -- plus a numeric score, reasons, and per-failed-unit journal correlation.',
            },
          ]}
        />

        {/* Guest Control Fabric */}
        <SectionHeader
          eyebrow="Guest Control Fabric"
          title="Transport-independent guest control"
          subtitle="Zyvor never assumes the guest has a network. A transport ladder picks the best available path per VM and per operation, and every pull records which tiers were attempted."
        />

        <FeaturePanels
          panels={[
            {
              title: 'Seven-tier transport ladder',
              items: [
                'virtio-serial agent daemon, then QGA guest-exec RPC',
                'QGA built-ins: ping, file I/O, freeze and thaw',
                'In-guest socket probe and HTTPS push cache',
                'Offline-disk repair for halted VMs on the root PVC',
                'Console-only fallback: a structured error with next steps',
              ],
            },
            {
              title: 'Capability contract & airgap install',
              accent: true,
              items: [
                'Control states: full_agent, airgap_live, qga_only, disk_only, console_only, blind_vm',
                'Negotiated capabilities for network, QGA, agent, exec, freeze, and telemetry',
                'Airgap bootstrap writes the agent tarball via QGA guest-file-write -- no curl in the guest',
                'Host-mediated polling for airgap_live VMs with no push heartbeat',
              ],
            },
          ]}
        />

        {/* KubeVirt & Zeus VM Tools */}
        <SectionHeader
          eyebrow="KubeVirt & Zeus OS"
          title="VMware Tools for KubeVirt, without libguestfs"
          subtitle="In-cluster, zyvor-api exposes offline boot-inspect for stopped VMs plus a fleet of guest-tools install paths -- all pure Rust, with no libguestfs, guestfish, or virt-inspector required."
        />

        <BentoGrid
          items={[
            {
              title: 'Offline boot-inspect for stopped VMs',
              desc: "Resolves the root PVC from the VM spec, locates the disk on the node, and runs GuestKit's offline boot-inspect to report OS release, fstab validity, bootloader, and cloud-init presence for Zeus OS Guest Intelligence.",
              span: 'wide',
              accent: true,
            },
            {
              title: 'Five install paths',
              desc: 'Cloud-init, live QGA bootstrap, airgap QGA file bootstrap, ISO attach via CDI, or offline injection with guestkit repair --inject-agent.',
            },
            {
              title: 'Policy-driven fleet coverage',
              desc: 'CRDs -- VMToolsBundle, VMGuestAgent, VMToolsPolicy, GuestActionPolicy -- drive auto-install and auto-upgrade reconcile, JIT approval for exec and remediation, and live fleet coverage.',
            },
          ]}
        />

        {/* Integration */}
        <div style={{textAlign: 'center'}}>
          <SectionHeader
            eyebrow="Integration"
            title="Part of the HyperSDK Platform Ecosystem"
            subtitle="GuestKit feeds directly into the migration pipeline. Inspect first, fix second, deploy third."
          />
          <IntegrationDiagram
            content={`GuestKit          hyper2kvm           HyperSDK Platform
  Inspect disks \u2192   Fix & convert    \u2192   Deploy anywhere
  AI diagnostics    VirtIO injection      ${platform.cloudProviders} providers
  6 formats         Guest OS repair       REST API`}
          />
        </div>

        <ProductReadingPathStrip productId="guestkit" />
        <ClientPresentationSection productId="guestkit" />
        <SuiteProductFooter
          productId="guestkit"
          ctaTitle="Ready to see inside your VM disks?"
          ctaSubtitle="See how GuestKit gives your team deep disk intelligence with AI-powered diagnostics and actionable fix plans."
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
