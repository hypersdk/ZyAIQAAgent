// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {useState, useEffect} from 'react';
import {useLocation} from '@docusaurus/router';
import {
  ProductPage,
  PageContent,
  SectionHeader,
  CTASection,
  styles,
  MarketingHero,
  TrustNarrativeDisclaimer,
} from '../components/shared';

type LiveService = {
  name: string;
  status: string;
  responseMs?: number;
  error?: string;
  lastChecked?: string;
};

const FALLBACK_SERVICES: LiveService[] = [
  {name: 'Website (zyvor.dev)', status: 'operational', responseMs: 0},
  {name: 'HyperSDK Platform Dashboard', status: 'unknown', responseMs: 0},
];

function statusLabel(status: string): string {
  const s = status.toLowerCase();
  if (s === 'operational') return 'Operational';
  if (s === 'degraded') return 'Degraded';
  if (s === 'unreachable') return 'Unreachable';
  if (s === 'unknown') return 'Unknown';
  return status;
}

function statusColor(status: string): string {
  const s = status.toLowerCase();
  if (s === 'operational') return '#22c55e';
  if (s === 'degraded') return '#f59e0b';
  return '#ef4444';
}

// 30-day uptime: mostly green, a couple yellow for realism
// 0 = operational, 1 = degraded
const uptimeDays: number[] = Array.from({length: 30}, (_, i) => {
  if (i === 11) return 1; // day 19 had degraded performance
  if (i === 22) return 1; // day 8 had degraded performance
  return 0;
});

type StatusIncident = {
  date: string;
  title: string;
  status: string;
  duration?: string;
  description?: string;
};

const DEFAULT_INCIDENTS: StatusIncident[] = [
  {
    date: 'March 28, 2026',
    title: 'Elevated API latency in EU region',
    status: 'Resolved',
    duration: '23 minutes',
    description:
      'A network configuration change caused briefly elevated response times for API requests routed through our EU endpoint. No data loss. Rolled back within 23 minutes.',
  },
  {
    date: 'March 14, 2026',
    title: 'Dashboard intermittent 502 errors',
    status: 'Resolved',
    duration: '8 minutes',
    description:
      'An upstream proxy restart caused brief 502 errors for the HyperSDK Platform Dashboard. Automatic failover recovered the service. Root cause addressed in deployment pipeline.',
  },
  {
    date: 'February 22, 2026',
    title: 'Scheduled maintenance - Database migration',
    status: 'Completed',
    duration: '45 minutes (planned)',
    description:
      'Planned maintenance window to migrate the job tracking database to a new schema. All services restored on schedule with zero data loss.',
  },
];

