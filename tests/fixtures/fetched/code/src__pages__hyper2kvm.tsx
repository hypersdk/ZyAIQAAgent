// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {
  ProductPage,
  PageHero,
  PageContent,
  SectionHeader,
  FeatureGrid,
  FeaturePanels,
  CommunityEditionCallout,
  BentoGrid,
  styles,
  SuiteProductFooter,
} from '../components/shared';
import {hyper2kvm} from '../data/platform-stats';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {ProductReadingPathStrip} from '../components/ProductReadingPathStrip';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';

export default function Hyper2KVM(): ReactNode {
  return (
    <ProductPage
      themeId="hyper2kvm"
      title="hyper2kvm Engine"
      description="Convert VMs from any hypervisor to KVM with automated guest fixing and validation."
    >
      <PageHero
        themeId="hyper2kvm"
        variant="split"
        badge="Production Ready"
        gradientWord="hyper2kvm"
        title="Engine"
        subtitle="Any Hypervisor → KVM Migration"
        description="Convert any hypervisor format to KVM with automated guest OS fixing and production-safe validation."
        primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
        secondaryCta={{
          label: 'Download PDF deck',
          to: 'pathname:///presentations/client/hyper2kvm/hyper2kvm-client.pdf',
          staticAsset: true,
        }}
      />

      <PageContent>
        <CommunityEditionCallout />

        <ProductConceptSections productId="hyper2kvm" />

        <BentoGrid
          items={[
            {
              title: 'Pure Python engine',
              desc: 'Complete VM manipulation without external dependencies — no agents or cloud APIs during conversion.',
              span: 'wide',
              accent: true,
            },
            {
              title: '5–7× faster',
              desc: 'Optimized pipeline vs libguestfs-style tooling for large batch conversions.',
            },
            {
              title: 'Works offline',
              desc: 'Pre-packaged for air-gapped sites — no registry or package manager required.',
            },
            {
              title: 'OpenStack Glance deploy',
              desc: 'Upload converted QCOW2 to Glance with openstacksdk; optional Nova boot — mutually exclusive with KubeVirt on the same job.',
            },
          ]}
        />

        {/* Supported Operating Systems */}
        <SectionHeader
          eyebrow="Supported Operating Systems"
          title={`${hyper2kvm.osVersions} OS Versions. Handled Automatically.`}
          subtitle="We detect the operating system and apply the correct fixes automatically. No manual intervention required."
        />

        <FeaturePanels
          panels={[
            {
              title: 'Windows',
              items: [
                'Windows Server 2016-2025, Windows 10/11, and legacy Server 2008 R2 / 2012 R2.',
                'We handle driver compatibility and boot configuration automatically.',
              ],
            },
            {
              title: 'Linux',
              accent: true,
              items: [
                'RHEL, CentOS, Ubuntu, Debian, SUSE, Fedora, Rocky, Alma, Oracle Linux, Arch, Alpine, and more.',
                '25+ distributions with automated bootloader and network reconfiguration.',
              ],
            },
          ]}
        />

        {/* Host-Safe Namespace Isolation */}
        <SectionHeader
          eyebrow="Host-Safe by Design"
          title="Convert Without Touching the Host"
          subtitle="Guest fixes run inside a Linux namespace, so a converter that reads a stranger's disk can never reach the machine it runs on."
        />

        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Namespace isolation',
              desc: 'Each conversion runs under unshare --mount --pid --fork, so guest disks live in a private mount and PID namespace — host processes are never in scope.',
            },
            {
              title: 'Private /dev + LVM filter',
              desc: 'A tmpfs /dev exposes only the guest NBD device, and an LVM device filter (a|nbd0.*|, r|.*|) makes activating a host volume group physically impossible.',
            },
            {
              title: 'Copy-on-write overlay',
              desc: 'OverlayFS layers the guest root read-only beneath a writable upper dir, so fixes apply in an isolated workspace and unwind cleanly if a stage fails.',
            },
            {
              title: 'Crash-safe cleanup',
              desc: 'Teardown releases the NBD backend, deactivates the guest VG, and unmounts overlays even when a conversion aborts — no leaked mounts or devices.',
            },
          ]}
        />

        {/* Distributed Worker Fleet */}
        <SectionHeader
          eyebrow="Scale-Out Migrations"
          title="A Distributed Worker Fleet"
          subtitle="Run hundreds of conversions across a Kubernetes worker pool with a job protocol built for reliability."
        />

        <BentoGrid
          items={[
            {
              title: 'REST + CRD job protocol',
              desc: 'Submit and track migrations over an HTTP job API or native Kubernetes MigrationJob resources. A formal state machine drives every job: validated → queued → assigned → running → completed.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Capability-aware scheduling',
              desc: 'Workers advertise a tier — userspace-only, NBD inspection, or full offline fixes — so a job only lands on a node that can actually run it.',
            },
            {
              title: 'Automatic retries',
              desc: 'Exponential-backoff retry with a retrying → queued loop keeps transient failures from killing a large batch.',
            },
            {
              title: 'Priority + DAG dependencies',
              desc: 'High-priority jobs jump the queue, and jobs can depend on other jobs for staged, multi-VM cutovers.',
            },
            {
              title: 'Live progress events',
              desc: 'Per-job progress is streamed as real-time events and exported to Prometheus, so long batches stay observable end to end.',
            },
          ]}
        />

        {/* Daemon / Watch-Folder Automation */}
        <SectionHeader
          eyebrow="Hands-Off Automation"
          title="Drop a Disk, Get a Bootable VM"
          subtitle="Run hyper2kvm as a systemd service that watches a directory and converts anything dropped into it."
        />

        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Watch-folder pipeline',
              desc: 'A filesystem watcher detects new disks the moment they land and runs the full convert-and-fix pipeline unattended — ideal for overnight batches.',
            },
            {
              title: 'Format auto-detection',
              desc: 'The file extension selects the source path automatically: .vmdk, .ova/.ovf, .vhd/.vhdx, .raw/.img, and .ami.',
            },
            {
              title: 'Safe intake',
              desc: 'Each file is checked for write-stability before processing and deduplicated, then archived once its run completes successfully.',
            },
            {
              title: 'Runs as a service',
              desc: 'Ships as a systemd unit with automatic restart, so a drop-folder becomes a durable part of an export → convert → deploy pipeline.',
            },
          ]}
        />

        {/* Comparison */}
        <SectionHeader
          eyebrow="Comparison"
          title="How hyper2kvm Compares"
          subtitle="See how hyper2kvm stacks up against other VM migration and conversion tools."
        />

        <div
          style={{
            background: 'rgba(18, 18, 18, 0.6)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: 16,
            overflow: 'hidden',
            marginBottom: '4rem',
            overflowX: 'auto',
          }}
        >
          {/* Header */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr repeat(4, 120px)',
              background: 'rgba(255, 140, 0, 0.08)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
              padding: '1rem 1.5rem',
              alignItems: 'center',
              minWidth: 700,
            }}
          >
            <div className={styles.monoLabel} style={{marginBottom: 0, color: 'var(--hs-text-muted)'}}>
              Feature
            </div>
            {['hyper2kvm', 'virt-v2v', 'Forklift', 'CloudEndure'].map((h, i) => (
              <div
                key={h}
                className={styles.monoLabel}
                style={{
                  marginBottom: 0,
                  color: i === 0 ? '#f47a60' : '#94a3b8',
                  fontWeight: i === 0 ? 700 : 600,
                  textAlign: 'center',
                }}
              >
                {h}
              </div>
            ))}
          </div>

          {/* Rows */}
          {(
            [
              {
                feature: 'First-boot success',
                values: [hyper2kvm.firstBootSuccess, '~70%', '~80%', '~85%'],
                winner: true,
              },
              {feature: 'Windows support', values: ['Full (VirtIO auto-inject)', 'Limited', 'Basic', 'Full']},
              {feature: 'Offline fixes', values: ['7-stage pipeline', 'Basic', 'None', 'None'], winner: true},
              {feature: 'KubeVirt deploy', values: ['Built-in', 'Manual', 'Built-in', 'No']},
              {feature: 'OpenStack Glance', values: ['Built-in', 'No', 'No', 'No'], winner: true},
              {
                feature: 'Web dashboard',
                values: [`${hyper2kvm.dashboardApis} h2kweb APIs`, 'CLI only', 'Web UI', 'Web UI'],
                winner: true,
              },
              {feature: 'LVM/LUKS support', values: ['Auto-detect', 'Manual', 'No', 'No'], winner: true},
              {feature: 'Air-gap support', values: ['Full', 'Partial', 'No', 'No'], winner: true},
              {
                feature: 'Pure Python engine',
                values: ['Yes (VMCraft)', 'libguestfs', 'Go', 'Proprietary'],
                winner: true,
              },
            ] as {feature: string; values: string[]; winner?: boolean}[]
          ).map((row, i, arr) => (
            <div
              key={row.feature}
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr repeat(4, 120px)',
                borderBottom: i < arr.length - 1 ? '1px solid rgba(255, 255, 255, 0.04)' : 'none',
                padding: '0.75rem 1.5rem',
                alignItems: 'center',
                background: row.winner ? 'rgba(255, 140, 0, 0.04)' : 'transparent',
                minWidth: 700,
              }}
            >
              <div
                style={{
                  color: 'var(--hs-text-body)',
                  fontSize: '0.9rem',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                {row.feature}
              </div>
              {row.values.map((val, j) => (
                <div
                  key={`${row.feature}-${j}`}
                  style={{
                    textAlign: 'center',
                    fontSize: '0.8rem',
                    color:
                      j === 0
                        ? '#f47a60'
                        : val === 'No' ||
                            val === 'None' ||
                            val === 'Limited' ||
                            val === 'Basic' ||
                            val === 'CLI only' ||
                            val === 'Manual' ||
                            val === 'Partial'
                          ? '#525252'
                          : '#94a3b8',
                    fontWeight: j === 0 ? 600 : 400,
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  {val}
                </div>
              ))}
            </div>
          ))}
        </div>

        <SuiteProductCapabilities productId="hyper2kvm" />

        <ProductReadingPathStrip productId="hyper2kvm" />
        <ClientPresentationSection productId="hyper2kvm" />
        <SuiteProductFooter
          productId="hyper2kvm"
          ctaTitle="Ready to migrate your VMs to KVM?"
          ctaSubtitle="Talk to our team to see how hyper2kvm can convert your virtual machines with zero downtime."
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
