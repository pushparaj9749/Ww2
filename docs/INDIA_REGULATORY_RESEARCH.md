# ZERO-LINK — India Regulatory Research

> **Scope:** Identify the lawful path for ZERO-LINK hardware in India. This document is research, not legal advice. Verify every limit against the current WPC/DoT text before building hardware.
> **Sources:** Secondary summaries of WPC/DoT rules [R30]–[R33]. Where sources conflict, the conflict is recorded.

---

## 1. Who regulates what

| Authority | Role |
|---|---|
| **Department of Telecommunications (DoT), Ministry of Communications** | Policy owner for telecom and spectrum. |
| **Wireless Planning & Coordination (WPC) Wing** | Frequency allocation, equipment type approval (ETA), wireless station licensing. All RF devices operating below 3000 GHz (except infrared above 3000 GHz) fall under WPC [R30]. |
| **Telecommunication Engineering Centre (TEC)** | Mandatory testing/certification for certain telecom equipment (MTCTE). Check whether ZERO-LINK nodes fall under MTCTE scope. |
| **DGFT** | Import policy; ETA is required for customs clearance of wireless equipment [R32]. |

**Key distinction:**
- **ETA (Equipment Type Approval):** For de-licensed (license-exempt) bands. Required before **import, manufacture, or sale** in India. Holder must be an Indian-registered company [R30].
- **Wireless Operating Licence:** For non-de-licensed bands (e.g., GSM/WCDMA). Not applicable to ZERO-LINK if it stays in de-licensed bands.
- **Operation:** Within de-licensed bands and power limits, end users generally do **not** need an individual operating licence [R32]. The ETA obligation falls on the manufacturer/importer.

---

## 2. De-licensed bands relevant to ZERO-LINK

| Band | GSR / notification (per secondary sources) | Use | ZERO-LINK relevance |
|---|---|---|---|
| **865–867 MHz** | GSR 564(E), 30.07.2008 [R31] | Low-power RF devices incl. RFID; LoRa/LoRaWAN IN865 | **Primary band.** Sub-GHz, best range/penetration. |
| 433–434 MHz | GSR 680(E) 2012; GSR 698(E) 2015 [R31] | Low/very-low-power devices, RFID | Secondary option. Lower power limits → shorter range. |
| 2.4–2.4835 GHz | GSR 45(E), 28.01.2005 [R31] | WLAN, Bluetooth | Short-range access only (phone ↔ node). |
| 5.15–5.875 GHz | GSR 1048(E), 18.10.2018 [R31] | WLAN (indoor/outdoor) | Optional high-rate local offload. |
| 13.56 MHz | GSR 884, 04.11.2010 [R31] | Very-low-power indoor, NFC | Irrelevant (cm range). |
| 402–405 MHz | Listed as de-licensed [R30] | Medical implants etc. | Irrelevant. |
| 26.957–27.283 MHz, 20–200 kHz, 335 MHz | Listed [R30] | SRD, crane remotes | Irrelevant. |

**Band choice:** 865–867 MHz is the only band that gives km-scale range within de-licensed limits. 2.4/5 GHz cannot reach 100 km even multi-hop at reasonable density (FSPL + power). 433 MHz is viable but power-limited.

---

## 3. Power limits — the conflicting sources (open question)

Secondary sources **disagree** on the 865–867 MHz limit:

| Source | Stated limit |
|---|---|
| REYAX RYLR998 guide [R8] | 1 W EIRP (30 dBm) |
| RFID guide (GSR 564(E) summary) [R32] | 4 W EIRP (≈2.46 W ERP); 1 W conducted + 6 dBi antenna |
| LoRa India guide [R8] | 36 dBm (4 W) outdoor; licence not required under 1 W |
| Zbotic LoRaWAN vs P2P [R8] | IN865 LoRaWAN: 14 dBm EIRP on most channels; 433 MHz: 10 mW EIRP |

**Why the conflict:** The GSR text covers RFID readers (which may have higher limits) vs general SRD vs LoRaWAN regional parameters (which are LoRa Alliance specs, not law). Secondary blogs conflate them.

**ZERO-LINK design rule (conservative):**
- Assume **≤1 W EIRP (30 dBm)** for 865–867 MHz until the current GSR text is verified.
- Design typical TX at 20 dBm conducted + 2 dBi antenna = 22 dBm EIRP (well within any stated limit).
- Directional backbone antennas (12 dBi) must reduce conducted power so EIRP stays ≤30 dBm (e.g., 18 dBm + 12 dBi = 30 dBm).
- **Action before hardware:** Obtain the current WPC GSR 564(E) text and any amendments from `dot.gov.in` / `wpc.gov.in`; confirm EIRP, channel spacing (200 kHz cited [R32]), and duty-cycle rules.

---

## 4. Certification path for a prototype

1. **Prototype / research phase (non-commercial):**
   - Use **pre-certified LoRa modules** (CE/FCC) configured to 865–867 MHz within power limits.
   - Keep TX power low (≤20 dBm conducted) and duty cycle low.
   - Do not transmit outside de-licensed bands; do not use 915 MHz modules in India (US band, not de-licensed here [R8]).
   - Document frequencies, powers, and duty cycles for every test.
   - **Verify** whether field trials need additional WPC permission beyond using certified modules. Do not assume hobbyist exemption covers organised field tests.

2. **Commercial phase (sale/import/manufacture):**
   - Apply for **WPC ETA** via the WPC online portal. Indian-registered company required as holder [R30].
   - ETA accepts CE RED test reports without local re-testing in many cases [R30]; otherwise test via DoT-authorised/ILAC lab [R30].
   - Check **TEC MTCTE** applicability for the device category.
   - Customs clearance requires ETA [R32].

3. **Self-declaration:** WPC has introduced ETA through self-declaration for certain low-power license-exempt categories [R32]. Check current eligibility; do not assume it applies.

---

## 5. What ZERO-LINK must never do

- Transmit on non-de-licensed frequencies (e.g., 915 MHz, GSM bands) without a licence.
- Exceed EIRP limits (including via high-gain antennas).
- Jam, interfere, or bypass restrictions.
- Sell/import hardware without ETA.
- Claim "licence-free" for bands that are not de-licensed.

## 6. Lawful testing checklist

- [ ] Band verified as de-licensed (865–867 MHz).
- [ ] Module pre-certified; firmware locked to band + power.
- [ ] EIRP calculated including antenna gain; ≤ conservative limit.
- [ ] Duty cycle minimised; test log maintained.
- [ ] WPC field-trial permission verified (if required).
- [ ] No commercial sale/import without ETA.
- [ ] TEC MTCTE scope checked.

## 7. Open regulatory questions

1. Current 865–867 MHz EIRP limit (1 W vs 4 W) — verify GSR text.
2. Duty-cycle / channel-access rules for 865–867 MHz SRD in India.
3. Field-trial permission requirements for research prototypes.
4. TEC MTCTE applicability to LoRa mesh nodes.
5. Whether LoRaWAN IN865 channel plan (865.0625 / 865.4025 / 865.985 MHz [R8]) is mandatory or advisory for raw LoRa P2P.

> **Bottom line:** ZERO-LINK can be prototyped lawfully with certified modules in 865–867 MHz at low power. Commercial deployment needs WPC ETA (and possibly TEC). No part of the 100 km architecture requires illegal spectrum or power — the physics works within the limits (see `FEASIBILITY_100KM.md`), provided relays/elevation are used.
