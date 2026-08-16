# Vendored assets

## mermaid.min.js

- Source: `https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js`
- License: MIT (Mermaid.js, https://github.com/mermaid-js/mermaid)
- Why vendored: `orchestrator/enterprise.py`'s CSP sets `script-src 'self' 'unsafe-inline'` —
  a CDN `<script src="https://cdn...">` is blocked, so the report templates that
  render an attack graph (`agents/reporter/attack_graph.py`) serve this file
  same-origin instead, via the existing `/reports` static mount.
- To update: re-download `mermaid@<version>/dist/mermaid.min.js` from the same
  CDN and replace this file; no build step required (it's a self-contained UMD
  bundle).
