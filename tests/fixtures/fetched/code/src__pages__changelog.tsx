// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode, FormEvent} from 'react';
import {useState} from 'react';
import Link from '@docusaurus/Link';
import {ProductPage, PageContent, CTASection, styles, MarketingHero} from '../components/shared';
import {changelogReleases, type ChangelogBadge} from '../data/changelog';
import {useFormspree} from '../hooks/useFormspree';

const badgeColors: Record<ChangelogBadge, {bg: string; text: string}> = {
  'New Feature': {bg: 'rgba(34, 197, 94, 0.12)', text: '#22c55e'},
  Performance: {bg: 'rgba(59, 130, 246, 0.12)', text: '#3b82f6'},
  Security: {bg: 'rgba(239, 68, 68, 0.12)', text: '#ef4444'},
  Integration: {bg: 'rgba(139, 92, 246, 0.12)', text: '#8b5cf6'},
  Infrastructure: {bg: 'rgba(245, 158, 11, 0.12)', text: '#f59e0b'},
  'Breaking Change': {bg: 'rgba(239, 68, 68, 0.08)', text: '#f87171'},
};

export default function ChangelogPage(): ReactNode {
  const [subscribeEmail, setSubscribeEmail] = useState('');
  const {status, error, mailHint, submit} = useFormspree();
  const subscribed = status === 'done' || status === 'done_no_mail';

  async function handleSubscribe(e: FormEvent) {
    e.preventDefault();
    const formData = new FormData();
    formData.set('intent', 'changelog-subscribe');
    formData.set('email', subscribeEmail);
    formData.set('message', 'Subscribe to HyperSDK release notes');
    await submit(formData);
  }

  return (
    <ProductPage title="Changelog" description="HyperSDK Platform product changelog. See what is new in every release.">
      <MarketingHero pageId="changelog" />

      <PageContent>
        <div style={{maxWidth: 850, margin: '0 auto'}}>
          <div
            className={styles.featureCard}
            style={{
              border: '1px solid rgba(255, 140, 0, 0.15)',
              padding: '2rem 2.5rem',
              textAlign: 'center',
              marginBottom: '3rem',
            }}
          >
            {subscribed ? (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.75rem',
                  flexWrap: 'wrap',
                }}
              >
                <span style={{color: 'var(--hs-success)', fontSize: '1.2rem'}}>&#10003;</span>
                <span style={{color: 'var(--hs-text-heading)', fontSize: '1rem', fontWeight: 600}}>
                  {mailHint || 'Subscribed! You will receive release notes for every new version.'}
                </span>
              </div>
            ) : (
              <>
                <h3
                  style={{
                    color: 'var(--hs-text-heading)',
                    fontSize: '1.15rem',
                    fontWeight: 700,
                    marginBottom: '0.5rem',
                  }}
                >
                  Subscribe to Release Notes
                </h3>
                <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem'}}>
                  Get notified when we ship new features. No marketing, just release notes.
                </p>
                <form
                  onSubmit={handleSubscribe}
                  style={{
                    display: 'flex',
                    gap: '0.75rem',
                    maxWidth: 440,
                    margin: '0 auto',
                    flexWrap: 'wrap',
                    justifyContent: 'center',
                  }}
                >
                  <input
                    type="email"
                    name="email"
                    placeholder="you@company.com"
                    required
                    value={subscribeEmail}
                    onChange={(e) => setSubscribeEmail(e.target.value)}
                    disabled={status === 'sending'}
                    style={{
                      flex: 1,
                      minWidth: 200,
                      padding: '0.7rem 1rem',
                      background: 'rgba(0, 0, 0, 0.4)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: 8,
                      color: 'var(--hs-text-heading)',
                      fontSize: '0.9rem',
                      outline: 'none',
                      boxSizing: 'border-box',
                    }}
                  />
                  <button
                    type="submit"
                    className={styles.primaryBtn}
                    style={{padding: '0.7rem 1.5rem', fontSize: '0.9rem'}}
                    disabled={status === 'sending'}
                  >
                    {status === 'sending' ? 'Subscribing…' : 'Subscribe'}
                  </button>
                </form>
                {error && <p style={{color: 'var(--hs-danger)', fontSize: '0.85rem', marginTop: '0.75rem'}}>{error}</p>}
              </>
            )}
          </div>

          <div style={{position: 'relative', paddingLeft: '2rem'}}>
            <div
              style={{
                position: 'absolute',
                left: '0.55rem',
                top: '0.5rem',
                bottom: '0.5rem',
                width: 2,
                background: 'linear-gradient(180deg, var(--hs-accent), rgba(240, 88, 58, 0.1))',
                borderRadius: 2,
              }}
            />

            {changelogReleases.map((r, i) => (
              <div
                key={r.version}
                style={{position: 'relative', marginBottom: i < changelogReleases.length - 1 ? '2.5rem' : 0}}
              >
                <div
                  style={{
                    position: 'absolute',
                    left: '-1.65rem',
                    top: '0.35rem',
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    background: i === 0 ? 'var(--hs-accent)' : 'rgba(240, 88, 58, 0.3)',
                    border: '2px solid var(--hs-bg)',
                    boxShadow: i === 0 ? '0 0 12px rgba(240, 88, 58, 0.5)' : undefined,
                  }}
                />

                <div
                  className={styles.featureCard}
                  style={{
                    border: i === 0 ? '1px solid rgba(240, 88, 58, 0.2)' : undefined,
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      marginBottom: '0.75rem',
                      flexWrap: 'wrap',
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: '1rem',
                        fontWeight: 700,
                        color: 'var(--hs-accent)',
                      }}
                    >
                      {r.version}
                    </span>
                    <span
                      style={{
                        color: 'var(--hs-text-subtle)',
                        fontSize: '0.85rem',
                      }}
                    >
                      {r.date}
                    </span>
                    {i === 0 && (
                      <span
                        style={{
                          background: 'rgba(240, 88, 58, 0.15)',
                          color: 'var(--hs-accent)',
                          fontSize: '0.7rem',
                          fontWeight: 600,
                          textTransform: 'uppercase',
                          letterSpacing: '0.08em',
                          padding: '0.2rem 0.6rem',
                          borderRadius: 6,
                        }}
                      >
                        Latest
                      </span>
                    )}
                  </div>

                  <div style={{display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1rem'}}>
                    {r.badges.map((badge) => {
                      const color = badgeColors[badge];
                      return (
                        <span
                          key={badge}
                          style={{
                            background: color.bg,
                            color: color.text,
                            fontSize: '0.65rem',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            letterSpacing: '0.06em',
                            padding: '0.15rem 0.55rem',
                            borderRadius: 5,
                            fontFamily: "'JetBrains Mono', monospace",
                          }}
                        >
                          {badge}
                        </span>
                      );
                    })}
                  </div>

                  <ul style={{margin: 0, paddingLeft: '1.25rem', marginBottom: '1rem'}}>
                    {r.highlights.map((h, j) => (
                      <li
                        key={h}
                        style={{
                          color: 'var(--hs-text-muted)',
                          fontSize: '0.95rem',
                          lineHeight: 1.7,
                          marginBottom: j < r.highlights.length - 1 ? '0.5rem' : 0,
                        }}
                      >
                        {h}
                      </li>
                    ))}
                  </ul>

                  <Link
                    to={r.releaseNotesUrl}
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
                    Full Release Notes &rarr;
                  </Link>
                </div>
              </div>
            ))}
          </div>

          <CTASection
            title="Want to See It in Action?"
            subtitle="Try the latest release or schedule a guided demo with our team."
            primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
            secondaryCta={{label: 'Try Live Demo', to: '/demo'}}
          />
        </div>
      </PageContent>
    </ProductPage>
  );
}
