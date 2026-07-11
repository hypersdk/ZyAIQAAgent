// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import {useState, useEffect, useMemo, useRef, lazy, Suspense} from 'react';
import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import Head from '@docusaurus/Head';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {PageSocialHead} from '../components/PageSocialHead';
import ComparisonTable from '../components/ComparisonTable';
import FAQAccordion from '../components/FAQAccordion';
import ProviderMarquee from '../components/ProviderMarquee';
import ScrollReveal from '../components/ScrollReveal';
import {LogoStrip, SupportOpenSourceSection} from '../components/shared';
import {GuidedDecksHub} from '../components/GuidedDecksHub';
import {
  STICKY_SCROLL_THRESHOLD,
  organizationJsonLd,
  softwareJsonLd,
  getHeroCtaVariant,
  HomeHero,
  HomeTrustBar,
  HomeZySignSpotlight,
  HomeOpenStack,
  HomeSuiteSpotlight,
  HomePathwayStrip,
  HomeStats,
  HomeProducts,
  HomeRunsAnywhere,
  HomeHowItWorks,
  HomeSolutions,
  HomeTestimonialsSection,
  HomeTrustedBySection,
  HomeBlog,
  HomeCTA,
  type HeroCtaVariant,
} from '../components/homepage';
import {getHomeHeroCopy} from '../data/homepage-locale';
import {buildFaqJsonLd} from '../data/faq-locale';
import {platform} from '../data/platform-stats';
import {dispatchMarketingEvent} from '../utils/marketingEvents';
import styles from './index.module.css';

const TerminalDemo = lazy(() => import('../components/TerminalDemo'));
const ExitIntent = lazy(() => import('../components/ExitIntent'));

