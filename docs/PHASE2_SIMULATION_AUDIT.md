# Phase 2 — Simulation Audit

**Status:** audit of the Phase 1 simulator (`simulation/zero_link_sim.py` @ commit
`1672f92`) against the claims in `docs/SIMULATION_PLAN.md`,
`docs/ARCHITECTURE_HYPOTHESES.md`, `docs/ZERO_LINK_SYSTEM_DESIGN.md` and
`docs/FEASIBILITY_100KM.md`.

**Headline:** the Phase 1 simulator did **not** implement the loss, timing,
contention or fairness properties its accompanying document claimed. Three of
the five Phase 1 conclusions survive re-testing; the *magnitude* of the ZERO-LINK
advantage does not.

> All results in this dossier are from a **software simulation**. No hardware was
> used, no field measurements exist, and nothing here is field-tested performance.

---

## 1. Method

1. Read the committed Phase 1 simulator (`git show 1672f92:simulation/zero_link_sim.py`,
   297 lines) line by line.
2. Extracted every quantitative claim made in `docs/SIMULATION_PLAN.md` and the
   Phase 1 results tables.
3. Diffed each claim against the code path that would have to implement it.
4. Rewrote the simulator (Phase 2) so each property is either implemented,
   explicitly labelled an approximation, or removed from the claims.
5. Re-ran every scenario with 5 seeds, then re-checked with 10 seeds.

Findings are graded:

| Severity | Meaning |
|---|---|
| **Critical** | Invalidates a specific Phase 1 numerical claim |
| **Major** | Biases the comparison toward or against an architecture |
| **Minor** | Reduces precision, reproducibility or interpretability |

---

## 2. Findings

### A1 — Probabilistic packet loss was documented but never implemented (**Critical**)

`docs/SIMULATION_PLAN.md` line 11 states links deliver "if distance ≤ range
(with probabilistic loss)". The Phase 1 code contains no loss model at all:

```python
def neighbours(node, nodes, rng_km):
    return [n for n in nodes if n.alive and n.nid != node.nid and dist(node, n) <= rng_km]
```

A link either exists or does not. **Impact:** every Phase 1 PDR is an
upper bound computed over perfect links; margins at maximum range (the dominant
real-world failure mode) are invisible. Flooding — which wins by path
redundancy — is the architecture most penalised by this omission in reality,
and it was not modelled at all.

### A2 — Multi-hop forwarding was instantaneous within a tick (**Critical**)

The per-tick loop walks every node in order and forwards a bundle to a neighbour
in the *same* tick; the neighbour may forward again in the same tick if it is
later in the list. With `TICK_SECONDS = 10`, a 10-hop chain can be "crossed" in
one iteration.

**Impact:** latency is systematically understated; store-and-forward (DTN) gains
nothing from its store, because there is never a period where a node must hold a
bundle; and collisions can never occur, because no two transmissions overlap.

### A3 — Ferry speed was physically implausible (**Critical for S3**)

```python
vx=rng.choice([-1, 1]) * 0.5,   # km per tick, tick = 10 s
```

0.5 km / 10 s = **50 m/s = 180 km/h**. The S3 corridor spans 10 → 90 km (an
80 km gap, crossable in ~27 min at that speed). Real ferries and rural buses run
5–15 m/s. `docs/FEASIBILITY_100KM.md` argues mobility-assisted delivery at
realistic speeds; the simulator used a speed ~4–10× too fast, which flatters
DTN.

### A4 — The star/gateway competitor was not a model, it was a lookup (**Critical**)

```python
if math.hypot(s.x - gx, s.y - gy) <= rng_km and math.hypot(d.x - gx, d.y - gy) <= rng_km:
    delivered += 1
    tx += 2
    lat.append(2 * TICK_SECONDS)
```

The star baseline had:

* **one** gateway at the bounding-box centre (no elevation, no site selection),
* no message timestamps — it delivered regardless of when the message was sent,
* no packet loss, no airtime, no duty cycle, no contention, no queue,
* no coverage outside the box centre's radius, so in S3/S4 (100 km corridors) it
  scored exactly 0.00 by construction.

**Impact:** Phase 1 reported "Star 0.03 / 0.00 / 0.00" as evidence that
centralised gateways fail. That result is an artefact of a single, badly sited,
lossless gateway. A real LoRaWAN deployment uses *multiple elevated* gateways and
10–15 km cells; when modelled that way (Phase 2) star reaches **0.55 PDR in the
dense scenario** — cheaply (44 TX, 0.35 J per delivered message). This is the
single largest unfairness in Phase 1.

