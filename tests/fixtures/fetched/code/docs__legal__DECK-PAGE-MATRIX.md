# Deck · page · doc alignment matrix

Last verified: 2026-06-02. Stats from `src/data/platform-stats.ts` (repo root — single source of truth for marketing numbers).

| Product | Marketing page | Doc guide | Client overview PDF | Sibling repo decks |
| --- | --- | --- | --- | --- |
| HyperSDK Platform | [/hypersdk](/hypersdk) | [/docs/hypersdk-platform](/docs/hypersdk-platform) | `/presentations/client/hypersdk/hypersdk-client.pdf` | `../hypersdk-/docs/client-presentations/` |
| hyper2kvm | [/hyper2kvm](/hyper2kvm) | [/docs/hyper2kvm](/docs/hyper2kvm) | `/presentations/client/hyper2kvm/hyper2kvm-client.pdf` | `../hyper2kvm-/docs/client-presentations/` |
| GuestKit | [/guestkit](/guestkit) | [/docs/guestkit](/docs/guestkit) | `/presentations/client/guestkit/guestkit-client.pdf` | `../guestkit/docs/client-presentations/` |
| Machina | [/machina](/machina) | [/docs/machina](/docs/machina) | `/presentations/client/machina/machina-client.pdf` | `../machina/docs/client-presentations/` |
| Zyvor Fabric | [/zyvor-fabric](/zyvor-fabric) | [/docs/zyvor-fabric](/docs/zyvor-fabric) | `/presentations/client/zyvor-fabric/zyvor-fabric-client.pdf` | `../zyvor-fabric/docs/client-presentations/` |
| Zeus OS | [/zeus-os](/zeus-os) | [/docs/zeus-os](/docs/zeus-os) | `/presentations/client/zeus-os/zeus-os-client.pdf` | `../v9s/docs/client-presentations/` |
| Veyron | [/vmrogue](/veyron) | [/docs/veyron](/docs/veyron) | `/presentations/client/vmrogue/vmrogue-client.pdf` | `../Veyron/docs/client-presentations/` |
| Ragnarok | [/ragnarok](/ragnarok) | [/docs/ragnarok](/docs/ragnarok) | `/presentations/client/ragnarok/ragnarok-client.pdf` | `../ragnarok/docs/client-presentations/` |
| Aether | [/aether](/aether) | [/docs/aether](/docs/aether) | `/presentations/client/aether/aether-client.pdf` | `../Aether/docs/client-presentations/` |
| PacketWolf | [/packetwolf](/packetwolf) | [/docs/packetwolf](/docs/packetwolf) | `/presentations/client/packetwolf/packetwolf-client.pdf` | `../packetwolf/docs/client-presentations/` |
| Forge | [/forge](/forge) | [/docs/forge](/docs/forge) | `/presentations/client/forge/forge-client.pdf` | `../forge/docs/client-presentations/` |
| IronWolf | [/ironwolf](/ironwolf) | [/docs/ironwolf](/docs/ironwolf) | `/presentations/client/ironwolf/ironwolf-client.pdf` | `../IronWolf/docs/client-presentations/` |
| HyperCluster | [/hypercluster](/hypercluster) | [/docs/hypercluster](/docs/hypercluster) | `/presentations/client/hypercluster/hypercluster-client.pdf` | `../hypercluster/docs/client-presentations/` |

**Sync workflow:** `npm run presentations:sync` copies sibling HTML into `static/presentations/client/<productId>/`. `npm run presentations:generate` builds overview decks from `platform-stats.ts` and PDFs for all HTML.

**Quarterly check:** Run `npm run stats:check`, verify matrix rows, refresh `CLIENT_DECK_SPECS` taglines in `scripts/generate-presentation-pdfs.ts`, and re-run sync + generate with `--force`.
