# ZERO-LINK — Master Research Report

> **Mission:** Discover whether an infrastructure-independent communication architecture for India (100 km target) is possible, what the best scientific approach is, and what is genuinely new.
> **Answer in one paragraph:** A direct 100 km handheld link is physically impossible under Indian de-licensed limits (horizon + Fresnel). A multi-hop 100 km system is feasible with planned relays and/or mobility, using established LoRa physics + DTN store-carry-forward + E2E crypto. The architecture (H1 TAM-DTN) is an integration of established components, not new physics. Its contribution is DTN-first design, India terrain/regulatory optimisation, and simulation validation. No hardware has been built or tested.

---

## 1. Executive findings

1. **Physical layer is settled.** Sub-GHz LoRa (865–867 MHz) is the only viable bearer for 100 km in India. All other PHYs fail by orders of magnitude (see `EXISTING_TECHNOLOGY_COMPARISON.md`).
2. **100 km needs relays or mobility.** Single-hop handheld 100 km violates horizon physics (10 km horizon at handheld height). Multi-hop chains (7–20 relays) or ferry mobility are required (see `FEASIBILITY_100KM.md`).
3. **Reticulum is the prior-art ceiling.** ZERO-LINK does not beat Reticulum at the stack level. Its defensible contribution is narrower (see §4).
4. **Simulation validates the architecture** (software only): H1 TAM-DTN matches flooding on PDR in dense networks at half the energy, wins decisively on partitioned/chain scenarios, and degrades gracefully under failures (see §6).
5. **Lawful path exists.** Certified modules in 865–867 MHz at low power; WPC ETA for commercial deployment (see `INDIA_REGULATORY_RESEARCH.md`).

---

## 2. Research domains summary

### A. Wireless communication
- **RF (LoRa):** Only PHY with km-scale range at de-licensed power. Link budget closes at 10–20 km/hop; horizon/Fresnel are the real limits [R1][R2][R5].
- **Optical (VLC/FSO):** <100 m (VLC) / km in clear air but ~140 m in severe fog [R25][R28]. Fails Indian monsoon availability.
- **Acoustic (air):** Tens of metres. Fails.
- **Magnetic induction:** <100 m ceiling [R26][R27]. Fails.

### B. Network architectures
- **Peer-to-peer / MANET:** AODV/OLSR assume an end-to-end path exists [R23]. Fails on partitions.
- **DTN (RFC 9171):** Store-carry-forward handles partitions [R21]. This is the key architectural primitive for ZERO-LINK.
- **Hybrid:** H1 = MANET-style routing when connected + DTN when partitioned. This hybrid is the design.

### C. Information theory
- LoRa SF12: ~250 bps, −137 dBm sensitivity [R2][R4]. Shannon limit respected; no coding gain beyond what LoRa already provides.
- FEC (LoRa coding rate) + CRC + custody ACKs + E2E receipts provide reliability at low rate.
- Airtime (seconds/message at SF12) is the capacity bottleneck, not Shannon capacity.

### D. Physical feasibility
- See `FEASIBILITY_100KM.md`. Scenario A (direct): infeasible. Scenario B (multi-hop): feasible with relays/mobility.

### E. Security
- E2E: X25519 + Ed25519 + AES-256-GCM + HKDF, ratcheting, replay protection, signed receipts. No servers to breach. Metadata (routing headers) in clear — documented limitation.

---

## 3. Prior-art analysis (condensed)

Full analysis in `EXISTING_TECHNOLOGY_COMPARISON.md`. Key conclusions:

| Prior art | Verdict |
|---|---|
| Bluetooth / Wi-Fi Direct / Briar / Bridgefy | Short-range only. Cannot reach 100 km. Useful only as phone-access layer. |
| LoRaWAN | Proves LoRa range; architecture (star + servers) is opposite of ZERO-LINK. Negative baseline. |
| Meshtastic / MeshCore | LoRa mesh baselines. Flooding congestion / repeater dependence. ZERO-LINK improves routing + DTN. |
| Reticulum | Strongest prior art. LoRa + routing + E2E + multi-interface already exists. ZERO-LINK must differentiate on DTN-first + India optimisation + validation. |
| DTN / MANET | Established architectures. ZERO-LINK binds them to LoRa + India constraints. |
| Optical / acoustic / MI | Fail 100 km. Not bearers. |

