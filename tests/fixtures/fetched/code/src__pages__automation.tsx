// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {platform} from '../data/platform-stats';
import {
  ProductPage,
  PageContent,
  SectionHeader,
  FeatureGrid,
  CTASection,
  MarketingHero,
  RelatedBlogSection,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';

const codeBlockStyle: React.CSSProperties = {
  background: '#0a0a0a',
  border: '1px solid rgba(240, 88, 58, 0.1)',
  borderRadius: '12px',
  padding: '1.5rem 2rem',
  fontFamily: "'JetBrains Mono', monospace",
  fontSize: '0.82rem',
  lineHeight: 1.7,
  color: '#c9d1d9',
  overflowX: 'auto',
  whiteSpace: 'pre',
  margin: 0,
  textAlign: 'left' as const,
};

const codeLabelStyle: React.CSSProperties = {
  fontFamily: "'JetBrains Mono', monospace",
  fontSize: '0.75rem',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
  marginBottom: '0.5rem',
  color: 'rgba(240, 88, 58, 0.8)',
};

function CodeBlock({label, children}: {label: string; children: string}) {
  return (
    <div style={{marginBottom: '2rem'}}>
      <div style={codeLabelStyle}>{label}</div>
      <pre style={codeBlockStyle}>{children}</pre>
    </div>
  );
}

export default function Automation(): ReactNode {
  return (
    <ProductPage
      title="CI/CD & Automation"
      description="Automate VM migrations with a full REST API, CLI, YAML manifests, and CI/CD integration."
    >
      <MarketingHero pageId="automation" />

      <PageContent>
        {/* Four Ways to Automate */}
        <FeatureGrid
          features={[
            {
              title: 'REST API',
              desc: `${platform.apiEndpoints} endpoints covering VM inventory, export, conversion, deployment, scheduling, webhooks, and system management. OpenAPI 3.0 specification available.`,
            },
            {
              title: 'CLI (hyperctl)',
              desc: 'Full-featured command-line interface that wraps every API endpoint. Scriptable output formats (JSON, YAML, table) for shell and automation pipelines.',
            },
            {
              title: 'YAML Manifests',
              desc: 'Define entire migration workflows declaratively. Version-controlled, auditable, with dry-run validation before execution.',
            },
            {
              title: 'Webhook Notifications',
              desc: 'Push real-time notifications to Slack, Discord, Microsoft Teams, PagerDuty, or any HTTP endpoint.',
            },
          ]}
          columns={2}
        />

        {/* Code Examples */}
        <SectionHeader
          eyebrow="Code Examples"
          title="Four Ways to Migrate"
          subtitle="Every migration operation is accessible through REST, CLI, YAML, and webhooks. Pick the interface that fits your workflow."
        />

        <div style={{maxWidth: 800, margin: '0 auto 4rem'}}>
          <CodeBlock label="REST API">{`curl -sk -X POST https://your-server:5080/api/v1/jobs \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "type": "export",
    "provider": "vsphere",
    "vm_name": "web-server-01",
    "format": "qcow2",
    "options": {"compress": true}
  }'`}</CodeBlock>

          <CodeBlock label="CLI">{`h2kvmctl --config - <<EOF
command: vsphere
vs_action: export_vm
vs_vm_name: web-server-01
output_dir: /exports
out_format: qcow2
compress: true
emit_domain_xml: true
EOF`}</CodeBlock>

          <CodeBlock label="YAML Manifest">{`migrations:
  - name: web-server-01
    source:
      provider: vsphere
      datacenter: DC1
    target:
      format: qcow2
      deploy: libvirt
    options:
      compress: true
      regen_initramfs: true
      fstab_mode: stabilize-all`}</CodeBlock>

          <CodeBlock label="Webhook Payload">{`{
  "event": "job.completed",
  "job_id": "job-a1b2c3d4",
  "vm_name": "web-server-01",
  "status": "success",
  "duration_seconds": 342,
  "output": {
    "format": "qcow2",
    "path": "/exports/web-server-01.qcow2",
    "size_bytes": 8589934592
  }
}`}</CodeBlock>
        </div>

        {/* CI/CD Integrations */}
        <SectionHeader eyebrow="Integrations" title="Integrate With Your Pipeline" />
        <FeatureGrid
          features={[
            {
              title: 'Jenkins',
              desc: 'Trigger migrations from Jenkins pipelines with shell steps or the HyperSDK Platform plugin.',
            },
            {
              title: 'GitLab CI',
              desc: 'Add migration stages to your .gitlab-ci.yml. Schedule nightly exports or run on-demand.',
            },
            {
              title: 'GitHub Actions',
              desc: 'Use the hypersdk/migrate-action for parallel multi-VM migrations in workflows.',
            },
            {
              title: 'Terraform',
              desc: 'Manage migration jobs alongside your existing Terraform infrastructure-as-code.',
            },
          ]}
          columns={2}
        />

        {/* CTA */}
        <RelatedBlogSection links={solutionPageBlogLinks.automation} />

        <CTASection
          title="See the API Documentation"
          subtitle="Explore the full API reference and start automating your migration pipeline today."
          primaryCta={{label: 'See the API Documentation', to: '/docs/intro'}}
        />
      </PageContent>
    </ProductPage>
  );
}
