// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import {lazy, Suspense, type ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {
  ProductPage,
  PageContent,
  SectionHeader,
  CTASection,
  styles,
  MarketingHero,
  TrustNarrativeDisclaimer,
} from '../components/shared';
import {GUESTKIT_DEMO_VIDEO, MIGRATION_DEMO_VIDEO} from '../data/product-demo-videos';
import {platform} from '../data/platform-stats';

const YouTubeEmbed = lazy(() => import('../components/YouTubeEmbed').then((m) => ({default: m.YouTubeEmbed})));

const demoHighlights = [
  {
    title: 'Discovery & export',
    desc: `Inventory VMs across ${platform.cloudProviders} providers and schedule export waves from one control plane.`,
  },
  {
    title: 'Convert & validate',
    desc: 'hyper2kvm pipeline with guest fixes, integrity checks, and first-boot validation.',
  },
  {
    title: 'Operate at scale',
    desc: 'Day-2 lifecycle on KVM and KubeVirt — APIs, dashboards, and observability in one suite.',
  },
];

const whatYoullSee = [
  `VM discovery across ${platform.cloudProviders} cloud providers`,
  'One-click export and conversion',
  'Real-time migration monitoring',
  'Hardware management (CPU, memory, disk, NIC editing)',
  'KubeVirt deployment',
  'Carbon-aware scheduling',
];

const shortcuts = [
  {keys: '1\u20139', desc: 'Switch between dashboard tabs'},
  {keys: '/', desc: 'Search VMs, jobs, and providers'},
  {keys: '?', desc: 'Open keyboard shortcut help'},
  {keys: 'g h', desc: 'Go to dashboard home'},
  {keys: 'n', desc: 'Start a new migration'},
  {keys: 'Esc', desc: 'Close panels and modals'},
];

