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
  FeaturePanels,
  CodePanel,
  BentoGrid,
  PillGroup,
  SuiteProductFooter,
} from '../components/shared';
import {ragnarok} from '../data/platform-stats';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';

function TrialSection(): ReactNode {
  return (
    <div id="trial" style={{scrollMarginTop: '80px'}}>
      <SectionHeader
        eyebrow="30-Day Free Trial"
        title="Install in 30 Seconds — No Sign-Up Required"
        subtitle="One Helm command. Trial starts automatically. No key, no account, no credit card."
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
        <CodePanel label="helm">{`helm install ragnarok oci://ghcr.io/hypersdk/charts/ragnarok \\
  --version 0.4.4 \\
  --namespace ragnarok-system \\
  --create-namespace \\
  --set security.jwtSecret="$(openssl rand -base64 32)"`}</CodePanel>
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
        <CodePanel label="kubectl">{`kubectl rollout status deployment/ragnarok-backend \\
  -n ragnarok-system --timeout=120s

kubectl get pods -n ragnarok-system
# NAME                        READY   STATUS    AGE
# ragnarok-backend-xxxx       1/1     Running   45s`}</CodePanel>
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
          Step 3 — Access the API
        </p>
        <CodePanel label="port-forward">{`kubectl port-forward svc/ragnarok-backend \\
  -n ragnarok-system 5010:5010

# Open: http://localhost:5010
# Health check:
curl http://localhost:5010/health`}</CodePanel>
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
        <CodePanel label="logs">{`kubectl logs -n ragnarok-system deployment/ragnarok-backend \\
  | grep -i 'trial\\|licence'
# → Ragnarok licence: Trial — valid until YYYY-MM-DD`}</CodePanel>
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
        <CodePanel label="helm upgrade">{`kubectl create secret generic ragnarok-license \\
  --from-literal=license.key="<your-key>" \\
  -n ragnarok-system

helm upgrade ragnarok oci://ghcr.io/hypersdk/charts/ragnarok \\
  --version 0.4.4 --reuse-values \\
  --set license.existingSecret="ragnarok-license" \\
  -n ragnarok-system`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: '30-day full access, zero friction',
            desc: 'All 6 AI agents, confidential computing hub, predictive scaling, auto-heal, cost optimizer, and full web UI — from the first helm install.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'OCI registry delivery',
            desc: 'No helm repo add needed. Pull directly from oci://ghcr.io/hypersdk/charts. Deploys backend in minutes.',
          },
          {
            title: 'Automatic trial clock',
            desc: 'Build date is baked into the binary. Trial runs for 30 days from image release. No activation step required.',
          },
          {
            title: 'After the trial',
            desc: 'Contact sales@zyvor.dev for a licence key. Apply it via a Kubernetes Secret — no reinstall needed.',
          },
        ]}
      />
      <div style={{marginTop: '16px'}}>
        <PillGroup
          items={['Kubernetes 1.28+', 'KubeVirt required', 'Helm 3.8+', 'kubectl configured', 'No account needed']}
        />
      </div>
    </div>
  );
}

