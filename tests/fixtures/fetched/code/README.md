# HyperSDK Platform Website

**Enterprise marketing site for the HyperSDK platform.**

Built with **Docusaurus 3**, **React 19**, and **TypeScript** — 52 marketing pages, 30 PDF presentations, ROI calculator, assessment quiz, and lead capture with UTM attribution.

```text
┌──────────────────────────────────────────────────────────────┐
│  Site         Landing · Products · Pricing · Blog · FAQ      │
├──────────────────────────────────────────────────────────────┤
│  Lead gen     ROI calculator · Whitepaper · Contact forms    │
├──────────────────────────────────────────────────────────────┤
│  Backend      Go contact-mailer · nginx · SSL                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Why This Site

| Need | Answer |
|------|--------|
| Product positioning | 52 pages across 12-product suite |
| Sales enablement | ROI calculator + assessment quiz |
| Technical credibility | 30 PDF presentations + architecture pages |
| Lead attribution | UTM capture + GitHub referrer tagging |
| i18n reach | Multi-locale FAQ and homepage content |

---

## Platform at a Glance

| Layer | What's in the repo |
|-------|-------------------|
| **Frontend** | Docusaurus 3 + React 19 — `src/`, `docs/` |
| **Content** | Marketing MDX, blog, presentations — `docs/`, `static/` |
| **Backend** | Go contact-mailer — `cmd/` |
| **Deploy** | nginx, k8s manifests, SSL — `nginx/`, `k8s/` |
| **Data** | FAQ, pricing, product stats — `src/data/` |

---

## Quick Start

```bash
git clone https://github.com/ssahani/hypersdk-web.git && cd hypersdk-web
npm install
npm start        # → http://localhost:3000
npm run build    # production static site
```

| Scenario | Path |
|----------|------|
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Analytics setup | README § Analytics |
| Product pages | `src/pages/` |

---

## Architecture

```
Website (:443)          HyperSDK (:5080)         hyper2kvm (:5070)
├── Landing             ├── 47-view dashboard    ├── 12-view dashboard
├── 52 marketing pages  ├── 238 API routes       ├── 110+ APIs
├── Blog (16 posts)     └── 10 cloud providers   └── VNC console
└── Lead capture
```

---

## Documentation

| Goal | Document |
|------|----------|
| Docs index | [docs/README.md](docs/README.md) |
| User stories | [docs/USER_STORIES.md](docs/USER_STORIES.md) |
| Live site | [zyvor.dev](https://zyvor.dev) |

---

## Development

See project docs for CI, testing, and contribution guidelines. Historical build summaries in the repo root are snapshots — **`docs/` and this README are authoritative.**

---

## License

See [LICENSE](LICENSE) or project-specific licensing files in `docs/legal/`.
