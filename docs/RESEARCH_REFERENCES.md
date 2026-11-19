# ZERO-LINK — Research References

> **Status:** Living bibliography. Every factual claim in the ZERO-LINK dossier should trace to a source listed here or to a first-principles calculation shown in-line.
> **Rule applied:** No fabricated sources, specifications, or experimental results. Where sources disagree (notably on Indian power limits), the disagreement is recorded rather than resolved by fiat.
> **Last updated:** 2026-11-19

---

## How to read this file

Each entry is tagged:

- **[ESTABLISHED]** — peer-reviewed paper, IETF RFC, official spec, or government publication.
- **[VENDOR/DOC]** — official project documentation or vendor datasheet (useful, but treat marketing claims with caution).
- **[SECONDARY]** — reputable secondary summary; used only to corroborate, never as sole support for a critical claim.
- **[CALCULATION]** — derived in this dossier from first principles (Friis, radio horizon, Fresnel); reproducible from the formulas given.

---

## 1. Radio physics and link budgets

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R1] | Friis, H. T. (1946). *A Note on a Simple Transmission Formula*. Proc. IRE. — P_r = P_t + G_t + G_r − FSPL − L_misc, FSPL = 20·log₁₀(4πdf/c). | [ESTABLISHED] | All link-budget calculations in `FEASIBILITY_100KM.md`. |
| [R2] | Semtech SX1276/SX1278 datasheet — sensitivity −137 dBm at SF12/BW125 kHz; TX power up to +20 dBm. Summarised at https://iottools.dev/lora-link-budget-calculator and https://zbotic.in/sx1276-lora-module-range-sensitivity-spreading-factor-guide/ | [VENDOR/DOC] | LoRa link-budget inputs. |
| [R3] | RF Link Budget Calculator — worked LoRa example, FSPL formula, fade-margin practice. https://rftools.io/calculators/rf/rf-link-budget/ | [SECONDARY] | Cross-check of Friis arithmetic. |
| [R4] | LoRaWAN SF12 link-budget analysis (EIRP +16 dBm EU / +24 dBm US, −137 dBm sensitivity, 156–164 dB budget; 250 bps at SF12; world-record 832 km balloon-to-ground). https://rfessentials.com/rf-knowledge-base/what-is-the-link-budget-for-a-lorawan-device-at-maximum-spreading-factor/ | [SECONDARY] | Why record ranges do not imply handheld 100 km. |
| [R5] | Line-of-sight / radio-horizon formulas: d_radio-horizon ≈ 4.12·√h km (h in m, 4/3-Earth model); Fresnel radius r ≈ 17.32·√(d/4f) m (d in km, f in GHz); 60% clearance rule. https://reversepcb.com/tools/line-of-sight-calculator/ ; https://www.jasra.org.my/antenna-height-vs-communication-range/ ; https://lorameshatlas.com/tools/range/ | [ESTABLISHED practice] | Horizon + Fresnel limits in `FEASIBILITY_100KM.md`. |

## 2. LoRa / LoRaWAN

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R6] | LoRaWAN architecture: end devices, 8-channel gateways (SX1301/1302/1303), Network Server (ChirpStack / The Things Stack); gateway does not decrypt payload; duty-cycle airtime budgets (EU868 1% ≈ 36 s/h); downlink scarcity. https://cloudstudioiot.com/hub/hardware/gateways-lorawan ; https://www.macnman.com/success-stories/blogs/lorawan-deployment-challenges ; https://cloudstudioiot.com/hub/how-lorawan-works | [SECONDARY] | `EXISTING_TECHNOLOGY_COMPARISON.md` LoRaWAN row. |
| [R7] | LoRa PHY trade-offs: R_b = SF·BW/2^SF; P_min = −174 + 10log₁₀(B) + NF + SNR_min; payload 51 B (SF12) to 242 B (SF7); link budgets >160 dB possible. https://next.gr/tutorials/rf-and-wireless-basics/long-range-lora-communication-protocol-tutorial | [SECONDARY] | Data-rate vs range trade-off. |
| [R8] | LoRa in India: IN865 band 865–867 MHz, channel plan, duty-cycle notes, 433 MHz P2P alternative, 915 MHz **not** unlicensed in India. https://zbotic.in/lorawan-vs-lora-point-to-point-architecture-use-cases/ ; https://gsasindia.com/blog/getting-started-lora-india-rylr998 ; https://zbotic.in/lora-technology-guide-india-long-range-iot-without-wifi/ | [SECONDARY] | India band selection. Power-limit figures differ between sources — see `INDIA_REGULATORY_RESEARCH.md` §3. |

