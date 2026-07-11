// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {EMAIL_SALES, EMAIL_SUPPORT} from '../data/emails';
import {LEGAL_ENTITY_INDIA} from '../data/legal-entity-india';
import {ProductPage, PageContent, styles, MarketingHero} from '../components/shared';

const LAST_UPDATED = 'June 27, 2026';

export default function Refund(): ReactNode {
  return (
    <ProductPage
      title="Refund Policy"
      description="Refund and cancellation policy for ZySign and HyperSDK Platform purchases from ZyvorAI Labs Private Limited."
    >
      <MarketingHero pageId="terms" />

      <PageContent>
        {/* Summary card */}
        <div
          className={styles.featureCard}
          style={{
            textAlign: 'left',
            maxWidth: 900,
            margin: '0 auto 2rem',
            padding: '2.5rem',
            border: '1px solid rgba(240, 88, 58, 0.2)',
            background: 'rgba(240, 88, 58, 0.03)',
          }}
        >
          <h2
            style={{
              fontSize: '1.3rem',
              fontWeight: 700,
              color: 'var(--hs-text-heading)',
              marginBottom: '1.25rem',
            }}
          >
            Key points
          </h2>
          <ul
            style={{
              listStyle: 'none',
              padding: 0,
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '0.85rem',
            }}
          >
            {[
              {
                bold: 'ZySign licence (₹590)',
                rest: ' — 7-day full refund, no questions asked. Email us with your Razorpay payment ID.',
              },
              {
                bold: 'Licence key shown instantly',
                rest: " — your key appears on screen immediately after payment; you don't need to wait for email.",
              },
              {bold: 'Refund timeline', rest: ' — 5–7 business days to your original payment method via Razorpay.'},
              {
                bold: 'Enterprise / HyperSDK Platform',
                rest: ' — governed by your signed MSA or Order Form. Contact sales@zyvor.dev.',
              },
            ].map(({bold, rest}) => (
              <li
                key={bold}
                style={{
                  display: 'flex',
                  gap: '0.75rem',
                  color: 'var(--hs-text-body)',
                  fontSize: '0.95rem',
                  lineHeight: 1.6,
                }}
              >
                <span style={{color: 'var(--hs-accent)', flexShrink: 0, marginTop: '0.1rem'}}>✓</span>
                <span>
                  <strong style={{color: 'var(--hs-text-heading)'}}>{bold}</strong>
                  {rest}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Full policy */}
        <div
          style={{
            maxWidth: 900,
            margin: '0 auto',
            color: 'var(--hs-text-body)',
            lineHeight: 1.8,
            fontSize: '0.95rem',
          }}
        >
          <p style={{color: 'var(--hs-text-muted)', fontSize: '0.85rem', marginBottom: '2.5rem'}}>
            Last updated: {LAST_UPDATED}. This policy applies to purchases made at zyvor.dev.
          </p>

          <h2>1. ZySign — individual licence (₹590)</h2>
          <p>
            You may request a full refund within <strong>7 calendar days</strong> of the date of purchase. No reason is
            required. We will process your refund to the original payment instrument (UPI, card, net banking) via
            Razorpay within 5–7 business days.
          </p>
          <p>
            After 7 days from purchase, licence fees are non-refundable. The licence key is delivered on screen
            immediately after payment and remains active for 1 year from the date of issue.
          </p>

          <h3>How to request a ZySign refund</h3>
          <ol style={{paddingLeft: '1.5rem'}}>
            <li>
              Email{' '}
              <a href={`mailto:${EMAIL_SUPPORT}`} style={{color: 'var(--hs-accent-light)'}}>
                {EMAIL_SUPPORT}
              </a>{' '}
              with the subject line: <strong>Refund Request — [your Razorpay payment ID]</strong>
            </li>
            <li>Include the email address you used at checkout (if any) and the date of purchase.</li>
            <li>
              We will confirm the refund by email within 1 business day and initiate the transfer. You will also receive
              a refund confirmation from Razorpay.
            </li>
          </ol>
          <p>Once a refund is issued, the licence key associated with that payment is deactivated.</p>

          <h2>2. HyperSDK Platform — enterprise</h2>
          <p>
            Refunds and cancellations for HyperSDK Platform subscriptions, enterprise licences, and professional
            services are governed by the terms of your signed Master Subscription Agreement (MSA) or Order Form. Contact{' '}
            <a href={`mailto:${EMAIL_SALES}`} style={{color: 'var(--hs-accent-light)'}}>
              {EMAIL_SALES}
            </a>{' '}
            to initiate any adjustment, credit, or early-termination request.
          </p>

          <h2>3. Exceptions</h2>
          <p>
            We reserve the right to deny a refund if there is evidence of abuse (e.g., purchasing and immediately
            requesting a refund multiple times, or violating the{' '}
            <a href="/terms" style={{color: 'var(--hs-accent-light)'}}>
              Terms of Service
            </a>
            ). In cases of suspected fraud or chargebacks initiated without contacting us first, we may contest the
            claim.
          </p>

          <h2>4. Payment processing</h2>
          <p>
            All transactions are processed by Razorpay (Razorpay Software Private Limited, Bangalore, India). Refund
            timelines depend on your bank or payment network and may vary. ZyvorAI Labs has no control over bank-side
            delays beyond Razorpay's refund initiation.
          </p>

          <h2>5. Contact</h2>
          <p>For any refund or billing question, reach us at:</p>
          <address
            style={{
              fontStyle: 'normal',
              background: 'var(--hs-surface)',
              border: '1px solid var(--hs-border)',
              borderRadius: 12,
              padding: '1.25rem 1.5rem',
              marginBottom: '1.5rem',
              lineHeight: 2,
            }}
          >
            <strong style={{color: 'var(--hs-text-heading)'}}>{LEGAL_ENTITY_INDIA.legalName}</strong>
            <br />
            {LEGAL_ENTITY_INDIA.addressOneLine}
            <br />
            CIN: {LEGAL_ENTITY_INDIA.cin}
            <br />
            <a href={`mailto:${EMAIL_SUPPORT}`} style={{color: 'var(--hs-accent-light)'}}>
              {EMAIL_SUPPORT}
            </a>
            {' · '}
            <a href={`mailto:${EMAIL_SALES}`} style={{color: 'var(--hs-accent-light)'}}>
              {EMAIL_SALES}
            </a>
          </address>
        </div>
      </PageContent>
    </ProductPage>
  );
}
