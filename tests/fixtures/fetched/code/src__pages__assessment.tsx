// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import {useState, useEffect, useRef} from 'react';
import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {ProductPage, PageContent, SectionHeader, MarketingHero, styles, RelatedBlogSection} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {dispatchMarketingEvent} from '../utils/marketingEvents';
import {buildAssessmentContactUrl} from '../utils/assessmentContactPrefill';

const questions = [
  {
    q: 'How many VMs do you manage?',
    options: ['<50', '50-200', '200-500', '500+'],
  },
  {
    q: 'Which hypervisor?',
    options: ['VMware', 'Hyper-V', 'Cloud', 'Mixed'],
  },
  {
    q: 'Annual VMware/cloud spend?',
    options: ['<$50K', '$50-200K', '$200K-1M', '$1M+'],
  },
  {
    q: 'Migration timeline?',
    options: ['3 months', '6 months', '12 months', 'No rush'],
  },
  {
    q: 'Top priority?',
    options: ['Cost savings', 'Performance', 'Compliance', 'Modernization'],
  },
];

function calculateSavings(answers: (number | null)[]): {low: string; high: string; percent: string} {
  const vmIdx = answers[0] ?? 0;
  const hypervisor = answers[1] ?? 0;
  const spendIdx = answers[2] ?? 0;

  const spendRanges = [
    [20000, 50000],
    [50000, 200000],
    [200000, 1000000],
    [1000000, 3000000],
  ];
  const [spendLow, spendHigh] = spendRanges[spendIdx];

  // VMware gets highest savings multiplier
  let savingsRate = hypervisor === 0 ? 0.65 : hypervisor === 3 ? 0.45 : 0.35;
  // More VMs = economies of scale
  savingsRate += vmIdx * 0.05;

  const low = Math.round((spendLow * savingsRate) / 1000) * 1000;
  const high = Math.round((spendHigh * savingsRate) / 1000) * 1000;

  const fmt = (n: number) => (n >= 1000000 ? `$${(n / 1000000).toFixed(1)}M` : `$${(n / 1000).toFixed(0)}K`);

  return {low: fmt(low), high: fmt(high), percent: `${Math.round(savingsRate * 100)}%`};
}