## 3. Mesh systems (Meshtastic, MeshCore, Reticulum)

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R9] | Meshtastic range guide: handheld-to-handheld km-scale; elevated relays; 331 km ground-to-ground record under exceptional conditions; hop limit default 3 (max 7); terrain/vegetation effects. https://www.sdrstore.eu/meshtastic-range-guide-how-far-lora-mesh-nodes-reach/ ; https://meshunderground.com/posts/maximize-meshtastic-range-tips-and-deep-dive/ ; https://meshnology.com/blogs/meshnology-blog-1/the-complete-beginners-guide-to-meshtastic-2026-edition | [SECONDARY] | Meshtastic baseline. |
| [R10] | Meshtastic overview: LoRa mesh, multi-hop relay, 228-char message limit, encryption, India region 865–867 MHz. https://www.seeedstudio.com/blog/2024/12/10/all-you-need-to-know-about-meshtastic/ | [SECONDARY] | Meshtastic baseline. |
| [R11] | MeshCore routing: flood-once-then-direct (source routing with path record), up to 64 hops, companion/repeater/room-server roles; vs Meshtastic flooding. https://blog.waev.app/blog/how-lora-mesh-routing-works/ ; https://jrattechworks.com/meshcore-lora-mesh-network-guide/ ; https://kindlymorrow.com/blog/what-is-meshcore-guide-2026 | [SECONDARY] | MeshCore baseline + ZERO-LINK routing inspiration. |
| [R12] | Reticulum Network Stack manual — hardware chapter: RNode as open LoRa transceiver platform; raw LoRa modulation (not LoRaWAN); interface modes (access point / boundary / transport); KISS protocol. https://reticulum.network/manual/hardware.html | [VENDOR/DOC] | Reticulum baseline. |
| [R13] | RNode platform details: SX1276/1278, SX1262, SX1280 support; KISS commands; multi-radio. https://deepwiki.com/markqvist/Reticulum/6.2-rnode-platform | [SECONDARY] | Reticulum baseline. |
| [R14] | Reticulum Primer (Faragher, 2024): propagation nodes, solar nodes, vehicle uplinks, IFAC, announce management over LoRa. https://reticulum.betweentheborders.com/primer.pdf | [SECONDARY] | Reticulum operational patterns. |
| [R15] | µReticulum (MicroPython Reticulum): transport mode, LXMF messaging, split-packet framing over 255-byte LoRa frames, 500-byte MTU. https://github.com/varna9000/micropython-reticulum | [VENDOR/DOC] | Proof that Reticulum runs on microcontrollers. |

## 4. Short-range mesh (Bluetooth, Wi-Fi Direct, Bridgefy, Briar)

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R16] | Bluetooth 5.0 spec summary: LE Coded PHY (S=2 → 500 kbps, ~2× range; S=8 → 125 kbps, ~4× range); max TX +20 dBm; link-budget table (0 dBm → 160 m; 20 dBm → 530–630 m open field). https://www.bluetooth.com/wp-content/uploads/2019/03/Bluetooth_5-FINAL.pdf ; https://www.silabs.com/whitepapers/bluetooth-5-refined-for-the-iot | [VENDOR/DOC] | Bluetooth baseline. |
| [R17] | Bluetooth 5 measured extremes: indoor max ~60 m (Coded PHY, 9 dBm); outdoor ~527 m (8 dBm, 125 kbps); 4× claim not confirmed in all conditions. https://www.rutronik.com/fileadmin/Rutronik/Downloads/printmedia/products/06_wireless/bluetooth5.pdf | [ESTABLISHED measurement] | Why Bluetooth cannot reach 100 km. |
| [R18] | Bluetooth range factors: Coded PHY trades rate for range; both ends must support it; ~1 km hilly-terrain best case. https://www.mokosmart.com/factors-affecting-bluetooth-range-in-iot/ ; https://novelbits.io/bluetooth-5-advertisements/ | [SECONDARY] | Bluetooth baseline. |
| [R19] | Bridgefy: Bluetooth mesh SDK, ~100 m per hop, multi-hop relay via phones, density profiles, 3.5-day persistence (sparse profile). https://www.blog.brightcoding.dev/2026/05/25/bridgefy-ios-sdk-revolutionize-offline-messaging-with-bluetooth-mesh ; https://techcrunch.com/2017/09/18/bridgefy-lets-developers-build-mesh-networking-into-their-apps/ ; https://hakifedha.org/docs/tools/privacy-security/offline-communication-tools/mesh-network-tools/bridgefy-offline-messaging | [SECONDARY] | Bridgefy baseline. |
| [R20] | Briar: P2P over Tor + Bluetooth/Wi-Fi Direct offline sync; no servers, no phone number; QR-code pairing; Android-only (desktop beta); text-only offline. https://europeanpurpose.com/tool/briar ; https://reclaimthenet.org/recommended-tool/briar ; https://www.howtogeek.com/how-to-text-on-your-phone-without-cell-or-wifi/ | [SECONDARY] | Briar baseline. |

