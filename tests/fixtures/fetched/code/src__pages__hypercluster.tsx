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
  BentoGrid,
  PillGroup,
  styles,
  SuiteProductFooter,
} from '../components/shared';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {hypercluster} from '../data/platform-stats';

const HC_VERSION = '0.1.0';
const HC_PKG_URL = `https://github.com/hypersdk/hypercluster/releases/download/v${HC_VERSION}/Hypercluster-${HC_VERSION}.pkg`;
const HC_PKG_SIZE = '6.9 MB';

function DownloadSection(): ReactNode {
  return (
    <div id="download" style={{scrollMarginTop: '80px'}}>
      <SectionHeader
        eyebrow="Download"
        title="30-Day Free Trial — Apple Silicon"
        subtitle={`Hypercluster Desktop ${HC_VERSION} for macOS 13 Ventura or later · Apple Silicon (M-series) · ${HC_PKG_SIZE}`}
      />
      <div style={{textAlign: 'center', marginBottom: '24px'}}>
        <a
          href={HC_PKG_URL}
          download
          style={{
            display: 'inline-block',
            padding: '14px 32px',
            background: 'linear-gradient(135deg, #f0583a, #ff8a3d)',
            color: '#fff',
            borderRadius: '12px',
            fontWeight: 700,
            fontSize: '16px',
            textDecoration: 'none',
            letterSpacing: '0.01em',
            boxShadow: '0 4px 20px rgba(240,88,58,0.35)',
          }}
        >
          ↓ Download Hypercluster {HC_VERSION}.pkg ({HC_PKG_SIZE})
        </a>
        <p style={{marginTop: '10px', fontSize: '13px', color: '#9ca3af'}}>
          macOS 13 Ventura or later · Apple Silicon only · No login required
        </p>
      </div>
      <BentoGrid
        items={[
          {
            title: '30-day full access',
            desc: 'All features unlocked during the trial — cluster deploy, scale, upgrade, preflight checks, AI insights, kubeconfig delivery.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'Installs to /Applications',
            desc: `Double-click Hypercluster-${HC_VERSION}.pkg. macOS Installer handles everything including the bundled CLI runtime.`,
          },
          {
            title: 'Uninstall cleanly',
            desc: 'Run Uninstall-Hypercluster.command (in the distribution folder) or drag Hypercluster.app to Trash. Trial record is kept in Keychain.',
          },
          {
            title: 'After the trial — get a licence key',
            desc: 'Email sales@zyvor.dev with your team size and use case. We send a licence key by return. Per-seat and team plans available.',
          },
        ]}
      />
      <div style={{marginTop: '16px', textAlign: 'center'}}>
        <PillGroup
          items={[
            'macOS 13 Ventura+',
            'Apple Silicon only',
            'SSH to cluster nodes',
            'Allow in System Settings › Privacy if Gatekeeper warns',
          ]}
        />
      </div>
    </div>
  );
}

