// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {
  ProductPage,
  PageContent,
  SectionHeader,
  FeatureGrid,
  CTASection,
  StatGrid,
  styles,
  MarketingHero,
  RelatedBlogSection,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';

export default function DatabaseMigration(): ReactNode {
  return (
    <ProductPage
      title="Database VM Migration"
      description="Migrate database VMs with zero downtime and verified data integrity."
    >
      <MarketingHero pageId="database-migration" />

      <PageContent>
        <StatGrid
          stats={[
            {value: '4', label: 'Database Engines'},
            {value: '< 5min', label: 'Cutover Window'},
            {value: '100%', label: 'Data Integrity Verified'},
            {value: '0', label: 'Data Loss Incidents'},
          ]}
        />

        <SectionHeader eyebrow="Supported" title="Supported Database Engines" />
        <FeatureGrid
          columns={2}
          features={[
            {title: 'PostgreSQL', desc: 'Versions 12-16. Replication preserved, integrity validated post-migration.'},
            {
              title: 'MySQL / MariaDB',
              desc: 'MySQL 8.0/8.4, MariaDB 10.6/11.x. Transaction consistency maintained throughout.',
            },
            {title: 'Oracle Database', desc: '19c, 21c, 23ai. RAC-aware migration with proper node sequencing.'},
            {title: 'SQL Server', desc: '2019, 2022. Availability Groups re-synchronized, encryption keys preserved.'},
          ]}
        />

        <SectionHeader
          eyebrow="Approach"
          title="Near-Zero Downtime Approach"
          subtitle="Incremental snapshots transfer most data while the database is running. The final cutover syncs only the delta, minimizing downtime to minutes."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Incremental Sync',
              desc: 'Only changed blocks are transferred after the initial snapshot. Minimizes bandwidth and export time.',
            },
            {
              title: 'Automated Validation',
              desc: 'Post-migration health checks verify table consistency, index integrity, and query performance.',
            },
            {
              title: 'Instant Rollback',
              desc: 'Original VMs are preserved until full sign-off. Restore in minutes if anything fails validation.',
            },
          ]}
        />

        {/* Database-Specific Features */}
        <SectionHeader
          eyebrow="Deep Integration"
          title="Database-Specific Features"
          subtitle="Purpose-built migration capabilities for each database engine, preserving replication, clustering, and tuning configurations."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'PostgreSQL',
              desc: 'Streaming replication topology preserved across primary and replicas. WAL archiving configuration migrated intact. pg_hba.conf and connection pooler settings carried over.',
            },
            {
              title: 'MySQL / MariaDB',
              desc: 'Group replication membership and topology maintained. InnoDB buffer pool size and tuning parameters optimized for KVM. Binary log positions tracked for seamless cutover.',
            },
            {
              title: 'SQL Server',
              desc: 'AlwaysOn Availability Group synchronization preserved. Windows authentication and linked server credentials migrated. TempDB and memory configuration adapted for target hardware.',
            },
            {
              title: 'Oracle Database',
              desc: 'RAC-aware migration with proper node sequencing and voting disk handling. ASM disk group layouts mapped to KVM storage. Listener and TNS configurations updated automatically.',
            },
          ]}
        />

        {/* Post-Migration Validation Checklist */}
        <SectionHeader
          eyebrow="Validation"
          title="Post-Migration Validation"
          subtitle="Every database migration includes a comprehensive validation checklist to confirm production readiness."
        />
        <div className={styles.featureCard} style={{maxWidth: 700, margin: '0 auto 5rem'}}>
          <ul style={{listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem'}}>
            {[
              {
                check: 'Data Integrity',
                detail: 'Row counts, checksum verification, and schema comparison between source and target.',
              },
              {
                check: 'Replication Status',
                detail: 'Confirm all replicas are synchronized and streaming from the migrated primary.',
              },
              {
                check: 'Connection Strings',
                detail: 'Validate application connection strings resolve to the new KVM-hosted database endpoints.',
              },
              {
                check: 'Performance Baseline',
                detail:
                  'Run standard query benchmarks and compare latency and throughput against pre-migration baselines.',
              },
              {
                check: 'Backup Verification',
                detail: 'Confirm automated backup jobs execute successfully and produce restorable snapshots.',
              },
              {
                check: 'Monitoring Setup',
                detail:
                  'Verify metrics collection, alerting rules, and dashboard visibility for the migrated database.',
              },
            ].map((item) => (
              <li key={item.check} style={{display: 'flex', gap: '1rem', alignItems: 'flex-start'}}>
                <span style={{color: 'var(--hs-success)', fontWeight: 700, fontSize: '1.1rem', flexShrink: 0}}>
                  {'\u2713'}
                </span>
                <div>
                  <strong style={{color: 'var(--hs-text-heading)', fontSize: '0.95rem'}}>{item.check}</strong>
                  <p
                    style={{color: 'var(--hs-text-muted)', fontSize: '0.85rem', margin: '0.25rem 0 0', lineHeight: 1.6}}
                  >
                    {item.detail}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.databaseMigration} />

        <CTASection
          title="Plan Your Database Migration"
          subtitle="Our database migration specialists will assess your workloads and execute a pilot migration with full data integrity verification."
          primaryCta={{label: 'Plan Your Database Migration', to: '/contact?intent=database'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=database'}}
        />
      </PageContent>
    </ProductPage>
  );
}
