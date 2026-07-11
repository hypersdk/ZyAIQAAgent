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
  BentoGrid,
  CodePanel,
  PillGroup,
  SuiteProductFooter,
} from '../components/shared';
import {ProductConceptSections} from '../components/ProductConceptSections';

function TrialSection(): ReactNode {
  return (
    <div id="trial" style={{scrollMarginTop: '80px', padding: '4rem 1.5rem', maxWidth: 860, margin: '0 auto'}}>
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
        <CodePanel label="helm">{`helm install hermes oci://ghcr.io/hypersdk/charts/hermes \\
  --version 0.2.0 \\
  --namespace hermes-system \\
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
        <CodePanel label="kubectl">{`kubectl rollout status deployment/hermes \\
  -n hermes-system --timeout=120s

kubectl get pods -n hermes-system
# NAME                  READY   STATUS    AGE
# hermes-xxxx           2/2     Running   45s   ← controller + server`}</CodePanel>
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
        <CodePanel label="port-forward">{`# Via NodePort (if node IP is reachable):
open http://<node-ip>:31847

# Or port-forward from any machine with kubectl:
kubectl port-forward svc/hermes-server \\
  -n hermes-system 8080:31847

# Open: http://localhost:8080`}</CodePanel>
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
        <CodePanel label="logs">{`kubectl logs -n hermes-system deployment/hermes -c server \\
  | grep -i 'trial\\|licence'
# → Hermes licence: Trial — valid until YYYY-MM-DD`}</CodePanel>
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
        <CodePanel label="helm upgrade">{`kubectl create secret generic hermes-license \\
  --from-literal=license.key="<your-key>" \\
  -n hermes-system

helm upgrade hermes oci://ghcr.io/hypersdk/charts/hermes \\
  --version 0.2.0 --reuse-values \\
  --set license.existingSecret="hermes-license" \\
  -n hermes-system`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: '30-day full access, zero friction',
            desc: 'Auto-discovery, LLM-powered insights, multi-cluster federation, RBAC workspaces, and the full web UI — from the first helm install.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'Automatic trial clock',
            desc: 'Build date is baked into the binary at compile time. The 30-day window starts then — no account or activation required.',
          },
          {
            title: 'Single Helm command',
            desc: 'No helm repo add. Helm 3.8+ pulls from OCI directly. Auto-discovers services on install.',
          },
          {
            title: 'After the trial',
            desc: 'Contact sales@zyvor.dev for a licence key. Apply it via a Kubernetes Secret — no reinstall needed.',
          },
        ]}
      />
      <div style={{marginTop: '16px'}}>
        <PillGroup
          items={['No account needed', 'Kubernetes 1.28+', 'Helm 3.8+', 'kubectl configured', 'LLM optional']}
        />
      </div>
    </div>
  );
}

