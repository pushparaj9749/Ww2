# Phase 2 — Novelty Reassessment

This document re-tests the Phase 1 novelty claim against prior art **after** the
simulation results were obtained. Phase 1 rated the architecture 90/95 and called
it an "original architectural hypothesis". That rating is re-examined here.

The purpose is not to defend the project. It is to state precisely what, if
anything, would be new enough to publish or fund.

---

## 1. The claim being tested

From `docs/ZERO_LINK_RESEARCH_REPORT.md` and `docs/ARCHITECTURE_HYPOTHESES.md`,
the proposed contribution (H1 TAM-DTN) is:

> A terrestrial, infrastructure-independent messaging architecture for India
> combining LoRa multi-hop, flood-once-then-direct route discovery, epidemic
> copy-budgeted forwarding, DTN store-carry-forward with custody transfer, and
> mobile ferry nodes, tuned for Indian terrain and the 865–867 MHz band, to
> deliver messages across 100 km without towers, internet or satellites.

---

## 2. What already exists

| Capability | System | Status |
|---|---|---|
| LoRa physical layer, raw (not LoRaWAN) | Reticulum/RNode [R12][R13] | **Exists** |
| Multi-hop LoRa mesh routing | Meshtastic [R9][R10] | **Exists** |
| Flood-once-then-direct (source-routed path record) | MeshCore [R11] | **Exists** |
| Store-and-forward over LoRa | Reticulum propagation nodes [R14] | **Exists** |
| Store-carry-forward with custody transfer | DTN Bundle Protocol v7 [R21] | **Exists** (IETF RFC) |
| Binary spray-and-wait / PROPHET DTN forwarding | DTN literature (Spyropoulos 2005; Lindgren 2003) | **Exists** |
| Encryption + authentication end-to-end | Reticulum, Briar, Meshtastic [R12][R20] | **Exists** |
| Gateway/star topology with duty cycle | LoRaWAN [R6] | **Exists** |
| Offline phone-to-phone messaging | Briar, Bridgefy [R19][R20] | **Exists** |
| Mobile-node-assisted delivery | DTN ferry/mule literature; Reticulum vehicle uplinks [R14][R21] | **Exists** |
| India 865–867 MHz band use | Meshtastic IN865, LoRaWAN IN865, commercial modules [R8] | **Exists** |

**Every individual mechanism in ZERO-LINK has prior art.** There is no component
in the design that is not already implemented by at least one deployed system or
specified in an IETF RFC.

---

## 3. Component-by-component classification

Using the Phase 1 taxonomy (Established technology / Existing research /
Proposed modification / Original architectural hypothesis / Experimentally
validated innovation).

| # | Component | Classification | Notes |
|---|---|---|---|
| C1 | LoRa PHY at 865–867 MHz | Established technology | Commercial modules, ETA-regulated [R8][R30] |
| C2 | Multi-hop relay mesh | Established technology | Meshtastic in production [R9] |
| C3 | Flood-once-then-direct route discovery + route cache | Established technology | MeshCore already does this [R11]; the Phase 2 simulator independently reproduced its behaviour and got the same shape of result |
| C4 | Epidemic forwarding with a copy budget | Existing research | Canonical DTN technique |
| C5 | Store-carry-forward with TTL | Established research/RFC | BPv7 [R21] |
| C6 | Custody ACK per hop | Established research | BPv7 custody transfer [R21]; Phase 2 shows it costs airtime and is currently never retried |
| C7 | Ferry/mule mobility | Existing research | DTN mule literature |
| C8 | Greedy + epidemic hybrid (geographic preference, copy budget for non-progressing forwards) | **Proposed modification** | A parameterised blend of two known schemes; the specific blend is not demonstrated to be better than either under independent testing |
| C9 | India terrain + regulatory parameterisation | **Proposed modification** | Engineering specificity, not a new mechanism |
| C10 | Simulation benchmark with fairness controls | **Proposed modification** (methodological) | Useful; closest thing to a reusable contribution |
| C11 | End-to-end 100 km architecture for India | **Original architectural hypothesis** — *unvalidated* | Integration-level claim only |
| C12 | Any experimentally validated innovation | **None** | No hardware, no field test, no independent replication |