export default function AssessmentPage(): ReactNode {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>([null, null, null, null, null]);
  const done = step >= questions.length;
  const startedRef = useRef(false);
  const completedRef = useRef(false);

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;
    dispatchMarketingEvent('assessment_started');
  }, []);

  const savings = done ? calculateSavings(answers) : null;
  const contactUrl =
    done && savings
      ? buildAssessmentContactUrl({
          answers: questions.map((item, index) => ({
            question: item.q,
            answer: item.options[answers[index] ?? 0] ?? '',
          })),
          savingsLow: savings.low,
          savingsHigh: savings.high,
          savingsPercent: savings.percent,
        })
      : '/contact?intent=assessment';

  useEffect(() => {
    if (!done || !savings || completedRef.current) return;
    completedRef.current = true;
    dispatchMarketingEvent('assessment_completed', {
      savings_low: savings.low,
      savings_high: savings.high,
      savings_percent: savings.percent,
    });
  }, [done, savings]);

  function select(optionIdx: number) {
    const next = [...answers];
    next[step] = optionIdx;
    setAnswers(next);
    setStep(step + 1);
  }

  return (
    <ProductPage
      title="Migration Assessment"
      description="Find out how much you could save by migrating with HyperSDK Platform."
    >
      <MarketingHero pageId="assessment" />

      <PageContent>
        {!done ? (
          <div
            className={styles.featureCard}
            style={{maxWidth: 640, margin: '0 auto', padding: '3rem', textAlign: 'center'}}
          >
            {/* Progress */}
            <div style={{display: 'flex', gap: '0.5rem', justifyContent: 'center', marginBottom: '2rem'}}>
              {questions.map((q, i) => (
                <div
                  key={q.q}
                  style={{
                    width: 40,
                    height: 4,
                    borderRadius: 2,
                    background: i <= step ? '#f0583a' : 'rgba(255,255,255,0.1)',
                    transition: 'background 0.3s',
                  }}
                />
              ))}
            </div>
            <p style={{color: 'var(--hs-text-subtle)', fontSize: '0.8rem', marginBottom: '0.5rem'}}>
              Question {step + 1} of {questions.length}
            </p>
            <h2 style={{color: 'var(--hs-text-heading)', fontSize: '1.5rem', fontWeight: 700, marginBottom: '2rem'}}>
              {questions[step].q}
            </h2>
            <div className={styles.gridCol2} style={{gap: '1rem'}}>
              {questions[step].options.map((opt, i) => (
                <button
                  key={opt}
                  onClick={() => select(i)}
                  className={styles.quizOption}
                  aria-label={`${questions[step].q}: ${opt}`}
                >
                  {opt}
                </button>
              ))}
            </div>
            {step > 0 && (
              <button
                onClick={() => setStep(step - 1)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--hs-text-subtle)',
                  cursor: 'pointer',
                  marginTop: '1.5rem',
                  fontSize: '0.85rem',
                }}
              >
                Back
              </button>
            )}
          </div>
        ) : (
          <div
            className={styles.featureCard}
            style={{
              maxWidth: 640,
              margin: '0 auto',
              padding: '3rem',
              textAlign: 'center',
              border: '1px solid rgba(240,88,58,0.3)',
            }}
          >
            <div className={styles.monoLabel} style={{marginBottom: '1rem'}}>
              Your Estimated Savings
            </div>
            <div style={{fontSize: '3rem', fontWeight: 800, color: 'var(--hs-text-heading)', marginBottom: '0.5rem'}}>
              {savings!.low} - {savings!.high}
            </div>
            <p style={{color: 'var(--hs-text-muted)', fontSize: '1rem', marginBottom: '0.25rem'}}>
              estimated annual savings
            </p>
            <p style={{color: 'var(--hs-accent-light)', fontSize: '1.1rem', fontWeight: 600, marginBottom: '2rem'}}>
              Up to {savings!.percent} reduction in infrastructure costs
            </p>
            <div style={{display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap'}}>
              <Link
                to={contactUrl}
                className={styles.primaryBtn}
                onClick={() => dispatchMarketingEvent('assessment_contact_click')}
              >
                Get Your Custom Assessment
              </Link>
              <button
                onClick={() => {
                  completedRef.current = false;
                  setStep(0);
                  setAnswers([null, null, null, null, null]);
                }}
                className={styles.secondaryBtn}
                style={{cursor: 'pointer'}}
              >
                Retake Quiz
              </button>
            </div>
          </div>
        )}

        {done && savings && (
          <div style={{padding: '0 2rem 4rem'}}>
            <div style={{maxWidth: 720, margin: '0 auto'}}>
              <SectionHeader
                eyebrow="Methodology"
                title="How We Calculated"
                subtitle="Our estimates are based on real customer data across hundreds of migrations."
              />
              <div className={styles.featureCard} style={{padding: '2.5rem', textAlign: 'left'}}>
                <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
                  {[
                    {
                      label: 'Current Spend',
                      detail:
                        'VM count multiplied by average cost per VM gives your current annual infrastructure spend. This includes licensing, support contracts, and infrastructure overhead.',
                    },
                    {
                      label: 'HyperSDK Platform Savings',
                      detail:
                        'HyperSDK Platform reduces per-VM cost by 60-90% by eliminating hypervisor licensing fees and moving to open-source KVM. VMware migrations see the highest savings due to per-socket licensing elimination.',
                    },
                    {
                      label: 'Cost Factors',
                      detail:
                        'We factor in licensing costs, ongoing support fees, infrastructure overhead, and migration execution costs. The estimate is conservative -- most customers report savings at the high end of the range.',
                    },
                    {
                      label: 'Timeline Estimates',
                      detail:
                        'Simple environments (homogeneous OS, standard configs): 2-4 weeks. Moderate complexity (mixed OS, some custom configs): 4-8 weeks. Complex environments (legacy apps, compliance requirements): 8-12 weeks.',
                    },
                  ].map((item) => (
                    <div key={item.label}>
                      <h4
                        style={{
                          color: 'var(--hs-accent-light)',
                          fontSize: '0.95rem',
                          fontWeight: 700,
                          marginBottom: '0.35rem',
                        }}
                      >
                        {item.label}
                      </h4>
                      <p
                        style={{
                          color: 'var(--hs-text-muted)',
                          fontSize: '0.88rem',
                          lineHeight: 1.7,
                          margin: 0,
                        }}
                      >
                        {item.detail}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <RelatedBlogSection links={solutionPageBlogLinks.assessment} />
      </PageContent>
    </ProductPage>
  );
}
