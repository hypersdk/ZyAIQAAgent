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
  IntegrationDiagram,
  BentoGrid,
  CodePanel,
  PillGroup,
  styles,
  SuiteProductFooter,
} from '../components/shared';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {ProductReadingPathStrip} from '../components/ProductReadingPathStrip';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import {aether} from '../data/platform-stats';

function TrialSection(): ReactNode {
  return (
    <div style={{padding: '4rem 1.5rem', maxWidth: 860, margin: '0 auto'}}>
      <SectionHeader
        eyebrow="30-Day Free Trial"
        title="Install in 30 Seconds — No Sign-Up Required"
        subtitle="Pull Aether directly from the OCI registry. The trial clock starts from the build date — no account, no email, no sales call."
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
        <CodePanel>{`helm install aether oci://ghcr.io/hypersdk/charts/aether \\
  --version 0.1.0 \\
  --namespace aether-system \\
  --create-namespace`}</CodePanel>
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
        <CodePanel>{`kubectl rollout status deployment/aether \\
  -n aether-system --timeout=120s

kubectl get pods -n aether-system
# NAME                READY   STATUS    AGE
# aether-xxxx         1/1     Running   30s`}</CodePanel>
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
          Step 3 — Access the dashboard
        </p>
        <CodePanel>{`kubectl port-forward svc/aether \\
  -n aether-system 5090:5090

# Open: http://localhost:5090
# Health check:
curl http://localhost:5090/health`}</CodePanel>
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
        <CodePanel>{`kubectl logs -n aether-system deployment/aether \\
  | grep -i 'trial\\|licence'
# → Aether licence: Trial — valid until YYYY-MM-DD`}</CodePanel>
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
        <CodePanel>{`kubectl create secret generic aether-license \\
  --from-literal=license.key="<your-key>" \\
  -n aether-system

helm upgrade aether oci://ghcr.io/hypersdk/charts/aether \\
  --version 0.1.0 --reuse-values \\
  --set license.existingSecret="aether-license" \\
  -n aether-system`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: 'Full Feature Access',
            desc: 'All four runtimes, 16 migration paths, confidential computing, and the full 43-page dashboard — nothing gated.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'Automatic trial clock',
            desc: 'Build date is baked into the binary at compile time. The 30-day window starts then — no account or key required.',
          },
          {
            title: 'Single Helm command',
            desc: 'No helm repo add. Helm 3.8+ pulls from OCI directly. Auto-discovers your cluster on startup.',
          },
          {
            title: 'After the Trial',
            desc: 'Move to a commercial licence with no data loss. Migration history and environment configs carry forward.',
          },
        ]}
      />
    </div>
  );
}

