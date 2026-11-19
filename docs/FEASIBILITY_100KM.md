# ZERO-LINK — 100 km Feasibility Analysis

> **Verdict up front:** Single-hop handheld-to-handheld 100 km is **not feasible** under Indian de-licensed power limits with omnidirectional antennas at ground level. Multi-hop 100 km is **feasible in principle** with elevated relays or mobility, but requires a continuous chain or DTN ferrying — it is not automatic. All numbers below are first-principles calculations [R1][R5], not measurements.

---

## 1. Method

Link budget (Friis) [R1]:

```
P_r = P_t + G_t + G_r − FSPL − L_misc
FSPL(dB) = 20·log10(d) + 20·log10(f) + 32.44   (d in km, f in MHz)
Link margin = P_r − Sensitivity
```

Radio horizon (4/3-Earth) [R5]:

```
d_horizon(km) ≈ 4.12·(√h1 + √h2)   (h in metres)
```

First Fresnel zone radius at midpoint [R5]:

```
r(m) ≈ 17.32·√(d / 4f)   (d in km, f in GHz)
Engineering rule: keep ≥60% of r clear of obstacles.
```

Assumptions (conservative, India-compliant):
- Frequency: 866 MHz (mid of 865–867 MHz de-licensed band).
- TX power: 20 dBm (100 mW) conducted; EIRP ≤ 30 dBm (1 W) assumed limit (see `INDIA_REGULATORY_RESEARCH.md` — sources conflict; 1 W is conservative).
- Antennas: handheld 2 dBi omni; backbone 12 dBi directional.
- Receiver: LoRa SF12/BW125 kHz, sensitivity −137 dBm [R2].
- Misc losses: 3 dB (cable, mismatch, polarisation).
- Fade margin target: ≥10 dB for reliable links; ≥20 dB for robust links.

---

## 2. Scenario A — Direct 100 km (Device A → Device B)

### 2.1 Free-space path loss alone

At 866 MHz, 100 km:

```
FSPL = 20·log10(100) + 20·log10(866) + 32.44
     = 40.0 + 58.75 + 32.44
     ≈ 131.2 dB
```

Link budget (handheld-to-handheld, 20 dBm TX, 2 dBi each end):

```
P_r = 20 + 2 + 2 − 131.2 − 3 = −110.2 dBm
Margin = −110.2 − (−137) = +26.8 dB
```

**On paper, the link closes with 27 dB margin.** This is why naive calculations claim 100 km is easy. It is misleading, because free space does not exist at ground level over 100 km.

### 2.2 The horizon problem (the real blocker)

Radio horizon for two handhelds at 1.5 m:

```
d = 4.12·(√1.5 + √1.5) ≈ 4.12·2.45 ≈ 10.1 km
```

100 km is **10× beyond the horizon**. The direct ray is blocked by Earth curvature. Diffraction around the curvature at 866 MHz over 90 km beyond horizon loses far more than the 27 dB margin (beyond-horizon diffraction loss grows steeply with distance; practical beyond-horizon UHF links at these powers are limited to tens of km with favourable ducting, not reliable 100 km).

To see 100 km, antenna heights must satisfy:

```
4.12·(√h1 + √h2) ≥ 100  →  √h1 + √h2 ≥ 24.3
```

- Equal heights: √h ≥ 12.1 → **h ≥ 147 m each**. That is a hilltop or a 50-storey tower, not a handheld.
- One handheld (1.5 m, √=1.22): other end needs √h ≥ 23.1 → **h ≥ 533 m**. A mountain.

### 2.3 The Fresnel problem (even with height)

Fresnel radius at midpoint of 100 km, 866 MHz (f=0.866 GHz):

```
r = 17.32·√(100 / (4·0.866)) = 17.32·√28.9 ≈ 17.32·5.37 ≈ 93 m
60% clearance ≈ 56 m
```

The path needs a **~112 m diameter clear ellipsoid** (56 m above/below the direct ray at midpoint). Over Indian terrain (trees, buildings, hills, monsoon vegetation), this clearance is rarely available even between elevated sites. Any obstruction inside the zone costs 6–20+ dB.

### 2.4 Scenario A verdict

| Configuration | Feasible? | Why |
|---|---|---|
| Handheld (1.5 m) ↔ handheld (1.5 m), 100 km | **No** | 10 km horizon; 90 km beyond horizon. Margin irrelevant. |
| Handheld ↔ hilltop (500 m), 100 km | **Marginal / weather-dependent** | Horizon closes; Fresnel + terrain + weather decide. Not reliable. |
| Hilltop (150 m) ↔ hilltop (150 m), 100 km, directional antennas | **Physically possible, not reliable** | Horizon + Fresnel close on paper; real terrain/weather rarely cooperate over 100 km. Record LoRa links (331 km [R9], 832 km [R4]) used exceptional line-of-sight (mountain/balloon), not typical terrain. |
| Handheld ↔ handheld, 100 km, higher TX power | **No (and illegal)** | Raising power does not fix horizon blockage; also exceeds de-licensed EIRP. |

**Conclusion A:** Do not promise direct 100 km. Any architecture claiming it is either assuming elevation that handhelds do not have, or confusing free-space arithmetic with real-world propagation.

---

## 3. Scenario B — Multi-node 100 km (A → relays → B)

### 3.1 Per-hop budget (the building block)

Same assumptions, per-hop distances:

| Hop distance | FSPL @866 MHz | P_r (20 dBm, 2 dBi) | Margin vs −137 dBm | Horizon needed (equal heights) | Fresnel r (60% clearance) |
|---|---|---|---|---|---|
| 5 km | 105.2 dB | −84.2 dBm | **+52.8 dB** | 3.5 m each | 21 m (13 m) |
| 10 km | 111.2 dB | −90.2 dBm | **+46.8 dB** | 6 m each | 30 m (18 m) |
| 15 km | 114.8 dB | −93.8 dBm | **+43.2 dB** | 13 m each | 36 m (22 m) |
| 20 km | 117.2 dB | −96.2 dBm | **+40.8 dB** | 23 m each | 42 m (25 m) |

**Interpretation:** Link budget is generous at 5–20 km. The constraints are horizon, Fresnel, and terrain — not power. A 10 km hop needs only ~6 m masts for horizon, but needs 18 m Fresnel clearance and clear terrain. In practice, Indian rural terrain (trees, undulation, buildings) limits reliable omnidirectional hops to **2–10 km**, with 10–15 km achievable on elevated/clear paths. This matches reported Meshtastic/LoRa field ranges [R9].

### 3.2 Chain arithmetic for 100 km

| Per-hop range | Hops for 100 km | Cumulative latency (SF12, ~2 s/hop + processing) | Failure points |
|---|---|---|---|
| 5 km | 20 hops | ~40–60 s (connected) | 19 relays must all be up |
| 10 km | 10 hops | ~20–30 s | 9 relays |
| 15 km | 7 hops | ~14–20 s | 6 relays |
| 20 km (elevated/directional) | 5 hops | ~10–15 s | 4 relays |

**Key insight:** Latency is not the problem (tens of seconds). **Reliability is.** If each relay has 95% availability, a 10-hop chain has 0.95⁹ ≈ 63% end-to-end availability. A 20-hop chain: 0.95¹⁹ ≈ 38%. Multi-hop chains multiply failure probability. This is why DTN store-carry-forward (H1/H2) matters: it converts chain failure into delay instead of loss.

### 3.3 Terrain and environment (India-specific)

- **Hills (Western/Eastern Ghats, Himalayas):** Shadowing blocks hops; hilltop relays help but need site access.
- **Plains (Gangetic, Deccan):** Best case — flat, long sightlines; vegetation and buildings are the main Fresnel obstructions.
- **Urban (Delhi, Mumbai, Kolkata, Bengaluru):** Concrete attenuation 10–30 dB; hops shrink to 0.5–3 km [R9]; 100 km needs 30–100+ hops — impractical without backbone nodes.
- **Monsoon:** Rain attenuation at 866 MHz is small (<1 dB/km), but wet foliage, flooding (antenna submersion), and power outages hurt availability. Optical (FSO) fails in monsoon; RF does not — another reason RF is the primary bearer [R28].
- **Vegetation:** Wet dense forest can cut range to hundreds of metres [R9]. Antenna above canopy is essential.

### 3.4 Energy

- TX energy per message (SF12, 20 dBm, ~2 s airtime): ~0.2–0.4 J (radio only).
- 10-hop chain: ~2–4 J per end-to-end message (all relays combined).
- Relay battery: 18650 Li-ion (~10 Wh = 36 kJ) → ~10,000+ relayed messages before recharge (idealised; real duty cycle + RX energy lower this).
- **Conclusion:** Energy is not the 100 km blocker. Relay availability and placement are.

### 3.5 Regulatory (India)

- Must stay in de-licensed bands (865–867 MHz primary) and within EIRP limits (assume ≤1 W; verify — see `INDIA_REGULATORY_RESEARCH.md`).
- Directional high-gain antennas must not push EIRP over the limit (gain counts toward EIRP).
- No duty-cycle assumption without verification; design for low duty cycle regardless.
- Commercial sale/import needs WPC ETA. Field testing with certified modules within limits is the lawful path.

### 3.6 Scenario B verdict

| Configuration | Feasible? | Conditions |
|---|---|---|
| 100 km via 10× 10 km omnidirectional hops, rural plains | **Yes, with planning** | Elevated relays (6–10 m), Fresnel clearance, solar power, DTN fallback for gaps |
| 100 km via 20× 5 km hops, mixed terrain | **Yes, but fragile** | Needs 19 relays; DTN essential; latency minutes |
| 100 km via 5× 20 km elevated/directional hops | **Yes (H3 backbone)** | Hills/rooftops, directional antennas, site access |
| 100 km via urban hops (1–3 km) | **Impractical** | 30–100 hops; congestion + failure multiplication |
| 100 km with no relays, no mobility | **No** | Violates horizon physics |

---

## 4. What 100 km actually requires (checklist)

1. **Relay chain or mobility.** No chain + no mobility = no 100 km. This is physics, not engineering effort.
2. **Elevation.** Every relay needs enough height for horizon + Fresnel. Ground-level relays in valleys will fail.
3. **DTN fallback.** Chains break (battery, weather, terrain). Store-carry-forward converts loss into delay.
4. **Low duty cycle.** SF12 airtime is seconds; flooding at density will congest the channel. Routing must be efficient.
5. **India compliance.** 865–867 MHz, ≤1 W EIRP (conservative), WPC ETA for commercial hardware.
6. **Simulation before hardware.** Relay placement must be validated in simulation (see `SIMULATION_PLAN.md`) before spending on masts/solar.

## 5. Honest statement

> **100 km is achievable as a multi-hop DTN system with planned relays and/or mobility. It is not achievable as a direct handheld link. Any ZERO-LINK claim must specify which scenario it refers to, what relay density it assumes, and what latency/availability it guarantees — or explicitly state that it guarantees neither.**
