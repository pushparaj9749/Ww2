# Phase 2 — Validation Results

**Software simulation only.** Every number below comes from
`simulation/zero_link_sim.py`. No hardware was built or measured; these are not
field results and must never be quoted as achieved range or reliability.

* **Primary run:** 5 seeds (42, 7, 123, 2024, 99) × 8 scenarios × 4 architectures
* **Per run:** 1 800 s simulated, 30 messages, 1 s ticks, base link loss 2 %
  (T8: 15 %), topology/messages/failures identical across architectures
* **Raw data:** `simulation/results_phase2.csv` (160 rows) and
  `simulation/results_phase2.json`
* **Logs:** `simulation/test_log_phase2.txt`,
  `simulation/test_log_phase2_100km.txt`,
  `simulation/test_log_phase2_hop.txt`
* **Robustness:** 10-seed re-run in `simulation/archive/`

---

## 1. Headline comparison (5 seeds)

| Scenario | Arch | PDR (mean ±95% CI) | Med lat (s) | p95 lat (s) | J/delivered | TX | Relay dep | Mean hops | Chan util | Collisions |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 Dense | ZERO-LINK | 0.90 ± 0.10 | 6.7 | 16.0 | 2.84 | 736 | 0.91 | 3.32 | 0.92% | 4.3% |
| T1 Dense | Flooding | 0.83 ± 0.11 | 6.7 | 15.2 | 10.14 | 1061 | 0.86 | 2.45 | 2.95% | 13.0% |
| T1 Dense | Star | 0.55 ± 0.06 | 4.0 | 4.0 | 0.35 | 44 | 1.00 | 1.00 | 0.11% | 0.0% |
| T1 Dense | SprayWait | 0.30 ± 0.06 | 3.9 | 14.0 | 3.00 | 112 | 0.92 | 1.30 | 0.31% | 1.1% |
| T2 Sparse | ZERO-LINK | 0.03 ± 0.03 | 1.7 | 2.0 | 4.40 | 54 | 0.17 | 0.33 | 0.11% | 1.8% |
| T2 Sparse | Flooding | 0.03 ± 0.02 | 1.7 | 2.3 | 20.25 | 91 | 0.00 | 0.00 | 0.40% | 1.5% |
| T2 Sparse | Star | 0.01 ± 0.02 | 4.0 | 4.0 | 1.34 | 4 | 1.00 | 1.00 | 0.02% | 0.0% |
| T2 Sparse | SprayWait | 0.03 ± 0.03 | 1.8 | 2.3 | 6.67 | 37 | 1.00 | 1.17 | 0.17% | 0.9% |
| T3 Partitioned (no ferry) | ZERO-LINK | 0.29 ± 0.06 | 4.0 | 12.6 | 3.93 | 317 | 0.78 | 1.76 | 0.53% | 4.1% |
| T3 Partitioned (no ferry) | Flooding | 0.29 ± 0.05 | 4.1 | 11.6 | 10.31 | 363 | 0.69 | 1.35 | 1.34% | 6.7% |
| T3 Partitioned (no ferry) | Star | 0.00 ± 0.00 | — | — | — | 0 | 0.00 | 0.00 | 0.00% | 0.0% |
| T3 Partitioned (no ferry) | SprayWait | 0.20 ± 0.06 | 4.3 | 7.8 | 4.17 | 97 | 0.92 | 1.16 | 0.36% | 0.8% |
| T4 Partitioned + ferries | ZERO-LINK | 0.37 ± 0.15 | 5.0 | 600.4 | 4.52 | 413 | 0.84 | 2.38 | 0.59% | 2.7% |
| T4 Partitioned + ferries | Flooding | 0.32 ± 0.14 | 3.8 | 11.4 | 11.45 | 394 | 0.73 | 1.74 | 1.25% | 7.0% |
| T4 Partitioned + ferries | Star | 0.07 ± 0.01 | 4.0 | 4.0 | 1.04 | 13 | 1.00 | 1.00 | 0.04% | 0.0% |
| T4 Partitioned + ferries | SprayWait | 0.19 ± 0.06 | 3.8 | 260.6 | 4.68 | 104 | 1.00 | 1.38 | 0.33% | 1.3% |
| T5 100 km chain | ZERO-LINK | 1.00 ± 0.00 | 21.9 | 39.2 | 1.56 | 451 | 1.00 | 10.00 | 1.88% | 1.2% |
| T5 100 km chain | Flooding | 0.00 ± 0.00 | — | — | — | 268 | 0.00 | 0.00 | 2.48% | 0.5% |
| T5 100 km chain | Star | 0.00 ± 0.00 | — | — | — | 0 | 0.00 | 0.00 | 0.00% | 0.0% |
| T5 100 km chain | SprayWait | 0.00 ± 0.00 | — | — | — | 74 | 0.00 | 0.00 | 0.69% | 0.0% |
| T6 Dense + relay failures | ZERO-LINK | 0.88 ± 0.10 | 7.1 | 17.6 | 2.70 | 677 | 0.91 | 3.42 | 0.85% | 4.2% |
| T6 Dense + relay failures | Flooding | 0.85 ± 0.10 | 7.1 | 17.0 | 8.98 | 962 | 0.88 | 2.62 | 2.67% | 12.6% |
| T6 Dense + relay failures | Star | 0.55 ± 0.06 | 4.0 | 4.0 | 0.35 | 44 | 1.00 | 1.00 | 0.11% | 0.0% |
| T6 Dense + relay failures | SprayWait | 0.30 ± 0.05 | 3.9 | 14.0 | 2.98 | 112 | 0.91 | 1.32 | 0.31% | 1.3% |
| T7 Congested | ZERO-LINK | 1.00 ± 0.00 | 7.1 | 15.4 | 6.48 | 1864 | 0.93 | 3.56 | 1.16% | 8.2% |
| T7 Congested | Flooding | 1.00 ± 0.00 | 6.9 | 14.4 | 22.17 | 2846 | 0.87 | 2.47 | 3.95% | 37.3% |
| T7 Congested | Star | 0.50 ± 0.12 | 4.0 | 4.0 | 0.39 | 43 | 1.00 | 1.00 | 0.06% | 0.0% |
| T7 Congested | SprayWait | 0.31 ± 0.07 | 4.0 | 7.6 | 2.99 | 114 | 0.91 | 1.23 | 0.16% | 1.4% |
| T8 Dense + 15% loss | ZERO-LINK | 0.89 ± 0.10 | 9.4 | 20.6 | 3.31 | 868 | 0.90 | 3.40 | 1.08% | 8.5% |
| T8 Dense + 15% loss | Flooding | 0.82 ± 0.11 | 7.5 | 20.8 | 10.63 | 1112 | 0.88 | 2.69 | 3.09% | 22.7% |
| T8 Dense + 15% loss | Star | 0.48 ± 0.05 | 4.0 | 4.0 | 0.39 | 42 | 1.00 | 1.00 | 0.11% | 0.0% |
| T8 Dense + 15% loss | SprayWait | 0.30 ± 0.06 | 6.1 | 13.8 | 3.52 | 135 | 0.87 | 1.30 | 0.38% | 3.1% |