export default function Ragnarok(): ReactNode {
  return (
    <ProductPage
      themeId="ragnarok"
      title="Ragnarok — AI-Powered VM Management"
      description="AI-powered VM management with confidential computing fabric. Natural language provisioning, TEE attestation, and cost optimization on KubeVirt."
    >
      <PageHero
        themeId="ragnarok"
        variant="split"
        eyebrow="Product"
        gradientWord="Ragnarok"
        title=""
        subtitle="AI-Powered VM Management for KubeVirt"
        description="Provision and operate KubeVirt fleets with AI-assisted workflows and confidential computing hooks."
        primaryCta={{label: 'Install Free Trial', to: '/docs/ragnarok#installation'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/ragnarok#installation'}}
      />

      <PageContent>
        {/* Stats */}
        <StatGrid
          columns={4}
          stats={[
            {value: `${ragnarok.aiAgents} AI Agents`, label: 'Intelligent Automation'},
            {value: ragnarok.autoHealSuccess, label: 'Auto-Heal Target'},
            {value: ragnarok.apiRoutes, label: 'API Endpoints'},
            {value: ragnarok.autoHealResponse, label: 'Target Response'},
          ]}
        />

        <ProductConceptSections productId="ragnarok" />

        {/* The Problem */}
        <SectionHeader
          eyebrow="The Problem"
          title="Managing VMs on Kubernetes Is Hard"
          subtitle="Teams struggle with complex YAML, fragmented tooling, and zero cost visibility. Ragnarok eliminates these challenges with AI-driven automation."
        />

        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Complex YAML',
              desc: 'Writing and maintaining KubeVirt manifests requires deep Kubernetes expertise and is error-prone at scale.',
            },
            {
              title: 'No Visibility',
              desc: 'No unified view of VM health, resource usage, or performance across namespaces and clusters.',
            },
            {
              title: 'Cost Overruns',
              desc: 'Without predictive cost analysis, teams over-provision resources and waste budget on idle VMs.',
            },
            {
              title: 'Slow Provisioning',
              desc: 'Manual VM creation and configuration takes hours instead of minutes. Tool sprawl slows every workflow.',
            },
          ]}
        />

        {/* Natural Language Demo */}
        <SectionHeader
          eyebrow="Natural Language"
          title="Describe It. Deploy It."
          subtitle="Tell Ragnarok what you need in plain English. The AI generates production-ready KubeVirt YAML in seconds."
        />

        <div style={{maxWidth: 800, margin: '0 auto 2rem'}}>
          <div
            style={{
              background: 'rgba(240, 88, 58, 0.06)',
              border: '1px solid rgba(240, 88, 58, 0.15)',
              borderRadius: '12px',
              padding: '1.25rem 1.5rem',
              marginBottom: '1rem',
            }}
          >
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'rgba(240, 88, 58, 0.8)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: '0.5rem',
              }}
            >
              Prompt
            </div>
            <div
              style={{
                color: '#e2e8f0',
                fontSize: '0.95rem',
                lineHeight: 1.6,
              }}
            >
              &quot;Create a production PostgreSQL server with 8 cores, 32GB RAM, 500GB storage on RHEL 9 with daily
              backups&quot;
            </div>
          </div>
          <CodePanel label="Generated YAML">{`apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: postgres-prod-01
  labels:
    app: postgresql
    environment: production
spec:
  template:
    spec:
      domain:
        cpu:
          cores: 8
        memory:
          guest: 32Gi
        devices:
          disks:
          - name: rootdisk
            disk:
              bus: virtio
          - name: datadisk
            disk:
              bus: virtio
      volumes:
      - name: rootdisk
        containerDisk:
          image: registry.example.com/rhel9:latest
      - name: datadisk
        persistentVolumeClaim:
          claimName: postgres-data-500g`}</CodePanel>
        </div>

        {/* AI Agents */}
        <SectionHeader
          eyebrow="AI Agents"
          title="Six Intelligent Agents"
          subtitle="Provisioning, optimization, healing, explanation, topology, and incident response — coordinated automation across the VM lifecycle."
        />

        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Provisioner',
              desc: 'Translates natural language into KubeVirt YAML. Selects templates, applies resource profiles, and validates before deployment.',
            },
            {
              title: 'Optimizer',
              desc: 'Continuous right-sizing, idle VM detection, and predictive cost analysis — modeled ~40% savings in typical estates.',
            },
            {
              title: 'Auto-Healer',
              desc: 'Sub-500ms response playbooks for common failure modes, targeting 91% autonomous auto-heal success.',
            },
            {
              title: 'Root-Cause & Explain',
              desc: 'Anomaly detection with plain-language incident explanation — operators see why, not just that something failed.',
            },
            {
              title: 'Topology & Drift',
              desc: 'Interactive React Flow graphs for VM, node, PVC, and network relationships. Drift detection across namespaces.',
            },
            {
              title: 'Incident Mode',
              desc: 'War-room UI correlates node failure, storage pressure, and mass-VM events — guided response with policy guardrails.',
            },
          ]}
        />

        {/* AI Features */}
        <SectionHeader
          eyebrow="AI Features"
          title="Intelligence at Every Layer"
          subtitle="AI is not an add-on. It is woven into every operation, from provisioning to cost management."
        />

        <FeaturePanels
          panels={[
            {
              title: 'Auto-Provisioning',
              items: [
                'Describe what you need in natural language',
                'AI generates optimal VM specifications',
                'Automatic resource sizing based on workload type',
                'One-click deployment to any namespace',
              ],
            },
            {
              title: 'Resource Optimization',
              accent: true,
              items: [
                'Continuous right-sizing recommendations',
                'Idle VM detection and auto-shutdown',
                'Predictive cost analysis and forecasting',
                'Anomaly detection with automated alerts',
              ],
            },
          ]}
        />

        {/* Visual Management */}
        <SectionHeader eyebrow="Visual Management" title="The vCenter Experience for Kubernetes" />

        <BentoGrid
          items={[
            {
              title: 'Real-Time Dashboards',
              desc: 'Live resource metrics, health scores, and performance trends across all VMs in your cluster. No YAML required.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Drag-and-Drop Operations',
              desc: 'Move, clone, and snapshot VMs with visual controls. One-click start, stop, and restart from the management console.',
            },
            {
              title: 'Cost Prediction',
              desc: 'AI-powered cost forecasting shows the impact of every provisioning decision before you commit resources.',
            },
          ]}
        />

        {/* Explainable Intelligence Engine */}
        <SectionHeader
          eyebrow="Intelligence Engine"
          title="Every Answer Carries an Honesty Label"
          subtitle="Collectors gather facts, engines rank hypotheses, and an optional LLM writes narrative only — never the conclusion. Each recommendation is tagged so operators know exactly where it came from."
        />

        <BentoGrid
          items={[
            {
              title: 'Four transparency labels',
              desc: 'Every signal is stamped heuristic (rule/threshold), learned (per-VM baseline), correlated (multi-signal RCA), or llm_assisted (narrative only — hypotheses unchanged). No black-box scores.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Ops Copilot',
              desc: 'POST /intelligence/copilot/ask returns ranked hypotheses plus explainable actions, scoped to the VM or incident in question.',
            },
            {
              title: 'Digital twin what-if',
              desc: '/intelligence/twin/simulate models a resource change before you apply it; /forecast/cluster projects exhaustion.',
            },
            {
              title: 'Migration risk & drift',
              desc: 'Live-migration risk scoring per VM, plus drift remediation plans that are proposed — never auto-applied — under a suggest/auto_low_risk policy.',
            },
            {
              title: 'Capacity marketplace & self-tuning',
              desc: 'Advisory runtime-pool capacity ranking and self-tuning signals from metrics, pools, and SPIRE — surfaced as recommendations, not silent changes.',
            },
          ]}
        />

        <div style={{maxWidth: 800, margin: '2rem auto 0'}}>
          <CodePanel label="Explainable API">{`# Ranked hypotheses with honesty labels
POST /api/v1/intelligence/copilot/ask
GET  /api/v1/intelligence/forecast/cluster
GET  /api/v1/intelligence/migrations/{vm_id}/risk
POST /api/v1/intelligence/drift/{vm_id}/plan   # no auto-apply
POST /api/v1/intelligence/twin/simulate
GET  /api/v1/intelligence/capacity/marketplace
GET  /api/v1/intelligence/self-tuning/status

# Native gRPC gateway for automation clients
RAGNAROK_GRPC_ENABLED=1  RAGNAROK_GRPC_LISTEN=0.0.0.0:50051`}</CodePanel>
        </div>

        <div style={{marginTop: '16px'}}>
          <PillGroup
            items={[
              'heuristic',
              'learned',
              'correlated',
              'llm_assisted',
              'Advisory by default',
              'REST + gRPC',
              'OpenAI-compatible (optional)',
            ]}
          />
        </div>

        {/* Security Profiles & Runtime Pools */}
        <SectionHeader
          eyebrow="Confidential Runtime"
          title="Security Profiles, Not Raw Runtime Classes"
          subtitle="Tenants pick a named profile. Ragnarok resolves the runtime pool, applies confidential defaults, and stamps the VM with the right labels — SEV-SNP, Kata, or GPU-attested."
        />

        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'sovereign-high',
              desc: 'Strict SEV-SNP on pool-sovereign-high-snp for regulated and sovereign workloads that must prove hardware isolation.',
            },
            {
              title: 'standard-confidential',
              desc: 'SEV-SNP by default on pool-standard-confidential-snp — the baseline profile for enterprise VMs.',
            },
            {
              title: 'sandbox',
              desc: 'Kata isolation without confidential computing on pool-sandbox-kata, sized for development and CI.',
            },
            {
              title: 'ai-gpu',
              desc: 'Confidential GPU pool (kata-qemu-nvidia-gpu-snp) for attested accelerator workloads on nvidia.com/gpu nodes.',
            },
          ]}
        />

        <div style={{maxWidth: 800, margin: '2rem auto 0'}}>
          <CodePanel label="RuntimePool CRD">{`# Install the confidential runtime pools as CRDs
./scripts/install-confidential-runtime-pools.sh
kubectl get runtimepools.ragnarok.io

# Create a VM by profile — API resolves the pool + labels
{
  "name": "api-svc",
  "security_profile": "sovereign-high",
  "cpu": 4, "memory": "8Gi", "disk": "40Gi"
}
# → ragnarok.zyvor.dev/security-profile
# → ragnarok.zyvor.dev/runtime-pool
# → ragnarok.zyvor.dev/runtime-class

# Node placement gate for confidential scheduling
POST /api/v1/confidential/scheduler/admit`}</CodePanel>
        </div>

        {/* Infrastructure as Code & Governance */}
        <SectionHeader
          eyebrow="Operate as Code"
          title="Terraform, kubectl, and a Role Matrix You Can Read"
          subtitle="Ragnarok is not UI-only. Declare VMs and templates in HCL, deploy with Kustomize overlays, and enforce fine-grained RBAC with a full audit trail."
        />

        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Terraform provider',
              desc: 'ragnarok_vm and ragnarok_template resources — published to the registry, versioned in CI on v* tags. Manage fleets in HCL alongside the rest of your stack.',
            },
            {
              title: 'kubectl / Kustomize',
              desc: 'Helm-free path: k8s/base manifests and k8s/overlays/prod, with External Secrets support for database and JWT credentials.',
            },
            {
              title: 'Fine-grained RBAC',
              desc: 'Admin / Developer / Viewer role × permission matrix (vm_write, vm_delete, vm_migrate, gitops_reconcile, cluster_manage…) served at /api/v1/rbac/matrix and the /roles UI.',
            },
            {
              title: 'Mutation audit trail',
              desc: 'GET /api/v1/audit records every mutating action for compliance evidence — admin-scoped and queryable.',
            },
            {
              title: 'Prometheus & Grafana',
              desc: '/metrics endpoint, per-VM charts via RAGNAROK_PROMETHEUS_URL, and embedded Grafana dashboards from RAGNAROK_GRAFANA_URL.',
            },
            {
              title: 'Network observability',
              desc: '/api/v1/network-observability/aggregates surfaces pod traffic with optional Cilium/Hubble series when scraped.',
            },
          ]}
        />

        <div style={{maxWidth: 800, margin: '2rem auto 0'}}>
          <CodePanel label="terraform">{`resource "ragnarok_vm" "web" {
  name   = "web-01"
  cpu    = 2
  memory = "4Gi"
  disk   = "20Gi"
  image  = "quay.io/containerdisks/ubuntu:22.04"
}

resource "ragnarok_template" "small_ubuntu" {
  name        = "Small Ubuntu"
  description = "Dev default"
  cpu         = 2
  memory      = "4Gi"
  disk        = "20Gi"
  image       = "quay.io/containerdisks/ubuntu:22.04"
}`}</CodePanel>
        </div>

        <SuiteProductCapabilities productId="ragnarok" />

        <TrialSection />

        <ClientPresentationSection productId="ragnarok" />
        <SuiteProductFooter
          productId="ragnarok"
          ctaTitle="Ready to manage Kubernetes VMs with AI?"
          ctaSubtitle="See how Ragnarok brings vCenter-class management to Kubernetes with AI-driven automation and cost optimization."
          secondaryCta={{label: 'Read the Docs', to: '/docs/ragnarok#installation'}}
        />
      </PageContent>
    </ProductPage>
  );
}
