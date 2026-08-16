# docs/assets

Committed demo artifacts for docs and the README (not under gitignored `reports/`).

| File | What it is |
|------|------------|
| [`zyvor-dev-mission-control-demo.gif`](zyvor-dev-mission-control-demo.gif) | README inline preview (GitHub renders GIFs) |
| [`zyvor-dev-mission-control-demo.mp4`](zyvor-dev-mission-control-demo.mp4) | H.264 recording — play on GitHub blob page |
| [`zyvor-dev-mission-control-demo.webm`](zyvor-dev-mission-control-demo.webm) | Original Playwright journey capture |
| [`zyvor-dev-demo.steps`](zyvor-dev-demo.steps) | Step file used to produce that video |
| **→ YouTube** | [youtu.be/oXVVWZiRgQY](https://youtu.be/oXVVWZiRgQY) — thumbnail via `https://i.ytimg.com/vi/oXVVWZiRgQY/maxresdefault.jpg` |
| [`guestkit-mission-control-demo.webm`](guestkit-mission-control-demo.webm) / [`.mp4`](guestkit-mission-control-demo.mp4) | Local capture of Mission Control → GuestKit flow |
| **→ YouTube** | [youtu.be/ys7SvKKqf9w](https://youtu.be/ys7SvKKqf9w) — thumbnail via `https://i.ytimg.com/vi/ys7SvKKqf9w/maxresdefault.jpg` |
| [`guestkit-github-demo.webm`](guestkit-github-demo.webm) / [`.mp4`](guestkit-github-demo.mp4) | Direct browser journey of the GitHub README (no dashboard) |
| [`guestkit-github.steps`](guestkit-github.steps) | Steps used by the MC flow job / direct GitHub recording |
| **→ YouTube** | [youtu.be/EwqVdjSabvE](https://youtu.be/EwqVdjSabvE) — thumbnail via `https://i.ytimg.com/vi/EwqVdjSabvE/maxresdefault.jpg` |
| [`guestkit-product-demo.webm`](guestkit-product-demo.webm) / [`.mp4`](guestkit-product-demo.mp4) | Direct journey of [zyvor.dev/guestkit](https://zyvor.dev/guestkit) |
| [`guestkit-product.steps`](guestkit-product.steps) | Steps for the product-page recording |
| **→ YouTube** | [youtu.be/43pSPf-FVsE](https://youtu.be/43pSPf-FVsE) — thumbnail via `https://i.ytimg.com/vi/43pSPf-FVsE/maxresdefault.jpg` |
| **KT walkthrough → YouTube** | [youtu.be/-_2jph4jW7c](https://youtu.be/-_2jph4jW7c) — full Mission Control KT session, recorded via `../../scripts/demo-videos/` (not committed here — see that folder's README) |

Regenerate the Mission Control demo (against a live serve / NodePort):

```bash
node scripts/record-mission-control-demo.mjs http://HOST:30080 docs/assets/guestkit-mission-control-demo.webm
ffmpeg -y -i docs/assets/guestkit-mission-control-demo.webm -c:v libx264 -pix_fmt yuv420p -movflags +faststart -an docs/assets/guestkit-mission-control-demo.mp4
```

Regenerate:

```bash
argus flow run https://zyvor.dev --steps docs/assets/zyvor-dev-demo.steps --video
cp reports/artifacts/flows/cli/journey.webm docs/assets/zyvor-dev-mission-control-demo.webm
ffmpeg -y -i docs/assets/zyvor-dev-mission-control-demo.webm -c:v libx264 -pix_fmt yuv420p -movflags +faststart -an docs/assets/zyvor-dev-mission-control-demo.mp4
ffmpeg -y -i docs/assets/zyvor-dev-mission-control-demo.webm -vf "fps=8,scale=720:-1:flags=lanczos" -loop 0 docs/assets/zyvor-dev-mission-control-demo.gif
```