export default function DemoPage(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const dashboardUrl = (siteConfig.customFields?.dashboardUrl as string) || '/';
  return (
    <ProductPage
      title="Live Demo"
      description="See HyperSDK Platform in action. Try the live dashboard or schedule a guided demo."
    >
      <MarketingHero pageId="demo" />

      <PageContent>
        <TrustNarrativeDisclaimer>
          The migration video is a product walkthrough, not a live customer environment. Dashboard access may require
          approval — book a guided demo for your hypervisor mix.
        </TrustNarrativeDisclaimer>
        <SectionHeader title="Migration video" />
        <div style={{maxWidth: 960, margin: '0 auto 4rem'}}>
          <Suspense fallback={<div style={{minHeight: 360, background: 'rgba(0,0,0,0.3)', borderRadius: 12}} />}>
            <YouTubeEmbed videoId={MIGRATION_DEMO_VIDEO.youtubeId} title={MIGRATION_DEMO_VIDEO.title} priorityThumb />
          </Suspense>
          <p style={{textAlign: 'center', marginTop: '0.85rem', marginBottom: 0}}>
            <a
              href={MIGRATION_DEMO_VIDEO.watchUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{color: 'var(--hs-accent-light)', fontSize: '0.95rem'}}
            >
              Open on YouTube
            </a>
            {' · '}
            <Link to="/analytics/youtube" style={{color: 'var(--hs-accent-light)', fontSize: '0.95rem'}}>
              Channel stats
            </Link>
          </p>
        </div>

        <SectionHeader
          eyebrow="GuestKit"
          title="VM disk intelligence demo"
          subtitle="Offline inspection, TUI workflows, and diagnostics — without booting the guest."
        />
        <div style={{maxWidth: 960, margin: '0 auto 4rem'}}>
          <Suspense fallback={<div style={{minHeight: 360, background: 'rgba(0,0,0,0.3)', borderRadius: 12}} />}>
            <YouTubeEmbed videoId={GUESTKIT_DEMO_VIDEO.youtubeId} title={GUESTKIT_DEMO_VIDEO.title} />
          </Suspense>
          <p style={{textAlign: 'center', marginTop: '0.85rem', marginBottom: 0}}>
            <a
              href={GUESTKIT_DEMO_VIDEO.watchUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{color: 'var(--hs-accent-light)', fontSize: '0.95rem'}}
            >
              Open on YouTube
            </a>
            {' · '}
            <Link to="/guestkit" style={{color: 'var(--hs-accent-light)', fontSize: '0.95rem'}}>
              GuestKit product page
            </Link>
          </p>
        </div>

        {/* Two options */}
        <div className={styles.gridCol2} style={{gap: '2rem', marginBottom: '4rem'}}>
          {/* Live Dashboard */}
          <div
            className={styles.featureCard}
            style={{
              border: '2px solid rgba(240, 88, 58, 0.3)',
              padding: '3rem 2.5rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: 16,
                background: 'rgba(240, 88, 58, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.8rem',
                marginBottom: '1.5rem',
              }}
            >
              &#9654;
            </div>
            <h2
              style={{
                fontSize: '1.6rem',
                fontWeight: 700,
                color: 'var(--hs-text-heading)',
                marginBottom: '1rem',
              }}
            >
              Try the Live Dashboard
            </h2>
            <p
              style={{
                color: 'var(--hs-text-muted)',
                fontSize: '1rem',
                lineHeight: 1.7,
                marginBottom: '2rem',
                flex: 1,
              }}
            >
              Explore the dashboard with {platform.dashboardViews} views. Browse VMs, check system health, view
              providers, and see the full operational interface that powers enterprise migrations.
            </p>
            <a
              href={`${dashboardUrl}${dashboardUrl.includes('?') ? '&' : '?'}utm_source=zyvor&utm_medium=demo_page`}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.primaryBtn}
            >
              Open Live Dashboard
            </a>
          </div>

          {/* Guided Demo */}
          <div
            className={styles.featureCard}
            style={{
              padding: '3rem 2.5rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: 16,
                background: 'rgba(139, 92, 246, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.8rem',
                marginBottom: '1.5rem',
              }}
            >
              &#128187;
            </div>
            <h2
              style={{
                fontSize: '1.6rem',
                fontWeight: 700,
                color: 'var(--hs-text-heading)',
                marginBottom: '1rem',
              }}
            >
              Schedule a Guided Demo
            </h2>
            <p
              style={{
                color: 'var(--hs-text-muted)',
                fontSize: '1rem',
                lineHeight: 1.7,
                marginBottom: '2rem',
                flex: 1,
              }}
            >
              30-minute walkthrough with our team. See the migration workflow end-to-end, from export to conversion to
              deployment. Tailored to your environment.
            </p>
            <Link to="/contact?intent=demo" className={styles.secondaryBtn}>
              Schedule Demo
            </Link>
          </div>
        </div>

        {/* What You'll See */}
        <SectionHeader eyebrow="Demo Highlights" title="What You Will See" />
        <div
          className={styles.gridCol2}
          style={{gap: '1rem', marginBottom: '4rem', maxWidth: 750, margin: '0 auto 4rem'}}
        >
          {whatYoullSee.map((item) => (
            <div
              key={item}
              className={styles.featureCard}
              style={{
                padding: '1rem 1.25rem',
                paddingLeft: '2.75rem',
                position: 'relative',
              }}
            >
              <span
                style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '1rem',
                  color: 'var(--hs-success)',
                  fontWeight: 700,
                  fontSize: '1rem',
                }}
              >
                {'\u2713'}
              </span>
              <span style={{color: 'var(--hs-text-body)', fontSize: '0.95rem', lineHeight: 1.6}}>{item}</span>
            </div>
          ))}
        </div>

        {/* Self-Guided Tour */}
        <SectionHeader
          eyebrow="Self-Guided Tour"
          title="Keyboard Shortcuts"
          subtitle="Navigate the dashboard like a power user. These shortcuts work in the live demo."
        />
        <div
          className={styles.featureCard}
          style={{
            maxWidth: 550,
            margin: '0 auto 4rem',
            padding: 0,
            overflow: 'hidden',
          }}
        >
          {shortcuts.map((s, i) => (
            <div
              key={s.keys}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.9rem 1.5rem',
                borderBottom: i < shortcuts.length - 1 ? '1px solid rgba(255, 255, 255, 0.04)' : 'none',
              }}
            >
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  color: 'var(--hs-accent-light)',
                  background: 'rgba(255, 140, 0, 0.08)',
                  border: '1px solid rgba(255, 140, 0, 0.15)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: 6,
                  minWidth: 50,
                  textAlign: 'center',
                }}
              >
                {s.keys}
              </span>
              <span
                style={{
                  color: 'var(--hs-text-muted)',
                  fontSize: '0.9rem',
                }}
              >
                {s.desc}
              </span>
            </div>
          ))}
        </div>

        <SectionHeader
          eyebrow="Platform preview"
          title="What the demo covers"
          subtitle="Live walkthrough of the suite workflow — no stock UI screenshots."
        />
        <div className={styles.gridCol3} style={{marginBottom: '4rem'}}>
          {demoHighlights.map((s) => (
            <div key={s.title} className={styles.featureCard} style={{padding: '1.5rem'}}>
              <h4
                style={{
                  color: 'var(--hs-text-heading)',
                  fontSize: '1.05rem',
                  fontWeight: 600,
                  marginBottom: '0.4rem',
                }}
              >
                {s.title}
              </h4>
              <p className={styles.featureCardDesc}>{s.desc}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <CTASection
          title="Ready to Migrate?"
          subtitle="Talk to our team about your enterprise requirements and get started with HyperSDK Platform."
          primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
          secondaryCta={{label: 'View Pricing', to: '/pricing'}}
        />
      </PageContent>
    </ProductPage>
  );
}
