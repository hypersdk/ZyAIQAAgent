// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {
  ProductPage,
  PageContent,
  StatGrid,
  SectionHeader,
  FeatureGrid,
  BentoGrid,
  CodePanel,
  PillGroup,
  SuiteProductFooter,
} from '../components/shared';
import styles from '../components/shared/shared.module.css';
import {forge} from '../data/platform-stats';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import ForgeZeusConsole from '../components/ForgeZeusConsole';

function TrialSection(): ReactNode {
  return (
    <div style={{padding: '4rem 1.5rem', maxWidth: 860, margin: '0 auto'}}>
      <SectionHeader
        eyebrow="30-Day Free Trial"
        title="Install in 30 Seconds — No Sign-Up Required"
        subtitle="Pull Forge directly from the OCI registry. The trial clock starts from the build date — no account, no email, no sales call."
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
        <CodePanel>{`helm install forge oci://ghcr.io/hypersdk/charts/forge-core \\
  --version 1.0.1 \\
  --namespace forge-system \\
  --create-namespace \\
  --set namespace.create=false`}</CodePanel>
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
          Step 2 — Verify install
        </p>
        <CodePanel>{`kubectl get all -n forge-system
# DaemonSets for GPU nodes appear (zero pods until forge.ai/gpu=true nodes join)

# Download the Forge CLI:
curl -LO https://releases.zyvor.dev/forge/latest/forge-linux-amd64
chmod +x forge-linux-amd64 && sudo mv forge-linux-amd64 /usr/local/bin/forge`}</CodePanel>
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
          Step 3 — Connect the CLI to your cluster
        </p>
        <CodePanel>{`# Point forge CLI at your cluster:
forge config set-context \\
  --cluster https://<api-server>:6443 \\
  --namespace forge-system

# List GPU pools (empty until GPU nodes are labelled):
forge gpu pools list`}</CodePanel>
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
        <CodePanel>{`forge version
# forge 1.0.0 · trial valid until YYYY-MM-DD`}</CodePanel>
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
        <CodePanel>{`# Via Helm:
helm upgrade forge oci://ghcr.io/hypersdk/charts/forge-core \\
  --version 1.0.1 --reuse-values \\
  --set license.key="<your-key>" \\
  -n forge-system

# Or via CLI:
forge license apply --key "<your-key>"`}</CodePanel>
      </div>

      <BentoGrid
        items={[
          {
            title: 'Full Feature Access',
            desc: 'All seven operators, 62 CRDs, RDMA-aware scheduling, FinOps dashboards, and the cluster copilot — nothing gated.',
            span: 'wide',
            accent: true,
          },
          {
            title: 'Automatic trial clock',
            desc: 'Build date is baked into the CLI binary at compile time. The 30-day window starts then — no account or key required.',
          },
          {
            title: 'Single Helm command',
            desc: 'No helm repo add. Helm 3.8+ pulls from OCI directly. GPU nodes detected automatically on install.',
          },
          {
            title: 'After the Trial',
            desc: 'Move to a commercial licence with no data loss. GPU pool configs, quota policies, and workload history carry forward.',
          },
        ]}
      />
      <PillGroup
        items={[
          'No account needed',
          'Kubernetes 1.28+',
          'NVIDIA GPU nodes',
          'InfiniBand / RoCE optional',
          'x86-64 or ARM64',
        ]}
      />
    </div>
  );
}

