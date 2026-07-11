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
import {platform} from '../data/platform-stats';

const distroFamilies = [
  {
    family: 'Enterprise Linux',
    distros: [
      'RHEL 7/8/9',
      'CentOS 7/Stream 8/9',
      'Fedora 38-41',
      'Rocky Linux 8/9',
      'AlmaLinux 8/9',
      'Oracle Linux 7/8/9',
    ],
  },
  {family: 'Debian', distros: ['Ubuntu 20.04/22.04/24.04', 'Debian 10/11/12', 'Linux Mint 21/22', 'Pop!_OS 22.04']},
  {family: 'SUSE', distros: ['SLES 12/15', 'openSUSE Leap 15.x', 'openSUSE Tumbleweed']},
  {
    family: 'Other',
    distros: ['Arch Linux', 'VMware Photon OS 3/4/5', 'Amazon Linux 2/2023', 'Alpine Linux 3.x', 'Gentoo'],
  },
];

export default function LinuxMigration(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const landing = getMigrationLanding('linux-migration', i18n.currentLocale);
  return (
    <ProductPage title="Linux VM Migration" description="Migrate 25+ Linux distributions to KVM automatically.">
      <MigrationMarketingHero landingId="linux-migration" />

      <PageContent>
        <MigrationTrustStrip config={landing} />
        <StatGrid
          stats={[
            {value: '25+', label: 'Distributions Supported'},
            {value: '< 3min', label: 'Average Conversion Time'},
            {value: platform.firstBootSuccess, label: 'First-Boot Success Rate'},
            {value: '0', label: 'Manual Steps Required'},
          ]}
        />

        <SectionHeader
          eyebrow="Distributions"
          title="Comprehensive Distribution Coverage"
          subtitle="From enterprise RHEL to lightweight Alpine, we detect the distribution and apply the correct migration pipeline automatically."
        />
        {/* Custom distro family grid - unique layout not covered by FeatureGrid */}
        <div className={`${styles.featureGrid} ${styles.gridCol4}`} style={{marginBottom: 0}}>
          {distroFamilies.map((fam) => (
            <div key={fam.family} className={styles.featureCard}>
              <h3 className={styles.monoLabel} style={{color: 'var(--hs-accent-light)'}}>
                {fam.family}
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
                {fam.distros.map((d) => (
                  <li
                    key={d}
                    style={{
                      color: 'var(--hs-text-body)',
                      fontSize: '0.85rem',
                      paddingLeft: '1.25rem',
                      position: 'relative',
                    }}
                  >
                    <span style={{position: 'absolute', left: 0, color: 'var(--hs-accent)', fontWeight: 700}}>
                      {'\u2713'}
                    </span>
                    {d}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Kernel Handling */}
        <SectionHeader
          eyebrow="Kernel"
          title="Kernel Handling"
          subtitle="The kernel is the most critical part of any Linux migration. HyperSDK Platform handles kernel compatibility automatically across all supported distributions."
        />
        <FeatureGrid
          columns={3}
          features={[
            {
              title: 'Auto-Detection',
              desc: 'Kernel version, loaded modules, and boot parameters are detected automatically from the source VM. No manual inspection or configuration required.',
            },
            {
              title: 'Module Injection',
              desc: 'VirtIO modules (virtio_blk, virtio_net, virtio_scsi) are added to the initramfs for all kernel versions, ensuring the VM boots on KVM without driver issues.',
            },
            {
              title: 'Custom Kernels',
              desc: 'Handles custom-compiled kernels with full module dependency resolution. Even non-standard kernel builds get the correct VirtIO modules injected into their initramfs.',
            },
          ]}
        />

        <RelatedBlogSection links={solutionPageBlogLinks.linuxMigration} />

        <CTASection
          title="Start Your Linux Migration"
          subtitle="Our engineers will inventory your Linux VMs and execute a pilot migration within days -- not weeks."
          primaryCta={{label: 'Start Your Linux Migration', to: '/contact?intent=linux'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=linux'}}
        />
      </PageContent>
    </ProductPage>
  );
}
