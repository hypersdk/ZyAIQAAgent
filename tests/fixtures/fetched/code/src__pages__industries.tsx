// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {ProductPage, MarketingHero, PageContent, CTASection, styles, RelatedBlogSection} from '../components/shared';
import {getIndustriesPageCopy, getIndustryCardOverride} from '../data/industries-locale';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {platform} from '../data/platform-stats';

interface IndustryLink {
  label: string;
  to: string;
}

interface Industry {
  id: string;
  icon: string;
  title: string;
  challenges: string[];
  solution: string;
  learnMore: IndustryLink[];
}

const industries: Industry[] = [
  {
    id: 'financial-services',
    icon: '\u{1F3E6}',
    title: 'Financial Services',
    challenges: [
      'Regulatory compliance for SOX, PCI-DSS, and Basel III',
      'Data sovereignty requirements across jurisdictions',
      'Zero-downtime migration for trading and risk systems',
      'Cost optimization after VMware licensing changes',
    ],
    solution:
      'HyperSDK Platform provides incremental export with Changed Block Tracking for near-zero-downtime cutovers during off-peak windows. Full manifest tracking and SHA-256 checksum verification deliver the audit trail required for regulatory compliance. For TEE-regulated workloads, Aether and Ragnarok add hardware attestation, measured images, and attest-gated secrets on KubeVirt.',
    learnMore: [
      {label: 'Compliance', to: '/compliance'},
      {label: 'Confidential computing', to: '/confidential-computing'},
      {label: 'Case Studies', to: '/case-studies'},
    ],
  },
  {
    id: 'healthcare',
    icon: '\u{1F3E5}',
    title: 'Healthcare',
    challenges: [
      'HIPAA-compliant data handling throughout migration',
      'Minimal downtime for EMR and PACS systems',
      'Complete audit trails for all migration operations',
      'Encrypted transfer of protected health information',
    ],
    solution:
      'HyperSDK Platform encrypts data in transit and at rest, provides detailed audit logs for every migration operation, and supports air-gapped deployments for environments without internet connectivity. Automated VirtIO driver injection handles Windows Server workloads running critical healthcare applications.',
    learnMore: [
      {label: 'Compliance', to: '/compliance'},
      {label: 'Case Studies', to: '/case-studies'},
    ],
  },
  {
    id: 'government',
    icon: '\u{1F3DB}',
    title: 'Government',
    challenges: [
      'FedRAMP and NIST compliance framework alignment',
      'Air-gapped deployment for classified environments',
      'Security hardening and RBAC for multi-tenant access',
      'Vendor-neutral infrastructure to avoid lock-in',
    ],
    solution:
      'HyperSDK Platform deploys in fully air-gapped configurations with no external network dependencies. RBAC, comprehensive audit logging, and configurable security policies satisfy SOC2 and FedRAMP control requirements. For sovereign cloud, Aether sovereign mode and Ragnarok TEE attestation provide hardware-rooted trust on SEV-SNP and TDX nodes.',
    learnMore: [
      {label: 'Compliance', to: '/compliance'},
      {label: 'Confidential computing', to: '/confidential-computing'},
      {label: 'Air-Gap Deployment', to: '/airgap'},
    ],
  },
  {
    id: 'manufacturing',
    icon: '\u{1F3ED}',
    title: 'Manufacturing',
    challenges: [
      'Edge computing and factory floor VM management',
      'OT/IT convergence for industrial control systems',
      'Precise hardware compatibility during migration',
      'Sustainability targets for carbon emissions reduction',
    ],
    solution: `HyperSDK Platform preserves VM configurations including CPU topology, memory allocation, and network settings across providers. Carbon-aware scheduling aligns migration operations with sustainability targets. The ${platform.dashboardViews} dashboard views provide plant operations teams with real-time visibility into migration progress across distributed sites.`,
    learnMore: [{label: 'Edge Computing', to: '/edge-computing'}],
  },
  {
    id: 'telecommunications',
    icon: '\u{1F4E1}',
    title: 'Telecommunications',
    challenges: [
      'Network function virtualization (NFV) workload migration',
      'Carrier-grade reliability with 99.999% uptime requirements',
      'High-throughput data transfer for large VM images',
      'Multi-site orchestration across distributed data centers',
    ],
    solution:
      "HyperSDK Platform handles large VM image transfers with resume support for unreliable network conditions. Scheduled migration with cron-based automation enables maintenance-window operations. The platform's multi-provider architecture supports the heterogeneous infrastructure typical in telecom environments.",
    learnMore: [{label: 'Multi-Tenant', to: '/multi-tenant'}],
  },
  {
    id: 'energy-utilities',
    icon: '\u{26A1}',
    title: 'Energy & Utilities',
    challenges: [
      'SCADA and industrial control system VM migration',
      'Remote site support with limited connectivity',
      'Legacy infrastructure modernization',
      'Compliance with NERC CIP and energy sector regulations',
    ],
    solution:
      'HyperSDK Platform supports offline and air-gapped migration for remote sites with limited connectivity. The platform handles legacy VM formats and provides automated conversion to modern infrastructure. Changed Block Tracking minimizes data transfer for bandwidth-constrained environments, and comprehensive audit logging satisfies energy sector compliance requirements.',
    learnMore: [{label: 'Cloud Repatriation', to: '/cloud-repatriation'}],
  },
];