export default function Aether(): ReactNode {
  return (
    <ProductPage
      themeId="aether"
      title="Aether -- Universal Runtime Control Plane"
      description="One spec, four runtimes. Deploy to Podman, Kubernetes, KubeVirt, or bare metal — with confidential computing on SEV-SNP and TDX."
    >
      <PageHero
        themeId="aether"
        variant="split"
        eyebrow="Product"
        gradientWord="Aether"
        title=""
        subtitle="Universal Runtime Control Plane"
        description="One workload spec for containers, VMs, and bare metal — with optional confidential computing."
        primaryCta={{label: 'Install Free Trial', to: '/docs/aether#installation'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/aether'}}
      />

      <PageContent>
        <StatGrid
          stats={[
            {value: String(aether.runtimes), label: 'Runtimes'},
            {value: String(aether.migrationPaths), label: 'Migration Routes'},
            {value: String(aether.strategies), label: 'Deploy Strategies'},
            {value: String(aether.dashboardPages), label: 'Dashboard Pages'},
          ]}
          columns={4}
        />

        <ProductConceptSections productId="aether" />

        <SectionHeader
          eyebrow="Confidential computing"
          title="Hardware-rooted trust in one workload spec"
          subtitle="Declare a confidential block in YAML — Aether wires KubeVirt launch security, Kata RuntimeClasses, attestation verify, and sovereign mode without a separate toolchain."
        />
        <BentoGrid
          items={[
            {
              title: 'KubeVirt confidential VMs',
              desc: 'SEV-SNP or TDX with vTPM, measured images, and strict attestation. Security profiles from sandbox through sovereign-high.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Kata / CoCo pods',
              desc: 'RuntimeClasses for kata-clh-snp, kata-clh-tdx, and GPU SNP — container isolation on the same TEE-capable nodes.',
            },
            {
              title: 'Confidential migration',
              desc: 'confidential-blue-green strategy with re-attestation before cutover — not blind virtctl migrate between TEE nodes.',
            },
            {
              title: 'Composite with Ragnarok',
              desc: 'Run Aether alone or link RAGNAROK_URL for enterprise attestation hub, attest-gated secrets, and fleet trust scores.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Key Capabilities"
          title="Deploy Once, Run Anywhere"
          subtitle="A single workload specification that targets containers, virtual machines, and bare-metal servers with zero rewriting."
        />
        <BentoGrid
          items={[
            {
              title: 'Podman Containers',
              desc: 'Deploy workloads as rootless containers on any Linux host. Full OCI compatibility with Podman pod semantics and systemd integration.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Kubernetes Orchestration',
              desc: 'Target Kubernetes clusters with native resource generation. Deployments, Services, ConfigMaps, and Ingress from the same spec.',
            },
            {
              title: 'KubeVirt Virtual Machines',
              desc: 'Run workloads as full virtual machines on Kubernetes. Bridge legacy applications to cloud-native infrastructure without refactoring.',
            },
            {
              title: 'Metal3 Bare Metal',
              desc: 'Provision and deploy directly to bare-metal servers via Metal3. Eliminate the hypervisor layer for maximum performance and density.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Migration"
          title="Migrate Between Runtimes in Minutes"
          subtitle="Start on Podman for development, promote to Kubernetes for staging, and deploy to bare metal for production -- all without changing your spec."
        />
        <IntegrationDiagram
          content={`Podman           Kubernetes        KubeVirt          Metal3
  Containers  \u2194    Pods & Services \u2194  Virtual Machines \u2194  Bare Metal
  Dev/Test         Staging            Legacy Apps        Max Perf

  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  One Workload Spec  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500`}
        />

        {/* Beyond VMs - custom section */}
        <div
          className={styles.featureCard}
          style={{maxWidth: 900, margin: '0 auto 3rem', padding: '2.5rem', textAlign: 'left'}}
        >
          <span className={styles.sectionEyebrow}>Beyond VMs</span>
          <h3 style={{fontSize: '1.4rem', fontWeight: 700, color: 'var(--hs-text-white)', margin: '0.75rem 0'}}>
            Migrate Code, Containers & Runtime -- Not Just VMs
          </h3>
          <p style={{color: 'var(--hs-text-muted)', lineHeight: 1.75, marginBottom: '1rem'}}>
            Go beyond disk-level conversion. Automatically translate your application stack -- from Docker Compose,
            systemd services, and VM-based workloads -- into Kubernetes-native resources and KubeVirt virtual machines.
          </p>
          <ul
            style={{
              color: 'var(--hs-text-body)',
              fontSize: '0.9rem',
              lineHeight: 1.8,
              paddingLeft: '1.2rem',
              margin: '0 0 1.5rem',
            }}
          >
            <li>Convert Docker Compose → Kubernetes Deployments, Services, and PVCs</li>
            <li>Map systemd services → containerized workloads or init containers</li>
            <li>Preserve environment variables, volumes, networking, and dependencies</li>
            <li>Generate production-ready YAML with sensible defaults</li>
            <li>Optional: keep workloads as VMs using KubeVirt when containers aren't suitable</li>
          </ul>

          {/* Visual flow */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              padding: '1rem',
              background: 'rgba(240,88,58,0.04)',
              borderRadius: 12,
              marginBottom: '1rem',
              flexWrap: 'wrap' as const,
            }}
          >
            {[
              'VM / Compose / systemd',
              '\u2192',
              'Extract',
              '\u2192',
              'Transform',
              '\u2192',
              'K8s YAML / KubeVirt VM',
            ].map((s, i) => (
              <span
                key={`${s}-${i}`}
                style={{
                  fontFamily: s === '\u2192' ? 'inherit' : "'JetBrains Mono', monospace",
                  fontSize: s === '\u2192' ? '1.2rem' : '0.8rem',
                  color: s === '\u2192' ? '#f0583a' : '#d4d4d4',
                  fontWeight: s === '\u2192' ? 400 : 600,
                }}
              >
                {s}
              </span>
            ))}
          </div>

          <p style={{color: 'var(--hs-accent)', fontSize: '0.9rem', fontWeight: 500, margin: 0}}>
            Reduce migration effort from weeks to minutes with automated, deterministic transformations.
          </p>
        </div>

        <SectionHeader
          eyebrow="Extensible runtimes"
          title="Add Your Own Runtime Without Forking Aether"
          subtitle="Beyond the four built-in targets, any external binary can act as a runtime adapter over a JSON-RPC protocol -- drop a manifest, register it, and drive it from the same workload spec."
        />
        <BentoGrid
          items={[
            {
              title: 'Any-language adapters',
              desc: 'Plugins speak JSON-RPC over stdin/stdout, so a runtime adapter can be written in any language. Each manifest declares the operations it supports -- build, run, stop, status -- and Aether routes only advertised capabilities.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Manifest discovery',
              desc: 'Drop a JSON manifest into ~/.aether/plugins/. aether plugin discover scans the directory and register records it in a persistent ~/.aether/plugins.json registry.',
            },
            {
              title: 'Same spec, new target',
              desc: 'Registered plugin runtimes join Podman, Kubernetes, KubeVirt, and Metal3 under one workload spec -- no rewrite to target a custom runtime.',
            },
            {
              title: 'Managed lifecycle',
              desc: 'aether plugin list and remove manage the registry; capability-scoped routing means a plugin is only asked to do what it declared it can.',
            },
          ]}
        />
        <PillGroup
          items={[
            'aether plugin discover',
            'aether plugin register manifest.json',
            'aether plugin list',
            'aether plugin remove <name>',
          ]}
        />

        <SectionHeader
          eyebrow="Always-on control loop"
          title="Detect Drift and Heal It on a Schedule"
          subtitle="A reconciliation daemon runs independent health, drift, and SLA loops, syncs desired state from Git, and reaches out to remote edge sites -- not just a one-shot drift check."
        />
        <BentoGrid
          items={[
            {
              title: 'Reconciliation daemon',
              desc: 'aether orchestrate watch runs health (30s), drift (300s), and SLA (60s) loops with circuit breaking. With auto_reconcile enabled, detected drift is applied back to desired state automatically.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Drift, then reconcile',
              desc: 'aether drift <name> --reconcile applies the field-level diff between running state and the declared spec -- no manual re-apply.',
            },
            {
              title: 'GitOps sync',
              desc: 'Point Aether at a Git repo and branch; aether gitops init / status / sync reconciles workload YAML changes into the control plane.',
            },
            {
              title: 'Edge site agents',
              desc: 'aether edge-agent registers a remote site with a central control plane, drains its reconcile queue, and heartbeats on an interval.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Enterprise governance"
          title="Policy Gates, RBAC, and SSO on Every Deploy"
          subtitle="Deploys pass a policy gate before any runtime sees them, and the API enforces role-based access with optional enterprise single sign-on."
        />
        <BentoGrid
          items={[
            {
              title: 'Policy gate before deploy',
              desc: 'aether policy-check --policy production evaluates resource limits, naming conventions, security requirements, and compliance rules. Violations block the deploy; warnings do not.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'OPA admission',
              desc: 'Point AETHER_OPA_URL at an Open Policy Agent server; with enforce mode on, cluster apply and workload deploy paths reject on a Rego deny.',
            },
            {
              title: 'RBAC API keys',
              desc: 'Admin, Operator, and Viewer roles scope every API endpoint -- full access, workload read/write, or read-only.',
            },
            {
              title: 'OIDC, SAML & LDAP SSO',
              desc: 'Sign in with OpenID Connect (auth code + PKCE), SAML 2.0, or LDAP / Active Directory bind. IdP groups map to roles, with Redis-backed session state across HA replicas.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="aether" />

        <ProductReadingPathStrip productId="aether" />
        <ClientPresentationSection productId="aether" />
        <TrialSection />
        <SuiteProductFooter
          productId="aether"
          ctaTitle="Ready to unify your runtime infrastructure?"
          ctaSubtitle="See how Aether lets your team deploy one spec across containers, virtual machines, and bare-metal servers."
          secondaryCta={{label: 'Read the Docs', to: '/docs/aether#installation'}}
        />
      </PageContent>
    </ProductPage>
  );
}