## 5. Delay-Tolerant Networking and MANET

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R21] | RFC 9171 — Bundle Protocol Version 7 (DTN): store-carry-forward overlay, bundles as CBOR blocks, custody transfer, convergence layers, security considerations. https://www.rfc-editor.org/rfc/rfc9171.html | [ESTABLISHED] | DTN architecture in ZERO-LINK. |
| [R22] | RFC 4838 — Delay-Tolerant Networking Architecture (referenced via MANET survey). https://www.offlineprotocol.com/learning/mesh-networking/what-is-a-mobile-ad-hoc-network-manet | [ESTABLISHED] | DTN rationale. |
| [R23] | MANET routing: AODV (RFC 3561, reactive, RREQ/RREP/RERR, destination sequence numbers) vs OLSRv2 (RFC 7181, proactive, MPR flooding); NHDP (RFC 6130). https://www.offlineprotocol.com/learning/mesh-networking/what-is-a-mobile-ad-hoc-network-manet ; https://www.easpublisher.com/get-articles/3285 ; https://onlinelibrary.wiley.com/doi/10.1155/2020/8810761 | [ESTABLISHED] | MANET baseline. |
| [R24] | DTN implementation survey (ISS emulation, bundle manager, custody transfer, fragmentation, priority queuing). https://arxiv.org/html/2605.21624v2 | [ESTABLISHED] | DTN implementation patterns. |

## 6. Alternative physical layers (optical, acoustic, magnetic)

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R25] | Underwater VLC review: VLC up to 5 Gbps, <1 ms latency, but <100 m in clear water, turbidity/alignment limits; acoustic <100 kbps, >1 s latency, <10 km; hybrid VLC+acoustic. https://www.mdpi.com/2304-6732/12/6/593 | [ESTABLISHED review] | Why optical/acoustic fail the 100 km target. |
| [R26] | Underwater sensor-network survey (ACM): acoustic modems (few kb/s, few km; MF 10–20 kHz BW); optical (1–10 Mbps, 1–150 m); magnetic induction (1–10 kbps, 2–10 m typical, up to ~90 m best case); comparison table. https://dx.doi.org/10.1145/3546827 | [ESTABLISHED survey] | Acoustic / MI / optical limits. |
| [R27] | Magnetic-induction range extension study: MI <100 m range, ~100 kbps capacity ceiling, conductivity effects. https://www.mdpi.com/2079-9292/14/22/4543 | [ESTABLISHED] | MI ceiling. |
| [R28] | Free-space optics: fog 70–350 dB/km (dense), rain 6–30 dB/km, haze 3–20 dB/km; FSO-only ~140 m in severe fog; hybrid FSO/RF complementary failure modes; ITU-R P.1814 link-margin practice. https://woodrowscientific.com/blog/free-space-optics-technology-systems/ ; https://woodrowscientific.com/blog/free-space-optical-communication-technology/ ; https://www.academia.edu/6975931/Free_space_optical_FSO_link_design_under_diverse_weather_conditions | [SECONDARY + ESTABLISHED] | FSO feasibility. |
| [R29] | Air-water VLC thesis (White Rose): DLOS optical air-to-water ~30 Mbps; underwater VLC <50 m; UAV relay concepts. https://etheses.whiterose.ac.uk/id/eprint/35421/1/WenzhiDu_PhDthesisWhiterose.pdf | [ESTABLISHED thesis] | Optical range corroboration. |

