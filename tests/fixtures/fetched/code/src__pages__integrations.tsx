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
  styles,
  MarketingHero,
  RelatedBlogSection,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';

const integrations = [
  {icon: '\u2699\uFE0F', name: 'Jenkins', desc: 'CI/CD pipeline automation for scheduled and triggered migrations.'},
  {
    icon: '\uD83E\uDD8A',
    name: 'GitLab CI',
    desc: 'Automated migration workflows integrated into your GitLab pipelines.',
  },
  {
    icon: '\uD83D\uDC19',
    name: 'GitHub Actions',
    desc: 'Infrastructure as code with migration manifests in your repositories.',
  },
  {
    icon: '\uD83C\uDFD7\uFE0F',
    name: 'Terraform',
    desc: 'Declarative migration manifests using HCL for reproducible workflows.',
  },
  {icon: '\uD83D\uDD27', name: 'Ansible', desc: 'Configuration management and post-migration provisioning playbooks.'},
  {
    icon: '\uD83D\uDD25',
    name: 'Prometheus',
    desc: 'Monitoring and alerting with native metrics export from HyperSDK Platform.',
  },
  {
    icon: '\uD83D\uDCCA',
    name: 'Grafana',
    desc: 'Dashboard visualization with pre-built HyperSDK Platform migration panels.',
  },
  {icon: '\uD83D\uDCAC', name: 'Slack', desc: 'Real-time migration notifications, alerts, and status updates.'},
  {
    icon: '\u2638\uFE0F',
    name: 'Kubernetes',
    desc: 'KubeVirt deployment with custom resources for VM lifecycle management.',
  },
  {
    icon: '\uD83D\uDC33',
    name: 'Docker',
    desc: 'Containerized deployment of HyperSDK Platform for portable, consistent environments.',
  },
];

const workflows = [
  {
    title: 'Jenkins Pipeline',
    language: 'groovy',
    code: `pipeline {
  agent any
  environment {
    HYPERSDK_URL = credentials('hypersdk-url')
    HYPERSDK_TOKEN = credentials('hypersdk-token')
  }
  stages {
    stage('Export VM') {
      steps {
        sh """
          curl -X POST \\
            \${HYPERSDK_URL}/api/v1/jobs \\
            -H "Authorization: Bearer \${HYPERSDK_TOKEN}" \\
            -H "Content-Type: application/json" \\
            -d '{"type":"export","vm_name":"prod-web-01"}'
        """
      }
    }
    stage('Convert') {
      steps {
        sh 'h2kvmctl --config convert.yaml'
      }
    }
    stage('Deploy') {
      steps {
        sh 'h2kvmctl --config deploy.yaml'
      }
    }
  }
}`,
  },
  {
    title: 'GitHub Actions',
    language: 'yaml',
    code: `name: VM Migration
on:
  workflow_dispatch:
    inputs:
      vm_name:
        description: 'VM to migrate'
        required: true

jobs:
  migrate:
    runs-on: self-hosted
    steps:
      - name: Export VM from VMware
        run: |
          curl -X POST \\
            \${{ secrets.HYPERSDK_URL }}/api/v1/jobs \\
            -H "Authorization: Bearer \${{ secrets.HYPERSDK_TOKEN }}" \\
            -d '{"type":"export","vm_name":"\${{ inputs.vm_name }}"}'

      - name: Convert and Deploy
        run: |
          h2kvmctl --config migrate.yaml \\
            --source \${{ inputs.vm_name }}.vmdk \\
            --deploy libvirt`,
  },
  {
    title: 'Ansible Playbook',
    language: 'yaml',
    code: `---
- name: Migrate VMs with HyperSDK Platform
  hosts: migration_server
  vars:
    hypersdk_url: "https://hypersdk.internal:8443"
    vms_to_migrate:
      - prod-web-01
      - prod-db-01
      - prod-app-01

  tasks:
    - name: Export and convert each VM
      uri:
        url: "{{ hypersdk_url }}/api/v1/jobs"
        method: POST
        headers:
          Authorization: "Bearer {{ hypersdk_token }}"
        body_format: json
        body:
          type: export
          vm_name: "{{ item }}"
          options:
            format: qcow2
            deploy_target: libvirt
      loop: "{{ vms_to_migrate }}"

    - name: Wait for all jobs to complete
      uri:
        url: "{{ hypersdk_url }}/api/v1/jobs/{{ item }}/status"
        method: GET
        headers:
          Authorization: "Bearer {{ hypersdk_token }}"
      register: job_status
      until: job_status.json.state == "completed"
      retries: 60
      delay: 30
      loop: "{{ job_ids }}"`,
  },
];

