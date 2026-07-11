// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {
  ProductPage,
  PageHero,
  PageContent,
  StatGrid,
  SectionHeader,
  BentoGrid,
  RelatedBlogSection,
  IntegrationDiagram,
  styles,
  SuiteProductFooter,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import {ClientPresentationSection} from '../components/ClientPresentationSection';
import {aether, ragnarok} from '../data/platform-stats';

export default function ConfidentialComputing(): ReactNode {
  return (
    <ProductPage
      themeId="aether"
      productId="confidential-fabric"
      title="Confidential Computing — SEV-SNP & TDX on KubeVirt"
      description="Hardware-rooted trust for regulated workloads. Aether deploys confidential VMs and Kata pods; Ragnarok attests fleets, gates secrets, and enforces trust policies."
    >
      <PageHero
        themeId="aether"
        variant="split"
        eyebrow="Solution"
        gradientWord="Confidential"
        title="Computing Fabric"
        subtitle="SEV-SNP and TDX on KubeVirt — attest, migrate, and operate TEE fleets without a separate toolchain."
        description="Declare a confidential block once in YAML. Aether wires KubeVirt launch security, Kata RuntimeClasses, measured images, and sovereign mode. Composite with Ragnarok for fleet attestation, trust scores, and attest-gated secrets."
        primaryCta={{label: 'Read the guide', to: '/docs/confidential-fabric'}}
        secondaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
      />

      <PageContent>
        <StatGrid
          stats={[
            {value: String(aether.confidentialTees), label: 'TEE types (SNP + TDX)'},
            {value: String(aether.securityProfiles), label: 'Security profiles'},
            {value: String(aether.migrationPaths), label: 'Migration paths'},
            {value: ragnarok.apiRoutes, label: 'Ragnarok API routes'},
          ]}
          columns={4}
        />

        <SectionHeader
          eyebrow="Composite architecture"
          title="Aether deploys. Ragnarok attests."
          subtitle="Run both control planes side-by-side — same confidential workload schema, shared TEE inventory, and re-attestation before every cutover."
        />
        <BentoGrid
          items={[
            {
              title: 'One confidential: block',
              desc: 'SEV-SNP or TDX, vTPM, measured images, and strict attestation gates in a single workload spec — no parallel YAML dialects.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'KubeVirt + Kata on TEE nodes',
              desc: 'Confidential VMs and CoCo pods (kata-clh-snp, kata-clh-tdx) on the same labeled cluster nodes.',
            },
            {
              title: 'Sovereign mode',
              desc: 'BYOK signing, offline attestation bundles, and region lock for air-gapped and regulated estates.',
            },
            {
              title: 'Fleet trust hub',
              desc: 'Ragnarok surfaces TEE inventory, trust scores, quarantine, and attest-gated secrets on `/confidential` dashboard views.',
            },
          ]}
        />

        <ProductConceptSections productId="aether" />

        <SuiteProductCapabilities productId="confidential-computing" />

        <SectionHeader
          eyebrow="Integration"
          title="Where confidential fits in the suite"
          subtitle="Prep TEE nodes with HyperCluster, migrate disks with HyperSDK Platform, deploy with Aether, and operate fleets with Ragnarok and Zeus OS."
        />
        <IntegrationDiagram
          content={`HyperCluster → label TEE nodes (Kata/SPIRE)
HyperSDK Platform + hyper2kvm → measured qcow2 artifacts
Aether → confidential VMs, Kata pods, confidential-blue-green migration
Ragnarok → attestation hub, trust enforce, attest-gated secrets
PacketWolf → verify annotations on east-west traffic`}
        />

        <div style={{justifyContent: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem', display: 'flex'}}>
          <Link className={styles.secondaryBtn} to="/aether">
            Aether product page
          </Link>
          <Link className={styles.secondaryBtn} to="/ragnarok">
            Ragnarok product page
          </Link>
          <Link className={styles.primaryBtn} to="/docs/confidential-fabric">
            Confidential fabric docs
          </Link>
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.confidentialComputing} />

        <ClientPresentationSection productId="aether" />
        <ClientPresentationSection productId="ragnarok" />

        <SuiteProductFooter
          productId="aether"
          ctaTitle="Ready for confidential and sovereign workloads?"
          ctaSubtitle="Walk through attestation gates, measured images, and composite Aether + Ragnarok deployment with our team."
          secondaryCta={{label: 'Ragnarok product page', to: '/ragnarok'}}
        />
      </PageContent>
    </ProductPage>
  );
}