---

## 4. Novelty assessment (honest)

**What is NOT novel:**
- LoRa PHY, DTN store-carry-forward, flood-then-direct routing, E2E crypto, mesh networking — all established (RFCs, Reticulum, MeshCore, Briar).

**What IS claimed (narrowly):**
1. **DTN-first LoRa mesh** tuned for Indian terrain and 865–867 MHz regulation (integration novelty).
2. **Terrain-aware relay planning** (elevation + Fresnel + vegetation) as a first-class design step.
3. **Simulation-validated comparison** against flooding and star baselines (validation novelty).
4. **H1 + H3 upgrade path** (flat mesh → elevated backbone) as a single architecture family.

**What is NOT claimed:**
- No new physical law, no new modulation, no patent novelty (patent search not performed).
- No single-hop 100 km.
- No hardware-validated performance.

---

## 5. Architecture (condensed)

Full design in `ZERO_LINK_SYSTEM_DESIGN.md`. Hypotheses in `ARCHITECTURE_HYPOTHESES.md`.

- **Primary: H1 TAM-DTN** — flat LoRa mesh, flood-once-then-direct when connected, DTN store-carry-forward when partitioned, energy-aware forwarding, India band/power compliance.
- **Disconnected mode: H2 ferrying** — H1 already ferries via mobile nodes; H2 is H1's behaviour on partitions, not a separate system.
- **Upgrade path: H3 backbone** — add elevated directional nodes where terrain allows, for fewer hops and lower latency.

---

## 6. Simulation results (software only)

Simulator: `simulation/zero_link_sim.py` (seed 42, 600 ticks × 10 s). **These are simulation results, not hardware performance.**

| Scenario | ZERO-LINK (H1) PDR | Flooding PDR | Star PDR | Notes |
|---|---|---|---|---|
| S1 Dense (40 nodes, 20×20 km, 5 km range) | 0.90 | 0.93 | 0.03 | ZERO-LINK half the TX/energy of flooding; star fails (1 gateway insufficient) |
| S2 Sparse (25 nodes, 50×50 km) | 0.07 | 0.07 | 0.00 | All fail — no connectivity, no delivery. Honest negative result. |
| S3 Partitioned + ferries (100 km corridor) | 0.50 | 0.25 | 0.00 | ZERO-LINK wins PDR via DTN ferrying; latency high (mean 1155 s) — DTN trade-off |
| S4 100 km chain (12 nodes, 10 km range) | 1.00 | 0.00 | 0.00 | ZERO-LINK delivers (11 hops, no hop limit); flooding hits hop limit 7; star out of range |
| S5 Failures (S1 + 40% relays die at tick 200) | 0.90 | 0.93 | 0.03 | ZERO-LINK degrades gracefully |

**Interpretation:**
- In dense connected networks, flooding is slightly better on PDR (0.93 vs 0.90) but costs ~2× the transmissions/energy. ZERO-LINK trades a small PDR margin for efficiency.
- In partitioned/chain scenarios, DTN + no-hop-limit routing is decisive (S3, S4).
- In sparse networks with no connectivity, nothing works (S2) — correctly.
- Star (LoRaWAN-like) fails everywhere except where a gateway happens to cover both ends — confirming that gateway dependence is the wrong architecture for infrastructure independence.

---

## 7. Final evaluation (scored)

Scoring: 1 (poor) – 5 (excellent). Weights per mission (Critical = ×3, High = ×2, Medium = ×1).

