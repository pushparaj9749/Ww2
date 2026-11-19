# ZERO-LINK — Infrastructure-Independent Communication Research (India)

> Research dossier. No hardware built. No Android app. Simulation only.

## The one-paragraph verdict

Direct 100 km handheld-to-handheld is physically impossible under Indian de-licensed limits (radio horizon ~10 km at handheld height). Multi-hop 100 km is feasible with planned relays and/or mobility using established LoRa physics + DTN store-carry-forward + E2E crypto — but in simulation it only reaches reliable delivery with ~100 % relay availability at 9–10 relay spacing. The proposed architecture (H1 TAM-DTN) is an honest integration of established technology, not a new architecture, and its advantage over a fair flooding baseline is energy efficiency (≈3–3.6×), not delivery probability.

## Deliverables

### Phase 1 — Research dossier

| File | What it is |
|---|---|
| `docs/EXECUTIVE_SUMMARY.md` | One-page summary |
| `docs/ZERO_LINK_RESEARCH_REPORT.md` | Master research report (scored evaluation) |
| `docs/EXISTING_TECHNOLOGY_COMPARISON.md` | Prior-art analysis (Bluetooth → Reticulum → optical/acoustic/MI) |
| `docs/ARCHITECTURE_HYPOTHESES.md` | Three hypotheses (H1 TAM-DTN, H2 Ferry, H3 Backbone) |
| `docs/ZERO_LINK_SYSTEM_DESIGN.md` | Detailed system design (layers, routing, crypto, failure handling) |
| `docs/INDIA_REGULATORY_RESEARCH.md` | WPC/DoT lawful path (865–867 MHz, ETA) |
| `docs/FEASIBILITY_100KM.md` | 100 km physics (Scenario A direct vs Scenario B multi-hop) |
| `docs/SIMULATION_PLAN.md` | Simulation methodology (Phase 1 — superseded by the Phase 2 audit) |
| `docs/RESEARCH_REFERENCES.md` | Bibliography (no fabricated sources) |

### Phase 2 — Simulation audit & scientific validation

| File | What it is |
|---|---|
| `docs/PHASE2_SIMULATION_AUDIT.md` | Audit of the Phase 1 simulator: 15 findings + 7 defects found in the Phase 2 rewrite itself |
| `docs/PHASE2_VALIDATION_RESULTS.md` | Fair 4-architecture comparison, 5 & 10 seeds, 100 km spacing × availability study |
| `docs/PHASE2_LIMITATIONS.md` | Every modelling assumption, its fidelity, and what would be needed to validate each claim |
| `docs/PHASE2_NOVELTY_REASSESSMENT.md` | Prior-art re-test; revised score 90/95 → ≈52/100 |
| `simulation/zero_link_sim.py` | Phase 2 simulator (stdlib only): 4 architectures, loss, airtime, half-duplex, collisions, batteries, storage, custody ACKs |
| `simulation/results_phase2.csv` / `.json` | Raw + aggregate results, 5 seeds × 8 scenarios × 4 architectures |
| `simulation/results_phase2_100km_sweep.csv` / `.json` | 100 km relay spacing × availability study (250 runs) |
| `simulation/results_phase2_hop_sensitivity.csv` | Fairness check: flooding hop-limit effect on the 100 km chain |
| `simulation/test_log_phase2*.txt` | Console logs for each run |
| `simulation/archive/` | Historical/interim outputs, preserved but not to be cited |

## Run the simulation

```bash
# primary (5 seeds) — writes CSV + JSON
python3 simulation/zero_link_sim.py --seeds 42,7,123,2024,99 \
    --out simulation/results_phase2.csv --json simulation/results_phase2.json

# 100 km relay spacing × availability study
python3 simulation/zero_link_sim.py --sweep-100km --seeds 42,7,123,2024,99,1,2,3,55,777

# flooding hop-limit fairness check
python3 simulation/zero_link_sim.py --hop-sensitivity --seeds 42,7,123,2024,99
```

Runtime: ≈53 s / ≈29 s / ≈5 s on one core. Python 3.8+, standard library only.

## Status labels

Every document distinguishes: **Established fact** (RFC/spec/measured), **Assumption** (stated, conservative), **Hypothesis** (proposed, unvalidated), **Simulation result** (software, not hardware). No hardware-validated results exist yet.

## What is *not* claimed

* No 100 km direct handheld range. 100 km always means multi-hop over N relays.
* No field-tested performance. All numbers are simulation output.
* No novelty claim for LoRa mesh, store-and-forward, flood-then-direct routing or custody transfer — all exist in Reticulum, MeshCore, Meshtastic, Briar and DTN RFCs.
* No claim that the architecture is superior to a star gateway on cost or latency where coverage exists.
