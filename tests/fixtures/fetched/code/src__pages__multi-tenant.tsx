// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {
  ProductPage,
  PageContent,
  SectionHeader,
  FeatureGrid,
  CTASection,
  RelatedBlogSection,
  IntegrationDiagram,
  styles,
  MarketingHero,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';

export default function MultiTenant(): ReactNode {
  return (
    <ProductPage
      title="Multi-Tenant Migration"
      description="Migrate VMs for multiple tenants with full isolation, audit trails, and white-label branding."
    >
      <MarketingHero pageId="multi-tenant" />

      <PageContent>
        {/* MSP Benefits - custom accent styling */}
        <div className={`${styles.featureGrid} ${styles.featureGridCol2}`}>
          {[
            {
              title: 'White-Label',
              desc: 'Brand the dashboard and API with your company identity. Your customers see your brand, not ours.',
            },
            {
              title: 'Per-Tenant Billing',
              desc: 'Built-in metering tracks VM count, storage consumed, and API calls per tenant for accurate chargeback.',
            },
            {
              title: 'Complete Isolation',
              desc: 'Storage, access control, audit logs, and network are all fully isolated between tenants.',
            },
            {
              title: 'Priority Support',
              desc: 'MSP partners receive 4-hour SLA support, dedicated technical account manager, and early access to new features.',
            },
          ].map((benefit) => (
            <div
              key={benefit.title}
              style={{
                background: 'rgba(16, 185, 129, 0.04)',
                border: '1px solid rgba(16, 185, 129, 0.12)',
                borderRadius: 16,
                padding: '2rem',
              }}
            >
              <h3
                style={{
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  color: 'var(--hs-success-light)',
                  marginBottom: '0.75rem',
                }}
              >
                {benefit.title}
              </h3>
              <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', lineHeight: 1.7, margin: 0}}>
                {benefit.desc}
              </p>
            </div>
          ))}
        </div>

        <SectionHeader eyebrow="Scale" title="Built to Scale" />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Parallel Execution',
              desc: 'Run migrations for multiple tenants simultaneously with configurable concurrency limits and resource quotas.',
            },
            {
              title: 'Failure Isolation',
              desc: 'A failed migration for one tenant never affects other tenants. Automatic retry with exponential backoff.',
            },
            {
              title: 'Progress Tracking',
              desc: 'Real-time dashboards show per-tenant and per-VM migration status. Webhook notifications on completion.',
            },
            {
              title: 'Declarative Batch Ops',
              desc: 'Define batch migrations in YAML manifests. Version-controlled, auditable, with dry-run validation.',
            },
          ]}
        />

        {/* Revenue Opportunity */}
        <SectionHeader
          eyebrow="Revenue"
          title="Revenue Opportunity"
          subtitle="Migration-as-a-Service is a high-margin, recurring revenue stream for managed service providers."
        />
        <div className={`${styles.featureGrid} ${styles.featureGridCol2}`}>
          {[
            {
              title: '$150 - $500 / VM',
              desc: 'Average MSP migration service charge per VM. Price varies by complexity, OS type, and SLA requirements.',
            },
            {
              title: '$15K - $50K / Month',
              desc: 'Recurring revenue from 100 VMs/month. Ongoing management and optimization services add further margin.',
            },
            {
              title: 'White-Label Dashboard',
              desc: 'Premium pricing justified by branded, professional dashboard experience. Your customers see your brand, building trust and loyalty.',
            },
            {
              title: 'Per-Tenant Billing',
              desc: 'Built-in metering and billing integration. Track usage per tenant automatically and generate invoices with zero manual effort.',
            },
          ].map((item) => (
            <div
              key={item.title}
              className={styles.featureCard}
              style={{borderColor: 'rgba(16, 185, 129, 0.15)', background: 'rgba(16, 185, 129, 0.03)'}}
            >
              <h3
                style={{
                  color: 'var(--hs-success-light)',
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  marginBottom: '0.75rem',
                }}
              >
                {item.title}
              </h3>
              <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', lineHeight: 1.7, margin: 0}}>{item.desc}</p>
            </div>
          ))}
        </div>

        {/* Tenant Dashboard */}
        <SectionHeader
          eyebrow="Dashboard"
          title="Tenant Dashboard"
          subtitle="A single MSP portal gives you full visibility into every tenant's migration status and revenue."
        />
        <IntegrationDiagram
          content={`MSP Portal
\u251C\u2500\u2500 Tenant A   (50 VMs,  $7,500/mo)
\u251C\u2500\u2500 Tenant B   (200 VMs, $30,000/mo)
\u251C\u2500\u2500 Tenant C   (25 VMs,  $3,750/mo)
\u2514\u2500\u2500 Tenant D   (100 VMs, $15,000/mo)
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
Total:       375 VMs, $56,250/mo`}
        />
        <div style={{marginBottom: '5rem'}} />

        <RelatedBlogSection links={solutionPageBlogLinks.multiTenant} />

        <CTASection
          title="Partner With Us"
          subtitle="Join the HyperSDK Platform MSP partner program. White-label the platform, offer migration-as-a-service, and grow your business with enterprise-grade tooling."
          primaryCta={{label: 'Partner With Us', to: '/contact?intent=partners'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=partners'}}
        />
      </PageContent>
    </ProductPage>
  );
}
