// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {ProductPage, MarketingHero, PageContent, SectionHeader, CTASection, styles} from '../components/shared';
import {getWhyHypersdkPageCopy} from '../data/why-hypersdk-locale';
import {platform} from '../data/platform-stats';
import {cloudProvidersCompactList} from '../data/cloud-providers';

type ComparisonRow = {
  feature: string;
  hypersdk: boolean | string;
  virtv2v: boolean | string;
  mtv: boolean | string;
  cloudendure: boolean | string;
  awshub: boolean | string;
  winner?: boolean;
};

const comparisonRows: ComparisonRow[] = [
  {feature: 'Multi-cloud support', hypersdk: true, virtv2v: false, mtv: false, cloudendure: true, awshub: true},
  {feature: 'Web dashboard', hypersdk: true, virtv2v: false, mtv: true, cloudendure: true, awshub: true},
  {feature: 'API-driven', hypersdk: true, virtv2v: false, mtv: true, cloudendure: true, awshub: true},
  {
    feature: 'Carbon-aware scheduling',
    hypersdk: true,
    virtv2v: false,
    mtv: false,
    cloudendure: false,
    awshub: false,
    winner: true,
  },
  {
    feature: 'Provider plugins (10+)',
    hypersdk: true,
    virtv2v: false,
    mtv: false,
    cloudendure: false,
    awshub: false,
    winner: true,
  },
  {feature: 'Cost estimation', hypersdk: true, virtv2v: false, mtv: false, cloudendure: false, awshub: true},
  {feature: 'Windows support', hypersdk: true, virtv2v: true, mtv: true, cloudendure: true, awshub: true},
  {feature: 'Linux support', hypersdk: true, virtv2v: true, mtv: true, cloudendure: true, awshub: true},
  {feature: 'KubeVirt integration', hypersdk: true, virtv2v: true, mtv: true, cloudendure: false, awshub: false},
  {feature: 'Offline migration', hypersdk: true, virtv2v: true, mtv: false, cloudendure: false, awshub: false},
  {
    feature: 'Pricing',
    hypersdk: 'Licensed*',
    virtv2v: 'Free',
    mtv: '$50K+/yr',
    cloudendure: '$$$$',
    awshub: '$$$',
    winner: true,
  },
  {
    feature: 'Deployment time',
    hypersdk: '5 min',
    virtv2v: 'Hours',
    mtv: 'Days',
    cloudendure: 'Days',
    awshub: 'Weeks',
    winner: true,
  },
  {
    feature: 'Manual work per VM',
    hypersdk: 'Automated',
    virtv2v: 'High',
    mtv: 'Medium',
    cloudendure: 'Medium',
    awshub: 'Medium',
    winner: true,
  },
];

const differentiators = [
  {
    number: '01',
    title: `Only Platform with ${platform.cloudProviders} Cloud Providers`,
    description: `HyperSDK Platform supports ${cloudProvidersCompactList} through a single, consistent API. No other migration platform offers this breadth of provider coverage with a unified interface.`,
  },
  {
    number: '02',
    title: 'Industry-First Carbon-Aware Scheduling',
    description:
      'Schedule VM migrations and operations during low-carbon periods using real-time electricity grid intensity data. HyperSDK Platform is the only enterprise migration platform with built-in carbon awareness, helping organizations meet sustainability goals without manual intervention.',
  },
  {
    number: '03',
    title: `${platform.dashboardViews} Dashboard Views`,
    description: `Monitor every aspect of your migration infrastructure through ${platform.dashboardViews} purpose-built dashboard views across all products. From VM inventory and migration progress to provider health and cost analytics, the HyperSDK Platform platform provides complete operational visibility in a single interface.`,
  },
  {
    number: '04',
    title: 'Upload and Deploy from Browser',
    description:
      'The HyperSDK Platform web dashboard enables drag-and-drop VM image upload with automatic format detection, conversion, and deployment to any target provider. No CLI required -- infrastructure teams can execute complete migrations through the browser.',
  },
  {
    number: '05',
    title: `${platform.apiEndpoints} REST API Endpoints`,
    description:
      'Every HyperSDK Platform capability is accessible through a comprehensive REST API. Integrate migration workflows into CI/CD pipelines, ITSM tools, or custom automation. Complete OpenAPI documentation with request/response examples for every endpoint.',
  },
  {
    number: '06',
    title: 'Lower migration TCO with superior automation',
    description:
      'Proprietary migration appliances tied to commercial Kubernetes stacks often require large platform subscriptions before you migrate a single VM. HyperSDK Platform deploys to KVM, OpenStack, and KubeVirt targets at a fraction of that cost.* That is 80% less manual work per VM compared to virt-v2v, with a fully automated pipeline from export to boot. *Contact sales for pricing.',
  },
];

