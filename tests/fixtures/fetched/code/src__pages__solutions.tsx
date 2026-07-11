// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {
  ProductPage,
  MarketingHero,
  PageContent,
  SectionHeader,
  FeatureGrid,
  CTASection,
  styles,
  TrustNarrativeDisclaimer,
  RelatedBlogSection,
} from '../components/shared';
import {solutionsCardBlogLinks, solutionPageBlogLinks} from '../data/solution-blog-links';
import {getSolutionCardOverride, getSolutionsPageCopy} from '../data/solutions-locale';
import {trustNarrativeDisclaimerText} from '../data/trust-narratives';
import {platform} from '../data/platform-stats';

const solutions = [
  {
    id: 'vmware-exit',
    contactIntent: 'vmware-exit',
    icon: '\u26A1',
    title: 'VMware & Nutanix Exit',
    tagline: 'Escape proprietary HCI licensing without disrupting operations.',
    description:
      'Broadcom-era VMware shocks and Nutanix renewal pressure pushed estates toward open KVM. HyperSDK Platform gives you a clear path out of vSphere or Nutanix AHV.',
    benefits: [
      'Export VMs directly from vSphere or Nutanix AHV with full manifest tracking',
      'Convert VMDK images to KVM-compatible formats automatically',
      'Inject VirtIO drivers and repair bootloaders for seamless transition',
      'Maintain data integrity with SHA-256 checksum verification',
      'Zero-downtime migration with incremental export support',
    ],
    caseStudyLabel: 'Read Case Study: Fortune 500 Financial',
    caseStudyLink: '/case-studies',
  },
  {
    id: 'cloud-migration',
    contactIntent: 'repatriation',
    icon: '\u2601',
    title: 'Multi-Cloud Migration',
    tagline: 'Move workloads between public cloud and KVM in either direction with one platform.',
    description:
      'HyperSDK Platform provides a unified interface for VM migration across AWS, Azure, GCP, OCI, Hyper-V, OpenStack, Alibaba Cloud, Proxmox, and KubeVirt -- from public cloud to KVM, KVM to public cloud, or across providers when you are consolidating or distributing for resilience.',
    benefits: [
      `${platform.cloudProviders} cloud provider backends with a single, consistent API`,
      `${platform.apiEndpoints} REST API endpoints for complete programmatic control`,
      'Cross-provider VM discovery and inventory management',
      'Automated format conversion between provider disk formats',
      'Resume support for large VM transfers over unreliable networks',
    ],
    caseStudyLabel: 'Read Case Study: National Healthcare',
    caseStudyLink: '/case-studies',
  },
  {
    id: 'disaster-recovery',
    contactIntent: 'assessment',
    icon: '\u26C1',
    title: 'Disaster Recovery',
    tagline: 'Automated backup and recovery across your entire VM fleet.',
    description:
      'Build resilient DR strategies with automated scheduling, changed-block tracking for incremental exports, and multi-site deployment. Keep your recovery point objectives tight and your recovery time minimal.',
    benefits: [
      'Scheduled VM exports with cron-based automation',
      'Changed Block Tracking (CBT) for incremental backups',
      'Multi-site replication across different cloud providers',
      'Manifest-tracked exports with full audit trail',
      'Carbon-aware scheduling to optimize for cost and sustainability',
    ],
    caseStudyLabel: 'Read Case Studies',
    caseStudyLink: '/case-studies',
  },
  {
    id: 'openstack-private-cloud',
    contactIntent: 'demo',
    icon: '\u2609',
    title: 'OpenStack Private Cloud',
    tagline: 'First-class Nova, Glance, and day-2 ops across the suite.',
    description:
      'Export Nova VMs and Glance images with HyperSDK Platform, convert and validate with hyper2kvm, deploy QCOW2 back to Glance, and run Nova & Glance operations from Machina — without Horizon lock-in.',
    benefits: [
      'OpenStack as a first-class provider in HyperSDK Platform export/import',
      'hyper2kvm deploy-to-Glance with optional Nova boot workflows',
      'Machina console for Nova/Glance day-2 on the same KVM host',
      'GuestKit disk inspect and repair before Glance upload',
      'Unified API and dashboard visibility across the migration pipeline',
    ],
    link: '/docs/openstack',
    caseStudyLabel: 'OpenStack integration guide',
    caseStudyLink: '/docs/openstack',
  },
  {
    id: 'confidential-sovereign',
    contactIntent: 'demo',
    icon: '\u26D4',
    title: 'Confidential / Sovereign Cloud',
    tagline: 'TEE attestation, measured images, and sovereign mode on KubeVirt.',
    description:
      'Run regulated workloads on SEV-SNP and TDX with Aether confidential VMs and Kata pods. Composite with Ragnarok for fleet attestation, trust scores, attest-gated secrets, and re-attestation before migration cutover.',
    benefits: [
      'Hardware-rooted trust with vTPM, launch security, and strict attestation gates',
      'Measured qcow2 catalog with cosign verification before deploy',
      'Sovereign mode: BYOK signing, offline bundles, and region lock',
      'Confidential-blue-green migration with matching TEE labels',
      'Composite Aether + Ragnarok for fleet trust enforce and `/confidential` UI',
    ],
    link: '/confidential-computing',
    caseStudyLabel: 'Confidential fabric docs',
    caseStudyLink: '/docs/confidential-fabric',
  },
  {
    id: 'kubernetes',
    contactIntent: 'demo',
    icon: '\u2638',
    title: 'Kubernetes Modernization',
    tagline: 'Run VMs on Kubernetes with KubeVirt integration.',
    description:
      'Bridge your traditional VM workloads with cloud-native infrastructure. Deploy and manage virtual machines on Kubernetes using KubeVirt, with full lifecycle management through the HyperSDK Platform platform.',
    benefits: [
      'Deploy VMs as KubeVirt resources on any Kubernetes cluster',
      'Convert existing VM images for KubeVirt compatibility',
      'Unified management of VMs and containers in one platform',
      'Full API and dashboard support for KubeVirt operations',
      'Gradual modernization path from VMs to containers',
    ],
    link: '/kubevirt',
    caseStudyLabel: 'Learn More About KubeVirt',
    caseStudyLink: '/kubevirt',
  },
];

