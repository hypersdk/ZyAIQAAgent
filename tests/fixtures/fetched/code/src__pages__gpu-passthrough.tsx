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
  StatGrid,
  styles,
  MarketingHero,
} from '../components/shared';
import {solutionPageBlogLinks} from '../data/solution-blog-links';

const benchmarks = [
  {workload: 'CUDA Matrix Multiply', bareMetal: '142 TFLOPS', passthrough: '140 TFLOPS', overhead: '1.4%'},
  {workload: 'TensorFlow ResNet-50', bareMetal: '890 img/s', passthrough: '878 img/s', overhead: '1.3%'},
  {workload: 'LLM Inference (Llama 70B)', bareMetal: '45 tok/s', passthrough: '44 tok/s', overhead: '2.2%'},
  {workload: 'FFmpeg H.265 Encode', bareMetal: '185 fps', passthrough: '182 fps', overhead: '1.6%'},
  {workload: 'Blender Render', bareMetal: '4.2 min', passthrough: '4.3 min', overhead: '2.4%'},
];

const supportedGPUs = [
  {
    vendor: 'NVIDIA',
    models: 'A100, H100, L40S, RTX 4090, RTX 6000 Ada',
    driver: '535+',
    status: 'Full Support',
    statusColor: '#10b981',
  },
  {vendor: 'NVIDIA', models: 'T4, V100, A10, A30', driver: '535+', status: 'Full Support', statusColor: '#10b981'},
  {vendor: 'AMD', models: 'MI300X, MI250X, MI210', driver: 'ROCm 6.0+', status: 'Full Support', statusColor: '#10b981'},
  {vendor: 'AMD', models: 'RX 7900, W7900', driver: 'AMDGPU', status: 'Full Support', statusColor: '#10b981'},
  {vendor: 'Intel', models: 'Flex 170, Flex 140', driver: 'i915', status: 'Full Support', statusColor: '#10b981'},
  {vendor: 'Intel', models: 'Arc A770, A750', driver: 'i915', status: 'Community', statusColor: '#f59e0b'},
];

const comparison = [
  {feature: 'Performance', passthrough: '98%+', vgpu: '85-95%', sharing: '60-80%', cloud: '90-95%'},
  {feature: 'Cost', passthrough: '$0 (hardware only)', vgpu: '$2K+/GPU/year license', sharing: '$0', cloud: '$2-8/hr'},
  {
    feature: 'Multi-tenant',
    passthrough: '1 VM per GPU',
    vgpu: 'Multiple VMs',
    sharing: 'Multiple VMs',
    cloud: 'Managed',
  },
  {feature: 'Setup Complexity', passthrough: 'Medium', vgpu: 'High', sharing: 'Low', cloud: 'None'},
];

