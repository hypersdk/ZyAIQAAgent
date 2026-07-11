// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {
  ProductPage,
  MigrationMarketingHero,
  PageContent,
  SectionHeader,
  FeatureGrid,
  CTASection,
  RelatedBlogSection,
  StatGrid,
  MigrationTrustStrip,
  styles,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {getMigrationLanding} from '../data/migration-landings-locale';

export default function WindowsMigration(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const landing = getMigrationLanding('windows-migration', i18n.currentLocale);
  return (
    <ProductPage
      title="Windows VM Migration"
      description="Migrate Windows VMs to KVM automatically. Zero blue screens, zero downtime."
    >
      <MigrationMarketingHero landingId="windows-migration" />

      <PageContent>
        <MigrationTrustStrip config={landing} />
        <StatGrid
          stats={[
            {value: '10+', label: 'Windows Versions'},
            {value: '0', label: 'Post-Migration BSODs'},
            {value: '100%', label: 'AD Trust Preserved'},
            {value: '< 5min', label: 'Cutover Window'},
          ]}
        />

        <SectionHeader eyebrow="Compatibility" title="Every Windows Version, Fully Supported" />
        {/* Custom Windows version grid - unique checklist layout */}
        <div className={`${styles.featureGrid} ${styles.featureGridCol3}`}>
          {[
            {category: 'Windows Server', versions: ['Server 2016', 'Server 2019', 'Server 2022', 'Server 2025']},
            {category: 'Windows Desktop', versions: ['Windows 10 Pro/Enterprise', 'Windows 11 Pro/Enterprise']},
            {category: 'Legacy Windows', versions: ['Server 2012 R2', 'Server 2008 R2']},
          ].map((cat) => (
            <div key={cat.category} className={styles.featureCard}>
              <h3 className={styles.monoLabel} style={{color: 'var(--hs-accent-light)'}}>
                {cat.category}
              </h3>
              <ul
                style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                }}
              >
                {cat.versions.map((v) => (
                  <li
                    key={v}
                    style={{
                      color: 'var(--hs-text-body)',
                      fontSize: '0.9rem',
                      paddingLeft: '1.25rem',
                      position: 'relative',
                    }}
                  >
                    <span style={{position: 'absolute', left: 0, color: 'var(--hs-accent)', fontWeight: 700}}>
                      {'\u2713'}
                    </span>
                    {v}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Application Preservation */}
        <SectionHeader
          eyebrow="Applications"
          title="Application Preservation"
          subtitle="Every Windows application and role is migrated intact. No re-installation, no reconfiguration."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Active Directory',
              desc: 'Domain trust relationships, group policy objects, DNS zones, and SYSVOL replication preserved across migration.',
            },
            {
              title: 'SQL Server',
              desc: 'Databases, scheduled jobs, logins, linked servers, and maintenance plans carried over without re-deployment.',
            },
            {
              title: 'Exchange Server',
              desc: 'Mailbox databases, transport rules, receive/send connectors, and content indexes migrated seamlessly.',
            },
            {
              title: 'IIS Web Server',
              desc: 'Web sites, application pools, SSL/TLS certificates, URL rewrite rules, and virtual directories all preserved.',
            },
            {
              title: 'File Server',
              desc: 'Network shares, NTFS permissions, DFS namespace and replication topology, and quotas maintained exactly.',
            },
            {
              title: 'Print Server',
              desc: 'Printers, drivers, print queues, port configurations, and per-printer permissions migrated intact.',
            },
          ]}
        />

        {/* Licensing Preservation */}
        <div
          className={styles.featureCard}
          style={{
            maxWidth: 700,
            margin: '0 auto 5rem',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            background: 'rgba(16, 185, 129, 0.04)',
            textAlign: 'center',
            padding: '2rem 2.5rem',
          }}
        >
          <h3 style={{color: 'var(--hs-success-light)', fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem'}}>
            Licensing Preservation
          </h3>
          <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', lineHeight: 1.7, margin: 0}}>
            Windows activation is preserved during migration. MAK (Multiple Activation Key) and KMS (Key Management
            Service) activations carry over to KVM -- no re-activation required. Volume licensing, OEM, and retail
            activation states are all maintained.
          </p>
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.windowsMigration} />

        <CTASection
          title="Schedule a Windows Migration Assessment"
          subtitle="Our engineers will inventory your Windows VMs and build a migration plan tailored to your Active Directory environment."
          primaryCta={{label: 'Schedule a Windows Migration Assessment', to: '/contact?intent=windows'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=windows'}}
        />
      </PageContent>
    </ProductPage>
  );
}
