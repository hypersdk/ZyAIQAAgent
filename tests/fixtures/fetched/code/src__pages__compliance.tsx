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
  StatGrid,
  SectionHeader,
  FeatureGrid,
  CTASection,
  RelatedBlogSection,
  IntegrationDiagram,
  styles,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';
import {getCompliancePageCopy} from '../data/compliance-locale';

const complianceRows: {
  standard: string;
  status: string;
  statusColor: string;
  details: string;
  docLink?: string;
}[] = [
  {
    standard: 'SOC 2 Type II',
    status: 'Ready',
    statusColor: '#10b981',
    details: 'Access controls, audit logging, change management, incident response procedures',
  },
  {
    standard: 'HIPAA',
    status: 'Ready',
    statusColor: '#10b981',
    details: 'PHI encryption at rest and in transit, access logging, BAA available on request',
  },
  {
    standard: 'FedRAMP',
    status: 'In Progress',
    statusColor: '#f59e0b',
    details: 'FIPS 140-2 validated encryption, NIST 800-53 security controls, continuous monitoring',
  },
  {
    standard: 'ISO 27001',
    status: 'Ready',
    statusColor: '#10b981',
    details: 'ISMS framework, risk assessment methodology, continuous monitoring and improvement',
  },
  {
    standard: 'GDPR',
    status: 'Compliant',
    statusColor: '#10b981',
    details: 'Data minimization, right to erasure, data processing agreements (DPA) available',
  },
  {
    standard: 'Hardware attestation (TEE)',
    status: 'Enterprise',
    statusColor: '#818cf8',
    details:
      'SEV-SNP/TDX measured images, attestation gates, and sovereign mode via Aether + Ragnarok — see confidential fabric guide',
    docLink: '/docs/confidential-fabric',
  },
  {
    standard: 'PCI DSS',
    status: 'Ready',
    statusColor: '#10b981',
    details: 'Network segmentation, AES-256 encryption, access controls, audit trails',
  },
];

const auditLogExample = `{
  "timestamp": "2026-04-12T10:30:00Z",
  "action": "vm.export",
  "user": "admin@company.com",
  "source_ip": "10.0.1.50",
  "resource": "web-server-01",
  "provider": "vsphere",
  "result": "success",
  "duration_ms": 45200,
  "details": {
    "format": "ova",
    "size_bytes": 12884901888,
    "destination": "/exports/web-server-01.ova"
  }
}`;

