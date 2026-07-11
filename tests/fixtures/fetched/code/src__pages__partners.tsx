// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {
  ProductPage,
  PageContent,
  SectionHeader,
  CTASection,
  RelatedBlogSection,
  styles,
  MarketingHero,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';

type IntegrationType = 'Native' | 'API' | 'Webhook' | 'Metrics';

const integrationColors: Record<IntegrationType, {bg: string; border: string; text: string}> = {
  Native: {bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.25)', text: '#22c55e'},
  API: {bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.25)', text: '#3b82f6'},
  Webhook: {bg: 'rgba(139, 92, 246, 0.1)', border: 'rgba(139, 92, 246, 0.25)', text: '#8b5cf6'},
  Metrics: {bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.25)', text: '#f59e0b'},
};

const partners: {
  name: string;
  desc: string;
  integration: IntegrationType;
  docsLink: string;
}[] = [
  {
    name: 'Enterprise Linux',
    desc: 'KVM and libvirt targets on Rocky, AlmaLinux, Oracle Linux, and other RPM-based enterprise distributions.',
    integration: 'Native',
    docsLink: '/docs/providers',
  },
  {
    name: 'VMware',
    desc: 'Source platform integration with vSphere and ESXi for seamless VM export and migration workflows.',
    integration: 'Native',
    docsLink: '/docs/providers',
  },
  {
    name: 'Nutanix',
    desc: 'Nutanix AHV and Prism integration for HCI estate export — same pipeline as vSphere exit programs.',
    integration: 'Native',
    docsLink: '/docs/providers',
  },
  {
    name: 'AWS',
    desc: 'Amazon EC2 export, S3 storage integration, and AMI creation for cloud-native VM deployment.',
    integration: 'API',
    docsLink: '/docs/api',
  },
  {
    name: 'Microsoft',
    desc: 'Azure Compute and Hyper-V migration support for hybrid cloud and Windows-centric environments.',
    integration: 'API',
    docsLink: '/docs/api',
  },
  {
    name: 'Google Cloud',
    desc: 'GCP Compute Engine integration for VM import, disk conversion, and workload deployment.',
    integration: 'API',
    docsLink: '/docs/api',
  },
  {
    name: 'Oracle',
    desc: 'OCI integration for VM migration to Oracle Cloud Infrastructure with full lifecycle management.',
    integration: 'API',
    docsLink: '/docs/providers',
  },
  {
    name: 'Kubernetes',
    desc: 'KubeVirt deployment and management for running VMs as native Kubernetes resources.',
    integration: 'Native',
    docsLink: '/docs/providers',
  },
  {
    name: 'Prometheus',
    desc: 'Monitoring and metrics integration with built-in exporters for migration observability.',
    integration: 'Metrics',
    docsLink: '/docs/api',
  },
];

const partnerPrograms = [
  {
    title: 'Technology Partners',
    desc: 'Integrate your product with HyperSDK Platform. Access our provider plugin system, REST API, and webhook framework to build native integrations.',
    cta: 'Explore Integrations',
    to: '/docs/api',
    accent: '#3b82f6',
  },
  {
    title: 'MSP Partners',
    desc: 'White-label HyperSDK Platform for your customers. Offer managed VM migration services with our multi-tenant platform, custom branding, and dedicated support.',
    cta: 'MSP Program Details',
    to: '/contact?intent=partners',
    accent: '#8b5cf6',
  },
  {
    title: 'Consulting Partners',
    desc: 'Certified migration delivery partners. Get trained on HyperSDK Platform, access priority support, and deliver VMware exit projects with confidence.',
    cta: 'Apply for Certification',
    to: '/contact?intent=partners',
    accent: '#f59e0b',
  },
];

export default function Partners(): ReactNode {
  return (
    <ProductPage
      title="Partners"
      description="HyperSDK Platform partner ecosystem — technology integrations across cloud providers and infrastructure platforms."
    >
      <MarketingHero pageId="partners" />

      <PageContent>
        {/* Technology Partners Grid */}
        <SectionHeader eyebrow="Technology Partners" title="Integrated Platforms" />
        <div className={styles.gridCol4} style={{marginBottom: '3rem'}}>
          {partners.map((p) => {
            const badge = integrationColors[p.integration];
            return (
              <div key={p.name} className={styles.featureCard} style={{textAlign: 'center', position: 'relative'}}>
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: 16,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 1.25rem',
                    background: 'linear-gradient(135deg, rgba(255, 140, 0, 0.15), rgba(255, 140, 0, 0.05))',
                    border: '1px solid rgba(255, 140, 0, 0.2)',
                  }}
                >
                  <span
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: 'var(--hs-accent-light)',
                    }}
                  >
                    {p.name.slice(0, 3).toUpperCase()}
                  </span>
                </div>

                {/* Integration Type Badge */}
                <div
                  style={{
                    display: 'inline-block',
                    background: badge.bg,
                    border: `1px solid ${badge.border}`,
                    borderRadius: 6,
                    padding: '0.15rem 0.6rem',
                    marginBottom: '0.75rem',
                  }}
                >
                  <span
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      color: badge.text,
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                    }}
                  >
                    {p.integration}
                  </span>
                </div>

                <h3 className={styles.featureCardTitle}>{p.name}</h3>
                <p className={styles.featureCardDesc} style={{marginBottom: '1rem'}}>
                  {p.desc}
                </p>

                {/* Documentation Link */}
                <Link
                  to={p.docsLink}
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    color: 'var(--hs-accent-light)',
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                  }}
                >
                  Documentation &rarr;
                </Link>
              </div>
            );
          })}
        </div>

        {/* Become a Partner */}
        <SectionHeader
          eyebrow="Partner Programs"
          title="Become a Partner"
          subtitle="Join the HyperSDK Platform ecosystem. We offer three partner tracks designed for technology vendors, managed service providers, and consulting firms."
        />
        <div className={styles.gridCol3} style={{marginBottom: '4rem'}}>
          {partnerPrograms.map((prog) => (
            <div
              key={prog.title}
              className={styles.featureCard}
              style={{
                display: 'flex',
                flexDirection: 'column',
                border: `1px solid ${prog.accent}22`,
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 4,
                  borderRadius: 2,
                  background: prog.accent,
                  marginBottom: '1.5rem',
                  opacity: 0.8,
                }}
              />
              <h3
                style={{
                  color: 'var(--hs-text-heading)',
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  marginBottom: '0.75rem',
                }}
              >
                {prog.title}
              </h3>
              <p
                style={{
                  color: 'var(--hs-text-muted)',
                  fontSize: '0.9rem',
                  lineHeight: 1.7,
                  flex: 1,
                  marginBottom: '1.5rem',
                }}
              >
                {prog.desc}
              </p>
              <Link
                to={prog.to}
                className={styles.secondaryBtn}
                style={{
                  justifyContent: 'center',
                  padding: '0.7rem 1.5rem',
                  fontSize: '0.9rem',
                }}
              >
                {prog.cta}
              </Link>
            </div>
          ))}
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.partners} />

        {/* CTA */}
        <CTASection
          title="Ready to Partner?"
          subtitle="Interested in integrating with HyperSDK Platform or offering it as part of your solution? Let's talk about how we can work together."
          primaryCta={{label: 'Contact Partnerships', to: '/contact?intent=partners'}}
          secondaryCta={{label: 'Learn More', to: '/docs/intro'}}
        />
      </PageContent>
    </ProductPage>
  );
}
