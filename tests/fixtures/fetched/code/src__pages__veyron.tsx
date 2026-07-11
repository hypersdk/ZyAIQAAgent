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
  IntegrationDiagram,
  PillGroup,
  CodePanel,
  BentoGrid,
  SuiteProductFooter,
} from '../components/shared';
import Link from '@docusaurus/Link';
import {veyron, platform} from '../data/platform-stats';
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
        <CodePanel label="Install Veyron">{`helm install veyron oci://ghcr.io/hypersdk/charts/veyron \\
  --version 0.3.2 \\
  --namespace veyron-system \\
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
        <CodePanel label="kubectl">{`kubectl rollout status deployment/veyron-api \\
  -n veyron-system --timeout=120s

kubectl get pods -n veyron-system
# NAME                        READY   STATUS    AGE
# veyron-api-xxxx             1/1     Running   40s
# veyron-operator-xxxx        1/1     Running   40s
# nats-xxxx                   1/1     Running   40s`}</CodePanel>
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
        <CodePanel label="port-forward">{`# Via NodePort (self-signed cert — accept in browser):
open https://<node-ip>:30151

# Or port-forward:
kubectl port-forward svc/veyron-api \\
  -n veyron-system 5151:443

# Open: https://localhost:5151
# Default API key:
kubectl get secret veyron-api-key -n veyron-system \\
  -o jsonpath='{.data.key}' | base64 -d && echo`}</CodePanel>
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
        <CodePanel label="logs">{`kubectl logs -n veyron-system deployment/veyron-api \\
  | grep -i 'trial\\|licence'
# → Veyron trial licence: Trial — valid until YYYY-MM-DD`}</CodePanel>
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
        <CodePanel label="helm upgrade">{`kubectl create secret generic veyron-license \\
  --from-literal=license.key="<your-key>" \\
  -n veyron-system

helm upgrade veyron oci://ghcr.io/hypersdk/charts/veyron \\
  --version 0.3.2 --reuse-values \\
  --set license.existingSecret="veyron-license" \\
  -n veyron-system`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: '30-day full access, zero friction',
            desc: 'All features unlocked: 44 OS templates, blueprints, REST API, web dashboard, operator CRDs, GitOps export, snapshots, and SOC detections — from the first helm install.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'OCI registry delivery',
            desc: 'No helm repo add needed. Pull directly from oci://ghcr.io/hypersdk/charts. Pin to a version or use latest.',
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
          items={['Kubernetes 1.28+', 'KubeVirt 1.0+', 'Helm 3.8+', 'kubectl configured', 'No account needed']}
        />
      </div>
    </div>
  );
}