export default function Hermes(): ReactNode {
  return (
    <ProductPage
      themeId="hermes"
      title="Hermes — Application Operating Layer for Kubernetes"
      description="Auto-discover every service on your cluster, surface LLM-powered insights, and give teams a shared launchpad — no manual inventory."
    >
      <PageHero
        themeId="hermes"
        variant="split"
        eyebrow="Product"
        gradientWord="Hermes"
        title=""
        subtitle="Application Operating Layer for Kubernetes"
        description="Auto-discover every dashboard, API, and internal tool — then give teams a permanent front door to launch any app without kubectl port-forward."
        primaryCta={{label: 'Install Free Trial', to: '/docs/hermes#installation'}}
        secondaryCta={{label: 'Read the Docs', to: '/docs/hermes'}}
      />

      <PageContent>
        <StatGrid
          columns={4}
          stats={[
            {value: '60+', label: 'REST Endpoints'},
            {value: '4', label: 'Auth Modes'},
            {value: '∞', label: 'Services Discovered'},
            {value: '31847', label: 'Default Port'},
          ]}
        />

        <ProductConceptSections productId="hermes" />

        {/* Core capabilities */}
        <SectionHeader
          eyebrow="Core capabilities"
          title="Know your cluster. Always."
          subtitle="Hermes watches every namespace, surfaces what's running, and gives teams a single pane of glass — with AI to explain what matters."
        />
        <BentoGrid
          items={[
            {
              title: 'Auto-discovery',
              desc: 'Detects Deployments, StatefulSets, DaemonSets, Ingresses, Gateway API routes, and service mesh endpoints — no YAML registration.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Shared Launchpad',
              desc: 'A team-facing portal that surfaces every app with health status, links, and documentation. One URL per cluster.',
            },
            {
              title: 'LLM-powered insights',
              desc: 'Ask "what is unhealthy?" in plain text. Zeus AI analyses pod events, restarts, and resource pressure across namespaces.',
            },
            {
              title: 'RBAC Workspaces',
              desc: 'Scope teams to namespaces they own. Workspace ACL rules keep dev, staging, and prod catalogs separate.',
            },
          ]}
        />

        {/* Multi-cluster federation */}
        <SectionHeader
          eyebrow="Multi-cluster"
          title="Federate Across Clusters"
          subtitle="Link multiple Hermes instances to get a unified view of services across dev, staging, and production environments."
        />
        <BentoGrid
          items={[
            {
              title: 'Cluster federation',
              desc: 'Each cluster runs its own Hermes. A hub instance federates them — cross-cluster service graph with unified auth.',
              span: 'wide',
              accent: true,
            },
            {
              title: '4 auth modes',
              desc: 'None (internal), API key, OIDC (Google, Okta, Keycloak), or trust-header federation. Mix per environment.',
            },
            {
              title: 'Persistent catalog',
              desc: 'SQLite-backed store persists discovered apps, share links, workspace ACL, and AI-generated summaries across restarts.',
            },
            {
              title: 'Share links',
              desc: 'Generate scoped, expiring links to specific apps or clusters — no account needed for the recipient.',
            },
          ]}
        />

        {/* Gateway front door */}
        <SectionHeader
          eyebrow="Gateway"
          title="One Front Door — Any Protocol"
          subtitle="Every published app gets a permanent launch URL through the Hermes gateway. No port-forward, no bookmark sprawl, no VPN gymnastics."
        />
        <BentoGrid
          items={[
            {
              title: 'Stable launch URLs',
              desc: 'Open any app at /launchpad/apps/{slug} by canonical slug, or /a/{namespace}/{slug} scoped to a namespace. The link never changes when pods reschedule.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'WebSocket, gRPC & SSE',
              desc: 'The proxy tunnels WebSocket upgrades, gRPC, server-sent events, and HTTP/2 — live dashboards and streaming APIs work through the same door.',
            },
            {
              title: 'Fails safe',
              desc: 'The gateway blocks the proxy (403/502) unless the app is published and has ready endpoints — no dead links to half-started pods.',
            },
            {
              title: 'Share-link proxy',
              desc: 'A /launchpad/s/{token} route opens one specific app via a time-limited token. The recipient needs no account and never touches kubectl.',
            },
          ]}
        />
        <CodePanel label="gateway">{`# Launch a published app by canonical slug
curl http://<node-ip>:31847/launchpad/apps/grafana

# Or scope by namespace + service slug
curl http://<node-ip>:31847/a/monitoring/grafana

# Every successful proxy records a 'launch' audit event`}</CodePanel>

        {/* Discovery & publishing */}
        <SectionHeader
          eyebrow="Discovery & publishing"
          title="Auto-Discovered, Deliberately Published"
          subtitle="Hermes finds every service continuously — but nothing is exposed until you say so. Annotations enrich the catalog without registering apps by hand."
        />
        <BentoGrid
          items={[
            {
              title: 'Safe by default',
              desc: 'Discovered services land in a review queue; auto-publish is off out of the box. You publish what teams should see — the rest stays private.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Annotate to enrich',
              desc: 'One hermes.zyvor.dev/ annotation adds display name, slug, owner, category, and icon. Environment is inferred from the namespace when omitted.',
            },
            {
              title: 'Live dependency graph',
              desc: 'depends-on annotations wire a service dependency graph; Zeus AI flags unresolved links so you see what a workload actually needs.',
            },
            {
              title: 'One-click or bulk publish',
              desc: 'Publish a single app or a whole namespace from the Discovery queue, guided by AI-ranked suggestions for what to surface first.',
            },
          ]}
        />
        <CodePanel label="annotations">{`metadata:
  annotations:
    hermes.zyvor.dev/enabled: "true"
    hermes.zyvor.dev/name: "Grafana"
    hermes.zyvor.dev/slug: "grafana"
    hermes.zyvor.dev/owner: "platform-team"
    hermes.zyvor.dev/depends-on: "prometheus,loki"
    hermes.zyvor.dev/recommended: "true"`}</CodePanel>

        {/* Zeus AI depth */}
        <SectionHeader
          eyebrow="Zeus AI"
          title="Ask Your Cluster in Plain Language"
          subtitle="Spotlight and the diagnose drawer turn raw probe errors and namespace archaeology into plain-English answers — with or without an LLM."
        />
        <BentoGrid
          items={[
            {
              title: 'Spotlight command bar',
              desc: 'Press ⌘K and type diagnose, why, suggest publish, graph insight, or ns insight <namespace> to get answers without leaving the keyboard.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Works without an LLM',
              desc: 'Every insight has a rule-based engine — fleet health, publish ranking, and diagnosis run offline. Add an OpenAI-compatible key only for richer narratives.',
            },
            {
              title: 'Diagnose drawer',
              desc: 'One global drawer explains any unhealthy app: route lens, a human-readable probe summary, and copy-ready kubectl commands.',
            },
            {
              title: 'Fleet, namespace & team rollups',
              desc: 'Insight endpoints roll health up by fleet, namespace, owner, dependency graph, and federated cluster — with a rules/LLM source badge.',
            },
          ]}
        />
        <div style={{marginTop: '16px'}}>
          <PillGroup
            items={[
              'ai: <question>',
              'diagnose',
              'why',
              'suggest publish',
              'graph insight',
              'ns insight',
              'rule-based fallback',
            ]}
          />
        </div>

        <TrialSection />

        <SuiteProductFooter
          productId="hermes"
          ctaTitle="Ready to see every service on your cluster?"
          ctaSubtitle="Install Hermes in 30 seconds — no sign-up, no sales call. Auto-discovery starts on first boot."
          secondaryCta={{label: 'Read the Docs', to: '/docs/hermes'}}
        />
      </PageContent>
    </ProductPage>
  );
}