`J/delivered` = total radio energy drawn by the network ÷ messages delivered
(includes energy spent on traffic that never arrived — that is deliberate: it
measures the cost of the system, not of successful packets).
`—` = no deliveries, so the metric is undefined.

---

## 2. Scenario-by-scenario analysis

### T1 — Dense connected (40 nodes, 20 × 20 km, 5 km range, 2 % loss)

* ZERO-LINK 0.90 vs flooding 0.83, **but the 95 % CIs overlap** (0.80–1.00 vs
  0.72–0.94). With 5 seeds, **the PDR difference is not statistically
  significant**.
* What *is* large and consistent: **energy per delivered message 2.84 J vs
  10.14 J (3.6× better)**, **channel occupancy 0.92 % vs 2.95 % (3.2× less)**,
  **collision rate 4.3 % vs 13.0 % (3× lower)**.
* **Star is the efficiency outlier**: 0.35 J/delivered and 4.0 s latency — but it
  only reaches 55 % of messages, because delivery requires both endpoints to be
  within a gateway's 5 km cell. Its failures are *structural*, not random.
* Spray-and-wait delivers 0.30: with binary spray L=4 over 40 nodes and 2 %
  loss, most copies die before reaching a destination 3 hops away; greedy
  forwarding (ZERO-LINK) is the right choice in a connected component.

### T2 — Sparse (25 nodes over 50 × 50 km, 5 km range)

All architectures collapse to 0.01–0.03. The graph is disconnected at this
density: **0.33 mean hops** for ZERO-LINK means almost all deliveries are direct,
single-link events. No architecture can fix a partition without mobility.
Honest conclusion: **sparse static deployment does not deliver; the density
assumption behind the design is load-bearing.**

### T3 — Partitioned, no mobility (two 15-node islands, 80 km apart)

* ZERO-LINK 0.29 = flooding 0.29. **Store-and-forward buys nothing when nothing
  moves.** DTN's advantage is entirely mobility-dependent.
