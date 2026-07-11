// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {
  ProductPage,
  PageContent,
  StatGrid,
  CTASection,
  styles,
  MarketingHero,
  TrustNarrativeDisclaimer,
} from '../components/shared';
import {caseStudyNarratives, caseStudyTopStats} from '../data/trust-narratives';

const topStats = [...caseStudyTopStats];
const caseStudies = caseStudyNarratives;

export default function CaseStudies(): ReactNode {
  return (
    <ProductPage
      title="Case Studies"
      description="See how enterprise organizations use HyperSDK Platform to migrate VMs across cloud providers."
    >
      <MarketingHero pageId="case-studies" />

      <PageContent>
        <TrustNarrativeDisclaimer>
          Composite program narratives for planning — not audited financial filings. Request a reference call or
          assessment for metrics tied to your estate.
        </TrustNarrativeDisclaimer>
        {/* Results at a Glance */}
        <div style={{marginBottom: '3rem'}}>
          <h2
            style={{
              textAlign: 'center',
              fontSize: '1.4rem',
              fontWeight: 700,
              color: 'var(--hs-text-heading)',
              marginBottom: '1.5rem',
              letterSpacing: '-0.01em',
            }}
          >
            Results at a Glance
          </h2>
          <StatGrid stats={topStats} columns={4} />
        </div>

        {/* Case Studies */}
        <div style={{display: 'flex', flexDirection: 'column', gap: '3rem', marginBottom: '3rem'}}>
          {caseStudies.map((cs) => (
            <div key={cs.title} className={styles.featureCard} style={{padding: '3rem'}}>
              <div style={{marginBottom: '2rem'}}>
                <span
                  style={{
                    background: 'rgba(255, 140, 0, 0.1)',
                    color: 'var(--hs-accent-light)',
                    padding: '0.35rem 1rem',
                    borderRadius: 8,
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    border: '1px solid rgba(255, 140, 0, 0.2)',
                    marginBottom: '1rem',
                    display: 'inline-block',
                  }}
                >
                  {cs.industry}
                </span>
                <h2
                  style={{
                    fontSize: '1.8rem',
                    fontWeight: 700,
                    color: 'var(--hs-text-heading)',
                    marginBottom: '0.5rem',
                  }}
                >
                  {cs.title}
                </h2>
                <p
                  style={{
                    color: 'var(--hs-accent-light)',
                    fontSize: '1.1rem',
                    fontWeight: 500,
                    margin: 0,
                  }}
                >
                  {cs.headline}
                </p>
              </div>

              <div className={styles.gridCol2} style={{gap: '2rem', marginBottom: '2rem'}}>
                <div>
                  <h3 className={styles.monoLabel}>The Challenge</h3>
                  <p className={styles.featureCardDesc}>{cs.challenge}</p>
                </div>
                <div>
                  <h3 className={styles.monoLabel}>The Solution</h3>
                  <p className={styles.featureCardDesc}>{cs.solution}</p>
                </div>
              </div>

              {/* Key Metrics */}
              <div
                className={styles.gridCol4}
                style={{
                  gap: '1rem',
                  background: 'rgba(255, 140, 0, 0.05)',
                  border: '1px solid rgba(255, 140, 0, 0.1)',
                  borderRadius: 12,
                  padding: '1.5rem',
                  marginBottom: '1.5rem',
                }}
              >
                {cs.results.map((r) => (
                  <div key={r.label} style={{textAlign: 'center'}}>
                    <div
                      style={{
                        fontSize: '1.8rem',
                        fontWeight: 800,
                        background: 'linear-gradient(135deg, #f47a60 0%, #a78bfa 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        marginBottom: '0.25rem',
                      }}
                    >
                      {r.metric}
                    </div>
                    <div
                      style={{
                        color: 'var(--hs-text-muted)',
                        fontSize: '0.8rem',
                        fontWeight: 500,
                      }}
                    >
                      {r.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <CTASection
          title="Ready to write your success story?"
          subtitle="See how HyperSDK Platform can transform your VM migration strategy with a personalized demo."
          primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