export default function Compliance(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const copy = getCompliancePageCopy(i18n.currentLocale);

  return (
    <ProductPage
      title="Compliance & Audit Trail"
      description="SOC 2, HIPAA, FedRAMP, PCI DSS ready. Complete audit logging, encryption, and RBAC for regulated industries."
    >
      <MarketingHero pageId="compliance" />

      <PageContent>
        {/* Certifications at a Glance */}
        <StatGrid
          stats={[
            {value: 'SOC 2', label: 'Type II Ready'},
            {value: 'HIPAA', label: 'BAA-Ready Architecture'},
            {value: 'FedRAMP', label: 'FIPS 140-2 Compatible'},
            {value: 'PCI DSS', label: 'v4.0 Compliant'},
          ]}
          columns={4}
        />

        {/* Security Features */}
        <SectionHeader eyebrow={copy.securityEyebrow} title={copy.securityTitle} subtitle={copy.securitySubtitle} />
        <FeatureGrid
          features={[
            {
              title: 'RBAC & Authentication',
              desc: 'PAM-integrated authentication with JWT session tokens. Four built-in roles (Admin, Operator, Viewer, Auditor) enforce least-privilege access across all API endpoints and dashboard views.',
            },
            {
              title: 'Encryption',
              desc: 'TLS 1.3 for all data in transit. AES-256 encryption at rest for stored disk images and configuration. Full LUKS volume support for encrypted VM migrations.',
            },
            {
              title: 'Audit Logging',
              desc: 'Structured JSON audit log captures every API call, login attempt, and configuration change. Append-only, cryptographically signed entries create a tamper-proof audit trail.',
            },
            {
              title: 'Rate Limiting',
              desc: '100 requests per minute default with configurable per-user and per-endpoint limits. Automatic throttling prevents abuse while ensuring legitimate operations complete.',
            },
            {
              title: 'Secrets Management',
              desc: 'Encrypted credential storage for cloud provider keys, vCenter passwords, and API tokens. Environment variable injection at runtime. No plaintext secrets on disk or in logs.',
            },
            {
              title: 'Network Security',
              desc: 'Content Security Policy (CSP) headers, strict CORS policies, HSTS enforcement, X-Frame-Options protection, and automatic TLS certificate provisioning with ECDSA P-256.',
            },
            {
              title: 'Hardware attestation (TEE)',
              desc: 'Enterprise confidential fabric on SEV-SNP/TDX — measured images, attestation gates, and sovereign mode via Aether + Ragnarok. See the confidential fabric guide for architecture details.',
            },
          ]}
          columns={2}
        />

        {/* Compliance Readiness Matrix */}
        <SectionHeader eyebrow={copy.matrixEyebrow} title={copy.matrixTitle} subtitle={copy.matrixSubtitle} />
        <div style={{overflowX: 'auto', margin: '0 auto 5rem', maxWidth: 950}}>
          <table
            className={styles.featureCard}
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              textAlign: 'left',
            }}
          >
            <thead>
              <tr style={{borderBottom: '2px solid var(--ifm-color-emphasis-300)'}}>
                <th style={{padding: '1rem', minWidth: 130}}>{copy.colStandard}</th>
                <th style={{padding: '1rem', minWidth: 110}}>{copy.colStatus}</th>
                <th style={{padding: '1rem'}}>{copy.colDetails}</th>
              </tr>
            </thead>
            <tbody>
              {complianceRows.map((row, i) => (
                <tr
                  key={row.standard}
                  style={{
                    borderBottom: i < complianceRows.length - 1 ? '1px solid var(--ifm-color-emphasis-200)' : undefined,
                  }}
                >
                  <td style={{padding: '1rem', fontWeight: 600, color: 'var(--hs-text-heading)'}}>{row.standard}</td>
                  <td style={{padding: '1rem'}}>
                    <span
                      style={{
                        background: `${row.statusColor}18`,
                        color: row.statusColor,
                        padding: '0.25rem 0.75rem',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {row.status}
                    </span>
                  </td>
                  <td style={{padding: '1rem', color: 'var(--hs-text-muted)', fontSize: '0.9rem', lineHeight: 1.6}}>
                    {row.details}
                    {row.docLink && (
                      <>
                        {' '}
                        <Link to={row.docLink} style={{color: 'var(--hs-accent-light)', fontWeight: 600}}>
                          Learn more →
                        </Link>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Audit Log Example */}
        <SectionHeader eyebrow={copy.auditEyebrow} title={copy.auditTitle} subtitle={copy.auditSubtitle} />
        <IntegrationDiagram content={auditLogExample} />
        <div style={{height: '3rem'}} />

        {/* Data Protection */}
        <SectionHeader eyebrow={copy.dataEyebrow} title={copy.dataTitle} subtitle={copy.dataSubtitle} />
        <FeatureGrid
          features={[
            {
              title: 'Data at Rest',
              desc: 'AES-256-GCM encryption for all stored disk images, snapshots, and configuration files. Supports customer-managed encryption keys (CMEK) for full key ownership.',
            },
            {
              title: 'Data in Transit',
              desc: 'TLS 1.3 with strong cipher suites for all API communication. mTLS available for service-to-service authentication in multi-node deployments.',
            },
            {
              title: 'Key Management',
              desc: 'Automatic key rotation with configurable intervals. Integration with external KMS providers (HashiCorp Vault, AWS KMS). Hardware security module (HSM) support for Enterprise tier.',
            },
            {
              title: 'Data Retention',
              desc: 'Configurable retention policies for audit logs, migration artifacts, and temporary files. Automatic secure deletion with cryptographic erasure verification.',
            },
          ]}
          columns={2}
        />

        <p className={styles.featureCardDesc} style={{textAlign: 'center', maxWidth: '36rem', margin: '0 auto 3rem'}}>
          Software licensing and data-processing terms: <Link to="/docs/licensing">Licensing overview</Link> ·{' '}
          <Link to="/privacy">Privacy Policy</Link>
        </p>

        <RelatedBlogSection links={solutionPageBlogLinks.compliance} />

        {/* CTA */}
        <CTASection
          title={copy.ctaTitle}
          subtitle={copy.ctaSubtitle}
          primaryCta={{label: copy.securityDatasheet, to: '/contact?intent=compliance'}}
          secondaryCta={{label: copy.scheduleReview, to: '/contact?intent=compliance'}}
        />
      </PageContent>
    </ProductPage>
  );
}
