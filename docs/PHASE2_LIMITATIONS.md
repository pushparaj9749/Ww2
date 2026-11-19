# Phase 2 — Limitations

This document states what the Phase 2 simulator **does not** model, which claims
therefore cannot be supported, and what evidence would be required to promote
each claim from "simulated" to "validated".

**Read this before quoting any number from `PHASE2_VALIDATION_RESULTS.md`.**

---

## 1. Standing disclaimer

* These are **software simulation results**. No hardware was built, bought or
  measured. Nothing here is field-tested performance.
* "100 km delivery" always means **100 km delivered over N relays at a stated
  spacing and availability** — never a direct handheld link.
* A simulated 1.00 PDR is a property of a model, not a service guarantee.

---

## 2. Modelling assumptions (and how good each one is)

| # | Assumption | Implementation | Fidelity |
|---|---|---|---|
| L1 | Link success is probabilistic and distance-dependent | `p = (1 - loss) × (1 − 0.30·(d/r)⁴)`; hard cut-off beyond range | **Approximation.** No fading (Rayleigh/Rician), no shadowing, no diffraction, no terrain, no antenna gain/pattern, no Fresnel-zone computation. The quartic edge term is a stand-in for "links get worse near maximum range". |
| L2 | LoRa airtime | SF7 0.4 s, SF9 0.9 s, SF12 2.0 s for ~100 B at BW125 | **Approximation.** Real airtime depends on exact payload, header mode, coding rate, preamble, BW and low-data-rate optimisation. Values are in the right order of magnitude (SF12/125 kHz ≈ 1–2 s for small payloads). |
| L3 | Half-duplex | `busy_until = tick + ceil(airtime)` blocks TX/RX | **Sound simplification.** Ignores TX→RX and RX→TX turnaround (~ms), and the fact that a node cannot decode a packet it began receiving mid-frame. |
| L4 | Collisions | Per-tick TX log; a receiver already targeted this tick fails | **Crude approximation.** Real collisions destroy *all* overlapping frames (only the later one dies here), and there is no capture effect, no preamble detection, no SNR-based capture. Collision counts should be read as an ordering, not a probability. |
| L5 | Channel access | Random 1–5 s backoff after a failed TX; no carrier sense | **Approximation.** Real LoRa uses CAD/LBT (Reticulum) or ALOHA-style access (Meshtastic default). No hidden-terminal modelling beyond the collision log. |
| L6 | Duty cycle | Only the star baseline is capped at 1 % (36 s/h); mesh architectures uncapped | **Deliberate.** 1 % is the EU868 rule; India's 865–867 MHz band has no equivalent published duty-cycle limit, so capping the mesh would be inventing a regulation. This *favours* the mesh architectures and must be stated. |
| L7 | Propagation delay | Ignored (negligible: 0.33 ms per 100 km) | Sound. |
| L8 | Multi-hop timing | Forwarding is scheduled per tick with airtime gating | Good, but **1 s granularity** rounds sub-second inter-hop gaps. |
| L9 | Battery | 10 Wh per node; 0.1 W TX, 0.02 W RX; node dies at 0 J | **Approximation.** No MCU/radio sleep current, no GPS, no display, no solar, no temperature effects. Real LoRa receivers drawing ~10 mA continuously at 3.7 V would drain a 10 Wh cell in ~11 days — idle energy is the dominant term and is **excluded**. All energy numbers are therefore *lower bounds on the radio-only cost*. |
| L10 | Storage | 50 bundles/node, oldest dropped, counted | Reasonable, but `STORE_MAX` was **never reached** in any scenario (0 drops across all runs), so storage limits are untested. |
| L11 | Duplicate suppression | Capped seen-cache (500), per-node hop map | Good. The cap is never reached either. |
| L12 | Custody ACK | One ACK TX per successfully received hop (0.3 s) | **Approximation.** Real custody transfer implies persistent storage, ACK retransmission and timeout policy; here an ACK is best-effort and never retried. |
| L13 | Retries | Max 2, scheduled +2 s, per bundle | Reasonable for an initial design; not tuned. |
| L14 | TTL | DTN 1 500 s, flooding 60 s, star n/a | Values chosen to reflect "flooding has no store". They shape T3/T4 outcomes and are disclosed rather than justified empirically. |
| L15 | Mobility | Ferries move at 15 m/s along a 1-D corridor, bouncing at both ends | **Approximation.** No real ferry timetable, no dwell time, no route variation, no correlation between ferry position and message timing. |
| L16 | Failures | 40 % of relays die at t ∈ [300, 600] s; `alive=False` permanently | **Partial.** No recovery, no intermittent links, no correlated failure (e.g. a power cut affecting a village), no gateway failure. |
| L17 | Terrain / elevation | **Not modelled at all** | **Major gap.** Range is a scalar. The 20 km elevated-relay spacing in `FEASIBILITY_100KM.md` cannot be tested here. |
| L18 | Interference | No external interferers, no adjacent-channel or co-channel users beyond the simulated nodes | **Major gap** for a shared 865–867 MHz band. |
| L19 | Traffic | 30 messages, uniform random source/destination among endpoints, 1 message per node per 900 s | **Not representative** of real messaging load (heavy-tailed, clustered, group traffic). Results are per-message means on a very light load. |
| L20 | Payload/crypto | Fixed ~100 B, no encryption, no signatures, no headers | DTN bundles with real crypto have larger payloads → more airtime → more collisions. Unquantified. |

---

## 3. Structural threats to validity

