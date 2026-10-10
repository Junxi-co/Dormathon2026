"""
evaluate.py  –  Member A (model & logic)
-----------------------------------------
Runs all three scenarios, prints a report to the console, and writes
results/metrics.md with five sections:

  (a) Forecast accuracy  – model MAE vs naive baseline + % improvement
  (b) Fault detection    – injected faults found vs missed
  (c) False alarms       – false positives on the clean "normal" scenario
  (d) Robustness test    – add noise + missing values, re-run detection
  (e) Impact estimate    – £ / kWh saved if a fault is caught N days earlier

Run from the repo root:
    py src/evaluate.py
"""

import textwrap
import numpy as np
import pandas as pd
from pathlib import Path

# Our pipeline
from src.pipeline import (
    load_data, train_and_forecast, flag_issues, categorize,
    prioritize, run_scenario,
    PRICE_PER_KWH, SYSTEM_KW
)

RESULTS_DIR = Path("results")
METRICS_FILE = RESULTS_DIR / "metrics.md"

# ── Known injected faults (ground truth for evaluation) ──────────────────────
# Each entry: (scenario, expected_type, fault_start, fault_end)
GROUND_TRUTH = [
    ("dusty",  "soiling",        "2026-02-10", "2026-02-17"),
    ("fault",  "equipment_fault","2026-01-31 08:00", "2026-01-31 17:00"),
]


# ════════════════════════════════════════════════════════════════════════════
# Helper – check if a detected issue overlaps a ground-truth window
# ════════════════════════════════════════════════════════════════════════════

def _overlaps(issue_start, issue_end, gt_start, gt_end) -> bool:
    """Return True if the issue time-window overlaps the ground-truth window."""
    return (issue_start <= pd.Timestamp(gt_end)) and (issue_end >= pd.Timestamp(gt_start))


# ════════════════════════════════════════════════════════════════════════════
# (a) Forecast accuracy
# ════════════════════════════════════════════════════════════════════════════

def eval_forecast() -> dict:
    """
    Run each scenario and collect model_mae and baseline_mae.
    Returns a dict keyed by scenario name.
    """
    results = {}
    for name in ("normal", "dusty", "fault"):
        plan, _ = run_scenario(name)
        pct_better = round(
            100 * (plan["baseline_mae"] - plan["model_mae"]) / (plan["baseline_mae"] + 1e-9), 1
        )
        results[name] = {
            "model_mae":    plan["model_mae"],
            "baseline_mae": plan["baseline_mae"],
            "pct_better":   pct_better,
        }
    return results


# ════════════════════════════════════════════════════════════════════════════
# (b) Fault detection – injected faults vs caught
# ════════════════════════════════════════════════════════════════════════════

def eval_detection() -> dict:
    """
    For each injected fault, check if at least one detected issue overlaps it
    and has the correct type.

    Returns: {"injected": int, "caught": int, "details": list[dict]}
    """
    caught   = 0
    details  = []
    for (scenario, expected_type, gt_start, gt_end) in GROUND_TRUTH:
        _, issues = run_scenario(scenario)
        found = False
        matched_type = "–"
        if not issues.empty:
            for _, row in issues.iterrows():
                if _overlaps(row["start"], row["end"], gt_start, gt_end):
                    found        = True
                    matched_type = row["type"]
                    if row["type"] == expected_type:
                        caught += 1
                    break
        details.append({
            "scenario":      scenario,
            "expected_type": expected_type,
            "gt_window":     f"{gt_start} → {gt_end}",
            "found":         found,
            "detected_type": matched_type,
            "correct_type":  matched_type == expected_type,
        })

    return {"injected": len(GROUND_TRUTH), "caught": caught, "details": details}


# ════════════════════════════════════════════════════════════════════════════
# (c) False alarms – detections on the clean "normal" scenario
# ════════════════════════════════════════════════════════════════════════════

def eval_false_alarms() -> dict:
    """
    Run detection on the clean "normal" scenario.
    Any issue flagged there is a false positive.
    """
    _, issues = run_scenario("normal")
    return {
        "false_alarms": len(issues),
        "issues":        issues,
    }


