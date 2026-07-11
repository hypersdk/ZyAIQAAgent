// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {CSSProperties, ReactNode} from 'react';
import {useState} from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Link from '@docusaurus/Link';
import {
  ProductPage,
  MigrationMarketingHero,
  PageContent,
  SectionHeader,
  StatGrid,
  FeatureGrid,
  CTASection,
  RelatedBlogSection,
  MigrationTrustStrip,
  styles,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {getMigrationLanding} from '../data/migration-landings-locale';

const repatSliderStyle: CSSProperties = {
  width: '100%',
  height: 6,
  borderRadius: 3,
  appearance: 'none' as const,
  background: 'rgba(255, 255, 255, 0.1)',
  outline: 'none',
  cursor: 'pointer',
  accentColor: '#f0583a',
};

function formatCurrency(n: number): string {
  return '$' + n.toLocaleString('en-US');
}

const costComparison = [
  {item: 'Compute (100 VMs)', cloud: '$384,000', onprem: '$96,000'},
  {item: 'Storage (200 TB)', cloud: '$276,000', onprem: '$48,000'},
  {item: 'Network Egress', cloud: '$72,000', onprem: '$0'},
  {item: 'Database Licensing', cloud: '$144,000', onprem: '$144,000'},
  {item: 'Support & Management', cloud: '$48,000', onprem: '$72,000'},
  {item: 'KVM + HyperSDK Platform', cloud: '$0', onprem: '$44,400'},
  {item: '3-Year Total', cloud: '$2,772,000', onprem: '$1,213,200'},
];

const transferCostGrid: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'minmax(140px, 1.4fr) minmax(88px, 0.85fr) minmax(72px, 0.65fr) minmax(120px, 1fr)',
  alignItems: 'center',
  columnGap: '1rem',
};

const dataTransferCosts = [
  {category: 'Data upload (ingress)', usd: '$0.00', inr: '\u20B90', note: 'Usually free', emphasize: false},
  {
    category: 'Data download (egress)',
    usd: '$0.08 \u2013 $0.12',
    inr: '\u20B96 \u2013 \u20B910',
    note: 'Main cost driver',
    emphasize: true,
  },
  {
    category: 'CDN / streaming',
    usd: '$0.02 \u2013 $0.08',
    inr: '\u20B92 \u2013 \u20B97',
    note: 'Often cheaper via CDN',
    emphasize: false,
  },
  {
    category: 'Inter-region transfer',
    usd: '$0.02 \u2013 $0.08',
    inr: '\u20B92 \u2013 \u20B97',
    note: 'Between regions',
    emphasize: false,
  },
  {
    category: 'Same region / internal',
    usd: 'Free \u2013 $0.01',
    inr: '\u20B90 \u2013 \u20B91',
    note: 'Often free or minimal',
    emphasize: false,
  },
];

