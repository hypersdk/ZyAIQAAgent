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
import {platform} from '../data/platform-stats';

export default function KubeVirt(): ReactNode {
  return (
    <ProductPage
      title="KubeVirt Migration"
      description="Run virtual machines on Kubernetes with KubeVirt. Migrate from any hypervisor with full lifecycle management."
    >
      <MarketingHero pageId="kubevirt" />

      <PageContent>
        {/* What is KubeVirt */}
        <SectionHeader
          eyebrow="Overview"
          title="VMs as Kubernetes-Native Resources"
          subtitle="KubeVirt extends Kubernetes to run virtual machines alongside container workloads. VMs are scheduled, managed, and monitored using the same Kubernetes APIs and tooling your team already knows. HyperSDK Platform provides the complete migration pipeline to get your VMs running on KubeVirt."
        />

        {/* Migration Flow */}
        <SectionHeader eyebrow="Migration Flow" title="Three Steps to KubeVirt" />

        {/* Flow visualization */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '3rem',
            flexWrap: 'wrap',
          }}
        >
          {['Export from Any Source', 'Convert & Fix Guest OS', 'Deploy to KubeVirt'].map((label, i) => (
            <div key={label} style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <div
                className={i === 2 ? styles.primaryBtn : undefined}
                style={
                  i === 2
                    ? {
                        padding: '0.65rem 1.2rem',
                        fontSize: '0.85rem',
                        fontFamily: 'var(--hs-font-mono)',
                        whiteSpace: 'nowrap' as const,
                      }
                    : {
                        background: 'rgba(255, 140, 0, 0.1)',
                        border: '1px solid rgba(255, 140, 0, 0.2)',
                        borderRadius: 10,
                        padding: '0.65rem 1.2rem',
                        color: 'var(--hs-accent-light)',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        fontFamily: 'var(--hs-font-mono)',
                        whiteSpace: 'nowrap' as const,
                      }
                }
              >
                {label}
              </div>
              {i < 2 && (
                <span style={{color: 'var(--hs-accent)', fontSize: '1.2rem', fontWeight: 700}}>{'\u2192'}</span>
              )}
            </div>
          ))}
        </div>

        <FeatureGrid
          features={[
            {
              title: 'Export',
              desc: `Extract VMs from vSphere, Nutanix AHV, AWS, Azure, GCP, Hyper-V, or any of ${platform.cloudProviders} supported providers with full manifest tracking.`,
            },
            {
              title: 'Convert',
              desc: 'Convert disk formats, inject drivers, fix guest OS configurations. Windows and Linux handled automatically.',
            },
            {
              title: 'Deploy',
              desc: 'Upload disk images to Kubernetes storage and deploy as VirtualMachine resources with a single command.',
            },
          ]}
          columns={3}
        />

        {/* Benefits */}
        <SectionHeader eyebrow="Benefits" title="Why Run VMs on Kubernetes" />
        <FeatureGrid
          features={[
            {title: 'Unified Management', desc: 'Manage VMs and containers through a single Kubernetes control plane.'},
            {
              title: 'Infrastructure as Code',
              desc: 'Define VM infrastructure with YAML. GitOps workflows apply to VMs just like containers.',
            },
            {
              title: 'Auto-Scaling and HA',
              desc: 'Kubernetes scheduling, node affinity, and live migration keep workloads running.',
            },
            {
              title: 'Cost Optimization',
              desc: 'Eliminate per-socket licensing. Run VMs on commodity Kubernetes clusters.',
            },
            {
              title: 'Single Dashboard',
              desc: 'Monitor VMs, containers, migrations, and cluster health from one interface.',
            },
            {
              title: 'Carbon-Aware',
              desc: 'Schedule VM operations during low-carbon periods using real-time grid data.',
            },
          ]}
          columns={3}
        />

        {/* Code & Containers Migration */}
        <div
          className={styles.featureCard}
          style={{
            maxWidth: 900,
            margin: '0 auto 3rem',
            border: '1px solid rgba(240,88,58,0.12)',
          }}
        >
          <h3 className={styles.featureCardTitleLg}>Migrate Code, Containers & Runtime -- Not Just VMs</h3>
          <p className={styles.featureCardDesc} style={{marginBottom: '1rem'}}>
            Go beyond disk-level conversion. Automatically translate your application stack -- from Docker Compose,
            systemd services, and VM-based workloads -- into Kubernetes-native resources and KubeVirt virtual machines.
          </p>
          <ul className={styles.featureCardList}>
            <li>Convert Docker Compose {'->'} Kubernetes Deployments, Services, and PVCs</li>
            <li>Map systemd services {'->'} containerized workloads or init containers</li>
            <li>Preserve environment variables, volumes, networking, and dependencies</li>
            <li>Optional: keep workloads as VMs using KubeVirt when containers aren't suitable</li>
          </ul>
          <p style={{color: 'var(--hs-accent)', fontSize: '0.9rem', fontWeight: 500, margin: '1rem 0 0'}}>
            Reduce migration effort from weeks to minutes with automated, deterministic transformations.
          </p>
        </div>

        {/* VM vs Container Decision Matrix */}
        <SectionHeader
          eyebrow="Decision Guide"
          title="VM vs Container Decision Matrix"
          subtitle="Not every workload belongs in a container. Use this matrix to decide which Kubernetes primitive fits each workload."
        />
        <div className={styles.featureCard} style={{overflow: 'hidden', padding: 0, marginBottom: '5rem'}}>
          {/* Table header */}
          <div
            className={styles.hideOnMobile}
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 150px 1fr',
              padding: '0.75rem 1.5rem',
              background: 'rgba(255, 140, 0, 0.08)',
              borderBottom: '1px solid var(--hs-border)',
            }}
          >
            <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.8rem'}}>
              Workload
            </span>
            <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.8rem', textAlign: 'center'}}>
              Recommendation
            </span>
            <span className={styles.monoLabel} style={{marginBottom: 0, fontSize: '0.8rem'}}>
              Why
            </span>
          </div>
          {/* Table rows */}
          {[
            {
              workload: 'Legacy Windows Apps',
              recommendation: 'VM (KubeVirt)',
              why: 'Needs kernel, drivers, registry, and full OS environment.',
              isVM: true,
            },
            {
              workload: 'Stateless Microservices',
              recommendation: 'Container (Pod)',
              why: 'Lightweight, fast scaling, no persistent state.',
              isVM: false,
            },
            {
              workload: 'Databases (PostgreSQL, MySQL)',
              recommendation: 'VM (KubeVirt)',
              why: 'Persistent storage, kernel tuning, memory management.',
              isVM: true,
            },
            {
              workload: 'CI/CD Runners',
              recommendation: 'Container (Pod)',
              why: 'Ephemeral, fast startup, disposable environments.',
              isVM: false,
            },
            {
              workload: 'Desktop / VDI',
              recommendation: 'VM (KubeVirt)',
              why: 'Full OS, GPU passthrough, display protocol support.',
              isVM: true,
            },
            {
              workload: 'Web Frontends',
              recommendation: 'Container (Pod)',
              why: 'Horizontal scaling, minimal resource footprint.',
              isVM: false,
            },
          ].map((row, i) => (
            <div
              key={row.workload}
              className={styles.stackOnMobile}
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 150px 1fr',
                padding: '0.75rem 1.5rem',
                borderBottom: i < 5 ? '1px solid var(--hs-border)' : 'none',
                alignItems: 'center',
              }}
            >
              <span style={{color: 'var(--hs-text-body)', fontSize: '0.9rem', fontWeight: 500}}>{row.workload}</span>
              <span
                style={{
                  textAlign: 'center',
                  fontSize: '0.8rem',
                  fontFamily: 'var(--hs-font-mono)',
                  fontWeight: 600,
                  color: row.isVM ? 'var(--hs-accent-light)' : 'var(--hs-success-light)',
                }}
              >
                {row.recommendation}
              </span>
              <span style={{color: 'var(--hs-text-muted)', fontSize: '0.85rem'}}>{row.why}</span>
            </div>
          ))}
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.kubevirt} />

        {/* CTA */}
        <CTASection
          title="See KubeVirt Migration in Action"
          subtitle="Schedule a live demo. We will walk through a complete migration from your current hypervisor to KubeVirt on your Kubernetes cluster."
        />
      </PageContent>
    </ProductPage>
  );
}