export default function Veyron(): ReactNode {
  return (
    <ProductPage
      themeId="veyron"
      title="Veyron — Kubernetes-Native VM Command Center"
      description="Build, validate, and deploy KubeVirt VMs from YAML. 44 OS templates, 8 resource profiles, multi-VM blueprints, REST API, and GitOps operator."
    >
      <PageHero
        themeId="veyron"
        variant="split"
        eyebrow="Product"
        gradientWord="Veyron"
        title=""
        subtitle="Kubernetes-Native VM Command Center"
        description="Build, deploy, and operate KubeVirt VMs — 44 templates, multi-VM blueprints, GitOps export, and a Mission Control dashboard."
        primaryCta={{label: 'Install Free Trial', to: '/docs/veyron#installation'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/veyron'}}
      />

      <PageContent>
        {/* Stats */}
        <StatGrid
          columns={4}
          stats={[
            {value: veyron.osTemplates, label: 'OS Templates'},
            {value: veyron.resourceProfiles, label: 'Resource Profiles'},
            {value: veyron.apiRoutes, label: 'REST API Routes'},
            {value: veyron.dashboardPages, label: 'Dashboard Pages'},
          ]}
        />

        <ProductConceptSections productId="veyron" />

        {/* Templates */}
        <div style={{textAlign: 'center'}}>
          <SectionHeader
            eyebrow="Templates"
            title="44 OS Templates, Ready to Deploy"
            subtitle="Pre-configured templates for every major operating system. Each template includes optimized defaults for KubeVirt with validated cloud-init configurations."
          />
          <PillGroup
            items={[
              'Ubuntu',
              'Fedora',
              'CentOS',
              'RHEL',
              'Debian',
              'SUSE',
              'Windows Server',
              'Windows 11',
              'Rocky',
              'Alma',
              'Arch',
              'FreeBSD',
            ]}
          />
        </div>

        {/* Profiles & Blueprints */}
        <SectionHeader eyebrow="Profiles & Blueprints" title="From Single VMs to Full Stacks" />

        <FeatureGrid
          columns={2}
          features={[
            {
              title: '8 Resource Profiles',
              desc: 'Pre-configured CPU, memory, and storage allocations tuned for specific workloads.',
            },
            {
              title: 'Multi-VM Blueprints',
              desc: 'Deploy complete application stacks in a single command with dependency ordering.',
            },
          ]}
        />

        <div style={{display: 'flex', gap: '2rem', justifyContent: 'center', marginBottom: '2rem'}}>
          <PillGroup
            items={['dev', 'prod', 'database', 'web', 'ai-ml', 'edge', 'minimal', 'custom']}
            variant="accent"
          />
        </div>
        <div style={{display: 'flex', gap: '2rem', justifyContent: 'center'}}>
          <PillGroup items={['LAMP Stack', 'Kubernetes Cluster', '3-Tier App', 'CI/CD Pipeline']} variant="purple" />
        </div>

        {/* Blueprint Example */}
        <SectionHeader
          eyebrow="Blueprint"
          title="Declarative Multi-VM Stacks"
          subtitle="Define your entire application infrastructure in a single YAML blueprint. Veyron handles dependency ordering, resource allocation, and network configuration."
        />

        <CodePanel label="veyron-blueprint.yaml">{`# veyron-blueprint.yaml
apiVersion: veyron/v1
kind: Blueprint
metadata:
  name: web-stack
  description: "3-tier web application stack"

vms:
  - name: web-frontend
    template: fedora-43-minimal
    profile: web-server
    resources:
      cpu: 2
      memory: 4Gi
      disk: 20Gi
    network:
      - name: frontend-net
        ip: 10.0.1.10

  - name: api-backend
    template: rhel-9
    profile: app-server
    resources:
      cpu: 4
      memory: 8Gi
      disk: 50Gi
    network:
      - name: backend-net
        ip: 10.0.2.10

  - name: database
    template: rhel-9
    profile: database
    resources:
      cpu: 8
      memory: 32Gi
      disk: 500Gi
    network:
      - name: backend-net
        ip: 10.0.2.20`}</CodePanel>

        {/* Smart Features */}
        <SectionHeader eyebrow="Smart Features" title="Intelligent VM Management" />

        <BentoGrid
          items={[
            {
              title: 'Health Checks & Scoring',
              desc: 'Automated validation of VM configurations with a health score. Catch misconfigurations before they reach production.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Smart Recommendations',
              desc: 'AI-like resource suggestions based on workload type. Right-size every VM automatically.',
            },
            {
              title: 'Dependency Management',
              desc: 'Automatic VM ordering and startup sequencing for multi-VM blueprints. Database before app, app before frontend.',
            },
            {
              title: 'Snapshots & Backup',
              desc: 'Built-in snapshot and backup management for KubeVirt VMs. Point-in-time recovery when you need it.',
            },
          ]}
        />

        {/* Integration */}
        <div style={{textAlign: 'center'}}>
          <SectionHeader
            eyebrow="Integration"
            title="The Complete Pipeline"
            subtitle="Veyron fits into the HyperSDK Platform ecosystem to deliver end-to-end VM lifecycle management."
          />
          <IntegrationDiagram
            content={`Veyron              Zeus OS          HyperSDK Platform
  Build VMs   \u2192   Manage on K8s   \u2192   Migrate anywhere
  44 templates       TUI + Web          ${platform.cloudProviders} providers
  8 profiles         Real-time          REST API`}
          />
        </div>

        {/* Security Operations (SOC) */}
        <SectionHeader
          eyebrow="Security Operations"
          title="A SOC Built Into the Fleet"
          subtitle="Veyron normalizes Kubernetes events, VM findings, and API audit mutations into an ECS-friendly stream, evaluates built-in threat detections, and pushes to your SIEM — no external agent required."
        />

        <BentoGrid
          items={[
            {
              title: 'Normalized security event stream',
              desc: 'Kubernetes Events, VM security findings, and non-GET API audit mutations are collected into an ECS-friendly buffer, persisted in labeled ConfigMaps in the API namespace.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Built-in threat detections',
              desc: 'Rules fire on public RDP/SSH NodePort exposure, namespaces with no NetworkPolicy, VeyronVM drift, privileged domain specs, and bursts of FailedScheduling — each acknowledgeable from the dashboard.',
            },
            {
              title: 'Attack-surface inventory',
              desc: 'A live list of internet-facing VM exposures — RDP NodePorts, SSH expose, and other signals — scoped per namespace.',
            },
            {
              title: 'Threat hunts & SOAR',
              desc: 'Run read-only Elastic KQL or Splunk SPL hunts, and fire SOAR playbook webhooks automatically when a new detection opens.',
            },
          ]}
        />
        <div style={{marginTop: '16px'}}>
          <PillGroup
            items={['Elastic ECS', 'Splunk HEC', 'Microsoft Sentinel', 'IBM QRadar (LEEF)', 'SOAR webhooks']}
            variant="purple"
          />
        </div>

        {/* AI Lifecycle Intelligence */}
        <SectionHeader
          eyebrow="AI Lifecycle Intelligence"
          title="Ask Zeus — Plain-Language VM Operations"
          subtitle="A deterministic assistant that composes real cluster data — no external LLM required. Ask in plain language and get root cause, evidence, and one-click fixes. Reach it from the dashboard dock (⌘J) or the veyron ai CLI."
        />

        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Veyron Doctor',
              desc: 'Per-VM health score with the specific issues behind a failed or degraded VM.',
            },
            {
              title: 'Scheduling Explainer',
              desc: 'Turns Pending / Unschedulable into a human-readable reason with the node constraint that blocked it.',
            },
            {
              title: 'YAML Builder',
              desc: 'Generates and validates a KubeVirt VirtualMachine spec from a template, CPU, memory, and disk.',
            },
            {
              title: 'Cost & Storage Advisor',
              desc: 'Fleet and per-VM spend, plus PVC and snapshot bloat surfaced by the Storage Doctor.',
            },
            {
              title: 'Network Lens',
              desc: 'Per-VM connectivity posture for debugging VM-to-VM reachability.',
            },
            {
              title: 'Security Sentinel',
              desc: 'Exposed RDP, missing policies, and drift — per VM or across the whole fleet.',
            },
          ]}
        />

        <CodePanel label="veyron ai">{`veyron ai "Why is my VM not starting?"
veyron ai doctor vm-db-01
veyron ai scheduling vm-app-01
veyron ai explain "0/5 nodes are available: 2 Insufficient memory"
veyron ai yaml --template windows-2022 --cpus 8 --memory 32Gi --disk 500Gi
veyron ai cost --name vm-app-01
veyron ai security --name vm-app-01`}</CodePanel>

        {/* Enterprise SSO & RBAC */}
        <SectionHeader
          eyebrow="Enterprise SSO & RBAC"
          title="OIDC Login, Role-Scoped Access"
          subtitle="Bring your own identity provider for human login while automation keeps API keys. Every route is enforced against the caller's role."
        />

        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'OIDC single sign-on',
              desc: 'Point Veyron at any OpenID Connect issuer — Keycloak, Okta, or Azure AD. The dashboard uses PKCE and exchanges the authorization code server-side; MFA stays enforced at your IdP.',
            },
            {
              title: 'Three-tier RBAC',
              desc: 'IdP groups map to admin, write, or readonly. Mutating VM routes require write; cluster activate and DR routes require admin.',
            },
            {
              title: 'One-time WebSocket tickets',
              desc: 'VNC and serial console upgrades use a short-lived ticket instead of embedding long-lived API keys in query strings.',
            },
            {
              title: 'Multi-key API RBAC',
              desc: 'Issue scoped automation keys in one variable — admin:k1,write:k2,readonly:k3 — without touching your IdP.',
            },
          ]}
        />
        <div style={{marginTop: '16px'}}>
          <PillGroup items={['Keycloak', 'Okta', 'Azure AD', 'PKCE', 'admin / write / readonly']} variant="accent" />
        </div>

        <SuiteProductCapabilities productId="veyron" />

        <TrialSection />

        <ClientPresentationSection productId="veyron" />
        <SuiteProductFooter
          productId="veyron"
          ctaTitle="Ready to build production-ready VMs?"
          ctaSubtitle="See how Veyron gives your team declarative VM building with 44 templates and intelligent automation."
          secondaryCta={{label: 'Read the Docs', to: '/docs/veyron#installation'}}
        />
      </PageContent>
    </ProductPage>
  );
}
