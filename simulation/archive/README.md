# Archived simulation outputs (historical, do not edit)

These files are preserved as a record of intermediate states of the Phase 2
simulator. They are superseded and **must not** be cited as final results.

| File | Simulator state | Why archived |
|---|---|---|
| `results_phase2_interim_2seed_PREFIX.{csv,json}` | 2 seeds (42, 7); star downlink scheduling bug fixed, gateway-selection and hop-tracking fixes NOT yet applied | Shows state before the final fairness fixes |
| `test_log_interim_2seed_PREFIX.txt` | console log of the same interim run | Matching log |

`PREFIX` marks runs made before the final 5-seed validation sweep. The final
results live in `simulation/results_phase2.{csv,json}` and
`simulation/test_log_phase2.txt`.