### A5 — LoRa airtime, half-duplex and duty cycle were absent (**Critical**)

No SF-dependent airtime existed (`TX_ENERGY_J = 0.3` is a constant), therefore:

* a node could transmit and receive simultaneously;
* a node could transmit continuously (no 1 % duty cycle for the star baseline,
  no per-node airtime budget for the mesh);
* a 2 s SF12 frame cost the same as a 0.3 s SF7 ACK.

### A6 — No contention or collision model (**Major**)

Without A2/A5 there is nothing to collide. Consequently the Phase 1 columns
"TX" and "energy" were the only cost metrics, and *channel occupancy* — the
resource that actually limits a shared LoRa channel — was never measured.

### A7 — No terrain, elevation or vegetation model (**Major, unfixed by design**)

Range is a scalar per scenario. `docs/FEASIBILITY_100KM.md` explicitly relies on
**elevated relays** to justify 20 km spacing; the simulator cannot represent
elevation, so it can only test the flat-ground conservative case (10 km spacing).
This makes the 100 km chain result *conservative on spacing* but *optimistic on
availability*, because flat-ground links at exactly 10 km are already at the
edge. See `PHASE2_LIMITATIONS.md` §3.

### A8 — Relay failure fraction did not match the plan (**Critical, documented mismatch**)

`docs/SIMULATION_PLAN.md` line 33: "S5 — 20 % relays fail mid-run".
Code: `def fail_relays(nodes, rng, frac=0.4)` — **40 %**. Additionally:

* failures were applied in a single instant (`tick == 200`) with no recovery,
  although the plan promises "failures and recovery";
* `fail_relays()` consumed the shared RNG **mid-run**, so the random draw
  sequence diverged between architectures — the three baselines no longer
  experienced identical conditions after tick 200;
* the failed nodes were the same set for all architectures (this part was fair).

### A9 — TTL asymmetry (flooding 300 s vs DTN 3000 s) was never disclosed (**Major**)

```python
BUNDLE_TTL = 300   # ticks => 3000 s
FLOOD_TTL  = 30    # ticks =>  300 s
```

A 10× lifetime advantage for DTN is defensible (flooding has no store), but the
Phase 1 report attributed S3's DTN deliveries to store-carry-forward without
noting that the flooding baseline was structurally forbidden from holding a
packet for more than 5 minutes.

### A10 — Hop-limit asymmetry decided S4 before the run (**Critical for the 100 km claim**)