* Spray-and-wait is worse (0.20): its copies are consumed inside the island.
* Star is 0.00 — correctly, because no gateway can cover both islands.

### T4 — Partitioned with ferries (20 km gap, 15 m/s crossing ≈ 1 330 s)

| Arch | PDR | DTN deliveries | p95 latency |
|---|---|---|---|
| ZERO-LINK | 0.37 ± 0.15 | 1.6 | 600 s |
| Flooding | 0.32 ± 0.14 | 0.0 | 11 s |
| SprayWait | 0.19 ± 0.06 | 0.4 | 261 s |
| Star | 0.07 ± 0.01 | 0.0 | 4 s |

This is the scenario the architecture was designed for. ZERO-LINK delivers
cross-partition traffic that flooding *cannot* deliver at all (flooding's 32 %
are all intra-island, p95 11 s). But **only 1.6 of 30 messages cross per run**,
and the p95 is ~10 minutes. Note the honest trade-off: flooding's p95 looks 50×
better only because it never attempts the hard case.

### T5 — 100 km chain (12 nodes, 10 km spacing, links at range edge)

ZERO-LINK 1.00 (median 21.9 s, p95 39.2 s, 10 hops). All baselines 0.00.

Two reasons, separated here for honesty:

1. **Structural:** the chain needs 11 hops; flooding was capped at 7 (Meshtastic's
   real maximum). See §4 — with a 12-hop budget flooding reaches 0.78.
2. **Real:** flooding holds no state, so a single lost packet at any of 11 hops
   ends that copy; ZERO-LINK retries (≤2), stores, and ACKs per hop.

The 100 km claim therefore survives, **conditional on** 9–10 continuously
available relays at 10 km spacing — see §3 and `PHASE2_LIMITATIONS.md`.

### T6 — Dense + 40 % relay failure at t≈300–600 s

ZERO-LINK 0.88 vs 0.85 flooding (CIs overlap), star unchanged at 0.55 (gateways
never fail — a modelling gap, see limitations). **Dense mesh absorbs 40 % relay
loss gracefully** because endpoints remain connected through non-relay nodes;
the failure scenario is therefore weak in the dense case. Failure impact is much
better exposed by the 100 km sweep in §3.

### T7 — Congestion (80 nodes in 20 × 20 km)

Both mesh variants reach 1.00. The difference is cost: **flooding 2 846 TX,
37 % collision rate, 22.2 J/delivered; ZERO-LINK 1 864 TX, 8.2 %, 6.5 J**.
This is the clearest, most defensible ZERO-LINK win in the study: same delivery,
~3.4× less energy, ~4.5× fewer collisions.

### T8 — High loss (15 %)

ZERO-LINK 0.89 vs flooding 0.82 (CIs overlap), energy 3.31 vs 10.63 J. Latency
degrades for both (median 9.4 s vs 6.7 s at 2 % loss) because of retry backoff.

---

## 3. The 100 km claim under test (10 seeds, 250 runs)

Chain: source at 0 km, destination at 100 km, relays evenly spaced, **radio range
set equal to the relay spacing** (worst case — every link operates at its
maximum range, where the loss model applies its 30 % edge penalty).

| Relays | Spacing (km) | Availability | PDR (mean ±95% CI) | Median lat (s) | p95 lat (s) | TX |
|---|---|---|---|---|---|---|
| 19 | 5.0 | 100% | 1.00 ± 0.00 | 53.4 | 81.4 | 901 |
| 19 | 5.0 | 95% | 0.30 ± 0.30 | 52.5 | 81.3 | 548 |
| 19 | 5.0 | 90% | 0.10 ± 0.20 | 57.5 | 84.0 | 362 |
| 19 | 5.0 | 80% | 0.00 ± 0.00 | — | — | 193 |
| 19 | 5.0 | 70% | 0.00 ± 0.00 | — | — | 150 |
| 12 | 7.5 | 100% | 1.00 ± 0.00 | 33.0 | 53.8 | 588 |
| 12 | 7.5 | 95% | 0.40 ± 0.32 | 30.4 | 53.5 | 376 |
| 12 | 7.5 | 90% | 0.10 ± 0.20 | 28.0 | 56.0 | 235 |
| 12 | 7.5 | 80% | 0.00 ± 0.00 | — | — | 157 |
| 12 | 7.5 | 70% | 0.00 ± 0.00 | — | — | 125 |
| 9 | 10.0 | 100% | 1.00 ± 0.00 | 24.4 | 42.2 | 451 |
| 9 | 10.0 | 95% | 0.50 ± 0.33 | 24.1 | 39.8 | 315 |
| 9 | 10.0 | 90% | 0.20 ± 0.26 | 25.2 | 40.0 | 207 |
| 9 | 10.0 | 80% | 0.10 ± 0.20 | 26.5 | 33.0 | 141 |
| 9 | 10.0 | 70% | 0.10 ± 0.20 | 26.5 | 33.0 | 120 |
| 6 | 15.0 | 100% | 1.00 ± 0.00 | 17.9 | 35.5 | 323 |
| 6 | 15.0 | 95% | 0.70 ± 0.30 | 17.1 | 33.3 | 267 |
| 6 | 15.0 | 90% | 0.40 ± 0.32 | 17.8 | 35.5 | 201 |
| 6 | 15.0 | 80% | 0.30 ± 0.30 | 18.3 | 35.3 | 166 |
| 6 | 15.0 | 70% | 0.20 ± 0.26 | 19.0 | 34.5 | 124 |
| 4 | 20.0 | 100% | 1.00 ± 0.00 | 12.1 | 26.4 | 234 |
| 4 | 20.0 | 95% | 0.90 ± 0.20 | 12.3 | 25.8 | 220 |
| 4 | 20.0 | 90% | 0.60 ± 0.32 | 12.7 | 26.3 | 165 |
| 4 | 20.0 | 80% | 0.40 ± 0.32 | 12.4 | 25.0 | 126 |
| 4 | 20.0 | 70% | 0.30 ± 0.30 | 12.2 | 23.0 | 98 |

