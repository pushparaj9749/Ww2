# ZERO-LINK — Simulation Plan

> **Purpose:** Validate the H1 TAM-DTN architecture in software before any hardware. Compare against two baselines. All results are simulation, not hardware performance.

---

## 1. Simulator

- **Location:** `simulation/zero_link_sim.py` (Python 3, stdlib only — no dependencies).
- **Model:** Discrete-event / tick-based simulation of N nodes on a 2D plane with terrain-independent range (range is a parameter; terrain is modelled as range reduction + link failure probability).
- **Node behaviours:** Endpoint, relay, mobile ferry. Each node has battery, bundle store, route cache, seen-cache.
- **Link model:** Two nodes can exchange bundles if distance ≤ range (with probabilistic loss). Range is configurable per scenario (2 km / 5 km / 10 km).
- **Routing models compared:**
  1. **ZERO-LINK (H1 TAM-DTN):** Flood-once-then-direct + DTN store-carry-forward (copy budget 6).
  2. **Baseline A — Flooding mesh (Meshtastic-like):** Blind flooding, hop limit 7, no path cache, no DTN (drop if no path).
  3. **Baseline B — Star (LoRaWAN-like):** Endpoints → gateway (if in range) → destination. No peer relay. Gateway assumed always up (best case for star).

## 2. Metrics

- **Delivery success rate (PDR):** Delivered / sent.
- **Latency:** Mean / median / p95 (seconds; DTN deliveries can be hours — reported separately).
- **Energy:** Total TX energy (J) + per-delivered-message energy.
- **Overhead:** Total transmissions per delivered message.

## 3. Scenarios

| # | Scenario | Nodes | Range | Mobility | Purpose |
|---|---|---|---|---|---|
| S1 | Dense connected | 40 nodes, 20×20 km | 5 km | Static | Best case for all architectures |
| S2 | Sparse connected | 25 nodes, 50×50 km | 5 km | Static | Tests relay density |
| S3 | Partitioned + ferry | 30 nodes, 100×20 km corridor | 5 km | 5 ferries moving | Tests DTN vs flooding/star |
| S4 | Long chain | 12 nodes in 100 km line | 10 km | Static | Tests 100 km chain feasibility |
| S5 | Node failures | S1 + 20% relays fail mid-run | 5 km | Static | Tests failure handling |

## 4. How to run

```bash
python3 simulation/zero_link_sim.py
```

Output: per-scenario table (PDR, latency, energy, overhead) for all three architectures + a summary verdict. Seed is fixed (42) for reproducibility.

## 5. Expected results (hypotheses, to be confirmed by running)

- S1: All three deliver; ZERO-LINK lowest overhead (direct routing beats flooding); star lowest latency (single hop to gateway).
- S2: Flooding degrades (hop limit); ZERO-LINK DTN rescues some deliveries; star fails (gateway out of range).
- S3: ZERO-LINK delivers via ferries (slow); flooding and star fail (no path).
- S4: ZERO-LINK delivers via chain; flooding hits hop limit; star fails.
- S5: ZERO-LINK degrades gracefully (DTN); flooding loses more; star unaffected (gateway assumed up).

## 6. Limitations (must be stated with any results)

- 2D plane, no real terrain/elevation/Fresnel modelling (range is a scalar).
- No real LoRa PHY (no SF/airtime/collision modelling beyond transmission counts).
- No crypto overhead modelling.
- Mobility is random waypoint, not real human mobility.
- **Simulation success ≠ hardware success.** Field validation with real radios in Indian terrain is still required.

## 7. Next steps after simulation

1. Add terrain/elevation (DEM-based) link model.
2. Add LoRa airtime/collision model (SF-dependent).
3. Add energy model with RX/sleep currents.
4. Calibrate range parameters with real LoRa measurements (lawful, certified modules).
5. Only then consider hardware prototyping.