export default function WhyHyperSDK(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const copy = getWhyHypersdkPageCopy(i18n.currentLocale);
  const tableHeaders = [copy.colHypersdk, copy.colVirtv2v, copy.colMtv, copy.colCloudendure, copy.colAwshub];

  return (
    <ProductPage
      title="Why HyperSDK Platform"
      description="Compare HyperSDK Platform with virt-v2v, Forklift, CloudEndure, and AWS Migration Hub. See why enterprises choose HyperSDK Platform for VM migration."
    >
      <MarketingHero pageId="why-hypersdk" />

      <PageContent>
        {/* Comparison Table */}
        <SectionHeader eyebrow={copy.compareEyebrow} title={copy.compareTitle} subtitle={copy.compareSubtitle} />

        <div
          style={{
            background: 'rgba(18, 18, 18, 0.6)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: 16,
            overflow: 'hidden',
            marginBottom: '4rem',
          }}
        >
          {/* Header */}
          <div
            className={styles.comparisonTable}
            style={{
              background: 'rgba(255, 140, 0, 0.08)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
              padding: '1rem 1.5rem',
              alignItems: 'center',
            }}
          >
            <div className={styles.monoLabel} style={{marginBottom: 0, color: 'var(--hs-text-muted)'}}>
              {copy.featureColumn}
            </div>
            {tableHeaders.map((h, i) => (
              <div
                key={h}
                className={styles.monoLabel}
                style={{
                  marginBottom: 0,
                  color: i === 0 ? '#f47a60' : '#94a3b8',
                  fontWeight: i === 0 ? 700 : 600,
                  textAlign: 'center',
                }}
              >
                {h}
              </div>
            ))}
          </div>

          {/* Rows */}
          {comparisonRows.map((row, i) => (
            <div
              key={row.feature}
              className={styles.comparisonTable}
              style={{
                borderBottom: i < comparisonRows.length - 1 ? '1px solid rgba(255, 255, 255, 0.04)' : 'none',
                padding: '0.75rem 1.5rem',
                alignItems: 'center',
                background: row.winner ? 'rgba(255, 140, 0, 0.04)' : 'transparent',
              }}
            >
              <div
                style={{
                  color: 'var(--hs-text-body)',
                  fontSize: '0.9rem',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                {row.feature}
                {row.winner && (
                  <span
                    style={{
                      fontSize: '0.6rem',
                      fontWeight: 700,
                      color: 'var(--hs-accent-light)',
                      background: 'rgba(255, 140, 0, 0.12)',
                      border: '1px solid rgba(255, 140, 0, 0.25)',
                      borderRadius: 4,
                      padding: '0.15rem 0.4rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {copy.onlyHypersdk}
                  </span>
                )}
              </div>
              {[row.hypersdk, row.virtv2v, row.mtv, row.cloudendure, row.awshub].map((val, j) => (
                <div
                  key={`${row.feature}-${j}`}
                  style={{
                    textAlign: 'center',
                    fontSize: typeof val === 'string' ? '0.8rem' : '1.1rem',
                    fontWeight: 700,
                    color:
                      typeof val === 'string'
                        ? j === 0
                          ? '#f47a60'
                          : '#94a3b8'
                        : val
                          ? j === 0
                            ? '#f47a60'
                            : '#4ade80'
                          : '#64748b',
                    fontFamily: typeof val === 'string' ? "'JetBrains Mono', monospace" : 'inherit',
                  }}
                >
                  {typeof val === 'string' ? val : val ? '\u2713' : '\u2717'}
                </div>
              ))}
            </div>
          ))}
        </div>

        <p
          style={{
            color: 'var(--hs-text-subtle)',
            fontSize: '0.85rem',
            fontStyle: 'italic',
            textAlign: 'center',
            marginTop: '-2rem',
            marginBottom: '4rem',
          }}
        >
          {copy.pricingFootnote}
        </p>

        {/* Key Differentiators */}
        <SectionHeader eyebrow={copy.differentiatorsEyebrow} title={copy.differentiatorsTitle} />

        <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '4rem'}}>
          {differentiators.map((d) => (
            <div
              key={d.number}
              className={`${styles.featureCard} ${styles.numberedRow}`}
              style={{
                padding: '2rem 2.5rem',
              }}
            >
              <div
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '2rem',
                  fontWeight: 800,
                  color: 'rgba(255, 140, 0, 0.25)',
                  lineHeight: 1,
                }}
              >
                {d.number}
              </div>
              <div>
                <h3
                  style={{
                    fontSize: '1.3rem',
                    fontWeight: 700,
                    color: 'var(--hs-text-heading)',
                    marginBottom: '0.75rem',
                  }}
                >
                  {d.title}
                </h3>
                <p className={styles.featureCardDesc}>{d.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <CTASection
          title={copy.evaluateTitle}
          subtitle={copy.evaluateSubtitle}
          primaryCta={{label: copy.scheduleDemo, to: '/contact?intent=demo'}}
          secondaryCta={{label: copy.viewSolutions, to: '/solutions'}}
        />
      </PageContent>
    </ProductPage>
  );
}