export default function Forge(): ReactNode {
  return (
    <ProductPage
      themeId="forge"
      title="Forge -- The AI Infrastructure Operating System"
      description="The AI infrastructure operating system with Zeus — an embedded, approval-gated AI ops engineer that Nutanix and Red Hat don't have. Kubernetes-native operators and CRDs for GPU scheduling, model serving, vector database, observability, security, and FinOps in one control plane. Built on open standards with no lock-in. Red Hat for AI infrastructure; Nutanix for AI."
    >
      <header className={styles.heroSection} style={{textAlign: 'left'}}>
        <div style={{maxWidth: 1120, margin: '0 auto', position: 'relative', zIndex: 1}}>
          <div className={styles.heroPills}>
            <span className={styles.pill}>
              <strong>Red Hat</strong> for AI infrastructure
            </span>
            <span className={styles.pill}>
              <strong>Nutanix</strong> for AI
            </span>
            <span className={styles.pillPurple}>Led by Zeus</span>
          </div>
          <span className={styles.heroEyebrow}>The AI Infrastructure Operating System</span>
          <h1 className={styles.heroTitle} style={{maxWidth: 940}}>
            Deploy a <span className={styles.heroTitleGradient}>private AI cloud</span> like it&apos;s one product.
          </h1>
          <p className={styles.heroSubtitle} style={{maxWidth: 660, margin: '0 0 1.75rem'}}>
            <strong>Forge is a Kubernetes-native AI Infrastructure Platform</strong> that lets enterprises deploy,
            manage, and scale private AI clouds across data center, edge, and hybrid — on open standards, with no
            lock-in.
          </p>
          <div className={styles.heroCtas} style={{justifyContent: 'flex-start'}}>
            <Link className={styles.primaryBtn} to="#see-zeus-decide">
              See Zeus decide →
            </Link>
            <Link className={styles.secondaryBtn} to="/docs/forge#the-eight-components-of-the-ai-infrastructure-os">
              The 8 components
            </Link>
          </div>
        </div>
      </header>

      <PageContent>
        <StatGrid
          stats={[
            {value: forge.rdmaBandwidth, label: 'RDMA Fabric'},
            {value: forge.latency, label: 'Latency Target'},
            {value: forge.gpuUtilization, label: 'GPU Utilization'},
            {value: String(forge.operators), label: 'Operators'},
            {value: String(forge.crds), label: 'CRDs'},
          ]}
          columns={5}
        />

        <ProductConceptSections productId="forge" />

        <SectionHeader
          eyebrow="Architecture"
          title="Seven Operators. One Control Plane."
          subtitle="Purpose-built Kubernetes operators for every layer of GPU infrastructure."
        />
        <BentoGrid
          items={[
            {
              title: 'GPU Operator',
              desc: 'NVIDIA-native scheduling with MIG, time-slicing, topology awareness, and automatic driver management.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'AI Operator',
              desc: 'Gang scheduling, elastic training, and workload orchestration for distributed AI/ML pipelines.',
            },
            {
              title: 'Storage Operator',
              desc: '40 GB/s per-node throughput with Lustre, GPFS, and BeeGFS integration. Feed data to GPUs at line rate.',
            },
            {
              title: 'Network Operator',
              desc: 'InfiniBand and RoCE v2 with automatic RDMA/NVLink tuning. Sub-microsecond GPU-to-GPU latency.',
            },
            {
              title: 'Quota Operator',
              desc: 'Multi-tenant GPU quota management with cost tracking and chargeback across teams and projects.',
            },
            {
              title: 'Network Intelligence',
              desc: 'eBPF-powered observability for GPU traffic patterns, bandwidth utilization, and network policy enforcement.',
            },
            {
              title: 'Virtualization Operator',
              desc: 'KubeVirt-backed FabricVirtualMachine CRDs — run VMs alongside GPU containers on the same control plane.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Private AI Cloud"
          title="Host your own AI cloud — LLMs on your GPUs, nothing phones home."
          subtitle="Forge is a self-hosted inference platform. Serve open models on your own hardware, run Ollama for local and air-gapped inference, and keep every token, prompt, and embedding inside your cluster."
        />
        <BentoGrid
          items={[
            {
              title: 'Six serving backends, one spec',
              desc: 'One FabricInferenceService CRD picks the engine per model — Ollama, vLLM, TensorRT-LLM, Triton, SGLang, or TorchServe. Scale-to-zero when idle, weighted canary between versions.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Ollama, built in',
              desc: 'Pull and serve Llama 3, Mistral, Qwen, and more with the ollama/ollama runtime managed by the AI operator — no external API, no per-token bill.',
            },
            {
              title: 'Private routing by policy',
              desc: 'The model-router sends privacy-tagged tasks to a local Ollama model automatically, so sensitive prompts never leave the building even when cloud models are also configured.',
            },
            {
              title: 'Embeddings on your hardware',
              desc: 'The embedding service runs nomic-embed-text on Ollama for the RAG pipeline — chunk, embed, and upsert into Qdrant without a hosted embedding API.',
            },
            {
              title: 'Air-gapped Zeus',
              desc: 'Set zeus.airgap=true and Zeus itself falls back to a local Ollama provider — the AI ops engineer keeps working with zero internet access.',
            },
          ]}
        />
        <CodePanel label="Serve an open model privately on your own GPUs">{`apiVersion: forge.ai/v1
kind: FabricInferenceService
metadata:
  name: llama3-private
  namespace: ai-platform
spec:
  modelRef: llama3           # pulled + served by Ollama
  backend: ollama            # ollama | vllm | tensorrt-llm | triton | sglang | torchserve
  minReplicas: 0             # scale-to-zero when idle
  maxReplicas: 4
  resources:
    gpuType: A100-80G
    gpuCount: 1`}</CodePanel>
        <PillGroup
          items={[
            'No per-token billing',
            'No prompt egress',
            'Ollama · vLLM · SGLang',
            'OpenAI-compatible endpoint',
            'Runs fully air-gapped',
          ]}
        />

        <SectionHeader
          eyebrow="AI Platform"
          title="A full AI platform, not just a scheduler."
          subtitle="Above the GPU fabric sits a Zeus OS control plane — eighteen modules across build, operate, and govern, all landing on one Mission Control surface. The same cluster that schedules GPUs also builds, ships, and governs the models that run on them."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Build',
              desc: 'Studio, Agents, Datasets, RAG, Prompts, Training, and Evaluations — author, fine-tune, and test models and agents without leaving the platform.',
            },
            {
              title: 'Operate',
              desc: 'Deployments, inference Gateway, and GPUs — promote a model to a served endpoint and watch it under load, all from Mission Control.',
            },
            {
              title: 'Govern',
              desc: 'Observability, Security, Costs, Marketplace, LLMOps, and Workspaces — traces, policy, chargeback, and multi-tenant notebooks in one governed surface.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="MLOps Pipelines"
          title="Pipelines that ship a model only when the metrics say so."
          subtitle="FabricWorkflow turns training into a governed DAG — jobs wait on upstream completion, deploy is gated on a metric threshold, and the whole graph can run on a cron schedule with automatic retries."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Conditional deploy',
              desc: 'A deploy step runs only when an upstream metric passes — e.g. accuracy > 0.95 — so a weak model never reaches production.',
            },
            {
              title: 'Fan-out / fan-in',
              desc: 'Train N models in parallel with a bounded concurrency, then aggregate — sweeps and ensembles as one workflow.',
            },
            {
              title: 'Scheduled retraining',
              desc: 'Cron-based execution (e.g. nightly at 02:00) keeps models fresh without a human kicking off the run.',
            },
            {
              title: 'Adaptive retries',
              desc: 'Failed jobs retry with backoff — and can retry on bigger hardware, so a transient OOM does not sink the pipeline.',
            },
          ]}
        />
        <CodePanel label="Deploy only if the trained model clears the bar">{`apiVersion: forge.ai/v1
kind: FabricWorkflow
metadata:
  name: nightly-retrain
spec:
  schedule: "0 2 * * *"        # cron — every night at 02:00
  jobs:
    - name: train
      template:
        command: [python, train.py]
      retryStrategy:
        limit: 2
        backoff: {duration: 5m}
    - name: deploy
      dependsOn: [train]
      condition: "{{jobs.train.metrics.accuracy}} > 0.95"
      template:
        command: [python, deploy.py]`}</CodePanel>

        <SectionHeader
          eyebrow="Training Productivity"
          title="The features researchers feel every single day."
          subtitle="Long training runs fail, drift, and waste GPUs. Forge ships the guardrails and time-savers as first-class CRDs — not scripts every team reinvents."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Checkpoint Guard',
              desc: 'Policy-driven checkpointing with emergency saves on GPU-health degradation, spot preemption, memory pressure, or loss divergence — validated and replicated to durable storage, auto-restored on restart.',
            },
            {
              title: 'Training Time Machine',
              desc: 'Index every checkpoint with its metrics, then fork a new run from any point with new hyperparameters. "What if I had dropped the LR at step 5000?" becomes one command.',
            },
            {
              title: 'Live Experiment',
              desc: 'Run several jobs at once on a live leaderboard, auto-stop the laggards, and report the GPU-hours and dollars saved — with plateau, divergence, and gradient-explosion detection.',
            },
            {
              title: 'Model Lineage',
              desc: 'End-to-end provenance — code, data, hyperparameters, infra, and eval — captured automatically, with immutable cryptographic hash chains for compliance and reproducibility.',
            },
            {
              title: 'Priority & Preemption',
              desc: 'Seven priority levels with SLA queue-time guarantees. Critical jobs preempt lower-priority ones — which auto-checkpoint and resume, so no work is lost.',
            },
            {
              title: 'GPU Memory Optimizer',
              desc: 'Profiles memory growth to predict OOM before it happens, auto-mitigates with gradient checkpointing or mixed precision, and right-sizes GPU requests from real usage.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="The Differentiator"
          title="Zeus — an AI ops engineer that works under approval."
          subtitle="Nutanix and Red Hat automate infrastructure. Neither ships an embedded, approval-gated AI SRE that reasons about your fleet, proposes an action, shows its blast radius, and waits for a human to sign off."
        />
        <div
          id="see-zeus-decide"
          style={{display: 'flex', justifyContent: 'center', margin: '0 auto 2.5rem', padding: '0 1rem'}}
        >
          <ForgeZeusConsole />
        </div>
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Reasons over live telemetry',
              desc: 'Utilization, queue depth, cost, topology, and incidents — Zeus sees the whole control plane, not one metric in isolation.',
            },
            {
              title: 'Proposes, never barges',
              desc: 'Every mutation is gated behind role-based approval. Zeus recommends and shows blast radius; a human signs off.',
            },
            {
              title: 'Multi-LLM with memory',
              desc: 'The model-router picks the right model per task, and Zeus runs fully air-gapped when the cluster has no internet.',
            },
            {
              title: 'Audited by construction',
              desc: 'Every approve or deny is recorded. Nothing acts silently — the SRE loop is accountable end to end.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Competitive Advantage"
          title="Replaces Five Vendors"
          subtitle="One self-hosted platform delivers what enterprises currently piece together from managed services and proprietary stacks."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'vs EKS / GKE',
              desc: 'Bare-metal GPU performance without cloud hypervisor tax. Your hardware, your data, your margins.',
            },
            {
              title: 'vs managed AI clouds',
              desc: 'No per-node licensing. Self-hosted from day one. No vendor lock-in on your AI infrastructure.',
            },
            {
              title: 'vs Databricks',
              desc: 'Self-hosted compute fabric you own. No per-GPU-hour billing surprises on training runs.',
            },
            {
              title: 'vs CoreWeave',
              desc: 'Run on your own bare metal. Same GPU density, zero egress fees, full data sovereignty.',
            },
            {
              title: 'vs Lambda Labs',
              desc: 'Enterprise-grade orchestration with RDMA and parallel filesystems. Production, not just prototyping.',
            },
            {
              title: 'vs DIY K8s + GPU',
              desc: 'Pre-integrated GPU scheduling, RDMA, and storage. Weeks of integration work eliminated.',
            },
          ]}
        />

        <SectionHeader eyebrow="Key Capabilities" title="Built for AI at Scale" />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Topology-Aware Scheduling',
              desc: 'Automatic NVLink and PCIe topology detection. Place workloads on optimal GPU combinations for maximum training throughput.',
            },
            {
              title: 'Zero-Touch NCCL',
              desc: 'Automatic NCCL configuration and tuning for distributed training. No manual env vars or topology files.',
            },
            {
              title: 'Multi-Cluster Orchestration',
              desc: 'Federate GPU resources across bare metal, EKS, GKE, and AKS from a single control plane.',
            },
            {
              title: 'Elastic Training',
              desc: 'Scale training jobs up and down dynamically based on GPU availability and priority policies.',
            },
          ]}
        />

        <SectionHeader
          eyebrow="Enterprise Day-2"
          title="Runs offline. Backs itself up. Recovers on a runbook."
          subtitle="The unglamorous operations enterprise buyers ask about on the second call — shipped, not slideware."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Air-gapped install',
              desc: 'Bundle every image, chart, and CRD into one tarball, load it into a private registry, and install fully offline — with connectivity-free verification.',
            },
            {
              title: 'Backup & disaster recovery',
              desc: 'Velero-based hourly config and daily full backups with volume snapshots, scripted restore with dry-run, and an ordered CRDs → operators → CRs → data runbook.',
            },
            {
              title: 'Open standards, no lock-in',
              desc: 'Kubernetes, CRDs, Helm, Prometheus, OCI, Velero, KubeVirt, and Qdrant — portable building blocks, not a proprietary format you can never leave.',
            },
            {
              title: 'Self-hosted from day one',
              desc: 'Your hardware, your data, your registry. No per-node licensing, no phone-home, full data sovereignty.',
            },
          ]}
        />

        <SuiteProductCapabilities productId="forge" />

        <ClientPresentationSection productId="forge" />
        <TrialSection />
        <SuiteProductFooter
          productId="forge"
          ctaTitle="Ready to own your GPU compute?"
          ctaSubtitle="See how Forge delivers 95%+ GPU utilization with Kubernetes-native orchestration -- fully self-hosted and enterprise-ready."
          secondaryCta={{label: 'Read the Docs', to: '/docs/forge#installation'}}
        />
      </PageContent>
    </ProductPage>
  );
}