---

## 4. What the Phase 2 results do to the novelty argument

The simulation was supposed to support the architecture's superiority. It did
not support it in the way Phase 1 asserted, and two findings actively weaken the
novelty claim:

### 4.1 The advantage is efficiency, not delivery — and efficiency is prior art's selling point

ZERO-LINK delivered 0.90 vs flooding's 0.83 in the dense case (CIs overlap),
while using 3.4–3.6× less energy and 3.2–4.5× less channel time. That is exactly
the value proposition Reticulum and MeshCore already market (efficient,
low-airtime, multi-hop LoRa). An efficiency win over *flooding* is not a
contribution against the state of the art.

### 4.2 The architecture is heavily relay-dependent

Mean relay dependency is **0.91** in the dense scenario and **1.00** in the
100 km chain; mean hop count 3.3 (dense) and 10 (chain). The system is not
"infrastructure-independent" in the sense the phrase suggests — it is
**relay-infrastructure-dependent**. It removes towers and the internet, but it
substitutes a requirement for 9–10 continuously powered relays over 100 km.
The 100 km sweep shows what that means:

| Relay availability | 4 relays (20 km) | 9 relays (10 km) | 19 relays (5 km) |
|---|---|---|---|
| 100 % | 1.00 | 1.00 | 1.00 |
| 95 % | 0.90 | 0.50 | 0.30 |
| 90 % | 0.60 | 0.20 | 0.10 |
| 80 % | 0.40 | 0.10 | 0.00 |

A 100 km link at 10 km spacing needs **~95 % per-relay uptime to reach even 50 %
delivery**. No published deployment in India demonstrates that uptime for
volunteer-maintained solar LoRa relays. This is a *feasibility* gap, not a
novelty claim, and it is the single most important unproven assumption in the
project.

### 4.3 Direct 100 km remains infeasible

Nothing in Phase 2 changes the analytic result: a handheld-to-handheld 100 km
link is outside the radio horizon (≈10 km at 1.5 m) and far outside practical
link budgets. Any future claim must say "100 km over 9–10 relays", never
"100 km range".

---

## 5. What could still be genuinely new

Ranked by how defensible each would be, with the evidence each needs.

### N1 — A reproducible, fairness-controlled benchmark for LoRa messaging architectures *(most defensible)*

There is no widely used open benchmark that compares a DTN-style architecture
against flooding, star and spray-and-wait **on identical topologies, messages,
failures and loss, with published seeds, CIs and raw CSV**. Meshtastic and
Reticulum comparisons in the wild are anecdotal ("I got 30 km on a hill").

*What exists here:* `simulation/zero_link_sim.py` with 4 architectures, 8
scenarios, 5/10 seeds, CSV+JSON, disclosed approximations, and a documented
audit of its own defects.
*What would make it a contribution:* publish it as an independent harness,
re-implement Reticulum/MeshCore behaviour as baselines, and get a third party to
run it.

### N2 — India-specific availability engineering *(plausible, unproven)*

If the contribution is "what relay density and uptime does India's terrain and
power reality actually allow for 100 km delivery?", that is a real question with
real data needs: measured uptime of solar LoRa relays across Indian districts,
monsoon/temperature effects, theft/power failures. No such dataset exists in this
project.

### N3 — Ferry-corridor delivery as a designed mode *(weak)*

The Phase 2 ferry scenario is the only place ZERO-LINK beats flooding at
something flooding cannot do at all — but at 1.6 of 30 messages per 30 minutes
and ~10 min p95. DTN mule networks are decades-old research. Contribution would
require showing a real corridor (e.g. a specific Ganges ferry route) with real
timing, not a 1-D bounce model.