export default function HyperCluster(): ReactNode {
  return (
    <ProductPage
      themeId="hypercluster"
      title="HyperCluster — Kubernetes Cluster Lifecycle"
      description="Deploy and operate production Kubernetes clusters with Kubespray, Podman runtime, and SSH-native automation. Preflight, deploy, scale, upgrade, and kubeconfig delivery from one config file."
    >
      <PageHero
        themeId="hypercluster"
        variant="split"
        eyebrow="Product"
        gradientWord="HyperCluster"
        title=""
        subtitle="Kubernetes Cluster Lifecycle"
        description="Deploy and upgrade production clusters with Kubespray — config, inventory, and kubeconfig in one workflow."
        primaryCta={{
          label: 'Download Free Trial',
          to: `https://github.com/hypersdk/hypercluster/releases/download/v${HC_VERSION}/Hypercluster-${HC_VERSION}.pkg`,
        }}
        secondaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
      />

      <PageContent>
        <StatGrid
          columns={4}
          stats={[
            {value: String(hypercluster.cliCommands), label: 'CLI Commands'},
            {value: 'Podman', label: 'Default Runtime'},
            {value: hypercluster.kubesprayVersion, label: 'Kubespray'},
            {value: 'SSH', label: 'Node Access'},
          ]}
        />

        <ProductConceptSections productId="hypercluster" />

        <SectionHeader
          eyebrow="How it works"
          title="One config file drives the full lifecycle"
          subtitle="hypercluster does not replace Kubernetes — it orchestrates proven Kubespray playbooks around your inventory."
        />

        <IntegrationDiagram
          content={`cluster.conf  →  hypercluster  →  Kubespray (Ansible)  →  nodes via SSH
                    │
                    ├─ clones .kubespray/ at pinned version
                    ├─ generates hosts.yaml + group_vars
                    ├─ cluster.yml · scale.yml · upgrade_cluster.yml
                    └─ fetches kubeconfig to your laptop`}
        />

        <BentoGrid
          items={[
            {
              title: 'Preflight checks',
              desc: 'Validate Ansible, Python modules (jinja2, netaddr), SSH keys, and connectivity before any playbook runs.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Deploy & init',
              desc: 'Clone Kubespray, render inventory from CONTROL_PLANE_IPS and WORKER_IPS, deploy the control plane, and pull admin.conf locally.',
            },
            {
              title: 'CNI & add-ons',
              desc: 'Choose Calico, Cilium, Flannel, or kube-ovn; enable metrics-server, ingress-nginx, or dashboard from cluster.conf.',
            },
            {
              title: 'CIDR-safe planning',
              desc: 'Documented pod and service subnet guidance so node networks never overlap Kubernetes allocations.',
            },
            {
              title: 'macOS Desktop app',
              desc: 'Hypercluster Desktop for Apple Silicon — 30-day free trial, download below. CLI deploy scripts also run from macOS and Linux laptops.',
            },
            {
              title: 'Suite foundation',
              desc: 'Bootstrap the Kubernetes substrate for Zeus OS, Veyron, PacketWolf, Forge, and IronWolf — export and convert first, cluster second.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="hypercluster" />

        <SectionHeader
          eyebrow="Virtualization platform"
          title="The k3s path installs a turnkey KubeVirt stack"
          subtitle="Set K8S_DISTRO=k3s and hypercluster deploy lays down the full virtualization platform in one run — no cluster of Helm commands to babysit."
        />

        <BentoGrid
          items={[
            {
              title: 'Cilium, kube-proxy-free',
              desc: 'k3s comes up with Flannel, kube-proxy, Traefik, and servicelb disabled; Cilium replaces kube-proxy and carries the CNI — with optional Hubble, BGP, Gateway API, and WireGuard encryption from cluster.conf.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'MetalLB LoadBalancer',
              desc: 'Bare-metal Services of type LoadBalancer get real IPs from METALLB_IP_POOL — no cloud LB required.',
            },
            {
              title: 'cert-manager',
              desc: 'Installed and health-gated so webhook certificates are ready before KubeVirt and CDI land.',
            },
            {
              title: 'KubeVirt + CDI',
              desc: 'KubeVirt operator and the Containerized Data Importer install and reconcile automatically — run VMs as pods with disk import from day one.',
            },
            {
              title: 'CNAO, snapshot & CSI',
              desc: 'Optional Cluster Network Addons Operator, snapshot-controller, and the KubeVirt CSI driver toggle on from cluster.conf for multi-network VMs and volume snapshots.',
            },
            {
              title: 'Single-node lab tuning',
              desc: 'lab storage mounts a secondary disk into a StorageClass; lab tune scales HA replicas down (and --restore back) so the whole stack fits one box.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Distribution engines"
          title="One CLI, five Kubernetes distributions"
          subtitle="The same cluster.conf and lifecycle commands drive whichever engine fits the site — Kubespray for production HA, k3s for KubeVirt labs, and three more."
        />

        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Kubespray (kubeadm)',
              desc: 'The default: upstream Kubernetes via pinned Kubespray Ansible playbooks with generated inventory and group_vars.',
            },
            {
              title: 'k3s',
              desc: 'Lightweight single-binary Kubernetes for KubeVirt labs and edge — bundled with the turnkey platform stack above.',
            },
            {
              title: 'RKE2',
              desc: 'Rancher’s hardened distribution across servers and agents, with the optional platform stack layered on after.',
            },
            {
              title: 'MicroK8s',
              desc: 'Snap-based install and node join for quick Ubuntu clusters.',
            },
            {
              title: 'Talos',
              desc: 'Immutable, API-managed OS path for locked-down nodes.',
            },
            {
              title: 'Same day-2, every engine',
              desc: 'preflight, deploy, kubeconfig fetch, and destroy behave the same regardless of K8S_DISTRO.',
            },
          ]}
        />

        <div style={{marginTop: '16px', textAlign: 'center'}}>
          <PillGroup items={['K8S_DISTRO=kubespray', 'k3s', 'rke2', 'microk8s', 'talos']} />
        </div>

        <SectionHeader
          eyebrow="Discover & hand off"
          title="Build the inventory, then hand the cluster to Forge"
          subtitle="Find nodes before you deploy, watch them after, and emit a structured payload the rest of the suite can import."
        />

        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Infrastructure discovery',
              desc: 'hypercluster discover enumerates candidate nodes from libvirt, Proxmox, VMware, an SSH CIDR scan, or a CSV — with optional SSH validation and --json for tooling.',
            },
            {
              title: 'JSON-native day-2',
              desc: 'status, health, vms, and workloads all speak --json; health --with-test runs the k3s platform smoke tests, and vms lists KubeVirt VMs plus the template catalog.',
            },
            {
              title: 'Forge Day-2 handoff',
              desc: 'forge-handoff --json emits cluster name, API endpoint, kubeconfig path, and detected stack components (Cilium, MetalLB, KubeVirt…) so Forge can import the cluster for Day-2 operations.',
            },
          ]}
        />

        <DownloadSection />

        <p
          className={styles.featureCardDesc}
          style={{
            textAlign: 'center',
            maxWidth: '36rem',
            margin: '0 auto 4rem',
          }}
        >
          Community Edition scope and proprietary licensing are documented under{' '}
          <Link to="/docs/products#community-edition">Product suite → Community Edition</Link> and{' '}
          <Link to="/docs/licensing">Licensing overview</Link>. Enterprise programs add supported releases and SLAs —{' '}
          <Link to="/pricing">compare plans</Link> or <Link to="/contact?intent=demo">book a demo</Link>.
        </p>

        <ClientPresentationSection productId="hypercluster" />
        <SuiteProductFooter
          productId="hypercluster"
          ctaTitle="Ready to standardize cluster bring-up?"
          ctaSubtitle="See how HyperCluster pairs with the migration and KubeVirt products in your VMware exit or private-cloud program."
          secondaryCta={{label: 'View pricing', to: '/pricing'}}
        />
      </PageContent>
    </ProductPage>
  );
}
