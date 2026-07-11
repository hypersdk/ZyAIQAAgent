// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {useState} from 'react';
import {
  ProductPage,
  PageHero,
  PageContent,
  StatGrid,
  SectionHeader,
  PillGroup,
  BentoGrid,
  SuiteProductFooter,
} from '../components/shared';
import {macSign} from '../data/platform-stats';
import {SuiteProductCapabilities} from '../components/SuiteProductCapabilities';
import {ProductConceptSections} from '../components/ProductConceptSections';
import {YouTubeEmbed} from '../components/YouTubeEmbed';
import RazorpayButton from '../components/RazorpayButton';

const VERSION = '1.1.0';
const GH_RELEASE = `https://github.com/hypersdk/zysign/releases/download/v${VERSION}`;
const DMG_URL = `${GH_RELEASE}/ZySign-${VERSION}.dmg`;
const DMG_SIZE = '89 MB';

function DownloadSection(): ReactNode {
  const [paymentId, setPaymentId] = useState('');
  const [licenceKey, setLicenceKey] = useState('');
  const [licenceEmail, setLicenceEmail] = useState('');
  const [invoiceUrl, setInvoiceUrl] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [copied, setCopied] = useState(false);

  function copyKey() {
    navigator.clipboard.writeText(licenceKey).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div id="pricing" style={{scrollMarginTop: '80px'}}>
      <SectionHeader
        eyebrow="Download & Pricing"
        title="Try Free · Buy When Ready"
        subtitle={`ZySign ${VERSION} for macOS 13 Ventura or later · Apple Silicon + Intel`}
      />

      {/* Two-column: Trial + Purchase */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        {/* Free trial card */}
        <div
          style={{
            padding: '2rem',
            borderRadius: '16px',
            border: '1px solid var(--hs-border)',
            background: 'var(--hs-surface)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          <div>
            <span
              style={{
                fontFamily: 'var(--hs-font-mono)',
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                color: 'var(--hs-text-muted)',
              }}
            >
              Free trial
            </span>
            <h3 style={{margin: '0.25rem 0 0', fontSize: '1.4rem'}}>30 Days — Free</h3>
            <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', margin: '0.5rem 0 0'}}>
              All features unlocked · No credit card · No login
            </p>
          </div>
          <ul
            style={{
              margin: 0,
              paddingLeft: '1.2rem',
              color: 'var(--hs-text-muted)',
              fontSize: '0.9rem',
              lineHeight: 1.7,
            }}
          >
            <li>PDF signing &amp; batch sign</li>
            <li>MCA21 V3 Web Bridge</li>
            <li>Audit trail &amp; filing calendar</li>
            <li>All 5 DSC token providers</li>
          </ul>
          <div style={{display: 'flex', flexDirection: 'column', gap: '0.6rem', marginTop: 'auto'}}>
            <a
              href={DMG_URL}
              style={{
                display: 'block',
                textAlign: 'center',
                padding: '12px 24px',
                background: 'transparent',
                color: 'var(--hs-text-heading)',
                border: '1px solid var(--hs-border)',
                borderRadius: '10px',
                fontWeight: 700,
                fontSize: '15px',
                textDecoration: 'none',
              }}
            >
              ↓ Download DMG — drag to Applications ({DMG_SIZE})
            </a>
          </div>
          <p style={{margin: 0, fontSize: '12px', color: 'var(--hs-text-subtle)', textAlign: 'center'}}>
            macOS 13 Ventura+ · Apple Silicon &amp; Intel · via GitHub Releases
          </p>
        </div>

        {/* Buy licence card */}
        <div
          style={{
            padding: '2rem',
            borderRadius: '16px',
            border: '2px solid var(--hs-accent)',
            background: 'var(--hs-surface)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            position: 'relative',
          }}
        >
          <span
            style={{
              position: 'absolute',
              top: '-12px',
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'var(--hs-accent)',
              color: '#fff',
              fontSize: '11px',
              fontWeight: 700,
              padding: '3px 14px',
              borderRadius: '20px',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              whiteSpace: 'nowrap',
            }}
          >
            Buy licence
          </span>
          <div>
            <span
              style={{
                fontFamily: 'var(--hs-font-mono)',
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                color: 'var(--hs-accent)',
              }}
            >
              1 year · per seat
            </span>
            <div style={{display: 'flex', alignItems: 'baseline', gap: '0.5rem', margin: '0.25rem 0 0'}}>
              <h3 style={{margin: 0, fontSize: '2rem'}}>₹500</h3>
              <span style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem'}}>+ 18% GST = ₹590</span>
            </div>
            <p style={{color: 'var(--hs-text-muted)', fontSize: '0.9rem', margin: '0.5rem 0 0'}}>
              Licence key shown instantly after payment · also emailed if you enter your address
            </p>
          </div>
          <ul
            style={{
              margin: 0,
              paddingLeft: '1.2rem',
              color: 'var(--hs-text-muted)',
              fontSize: '0.9rem',
              lineHeight: 1.7,
            }}
          >
            <li>1-year licence for one Mac</li>
            <li>All future {VERSION}.x updates</li>
            <li>Priority support on email</li>
            <li>Invoice with GST breakup</li>
          </ul>

          {licenceKey ? (
            <div
              style={{
                background: 'rgba(34,197,94,0.08)',
                border: '1px solid rgba(34,197,94,0.25)',
                borderRadius: '10px',
                padding: '1.25rem',
                marginTop: 'auto',
              }}
            >
              <p style={{margin: '0 0 0.5rem', fontWeight: 700, color: '#4ade80', fontSize: '0.95rem'}}>
                ✓ Payment successful — your licence key:
              </p>
              <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '0.5rem 0'}}>
                <code
                  style={{
                    flex: 1,
                    fontFamily: 'var(--hs-font-mono)',
                    fontSize: '1rem',
                    fontWeight: 700,
                    letterSpacing: '0.1em',
                    padding: '0.5rem 0.75rem',
                    background: 'var(--hs-surface-code, #101722)',
                    border: '1px solid rgba(34,197,94,0.25)',
                    borderRadius: '6px',
                    color: 'var(--hs-text-heading)',
                    userSelect: 'all',
                  }}
                >
                  {licenceKey}
                </code>
                <button
                  type="button"
                  onClick={copyKey}
                  style={{
                    padding: '0.5rem 0.75rem',
                    background: copied ? 'var(--ifm-color-success)' : 'var(--hs-accent)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: '0.8rem',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {copied ? '✓ Copied' : 'Copy'}
                </button>
              </div>
              <p style={{margin: '0.5rem 0 0', fontSize: '0.8rem', color: 'var(--hs-text-muted)'}}>
                Key also emailed to <strong>{licenceEmail}</strong>. Activate in ZySign → Settings → Licence using the
                exact same name &amp; email.
              </p>
              {invoiceUrl && (
                <a
                  href={invoiceUrl}
                  download
                  style={{
                    display: 'inline-block',
                    marginTop: '0.75rem',
                    padding: '0.5rem 1rem',
                    background: 'rgba(240,88,58,0.1)',
                    border: '1px solid rgba(240,88,58,0.3)',
                    borderRadius: '6px',
                    color: 'var(--hs-accent)',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    textDecoration: 'none',
                  }}
                >
                  ↓ Download GST Invoice (PDF)
                </a>
              )}
            </div>
          ) : (
            <>
              <div style={{display: 'flex', flexDirection: 'column', gap: '0.75rem'}}>
                <div>
                  <label
                    htmlFor="zysign-name"
                    style={{
                      display: 'block',
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      color: 'var(--hs-text-muted)',
                      marginBottom: '0.3rem',
                      letterSpacing: '0.03em',
                    }}
                  >
                    Full name <span style={{color: 'var(--hs-accent)'}}>*</span>{' '}
                    <span style={{fontWeight: 400, opacity: 0.6}}>(for licence &amp; GST receipt)</span>
                  </label>
                  <input
                    id="zysign-name"
                    type="text"
                    placeholder="e.g. Rajesh Kumar"
                    autoComplete="name"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.75rem',
                      borderRadius: '8px',
                      border: '1px solid var(--hs-border)',
                      backgroundColor: 'var(--hs-surface-code, #101722)',
                      color: 'var(--hs-text-heading)',
                      fontSize: '0.9rem',
                      outline: 'none',
                    }}
                  />
                </div>
                <div>
                  <label
                    htmlFor="zysign-email"
                    style={{
                      display: 'block',
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      color: 'var(--hs-text-muted)',
                      marginBottom: '0.3rem',
                      letterSpacing: '0.03em',
                    }}
                  >
                    Email <span style={{color: 'var(--hs-accent)'}}>*</span>{' '}
                    <span style={{fontWeight: 400, opacity: 0.6}}>(licence key &amp; GST receipt sent here)</span>
                  </label>
                  <input
                    id="zysign-email"
                    type="email"
                    placeholder="e.g. rajesh@example.com"
                    autoComplete="email"
                    value={customerEmail}
                    onChange={(e) => setCustomerEmail(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.75rem',
                      borderRadius: '8px',
                      border: '1px solid var(--hs-border)',
                      backgroundColor: 'var(--hs-surface-code, #101722)',
                      color: 'var(--hs-text-heading)',
                      fontSize: '0.9rem',
                      outline: 'none',
                    }}
                  />
                </div>
              </div>
              {(() => {
                const canPay = customerName.trim().length > 0 && customerEmail.trim().includes('@');
                return (
                  <RazorpayButton
                    amount={59000}
                    currency="INR"
                    productName="ZySign"
                    description="1-year licence key · macOS DSC Toolkit"
                    customerName={customerName}
                    customerEmail={customerEmail}
                    onSuccess={(pid, key, email, inv) => {
                      setPaymentId(pid);
                      setLicenceKey(key ?? '');
                      setLicenceEmail(email ?? customerEmail);
                      setInvoiceUrl(inv ?? '');
                    }}
                    style={{
                      display: 'block',
                      width: '100%',
                      padding: '13px 24px',
                      background: canPay ? 'var(--hs-accent)' : 'rgba(255,255,255,0.08)',
                      color: canPay ? '#fff' : 'var(--hs-text-muted)',
                      border: 'none',
                      borderRadius: '10px',
                      fontWeight: 700,
                      fontSize: '15px',
                      cursor: canPay ? 'pointer' : 'not-allowed',
                      pointerEvents: canPay ? 'auto' : 'none',
                      marginTop: 'auto',
                    }}
                  >
                    {canPay ? 'Pay ₹590 — Buy Licence Now' : 'Enter name & email to continue'}
                  </RazorpayButton>
                );
              })()}
            </>
          )}

          <p style={{margin: 0, fontSize: '12px', color: 'var(--hs-text-subtle)', textAlign: 'center'}}>
            Secure payment via Razorpay · UPI, cards, net banking
          </p>
        </div>
      </div>

      <BentoGrid
        items={[
          {
            title: 'Installs to /Applications',
            desc: `Double-click ZySign-${VERSION}.dmg and drag ZySign to Applications. macOS handles everything including the Python core.`,
            span: 'wide',
            accent: true,
          },
          {
            title: 'Licence key activation',
            desc: 'Open ZySign → Preferences → Licence. Paste your key and click Activate. Works offline.',
          },
          {
            title: 'Uninstall cleanly',
            desc: 'Drag ZySign.app to Trash. No leftover daemons or login items.',
          },
        ]}
      />
      <div style={{marginTop: '16px', textAlign: 'center'}}>
        <PillGroup
          items={[
            'macOS 13 Ventura+',
            'Apple Silicon · Intel',
            'No cloud dependency',
            'Allow in System Settings › Privacy if Gatekeeper warns',
          ]}
        />
      </div>
    </div>
  );
}

export default function ZySign(): ReactNode {
  return (
    <ProductPage
      themeId="zysign"
      title="ZySign — macOS DSC Toolkit for MCA21 V3"
      description="Replace the eMudhra emBridge daemon with a fully local, PKCS#11-based implementation. Sign MCA21 V3 eForms from your browser — no cloud, no black-box daemon."
    >
      <PageHero
        themeId="zysign"
        variant="split"
        eyebrow="Product"
        gradientWord="ZySign"
        title=""
        subtitle="macOS DSC Toolkit for MCA21 V3"
        description="Sign MCA21 eForms from your browser using any USB DSC token. PINs and keys never leave your machine."
        primaryCta={{label: 'Download Free Trial', to: DMG_URL}}
        secondaryCta={{label: 'Book a Demo', to: '/contact?intent=demo'}}
      />

      <PageContent>
        {/* Stats */}
        <StatGrid
          columns={4}
          stats={[
            {value: macSign.tokenProviders, label: 'Token Providers'},
            {value: macSign.components, label: 'Components'},
            {value: macSign.signingModes, label: 'Signing Modes'},
            {value: macSign.version, label: 'Version'},
          ]}
        />

        {/* Demo */}
        <SectionHeader
          eyebrow="See It in Action"
          title="ZySign Live Demo"
          subtitle="Watch ZySign replace the emBridge daemon and sign an MCA21 V3 eForm directly from Safari — no cloud, no daemon, no extensions."
        />
        <YouTubeEmbed videoId="MCwEc3q0iwA" title="ZySign — macOS DSC Toolkit for MCA21 V3 demo" priorityThumb />

        <ProductConceptSections productId="zysign" />

        {/* Token support */}
        <div style={{textAlign: 'center'}}>
          <SectionHeader
            eyebrow="DSC Tokens"
            title="5 PKCS#11 Providers — Every Indian DSC Token"
            subtitle="ZySign auto-detects your token on startup. Switch providers without restarting the bridge."
          />
          <PillGroup
            items={[
              'mToken CryptoID',
              'ePass 2003 (Feitian)',
              'ProxKey (WatchData)',
              'eMudhra USB token',
              'OpenSC (generic)',
            ]}
          />
        </div>

        {/* Security model */}
        <SectionHeader
          eyebrow="Security"
          title="Local by Design"
          subtitle="Every cryptographic operation runs on your machine. Nothing leaves."
        />

        <BentoGrid
          items={[
            {
              title: 'Keys stay in the token',
              desc: 'Private keys remain inside the hardware DSC token at all times. The PKCS#11 layer handles all signing operations on-device.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'PINs never logged',
              desc: 'PINs pass directly to PKCS#11 — never stored, logged, or sent over any network.',
            },
            {
              title: 'No cloud, no telemetry',
              desc: 'ZySign makes zero outbound calls. No analytics. No update checks. No third-party endpoints.',
            },
            {
              title: 'Audit-ready signatures',
              desc: 'Structured signing logs, certificate chain inspection, and immediate post-sign PDF verification for compliance programs.',
            },
          ]}
        />

        {/* DSC role locking */}
        <SectionHeader
          eyebrow="Filing Integrity"
          title="DSC Role Locking — Never Fail the “Same DSC” Check"
          subtitle="Bind each MCA role to one certificate thumbprint. ZySign blocks a mismatched token before you sign — so a filing never bounces back."
        />

        <BentoGrid
          items={[
            {
              title: 'Thumbprint-locked roles',
              desc: 'Save a SHA-256 certificate thumbprint per role — Director, Professional, or Authorized Representative. Every preflight compares the selected certificate against the saved lock and refuses to sign on mismatch.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Preflight before every sign',
              desc: 'A preflight check validates the certificate, the role lock, and the PDF signature fields before a single byte is signed — no wasted PIN entries.',
            },
            {
              title: 'Stops the portal rejection',
              desc: 'Prevents the MCA error “The same DSC key has not been used for signing as was used during filing” — the most common reason a form comes back.',
            },
            {
              title: 'Locks stored locally',
              desc: 'Per-role profiles live in a local profiles.json under Application Support. No cloud, survives restarts, managed from the app or the CLI (profile save / list / delete).',
            },
          ]}
        />

        {/* Certificate intelligence */}
        <SectionHeader
          eyebrow="Certificate Intelligence"
          title="Only the Right Certificate, Every Time"
          subtitle="A DSC token often carries encryption and expired certificates alongside the signing one. ZySign filters the list down to what you can actually file with."
        />

        <BentoGrid
          items={[
            {
              title: 'Signing-only KeyUsage filter',
              desc: 'Keeps certificates whose KeyUsage is digitalSignature or contentCommitment and drops encryption-only keys — so you can never accidentally pick the wrong certificate.',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Licensed CA validation',
              desc: 'Checks each certificate’s issuer against the roster of MCA-licensed Certifying Authorities before it is offered for signing.',
            },
            {
              title: 'Expiry drop',
              desc: 'Certificates past their notAfter date are removed from the list automatically — no more selecting a lapsed DSC by mistake.',
            },
            {
              title: 'PAN & identity extraction',
              desc: 'Pulls the PAN or holder identity straight from the certificate subject, plus RSA key size and serial, so you can confirm the right person is signing.',
            },
          ]}
        />
        <div style={{marginTop: '16px', textAlign: 'center'}}>
          <PillGroup
            items={[
              'eMudhra',
              'Capricorn',
              'PantaSign',
              'VSign',
              'IDSign',
              'XtraTrust',
              'NCode',
              'SafeScrypt',
              'CDSL',
              'NSDL',
              'CCA / RCAI',
            ]}
          />
        </div>

        {/* Beyond MCA — multi-portal */}
        <SectionHeader
          eyebrow="Beyond MCA"
          title="One Token, Every Government Portal"
          subtitle="The same USB DSC that files at MCA also approves GST, Income Tax, and Zoho Sign requests — through a single review-and-approve flow inside ZySign."
        />

        <BentoGrid
          items={[
            {
              title: 'GST & Income Tax emSigner',
              desc: 'Beyond the emSigner WebSocket on :1585, ZySign exposes an approval flow: the pending portal request surfaces in the app with its sign type and masked PAN, and you approve or reject it (/emsigner/pending · /emsigner/sign · /emsigner/cancel).',
              span: 'wide',
              accent: true,
            },
            {
              title: 'Zoho Sign USB DSC',
              desc: 'A dedicated /zoho/usb-sign endpoint signs Zoho Sign USB-token requests through the exact same PKCS#11 pipeline — one workflow for corporate and government signing.',
            },
            {
              title: 'PAN masked in transit',
              desc: 'REST responses mask the PAN to the first three and last character. The full value is only ever used in the reply sent straight back to the portal.',
            },
            {
              title: 'Native JSON API',
              desc: 'An unencrypted /embridge/v2/* API (status, getAllCertificate, sign) drives ZySign’s own desktop apps without the reverse-engineered envelope — plain JSON for tooling and tests.',
            },
          ]}
        />

        {/* Portal compatibility */}
        <div style={{textAlign: 'center'}}>
          <SectionHeader
            eyebrow="Compatibility"
            title="No Portal Changes Required"
            subtitle="ZySign presents the exact emBridge API the MCA portal JavaScript expects — TLS cert auto-trusted in the macOS Keychain."
          />
          <PillGroup
            items={[
              'MCA21 V3 eFiling portal',
              'No browser extension',
              'No portal modifications',
              'Self-signed cert auto-trusted',
              'PKCS#7 / CMS signatures',
              'PDF field signing',
            ]}
            variant="accent"
          />
        </div>

        {/* Download + Trial */}
        <DownloadSection />

        <SuiteProductCapabilities productId="zysign" />

        <SuiteProductFooter
          productId="zysign"
          ctaTitle="Ready to file without the emBridge daemon?"
          ctaSubtitle="ZySign gives chartered accountants, company secretaries, and compliance teams a transparent, privacy-respecting DSC signing stack on macOS."
          secondaryCta={{label: 'Read the Docs', to: '/docs/zysign'}}
        />
      </PageContent>
    </ProductPage>
  );
}
