# Solar Decision Assistant – Evaluation Metrics

Generated automatically by `src/evaluate.py`.

---

## (a) Forecast Accuracy

| Scenario | Model MAE | Baseline MAE | % Better |
|----------|----------:|-------------:|---------:|
| normal   |     1.132 |         2.480 |   54.4 % |
| dusty    |     3.139 |         2.137 |  -46.9 % |
| fault    |     1.317 |         2.480 |   46.9 % |

*MAE = Mean Absolute Error in kWh. Lower is better.*
*Baseline = same-hour-yesterday (naive shift-24 prediction).*

---

## (b) Fault Detection

2 fault(s) injected, 2 caught with correct type.

| Scenario | Expected type    | Ground-truth window                    | Detected type    | Result |
|----------|------------------|----------------------------------------|------------------|--------|
| dusty    | soiling          | 2026-02-10 → 2026-02-17             | soiling          | ✅ |
| fault    | equipment_fault  | 2026-01-31 08:00 → 2026-01-31 17:00 | equipment_fault  | ✅ |

---

## (c) False Alarms (Normal scenario)

Issues flagged on clean data: **1**

Some false alarms detected – consider tightening the threshold.

---

## (d) Robustness Test

- Added Gaussian noise σ = 10 % of mean output
- Dropped 5 % of rows (simulated sensor outages), then interpolated

**Fault still detected after noise + missing data:** Yes ✅
Issues detected in noisy data: 7

---

## (e) Impact Estimate

**Assumptions (all explicit):**

| Assumption                | Value                        |
|---------------------------|------------------------------|
| System nameplate capacity | 50 kW         |
| Capacity factor           | 15.0 % |
| Daily clean output        | 180.0 kWh  |
| Soiling degradation       | 15.0 %   |
| Days caught earlier       | 5 days (vs. manual) |
| Electricity tariff        | $0.12 / kWh |

**Result:** catching soiling 5 days earlier recovers.
**135.0 kWh** worth **$16.2** per event.

---
*End of report.*