const industries = [
  {
    title: 'Financial Services',
    desc: 'Banks and trading firms run mission-critical workloads on VMware that cannot tolerate downtime during migration. HyperSDK Platform provides incremental export with changed-block tracking, enabling near-zero-downtime cutover windows. Full audit trails satisfy SOX and PCI-DSS; Aether and Ragnarok add TEE attestation and measured images for regulated compute on KubeVirt.',
  },
  {
    title: 'Healthcare',
    desc: 'Healthcare organizations manage sensitive patient data across legacy VM infrastructure that must remain HIPAA-compliant throughout any migration. HyperSDK Platform encrypts data in transit and at rest, provides detailed audit logs for every migration operation, and supports air-gapped deployments for environments without internet connectivity. The platform handles Windows Server workloads running EMR and PACS systems with automated VirtIO driver injection.',
  },
  {
    title: 'Government',
    desc: 'Government agencies face strict procurement cycles and vendor lock-in concerns that make VMware licensing renewals particularly painful. HyperSDK Platform enables sovereign cloud deployment on OpenStack and owned KVM/libvirt, supports offline migration for classified environments, and provides API-driven automation for FedRAMP and NIST frameworks. Confidential fabric on SEV-SNP/TDX delivers hardware attestation for sovereign workloads.',
  },
  {
    title: 'Manufacturing',
    desc: `Manufacturing companies run industrial control systems and SCADA applications on VMs that require precise hardware compatibility during migration. HyperSDK Platform preserves VM configurations including CPU topology, memory allocation, and network settings across providers. Carbon-aware scheduling aligns migration operations with sustainability targets, and the ${platform.dashboardViews} dashboard views provide plant operations teams with real-time visibility into migration progress.`,
  },
];