export default function Industries(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const copy = getIndustriesPageCopy(i18n.currentLocale);

  return (
    <ProductPage
      title="Industries"
      description="HyperSDK Platform solutions for financial services, healthcare, government, manufacturing, telecom, and energy."
    >
      <MarketingHero pageId="industries" />

      <PageContent>
        {/* Industry Cards */}
        <div style={{display: 'flex', flexDirection: 'column', gap: '2rem', marginBottom: '3rem'}}>
          {industries.map((ind) => {
            const card = getIndustryCardOverride(ind.id, i18n.currentLocale);
            const title = card.title ?? ind.title;
            return (
              <div
                key={ind.id}
                id={ind.id}
                className={`${styles.featureCard} ${styles.splitGrid}`}
                style={{
                  padding: '3rem',
                }}
              >
                <div>
                  <div
                    style={{
                      width: 52,
                      height: 52,
                      borderRadius: 14,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1.25rem',
                      fontSize: '1.5rem',
                      background: 'linear-gradient(135deg, rgba(255, 140, 0, 0.15), rgba(255, 140, 0, 0.05))',
                      border: '1px solid rgba(255, 140, 0, 0.2)',
                    }}
                  >
                    {ind.icon}
                  </div>
                  <h2
                    style={{
                      fontSize: '1.8rem',
                      fontWeight: 700,
                      color: 'var(--hs-text-heading)',
                      marginBottom: '1rem',
                    }}
                  >
                    {title}
                  </h2>
                  <h3 className={styles.monoLabel}>{copy.keyChallenges}</h3>
                  <ul
                    style={{
                      listStyle: 'none',
                      padding: 0,
                      margin: 0,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.6rem',
                    }}
                  >
                    {ind.challenges.map((c) => (
                      <li
                        key={c}
                        style={{
                          color: 'var(--hs-text-body)',
                          fontSize: '0.9rem',
                          paddingLeft: '1.5rem',
                          position: 'relative',
                          lineHeight: 1.5,
                        }}
                      >
                        <span
                          style={{
                            position: 'absolute',
                            left: 0,
                            color: 'var(--hs-warning)',
                            fontWeight: 700,
                          }}
                        >
                          {'\u25B8'}
                        </span>
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className={styles.monoLabel}>{copy.howWeHelp}</h3>
                  <p
                    style={{
                      color: 'var(--hs-text-muted)',
                      fontSize: '0.95rem',
                      lineHeight: 1.8,
                      marginBottom: '1.5rem',
                    }}
                  >
                    {ind.solution}
                  </p>
                  <div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap'}}>
                    <Link
                      to="/contact?intent=demo"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                        color: 'var(--hs-accent-light)',
                        fontWeight: 600,
                        fontSize: '0.95rem',
                        textDecoration: 'none',
                      }}
                    >
                      {copy.talkToSales} <span>{'\u2192'}</span>
                    </Link>
                    {ind.learnMore.map((lm) => (
                      <Link
                        key={lm.to}
                        to={lm.to}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          color: '#a78bfa',
                          fontWeight: 600,
                          fontSize: '0.95rem',
                          textDecoration: 'none',
                        }}
                      >
                        {lm.label} <span>{'\u2192'}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA */}
        <RelatedBlogSection links={solutionPageBlogLinks.industries} />

        <CTASection
          title={copy.ctaTitle}
          subtitle={copy.ctaSubtitle}
          primaryCta={{label: copy.contactSales, to: '/contact?intent=sales'}}
          secondaryCta={{label: copy.scheduleDemo, to: '/contact?intent=demo'}}
        />
      </PageContent>
    </ProductPage>
  );
}
