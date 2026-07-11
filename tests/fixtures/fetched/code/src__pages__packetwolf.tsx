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
  FeaturePanels,
  IntegrationDiagram,
  PillGroup,
  BentoGrid,
  CodePanel,
  SectionBand,
  SuiteProductFooter,
} from '../components/shared';
import {packetWolf} from '../data/platform-stats';
import {packetwolfFlagship} from '../data/packetwolf-details';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {ProductReadingPathStrip} from '../components/ProductReadingPathStrip';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';

const netpredSample = `$ netpred kernel connections

LOCAL                  REMOTE                 STATE        PID      PROCESS
10.0.0.86:58568        10.0.0.111:8181        ESTABLISHED  1234     python
127.0.0.1:56262        127.0.0.1:6443         ESTABLISHED  5678     kubelet

$ netpred explain payment
[KERNEL] PID 1234 (python) -> 10.0.0.5:5432 [ESTABLISHED]
[POLICY] CiliumNetworkPolicy deny rule active on backend path`;

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
        <CodePanel label="helm">{`helm install packetwolf oci://ghcr.io/hypersdk/charts/packetwolf \\
  --version 1.0.3 \\
  --namespace packetwolf-system \\
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
        <CodePanel label="kubectl">{`kubectl rollout status deployment/packetwolf-api \\
  -n packetwolf-system --timeout=120s

kubectl get pods -n packetwolf-system
# NAME                              READY   STATUS    AGE
# packetwolf-api-xxxx               1/1     Running   30s
# packetwolf-traffic-client-xxxx    1/1     Running   30s
# packetwolf-traffic-echo-xxxx      1/1     Running   30s`}</CodePanel>
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
        <CodePanel label="port-forward">{`kubectl port-forward svc/packetwolf-api \\
  -n packetwolf-system 9191:9191

# Open: http://localhost:9191

# Retrieve the auto-generated admin API key:
kubectl get secret packetwolf-secret -n packetwolf-system \\
  -o jsonpath='{.data.PACKETWOLF_ADMIN_API_KEY}' | base64 -d && echo`}</CodePanel>
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
        <CodePanel label="logs">{`kubectl logs -n packetwolf-system deployment/packetwolf-api \\
  | grep -i 'trial\\|licence'
# → PacketWolf trial licence: Trial — valid until YYYY-MM-DD`}</CodePanel>
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
        <CodePanel label="helm upgrade">{`kubectl create secret generic packetwolf-license \\
  --from-literal=license.key="<your-key>" \\
  -n packetwolf-system

helm upgrade packetwolf oci://ghcr.io/hypersdk/charts/packetwolf \\
  --version 1.0.3 --reuse-values \\
  --set license.existingSecret="packetwolf-license" \\
  -n packetwolf-system`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: '30-day full access, zero friction',
            desc: 'All 15 modules: AutoPolicy, Healer, RootCause, Chaos, Canary, KernelIntel, MultiCluster, PacketExplainer, and more. Full 80-route dashboard + TUI — from the first helm install.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'OCI registry delivery',
            desc: 'No helm repo add needed. Pull directly from oci://ghcr.io/hypersdk/charts. Deploy operator + dashboard on your Cilium cluster. CRDs installed with one command.',
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
        <PillGroup items={['Cilium 1.14+', 'Kubernetes 1.28+', 'Hubble enabled', 'Helm 3.8+', 'No account needed']} />
      </div>
    </div>
  );
}

