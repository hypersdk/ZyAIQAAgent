// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {useState, useEffect} from 'react';
import Link from '@docusaurus/Link';
import {ProductPage, PageContent, styles, MarketingHero} from '../components/shared';

const STORAGE_KEY = 'hypersdk-checklist-v2';

interface ChecklistSection {
  title: string;
  description: string;
  items: string[];
}

const sections: ChecklistSection[] = [
  {
    title: 'Pre-Migration',
    description: 'Complete these steps before starting any migration work.',
    items: [
      'Inventory all VMs (OS, size, dependencies)',
      'Assess migration readiness (run HyperSDK Platform readiness check)',
      'Document network topology and firewall rules',
      'Backup all VMs and verify restore capability',
      'Plan rollback procedure',
      'Schedule maintenance window',
    ],
  },
  {
    title: 'During Migration',
    description: 'Execute these steps during your migration window.',
    items: [
      'Export VMs from source hypervisor',
      'Convert disk formats (VMDK \u2192 QCOW2)',
      'Apply offline fixes (fstab, initramfs, GRUB)',
      'Deploy to target (libvirt/KubeVirt)',
      'Verify boot and network connectivity',
    ],
  },
  {
    title: 'Post-Migration',
    description: 'Validate and finalize after migration is complete.',
    items: [
      'Validate all services are running',
      'Test network connectivity and DNS',
      'Monitor performance for 48 hours',
      'Update documentation and CMDB',
      'Decommission source VMs after verification period',
    ],
  },
];

const totalItems = sections.reduce((acc, s) => acc + s.items.length, 0);

const relatedResources = [
  {
    title: 'ROI Calculator',
    desc: 'Estimate your projected savings from migrating off VMware with our interactive calculator.',
    link: '/roi',
  },
  {
    title: 'VMware Exit Guide',
    desc: '48-page whitepaper on how Fortune 500 companies saved $1.2M/year migrating to KVM.',
    link: '/whitepaper',
  },
  {
    title: 'Assessment Quiz',
    desc: 'Take our 2-minute quiz to evaluate your migration readiness and get a personalized report.',
    link: '/assessment',
  },
];