### N4 — The greedy+epidemic hybrid (C8) *(unlikely)*

Would need a head-to-head parameter sweep against pure greedy, pure epidemic and
spray-and-focus, showing a region of the parameter space where the hybrid wins.
Phase 2 did not run that sweep; nothing suggests the hybrid is unique.

### Explicitly **not** novel
* LoRa multi-hop messaging.
* Store-and-forward over LoRa.
* Flood-then-direct routing.
* Custody transfer.
* Using a star gateway where coverage allows.
* "Works without internet/towers" — that is the premise of Meshtastic,
  Reticulum and Briar, all shipping today.

---

## 6. Experiments required to substantiate any contribution

| Claim to substantiate | Experiment | Would prove |
|---|---|---|
| N1 benchmark | Release harness; 3rd-party run; Reticulum baseline implemented | Methodological contribution |
| 100 km multi-hop works | 9–10 relay field deployment on one real corridor, ≥4 weeks | The core feasibility claim |
| Relay availability is achievable | Uptime telemetry from those relays (power, weather, failures) | The hidden assumption in §4.2 |
| Terrain: 20 km spacing | Link-budget measurements across 3 Indian terrains with elevation data | Whether relay count can drop to 4–6 |
| Energy advantage is real | Bench power profiling (TX/RX/idle/sleep) of one node | Replaces assumption L9 |
| Regulatory viability | Confirmed GSR 564(E) power limits + ETA route [R31][R32] | Legal path to deployment |
| Ferry mode useful | Timetabled corridor trial with real ferry position logs | N3 |

None of these is a software task, and none can be done without hardware
spending — which this phase explicitly does not authorise.

---

## 7. Revised scoring

Phase 1 scored H1 at 90/95. Rescoring on the evidence available after Phase 2:

| Dimension | Phase 1 | Phase 2 | Why |
|---|---|---|---|
| Novelty | 18/20 | **6/20** | All mechanisms have prior art; only integration + benchmark remain |
| Technical feasibility | 20/20 | **10/20** | 100 km requires ≥95 % relay uptime at 10 km spacing; unproven in India |
| Simulation evidence | 18/20 | **13/20** | Phase 1 sim was defective; Phase 2 sim is honest but small-scale and approximation-heavy |
| Regulatory clarity | 12/15 | **10/15** | 1 W vs 4 W EIRP conflict unresolved; ETA path identified [R30]–[R32] |
| Cost/practicality | 15/15 | **10/15** | Relay count implies maintenance burden not costed |
| Differentiation vs Reticulum | 7/5 → capped | **3/5** | Reticulum already provides store-and-forward + crypto + multi-interface |
| **Total** | **90/95** | **≈52/100** | |

The honest summary: **ZERO-LINK is a reasonable integration of known techniques
with a genuinely useful open benchmark, and an unproven 100 km feasibility
argument.** It is not a new architecture. Presenting it as one would not survive
peer review; presenting it as an India-specific engineering study with a
reproducible evaluation harness could.

---

## 8. Positioning statement that survives scrutiny

> ZERO-LINK is a LoRa-based, infrastructure-independent messaging design for
> rural India that integrates store-carry-forward DTN, flood-then-direct routing
> and copy-budgeted forwarding — techniques that already exist in Reticulum,
> MeshCore, Meshtastic and the DTN literature — and evaluates them against
> flooding, star/gateway and spray-and-wait baselines in a reproducible
> simulation harness with disclosed approximations. Simulation indicates that
> multi-hop delivery over 100 km is achievable at 9–10 relay spacing **only with
> ~100 % relay availability**, that the design is 3–3.6× more energy-efficient
> than flooding under equal delivery, and that direct handheld 100 km delivery is
> not feasible. No field validation exists.

That statement is defensible. The Phase 1 version was not.
