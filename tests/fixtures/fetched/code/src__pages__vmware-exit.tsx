// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {useState} from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Link from '@docusaurus/Link';
import {PresentationReadingPaths} from '../components/PresentationReadingPaths';
import {PresentationPathHead} from '../components/PresentationPathHead';
import {
  ProductPage,
  MigrationMarketingHero,
  PageContent,
  SectionHeader,
  StatGrid,
  FeatureGrid,
  CTASection,
  RelatedBlogSection,
  MigrationTrustStrip,
  styles,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {platform} from '../data/platform-stats';
import {getMigrationLanding} from '../data/migration-landings-locale';

const sliderStyle: React.CSSProperties = {
  width: '100%',
  height: 6,
  borderRadius: 3,
  appearance: 'none' as const,
  background: 'rgba(255, 255, 255, 0.1)',
  outline: 'none',
  cursor: 'pointer',
  accentColor: '#f0583a',
};

function formatCurrency(n: number): string {
  return '$' + n.toLocaleString('en-US');
}

export default function VMwareExit(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const landing = getMigrationLanding('vmware-exit', i18n.currentLocale);
  const [sockets, setSockets] = useState(10);
  const [costPerSocket, setCostPerSocket] = useState(10000);

  const vmwareCost = sockets * costPerSocket;
  const kvmCost = sockets * 800;
  const savings = vmwareCost - kvmCost;
  const savingsPercent = Math.round((savings / vmwareCost) * 100);

  return (
    <ProductPage
      title="VMware Exit Strategy"
      description="Escape VMware licensing. Migrate to KVM with zero disruption using HyperSDK Platform."
    >
      <PresentationPathHead
        allowedPaths={['vmware-exit', 'cio', 'pm']}
        fallbackTitle="VMware Exit Strategy · Zyvor"
        fallbackDescription="Escape VMware licensing. Migrate to KVM with zero disruption using HyperSDK Platform."
      />
      <MigrationMarketingHero landingId="vmware-exit" />

      <PageContent>
        <MigrationTrustStrip config={landing} />
        {/* The Problem */}
        <SectionHeader eyebrow="The Problem" title="VMware Licensing Has Become Unsustainable" />
        <FeatureGrid
          features={[
            {
              title: '200-500% Cost Increases',
              desc: 'vSphere licenses now $5K-15K per socket, vCenter $6K-10K, vSAN $2K-8K per socket, NSX $4K-12K per socket. Perpetual licenses are gone.',
            },
            {
              title: 'Forced Bundle Purchasing',
              desc: 'Must buy entire suites even when you only need vSphere. Paying for features you never use.',
            },
            {
              title: 'Vendor Lock-In Deepens',
              desc: 'Proprietary formats and API changes make it harder to leave. The longer you wait, the harder the exit.',
            },
          ]}
          columns={3}
        />

        {/* The Real Numbers */}
        <SectionHeader
          eyebrow="The Real Numbers"
          title="What Broadcom Is Actually Charging"
          subtitle="These are real numbers from real customers. Broadcom forced 3-year minimum commitments on every renewal."
        />
        <FeatureGrid
          features={[
            {
              title: '$45K/yr \u2192 $187K/yr',
              desc: '315% increase on a single renewal. This is not an outlier -- it is the new normal for VMware customers.',
            },
            {
              title: '$1.2M/yr',
              desc: '500-VM enterprise under VMware Cloud Foundation. Previously $350K/yr -- a cost increase that broke annual budgets overnight.',
            },
            {
              title: '$100K minimum',
              desc: 'Small businesses told to meet a $100K minimum order or "find a different vendor." Broadcom does not want your business.',
            },
            {
              title: '16-core minimum',
              desc: 'Per-core licensing with a 16-core minimum per socket. Even old servers with 8 cores pay for 16. That is a 60% increase for legacy hardware.',
            },
          ]}
          columns={2}
        />

        {/* Cost Savings */}
        <SectionHeader
          eyebrow="Cost Savings"
          title="93% Annual Cost Reduction"
          subtitle={`Real numbers from a 350-VM Fortune 500 migration. ${platform.firstBootSuccess} first-boot success rate. 70% average TCO reduction across all customer deployments.`}
        />
        <StatGrid
          stats={[
            {value: '$1.4M', label: 'VMware Annual Cost'},
            {value: '$96K', label: 'KVM Annual Cost'},
            {value: '$1.2M', label: 'Annual Savings'},
          ]}
          columns={3}
        />

        {/* How It Works */}
        <SectionHeader eyebrow="Toolchain" title="Three Tools, One Pipeline" />
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '0.5rem',
            flexWrap: 'wrap',
            marginBottom: '5rem',
          }}
        >
          {[
            {label: 'HyperSDK Platform', desc: 'Export from vSphere or Nutanix'},
            {label: 'hyper2kvm', desc: 'Convert & fix'},
            {label: 'libvirt / KubeVirt', desc: 'Deploy on KVM'},
          ].map((tool, i) => (
            <div key={tool.label} style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <div
                className={i === 2 ? styles.primaryBtn : undefined}
                style={
                  i === 2
                    ? {
                        padding: '0.85rem 1.5rem',
                        textAlign: 'center' as const,
                        flexDirection: 'column' as const,
                      }
                    : {
                        background: 'rgba(255, 140, 0, 0.1)',
                        border: '1px solid rgba(255, 140, 0, 0.2)',
                        borderRadius: 10,
                        padding: '0.85rem 1.5rem',
                        textAlign: 'center' as const,
                      }
                }
              >
                <div
                  style={{
                    color: i === 2 ? '#fff' : 'var(--hs-accent-light)',
                    fontSize: '0.95rem',
                    fontWeight: 700,
                    fontFamily: 'var(--hs-font-mono)',
                  }}
                >
                  {tool.label}
                </div>
                <div
                  style={{
                    color: i === 2 ? 'rgba(255,255,255,0.7)' : 'var(--hs-text-muted)',
                    fontSize: '0.75rem',
                    marginTop: '0.25rem',
                  }}
                >
                  {tool.desc}
                </div>
              </div>
              {i < 2 && (
                <span style={{color: 'var(--hs-accent)', fontSize: '1.2rem', fontWeight: 700}}>{'\u2192'}</span>
              )}
            </div>
          ))}
        </div>

        {/* Customer Quote */}
        <div className={styles.featureCard} style={{textAlign: 'center', marginBottom: '2rem'}}>
          <p
            style={{
              color: 'var(--hs-text-body)',
              fontSize: '1.1rem',
              fontStyle: 'italic',
              lineHeight: 1.7,
              maxWidth: 700,
              margin: '0 auto 1rem',
            }}
          >
            {`We saved $1.2M annually by migrating 350 VMs to KVM. The ${platform.firstBootSuccess} first-boot success rate meant minimal disruption.`}
          </p>
          <p style={{color: 'var(--hs-accent-light)', fontSize: '0.9rem', fontWeight: 600, margin: 0}}>
            -- VP Infrastructure, Fortune 500 Financial Services
          </p>
        </div>

        {/* Quick Savings Estimate */}
        <div
          className={styles.featureCard}
          style={{
            border: '1px solid var(--hs-border-accent)',
            marginBottom: '2rem',
          }}
        >
          <div style={{textAlign: 'center', marginBottom: '2rem'}}>
            <span className={styles.sectionEyebrow}>Interactive Calculator</span>
            <h2 className={styles.sectionTitle} style={{fontSize: '1.8rem'}}>
              Quick Savings Estimate
            </h2>
            <p className={styles.featureCardDesc} style={{textAlign: 'center'}}>
              Drag the sliders to estimate your VMware exit savings.
            </p>
          </div>

          <div className={styles.gridCol2} style={{gap: '2rem', marginBottom: '2rem'}}>
            <div>
              <label
                className={styles.monoLabel}
                style={{display: 'block', marginBottom: '0.5rem', fontSize: '0.8rem'}}
              >
                Number of Sockets: <span style={{color: 'var(--hs-accent-light)'}}>{sockets}</span>
              </label>
              <input
                type="range"
                min={2}
                max={100}
                value={sockets}
                onChange={(e) => setSockets(Number(e.target.value))}
                style={sliderStyle}
              />
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  color: 'var(--hs-text-muted)',
                  fontSize: '0.7rem',
                  marginTop: '0.25rem',
                }}
              >
                <span>2</span>
                <span>100</span>
              </div>
            </div>
            <div>
              <label
                className={styles.monoLabel}
                style={{display: 'block', marginBottom: '0.5rem', fontSize: '0.8rem'}}
              >
                VMware Cost / Socket:{' '}
                <span style={{color: 'var(--hs-accent-light)'}}>{formatCurrency(costPerSocket)}</span>
              </label>
              <input
                type="range"
                min={5000}
                max={20000}
                step={500}
                value={costPerSocket}
                onChange={(e) => setCostPerSocket(Number(e.target.value))}
                style={sliderStyle}
              />
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  color: 'var(--hs-text-muted)',
                  fontSize: '0.7rem',
                  marginTop: '0.25rem',
                }}
              >
                <span>$5K</span>
                <span>$20K</span>
              </div>
            </div>
          </div>

          <div
            style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--hs-border-accent)',
              borderRadius: 12,
              padding: '1.5rem 2rem',
              textAlign: 'center',
              marginBottom: '1.5rem',
            }}
          >
            <div style={{fontSize: '1rem', color: 'var(--hs-text-body)', lineHeight: 2}}>
              <span>
                Current VMware:{' '}
                <strong style={{color: 'var(--hs-error)', fontFamily: 'var(--hs-font-mono)'}}>
                  {formatCurrency(vmwareCost)}/year
                </strong>
              </span>
              <span style={{color: 'var(--hs-text-muted)', margin: '0 0.75rem'}}>{'\u2192'}</span>
              <span>
                KVM:{' '}
                <strong style={{color: 'var(--hs-success)', fontFamily: 'var(--hs-font-mono)'}}>
                  {formatCurrency(kvmCost)}/year
                </strong>
              </span>
              <span style={{color: 'var(--hs-text-muted)', margin: '0 0.75rem'}}>=</span>
              <span
                style={{
                  color: 'var(--hs-accent-light)',
                  fontWeight: 800,
                  fontSize: '1.15rem',
                  fontFamily: 'var(--hs-font-mono)',
                }}
              >
                {formatCurrency(savings)} saved ({savingsPercent}%)
              </span>
            </div>
          </div>

          <div style={{textAlign: 'center'}}>
            <Link className={styles.primaryBtn} to="/contact?intent=vmware-exit">
              Get a Detailed Analysis
            </Link>
          </div>
        </div>

        <PresentationReadingPaths
          paths={['vmware-exit', 'cio', 'pm']}
          defaultPath="vmware-exit"
          eyebrow="Execution-first"
          title="Don't start with architecture"
          subtitle="Everyone wants the VMware exit. Most programs break on operational continuity — keeping workloads live during convert, validate, and cutover. Download these decks in order."
        />

        <RelatedBlogSection links={solutionPageBlogLinks.vmwareExit} />

        {/* CTA */}
        <CTASection
          title="Schedule a VMware Exit Assessment"
          subtitle="We will analyze your VMware environment, estimate migration effort, and provide a detailed cost-savings projection -- at no cost."
          primaryCta={{label: 'Schedule a VMware Exit Assessment', to: '/contact?intent=vmware-exit'}}
        />
      </PageContent>
    </ProductPage>
  );
}
