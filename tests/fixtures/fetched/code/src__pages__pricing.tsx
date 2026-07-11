// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {ProductPage, MarketingHero, PageContent, SectionHeader, FeatureGrid, styles} from '../components/shared';
import {getPricingFaqs} from '../data/pricing-faq-locale';
import {getPricingComparison, getPricingCopy, getPricingTableLabels, getPricingTiers} from '../data/pricing-locale';
import {dispatchMarketingEvent} from '../utils/marketingEvents';
import RazorpayButton from '../components/RazorpayButton';

export default function PricingPage(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const pricingCopy = getPricingCopy(i18n.currentLocale);
  const faqs = getPricingFaqs(i18n.currentLocale);
  const tiers = getPricingTiers(i18n.currentLocale);
  const comparisonRows = getPricingComparison(i18n.currentLocale);
  const tableLabels = getPricingTableLabels(i18n.currentLocale);
  return (
    <ProductPage
      title="Pricing"
      description="HyperSDK Platform pricing -- simple, transparent plans for teams of every size."
    >
      <MarketingHero pageId="pricing" />

      <PageContent>
        {/* Tier cards */}
        <div className={styles.pricingGrid}>
          {tiers.map((t) => (
            <div key={t.name} className={t.highlight ? styles.pricingCardHighlight : styles.pricingCard}>
              {t.badge && (
                <span className={styles.pricingBadge} style={t.badgeColor ? {background: t.badgeColor} : undefined}>
                  {t.badge}
                </span>
              )}
              <h3 className={styles.monoLabel}>{t.name}</h3>
              <div style={{marginBottom: '0.5rem'}}>
                <span className={styles.pricingPrice}>{t.price}</span>
                <span className={styles.pricingPriceNote}>{t.priceNote}</span>
              </div>
              <div
                style={{
                  color: 'var(--hs-text-muted)',
                  fontSize: '0.8rem',
                  marginBottom: '2rem',
                  fontFamily: 'var(--hs-font-mono)',
                }}
              >
                {t.priceSub}
              </div>
              <ul className={styles.pricingFeatureList}>
                {t.features.map((f) => (
                  <li key={f} className={styles.pricingFeatureItem}>
                    <span className={styles.pricingCheck}>&#10003;</span>
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                to={t.ctaLink}
                className={t.highlight ? styles.primaryBtn : styles.secondaryBtn}
                style={{
                  display: 'block',
                  textAlign: 'center',
                  justifyContent: 'center',
                }}
                onClick={() =>
                  dispatchMarketingEvent('cta_click', {
                    label: t.cta,
                    to: t.ctaLink,
                    placement: 'pricing_tier',
                    tier: t.name,
                  })
                }
              >
                {t.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* Online Purchase — India (Razorpay) */}
        <div
          style={{
            textAlign: 'center',
            margin: '0 0 4rem',
            padding: '2.5rem 2rem',
            background: 'var(--ifm-card-background-color)',
            borderRadius: 12,
            border: '1px solid var(--ifm-color-emphasis-200)',
          }}
        >
          <p
            style={{
              fontFamily: 'var(--hs-font-mono)',
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: 'var(--hs-accent)',
              marginBottom: '0.5rem',
            }}
          >
            India · Pay online
          </p>
          <h3 style={{margin: '0 0 0.5rem', fontSize: '1.25rem'}}>Starter Plan — ₹4,999/month</h3>
          <p style={{color: 'var(--hs-text-muted)', margin: '0 0 1.75rem', fontSize: '0.9rem'}}>
            Instant access · up to 25 VMs · 30-day money-back guarantee
          </p>
          <RazorpayButton
            amount={499900}
            currency="INR"
            productName="HyperSDK Platform"
            description="Starter Plan · up to 25 VMs"
            className={styles.primaryBtn}
            onSuccess={(paymentId) =>
              dispatchMarketingEvent('razorpay_payment_success', {payment_id: paymentId, tier: 'starter'})
            }
          >
            Pay ₹4,999 — Buy Now
          </RazorpayButton>
          <p style={{color: 'var(--hs-text-subtle)', fontSize: '0.78rem', marginTop: '1rem'}}>
            Secure payment via Razorpay · UPI, cards, net banking supported
          </p>
        </div>

        {/* Feature Comparison Matrix */}
        <SectionHeader
          eyebrow={pricingCopy.compareEyebrow}
          title={pricingCopy.compareTitle}
          subtitle={pricingCopy.compareSubtitle}
        />
        <div style={{overflowX: 'auto', margin: '0 auto 2rem', maxWidth: 950}}>
          <table
            className={styles.featureCard}
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              textAlign: 'left',
            }}
          >
            <thead>
              <tr style={{borderBottom: '2px solid var(--ifm-color-emphasis-300)'}}>
                <th style={{padding: '1rem', minWidth: 160}}>{tableLabels.featureColumn}</th>
                <th style={{padding: '1rem', textAlign: 'center', minWidth: 120}}>{tableLabels.starterColumn}</th>
                <th style={{padding: '1rem', textAlign: 'center', minWidth: 120}}>{tableLabels.professionalColumn}</th>
                <th style={{padding: '1rem', textAlign: 'center', minWidth: 120}}>{tableLabels.enterpriseColumn}</th>
              </tr>
            </thead>
            <tbody>
              {comparisonRows.map((row, i) => (
                <tr
                  key={row.feature}
                  style={{
                    borderBottom: i < comparisonRows.length - 1 ? '1px solid var(--ifm-color-emphasis-200)' : undefined,
                  }}
                >
                  <td style={{padding: '1rem', fontWeight: 600, color: 'var(--hs-text-heading)'}}>{row.feature}</td>
                  <td
                    style={{
                      padding: '1rem',
                      textAlign: 'center',
                      color: row.starter ? 'var(--hs-text-muted)' : 'var(--hs-text-subtle)',
                      fontSize: '0.9rem',
                    }}
                  >
                    {row.starter ?? <span style={{opacity: 0.4}}>--</span>}
                  </td>
                  <td
                    style={{
                      padding: '1rem',
                      textAlign: 'center',
                      color: row.professional ? 'var(--hs-text-muted)' : 'var(--hs-text-subtle)',
                      fontSize: '0.9rem',
                    }}
                  >
                    {row.professional ?? <span style={{opacity: 0.4}}>--</span>}
                  </td>
                  <td
                    style={{
                      padding: '1rem',
                      textAlign: 'center',
                      color: row.enterprise ? 'var(--hs-text-muted)' : 'var(--hs-text-subtle)',
                      fontSize: '0.9rem',
                    }}
                  >
                    {row.enterprise ?? <span style={{opacity: 0.4}}>--</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div
          style={{
            textAlign: 'center',
            marginBottom: '5rem',
            color: 'var(--hs-text-muted)',
            fontSize: '0.85rem',
            fontStyle: 'italic',
          }}
        >
          {pricingCopy.volumeNote}
        </div>

        {/* Partner Program */}
        <SectionHeader
          eyebrow={pricingCopy.partnerEyebrow}
          title={pricingCopy.partnerTitle}
          subtitle={pricingCopy.partnerSubtitle}
        />
        <FeatureGrid
          columns={3}
          features={[
            {title: pricingCopy.partnerTier1Title, desc: pricingCopy.partnerTier1Desc},
            {title: pricingCopy.partnerTier2Title, desc: pricingCopy.partnerTier2Desc},
            {title: pricingCopy.partnerTier3Title, desc: pricingCopy.partnerTier3Desc},
          ]}
        />

        {/* Customer Savings by VM Count */}
        <div className={`${styles.featureGrid} ${styles.featureGridCol3}`}>
          {[
            {vms: '25 VMs', savings: '$112K', period: pricingCopy.savingsPeriod},
            {vms: '100 VMs', savings: '$730K', period: pricingCopy.savingsPeriod},
            {vms: '500 VMs', savings: '$3.74M', period: pricingCopy.savingsPeriod},
          ].map((row) => (
            <div key={row.vms} className={styles.savingsCard}>
              <div className={styles.savingsLabel}>{row.vms}</div>
              <div className={styles.savingsValue}>{row.savings}</div>
              <div className={styles.savingsPeriod}>{row.period}</div>
            </div>
          ))}
        </div>

        <div className={styles.textCenter} style={{marginBottom: '3rem'}}>
          <Link
            to="/contact"
            className={styles.primaryBtn}
            onClick={() =>
              dispatchMarketingEvent('cta_click', {
                label: pricingCopy.joinPartner,
                to: '/contact?intent=partners',
                placement: 'pricing_partner',
              })
            }
          >
            {pricingCopy.joinPartner}
          </Link>
          <p className={styles.featureCardDesc} style={{marginTop: '1.25rem'}}>
            Compare{' '}
            <Link to="/docs/editions" style={{color: 'var(--hs-accent-light)', fontWeight: 600}}>
              Community vs Enterprise Edition
            </Link>{' '}
            for confidential fabric, HyperCluster, and SLA coverage. All tiers are proprietary — see{' '}
            <Link to="/docs/licensing" style={{color: 'var(--hs-accent-light)', fontWeight: 600}}>
              licensing overview
            </Link>{' '}
            and the <Link to="/license">deploy EULA</Link>.
          </p>
        </div>

        {/* FAQ */}
        <div className={styles.faqWrapper}>
          <h2 className={styles.faqTitle}>{pricingCopy.faqTitle}</h2>
          <p className={styles.featureCardDesc} style={{textAlign: 'center', marginBottom: '1.5rem'}}>
            {pricingCopy.faqSubtitle}
          </p>
          {faqs.map((f) => (
            <div key={f.q} className={styles.faqCard}>
              <h4 className={styles.faqQuestion}>{f.q}</h4>
              <p className={styles.featureCardDesc}>{f.a}</p>
            </div>
          ))}
        </div>
      </PageContent>
    </ProductPage>
  );
}
