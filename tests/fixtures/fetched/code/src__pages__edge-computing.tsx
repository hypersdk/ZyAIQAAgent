// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {
  ProductPage,
  PageContent,
  FeatureGrid,
  CTASection,
  RelatedBlogSection,
  StatGrid,
  SectionHeader,
  MarketingHero,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {licensingTco, cloudEconomics} from '../data/platform-stats';
import ScrollReveal from '../components/ScrollReveal';
import css from './edge-computing.module.css';

function IconLicense(props: {className?: string}) {
  return (
    <svg className={props.className} width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M8 10V8a4 4 0 118 0v2M6 10h12v10a1 1 0 01-1 1H7a1 1 0 01-1-1V10z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconCloud(props: {className?: string}) {
  return (
    <svg className={props.className} width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M6 16h12a3 3 0 002.4-4.8 3.5 3.5 0 00-6.55-.7A4 4 0 006 12a3.5 3.5 0 00-1 6.9"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconBuilding(props: {className?: string}) {
  return (
    <svg className={props.className} width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 21V8l8-4v17M4 13h8M9 9v.01M9 12v.01M9 15v.01M14 21V11h6v10M17 14h.01M17 17h.01M17 20h.01"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const edgeVsCloudTransfer = [
  {
    model: 'Cloud (direct egress)',
    upload: 'Free',
    download: '$0.08–$0.12',
    effective: 'High',
    latency: 'Medium',
    scale: 'High',
    useCase: 'Basic apps, low traffic',
    rowStyle: 'warn' as const,
  },
  {
    model: 'Cloud + edge (CDN)',
    upload: 'Free',
    download: '$0.02–$0.08',
    effective: 'Medium–low',
    latency: 'Low',
    scale: 'Very high',
    useCase: 'Web apps, APIs, media',
    rowStyle: 'neutral' as const,
  },
  {
    model: 'Edge-heavy (CDN-first)',
    upload: 'Free',
    download: '$0.01–$0.05',
    effective: 'Low',
    latency: 'Very low',
    scale: 'Very high',
    useCase: 'Streaming, global apps',
    rowStyle: 'neutral' as const,
  },
  {
    model: 'Edge + cache (hybrid)',
    upload: 'Free',
    download: '$0.01–$0.04',
    effective: 'Lowest practical',
    latency: 'Very low',
    scale: 'Very high',
    useCase: 'Large-scale platforms',
    rowStyle: 'best' as const,
  },
];

const trafficTierRows = [
  {level: '< 5 TB/month', choice: 'Cloud only'},
  {level: '5–50 TB/month', choice: 'Cloud + CDN'},
  {level: '50–500 TB/month', choice: 'Edge-heavy'},
  {level: '500 TB+', choice: 'Edge + hybrid'},
];

const whyEdgeItems = [
  {
    title: 'Cuts origin egress',
    body: 'The largest lever when bytes leave your cloud billable perimeter.',
  },
  {
    title: 'Caches closer to users',
    body: 'Lower latency for web, APIs, and media worldwide (including India-heavy traffic).',
  },
  {
    title: 'Absorbs spikes',
    body: 'Less thundering herd against core regions and databases.',
  },
  {
    title: 'Better global performance',
    body: 'One POP mesh instead of every request round-tripping to a single region.',
  },
];

function EdgeTopologyDiagram(): ReactNode {
  return (
    <div className={css.topology} aria-label="Retail edge deployment topology">
      <div className={css.topologyHq}>
        <div className={css.topologyHqLabel}>Central HQ</div>
        <div className={css.topologyHqTitle}>HyperSDK Platform control plane</div>
        <div className={css.topologyPills}>
          <span className={`${css.topologyPill} ${css.topologyPillAccent}`}>REST API</span>
          <span className={css.topologyPill}>Web dashboard</span>
          <span className={css.topologyPill}>Job scheduler</span>
        </div>
      </div>
      <div className={css.topologyLink}>
        <span className={css.topologyLinkPulse} aria-hidden />
        Encrypted WAN
      </div>
      <div className={css.topologyStores}>
        {[
          {name: 'Store 1', spec: '2 vCPU · 4 GB RAM'},
          {name: 'Store 2', spec: '2 vCPU · 4 GB RAM'},
          {name: 'Store N', spec: '500+ sites'},
        ].map((s) => (
          <div key={s.name} className={css.topologyStore}>
            <div className={css.topologyStoreName}>{s.name}</div>
            <div className={css.topologyStoreSpec}>{s.spec}</div>
            <span className={css.topologyStoreBadge}>KVM + sync</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function EdgeComputing(): ReactNode {
  return (
    <ProductPage
      title="Edge Computing Migration"
      description="Migrate VMs to edge locations. Small footprint, offline capable, centrally managed."
    >
      <MarketingHero pageId="edge-computing" />

      <PageContent>
        <div className={css.mesh}>
          <div className={css.pillRow}>
            <span className={`${css.pill} ${css.pillAccent}`}>KVM @ edge</span>
            <span className={css.pill}>Declarative YAML</span>
            <span className={css.pill}>Delta block sync</span>
            <span className={css.pill}>Job queue + replay</span>
          </div>

          <ScrollReveal>
            <div className={css.statsBand}>
              <div className={css.statsBandInner}>
                <StatGrid
                  stats={[
                    {value: '2 cores', label: 'Minimum CPU'},
                    {value: '4 GB', label: 'Minimum RAM'},
                    {value: 'Full', label: 'Offline capable'},
                    {value: '500+', label: 'Sites managed'},
                  ]}
                />
              </div>
            </div>
          </ScrollReveal>

          <SectionHeader
            eyebrow="Economics"
            title="Cheaper Than Always-On Cloud for Steady Workloads"
            subtitle={`VMware-style stacks still cost ${licensingTco.vmwarePerVmYearRange} per VM per year in typical license plus support—about ${licensingTco.vmware100VmYearLabel} annually at 100 VMs. Tier-1 cloud adds multi-AZ, egress, and managed premiums on every 24/7 VM. Edge and on-premises clusters trade that metered mark-up for amortized hardware you control, which is why modeled TCOs land ${cloudEconomics.steadyStateVsPublicCloudRunRate} leaner than equivalent public-cloud footprints for analytics, branch apps, and warehouse-style data.`}
          />

          <ScrollReveal delay={80}>
            <div className={css.economicsGrid}>
              <div className={css.econCard}>
                <div className={css.econIcon}>
                  <IconLicense />
                </div>
                <h3 className={css.econTitle}>VMware-style licensing</h3>
                <p className={css.econDesc}>
                  Typical enterprise stacks land at {licensingTco.vmwarePerVmYearRange} per VM per year in license and
                  support alone — about {licensingTco.vmware100VmYearLabel} annually at 100 VMs before hardware or
                  migration services.
                </p>
              </div>
              <div className={css.econCard}>
                <div className={css.econIcon}>
                  <IconCloud />
                </div>
                <h3 className={css.econTitle}>Public cloud meter</h3>
                <p className={css.econDesc}>
                  Multi-AZ networking, managed premiums, and egress turn steady 24/7 VMs into runaway OpEx. Customers
                  have removed {cloudEconomics.customerFirstYearCloudSavings} in first-year cloud spend after
                  consolidating fragmented tooling.
                </p>
              </div>
              <div className={css.econCard}>
                <div className={css.econIcon}>
                  <IconBuilding />
                </div>
                <h3 className={css.econTitle}>Owned edge & data halls</h3>
                <p className={css.econDesc}>
                  Swap metered mark-up for amortized capacity you control. Modeled TCOs for steady workloads land{' '}
                  {cloudEconomics.steadyStateVsPublicCloudRunRate} leaner than identical always-on public-cloud quotes;
                  one edge program cut infrastructure spend {cloudEconomics.edgeCaseStudyInfraReduction}.
                </p>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={100}>
            <section className={css.transferShell} aria-labelledby="edge-transfer-title">
              <div className={css.transferHead}>
                <p className={css.transferEyebrow}>Data transfer economics</p>
                <h2 id="edge-transfer-title" className={css.transferTitle}>
                  Edge vs cloud egress
                </h2>
                <p className={css.transferLead}>
                  Illustrative per-GB download pricing bands; origin egress drops when responses are served from edge
                  caches and CDNs instead of hitting your cloud object store or app tier directly.
                </p>
              </div>
              <div className={css.transferBody}>
                <div className={css.transferScroll}>
                  <div className={css.transferHeader} aria-hidden>
                    <span>Model</span>
                    <span>Upload</span>
                    <span>Download</span>
                    <span>Effective $/GB</span>
                    <span>Latency</span>
                    <span>Scale</span>
                    <span>Best fit</span>
                  </div>
                  {edgeVsCloudTransfer.map((row) => (
                    <div key={row.model} className={css.transferRow} data-style={row.rowStyle}>
                      <div className={css.transferModel}>{row.model}</div>
                      <div className={css.transferGrid}>
                        <div className={css.transferCell} data-label="Upload">
                          {row.upload}
                        </div>
                        <div className={css.transferCell} data-label="Download" data-tone="money">
                          {row.download}
                        </div>
                        <div className={css.transferCell} data-label="Effective $/GB">
                          {row.effective}
                        </div>
                        <div className={css.transferCell} data-label="Latency">
                          {row.latency}
                        </div>
                        <div className={css.transferCell} data-label="Scale">
                          {row.scale}
                        </div>
                        <div className={css.transferCell} data-label="Best fit">
                          {row.useCase}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className={css.whyBlock}>
                  <h3 className={css.whyTitle}>Why edge wins</h3>
                  <div className={css.whyGrid}>
                    {whyEdgeItems.map((w) => (
                      <div key={w.title} className={css.whyItem}>
                        <span className={css.whyCheck} aria-hidden>
                          ✓
                        </span>
                        <div>
                          <strong>{w.title}</strong>
                          <span>{w.body}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className={css.trafficBlock}>
                  <h3 className={css.trafficTitle}>Traffic level rule-of-thumb</h3>
                  <div className={css.trafficBar} aria-hidden />
                  <div className={css.trafficRows}>
                    {trafficTierRows.map((tr) => (
                      <div key={tr.level} className={css.trafficRow}>
                        <span className={css.trafficVol}>{tr.level}</span>
                        <span className={css.trafficChoice}>{tr.choice}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <blockquote className={css.pullQuote}>
                  Edge is not only a latency story — with effective caching, it can{' '}
                  <strong>shrink cloud egress spend on the order of 50–90%</strong> versus serving the same audience
                  straight from origin.
                </blockquote>
              </div>
            </section>
          </ScrollReveal>

          <FeatureGrid
            columns={2}
            features={[
              {
                title: 'Small Footprint',
                desc: 'Runs on minimal hardware. No vCenter, no management cluster, no SAN. A single binary and a KVM host are all you need.',
              },
              {
                title: 'Offline Capable',
                desc: 'Queues migration jobs locally, syncs when connectivity returns. Never loses state during network partitions.',
              },
              {
                title: 'Declarative Manifests',
                desc: 'Define edge site deployments in YAML. Ship a USB drive with the manifest and images to deploy automatically.',
              },
              {
                title: 'Centralized Management',
                desc: 'Manage hundreds of edge sites from a single control plane. Monitor health and resource utilization across all locations.',
              },
            ]}
          />

          <div className={css.sectionSpaced}>
            <SectionHeader
              eyebrow="Deployment Scenario"
              title="Retail Chain: 500 Stores, One Dashboard"
              subtitle="A national retailer deploys edge nodes to every store location. Each node runs independently during outages and syncs back when connectivity is restored."
            />
          </div>

          <ScrollReveal delay={60}>
            <EdgeTopologyDiagram />
          </ScrollReveal>

          <FeatureGrid
            columns={2}
            features={[
              {
                title: 'Central HQ',
                desc: 'HyperSDK Platform dashboard manages all 500+ locations from a single pane. Push VM images, schedule updates, and monitor health in real time.',
              },
              {
                title: 'Store Nodes',
                desc: 'Each store runs a 2-core, 4GB edge node with KVM. Point-of-sale, inventory, and local services run as VMs with sub-second failover.',
              },
              {
                title: 'Offline Operation',
                desc: 'Stores operate independently during internet outages. Local job queue preserves all operations and replays them when connectivity returns.',
              },
              {
                title: 'Incremental Sync',
                desc: 'Only changed blocks are transferred during sync windows. Stores resume full operation within minutes of reconnecting.',
              },
            ]}
          />

          <SectionHeader
            eyebrow="Bandwidth"
            title="Bandwidth Optimization"
            subtitle="Edge deployments cannot afford to transfer full disk images over limited WAN links. HyperSDK Platform minimizes bandwidth at every step."
          />

          <FeatureGrid
            columns={3}
            features={[
              {
                title: 'Delta Sync',
                desc: 'Only changed blocks are transferred between central and edge. After the initial deployment, updates are measured in megabytes, not gigabytes.',
              },
              {
                title: 'Compression',
                desc: '60-80% bandwidth reduction using qcow2 compression and deduplication. A 40GB VM image transfers as 8-16GB over the wire.',
              },
              {
                title: 'Off-Peak Scheduling',
                desc: 'Transfers are scheduled during off-peak hours automatically. Business-critical bandwidth is never consumed by image sync operations.',
              },
            ]}
          />

          <RelatedBlogSection links={solutionPageBlogLinks.edgeComputing} />

          <CTASection
            title="Discuss Edge Deployment"
            subtitle="Our edge specialists will assess your site requirements and design a migration plan for your distributed infrastructure."
            primaryCta={{label: 'Discuss Edge Deployment', to: '/contact?intent=edge'}}
            secondaryCta={{label: 'Contact Sales', to: '/contact?intent=edge'}}
          />
        </div>
      </PageContent>
    </ProductPage>
  );
}