Flooding was capped at 7 hops (Meshtastic's real default/max) while the 100 km
chain needs **11 hops**. Flooding therefore *could not* deliver in S4, and Phase 1
reported "S4: ZERO-LINK 1.00 vs Flooding 0.00" without qualification.

Phase 2 re-tested this explicitly (`simulation/results_phase2_hop_sensitivity.csv`):
with a hop budget of 7 or 10, flooding still scores 0.00; with the physically
sufficient budget of 12 it reaches **0.78**, against ZERO-LINK's 1.00. So the
Phase 1 claim survives, but the *reason* is mostly hop budget, not DTN — and that
distinction was missing.

### A11 — Energy model was a per-packet constant (**Major**)

`energy = tx * TX_ENERGY_J + rx * RX_ENERGY_J` with fixed 0.3 J / 0.05 J,
independent of SF, airtime, payload or duty cycle. The star baseline counted
TX only and ignored receive energy entirely. No idle/listen energy (the dominant
term for a real LoRa receiver), no battery state, no depletion.

**Impact:** the Phase 1 claim "ZERO-LINK uses ~half the energy of flooding" is
directionally consistent with Phase 2 (+3.6× advantage) but its magnitude was
produced by a model with no physical basis.

### A12 — Metrics were incomplete and single-seed (**Critical for statistical claims**)

* one seed (42) only — no variance, no confidence interval;
* `p95_lat_s = lat[int(0.95 * len(lat))]` — a nearest-rank index with no
  interpolation and no guard for tiny samples;
* one mean latency mixed connected and store-carry deliveries (S3 reported
  mean 1155 s, hiding that most deliveries were fast and a few were DTN);
* no channel utilisation, collision rate, relay dependency, storage consumption,
  or connected-vs-DTN split;
* no CSV/JSON output; results existed only as console text.

### A13 — No storage limits or duplicate-suppression stress (**Major**)

`seen` was an unbounded set and stores were unbounded dicts, so the storage
constraint that governs DTN behaviour under load could never bind.

### A14 — Custody transfer and retransmission were documented but absent (**Major**)

`docs/ZERO_LINK_SYSTEM_DESIGN.md` describes custody ACKs and retry limits; the
Phase 1 simulator had neither, so the design's reliability mechanism was
entirely unvalidated. (Phase 2 implements both, costly in airtime — see results.)

### A15 — "Identical conditions" was violated in three ways (**Critical for fairness**)

1. **Star** ignored message timestamps and delivered on a count basis (A4).
2. **Failure injection** consumed the shared RNG mid-run (A8).
3. **Message generation**: `make_messages()` was called *inside* each run using
   the same RNG object that had already been consumed differently by each
   architecture's own logic, so the stream was not guaranteed identical.

Phase 2 generates topology, messages and the failure schedule **once per
(seed, scenario)** and deep-copies the topology for each architecture, with an
independent, architecture-indexed RNG for loss/contention only.

### Minor findings

| ID | Finding | Note |
|---|---|---|
| M1 | Ferry bounds hard-coded to 100.0 km while the corridor width was passed separately | Ferries could leave the scenario box |
| M2 | `route_cache` populated but never used to select a next hop in some paths | Dead code; "route learning" only partly exercised |
| M3 | No `--seed`/`--out` CLI; constants edited by hand | Not reproducible without editing source |
| M4 | p95 index can exceed `len-1` for small samples | Latent `IndexError`; clamped in Phase 2 |

---

## 3. Defects found in the Phase 2 rewrite itself (disclosed for transparency)

The rewrite was not correct on the first run. Each of these was found by
instrumenting the simulator, and each is fixed in the committed version:

| Defect | Symptom | Cause | Fix |
|---|---|---|---|
| Spray-and-wait TX explosion | 7 688 TX attempts, 77 successes (seed 7) | Contention retried every tick with no backoff | `backoff_until = tick + U(1,5)` after a failed TX |
| Flooding artificially crushed | T1 PDR 0.10 | One unicast TX per neighbour, counted as N transmissions, and busy receivers silently dropped the packet | Single `do_broadcast()` with per-link loss; re-queue on busy/all-lost |
| Star delivered nothing | T1 PDR 0.00 despite 23/30 messages having both ends in coverage | Downlinks were scheduled at `tick+2` while the gateway's `busy_until` was also `tick+2` (half-duplex self-block) | Downlink at `tick+4`; also `pending` entries were executed immediately instead of waiting for `t` |
| Star artificially limited | Downlinks bound to the uplink gateway | Only one gateway considered | Nearest gateway in range (matches LoRaWAN multi-gateway reception) |
| Irreproducible runs | Different results for identical `--seeds` across processes | `random.Random(seed * 1000 + hash(arch_name) % 1000)` — `hash()` of a `str` is salted per process | Architecture index used instead; verified identical output under `PYTHONHASHSEED=0` and `=999` |
| Impossible hop counts | `mean_hops = 15.2` on a 20 km topology with 5 km range | Hop counter mutated on a bundle object **shared** between nodes | Per-node `hopmap`; relay count = forwarders before destination |
| Ferry scenario impossible | T4 PDR 0.00, no DTN delivery | 80 km gap at realistic speed cannot be crossed within 1 800 s | Corridor 0–10 / 30–40 km (20 km gap, ~1 330 s at 15 m/s) |

The last row is a **scenario design** fix, not a modelling fix: it keeps the
ferry speed physical and shortens the gap instead.

---

## 4. What changed in the simulator (summary)

| Capability | Phase 1 | Phase 2 |
|---|---|---|
| Packet loss | none | per-link probabilistic, distance-dependent edge loss (approximation) |
| Airtime | constant energy | SF-dependent airtime, per-node busy window (half-duplex) |
| Contention | none | per-tick TX log + CSMA-style random backoff (approximation) |
| Duty cycle | none | 1 % airtime budget enforced for the star baseline |
| Multi-hop timing | same tick | scheduled, airtime-gated, queued |
| Batteries | none | 10 Wh budget, TX/RX draw, node dies at 0 J |
| Storage | unbounded | 50-bundle cap, oldest-drop, counted |
| Custody ACK | none | ACK TX after successful hop (costs airtime) |
| Retries | none | max 2, scheduled 2 s later |
| TTL | fixed per arch | DTN 1500 s, flooding 60 s (both disclosed) |
| Duplicate suppression | set, unbounded | capped seen-cache + per-node hop map |
| Ferry speed | 50 m/s | 15 m/s |
| Failures | instant, 40 %, no recovery | scheduled, 40 % (plan corrected to match), no recovery (documented) |
| Seeds | 1 | 5 primary + 10 robustness + 10 for the 100 km sweep |
| Outputs | console | CSV + JSON (raw and aggregate), logs |
| Statistics | single value | mean, 95 % CI, median, p95, per-scenario split |
| Metrics | PDR, latency, TX, energy | + channel utilisation, collision rate, relay dependency, mean hops, storage, connected/DTN split |

---

## 5. Verification performed

```bash
# reproducibility (identical output under different hash salts)
PYTHONHASHSEED=0     python3 simulation/zero_link_sim.py --seeds 42 --out /tmp/a.csv --json /tmp/a.json
PYTHONHASHSEED=999   python3 simulation/zero_link_sim.py --seeds 42 --out /tmp/b.csv --json /tmp/b.json
diff /tmp/a.csv /tmp/b.csv          # no output = reproducible

# primary validation (5 seeds)
python3 simulation/zero_link_sim.py --seeds 42,7,123,2024,99 \
    --out simulation/results_phase2.csv --json simulation/results_phase2.json

# robustness (10 seeds)
python3 simulation/zero_link_sim.py --seeds 42,7,123,2024,99,1,2,3,55,777 \
    --out simulation/archive/results_phase2_10seed_robustness.csv \
    --json simulation/archive/results_phase2_10seed_robustness.json

# 100 km relay spacing x availability study (10 seeds)
python3 simulation/zero_link_sim.py --sweep-100km --seeds 42,7,123,2024,99,1,2,3,55,777

# hop-limit fairness check on the 100 km chain
python3 simulation/zero_link_sim.py --hop-sensitivity --seeds 42,7,123,2024,99
```

**Sanity check that the model behaves like theory:** in the 100 km sweep, delivery
probability should follow `a^n` for relay availability `a` and `n` relays.
Measured vs predicted at `a = 0.9`: 4 relays/20 km → 0.60 vs 0.66 predicted;
9 relays/10 km → 0.20 vs 0.39; 19 relays/5 km → 0.10 vs 0.14. The model tracks
theory in direction and order of magnitude, and is conservative at mid-range
spacing (tight link budgets plus collisions), which is the expected direction
for a lossy, half-duplex network.

---

## 6. Phase 1 results — validity verdict

| Phase 1 claim | Verdict after audit |
|---|---|
| "Direct handheld 100 km is infeasible" | **Holds** (analytic: radio horizon, FSPL — not a simulator claim) |
| "Multi-hop 100 km is feasible with 7–20 relays" | **Holds only with ~100 % relay availability**; at 95 % availability, PDR falls to 0.40–0.90 depending on spacing (Phase 2 sweep) |
| "ZERO-LINK beats flooding on PDR in dense networks (0.90 vs 0.93)" | **Not supported as stated** — Phase 1 flooding was actually *ahead*; Phase 2 gives ZERO-LINK 0.90 vs 0.83 with overlapping CIs → **no significant PDR difference** |
| "ZERO-LINK uses ~half the energy of flooding" | **Holds and strengthens**: 3.6× less energy per delivered message, 3.2× less channel occupancy |
| "Star fails (0.03)" | **Retracted** — an artefact of one badly sited, lossless gateway. Fair model: 0.55 PDR in the dense case |
| "DTN essential in partitioned networks" | **Holds**, but only with mobility: without a ferry, DTN ≈ flooding (0.29 vs 0.29) |
| "Simulation validates the architecture" | **Overstated in Phase 1** — it validated an unimplemented idealisation |

---

## 7. Unresolved audit items

* Terrain/elevation modelling is absent (A7). The 20 km elevated-relay spacing
  used in `FEASIBILITY_100KM.md` remains **analytically** argued, not simulated.
* The collision model is overlap-based and kills only the later packet
  (real collisions destroy both). Labelled an approximation.
* No capture effect, no fading, no adjacent-channel interference, no duty-cycle
  enforcement for the mesh architectures (only the star baseline).
* Node failure has no recovery path, so "recovery" in the design docs is untested.
* All energy figures are radio-only; MCU sleep/processing energy is excluded.

These are carried into `docs/PHASE2_LIMITATIONS.md`.