export default function Home(): ReactNode {
  const {siteConfig, i18n} = useDocusaurusContext();
  const homeCopy = getHomeHeroCopy(i18n.currentLocale);
  const siteUrl = siteConfig.url.replace(/\/$/, '');
  const homeTitle = 'Zeus OS · PacketWolf · Edge & Kubernetes Infrastructure | HyperSDK Platform';
  const homeDescription = `Zeus OS, PacketWolf, and HyperSDK Platform — edge-native Kubernetes, KubeVirt VM management, kernel-native network intelligence, GPU fabric, and private cloud. Migrate from VMware or Nutanix when ready — then run open infrastructure for the long term. ${platform.products} products, ${platform.apiEndpoints} APIs.`;

  const [showSticky, setShowSticky] = useState(false);
  const [ctaVariant, setCtaVariant] = useState<HeroCtaVariant | null>(null);
  const [stickyIntent, setStickyIntent] = useState<'default' | 'compare' | 'faq'>('default');
  const hasTrackedVariant = useRef(false);
  const stickyVisibleRef = useRef(false);

  useEffect(() => {
    setCtaVariant(getHeroCtaVariant());
  }, []);

  useEffect(() => {
    if (!ctaVariant || hasTrackedVariant.current) return;
    hasTrackedVariant.current = true;
    dispatchMarketingEvent('homepage_hero_variant_exposed', {
      variant: ctaVariant,
    });
  }, [ctaVariant]);

  useEffect(() => {
    let ticking = false;
    const updateStickyState = () => {
      const nextVisible = window.scrollY > STICKY_SCROLL_THRESHOLD;
      if (nextVisible !== stickyVisibleRef.current) {
        stickyVisibleRef.current = nextVisible;
        setShowSticky(nextVisible);
      }
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(updateStickyState);
      }
    };

    updateStickyState();
    window.addEventListener('scroll', onScroll, {passive: true});
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const compareSection = document.getElementById('compare-section');
    const faqSection = document.getElementById('faq-section');
    if (!compareSection || !faqSection) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          if (entry.target.id === 'faq-section') {
            setStickyIntent('faq');
          } else if (entry.target.id === 'compare-section') {
            setStickyIntent('compare');
          }
        });
      },
      {threshold: 0.35},
    );

    observer.observe(compareSection);
    observer.observe(faqSection);
    return () => observer.disconnect();
  }, []);

  const stickyConfig = useMemo(() => {
    if (stickyIntent === 'faq') {
      return {
        text: homeCopy.stickyFaqText,
        label: homeCopy.stickyFaq,
        to: '/contact?intent=faq',
      };
    }
    if (stickyIntent === 'compare') {
      return {
        text: homeCopy.stickyCompareText,
        label: homeCopy.stickyCompare,
        to: '/roi',
      };
    }
    return {
      text: homeCopy.stickyDefault,
      label: homeCopy.stickyDemo,
      to: '/contact?intent=demo',
    };
  }, [stickyIntent, homeCopy]);

  return (
    <Layout title={homeTitle} description={homeDescription}>
      <Head>
        <link rel="canonical" href={siteUrl} />
        <script type="application/ld+json">{JSON.stringify(organizationJsonLd)}</script>
        <script type="application/ld+json">{JSON.stringify(softwareJsonLd)}</script>
        <script type="application/ld+json">{JSON.stringify(buildFaqJsonLd(i18n.currentLocale))}</script>
      </Head>
      <PageSocialHead title={homeTitle} description={homeDescription} canonicalUrl={siteUrl} />
      <HomeHero ctaVariant={ctaVariant || 'A'} />
      <HomeTrustBar />
      <LogoStrip />
      <HomeZySignSpotlight />
      <HomeOpenStack />
      <HomeSuiteSpotlight />
      <HomePathwayStrip />
      <ProviderMarquee />
      <main>
        <section className={styles.terminalSection}>
          <ScrollReveal>
            <div className={styles.sectionHeader}>
              <span className={styles.sectionEyebrow}>{homeCopy.sectionTerminalEyebrow}</span>
              <h2 className={styles.sectionTitle}>{homeCopy.sectionTerminalTitle}</h2>
              <p className={styles.sectionSubtitle}>{homeCopy.sectionTerminalSubtitle}</p>
            </div>
            <Suspense fallback={null}>
              <TerminalDemo />
            </Suspense>
          </ScrollReveal>
        </section>
        <ScrollReveal direction="up">
          <HomeStats />
        </ScrollReveal>
        <HomeProducts />
        <HomeRunsAnywhere />
        <HomeHowItWorks />
        <HomeSolutions />

        <section className={styles.comparisonSection}>
          <ScrollReveal>
            <GuidedDecksHub />
          </ScrollReveal>
        </section>

        <section className={styles.comparisonSection} id="compare-section">
          <ScrollReveal>
            <div className={styles.sectionHeader}>
              <span className={styles.sectionEyebrow}>{homeCopy.sectionCompareEyebrow}</span>
              <h2 className={styles.sectionTitle}>{homeCopy.sectionCompareTitle}</h2>
              <p className={styles.sectionSubtitle}>{homeCopy.sectionCompareSubtitle}</p>
            </div>
          </ScrollReveal>
          <ComparisonTable />
        </section>

        <HomeTestimonialsSection />
        <HomeTrustedBySection />
        <ScrollReveal>
          <HomeBlog />
        </ScrollReveal>

        <section className={styles.faqSection} id="faq-section">
          <ScrollReveal>
            <div className={styles.sectionHeader}>
              <span className={styles.sectionEyebrow}>{homeCopy.sectionFaqEyebrow}</span>
              <h2 className={styles.sectionTitle}>{homeCopy.sectionFaqTitle}</h2>
              <p className={styles.sectionSubtitle}>{homeCopy.sectionFaqSubtitle}</p>
            </div>
          </ScrollReveal>
          <FAQAccordion mobileLimit={6} />
        </section>

        <SupportOpenSourceSection />

        <HomeCTA />
      </main>

      <Link to="/contact?intent=demo" className={styles.chatButton} aria-label="Contact us" role="button">
        &#128172;
      </Link>

      <div className={showSticky ? styles.stickyCtaVisible : styles.stickyCta}>
        <span className={styles.stickyCtaText}>{stickyConfig.text}</span>
        <Link
          to={stickyConfig.to}
          className={styles.stickyCtaBtn}
          role="button"
          onClick={() =>
            dispatchMarketingEvent('homepage_cta_click', {
              section: 'sticky',
              target: 'primary',
              intent: stickyIntent,
              destination: stickyConfig.to,
            })
          }
        >
          {stickyConfig.label}
        </Link>
      </div>
      <Suspense fallback={null}>
        <ExitIntent />
      </Suspense>
    </Layout>
  );
}
