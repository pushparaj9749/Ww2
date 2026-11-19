# ZERO-LINK — Architecture Hypotheses

> **Rule:** Three genuinely different hypotheses. Each states its closest predecessor honestly. Novelty is claimed only where it exists, and only at the level it exists (integration / optimisation / validation — not new physics).
> **Common ground (all hypotheses):** Sub-GHz LoRa PHY in India's de-licensed 865–867 MHz band (see `INDIA_REGULATORY_RESEARCH.md`), E2E encryption, DTN store-carry-forward. The hypotheses differ in **network architecture**, not in radio physics.

---

## H1 — Terrain-Adaptive LoRa Mesh with DTN Store-Carry-Forward (TAM-DTN)

**Closest predecessor:** Reticulum + RNode [R12]–[R15], with MeshCore-style flood-then-direct routing [R11] and DTN custody transfer [R21].
**Novelty claim:** *Integration + India-specific optimisation + simulation validation.* Not a new PHY, not a new routing primitive. The claim is that a DTN-first, terrain-aware, energy-aware LoRa mesh tuned for Indian topography and regulation is a distinct deployable architecture, even though its components are established.

### Core concept
A flat peer mesh of LoRa nodes. When a connected path exists, messages route multi-hop (flood-once-then-direct). When no path exists (partition), nodes store bundles and carry them until a contact appears (DTN). Relay placement is planned from terrain data (elevation, Fresnel clearance, vegetation) rather than ad-hoc.

### Physical mechanism
LoRa chirp spread-spectrum at 865–867 MHz, SF/BW adapted per link (SF7 for short/high-rate, SF12 for long/low-rate). Per-hop planning range 2–15 km depending on terrain (see `FEASIBILITY_100KM.md`).

### Discovery
- Neighbour discovery: periodic short beacons (low duty cycle) + promiscuous listening.
- Path discovery: flood-once with path-record accumulation (MeshCore pattern [R11]); destination returns the path; subsequent messages use cached direct routes.
- Announce-style identity exchange (Reticulum pattern [R14]) but rate-limited on slow links.

### Encoding / transmission
- Bundle format inspired by RFC 9171 (primary block + payload + extension blocks) but simplified for LoRa MTU (≤242 B).
- Payload E2E-encrypted (AES-GCM); routing headers in clear.
- FEC (LoRa coding rate) + CRC + hop-by-hop custody ACKs; E2E delivery receipt from destination.

### Reception
- Half-duplex LoRa RX; nodes listen except during TX.
- Duplicate suppression via bundle ID + seen-cache.

### Intermediate nodes
- **Yes, for connected operation.** 100 km needs ~7–20 relays in a chain (depending on per-hop range).
- **No, for DTN operation.** If no chain exists, mobile nodes ferry bundles (store-carry-forward).

### Disconnected operation
- DTN store-carry-forward: bundles persist on nodes; epidemic-lite forwarding (limited copies) on contact; TTL/expiry prevents infinite storage.

### Scaling
- Flood-once-then-direct limits flooding cost to first contact.
- DTN copy budget (e.g., max 4–8 copies) bounds epidemic explosion.
- Role separation (endpoint vs relay) reduces airtime waste (MeshCore lesson [R11]).

### Power / hardware
- Node: LoRa transceiver (SX1262-class) + MCU (ESP32-class) + 2 dBi antenna + Li-ion/solar. TX 20–100 mW; sleep µW.
- Relay: same + solar panel + elevated antenna (mast/rooftop/hill).

### Limitations
- Needs relay density for low-latency 100 km; gaps force DTN delays (minutes–hours).
- SF12 airtime ~1.5–2.5 s/message; channel congestion at density.
- Terrain shadowing can break chains unpredictably.

### Scientific feasibility
- **Feasible as a multi-hop/DTN system.** Each hop is within established LoRa link budgets. The system-level claim (100 km delivery) depends on relay density/mobility, not on new physics.
- **Not feasible as a single-hop 100 km handheld link** (horizon + Fresnel, see `FEASIBILITY_100KM.md`).

### What is architecturally different
- DTN-first (store-carry-forward is the default, not a fallback).
- Terrain-aware relay planning (elevation + Fresnel + vegetation) as a first-class design step.
- Energy-aware forwarding (low-battery nodes shed relay duty).
- India band/power compliance built into the PHY configuration.

---

## H2 — Opportunistic Ferry Network (OFN)

**Closest predecessor:** Briar's phone-to-phone store-and-forward [R20] + DTN epidemic routing (RFC 9171 [R21]) + delay-tolerant ferrying literature.
**Novelty claim:** *Application of ferry-DTN to dedicated LoRa nodes with human-mobility patterns.* The ferry concept itself is established; the hypothesis is that scheduled human mobility (buses, trains, market days, school routes) can be exploited as a predictable transport layer for 100 km delivery without any fixed relays.

### Core concept
No fixed relay chain. Nodes are carried by people/vehicles. Messages spread epidemically (with copy limits) whenever carriers meet. Delivery time is governed by mobility, not by radio range. 100 km is covered by physical movement of carriers, not by RF hops.

### Physical mechanism
Same LoRa PHY as H1, but links are short-range opportunistic contacts (tens to hundreds of metres, seconds to minutes). Radio range barely matters; contact duration matters.

### Discovery
- Encounter-based: nodes beacon on contact; exchange bundle summaries (anti-entropy: "I have bundles for X, Y, Z").
- No global routing tables; utility scores (last-seen, encounter frequency, delivery history) guide forwarding.

### Encoding / transmission
- Same bundle + E2E encryption as H1.
- Forwarding policy: spray-and-wait (limited copies) or utility-based (PRoPHET-style delivery predictability).