# ════════════════════════════════════════════════════════════════════════════
# (d) Robustness – add noise and missing values, re-run detection
# ════════════════════════════════════════════════════════════════════════════

def eval_robustness() -> dict:
    """
    Take the "fault" scenario data, inject:
      - Gaussian noise (σ = 10 % of mean output) to every actual_output value
      - 5 % of rows set to NaN (simulating sensor outages)

    Then re-run the full detection pipeline and check if the fault is still found.
    """
    rng = np.random.default_rng(seed=99)
    df  = load_data("fault")

    mean_out = df["actual_output"].mean()
    # Add noise
    df["actual_output"] += rng.normal(0, 0.10 * mean_out, len(df))
    df["actual_output"]  = df["actual_output"].clip(lower=0)

    # Drop 5 % of rows (simulate missing sensor readings)
    drop_idx = rng.choice(df.index, size=int(0.05 * len(df)), replace=False)
    df = df.drop(index=drop_idx).reset_index(drop=True)

    # Interpolate missing timestamps linearly so the model can still run
    df = df.set_index("timestamp").resample("h").mean().interpolate("linear").reset_index()

    df, _, _ = train_and_forecast(df)
    raw      = flag_issues(df)
    cat      = categorize(raw)
    issues   = prioritize(cat)

    gt_start, gt_end = "2026-01-31 08:00", "2026-01-31 17:00"
    fault_found = False
    if not issues.empty:
        for _, row in issues.iterrows():
            if _overlaps(row["start"], row["end"], gt_start, gt_end):
                fault_found = True
                break

    return {
        "noise_sigma_pct": 10,
        "missing_pct":     5,
        "fault_still_found": fault_found,
        "issues_detected": len(issues),
    }


# ════════════════════════════════════════════════════════════════════════════
# (e) Impact estimate
# ════════════════════════════════════════════════════════════════════════════

def eval_impact() -> dict:
    """
    Assumptions written out explicitly:
      - System size:       SYSTEM_KW kW nameplate
      - Capacity factor:   15 % (typical for a small northern-hemisphere farm)
      - Soiling rate:      15 % output loss if not caught for 7 extra days
      - Tariff:            PRICE_PER_KWH USD / kWh
      - Days earlier caught by this system vs manual inspection (assumed +5 days)

    Estimate: extra kWh recovered × price = $ saved per event.
    """
    capacity_factor    = 0.15
    daily_kwh          = SYSTEM_KW * capacity_factor * 24        # kWh/day clean
    soiling_loss_pct   = 0.15                                     # 15 % degradation
    days_earlier       = 5                                        # vs. manual check
    kwh_recovered      = daily_kwh * soiling_loss_pct * days_earlier
    revenue_recovered  = round(kwh_recovered * PRICE_PER_KWH, 2)

    return {
        "system_kw":           SYSTEM_KW,
        "capacity_factor_pct": capacity_factor * 100,
        "daily_clean_kwh":     round(daily_kwh, 1),
        "soiling_loss_pct":    soiling_loss_pct * 100,
        "days_earlier_caught": days_earlier,
        "kwh_recovered":       round(kwh_recovered, 1),
        "revenue_recovered_usd": revenue_recovered,
        "tariff_usd_per_kwh":  PRICE_PER_KWH,
    }


# ════════════════════════════════════════════════════════════════════════════
# Report builder
# ════════════════════════════════════════════════════════════════════════════

