# ZERO-LINK — Existing Technology Comparison

> **Purpose:** Establish the prior-art baseline honestly. For each system: operating principle, architecture, infrastructure, range, power, relay dependence, security, scalability, limits, and what ZERO-LINK could improve.
> **Method:** Only sources in `RESEARCH_REFERENCES.md`. Ranges are planning estimates, not guarantees. Record ranges (e.g., 331 km, 832 km) are exceptional-condition results and are labelled as such.

---

## 1. Summary matrix

| System | PHY / medium | Infra needed | Typical 1-hop range (planning) | Power | Relays? | Security | 100 km potential |
|---|---|---|---|---|---|---|---|
| Bluetooth LE (incl. Coded PHY) | 2.4 GHz RF | None (phone-to-phone) | 10–100 m; ~500 m best-case outdoor | Very low | Yes (mesh apps) | LE pairing; app-level E2E varies | **No** — physics + horizon |
| Wi-Fi Direct | 2.4/5 GHz RF | None | 50–200 m | High | Yes | WPA2 group keys | **No** |
| LoRa (raw P2P) | Sub-GHz chirp spread-spectrum | None | 2–15 km rural; 0.5–3 km urban | Very low | Optional | None at PHY | **Only with elevation + relays** |
| LoRaWAN | LoRa + MAC | Gateways + Network Server | 2–15 km to gateway | Very low (end device) | Gateway, not peer | AES-128 (AppSKey/NwkSKey) | **No** — star, needs gateways |
| Meshtastic | LoRa mesh | None (nodes relay) | 2–15 km/hop; 331 km record (exceptional) | Low | Yes (every node) | Channel PSK, E2E optional | **Only as dense multi-hop chain** |
| MeshCore | LoRa mesh | None (repeaters) | Similar to Meshtastic; 64 hops | Low | Yes (dedicated repeaters) | E2E (X25519 etc.) | **Only as dense multi-hop chain** |
| Reticulum (+RNode) | Raw LoRa / TCP / serial | None (interfaces) | Same LoRa physics; multi-interface | Low | Optional (transport mode) | E2E (X25519/Ed25519/AES) | **Closest baseline; still needs relays/mobility** |
| Briar | Bluetooth / Wi-Fi Direct / Tor | None offline | 10–100 m/hop | Phone battery | Yes (phones) | E2E, no servers | **No** — short-range hops only |
| Bridgefy | Bluetooth mesh SDK | None | ~100 m/hop | Phone battery | Yes (phones) | App-dependent | **No** |
| DTN (RFC 9171) | Any convergence layer | None (overlay) | Transport-dependent | Transport-dependent | Store-carry-forward | BSP blocks (optional) | **Architecture, not a radio — needs a PHY** |
| MANET (AODV/OLSR) | Usually Wi-Fi RF | None | Wi-Fi range (~100 m) | High | Yes (all nodes) | Optional (IPsec etc.) | **No** — Wi-Fi range ceiling |
| VLC / FSO | Light (visible / near-IR) | None | VLC <100 m; FSO km in clear air, ~140 m in severe fog | Medium–high (pointing) | Optional | Optical = hard to intercept | **No for 100 km in Indian monsoon/fog** |
| Acoustic (air) | Sound in air | None | Tens of metres (audible); ultrasonic ~m | Low–medium | Optional | None | **No** |
| Magnetic induction | Near-field B-field | None | Centimetres to ~90 m (best case) | Low | Optional | None | **No** |

**Reading the table:** No existing system delivers 100 km handheld-to-handheld without infrastructure. Every long-range entry is LoRa-based and still needs either elevation, a relay chain, or mobility. That is the honest starting point for ZERO-LINK.

---

## 2. System-by-system analysis

### 2.1 Bluetooth (incl. Bluetooth 5 LE Coded PHY)