export default function Checklist(): ReactNode {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({name: '', email: '', company: ''});
  const [checked, setChecked] = useState<boolean[]>(() => new Array(totalItems).fill(false));

  // Load saved state on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length === totalItems) {
          setChecked(parsed);
        }
      }
    } catch (e) {
      console.warn('localStorage error:', e);
    }
  }, []);

  // Persist state on change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(checked));
    } catch (e) {
      console.warn('localStorage error:', e);
    }
  }, [checked]);

  const toggleItem = (globalIndex: number) => {
    setChecked((prev) => {
      const next = [...prev];
      next[globalIndex] = !next[globalIndex];
      return next;
    });
  };

  const completedCount = checked.filter(Boolean).length;
  const percentComplete = Math.round((completedCount / totalItems) * 100);
  const showDownloadCta = percentComplete > 50;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  // Build a flat index offset for each section
  let globalOffset = 0;

  return (
    <ProductPage
      title="Download: The VM Migration Checklist"
      description="Download the VM Migration Checklist. Everything your team needs before, during, and after migration."
    >
      <MarketingHero pageId="checklist" />

      <PageContent>
        {/* Progress Bar */}
        <div style={{marginBottom: '2.5rem'}}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '0.75rem',
            }}
          >
            <span
              style={{
                color: 'var(--hs-text-body)',
                fontSize: '0.95rem',
                fontWeight: 600,
              }}
            >
              {completedCount} of {totalItems} completed ({percentComplete}%)
            </span>
            {showDownloadCta && (
              <Link
                className={styles.primaryBtn}
                to="/contact?intent=assessment"
                style={{
                  padding: '0.5rem 1.5rem',
                  fontSize: '0.85rem',
                }}
              >
                Get a Migration Assessment
              </Link>
            )}
          </div>
          <div
            style={{
              width: '100%',
              height: 10,
              background: 'rgba(255, 255, 255, 0.08)',
              borderRadius: 5,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${percentComplete}%`,
                height: '100%',
                background:
                  percentComplete === 100
                    ? 'linear-gradient(90deg, #10b981, #34d399)'
                    : 'linear-gradient(90deg, #f0583a, #ff8c00)',
                borderRadius: 5,
                transition: 'width 0.3s ease, background 0.3s ease',
              }}
            />
          </div>
          {percentComplete === 100 && (
            <p
              style={{
                color: '#10b981',
                fontSize: '0.9rem',
                fontWeight: 600,
                marginTop: '0.5rem',
                textAlign: 'center',
              }}
            >
              All items complete -- you are ready to migrate!
            </p>
          )}
        </div>

        <div
          className={styles.splitGrid}
          style={{
            marginBottom: '5rem',
          }}
        >
          {/* Interactive Checklist Sections */}
          <div>
            {sections.map((section) => {
              const sectionStart = globalOffset;
              const sectionItems = section.items.map((item, i) => ({
                item,
                globalIndex: sectionStart + i,
              }));
              globalOffset += section.items.length;

              const sectionChecked = sectionItems.filter((si) => checked[si.globalIndex]).length;
              const sectionTotal = sectionItems.length;
              const sectionPercent = Math.round((sectionChecked / sectionTotal) * 100);

              return (
                <div key={section.title} style={{marginBottom: '2rem'}}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '0.75rem',
                    }}
                  >
                    <h2
                      style={{
                        fontSize: '1.3rem',
                        fontWeight: 700,
                        color: 'var(--hs-text-heading)',
                        margin: 0,
                      }}
                    >
                      {section.title}
                    </h2>
                    <span
                      style={{
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color: sectionPercent === 100 ? '#10b981' : 'var(--hs-text-muted)',
                        background: sectionPercent === 100 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                        padding: '0.25rem 0.75rem',
                        borderRadius: 20,
                        border: `1px solid ${sectionPercent === 100 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                      }}
                    >
                      {sectionChecked}/{sectionTotal}
                    </span>
                  </div>
                  <p
                    style={{
                      color: 'var(--hs-text-muted)',
                      fontSize: '0.85rem',
                      marginBottom: '0.75rem',
                      lineHeight: 1.5,
                    }}
                  >
                    {section.description}
                  </p>

                  {/* Section progress */}
                  <div
                    style={{
                      width: '100%',
                      height: 4,
                      background: 'rgba(255, 255, 255, 0.06)',
                      borderRadius: 2,
                      overflow: 'hidden',
                      marginBottom: '0.75rem',
                    }}
                  >
                    <div
                      style={{
                        width: `${sectionPercent}%`,
                        height: '100%',
                        background:
                          sectionPercent === 100
                            ? 'linear-gradient(90deg, #10b981, #34d399)'
                            : 'linear-gradient(90deg, #f0583a, #ff8c00)',
                        borderRadius: 2,
                        transition: 'width 0.3s ease',
                      }}
                    />
                  </div>

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
                    {sectionItems.map((si) => (
                      <li
                        key={si.globalIndex}
                        className={styles.featureCard}
                        style={{
                          padding: '0.85rem 1.25rem',
                          paddingLeft: '3rem',
                          position: 'relative',
                          cursor: 'pointer',
                          borderColor: checked[si.globalIndex] ? 'rgba(16, 185, 129, 0.3)' : undefined,
                          opacity: checked[si.globalIndex] ? 0.75 : 1,
                        }}
                        onClick={() => toggleItem(si.globalIndex)}
                      >
                        <input
                          type="checkbox"
                          checked={checked[si.globalIndex]}
                          onChange={() => toggleItem(si.globalIndex)}
                          onClick={(e) => e.stopPropagation()}
                          style={{
                            position: 'absolute',
                            left: '1rem',
                            top: '0.95rem',
                            width: 18,
                            height: 18,
                            accentColor: '#10b981',
                            cursor: 'pointer',
                          }}
                        />
                        <span
                          style={{
                            color: checked[si.globalIndex] ? '#64748b' : '#cbd5e1',
                            fontSize: '0.9rem',
                            lineHeight: 1.5,
                            textDecoration: checked[si.globalIndex] ? 'line-through' : 'none',
                            transition: 'color 0.2s ease',
                          }}
                        >
                          {si.item}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>

          {/* Form */}
          <div
            className={styles.featureCard}
            style={{
              border: '1px solid rgba(255, 140, 0, 0.15)',
              padding: '2.5rem',
              alignSelf: 'start',
            }}
          >
            {submitted ? (
              <div style={{textAlign: 'center', padding: '2rem 0'}}>
                <div style={{fontSize: '3rem', marginBottom: '1rem'}}>{'\u2705'}</div>
                <h3
                  style={{
                    color: 'var(--hs-text-heading)',
                    fontSize: '1.5rem',
                    fontWeight: 700,
                    marginBottom: '0.75rem',
                  }}
                >
                  Thank you!
                </h3>
                <p style={{color: 'var(--hs-text-muted)', fontSize: '1rem', lineHeight: 1.7}}>
                  Check your email for the download link. The checklist will arrive within 2 minutes.
                </p>
              </div>
            ) : (
              <>
                <h3
                  style={{color: 'var(--hs-text-heading)', fontSize: '1.3rem', fontWeight: 700, marginBottom: '1.5rem'}}
                >
                  Get Your Free Checklist
                </h3>
                <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
                  {[
                    {label: 'Full Name', key: 'name', type: 'text', placeholder: 'Jane Smith'},
                    {label: 'Work Email', key: 'email', type: 'email', placeholder: 'jane@company.com'},
                    {label: 'Company', key: 'company', type: 'text', placeholder: 'Acme Corp'},
                  ].map((field) => (
                    <div key={field.key}>
                      <label
                        className={styles.monoLabel}
                        style={{
                          display: 'block',
                          color: 'var(--hs-text-muted)',
                          fontSize: '0.8rem',
                          marginBottom: '0.4rem',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {field.label}
                      </label>
                      <input
                        type={field.type}
                        placeholder={field.placeholder}
                        required
                        value={form[field.key]}
                        onChange={(e) => setForm({...form, [field.key]: e.target.value})}
                        style={{
                          width: '100%',
                          padding: '0.75rem 1rem',
                          background: 'rgba(0, 0, 0, 0.4)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: 8,
                          color: 'var(--hs-text-heading)',
                          fontSize: '0.95rem',
                          outline: 'none',
                          boxSizing: 'border-box',
                        }}
                      />
                    </div>
                  ))}
                  <button
                    type="submit"
                    className={styles.primaryBtn}
                    style={{
                      marginTop: '0.5rem',
                      justifyContent: 'center',
                    }}
                  >
                    Download Checklist
                  </button>
                </form>
              </>
            )}
          </div>
        </div>

        {/* Related Resources */}
        <h2
          style={{
            fontSize: '1.8rem',
            fontWeight: 800,
            color: 'var(--hs-text-heading)',
            textAlign: 'center',
            marginBottom: '2rem',
          }}
        >
          Related Resources
        </h2>
        <div
          className={styles.gridCol3}
          style={{
            marginBottom: '4rem',
          }}
        >
          {relatedResources.map((r) => (
            <Link key={r.title} to={r.link} style={{textDecoration: 'none'}}>
              <div className={styles.featureCard} style={{height: '100%'}}>
                <h3
                  style={{
                    color: 'var(--hs-accent-light)',
                    fontSize: '1.1rem',
                    fontWeight: 700,
                    marginBottom: '0.75rem',
                  }}
                >
                  {r.title}
                </h3>
                <p className={styles.featureCardDesc}>{r.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </PageContent>
    </ProductPage>
  );
}