| Criterion | Weight | H1 TAM-DTN | H2 Ferry | H3 Backbone | Reasoning |
|---|---|---|---|---|---|
| Scientific feasibility | Critical | 5 | 4 | 4 | H1 uses only established physics + proven DTN. H2 needs mobility guarantees. H3 needs sites. |
| Infrastructure independence | Critical | 5 | 5 | 3 | H1/H2 need no fixed infra. H3 needs masts/sites (peer-operated, but still infra). |
| 100 km potential | Critical | 4 | 3 | 5 | H3 fewest hops. H1 needs 7–20 relays. H2 needs mobility, latency unbounded. |
| Architectural novelty | Critical | 3 | 3 | 3 | All are integrations of established components. No new physics. Score 3 = honest integration novelty. |
| Power efficiency | High | 4 | 5 | 3 | H2 lowest duty cycle. H1 efficient routing. H3 always-on backbone. |
| Reliability | High | 4 | 2 | 3 | H1 DTN + mesh redundancy. H2 latency/loss unbounded. H3 single-point backbone risk. |
| Security | High | 4 | 4 | 4 | All share E2E crypto. Metadata leakage in all (routing headers). |
| Scalability | High | 4 | 3 | 4 | H1/H3 scale by adding nodes. H2 scales with mobility density only. |
| Hardware cost | Medium | 4 | 5 | 2 | H2 cheapest (handhelds only). H3 most expensive (masts, solar, directional). |
| Implementation complexity | Medium | 3 | 4 | 3 | H2 simplest (no routing). H1/H3 need full stack. |

**Weighted totals (max 5×19=95):**
- H1: 5×3+5×3+4×3+3×3+4×2+4×2+4×2+4×2+4×1+3×1 = 15+15+12+9+8+8+8+8+4+3 = **90**
- H2: 12+15+9+9+10+4+8+6+5+4 = **82**
- H3: 12+9+15+9+6+6+8+8+2+3 = **78**

**Strongest candidate: H1 TAM-DTN.** It is the only hypothesis that is simultaneously feasible, infrastructure-independent, 100 km-capable (multi-hop), and reasonably efficient. H2 is a mode of H1, not a competitor. H3 is an upgrade path for H1 where elevation exists.

**If no candidate met the requirements:** H1 meets them *as a multi-hop DTN system*. No candidate meets them as a direct 100 km link. That distinction is the core honest finding.

---

## 8. Assumptions, limitations, unanswered questions

**Assumptions:**
- 865–867 MHz, ≤1 W EIRP (conservative; sources conflict — verify GSR).
- LoRa SF12 sensitivity −137 dBm; TX 20 dBm; 2 dBi handheld antennas.
- Relay availability 95% (for chain arithmetic); real availability TBD.
- Simulation range model (scalar, no terrain) approximates reality.

**Limitations:**
- No hardware built, no field measurements in Indian terrain.
- No patent prior-art search.
- No real LoRa PHY/collision modelling in simulation.
- Metadata leakage (routing headers) not mitigated by default.

**Unanswered questions:**
1. Real LoRa range in Indian terrain (Ghats, plains, urban) — needs field tests.
2. Current WPC GSR power/duty-cycle text — needs official verification.
3. Field-trial permission requirements — needs WPC confirmation.
4. Patent landscape — needs formal search.
5. Human mobility patterns for ferry optimisation — needs data.

---

## 9. Recommended next steps (in order)

1. Verify WPC GSR text (power, duty cycle, field-trial rules).
2. Formal patent/prior-art search.
3. Extend simulation with DEM terrain + LoRa airtime/collision models.
4. Lawful field tests with certified modules (low power, 865–867 MHz) to calibrate range.
5. Only then: prototype hardware + relay placement pilot.

---

## 10. Deliverables index

| # | File | Contents |
|---|---|---|
| 1 | `ZERO_LINK_RESEARCH_REPORT.md` (this file) | Master report |
| 2 | `EXISTING_TECHNOLOGY_COMPARISON.md` | Prior-art analysis |
| 3 | `ARCHITECTURE_HYPOTHESES.md` | H1/H2/H3 with novelty assessment |
| 4 | `ZERO_LINK_SYSTEM_DESIGN.md` | Detailed system design |
| 5 | `INDIA_REGULATORY_RESEARCH.md` | WPC/DoT regulatory path |
| 6 | `FEASIBILITY_100KM.md` | 100 km physics (Scenarios A/B) |
| 7 | `SIMULATION_PLAN.md` | Simulation methodology |
| 8 | `RESEARCH_REFERENCES.md` | Bibliography |
| 9 | `EXECUTIVE_SUMMARY.md` | One-page summary |
| — | `simulation/zero_link_sim.py` | Runnable simulator |

> **Final statement:** ZERO-LINK is feasible as a multi-hop DTN system with planned relays and/or mobility. It is not feasible as a direct 100 km handheld link. The architecture is an honest integration of established technology, validated in simulation, with a lawful path to prototyping. That is the discovery.