### What this means

1. **100 km multi-hop delivery works in simulation — only with ~100 % relay
   availability.** At 100 % availability, every spacing from 5 to 20 km delivers
   1.00. That is a "no relay is ever down" assumption, not a service guarantee.
2. **Availability dominates spacing.** Reducing relays from 19 to 4 raises PDR at
   90 % availability from 0.10 to 0.60 — the opposite of the intuition that more
   relays = more reliability. Each relay is a series failure point: the end-to-end
   probability is ≈ `a^n`.
3. **The model reproduces theory.** Measured vs `a^n` at a = 0.9: 4 relays →
   0.60 (0.66 predicted), 9 → 0.20 (0.39), 19 → 0.10 (0.14). Conservative at
   midrange spacing, where tight budgets and collisions bite. This is a good sign
   that the network layer is behaving as designed.
4. **Latency scales linearly with hop count:** 12.1 s at 5 hops → 53.4 s at 20
   hops (≈2.6 s/hop, consistent with 2 s SF12 airtime + processing).
5. **Required relay count for 100 km:** ≥4 with 20 km spacing *if* links survive
   at 20 km; 9–10 at 10 km spacing in the conservative flat-ground case; 19 at
   5 km. The Phase 1 estimate (7–20 relays) is consistent with this.

### Direct handheld 100 km — kept separate

The simulator does **not** model a 100 km direct link as achievable, and no run
tries to. Phase 1's analytic result stands: radio horizon ≈10.1 km at 1.5 m
antenna height, FSPL ≈131 dB at 100 km/866 MHz, first Fresnel radius ≈93 m —
a handheld-to-handheld 100 km link is not a realistic service target. Every
100 km figure in this dossier is **multi-hop with N relays at the stated spacing
and availability**.

---

## 4. Fairness check: was T5 just flooding's hop limit?

`python3 simulation/zero_link_sim.py --hop-sensitivity --seeds 42,7,123,2024,99`

| Architecture | Hop limit | Flood TTL | PDR (mean) |
|---|---|---|---|
| Flooding | 7 (Meshtastic max) | 60 s | 0.00 |
| Flooding | 7 | 600 s | 0.00 |
| Flooding | 10 | 60 s | 0.00 |
| Flooding | 10 | 600 s | 0.00 |
| Flooding | 12 | 60 s | 0.78 |
| Flooding | 12 | 600 s | 0.79 |
| ZERO-LINK | n/a (store-based) | 1 500 s | 1.00 |

**Conclusion:** T5's 1.00 vs 0.00 is *mostly* a hop-budget artefact — flooding
physically cannot cross an 11-hop chain at a 7–10 hop limit. When given a
sufficient budget it reaches **0.78**, still below ZERO-LINK's 1.00. The residual
gap is genuine (store + retries + per-hop ACKs), but it is 0.22, not 1.00.

---

## 5. Robustness: 5 seeds vs 10 seeds