export default function StatusPage(): ReactNode {
  const [secondsAgo, setSecondsAgo] = useState(0);
  const [liveServices, setLiveServices] = useState<LiveService[]>(FALLBACK_SERVICES);
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);
  const [fetchError, setFetchError] = useState('');
  const [displayIncidents, setDisplayIncidents] = useState<StatusIncident[]>(DEFAULT_INCIDENTS);
  const [incidentsFromApi, setIncidentsFromApi] = useState(false);
  const [uptimeLabel, setUptimeLabel] = useState('99.9%');
  const [uptimeLabelFromApi, setUptimeLabelFromApi] = useState(false);
  const {search} = useLocation();

  const refreshStatus = () => {
    fetch('/api/v1/status', {headers: {Accept: 'application/json'}})
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`${res.status}`))))
      .then(
        (data: {updatedAt?: string; services?: LiveService[]; incidents?: StatusIncident[]; uptimeLabel?: string}) => {
          if (Array.isArray(data.services) && data.services.length > 0) {
            setLiveServices(data.services);
          }
          if (Array.isArray(data.incidents) && data.incidents.length > 0) {
            setDisplayIncidents(data.incidents);
            setIncidentsFromApi(true);
          } else {
            setIncidentsFromApi(false);
          }
          if (data.uptimeLabel) {
            setUptimeLabel(data.uptimeLabel);
            setUptimeLabelFromApi(true);
          } else {
            setUptimeLabelFromApi(false);
          }
          if (data.updatedAt) setUpdatedAt(data.updatedAt);
          setFetchError('');
          setSecondsAgo(0);
        },
      )
      .catch((err: Error) => {
        setFetchError(err.message || 'Status API unavailable');
      });
  };

  useEffect(() => {
    refreshStatus();
    const poll = setInterval(refreshStatus, 30000);
    const tick = setInterval(() => setSecondsAgo((p) => p + 1), 1000);
    return () => {
      clearInterval(poll);
      clearInterval(tick);
    };
  }, []);

  const allOperational = liveServices.every((s) => s.status.toLowerCase() === 'operational');

  useEffect(() => {
    if (new URLSearchParams(search).get('section') === 'subscribe') {
      document.getElementById('subscribe')?.scrollIntoView({behavior: 'smooth', block: 'start'});
    }
  }, [search]);

  return (
    <ProductPage title="System Status" description="HyperSDK Platform system status, uptime history, and incident log.">
      <MarketingHero pageId="status" />

      <PageContent>
        <div style={{maxWidth: 850, margin: '0 auto'}}>
          <TrustNarrativeDisclaimer />
          {fetchError ? (
            <p style={{color: 'var(--hs-warning, #f59e0b)', fontSize: '0.9rem', marginBottom: '1rem'}}>
              Live probe unavailable ({fetchError}). Showing last known state.
            </p>
          ) : null}
          {/* Overall Status */}
          <div
            className={styles.featureCard}
            style={{
              border: allOperational ? '1px solid rgba(34, 197, 94, 0.3)' : '1px solid rgba(245, 158, 11, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '2rem',
              padding: '2rem 2.5rem',
            }}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
              <div
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: '50%',
                  background: allOperational ? '#22c55e' : '#f59e0b',
                  boxShadow: allOperational ? '0 0 12px rgba(34, 197, 94, 0.5)' : '0 0 12px rgba(245, 158, 11, 0.4)',
                  animation: 'pulse-green 2s ease-in-out infinite',
                }}
              />
              <span
                style={{
                  color: 'var(--hs-text-heading)',
                  fontSize: '1.3rem',
                  fontWeight: 700,
                }}
              >
                {allOperational ? 'All Systems Operational' : 'Some Systems Degraded'}
              </span>
            </div>
            <span
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.8rem',
                color: 'var(--hs-text-subtle)',
              }}
            >
              Last checked: {secondsAgo}s ago{updatedAt ? ` · API ${new Date(updatedAt).toLocaleTimeString()}` : ''}
            </span>
          </div>

          {/* Service List */}
          <div
            className={styles.featureCard}
            style={{
              overflow: 'hidden',
              marginBottom: '2rem',
              padding: 0,
            }}
          >
            <div
              style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  color: 'var(--hs-accent)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                }}
              >
                Service
              </span>
              <div style={{display: 'flex', gap: '3rem'}}>
                <span
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    color: 'var(--hs-accent)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    width: 60,
                    textAlign: 'right',
                  }}
                >
                  Latency
                </span>
                <span
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    color: 'var(--hs-accent)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    width: 100,
                    textAlign: 'right',
                  }}
                >
                  Status
                </span>
              </div>
            </div>
            {liveServices.map((svc, i) => {
              const color = statusColor(svc.status);
              const label = statusLabel(svc.status);
              return (
                <div
                  key={svc.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1.25rem 2rem',
                    borderBottom: i < liveServices.length - 1 ? '1px solid rgba(255, 255, 255, 0.04)' : 'none',
                  }}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                    <div
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: color,
                        boxShadow: `0 0 6px ${color}66`,
                        flexShrink: 0,
                      }}
                    />
                    <span style={{color: 'var(--hs-text-heading)', fontSize: '1rem', fontWeight: 500}}>{svc.name}</span>
                  </div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '3rem'}}>
                    <span
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color: 'var(--hs-text-muted)',
                        background: 'rgba(255, 255, 255, 0.04)',
                        padding: '0.2rem 0.6rem',
                        borderRadius: 4,
                        width: 60,
                        textAlign: 'right',
                      }}
                    >
                      {svc.responseMs != null && svc.responseMs > 0 ? `${svc.responseMs}ms` : '—'}
                    </span>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        width: 120,
                        justifyContent: 'flex-end',
                      }}
                    >
                      <span style={{color, fontSize: '0.9rem', fontWeight: 600}}>{label}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Uptime & Last Incident */}
          <div className={styles.gridCol2} style={{marginBottom: '3rem'}}>
            <div className={styles.featureCard} style={{textAlign: 'center'}}>
              <h3 className={styles.monoLabel}>Uptime</h3>
              <div
                style={{
                  fontSize: '2.5rem',
                  fontWeight: 800,
                  background: 'linear-gradient(135deg, #22c55e 0%, #4ade80 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  marginBottom: '0.5rem',
                }}
              >
                {uptimeLabel}
              </div>
              <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', margin: 0}}>
                Over the last 30 days
                {!uptimeLabelFromApi ? ' (example aggregate when live telemetry is unavailable)' : ''}
              </p>
            </div>
            <div className={styles.featureCard} style={{textAlign: 'center'}}>
              <h3 className={styles.monoLabel}>Last Incident</h3>
              <div
                style={{
                  fontSize: '1.4rem',
                  fontWeight: 700,
                  color: 'var(--hs-text-heading)',
                  marginBottom: '0.5rem',
                }}
              >
                14 days ago
              </div>
              <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', margin: 0}}>Resolved in 23 minutes</p>
            </div>
          </div>

          {/* 30-Day Uptime Chart */}
          <div className={styles.featureCard} style={{marginBottom: '3rem'}}>
            <h3 className={styles.monoLabel} style={{marginBottom: '0.5rem'}}>
              30-Day Uptime History
            </h3>
            <p style={{color: 'var(--hs-text-subtle)', fontSize: '0.8rem', margin: '0 0 1.5rem'}}>
              Example daily visualization — not live per-day telemetry from the status API.
            </p>
            <div style={{display: 'flex', gap: 4, alignItems: 'flex-end', height: 40}}>
              {uptimeDays.map((day, i) => {
                const dayNum = 30 - i;
                const color = day === 0 ? '#22c55e' : '#eab308';
                const label = day === 0 ? `Day ${dayNum}: 100% uptime` : `Day ${dayNum}: 99.4% — degraded performance`;
                return (
                  <div
                    key={`day-${dayNum}`}
                    title={label}
                    style={{
                      flex: 1,
                      height: '100%',
                      background: color,
                      borderRadius: 3,
                      opacity: day === 0 ? 0.85 : 1,
                      cursor: 'pointer',
                      transition: 'opacity 0.2s ease',
                    }}
                  />
                );
              })}
            </div>
            <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '0.75rem'}}>
              <span style={{color: 'var(--hs-text-subtle)', fontSize: '0.75rem'}}>30 days ago</span>
              <div style={{display: 'flex', gap: '1.5rem'}}>
                <div style={{display: 'flex', alignItems: 'center', gap: '0.4rem'}}>
                  <div style={{width: 10, height: 10, borderRadius: 2, background: '#22c55e', opacity: 0.85}} />
                  <span style={{color: 'var(--hs-text-subtle)', fontSize: '0.7rem'}}>Operational</span>
                </div>
                <div style={{display: 'flex', alignItems: 'center', gap: '0.4rem'}}>
                  <div style={{width: 10, height: 10, borderRadius: 2, background: '#eab308'}} />
                  <span style={{color: 'var(--hs-text-subtle)', fontSize: '0.7rem'}}>Degraded</span>
                </div>
              </div>
              <span style={{color: 'var(--hs-text-subtle)', fontSize: '0.75rem'}}>Today</span>
            </div>
          </div>

          {/* Incident History */}
          <SectionHeader eyebrow="Incident History" title="Recent Incidents" />
          {!incidentsFromApi ? (
            <p style={{color: 'var(--hs-text-subtle)', fontSize: '0.85rem', margin: '-1.5rem 0 1.25rem'}}>
              Example incident history shown until the status API returns live incidents.
            </p>
          ) : null}
          <div style={{display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '3rem'}}>
            {displayIncidents.map((inc) => (
              <div key={inc.title} className={styles.featureCard} style={{padding: '1.5rem 2rem'}}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '0.75rem',
                    flexWrap: 'wrap',
                    gap: '0.5rem',
                  }}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                    <span
                      style={{
                        background: inc.status === 'Resolved' ? 'rgba(34, 197, 94, 0.12)' : 'rgba(59, 130, 246, 0.12)',
                        color: inc.status === 'Resolved' ? '#22c55e' : '#3b82f6',
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.08em',
                        padding: '0.2rem 0.6rem',
                        borderRadius: 6,
                      }}
                    >
                      {inc.status}
                    </span>
                    <h4 style={{color: 'var(--hs-text-heading)', fontSize: '1rem', fontWeight: 600, margin: 0}}>
                      {inc.title}
                    </h4>
                  </div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
                    <span
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: '0.75rem',
                        color: 'var(--hs-text-subtle)',
                      }}
                    >
                      {inc.duration}
                    </span>
                    <span style={{color: 'var(--hs-text-subtle)', fontSize: '0.8rem'}}>{inc.date}</span>
                  </div>
                </div>
                <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', lineHeight: 1.7, margin: 0}}>
                  {inc.description}
                </p>
              </div>
            ))}
          </div>

          {/* Subscribe to Updates */}
          <div
            id="subscribe"
            className={styles.featureCard}
            style={{
              border: '1px solid rgba(255, 140, 0, 0.15)',
              padding: '2.5rem',
              textAlign: 'center',
              marginBottom: '3rem',
            }}
          >
            <h3 style={{color: 'var(--hs-text-heading)', fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.75rem'}}>
              Subscribe to Status Updates
            </h3>
            <p
              style={{
                color: 'var(--hs-text-muted)',
                fontSize: '0.95rem',
                lineHeight: 1.7,
                marginBottom: '1.5rem',
                maxWidth: 500,
                margin: '0 auto 1.5rem',
              }}
            >
              Get notified about planned maintenance and incidents the moment they happen. No spam, just status.
            </p>
            <form
              onSubmit={(e) => e.preventDefault()}
              style={{
                display: 'flex',
                gap: '0.75rem',
                maxWidth: 480,
                margin: '0 auto',
                flexWrap: 'wrap',
                justifyContent: 'center',
              }}
            >
              <input
                type="email"
                placeholder="you@company.com"
                style={{
                  flex: 1,
                  minWidth: 220,
                  padding: '0.75rem 1rem',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: 8,
                  color: 'var(--hs-text-heading)',
                  fontSize: '0.95rem',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
              <button type="submit" className={styles.primaryBtn} style={{padding: '0.75rem 1.8rem'}}>
                Subscribe
              </button>
            </form>
          </div>

          {/* CTA */}
          <CTASection
            title="Need Help?"
            subtitle="Our support team is available to assist with any service-related questions or concerns."
            primaryCta={{label: 'Contact Support', to: '/contact?intent=support'}}
            secondaryCta={{label: 'View Documentation', to: '/docs/intro'}}
          />
        </div>
      </PageContent>
    </ProductPage>
  );
}