### Reception
- Store-and-forward: every node is a custodian until delivery receipt returns.

### Intermediate nodes
- **No fixed intermediates.** Carriers *are* the intermediates, but they are mobile and unplanned.

### Disconnected operation
- **This is the native mode.** Disconnection is assumed; connectivity is an opportunity.

### Scaling
- Copy budget bounds storage/energy. Utility routing bounds wasted forwards.
- Scales with carrier density and mobility, not with radio range.

### Power / hardware
- Handheld LoRa node (phone-attached or standalone). Very low duty cycle (beacon + opportunistic TX).
- No masts, no solar relays, no site maintenance.

### Limitations
- Latency: minutes to days. No delivery guarantee without mobility assumptions.
- Needs carrier density; sparse areas = no delivery.
- Privacy: carriers hold ciphertext (safe) but metadata (who messaged whom, when) leaks to carriers unless padded.

### Scientific feasibility
- **Feasible for delay-tolerant delivery** (eventual delivery if mobility connects the graph). This is proven DTN behaviour [R21][R24].
- **Not feasible for timely 100 km delivery** without mobility guarantees. H2 cannot promise latency.

### What is architecturally different
- Zero fixed infrastructure (not even relays).
- Mobility as the transport layer.
- Best suited to rural India where fixed relays are hard to maintain but human mobility (buses, trains, foot traffic) is dense.

---

## H3 — Elevated Backbone + LoRa Access (EBLA)

**Closest predecessor:** Ham-radio / point-to-point backbone practice + LoRaWAN gateway placement logic [R6] + hybrid FSO/RF backbone thinking [R28].
**Novelty claim:** *Decentralised backbone (no telecom operator, no server) using elevated high-gain links.* The backbone concept is established; the hypothesis is that a small number of elevated, solar-powered, peer-operated backbone nodes can provide 100 km coverage as a decentralised alternative to telecom towers.

### Core concept
Two tiers:
- **Access tier:** Handheld LoRa nodes (H1-style mesh, 2–5 km hops).
- **Backbone tier:** Elevated nodes (hills, rooftops, water tanks, temples, schools) with high-gain directional antennas forming long point-to-point links (20–50 km per backbone hop). Backbone nodes peer-route among themselves without any central server.

### Physical mechanism
- Access: LoRa omnidirectional, SF9–SF12.
- Backbone: LoRa (or higher-rate sub-GHz) with directional Yagi/panel antennas (10–15 dBi), elevated 10–30 m. Higher gain + elevation extends per-hop range and clears Fresnel obstructions.

### Discovery
- Access: as H1.
- Backbone: static/neighbour-table routing (backbone topology changes slowly); link-state or distance-vector among backbone nodes only.

### Encoding / transmission
- Same bundle + E2E encryption.
- Backbone links can use lower SF (higher rate) because gain + elevation improve SNR.

### Reception
- Backbone nodes are always-on (solar + battery), listen continuously.

### Intermediate nodes
- **Yes — backbone nodes.** 100 km needs ~2–5 backbone hops + access hops at each end.

### Disconnected operation
- If backbone is down, access-tier DTN (H1) still works locally; backbone DTN stores bundles for later.

### Scaling
- Backbone scales by adding backbone nodes (like adding towers, but peer-operated).
- Access scales by adding handhelds (no backbone change).

### Power / hardware
- Backbone: solar + battery + mast + directional antenna. Higher cost/complexity than H1 relays.
- Access: handheld as H1.

### Limitations
- Needs elevated sites (land access, mounting, maintenance).
- Directional antennas need aiming; misalignment loses gain.
- Backbone nodes are single points of failure for their area (mitigated by mesh redundancy).
- Higher cost per backbone node.

### Scientific feasibility
- **Feasible.** Elevated + directional LoRa links of 20–50 km are within link budgets (see `FEASIBILITY_100KM.md` Scenario A with elevation). This is the **only** hypothesis that approaches 100 km with few hops.
- Still not single-hop handheld-to-handheld 100 km.

### What is architecturally different
- Explicit two-tier design (backbone + access) instead of flat mesh.
- Decentralised backbone (peer-operated, no operator/server) — the "tower without the telecom company" hypothesis.
- Best latency of the three hypotheses for 100 km (few hops, high-rate backbone).

---

## Comparison of hypotheses

| Criterion | H1 TAM-DTN | H2 OFN (Ferry) | H3 EBLA (Backbone) |
|---|---|---|---|
| Fixed infrastructure | Relays (light) | **None** | Backbone nodes (heavy) |
| 100 km hops needed | 7–20 | 0 RF hops (mobility) | 2–5 backbone + access |
| Latency (connected) | Seconds–minutes | Minutes–days | Seconds |
| Latency (disconnected) | Minutes–hours (DTN) | Hours–days | Minutes–hours (DTN fallback) |
| Cost to deploy | Medium | **Low** | High |
| Maintenance | Medium | Low | High |
| Best for | Villages, campuses, disaster relief | Rural mobility corridors | Hill/rooftop-rich areas, fixed coverage |
| Closest prior art | Reticulum/MeshCore | Briar/DTN epidemic | Ham backbone / LoRaWAN gateways |

## Recommendation

**H1 (TAM-DTN) as the primary architecture**, with H2 as its disconnected-mode behaviour (H1 already includes ferrying) and H3 as an optional upgrade path (add backbone nodes where elevation is available). H1 is the best balance of feasibility, cost, and honesty: it does not promise single-hop 100 km, it degrades gracefully to DTN, and its components are all established — so the engineering risk is in integration and validation, not in new physics.

H2 alone is too slow for most use cases. H3 alone is too expensive and site-dependent. H1 + optional H3 upgrades is the credible path.
