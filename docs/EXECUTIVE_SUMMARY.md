# ZERO-LINK — Executive Summary

> **Question:** Can India have infrastructure-independent communication reaching 100 km?
> **Answer:** Yes — as a multi-hop system with relays and/or mobility. No — as a direct handheld link. The physics is unambiguous.

---

## The discovery

**Direct 100 km (handheld ↔ handheld): IMPOSSIBLE.**
Two handhelds at 1.5 m see ~10 km to the radio horizon. 100 km is 10× beyond it. Free-space arithmetic says the link "closes" (+27 dB margin), but Earth curvature blocks the ray. Raising power does not fix geometry (and would be illegal). Any claim otherwise confuses paper arithmetic with propagation.

**Multi-hop 100 km: FEASIBLE with planning.**
Per-hop LoRa links of 2–15 km close comfortably within Indian de-licensed limits (865–867 MHz, ≤1 W EIRP). A 100 km chain needs 7–20 relays (or 2–5 elevated backbone nodes, or mobile ferries). Latency is seconds when connected; reliability needs DTN store-carry-forward to survive relay failures. Simulation confirms: H1 TAM-DTN delivers 100 km chains where flooding (hop limit) and star (gateway range) deliver zero.

## The architecture (H1 TAM-DTN)

Flat LoRa mesh. Flood-once-then-direct routing when a path exists. DTN store-carry-forward when partitioned. E2E encryption (X25519/Ed25519/AES-GCM). Energy-aware forwarding. Terrain-aware relay placement. No servers, no gateways, no telecom infrastructure.

**Honest novelty:** Integration + India optimisation + simulation validation. Not new physics. Reticulum is the prior-art ceiling; ZERO-LINK differentiates on DTN-first design, terrain planning, and validation — not on reinventing the stack.

## Simulation (software only, seed 42)

| Scenario | ZERO-LINK | Flooding | Star |
|---|---|---|---|
| Dense connected | 0.90 PDR, half the energy | 0.93 PDR | 0.03 |
| Sparse (no connectivity) | 0.07 | 0.07 | 0.00 |
| Partitioned + ferries | 0.50 (slow, DTN) | 0.25 | 0.00 |
| 100 km chain | 1.00 | 0.00 | 0.00 |
| Relay failures | 0.90 (graceful) | 0.93 | 0.03 |

Run it: `python3 simulation/zero_link_sim.py`

## Lawful path (India)

Certified LoRa modules in 865–867 MHz at low power for prototyping. WPC ETA for commercial sale/import. Verify the current GSR power limit (sources conflict: 1 W vs 4 W) before building. No illegal spectrum or power needed.

## What remains

1. Verify WPC GSR text. 2. Patent search. 3. Terrain-aware simulation. 4. Lawful field tests to calibrate range. 5. Prototype pilot.

## Bottom line

ZERO-LINK is a credible multi-hop DTN system, not a magic 100 km radio. Build the relays, plan the terrain, validate in the field. The vision (nationwide, infrastructure-independent) is a deployment programme, not a single device — and it starts with honest physics.