### 3.1 Single-channel abstraction
All nodes share one channel with one range parameter. Real deployments face
frequency planning, channel switching per region (IN865 channels
865.0625/865.4025/865.985 MHz), and sub-band power limits. None of this is
represented.

### 3.2 Range as a scalar
Folding terrain, antenna height, vegetation and weather into a single radius is
the largest physical simplification. Because the design's central feasibility
argument rests on **elevated relays reaching 20 km**, the simulator can only
demonstrate the conservative flat-ground case (10 km spacing, links at the edge).

### 3.3 Small message counts, light load
30 messages per 1 800 s across 12–80 nodes is far below any realistic message
rate. Congestion was tested by raising node count (T7), not traffic. A real
congestion test would keep density fixed and raise offered load by 10–100×.

### 3.4 Seed count
5 seeds (primary) and 10 seeds (robustness and the 100 km sweep). Confidence
intervals of ±0.10–0.30 on PDR mean that **differences below ~0.10 are not
resolvable**, and several reported differences (e.g. 0.90 vs 0.83) fall inside
that band. No significance test beyond CI overlap was performed.

### 3.5 Baselines are credible but not optimal
* **Flooding** is capped at 7 hops (Meshtastic's real maximum) and 60 s TTL.
  §4 of the results doc shows this decides T5 near-entirely; a 12-hop budget
  raises flooding from 0.00 to 0.78.
* **Star** is given 4 gateways placed at fixed corridor positions, no elevation
  advantage, and no backhaul latency. Real LoRaWAN gateways are typically on
  towers (10–15 km cells) — a fairer comparison might give star *better* range
  than handhelds, which this simulator does not.
* **Spray-and-wait** uses binary spray L=4 with no utility-based forwarding.
  Stronger DTN variants (Prophet, encounter-based metrics, spray-and-focus) would
  perform better and were not implemented.
* **ZERO-LINK** was tuned by its own author (copy budget 6, retries 2, greedy +
  epidemic hybrid). It is the most "designed" of the four, which is a
  home-advantage that parameter sweeps have not removed.

### 3.6 The comparison is not blind
The same simulator, written by the same effort, implements both the proposed
architecture and its competitors. Mitigations applied: identical topology,
messages, failures, loss and duration per seed; independent RNG per architecture;
competitor bugs fixed rather than left in (star scheduling, flooding broadcast);
the hop-limit artefact explicitly measured and disclosed.

---

## 4. Claim-by-claim confidence

| Claim | Evidence | Confidence |
|---|---|---|
| Direct handheld 100 km is infeasible | Analytic (horizon, FSPL, Fresnel) from Phase 1 | **High** (physics, not simulation) |
| 100 km multi-hop delivery is possible with 9–10 relays at 10 km spacing | Simulation, 5+10 seeds, flat ground, links at range edge | **Medium** — depends on L1/L17; needs a link-budget field test |
| 100 km delivery at 20 km spacing needs elevated relays | Analytic only; not simulated | **Low–medium** — unvalidated by this simulator |
| Availability, not spacing, dominates end-to-end PDR | Simulation across 25 spacing×availability cells; matches `a^n` theory | **High** (structural result, not sensitive to L1) |
| ZERO-LINK is more energy-efficient than flooding | 3.4–3.6× across T1/T7/T8 | **Medium–high** — direction robust; magnitude depends on L2/L9 |
| ZERO-LINK delivers more than flooding | 0.90 vs 0.83 (CIs overlap) | **Low** — not statistically significant |
| ZERO-LINK beats a star gateway | Only outside star's coverage; star wins on cost/latency inside it | **High** (clear mechanism) |
| Store-carry-forward helps in partitions | Only with mobility: 0.37 vs 0.29 without ferry; 1.6 DTN deliveries per run | **Medium** — depends entirely on L15 |
| The design works in India's 865–867 MHz band | Not simulated; regulatory research only | **Unproven** — WPC ETA, power limits, 1 W vs 4 W conflict unresolved |

---

## 5. What would be required to validate each claim

| To validate | Experiment | Cost/effort |
|---|---|---|
| Link budget at 5/10/20 km | 2-node LoRa point-to-point RSSI/PER sweep, ground vs elevated, over ≥1 week | 2 modules + 2 sites; low cost |
| Terrain effects | Same, across 3–4 Indian terrains (plains, plateau, forest edge) | Field campaign |
| 100 km chain | Deploy 9–10 relays on a real corridor with power/logging | Significant, requires permissions |
| Availability impact | 4-week uptime logging of relay nodes | Passive logging |
| Congestion/collisions | 20–80 node testbed with synthetic load | Lab-scale |
| Energy | Power-profiling a real node (TX, RX, idle, sleep) | Bench measurement |
| Regulatory | Confirm GSR text for 865–867 MHz power limits; obtain ETA path | Documentary/legal |
| Comparative performance | Re-implement Reticulum/MeshCore behaviour as baselines, or run them on the same testbed | Software + hardware |

---

## 6. Known simulator defects that remain

* Collisions kill only the later packet (L4).
* No capture effect, no CAD/LBT.
* Mesh architectures have no duty-cycle cap (L6) — favours them.
* Star gateway never fails; ZERO-LINK relays do — favours star.
* Storage and seen-cache limits never bind (L10/L11) — DTN behaviour under
  memory pressure is untested.
* The 1 s tick quantises forwarding (L8).
* `STORE_MAX` scenario needs ≥ several hundred messages to be meaningful.

These are acceptable for an architectural comparison but must be closed before
any performance claim is made about a real deployment.