export default function Solutions(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const copy = getSolutionsPageCopy(i18n.currentLocale);

  return (
    <ProductPage
      title="Solutions"
      description="Enterprise solutions for VMware exit, multi-cloud migration, disaster recovery, and Kubernetes modernization."
    >
      <MarketingHero pageId="solutions" />

      <PageContent>
        <TrustNarrativeDisclaimer>{trustNarrativeDisclaimerText}</TrustNarrativeDisclaimer>
        <div className={`${styles.featureGrid} ${styles.gridSingle}`}>
          {solutions.map((s) => {
            const card = getSolutionCardOverride(s.id, i18n.currentLocale);
            const title = card.title ?? s.title;
            const tagline = card.tagline ?? s.tagline;
            const caseStudyLabel = card.caseStudyLabel ?? s.caseStudyLabel;
            return (
              <div key={s.id} id={s.id} className={`${styles.featureCard} ${styles.splitGrid}`}>
                <div>
                  <div
                    style={{
                      width: 52,
                      height: 52,
                      borderRadius: 14,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1.25rem',
                      fontSize: '1.5rem',
                      background: 'linear-gradient(135deg, rgba(255, 140, 0, 0.15), rgba(255, 140, 0, 0.05))',
                      border: '1px solid rgba(255, 140, 0, 0.2)',
                    }}
                  >
                    {s.icon}
                  </div>
                  <h2 className={styles.featureCardTitleLg} style={{fontSize: '1.8rem'}}>
                    {title}
                  </h2>
                  <p style={{color: 'var(--hs-accent-light)', fontSize: '1rem', fontWeight: 500, marginBottom: '1rem'}}>
                    {tagline}
                  </p>
                  <p className={styles.featureCardDesc}>{s.description}</p>
                </div>

                <div>
                  <h3 className={styles.sectionEyebrow}>{copy.keyBenefits}</h3>
                  <ul className={styles.featureCardList} style={{listStyle: 'none', paddingLeft: 0}}>
                    {s.benefits.map((b) => (
                      <li key={b} style={{paddingLeft: '1.5rem', position: 'relative'}}>
                        <span style={{position: 'absolute', left: 0, color: 'var(--hs-accent)', fontWeight: 700}}>
                          {'\u2713'}
                        </span>
                        {b}
                      </li>
                    ))}
                  </ul>
                  <div style={{display: 'flex', gap: '1.5rem', marginTop: '1.5rem', flexWrap: 'wrap'}}>
                    <Link
                      to={`/contact?intent=${s.contactIntent}`}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                        color: 'var(--hs-accent-light)',
                        fontWeight: 600,
                        fontSize: '0.95rem',
                        textDecoration: 'none',
                      }}
                    >
                      {copy.talkToExpert} <span>{'\u2192'}</span>
                    </Link>
                    {'link' in s && s.link && (
                      <Link
                        to={s.link as string}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          color: 'var(--hs-purple)',
                          fontWeight: 600,
                          fontSize: '0.95rem',
                          textDecoration: 'none',
                        }}
                      >
                        {copy.learnMore} <span>{'\u2192'}</span>
                      </Link>
                    )}
                    <Link
                      to={s.caseStudyLink}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                        color: '#10b981',
                        fontWeight: 600,
                        fontSize: '0.95rem',
                        textDecoration: 'none',
                      }}
                    >
                      {caseStudyLabel} <span>{'\u2192'}</span>
                    </Link>
                    {(solutionsCardBlogLinks[s.id] ?? []).map((blog) => (
                      <Link
                        key={blog.to}
                        to={blog.to}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          color: 'var(--hs-accent-light)',
                          fontWeight: 600,
                          fontSize: '0.95rem',
                          textDecoration: 'none',
                        }}
                      >
                        {blog.label} <span>{'\u2192'}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <SectionHeader
          eyebrow={copy.industriesEyebrow}
          title={copy.industriesTitle}
          subtitle={copy.industriesSubtitle}
        />

        <FeatureGrid features={industries} columns={2} />

        <div style={{textAlign: 'center', marginBottom: '2.5rem'}}>
          <Link
            to="/blog/suite-product-deep-dives-index"
            style={{color: 'var(--hs-accent-light)', fontWeight: 600, textDecoration: 'none'}}
          >
            Read all solution and product articles on the blog <span aria-hidden="true">{'\u2192'}</span>
          </Link>
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.solutionsHub} />

        <CTASection
          title={copy.ctaTitle}
          subtitle={copy.ctaSubtitle}
          primaryCta={{label: copy.contactSales, to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
