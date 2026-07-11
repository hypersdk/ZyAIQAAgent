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
  RelatedBlogSection,
  styles,
  MarketingHero,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';

export default function AirGap(): ReactNode {
  return (
    <ProductPage
      title="Air-Gap & Disconnected Migration"
      description="Migrate VMs in secure environments without internet access. Built for government, defense, and compliance-restricted networks."
    >
      <MarketingHero pageId="airgap" />

      <PageContent>
        <SectionHeader eyebrow="Use Cases" title="Built for the Most Restricted Environments" />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Classified Networks',
              desc: 'Defense and intelligence organizations with strict data diode policies and air-gapped infrastructure.',
            },
            {
              title: 'Offshore & Remote Sites',
              desc: 'Oil rigs, research stations, and maritime vessels with intermittent or no connectivity.',
            },
            {
              title: 'Financial Trading',
              desc: 'Air-gapped trading infrastructure isolated from corporate networks for latency control.',
            },
            {
              title: 'Healthcare Compliance',
              desc: 'Medical device networks operating under FDA regulations requiring validated, traceable migrations.',
            },
            {
              title: 'SCIF Environments',
              desc: 'Sensitive Compartmented Information Facilities requiring complete network isolation.',
            },
            {
              title: 'Manufacturing',
              desc: 'Factory floor systems with OT network segmentation and no internet access.',
            },
          ]}
        />

        <SectionHeader eyebrow="Features" title="Key Features" />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'No Internet Required',
              desc: 'Every component is pre-packaged for fully offline operation. No package manager, no container registry, no cloud API calls.',
            },
            {
              title: 'FIPS-Compatible',
              desc: 'Cryptographic operations use validated modules. Data integrity verified at every stage of the migration pipeline.',
            },
            {
              title: 'Complete Audit Trail',
              desc: 'Every operation is logged with timestamps, operator identity, and cryptographic hashes. Suitable for SIEM ingestion.',
            },
            {
              title: 'Chain of Custody',
              desc: 'Manifest files track every artifact from export through transfer to import. Tamper-evident packaging with digital signatures.',
            },
          ]}
        />

        {/* Secure Transfer Methods */}
        <SectionHeader
          eyebrow="Transfer"
          title="Secure Transfer Methods"
          subtitle="Multiple verified methods for moving migration artifacts across security boundaries."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Encrypted USB',
              desc: 'AES-256 encrypted portable drives with hardware-backed key storage. FIPS 140-2 validated encryption modules. Automatic wipe on tamper detection.',
            },
            {
              title: 'Data Diode',
              desc: 'One-way transfer for classified networks using hardware-enforced unidirectional data flow. Compatible with Owl, Waterfall, and BAE Systems data diodes.',
            },
            {
              title: 'Manual Copy',
              desc: 'Verified checksums with SHA-256 at every stage. Manifest files list every artifact with size, hash, and timestamp. Human-verifiable integrity chain.',
            },
            {
              title: 'Sneakernet',
              desc: 'Physical media with chain of custody documentation. Tamper-evident packaging with serial-numbered seals. Compatible with DoD courier procedures.',
            },
          ]}
        />

        {/* Air-Gap Deployment Guide */}
        <SectionHeader
          eyebrow="Workflow"
          title="Air-Gap Deployment Guide"
          subtitle="Three simple steps to package, transfer, and deploy migrations in disconnected environments."
        />
        <div className={`${styles.featureGrid} ${styles.featureGridCol3}`}>
          {[
            {
              step: '1',
              title: 'Package',
              code: 'h2kvmctl package --offline --output /media/usb/',
              desc: 'Bundle all migration artifacts, dependencies, and tools into a self-contained offline package. Includes cryptographic manifest.',
            },
            {
              step: '2',
              title: 'Transfer',
              code: 'Physically move media to air-gapped network',
              desc: 'Transport the encrypted package across the security boundary using your approved transfer method. Chain of custody documented.',
            },
            {
              step: '3',
              title: 'Deploy',
              code: 'h2kvmctl deploy --offline --input /media/usb/',
              desc: 'Import and deploy VMs on the air-gapped target. Checksums verified automatically before deployment begins.',
            },
          ].map((item) => (
            <div key={item.step} className={styles.featureCard} style={{position: 'relative', paddingTop: '2.5rem'}}>
              <div
                style={{
                  position: 'absolute',
                  top: -16,
                  left: 24,
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  background: 'var(--hs-gradient-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: '0.9rem',
                  color: '#fff',
                  fontFamily: 'var(--hs-font-mono)',
                }}
              >
                {item.step}
              </div>
              <h3 className={styles.featureCardTitle}>{item.title}</h3>
              <div
                style={{
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--hs-border)',
                  borderRadius: 8,
                  padding: '0.75rem 1rem',
                  marginBottom: '0.75rem',
                  overflow: 'auto',
                }}
              >
                <code
                  style={{
                    fontFamily: 'var(--hs-font-mono)',
                    fontSize: '0.8rem',
                    color: 'var(--hs-accent-light)',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {item.code}
                </code>
              </div>
              <p className={styles.featureCardDesc}>{item.desc}</p>
            </div>
          ))}
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.airgap} />

        <CTASection
          title="Need Air-Gap Migration Support?"
          subtitle="Our team has experience deploying in classified and disconnected environments. Contact us to discuss your security requirements."
          primaryCta={{label: 'Contact for Air-Gap Solutions', to: '/contact?intent=airgap'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=airgap'}}
        />
      </PageContent>
    </ProductPage>
  );
}