def build_report(forecast, detection, false_alarms, robustness, impact) -> str:
    """Assemble all results into a Markdown string."""

    # (a) Forecast accuracy table
    acc_rows = ""
    for s, v in forecast.items():
        acc_rows += (
            f"| {s:<8} | {v['model_mae']:>9.3f} | {v['baseline_mae']:>13.3f} |"
            f" {v['pct_better']:>6.1f} % |\n"
        )

    # (b) Detection table
    det_rows = ""
    for d in detection["details"]:
        tick = "✅" if d["correct_type"] else ("⚠️ wrong type" if d["found"] else "❌")
        det_rows += (
            f"| {d['scenario']:<8} | {d['expected_type']:<16} | "
            f"{d['gt_window']:<35} | {d['detected_type']:<16} | {tick} |\n"
        )

    # (e) Impact rows
    imp = impact
    imp_text = textwrap.dedent(f"""
    **Assumptions (all explicit):**

    | Assumption                | Value                        |
    |---------------------------|------------------------------|
    | System nameplate capacity | {imp['system_kw']} kW         |
    | Capacity factor           | {imp['capacity_factor_pct']} % |
    | Daily clean output        | {imp['daily_clean_kwh']} kWh  |
    | Soiling degradation       | {imp['soiling_loss_pct']} %   |
    | Days caught earlier       | {imp['days_earlier_caught']} days (vs. manual) |
    | Electricity tariff        | ${imp['tariff_usd_per_kwh']} / kWh |

    **Result:** catching soiling {imp['days_earlier_caught']} days earlier recovers
    **{imp['kwh_recovered']} kWh** worth **${imp['revenue_recovered_usd']}** per event.
    """).strip()

    report = f"""# Solar Decision Assistant – Evaluation Metrics

Generated automatically by `src/evaluate.py`.

---

## (a) Forecast Accuracy

| Scenario | Model MAE | Baseline MAE | % Better |
|----------|----------:|-------------:|---------:|
{acc_rows.rstrip()}

*MAE = Mean Absolute Error in kWh. Lower is better.*
*Baseline = same-hour-yesterday (naive shift-24 prediction).*

---

## (b) Fault Detection

{detection['injected']} fault(s) injected, {detection['caught']} caught with correct type.

| Scenario | Expected type    | Ground-truth window                    | Detected type    | Result |
|----------|------------------|----------------------------------------|------------------|--------|
{det_rows.rstrip()}

---

## (c) False Alarms (Normal scenario)

Issues flagged on clean data: **{false_alarms['false_alarms']}**

{"No false alarms – the detector is not over-sensitive. ✅" if false_alarms['false_alarms'] == 0 else "Some false alarms detected – consider tightening the threshold."}

---

## (d) Robustness Test

- Added Gaussian noise σ = {robustness['noise_sigma_pct']} % of mean output
- Dropped {robustness['missing_pct']} % of rows (simulated sensor outages), then interpolated

**Fault still detected after noise + missing data:** {"Yes ✅" if robustness['fault_still_found'] else "No ❌"}
Issues detected in noisy data: {robustness['issues_detected']}

---

## (e) Impact Estimate

{imp_text}

---
*End of report.*
"""
    return report


# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print("  Solar Decision Assistant – Evaluation")
    print("=" * 55)

    print("\n[a] Evaluating forecast accuracy…")
    forecast = eval_forecast()
    for s, v in forecast.items():
        print(f"    {s:8s}  model {v['model_mae']} kWh  "
              f"baseline {v['baseline_mae']} kWh  "
              f"({v['pct_better']}% better)")

    print("\n[b] Checking fault detection…")
    detection = eval_detection()
    for d in detection["details"]:
        status = "CAUGHT ✅" if d["correct_type"] else ("FOUND but wrong type ⚠️" if d["found"] else "MISSED ❌")
        print(f"    {d['scenario']:8s}  expected={d['expected_type']:16s}  {status}")
    print(f"    Summary: {detection['caught']} / {detection['injected']} correct")

    print("\n[c] Counting false alarms on 'normal' scenario…")
    fa = eval_false_alarms()
    print(f"    False alarms: {fa['false_alarms']}")

    print("\n[d] Running robustness test…")
    rob = eval_robustness()
    print(f"    Fault found after noise+missing: {rob['fault_still_found']}")

    print("\n[e] Calculating impact estimate…")
    imp = eval_impact()
    print(f"    Catching soiling {imp['days_earlier_caught']} days earlier saves "
          f"${imp['revenue_recovered_usd']}")

    # Write results/metrics.md
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report(forecast, detection, fa, rob, imp)
    METRICS_FILE.write_text(report, encoding="utf-8")
    print(f"\n✅  Full report written to {METRICS_FILE}")
    print("=" * 55)


if __name__ == "__main__":
    main()