## 7. Indian regulation

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R30] | WPC ETA process: de-licensed bands list (2.4 GHz, 5 GHz, 865–867 MHz, 433–434 MHz, 13.56 MHz, etc.); ETA vs licence; Indian company required; CE RED reports accepted. https://www.jjrlab.com/news/how-to-get-an-indian-wpc-certificate.html ; https://e2ecomplianceadvisors.com/wpc-eta-approval ; http://www.baclcorp.com.cn/show.asp?para=en_6_1014_751 | [SECONDARY] | `INDIA_REGULATORY_RESEARCH.md`. |
| [R31] | WPC de-licensed band table with GSR numbers/dates (GSR 564(E) 2008 for 865–867 MHz; GSR 45(E) 2005 for 2.4 GHz; GSR 1048(E) 2018 for 5 GHz; GSR 680(E)/698(E) for 433 MHz). https://www.professionalutilities.com/wpc-certificate/wifi-router.php | [SECONDARY] | Band table. |
| [R32] | India 865–867 MHz power limits: sources disagree — 1 W EIRP (30 dBm) vs 4 W EIRP (36 dBm) / 4 W ERP; 200 kHz channel spacing; ETA required for sale/import. https://rfidsoftwares.com/resources/wpc-rfid-frequency-india/ ; https://www.wedoimport.com/compliance/wpc-eta-license-mandatory-product-list/ ; https://zbotic.in/lora-technology-guide-india-long-range-iot-without-wifi/ ; https://gsasindia.com/blog/getting-started-lora-india-rylr998 | [SECONDARY — CONFLICTING] | Recorded as open question; design uses conservative 1 W assumption. |
| [R33] | DoT/WPC 6 GHz Wi-Fi ETA transition deadline (6 July 2026) — evidence of active WPC administration. https://www.certification-india.com/en/dot-extends-6ghz-wi-fi-compliance-deadline/ | [SECONDARY] | Regulatory currency note. |

## 8. Prior-art and novelty caution

| # | Source | Type | Used for |
|---|--------|------|----------|
| [R34] | Reticulum manual + primer + µReticulum (see [R12]–[R15]) — demonstrates that LoRa + DTN-style store-and-forward + E2E crypto + multi-interface routing already exists as open prior art. | [VENDOR/DOC] | Novelty boundary for ZERO-LINK. |
| [R35] | MeshCore + Meshtastic (see [R9]–[R11]) — demonstrates LoRa mesh routing (flood and flood-then-direct) already exists. | [SECONDARY] | Novelty boundary. |
| [R36] | Briar + Bridgefy (see [R19]–[R20]) — demonstrates Bluetooth/Wi-Fi offline mesh already exists. | [SECONDARY] | Novelty boundary. |
| [R37] | DTN RFCs + MANET RFCs (see [R21]–[R23]) — demonstrates store-carry-forward and ad-hoc routing already exist. | [ESTABLISHED] | Novelty boundary. |

> **Patent note:** No patent search was performed as part of this dossier (no patent-database access in the research environment). Any claim of patent novelty would be unsupported. The dossier therefore claims **architectural integration novelty only**, and flags a formal prior-art/patent search as required future work (see `ZERO_LINK_RESEARCH_REPORT.md` §9).

---

## Open questions carried forward

1. **Indian 865–867 MHz EIRP limit** — secondary sources conflict (1 W vs 4 W). Must verify against the current WPC GSR text before any hardware design. Design assumption in this dossier: **≤1 W EIRP** (conservative).
2. **Duty-cycle / channel-access rules for 865–867 MHz in India** — EU868-style 1% limits do not clearly apply; LoRaWAN IN865 regional parameters specify channels and EIRP but the dossier does not treat them as law. Verify with WPC.
3. **Experimental-test permissions** — whether field trials with certified modules need additional WPC/DoT permission beyond ETA. Verify before any RF testing.
4. **Patent prior art** — not searched. Required before any novelty claim.
5. **Real-world LoRa range in Indian terrain** — no Indian field measurements were available; ranges in this dossier are planning estimates from link budgets + international reports, not Indian measurements.