export default function IntegrationsPage(): ReactNode {
  return (
    <ProductPage
      title="Integrations"
      description="HyperSDK Platform integrates with your existing tools and workflows."
    >
      <MarketingHero pageId="integrations" />

      <PageContent>
        {/* Integration Grid */}
        <div
          className={styles.gridCol3}
          style={{
            marginBottom: '4rem',
          }}
        >
          {integrations.map((item) => (
            <div key={item.name} className={styles.featureCard}>
              <div
                style={{
                  fontSize: '2rem',
                  marginBottom: '1rem',
                  width: 52,
                  height: 52,
                  borderRadius: 12,
                  background: 'rgba(255, 140, 0, 0.06)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {item.icon}
              </div>
              <h3 className={styles.featureCardTitle}>{item.name}</h3>
              <p className={styles.featureCardDesc}>{item.desc}</p>
            </div>
          ))}
        </div>

        {/* How it works */}
        <SectionHeader
          eyebrow="How It Works"
          title="Connect in Minutes"
          subtitle={`HyperSDK Platform provides a REST API with ${platform.apiEndpoints} endpoints, webhook notifications, and native metric exports. Any tool that can make HTTP requests or consume Prometheus metrics can integrate with HyperSDK Platform.`}
        />
        <FeatureGrid
          columns={3}
          features={[
            {title: '01 - API Access', desc: 'Full REST API with OpenAPI documentation. Use any HTTP client or SDK.'},
            {title: '02 - Webhooks', desc: 'Real-time event notifications for job status, errors, and completions.'},
            {title: '03 - Metrics', desc: 'Prometheus-compatible metrics endpoint for monitoring and alerting.'},
          ]}
        />

        {/* Real Workflows */}
        <SectionHeader
          eyebrow="Real Workflows"
          title="Production-Ready Examples"
          subtitle="Copy these examples into your CI/CD pipelines and automation tools to start migrating VMs programmatically."
        />

        <div style={{display: 'flex', flexDirection: 'column', gap: '2rem', marginBottom: '4rem'}}>
          {workflows.map((wf) => (
            <div key={wf.title} className={styles.featureCard} style={{padding: '2rem'}}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  marginBottom: '1.25rem',
                }}
              >
                <h3
                  style={{
                    color: 'var(--hs-text-heading)',
                    fontSize: '1.2rem',
                    fontWeight: 700,
                    margin: 0,
                  }}
                >
                  {wf.title}
                </h3>
                <span
                  style={{
                    background: 'rgba(255, 140, 0, 0.1)',
                    color: 'var(--hs-accent-light)',
                    padding: '0.2rem 0.6rem',
                    borderRadius: 6,
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    border: '1px solid rgba(255, 140, 0, 0.2)',
                    textTransform: 'uppercase',
                  }}
                >
                  {wf.language}
                </span>
              </div>
              <pre
                style={{
                  background: 'rgba(0, 0, 0, 0.5)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: 8,
                  padding: '1.25rem 1.5rem',
                  overflow: 'auto',
                  margin: 0,
                  fontSize: '0.82rem',
                  lineHeight: 1.6,
                  color: '#e2e8f0',
                  fontFamily: '"JetBrains Mono", "Fira Code", "SF Mono", Consolas, monospace',
                }}
              >
                <code>{wf.code}</code>
              </pre>
            </div>
          ))}
        </div>

        {/* CTA */}
        <RelatedBlogSection links={solutionPageBlogLinks.integrations} />

        <CTASection
          title="Need a Custom Integration?"
          subtitle="Our team can help you build custom integrations for your specific environment and tools."
          primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
          secondaryCta={{label: 'View Documentation', to: '/docs/intro'}}
        />
      </PageContent>
    </ProductPage>
  );
}