- **Operating principle:** 2.4 GHz GFSK; LE Coded PHY adds forward error correction (S=2 → 500 kbps, S=8 → 125 kbps) to improve receiver sensitivity without raising TX power [R16][R18].
- **Architecture:** Star (peripheral/central) or LE Mesh (managed flooding). Phone apps (Briar, Bridgefy) build peer meshes on top.
- **Infrastructure:** None for direct links; mesh needs participating phones.
- **Range:** 10–100 m typical; Silicon Labs link-budget table: 0 dBm → ~160 m, 20 dBm → ~530–630 m open field [R16]. Measured outdoor max ~527 m at 8 dBm/125 kbps; indoor ~60 m [R17]. The "4× range" claim is a sensitivity improvement (4–6 dB), not a guarantee [R16].
- **Power:** Very low (mA-scale). Coded PHY increases airtime → higher average power per message [R16].
- **Relay dependence:** Single-hop by default; multi-hop only via app-layer mesh (Briar/Bridgefy).
- **Security:** LE Secure Connections (ECDH); app-layer E2E varies by app.
- **Scalability:** Mesh flooding does not scale to large areas; connection limits per phone.
- **Limits:** 2.4 GHz path loss + body/wall attenuation; horizon at handheld height ~5–10 km is irrelevant because link budget closes far earlier. Cannot approach 100 km.
- **What ZERO-LINK could improve:** Nothing at the PHY — Bluetooth is the wrong tool for 100 km. ZERO-LINK should treat Bluetooth only as an optional short-range access layer (phone ↔ node), never as the long-haul bearer.

### 2.2 Wi-Fi Direct

- **Operating principle:** IEEE 802.11 peer-to-peer groups at 2.4/5 GHz; higher bandwidth, higher power than Bluetooth.
- **Architecture:** Group Owner + clients; app-layer relay for multi-hop.
- **Infrastructure:** None for a group; multi-hop needs relay phones.
- **Range:** ~50–200 m practical (higher power, but 2.4/5 GHz FSPL is worse than sub-GHz and antennas are small).
- **Power:** High (hundreds of mA); poor for battery nodes.
- **Security:** WPA2-PSK group keys; weak for open mesh use.
- **Limits:** Power, range, phone OS background restrictions (the same reason Briar is Android-only [R20]).
- **What ZERO-LINK could improve:** Replace Wi-Fi Direct with sub-GHz LoRa for the long-haul bearer; keep Wi-Fi only for high-rate local offload if needed.

### 2.3 LoRa (raw point-to-point) — the PHY baseline

- **Operating principle:** Chirp spread-spectrum; spreading factor SF7–SF12 trades data rate for sensitivity. SF12/BW125 kHz: ~250–293 bps, −137 dBm sensitivity [R2][R4][R7].
- **Architecture:** None at PHY — raw modem. Network behaviour is whatever the stack above it does.
- **Infrastructure:** None for P2P.
- **Range:** Planning estimates: rural open 8–15 km (SF12), suburban 3–5 km, urban 1–3 km [R2][R5]. World record 832 km was balloon-to-ground line-of-sight [R4] — not a handheld expectation.
- **Power:** 20–100 mW TX; µW sleep. AA-battery nodes can run years at low duty cycle [R7].
- **Relay dependence:** None for P2P; mesh stacks add relays.
- **Security:** None at PHY. Must be added above.
- **Scalability:** Single channel, low rate; collisions grow with density. Payload 51 B at SF12 [R7].
- **Limits:** Data rate (text-only), airtime (seconds per message at SF12), horizon/Fresnel at ground level, terrain shadowing.
- **What ZERO-LINK could improve:** Everything above the PHY — routing, DTN store-carry-forward, E2E crypto, energy-aware forwarding, India band/power compliance. The PHY itself is established technology and is **not** claimed as novel.

### 2.4 LoRaWAN