export default function PacketWolf(): ReactNode {
  return (
    <ProductPage
      themeId="packetwolf"
      title="PacketWolf — Kernel-Native Network Intelligence"
      description="Kernel-native network intelligence for Cilium Kubernetes — observe, map, and automate policy from eBPF data."
    >
      <PageHero
        themeId="packetwolf"
        variant="bento"
        flagship
        eyebrow="Observability"
        gradientWord="PacketWolf"
        title=""
        subtitle="Kernel-Native Network Intelligence"
        description="Observe, map, and automate cluster network policy from eBPF and Cilium data."
        primaryCta={{label: 'Install Free Trial', to: '/docs/packetwolf#installation'}}
        secondaryCta={{
          label: 'Download PM overview PDF',
          to: 'pathname:///presentations/client/packetwolf/packetwolf-product-overview.pdf',
          staticAsset: true,
        }}
        bentoHighlights={[
          {title: 'Process attribution', desc: 'PID and process name on every socket — the golden differentiator.'},
          {title: '15 modules', desc: 'AutoPolicy, Healer, RootCause, Chaos, Canary, and more on one bus.'},
          {title: '80+ route console', desc: 'React 19 operator UI with live eBPF map viewers.'},
        ]}
      />

      <PageContent>
        <StatGrid stats={packetwolfFlagship.stats.map((s) => ({value: s.value, label: s.label}))} columns={3} />

        <ProductConceptSections productId="packetwolf" />

        <SectionHeader
          eyebrow="Why PacketWolf"
          title="Pods are not enough"
          subtitle="Hubble shows pod-to-pod flows. PacketWolf shows the process, socket, and policy story behind every connection."
        />
        <BentoGrid
          items={[
            {
              title: 'Process-to-network attribution',
              desc: 'Map ESTABLISHED sockets to PID and process name inside the container — the golden differentiator for SRE and security investigations.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'God Mode explain',
              desc: '`netpred explain <service>` stitches kernel connections, DNS, policy denies, and drops into one actionable narrative.',
            },
            {
              title: 'Graph engine',
              desc: 'petgraph service dependency graph with live Hubble enrichment, stale-node pruning, and shortest-path queries.',
            },
            {
              title: 'Cross-layer correlation',
              desc: 'Automatically link TCP resets, Cilium denies, and policy CRDs — root cause in seconds, not war rooms.',
              span: 'wide',
            },
          ]}
        />

        <CodePanel label="netpred · terminal">{netpredSample}</CodePanel>

        <SectionBand tone="elevated">
          <SectionHeader
            eyebrow="Architecture"
            title="Three layers, one event bus"
            subtitle="Kernel intelligence, NetPredator operator, and fifteen automation modules share a tokio broadcast bus and petgraph graph engine."
          />
          <IntegrationDiagram
            content={`CLI netpred (${packetWolf.tuiTabs} tabs) · TUI · Web UI (${packetWolf.views} routes) · ${packetWolf.apiEndpoints} REST · ${packetWolf.websocketStreams} WebSockets
                              │
              NetPredator Operator (5 CRDs)     Kernel Intelligence
              FlowPolicy · AutoPolicy · …       /proc + Cilium maps + optional eBPF
                              │
                    Event bus · Graph engine · Policy translator
                              │
              15 modules: AutoPolicy · Healer · RootCause · Chaos · Canary · …`}
          />
        </SectionBand>

        <SectionHeader
          eyebrow="Intelligence"
          title="Fifteen modules on one platform"
          subtitle="Each module is production-oriented — not a demo checkbox."
        />
        <div style={{marginBottom: '2rem'}}>
          <PillGroup items={packetwolfFlagship.intelligenceModules.map((m) => m.name)} variant="accent" />
        </div>

        <SectionHeader
          eyebrow="Dashboard"
          title={`${packetWolf.views} routes across seven navigation groups`}
          subtitle="React 19 operator console — security, observability, intelligence, and live eBPF map viewers."
        />
        <FeatureGrid
          columns={2}
          features={packetwolfFlagship.dashboardGroups.map((g) => ({
            title: g.group,
            desc: g.highlights,
          }))}
        />

        <SectionHeader
          eyebrow="Policy lifecycle"
          title="From observation to enforcement"
          subtitle="AutoPolicy learns traffic, Simulator validates rules, Chaos proves resilience, Canary rolls out safely."
        />
        <FeaturePanels
          panels={[
            {
              title: 'Observe & learn',
              items: [
                'Hubble flows + kernel attribution in one timeline',
                'Behavioral fingerprints and anomaly detection per workload',
                'Service map, topology, and SLO views for platform owners',
              ],
            },
            {
              title: 'Enforce & prove',
              accent: true,
              items: [
                'AutoPolicy → FlowPolicy CRDs → Cilium enforcement',
                'Replay historical traffic before policy changes land',
                'Chaos inject latency/loss; Canary rollback on error budgets',
              ],
            },
          ]}
        />

        <SectionHeader eyebrow="Interfaces" title="Browser, terminal, and API parity" />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: `${packetWolf.views}-route dashboard`,
              desc: 'Visual policy builder, incident mode, kernel intel page, graph explorer, and live eBPF map viewers.',
            },
            {
              title: `${packetWolf.tuiTabs}-tab TUI`,
              desc: 'Keyboard-first netpred for bastion and air-gapped environments — same data plane as the web UI.',
            },
            {
              title: `${packetWolf.apiEndpoints} REST APIs`,
              desc: 'Automate policy, flows, chaos, and graph export — integrate with SOAR, ticketing, and GitOps pipelines.',
            },
          ]}
        />

        <SectionHeader eyebrow="Cilium native" title="Built on the stack you already run" />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Cilium CNI 1.14+',
              desc: 'Reads conntrack, policy, LB, ipcache, and drop maps directly — no sidecar probe tax.',
            },
            {
              title: 'Hubble streaming',
              desc: 'Live flow feed correlated to process-level kernel events for unified triage.',
            },
            {
              title: 'Prometheus & Grafana',
              desc: 'Metrics exporter and dashboards for policy compliance and network health KPIs.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Ask Zeus"
          title="A network copilot that reasons over your cluster"
          subtitle="Natural-language questions answered from live telemetry — with an agentic mode that calls read-only tools, shows its work, and fails open to a deterministic rule router."
        />
        <BentoGrid
          items={[
            {
              title: 'Three engine modes',
              desc: 'Rule router (deterministic keyword engine, no LLM needed), Hybrid (rule + LLM narrative), and Agent (the LLM selects read-only tools and synthesizes an answer with a full agent_trace). Every reply carries an Agent / Hybrid / Rule badge.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Tool-calling over your telemetry',
              desc: 'Agent mode picks from dozens of read-only tools — process lens, threat threads, attack graph, risk graph, DNS wolf, drop decoder, policy recommendation — inside a bounded loop with a per-answer tool and time budget.',
            },
            {
              title: 'Gated write tools',
              desc: 'With write tools enabled, Zeus can propose actions — submit a policy for approval, run a playbook, preview a healer apply — but every cluster change needs explicit UI confirmation first.',
            },
            {
              title: 'Fails open, never blocks',
              desc: 'On LLM timeout or failure, Zeus automatically falls back to the deterministic rule router, so an answer always comes back — the console never depends on an external model to stay useful.',
              span: 'wide',
            },
          ]}
        />
        <CodePanel label="POST /api/v1/network/copilot">{`$ curl -s -X POST http://localhost:9191/api/v1/network/copilot \\
  -H "Authorization: Bearer $TOKEN" \\
  --json '{"query":"why can payment not reach postgres?","mode":"agent"}'

{
  "answer": "payment-svc has no egress rule for postgres:5432 — 12 TCP resets in 60s.",
  "badge": "agent",
  "agent_trace": {
    "tools_called": ["get_process_lens", "get_drop_decoder", "get_policy_recommendation"],
    "elapsed_ms": 1840
  },
  "suggested_action": "apply FlowPolicy payment-egress-postgres"
}`}</CodePanel>
        <div style={{marginTop: '16px'}}>
          <PillGroup
            items={[
              'Rule mode — no LLM',
              'Hybrid narrative',
              'Agentic tool-calling',
              'Bounded tool budget',
              'Confirmation-gated writes',
            ]}
          />
        </div>

        <SectionHeader
          eyebrow="Security posture"
          title="Detection, forensics, and compliance — not just flows"
          subtitle="PacketWolf turns kernel and Hubble telemetry into attack stories, risk scores, and audit-ready evidence."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'ThreatThread + AttackGraph',
              desc: 'Correlated alerts become multi-stage attack narratives; unified attack paths link risky workloads to topology edges so you see lateral-movement routes, not isolated events.',
            },
            {
              title: 'RiskGraph + KubePosture',
              desc: 'Per-workload and per-namespace risk scores, plus a segmentation score that surfaces default-deny gaps and workloads with unrestricted world egress.',
            },
            {
              title: 'One-click quarantine',
              desc: 'Preview then apply admin-gated workload isolation — generate the CiliumNetworkPolicy that fences off a compromised pod, with a diff before anything lands.',
            },
            {
              title: 'ForensicPack + GeoThreat',
              desc: 'Export an IR evidence bundle with a CEF sample for your SIEM; enrich egress with ASN, country, and reputation (optional MaxMind + threat-intel feeds).',
            },
            {
              title: 'ComplianceLens',
              desc: 'Map live network posture to SOC2, PCI-DSS 4.0, HIPAA, and Zero Trust controls — continuous evidence instead of a point-in-time audit.',
            },
            {
              title: 'DNSWolf + RuntimeGuard',
              desc: 'Per-workload DNS volume, failures, resolvers, and tunneling signals; runtime exec events correlated to flows with ThreatSense runtime alerts.',
            },
          ]}
        />
        <div style={{marginTop: '16px'}}>
          <PillGroup items={['SOC2', 'PCI-DSS 4.0', 'HIPAA', 'Zero Trust', 'CEF / SIEM export']} />
        </div>

        <SectionHeader
          eyebrow="Policy intelligence"
          title="Every suggestion is scored, explained, and simulated"
          subtitle="AutoPolicy doesn't just emit YAML — it ranks each rule with a weighted ML confidence score and grades your posture against least privilege."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: '7-feature confidence score',
              desc: 'Each learned rule is scored on temporal stability, traffic volume, port trust, protocol, namespace trust, label specificity, and traffic regularity — weighted so stable, high-volume flows rank highest.',
            },
            {
              title: 'Least-privilege scorecard',
              desc: 'POST a policy to /policies/score for a least-privilege grade, or /policies/explain for a plain-English summary of exactly what a CiliumNetworkPolicy allows and denies.',
            },
            {
              title: 'Observe → simulate → approve',
              desc: 'AutoPolicy Pilot and Zero-Trust Pilot forge a policy from natural language or observed traffic, simulate its blast radius, and hold it for approval before it enforces.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="packetwolf" />

        <TrialSection />

        <ProductReadingPathStrip productId="packetwolf" />
        <ClientPresentationSection productId="packetwolf" />
        <SuiteProductFooter
          productId="packetwolf"
          ctaTitle="See PacketWolf on your cluster"
          ctaSubtitle="Walk through process attribution on a live namespace, then compare AutoPolicy output to your hand-written Cilium rules."
          secondaryCta={{label: 'Read the Docs', to: '/docs/packetwolf#installation'}}
        />
      </PageContent>
    </ProductPage>
  );
}
