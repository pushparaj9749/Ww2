# ZERO-LINK — Infrastructure-Independent Communication Research (India)

> Research dossier. No hardware built. No Android app. Simulation only.

## The one-paragraph verdict

Direct 100 km handheld-to-handheld is physically impossible under Indian de-licensed limits (radio horizon ~10 km at handheld height). Multi-hop 100 km is feasible with planned relays and/or mobility using established LoRa physics + DTN store-carry-forward + E2E crypto. The proposed architecture (H1 TAM-DTN) is an honest integration of established technology, validated in software simulation.

## Deliverables

| File | What it is |
|---|---|
| `docs/EXECUTIVE_SUMMARY.md` | One-page summary |
| `docs/ZERO_LINK_RESEARCH_REPORT.md` | Master research report (scored evaluation) |
| `docs/EXISTING_TECHNOLOGY_COMPARISON.md` | Prior-art analysis (Bluetooth → Reticulum → optical/acoustic/MI) |
| `docs/ARCHITECTURE_HYPOTHESES.md` | Three hypotheses (H1 TAM-DTN, H2 Ferry, H3 Backbone) |
| `docs/ZERO_LINK_SYSTEM_DESIGN.md` | Detailed system design (layers, routing, crypto, failure handling) |
| `docs/INDIA_REGULATORY_RESEARCH.md` | WPC/DoT lawful path (865–867 MHz, ETA) |
| `docs/FEASIBILITY_100KM.md` | 100 km physics (Scenario A direct vs Scenario B multi-hop) |
| `docs/SIMULATION_PLAN.md` | Simulation methodology |
| `docs/RESEARCH_REFERENCES.md` | Bibliography (no fabricated sources) |
| `simulation/zero_link_sim.py` | Runnable simulator (stdlib only) |

## Run the simulation

```bash
python3 simulation/zero_link_sim.py
```

Software only — results are NOT real-world hardware performance.

## Status labels

Every document distinguishes: **Established fact** (RFC/spec/measured), **Assumption** (stated, conservative), **Hypothesis** (proposed, unvalidated), **Simulation result** (software, not hardware). No hardware-validated results exist yet.