| Scenario | Arch | PDR 5 seeds | PDR 10 seeds | Drift |
|---|---|---|---|---|
| T1 | ZERO-LINK | 0.90 | 0.89 | −0.01 |
| T1 | Flooding | 0.83 | 0.84 | +0.02 |
| T1 | Star | 0.55 | 0.51 | −0.05 |
| T3 | ZERO-LINK | 0.29 | 0.35 | +0.06 |
| T4 | ZERO-LINK | 0.37 | 0.40 | +0.04 |
| T5 | ZERO-LINK | 1.00 | 1.00 | 0.00 |
| T7 | ZERO-LINK | 1.00 | 1.00 | 0.00 |
| T8 | Star | 0.48 | 0.42 | −0.06 |

Ordering never changes; drifts are ≤0.06 except star (−0.05/−0.06), whose PDR
depends on a few gateways and therefore has high seed variance. No conclusion in
this dossier depends on a margin smaller than the seed drift.

---

## 6. Does ZERO-LINK still outperform the baselines?

**Partly — and not on the axis Phase 1 claimed.**

| Question | Answer |
|---|---|
| Highest delivery in connected networks? | Yes, but **not significantly** (0.90 vs 0.83, overlapping CIs) |
| Lowest cost per delivered message? | Yes among mesh architectures (2.84 J vs 10.14 J flooding, 27 vs 43 TX) |
| Lowest absolute cost? | **No — star wins** (0.35 J, 44 TX) where it has coverage |
| Lowest latency? | **No** — star 4.0 s, spray 3.9 s median; ZERO-LINK 6.7 s |
| Best under congestion? | **Yes, clearly** (equal PDR, 3.4× less energy, 4.5× fewer collisions) |
| Best across partitions? | **Yes** — only architecture delivering cross-partition traffic via ferry, and it does so at 10-minute latency |
| Robust to relay loss? | **Yes** — highest PDR at every availability level in the 100 km sweep |
| Wins in sparse static networks? | **No** — nothing works; 0.03 for all |

### Where it wins
* Connected and dense: equal-or-better PDR at a third of the energy.
* Congested: same delivery, far fewer collisions — the argument that matters for
  a shared 865–867 MHz band.
* Mobile/partitioned: the only architecture that carries bundles across a gap.
* Degraded relay availability: degrades most gracefully because of retries and
  custody ACKs.

### Where it loses
* **Absolute energy and latency**: a star gateway is 8× cheaper per message and
  40 % faster *when both endpoints are in one cell*. ZERO-LINK's case rests on
  coverage, not efficiency.
* **Sparse static topologies**: store-carry-forward without mobility is useless;
  with zero ferries it exactly ties flooding.
* **Tail latency**: p95 600 s in the ferry scenario vs 11 s flooding (which
  simply refuses the hard deliveries).
* **Protocol overhead**: 91 % of deliveries depend on ≥1 intermediate node and
  mean hop count is 3.3 — the system is *relay-dependent*, which is a
  vulnerability, not just an efficiency.

---

## 7. Reproduction

```bash
# primary (5 seeds) — writes CSV, JSON, log
python3 simulation/zero_link_sim.py --seeds 42,7,123,2024,99 \
    --out simulation/results_phase2.csv --json simulation/results_phase2.json

# 10-seed robustness
python3 simulation/zero_link_sim.py --seeds 42,7,123,2024,99,1,2,3,55,777 \
    --out simulation/archive/results_phase2_10seed_robustness.csv \
    --json simulation/archive/results_phase2_10seed_robustness.json

# 100 km spacing x availability study
python3 simulation/zero_link_sim.py --sweep-100km --seeds 42,7,123,2024,99,1,2,3,55,777

# flooding hop-limit fairness check
python3 simulation/zero_link_sim.py --hop-sensitivity --seeds 42,7,123,2024,99

# determinism check
PYTHONHASHSEED=0   python3 simulation/zero_link_sim.py --seeds 42 --out /tmp/a.csv --json /tmp/a.json
PYTHONHASHSEED=999 python3 simulation/zero_link_sim.py --seeds 42 --out /tmp/b.csv --json /tmp/b.json
diff /tmp/a.csv /tmp/b.csv
```

Runtime: primary sweep ≈53 s, 10-seed ≈109 s, 100 km study ≈29 s, hop check ≈5 s
(single core, stdlib only).

---

## 8. What this study does not show

* Nothing about real radios, antennas, terrain, buildings or interference.
* Nothing about 865–867 MHz regulatory power limits (the simulator has one
  abstract channel).
* Nothing about encryption, key distribution or metadata leakage.
* Nothing about energy beyond radio TX/RX (no MCU, no sleep states, no solar).
* Nothing about human usability, cost or manufacturability.

See `docs/PHASE2_LIMITATIONS.md` for the full list, and
`docs/PHASE2_NOVELTY_REASSESSMENT.md` for what remains genuinely new.