- **Operating principle:** LoRa PHY + star MAC; end devices → gateways → Network Server → Application Server [R6].
- **Architecture:** Centralised star. Gateway is a transparent forwarder (does not decrypt payload); Network Server manages join/FCnt/downlinks [R6].
- **Infrastructure:** **Required** — gateways + backhaul (usually IP). This violates ZERO-LINK's infrastructure-independence requirement by design.
- **Range:** Same LoRa physics to the gateway (km-scale), but coverage is defined by gateway placement, not peer links.
- **Power:** End device <50 µW average [R6].
- **Security:** AES-128 with AppSKey/NwkSKey; good E2E story, but requires server infrastructure.
- **Scalability:** Thousands of nodes per gateway at low duty cycle; downlink capacity is the bottleneck; EU868 1% duty cycle ≈ 36 s/h airtime [R6].
- **Limits:** Needs gateways; uplink-focused; seconds-to-minutes downlink latency; not a peer mesh.
- **What ZERO-LINK could improve:** Remove gateways/servers entirely; replace star with peer mesh + DTN. LoRaWAN is a useful **negative baseline**: it proves LoRa range works, but its architecture is the opposite of ZERO-LINK's.

### 2.5 Meshtastic

- **Operating principle:** LoRa + flooding mesh; every node can relay; default hop limit 3 (max 7) [R9].
- **Architecture:** Flat flooding mesh; channel name + PSK for grouping/encryption [R10].
- **Infrastructure:** None.
- **Range:** 2–15 km/hop with good antennas/placement; 331 km ground-to-ground record under exceptional conditions [R9]. Urban 0.5–3 km [R9].
- **Power:** Low (LoRa radio + MCU).
- **Relay dependence:** Yes — every node relays by default, which improves coverage but wastes airtime.
- **Security:** Channel PSK; E2E optional. Not a strong decentralized-identity story.
- **Scalability:** Practically 20–50 nodes per area before congestion [R9]; flooding overhead grows with density.
- **Limits:** Text-only (228 chars [R10]); flooding congestion; hop limit caps 100 km chains (3 hops × 15 km = 45 km max, and that assumes perfect placement).
- **What ZERO-LINK could improve:** Smarter routing than blind flooding (flood-once-then-direct, DTN store-carry-forward, energy-aware forwarding); stronger E2E crypto + identity; India-specific band/power/terrain tuning; simulation-validated relay placement.

### 2.6 MeshCore

- **Operating principle:** LoRa + hybrid routing: first message floods to discover a path (recording repeaters), destination returns the path, later messages use direct source routing [R11].
- **Architecture:** Role-separated: companions (endpoints, do not relay), repeaters (dedicated infrastructure), room servers [R11].
- **Infrastructure:** None, but needs intentionally placed repeaters for coverage.
- **Range:** Same LoRa physics; up to 64 hops [R11].
- **Power:** Low.
- **Relay dependence:** Yes — dedicated repeaters, not every node.
- **Security:** E2E crypto for direct messages.
- **Scalability:** Better than flooding (direct routing saves airtime); still needs repeater density.
- **Limits:** Needs repeater placement; group traffic still floods; 100 km needs ~7–20 well-placed repeaters in a chain.
- **What ZERO-LINK could improve:** MeshCore is the **closest routing prior art**. ZERO-LINK's differentiation must be: DTN store-carry-forward for disconnected operation (MeshCore assumes a connected path), terrain-aware relay planning for Indian topography, and formal simulation comparison. Without those, ZERO-LINK would just be a MeshCore clone.

### 2.7 Reticulum (+ RNode)

- **Operating principle:** Multi-interface network stack (LoRa via RNode, TCP, serial, etc.); raw LoRa modulation, **not** LoRaWAN [R12]. RNode is an open transceiver platform (SX1276/1278, SX1262, SX1280) [R13].
- **Architecture:** Interface-agnostic routing with announce/path tables; transport mode turns a node into a relay; access-point/boundary modes control announce propagation [R12][R14]. LXMF messaging; 500-byte MTU over 255-byte LoRa frames via split-packet framing [R15].
- **Infrastructure:** None required; can optionally bridge to IP.
- **Range:** Same LoRa physics per hop; multi-hop via transport nodes.
- **Power:** Low (RNode-optimised).
- **Security:** E2E via X25519/Ed25519/AES/HKDF/HMAC; IFAC for interface access control [R12][R14].
- **Scalability:** Designed for large, heterogeneous networks; announce management is the scaling challenge on slow LoRa links [R14].
- **Limits:** Still bounded by LoRa per-hop range; needs relay density or mobility for 100 km; announce overhead on slow links.
- **What ZERO-LINK could improve:** Reticulum is the **strongest overall prior art** — it already combines LoRa + routing + E2E crypto + multi-interface. ZERO-LINK cannot honestly claim novelty over Reticulum at the stack level. The defensible ZERO-LINK contribution is narrower: (a) India-specific physical/regulatory optimisation, (b) DTN-first (store-carry-forward as the default, not an add-on), (c) terrain-aware relay planning + simulation validation, (d) phone-accessible deployment model. See `ARCHITECTURE_HYPOTHESES.md`.