export default function CloudRepatriation(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const landing = getMigrationLanding('cloud-repatriation', i18n.currentLocale);
  const [vms, setVms] = useState(50);
  const [cloudCostPerVM, setCloudCostPerVM] = useState(200);

  const monthlyCost = vms * cloudCostPerVM;
  const annualCloud = monthlyCost * 12;
  const annualOnPrem = vms * 100 * 12;
  const annualSavings = annualCloud - annualOnPrem;

  return (
    <ProductPage
      title="Cloud Repatriation"
      description="Bring your workloads home. Migrate from AWS, Azure, and GCP to on-premises KVM."
    >
      <MigrationMarketingHero landingId="cloud-repatriation" />

      <PageContent>
        <MigrationTrustStrip config={landing} />
        {/* Why Repatriate */}
        <FeatureGrid
          features={[
            {
              title: 'Spiraling Cloud Costs',
              desc: 'Cloud spending grows 20-30% annually. After three years, most enterprises pay 2-3x what on-prem would cost.',
            },
            {
              title: 'Data Sovereignty',
              desc: 'GDPR, CCPA, and sector-specific regulations demand data stays within jurisdictional boundaries.',
            },
            {
              title: 'Performance & Latency',
              desc: 'Latency-sensitive workloads suffer on shared cloud infrastructure. On-prem delivers predictable performance.',
            },
          ]}
          columns={3}
        />

        {/* Cost Comparison */}
        <SectionHeader
          eyebrow="Cost Analysis"
          title="Cloud vs. On-Premises: 3-Year Total Cost"
          subtitle="Real numbers from an 80-VM healthcare provider repatriation. 100% HIPAA compliant. 4 weeks migration timeline."
        />

        <StatGrid
          stats={[
            {value: '$85K', label: 'Azure Monthly Cost'},
            {value: '$8K', label: 'KVM Monthly Cost'},
            {value: '$720K', label: 'Annual Savings'},
          ]}
          columns={3}
        />

        <div
          className={styles.featureCard}
          style={{marginBottom: '2.5rem', border: '1px solid var(--hs-border-accent)'}}
        >
          <span className={styles.sectionEyebrow} style={{display: 'block', marginBottom: '0.5rem'}}>
            Typical public-cloud pricing
          </span>
          <h3 className={styles.sectionTitle} style={{fontSize: '1.35rem', marginBottom: '0.35rem'}}>
            Data transfer costs (rule-of-thumb)
          </h3>
          <p className={styles.featureCardDesc} style={{marginBottom: '1.25rem'}}>
            Per-gigabyte figures vary by provider, region, and commitment discounts. INR uses an illustrative ~₹83/USD
            for quick mental math.
          </p>
          <div style={{overflowX: 'auto', marginBottom: '1.25rem', WebkitOverflowScrolling: 'touch'}}>
            <div style={{minWidth: 520}}>
              <div
                style={{
                  ...transferCostGrid,
                  padding: '0.65rem 1.25rem',
                  background: 'rgba(255, 140, 0, 0.08)',
                  borderBottom: '1px solid var(--hs-border)',
                  borderRadius: '8px 8px 0 0',
                }}
              >
                <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.75rem'}}>
                  Category
                </span>
                <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.75rem', textAlign: 'right'}}>
                  USD / GB
                </span>
                <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.75rem', textAlign: 'right'}}>
                  INR / GB
                </span>
                <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.75rem'}}>
                  Notes
                </span>
              </div>
              {dataTransferCosts.map((row, i) => (
                <div
                  key={row.category}
                  style={{
                    ...transferCostGrid,
                    padding: '0.55rem 1.25rem',
                    borderBottom: i < dataTransferCosts.length - 1 ? '1px solid var(--hs-border)' : 'none',
                    background: row.emphasize ? 'rgba(240, 88, 58, 0.1)' : 'transparent',
                    borderRadius: i === dataTransferCosts.length - 1 ? '0 0 8px 8px' : undefined,
                  }}
                >
                  <span
                    style={{
                      color: 'var(--hs-text-heading)',
                      fontSize: '0.88rem',
                      fontWeight: row.emphasize ? 700 : 500,
                    }}
                  >
                    {row.category}
                  </span>
                  <span
                    style={{
                      color: row.emphasize ? 'var(--hs-error-light)' : 'var(--hs-text-body)',
                      fontSize: '0.88rem',
                      fontFamily: 'var(--hs-font-mono)',
                      textAlign: 'right',
                    }}
                  >
                    {row.usd}
                  </span>
                  <span
                    style={{
                      color: 'var(--hs-text-body)',
                      fontSize: '0.88rem',
                      fontFamily: 'var(--hs-font-mono)',
                      textAlign: 'right',
                    }}
                  >
                    {row.inr}
                  </span>
                  <span style={{color: 'var(--hs-text-muted)', fontSize: '0.82rem'}}>{row.note}</span>
                </div>
              ))}
            </div>
          </div>
          <div style={{borderTop: '1px solid var(--hs-border)', paddingTop: '1.1rem'}}>
            <span className={styles.monoLabel} style={{display: 'block', marginBottom: '0.5rem', fontSize: '0.72rem'}}>
              Quick takeaway
            </span>
            <ul
              style={{
                margin: 0,
                paddingLeft: '1.15rem',
                color: 'var(--hs-text-body)',
                fontSize: '0.9rem',
                lineHeight: 1.75,
              }}
            >
              <li>Upload (ingress) is usually free.</li>
              <li>Same-region and internal traffic is often free or minimal.</li>
              <li>Download, streaming, and wide-area egress are where bills spike.</li>
            </ul>
          </div>
        </div>

        <div className={styles.featureCard} style={{overflow: 'hidden', padding: 0, marginBottom: '5rem'}}>
          <div
            className={styles.costTable}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'rgba(255, 140, 0, 0.08)',
              borderBottom: '1px solid var(--hs-border)',
            }}
          >
            <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.8rem'}}>
              Line Item (Annual)
            </span>
            <span
              className={styles.monoLabel}
              style={{marginBottom: 0, fontSize: '0.8rem', color: 'var(--hs-error)', textAlign: 'right'}}
            >
              Cloud
            </span>
            <span
              className={styles.monoLabel}
              style={{marginBottom: 0, fontSize: '0.8rem', color: 'var(--hs-success)', textAlign: 'right'}}
            >
              On-Prem
            </span>
          </div>
          {costComparison.map((row, i) => (
            <div
              key={row.item}
              className={styles.costTable}
              style={{
                padding: '0.65rem 1.5rem',
                borderBottom: i < costComparison.length - 1 ? '1px solid var(--hs-border)' : 'none',
                background: i === costComparison.length - 1 ? 'rgba(255, 140, 0, 0.04)' : 'transparent',
              }}
            >
              <span
                style={{
                  color: i === costComparison.length - 1 ? 'var(--hs-text-heading)' : 'var(--hs-text-body)',
                  fontSize: '0.9rem',
                  fontWeight: i === costComparison.length - 1 ? 700 : 400,
                }}
              >
                {row.item}
              </span>
              <span
                style={{
                  color: 'var(--hs-error-light)',
                  fontSize: '0.9rem',
                  fontFamily: 'var(--hs-font-mono)',
                  textAlign: 'right',
                  fontWeight: i === costComparison.length - 1 ? 700 : 400,
                }}
              >
                {row.cloud}
              </span>
              <span
                style={{
                  color: 'var(--hs-success-light)',
                  fontSize: '0.9rem',
                  fontFamily: 'var(--hs-font-mono)',
                  textAlign: 'right',
                  fontWeight: i === costComparison.length - 1 ? 700 : 400,
                }}
              >
                {row.onprem}
              </span>
            </div>
          ))}
        </div>

        {/* Quick Repatriation Estimate */}
        <div
          className={styles.featureCard}
          style={{
            border: '1px solid var(--hs-border-accent)',
            marginBottom: '2rem',
          }}
        >
          <div style={{textAlign: 'center', marginBottom: '2rem'}}>
            <span className={styles.sectionEyebrow}>Interactive Calculator</span>
            <h2 className={styles.sectionTitle} style={{fontSize: '1.8rem'}}>
              Quick Repatriation Estimate
            </h2>
            <p className={styles.featureCardDesc} style={{textAlign: 'center'}}>
              Drag the sliders to estimate your cloud repatriation savings.
            </p>
          </div>

          <div className={styles.gridCol2} style={{gap: '2rem', marginBottom: '2rem'}}>
            <div>
              <label
                className={styles.monoLabel}
                style={{display: 'block', marginBottom: '0.5rem', fontSize: '0.8rem'}}
              >
                Number of VMs: <span style={{color: 'var(--hs-accent-light)'}}>{vms}</span>
              </label>
              <input
                type="range"
                min={10}
                max={500}
                step={10}
                value={vms}
                onChange={(e) => setVms(Number(e.target.value))}
                style={repatSliderStyle}
              />
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  color: 'var(--hs-text-muted)',
                  fontSize: '0.7rem',
                  marginTop: '0.25rem',
                }}
              >
                <span>10</span>
                <span>500</span>
              </div>
            </div>
            <div>
              <label
                className={styles.monoLabel}
                style={{display: 'block', marginBottom: '0.5rem', fontSize: '0.8rem'}}
              >
                Monthly Cloud Cost / VM:{' '}
                <span style={{color: 'var(--hs-accent-light)'}}>{formatCurrency(cloudCostPerVM)}</span>
              </label>
              <input
                type="range"
                min={50}
                max={500}
                step={10}
                value={cloudCostPerVM}
                onChange={(e) => setCloudCostPerVM(Number(e.target.value))}
                style={repatSliderStyle}
              />
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  color: 'var(--hs-text-muted)',
                  fontSize: '0.7rem',
                  marginTop: '0.25rem',
                }}
              >
                <span>$50</span>
                <span>$500</span>
              </div>
            </div>
          </div>

          <div
            style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--hs-border-accent)',
              borderRadius: 12,
              padding: '1.5rem 2rem',
              textAlign: 'center',
              marginBottom: '1.5rem',
            }}
          >
            <div style={{fontSize: '1rem', color: 'var(--hs-text-body)', lineHeight: 2}}>
              <span>
                Cloud:{' '}
                <strong style={{color: 'var(--hs-error)', fontFamily: 'var(--hs-font-mono)'}}>
                  {formatCurrency(annualCloud)}/year
                </strong>
              </span>
              <span style={{color: 'var(--hs-text-muted)', margin: '0 0.75rem'}}>{'\u2192'}</span>
              <span>
                On-Prem:{' '}
                <strong style={{color: 'var(--hs-success)', fontFamily: 'var(--hs-font-mono)'}}>
                  {formatCurrency(annualOnPrem)}/year
                </strong>
              </span>
              <span style={{color: 'var(--hs-text-muted)', margin: '0 0.75rem'}}>=</span>
              <span
                style={{
                  color: 'var(--hs-accent-light)',
                  fontWeight: 800,
                  fontSize: '1.15rem',
                  fontFamily: 'var(--hs-font-mono)',
                }}
              >
                {formatCurrency(annualSavings)} saved
              </span>
            </div>
          </div>

          <div style={{textAlign: 'center'}}>
            <Link className={styles.primaryBtn} to="/contact?intent=repatriation">
              Plan Your Repatriation
            </Link>
          </div>
        </div>

        {/* Data Sovereignty Drivers */}
        <SectionHeader
          eyebrow="Compliance"
          title="Data Sovereignty Drivers"
          subtitle="Regulatory requirements are a primary driver for cloud repatriation. Keep your data where the law requires it."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'GDPR (EU)',
              desc: 'Data must stay within EU member states. Cross-border transfers require adequacy decisions or standard contractual clauses. On-prem KVM eliminates third-party data processor risk.',
            },
            {
              title: 'CCPA (California)',
              desc: 'Consumer data protection requirements with strict breach notification timelines. On-premises infrastructure simplifies compliance with data access and deletion requests.',
            },
            {
              title: 'PDPA (Singapore)',
              desc: 'Cross-border transfer restrictions require consent and equivalent protection guarantees. On-prem deployment ensures data residency within Singapore jurisdiction.',
            },
            {
              title: 'Federal (US Gov)',
              desc: 'FedRAMP, ITAR, and classified data requirements mandate specific infrastructure controls. On-prem KVM meets NIST 800-171, CMMC, and DFARS requirements.',
            },
          ]}
        />

        <RelatedBlogSection links={solutionPageBlogLinks.cloudRepatriation} />

        {/* CTA */}
        <CTASection
          title="Calculate Your Savings"
          subtitle="Our solutions engineers will analyze your cloud spend and provide a detailed repatriation cost model -- at no cost and no obligation."
          primaryCta={{label: 'Calculate Your Savings', to: '/contact?intent=repatriation'}}
        />
      </PageContent>
    </ProductPage>
  );
}
