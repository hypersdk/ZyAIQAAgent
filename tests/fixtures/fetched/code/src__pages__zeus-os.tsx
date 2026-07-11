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
  FeaturePanels,
  IntegrationDiagram,
  BentoGrid,
  CodePanel,
  styles,
  SuiteProductFooter,
} from '../components/shared';
import {v9s, platform} from '../data/platform-stats';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {ProductReadingPathStrip} from '../components/ProductReadingPathStrip';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';

function TrialSection(): ReactNode {
  return (
    <div id="trial" style={{scrollMarginTop: '80px'}}>
      <SectionHeader
        eyebrow="30-Day Free Trial"
        title="Install in 30 Seconds — No Sign-Up Required"
        subtitle="Build date is baked into the binary. The 30-day trial starts on install — no account, no credit card."
      />

      {/* Step 1 */}
      <div style={{marginBottom: '2rem'}}>
        <p
          style={{
            fontSize: '13px',
            fontWeight: 700,
            color: '#7c3aed',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '8px',
            textAlign: 'left',
          }}
        >
          Step 1 — Install
        </p>
        <CodePanel label="Install Zeus OS">{`helm install zeus-os oci://ghcr.io/hypersdk/charts/zeus-os \\
  --version 0.2.0 \\
  --namespace zeus-os-system --create-namespace`}</CodePanel>
      </div>

      {/* Step 2 */}
      <div style={{marginBottom: '2rem'}}>
        <p
          style={{
            fontSize: '13px',
            fontWeight: 700,
            color: '#7c3aed',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '8px',
            textAlign: 'left',
          }}
        >
          Step 2 — Verify pods are running
        </p>
        <CodePanel label="kubectl">{`kubectl rollout status deployment/zeus-os \\
  -n zeus-os --timeout=120s

kubectl get pods -n zeus-os
# NAME                  READY   STATUS    AGE
# zeus-os-xxxx          1/1     Running   40s`}</CodePanel>
      </div>

      {/* Step 3 */}
      <div style={{marginBottom: '2rem'}}>
        <p
          style={{
            fontSize: '13px',
            fontWeight: 700,
            color: '#7c3aed',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '8px',
            textAlign: 'left',
          }}
        >
          Step 3 — Open the dashboard
        </p>
        <CodePanel label="port-forward">{`# Via NodePort (if node IP is reachable):
open http://<node-ip>:30050

# Or port-forward:
kubectl port-forward svc/zeus-os -n zeus-os 5050:5050

# Open: http://localhost:5050`}</CodePanel>
      </div>

      {/* Step 4 */}
      <div style={{marginBottom: '2rem'}}>
        <p
          style={{
            fontSize: '13px',
            fontWeight: 700,
            color: '#7c3aed',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '8px',
            textAlign: 'left',
          }}
        >
          Step 4 — Confirm trial is active
        </p>
        <CodePanel label="logs">{`kubectl logs -n zeus-os deployment/zeus-os \\
  | grep -i 'trial\\|licence'
# → Zeus OS licence: Trial — valid until YYYY-MM-DD`}</CodePanel>
      </div>

      {/* Step 5 */}
      <div style={{marginBottom: '2rem'}}>
        <p
          style={{
            fontSize: '13px',
            fontWeight: 700,
            color: '#7c3aed',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '8px',
            textAlign: 'left',
          }}
        >
          Step 5 — Apply a licence key (after trial)
        </p>
        <CodePanel label="helm upgrade">{`helm upgrade zeus-os oci://ghcr.io/hypersdk/charts/zeus-os \\
  --version 0.2.0 --reuse-values \\
  --set license.key="<your-key>" \\
  -n zeus-os`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: 'Full platform, zero sign-up',
            desc: 'Web dashboard, Ratatui TUI, 48+ views, VM lifecycle, live consoles, cost analytics, incident war-room — all active from the first helm install.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'OCI registry delivery',
            desc: 'No helm repo add needed. Pull directly from oci://ghcr.io/hypersdk/charts. Runs on any Kubernetes 1.31+ cluster with KubeVirt.',
          },
          {
            title: 'Automatic trial clock',
            desc: 'Build date is baked into the binary at compile time. Trial window is 30 days — no phone-home, no daemon, no usage tracking.',
          },
          {
            title: 'After the trial',
            desc: 'Contact sales@zyvor.dev for a licence key. Apply with --set license.key=... on helm upgrade — zero downtime.',
          },
        ]}
      />
    </div>
  );
}