### 2.8 Briar

- **Operating principle:** P2P messaging over Tor (online) + Bluetooth/Wi-Fi Direct (offline); no servers, no phone number [R20].
- **Architecture:** Trust-network mesh; messages hop phone-to-phone when devices are in range; store-and-forward via phones [R20].
- **Infrastructure:** None offline.
- **Range:** Bluetooth/Wi-Fi range per hop (10–100 m) [R20].
- **Power:** Phone battery; background restrictions hurt reliability [R20].
- **Security:** E2E, audited, no metadata servers. Strongest privacy story among short-range options.
- **Scalability:** Needs dense Briar users; Android-only (iOS background limits) [R20].
- **Limits:** Short-range hops only; text-only offline; no long-haul bearer.
- **What ZERO-LINK could improve:** Add a sub-GHz long-haul bearer so messages do not need phones to be within 100 m. Briar's trust/E2E model is worth reusing; its radio layer is not.

### 2.9 Bridgefy

- **Operating principle:** Bluetooth mesh SDK; phones relay for each other [R19].
- **Architecture:** App-layer mesh with density profiles (sparse/high-density) [R19].
- **Infrastructure:** None.
- **Range:** ~100 m/hop; 10 hops ≈ 500 m [R19].
- **Power:** Phone battery.
- **Security:** App-dependent; not a strong E2E story.
- **Scalability:** Needs participating phones; no network without users [R19].
- **Limits:** Bluetooth range ceiling; phone-dependence; closed SDK.
- **What ZERO-LINK could improve:** Everything — dedicated LoRa nodes remove phone-dependence and extend per-hop range by ~100×. Bridgefy is a weak baseline, useful only to show that phone-only mesh cannot reach 100 km.

### 2.10 Delay-Tolerant Networking (DTN, RFC 9171)

- **Operating principle:** Store-carry-forward overlay; bundles (CBOR blocks) persist at nodes until a forwarding opportunity appears [R21].
- **Architecture:** Overlay above any convergence layer (TCP, LoRa, etc.); custody transfer moves responsibility hop-by-hop [R21][R24].
- **Infrastructure:** None — works over whatever links exist, including intermittent ones.
- **Range:** Transport-dependent. DTN does not create range; it exploits mobility and intermittent contacts.
- **Power:** Transport-dependent.
- **Security:** Bundle Security Protocol blocks (optional); primary block stays in clear for routing [R21].
- **Scalability:** Epidemic routing scales poorly (copies explode); utility-based routing (PRoPHET, CGR) improves it.
- **Limits:** Latency is unbounded (hours/days if no contact); needs contact-graph knowledge or epidemic cost.
- **What ZERO-LINK could improve:** DTN is an **architecture, not a radio**. ZERO-LINK's job is to bind DTN to a LoRa convergence layer + E2E crypto + India constraints. The binding is the contribution; DTN itself is established (RFC 9171, CCSDS, ISS deployment [R24]).

### 2.11 MANET (AODV / OLSR)