export default function GPUPassthrough(): ReactNode {
  return (
    <ProductPage
      title="GPU Passthrough & vGPU"
      description="Run AI/ML workloads on KVM with full GPU access. 98%+ bare-metal performance with automated configuration."
    >
      <MarketingHero pageId="gpu-passthrough" />

      <PageContent>
        <StatGrid
          columns={3}
          stats={[
            {value: '98%+', label: 'Bare-Metal Performance'},
            {value: 'vGPU', label: 'Multi-Tenant GPU Sharing'},
            {value: 'CUDA', label: 'Full Framework Support'},
          ]}
        />

        <SectionHeader eyebrow="Use Cases" title="GPU-Accelerated Workloads on KVM" />
        <FeatureGrid
          columns={3}
          features={[
            {title: 'AI/ML Training', desc: 'Train deep learning models with direct GPU access and full CUDA support.'},
            {title: 'Inference Serving', desc: 'Low-latency model serving with dedicated or shared GPU resources.'},
            {title: 'Virtual Desktop (VDI)', desc: 'GPU-accelerated virtual desktops for engineers and designers.'},
            {title: 'Scientific Computing', desc: 'CUDA-accelerated simulations and finite element analysis.'},
            {title: 'Video Rendering', desc: 'GPU-accelerated encoding, 3D rendering, and post-production.'},
            {title: 'Database Acceleration', desc: 'GPU-accelerated analytics and real-time query engines.'},
          ]}
        />

        {/* Performance Benchmarks */}
        <SectionHeader
          eyebrow="Performance"
          title="Near Bare-Metal Performance"
          subtitle="Independent benchmarks confirm that GPU passthrough on KVM delivers within 1-3% of native hardware performance across all major workloads."
        />
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
                <th style={{padding: '1rem'}}>Workload</th>
                <th style={{padding: '1rem'}}>Bare Metal</th>
                <th style={{padding: '1rem'}}>GPU Passthrough</th>
                <th style={{padding: '1rem'}}>Overhead</th>
              </tr>
            </thead>
            <tbody>
              {benchmarks.map((row, i) => (
                <tr
                  key={row.workload}
                  style={{
                    borderBottom: i < benchmarks.length - 1 ? '1px solid var(--ifm-color-emphasis-200)' : undefined,
                  }}
                >
                  <td style={{padding: '1rem', fontWeight: 600, color: 'var(--hs-text-heading)'}}>{row.workload}</td>
                  <td
                    style={{
                      padding: '1rem',
                      color: 'var(--hs-text-muted)',
                      fontFamily: 'var(--hs-font-mono)',
                      fontSize: '0.9rem',
                    }}
                  >
                    {row.bareMetal}
                  </td>
                  <td
                    style={{
                      padding: '1rem',
                      color: 'var(--hs-text-muted)',
                      fontFamily: 'var(--hs-font-mono)',
                      fontSize: '0.9rem',
                    }}
                  >
                    {row.passthrough}
                  </td>
                  <td style={{padding: '1rem'}}>
                    <span
                      style={{
                        background: 'rgba(16, 185, 129, 0.12)',
                        color: '#10b981',
                        padding: '0.2rem 0.6rem',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        fontFamily: 'var(--hs-font-mono)',
                      }}
                    >
                      {row.overhead}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Supported GPUs */}
        <SectionHeader
          eyebrow="Compatibility"
          title="Supported GPU Hardware"
          subtitle="HyperSDK Platform supports GPU passthrough for NVIDIA, AMD, and Intel GPUs across data center and workstation models."
        />
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
                <th style={{padding: '1rem'}}>Vendor</th>
                <th style={{padding: '1rem'}}>Models</th>
                <th style={{padding: '1rem'}}>Driver</th>
                <th style={{padding: '1rem'}}>Status</th>
              </tr>
            </thead>
            <tbody>
              {supportedGPUs.map((row, i) => (
                <tr
                  key={`${row.vendor}-${row.models}`}
                  style={{
                    borderBottom: i < supportedGPUs.length - 1 ? '1px solid var(--ifm-color-emphasis-200)' : undefined,
                  }}
                >
                  <td style={{padding: '1rem', fontWeight: 600, color: 'var(--hs-text-heading)'}}>{row.vendor}</td>
                  <td style={{padding: '1rem', color: 'var(--hs-text-muted)', fontSize: '0.9rem'}}>{row.models}</td>
                  <td
                    style={{
                      padding: '1rem',
                      color: 'var(--hs-text-muted)',
                      fontFamily: 'var(--hs-font-mono)',
                      fontSize: '0.85rem',
                    }}
                  >
                    {row.driver}
                  </td>
                  <td style={{padding: '1rem'}}>
                    <span
                      style={{
                        background: `${row.statusColor}18`,
                        color: row.statusColor,
                        padding: '0.2rem 0.6rem',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                      }}
                    >
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Requirements */}
        <SectionHeader
          eyebrow="Requirements"
          title="What You Need for GPU Passthrough"
          subtitle="Four prerequisites to enable full GPU passthrough on your KVM host."
        />
        <FeatureGrid
          columns={2}
          features={[
            {
              title: 'Hardware: IOMMU / VT-d',
              desc: 'Enable IOMMU (Intel VT-d or AMD-Vi) in your BIOS/UEFI settings. This allows the hypervisor to assign PCI devices directly to virtual machines with hardware-level isolation.',
            },
            {
              title: 'Kernel: 5.15+ with vfio-pci',
              desc: 'Linux kernel 5.15 or later with the vfio-pci module loaded. Add intel_iommu=on (or amd_iommu=on) to your kernel command line and bind the GPU to the vfio-pci driver.',
            },
            {
              title: 'Host: Unbind GPU Driver',
              desc: 'The host must not have a GPU driver loaded for the passthrough device. Use vfio-pci to claim the device at boot, preventing the host from initializing the GPU.',
            },
            {
              title: 'Guest: Install Vendor Drivers',
              desc: 'Install the appropriate vendor GPU drivers inside the VM after passthrough is configured. NVIDIA 535+, AMD ROCm 6.0+, or Intel i915 depending on your hardware.',
            },
          ]}
        />

        {/* Comparison */}
        <SectionHeader
          eyebrow="Comparison"
          title="GPU Passthrough vs. Alternatives"
          subtitle="Compare GPU passthrough to vGPU licensing, GPU sharing, and cloud GPU instances."
        />
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
                <th style={{padding: '1rem'}}>Feature</th>
                <th style={{padding: '1rem'}}>GPU Passthrough</th>
                <th style={{padding: '1rem'}}>vGPU (NVIDIA GRID)</th>
                <th style={{padding: '1rem'}}>GPU Sharing</th>
                <th style={{padding: '1rem'}}>Cloud GPU</th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((row, i) => (
                <tr
                  key={row.feature}
                  style={{
                    borderBottom: i < comparison.length - 1 ? '1px solid var(--ifm-color-emphasis-200)' : undefined,
                  }}
                >
                  <td style={{padding: '1rem', fontWeight: 600, color: 'var(--hs-text-heading)'}}>{row.feature}</td>
                  <td style={{padding: '1rem', color: '#10b981', fontWeight: 600, fontSize: '0.9rem'}}>
                    {row.passthrough}
                  </td>
                  <td style={{padding: '1rem', color: 'var(--hs-text-muted)', fontSize: '0.9rem'}}>{row.vgpu}</td>
                  <td style={{padding: '1rem', color: 'var(--hs-text-muted)', fontSize: '0.9rem'}}>{row.sharing}</td>
                  <td style={{padding: '1rem', color: 'var(--hs-text-muted)', fontSize: '0.9rem'}}>{row.cloud}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <RelatedBlogSection links={solutionPageBlogLinks.gpuPassthrough} />

        <CTASection
          title="Need GPU Passthrough for Your Migration?"
          subtitle="Our team can help you plan GPU-accelerated VM deployments on KVM, including IOMMU configuration, driver setup, and performance validation."
          primaryCta={{label: 'Talk to an Expert', to: '/contact?intent=demo'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