export default function ZeusOSPage(): ReactNode {
  return (
    <ProductPage
      themeId="zeus-os"
      title="Zeus OS — Visual Infrastructure Operating System"
      description="Manage Kubernetes, KubeVirt VMs, migrations, network topology, and incident response from a single control plane. Web dashboard and Rust TUI."
    >
      <PageHero
        themeId="zeus-os"
        variant="split"
        badge="KubeVirt manage"
        gradientWord="Zeus"
        title="OS"
        subtitle="Visual Infrastructure Operating System"
        description="Manage Kubernetes, KubeVirt VMs, migrations, network topology, and incident response from a single control plane."
        primaryCta={{label: 'Install Free Trial', to: '/docs/zeus-os#installation'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/zeus-os#installation'}}
      />

      <PageContent>
        <StatGrid
          columns={4}
          stats={[
            {value: `${v9s.tuiViews} TUI`, label: 'Terminal Views'},
            {value: String(v9s.apiModules), label: 'API Modules'},
            {value: String(v9s.webComponents), label: 'React Components'},
            {value: String(v9s.uiViews), label: 'Web UI Views'},
          ]}
        />

        <ProductConceptSections productId="zeus-os" />

        <SectionHeader
          eyebrow="Two Interfaces"
          title="Choose How You Work"
          subtitle="Whether you prefer the terminal or the browser, Zeus OS meets you where you are."
        />

        <FeaturePanels
          panels={[
            {
              title: 'Terminal UI',
              items: [
                'Keyboard-driven navigation, k9s-style',
                'SSH-friendly — manage VMs from any terminal',
                'Instant response with zero browser overhead',
                'Full VM lifecycle control from the command line',
              ],
            },
            {
              title: 'Web Dashboard',
              accent: true,
              items: [
                'Built with React 19 for a modern experience',
                'Real-time updates across all connected clients',
                'Visual VM management with drag-and-drop',
                'Rich charts and resource monitoring',
              ],
            },
          ]}
        />

        <SectionHeader eyebrow="Capabilities" title="What You Can Do" />

        <BentoGrid
          items={[
            {
              title: 'VM Lifecycle',
              desc: 'List, create, start, stop, restart, and delete virtual machines on KubeVirt with a single keystroke or click.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Live Logs & Console',
              desc: 'Stream live logs and access VNC console directly from the TUI or browser. No kubectl required.',
            },
            {
              title: 'Resource Monitoring',
              desc: 'Real-time CPU, memory, and storage metrics for every VM. Spot issues before they become incidents.',
            },
          ]}
        />

        <div style={{textAlign: 'center'}}>
          <SectionHeader
            eyebrow="Integration"
            title="Part of the Zeus OS Suite"
            subtitle="Zeus OS works alongside HyperSDK Platform, hyper2kvm, and GuestKit to deliver the full VM lifecycle."
          />
          <IntegrationDiagram
            content={`HyperSDK Platform          hyper2kvm           Zeus OS
  Export VMs   \u2192   Convert to KVM   \u2192   Day-2 on K8s
  ${platform.cloudProviders} providers     VirtIO injection      Web + TUI
  REST API         Guest OS fixing       Real-time`}
          />
        </div>

        <SectionHeader
          eyebrow="Comparison"
          title="How Zeus OS Compares"
          subtitle="See how Zeus OS stacks up against other VM and Kubernetes management tools."
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
            {['Zeus OS', 'kubectl', 'virt-manager', 'Cockpit'].map((h, i) => (
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

          {(
            [
              {feature: 'KubeVirt VMs', values: [true, 'Manual YAML', false, false], winner: true},
              {feature: 'Libvirt VMs', values: [true, false, true, true]},
              {feature: 'Real-time stats', values: [true, false, true, true]},
              {feature: 'Multi-cluster', values: [true, 'Context switch', false, false], winner: true},
              {feature: 'Keyboard-driven', values: [true, true, false, false]},
              {feature: 'Hardware editing', values: [true, 'Manual YAML', true, 'Limited']},
              {feature: 'Batch operations', values: [true, 'With scripts', false, false], winner: true},
              {feature: 'GPU passthrough', values: [true, 'Manual', true, false], winner: true},
            ] as {feature: string; values: (boolean | string)[]; winner?: boolean}[]
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
              <div style={{color: 'var(--hs-text-body)', fontSize: '0.9rem', fontWeight: 500}}>{row.feature}</div>
              {row.values.map((val, j) => (
                <div
                  key={`${row.feature}-${j}`}
                  style={{
                    textAlign: 'center',
                    fontSize: typeof val === 'string' ? '0.8rem' : '1.1rem',
                    color: j === 0 ? '#f47a60' : val === true ? '#22c55e' : val === false ? '#525252' : '#94a3b8',
                    fontFamily: typeof val === 'string' ? "'JetBrains Mono', monospace" : undefined,
                    fontWeight: j === 0 ? 600 : 400,
                  }}
                >
                  {typeof val === 'boolean' ? (val ? '\u2713' : '\u2717') : val}
                </div>
              ))}
            </div>
          ))}
        </div>

        <SectionHeader
          eyebrow="Self-Service VMs"
          title="Template Marketplace & Blueprints"
          subtitle="A golden catalog, parameterized cloud-init, and multi-VM blueprints — deploy production VMs without hand-writing KubeVirt YAML."
        />

        <BentoGrid
          items={[
            {
              title: 'Golden catalog & Marketplace',
              desc: 'Templates are Kubernetes ConfigMaps labeled zeus-os.io/template. Browse the Marketplace, hit Deploy or Customize, or Quick Deploy straight from the golden catalog — no kubectl.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Parameterized cloud-init',
              desc: 'Templates carry a parameters schema and ${VAR} substitution — VM_NAME, NAMESPACE, SSH_AUTHORIZED_KEYS, and custom fields are injected at deploy time. Preview the rendered spec before you commit.',
            },
            {
              title: 'Cloud-init security scan',
              desc: 'Every template is scanned for denied cloud-init directives before it can be saved, so a bad snippet never reaches a running guest.',
            },
            {
              title: 'Governance & versioning',
              desc: 'Templates move through draft → approved → deprecated. Submit for review, approve, list versions, and restore. Drafts are blocked from production namespaces unless explicitly allowed.',
            },
            {
              title: 'Multi-VM blueprints',
              desc: 'Blueprints (label zeus-os.io/blueprint) stamp out whole stacks — a Linux k3s cluster or an AI fleet — substituting parameters into every resource in one deploy.',
            },
            {
              title: 'AI draft & Git-backed sync',
              desc: 'Generate a starter template with AI (always lands as a draft for review), or point Zeus OS at a Git repo and sync your golden templates into the cluster as ConfigMaps.',
            },
          ]}
        />

        <CodePanel label="Template lifecycle — REST API">{`# Render a template with your parameters (dry run)
POST /api/v1/templates/render-preview

# Deploy a golden template into a namespace
POST /api/v1/templates/production/ubuntu-24-04/instantiate

# Governance: submit, approve, roll back
POST /api/v1/templates/production/ubuntu-24-04/submit-review
POST /api/v1/templates/production/ubuntu-24-04/approve
POST /api/v1/templates/production/ubuntu-24-04/restore

# Sync golden templates from Git
POST /api/v1/templates/sync-git`}</CodePanel>

        <SectionHeader
          eyebrow="Visual Shell"
          title="Zeus Desktop & Cinema Consoles"
          subtitle="Not just a dashboard — a macOS-style desktop for infrastructure, with a command palette, a dock, and display-first VM consoles."
        />

        <FeaturePanels
          panels={[
            {
              title: 'Zeus Desktop shell',
              items: [
                'macOS-style shell — top bar, sidebar, dock, and tabbed windows',
                '⌘K command palette (Command Halo) jumps to any center or action',
                'Orbit cards expand from Compact to Comfortable, Theatre, and Focus',
                'Three-plane layout: fixed shell, infinite workspace, and focus studio overlays',
              ],
            },
            {
              title: 'Cinema & Studio consoles',
              accent: true,
              items: [
                'Cinema mode — display-first VNC / RDP / SPICE, hover-reveal controls',
                'Studio mode — split panes with a View Lens bar for power users',
                'Browse mode — fleet inventory plus a live inspector',
                'Your last console mode is remembered per browser and reopened on deep links',
              ],
            },
          ]}
        />

        <SectionHeader
          eyebrow="Golden Images"
          title="Image Factory & Windows Guest Customization"
          subtitle="Bake golden images from running VMs and customize Windows guests — sysprep and AD domain-join without leaving Zeus OS."
        />

        <BentoGrid
          items={[
            {
              title: 'Image Factory pipelines',
              desc: 'Build golden images through staged pipelines you advance step by step, then promote a golden DataVolume so new VMs boot from a hardened, versioned base.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Clone to golden',
              desc: 'Snapshot a prepared VM into a golden PVC and publish it as a zeus-os.io/template ConfigMap — a running machine becomes a reusable, approved template.',
            },
            {
              title: 'Windows sysprep & domain-join',
              desc: 'Generate sysprep unattend answers (JSON or XML) into a ConfigMap and trigger Active Directory domain-join on a Windows VM directly from the API.',
            },
          ]}
        />

        <CodePanel label="Image factory & Windows customization">{`# Golden image pipeline
POST /api/v1/image-factory/pipelines
POST /api/v1/image-factory/pipelines/prod/pipe-01/advance
POST /api/v1/image-factory/promote

# Windows guest customization
POST /api/v1/windows-customization/generate.xml   # sysprep unattend
POST /api/v1/vms/prod/win-2022/domain-join`}</CodePanel>

        <TrialSection />

        <SuiteProductCapabilities productId="zeus-os" />
        <ProductReadingPathStrip productId="zeus-os" />
        <ClientPresentationSection productId="zeus-os" />
        <SuiteProductFooter
          productId="zeus-os"
          ctaTitle="Ready to run Zeus OS on your KubeVirt fleet?"
          ctaSubtitle="See how Zeus OS gives your team a visual infrastructure OS for virtual machine management on Kubernetes — web dashboard and TUI."
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