- **Operating principle:** Mobile ad-hoc routing: AODV (reactive, RREQ/RREP/RERR, destination sequence numbers, RFC 3561) vs OLSRv2 (proactive, link-state, MPR flooding, RFC 7181) [R23].
- **Architecture:** Flat IP mesh; every node routes.
- **Infrastructure:** None.
- **Range:** Typically Wi-Fi range (~100 m/hop). MANET routing does not extend radio range.
- **Power:** High (Wi-Fi).
- **Security:** Optional (IPsec, etc.); not inherent.
- **Scalability:** OLSR suits dense networks; AODV suits sparse/on-demand. Both assume an end-to-end path exists.
- **Limits:** No path → no delivery. MANET has no store-carry-forward story for partitioned networks.
- **What ZERO-LINK could improve:** Combine MANET-style route discovery with DTN store-carry-forward so partitioned networks still deliver (eventually). Neither alone suffices for 100 km.

### 2.12 Visible-light / free-space optics (VLC / FSO)

- **Operating principle:** Intensity-modulated light (LED/laser) detected by photodiode; VLC 380–780 nm, FSO near-IR [R25][R28].
- **Architecture:** Point-to-point (needs alignment) or diffuse (wide beam, low rate) [R25].
- **Infrastructure:** None.
- **Range:** VLC <100 m in clear water/air [R25]; FSO km-scale in clear air but ~140 m in severe fog (350 dB/km) [R28]. Rain 6–30 dB/km, haze 3–20 dB/km [R28].
- **Power:** Medium–high (optical power + pointing/tracking).
- **Security:** Line-of-sight = hard to intercept; no crypto needed for confidentiality against off-axis eavesdroppers (but not a substitute for E2E crypto).
- **Scalability:** Point-to-point only; needs alignment per link.
- **Limits:** Fog/rain/turbidity kill availability; alignment; eye-safety limits on optical power.
- **What ZERO-LINK could improve:** Nothing for the 100 km target in Indian monsoon/fog conditions. Optical is a **high-rate short-range complement** (e.g., backbone offload in clear weather), not the primary bearer. Hybrid FSO/RF has complementary failure modes [R28] — worth noting, not worth building as primary.

### 2.13 Acoustic (air)

- **Operating principle:** Pressure waves in air (audible or ultrasonic).
- **Architecture:** Broadcast; no routing.
- **Infrastructure:** None.
- **Range:** Audible voice ~100 m; ultrasonic data ~metres. Underwater acoustic is different (km-scale, kb/s [R26]) but irrelevant to overland India messaging.
- **Power:** Low–medium.
- **Security:** None (broadcast).
- **Limits:** Ambient noise, low bandwidth, no privacy.
- **What ZERO-LINK could improve:** Nothing. Acoustic in air cannot meet range/rate/security requirements.

### 2.14 Magnetic induction (MI)

- **Operating principle:** Time-varying magnetic field from a coil induces voltage in a nearby coil (near-field) [R26][R27].
- **Architecture:** Point-to-point near-field.
- **Infrastructure:** None.
- **Range:** Centimetres to ~10 m typical; ~90 m best-case (5 MHz, large coils) [R26]; <100 m ceiling [R27].
- **Power:** Low; can also transfer power.
- **Security:** None inherent.
- **Limits:** 1/r³ field falloff; coil size vs range trade-off; narrow bandwidth (~100 kbps ceiling [R27]).
- **What ZERO-LINK could improve:** Nothing for 100 km. MI is a niche (underground, underwater, through-metal) — not a 100 km bearer.

---

## 3. What the comparison proves

1. **The physical layer for 100 km is LoRa (sub-GHz chirp spread-spectrum) or nothing.** Every other PHY fails on range, rate, or weather availability by orders of magnitude. This is an established fact, not a ZERO-LINK invention.
2. **No existing system achieves 100 km without relays, elevation, or mobility.** Record ranges are exceptional-condition demonstrations, not deployable coverage.
3. **Reticulum is the prior-art ceiling.** Any ZERO-LINK design that does not beat or complement Reticulum on a specific axis (DTN-first operation, India terrain/regulation, simulation-validated placement) is a reimplementation, not an innovation.
4. **The open problem is not the radio — it is the network.** Routing, store-carry-forward, energy-aware forwarding, E2E identity, and relay placement for Indian terrain are where ZERO-LINK must contribute.
