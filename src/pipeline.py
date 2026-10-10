"""
pipeline.py  –  Member A (model & logic)
-----------------------------------------
All data generation, forecasting, anomaly detection, categorisation,
prioritisation, and schedule optimisation for the "Tomorrow's Solar Plan"
prototype.

Keep every function short and obviously named.
CONTRACT columns used throughout:
    timestamp, irradiance, cloud_cover, temperature, actual_output,
    forecast, baseline, residual, flagged, issue_id, type,
    kwh_lost, cost_lost, rank
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# ── Top-level constants you might want to tweak ───────────────────────────────
PRICE_PER_KWH   = 0.12   # USD – export / avoided-cost rate
PEAK_TARIFF     = 0.28   # USD / kWh  (on-peak grid electricity price)
OFFPEAK_TARIFF  = 0.10   # USD / kWh  (cheap-rate window for battery top-up)
SYSTEM_KW       = 50     # nameplate capacity of the solar farm in kW
RANDOM_SEED     = 42
DATA_DIR        = Path("data")
# ─────────────────────────────────────────────────────────────────────────────


# ════════════════════════════════════════════════════════════════════════════
# STEP 1  –  Data generation
# ════════════════════════════════════════════════════════════════════════════

def load_data(scenario: str = "normal") -> pd.DataFrame:
    """
    Load data/solar_data_{scenario}.csv if it exists.
    Otherwise generate 60 days of synthetic hourly data and save it.

    scenario must be one of: "normal", "dusty", "fault"

    Returns a DataFrame with CONTRACT columns:
        timestamp, irradiance, cloud_cover, temperature, actual_output
    """
    path = DATA_DIR / f"solar_data_{scenario}.csv"
    if path.exists():
        df = pd.read_csv(path, parse_dates=["timestamp"])
        return df

    print(f"  [data] {path} not found – generating fake '{scenario}' data…")
    df = _generate(scenario)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def _generate(scenario: str) -> pd.DataFrame:
    """
    Build 60 days × 24 hours = 1 440 rows of plausible solar data.

    Sun curve: irradiance follows a half-sine between 06:00 and 18:00.
    Three scenarios:
        normal  – clean data, small random noise only
        dusty   – 15 % output decline accumulates over days 40-47 (soiling)
        fault   – sudden near-zero drop on day 30 08:00-17:00 (equipment fault)
    """
    rng   = np.random.default_rng(RANDOM_SEED)
    hours = 60 * 24
    ts    = pd.date_range("2026-01-01", periods=hours, freq="h")
    hod   = ts.hour.to_numpy()   # plain numpy array – avoids pandas Index mutation errors

    # ── Weather ──────────────────────────────────────────────────────────────
    # Irradiance: daytime sine arch, zero at night
    irradiance = np.clip(
        SYSTEM_KW * 16 * np.sin(np.pi * np.clip(hod - 6, 0, 12) / 12)
        + rng.normal(0, 20, hours),
        0, None
    )
    # Cloud cover: 0 (clear) – 1 (overcast), slightly correlated day-to-day
    cloud_raw  = rng.beta(2, 5, hours)
    cloud_cover = np.clip(cloud_raw, 0, 1)
    # Temperature: warmer midday
    temperature = 18 + 6 * np.sin(np.pi * np.clip(hod - 6, 0, 12) / 12) + rng.normal(0, 1.5, hours)

    # ── Base output (kWh per hour) ────────────────────────────────────────────
    output = np.clip(
        irradiance * (1 - 0.55 * cloud_cover) * 0.06 + rng.normal(0, 1.5, hours),
        0, None
    )

    # Convert ts to numpy for boolean mask compatibility
    ts_np = ts.to_numpy()

    # ── Inject scenario faults ────────────────────────────────────────────────
    if scenario == "dusty":
        # Slow 15 % output decline over days 40-47; weather stays clear
        day40 = pd.Timestamp("2026-02-10").to_datetime64()
        hrs_since = np.maximum((ts_np - day40) / np.timedelta64(1, "h"), 0)
        soiling   = np.clip(1 - 0.0214 * hrs_since, 0.85, 1)   # ~15 % over 7 days
        output   *= soiling
        # Keep skies clear during the soiling window so detection isn't confused
        day40_end = pd.Timestamp("2026-02-17").to_datetime64()
        dusty_mask = (ts_np >= day40) & (ts_np < day40_end)
        cloud_cover = np.where(dusty_mask, cloud_cover * 0.3, cloud_cover)
        irradiance  = np.where(dusty_mask, irradiance * 1.1,  irradiance)

    elif scenario == "fault":
        # Sudden near-zero drop on day 30 (January 31), daytime hours 08-17
        f_start    = pd.Timestamp("2026-01-31 08:00").to_datetime64()
        f_end      = pd.Timestamp("2026-01-31 17:00").to_datetime64()
        fault_mask = (ts_np >= f_start) & (ts_np <= f_end)
        output[fault_mask] *= 0.03   # ~zero
        # Weather is fine that day – makes the fault stand out clearly
        cloud_cover = np.where(fault_mask, 0.05, cloud_cover)

    # ── Assemble DataFrame ────────────────────────────────────────────────────
    df = pd.DataFrame({
        "timestamp":     ts,
        "irradiance":    np.round(irradiance, 2),
        "cloud_cover":   np.round(cloud_cover, 3),
        "temperature":   np.round(temperature, 2),
        "actual_output": np.round(output, 3),
    })
    return df


# ════════════════════════════════════════════════════════════════════════════
# STEP 2  –  Forecast
# ════════════════════════════════════════════════════════════════════════════

def train_and_forecast(df: pd.DataFrame) -> tuple:
    """
    Train a RandomForestRegressor on weather features + hour-of-day.
    Also compute a naive baseline (same hour, previous day = shift 24).

    Train / test split: first 40 days train, last 20 days test.

    Adds CONTRACT columns to df:
        forecast  – model output (clipped ≥ 0)
        baseline  – 24-hour shift of actual_output

    Returns:
        (df, model_mae, baseline_mae)
        Both MAEs are floats (kWh), computed on the test window only.
    """
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    feats = ["irradiance", "cloud_cover", "temperature", "hour"]

    split = df["timestamp"].min() + pd.Timedelta(days=40)
    train = df[df["timestamp"] <  split]
    test  = df[df["timestamp"] >= split]

    model = RandomForestRegressor(n_estimators=100, random_state=RANDOM_SEED, n_jobs=-1)
    model.fit(train[feats], train["actual_output"])

    df["forecast"] = np.clip(model.predict(df[feats]), 0, None)
    df["baseline"] = df["actual_output"].shift(24)   # naive: yesterday same hour

    # Evaluate on test set (drop the first 24 h of test so baseline is never NaN)
    t = df[df["timestamp"] >= split].dropna(subset=["baseline"])
    model_mae    = round(mean_absolute_error(t["actual_output"], t["forecast"]),    3)
    baseline_mae = round(mean_absolute_error(t["actual_output"], t["baseline"]), 3)

    return df, model_mae, baseline_mae


# ════════════════════════════════════════════════════════════════════════════
# STEP 3  –  Detect underperformance
# ════════════════════════════════════════════════════════════════════════════

def flag_issues(df: pd.DataFrame,
                threshold: float = 0.40,
                min_hours: int   = 3) -> pd.DataFrame:
    """
    Mark rows where actual output is much lower than forecast.

    Two detection tiers:
      hard gap – actual < threshold (40 %) × forecast, sustained ≥ min_hours
      soft gap – actual < 90 % × forecast, sustained ≥ 2 h

    Nearby events (gap between them < 14 h, e.g. a single night) are merged
    into one event so that multi-day soiling appears as a single long issue.

    Adds CONTRACT columns:  residual, flagged
    Returns a summary DataFrame of issue events with columns:
        issue_id, start, end, duration_hours,
        mean_actual, mean_forecast, mean_irradiance, mean_cloud
    """
    df = df.copy()
    df["residual"] = df["actual_output"] - df["forecast"]

    hard_flag = (df["forecast"] > 1) & (df["actual_output"] < threshold * df["forecast"])
    soft_flag = (df["forecast"] > 1) & (df["actual_output"] < 0.90 * df["forecast"])

    grp_hard = (hard_flag != hard_flag.shift()).cumsum()
    run_hard  = hard_flag.groupby(grp_hard).transform("sum")

    grp_soft = (soft_flag != soft_flag.shift()).cumsum()
    run_soft  = soft_flag.groupby(grp_soft).transform("sum")

    df["flagged"] = (
        (hard_flag & (run_hard >= min_hours)) |
        (soft_flag & (run_soft >= 5))   # require ≥5 consecutive soft-gap hours
    )

    # Assign raw event ids
    df["event_id"] = (df["flagged"] & ~df["flagged"].shift(fill_value=False)).cumsum()
    df.loc[~df["flagged"], "event_id"] = 0

    # Build raw event list
    raw_events = []
    for eid, grp in df[df["flagged"]].groupby("event_id"):
        raw_events.append({
            "event_id": int(eid),
            "start":    grp["timestamp"].iloc[0],
            "end":      grp["timestamp"].iloc[-1],
        })

    if not raw_events:
        return pd.DataFrame(columns=["issue_id", "start", "end", "duration_hours",
                                     "mean_actual", "mean_forecast",
                                     "mean_irradiance", "mean_cloud"])

    # ── Merge events that are less than 14 hours apart ────────────────────────
    # This handles soiling where night-time (forecast ≤ 1) breaks the run.
    raw_events.sort(key=lambda e: e["start"])
    merged = [raw_events[0].copy()]
    for ev in raw_events[1:]:
        gap_h = (ev["start"] - merged[-1]["end"]).total_seconds() / 3600
        if gap_h < 14:
            merged[-1]["end"] = ev["end"]   # extend the previous event
        else:
            merged.append(ev.copy())

    # ── Build final summary rows ───────────────────────────────────────────────
    events = []
    for i, ev in enumerate(merged, start=1):
        mask = (df["timestamp"] >= ev["start"]) & (df["timestamp"] <= ev["end"])
        grp  = df[mask & df["flagged"]]
        if grp.empty:
            continue
        events.append({
            "issue_id":        i,
            "start":           ev["start"],
            "end":             ev["end"],
            "duration_hours":  len(grp),
            "mean_actual":     round(grp["actual_output"].mean(), 3),
            "mean_forecast":   round(grp["forecast"].mean(),      3),
            "mean_irradiance": round(grp["irradiance"].mean(),    1),
            "mean_cloud":      round(grp["cloud_cover"].mean(),   3),
        })

    return pd.DataFrame(events)


# ════════════════════════════════════════════════════════════════════════════
# STEP 4  –  Categorise
# ════════════════════════════════════════════════════════════════════════════

def categorize(issues: pd.DataFrame) -> pd.DataFrame:
    """
    Label each detected issue with a fault type using simple rule-based logic.

    Rules (applied in order; first match wins):
        equipment_fault  – mean_actual < 5 % of mean_forecast
                           AND mean_irradiance is good (> 200 W/m²)
        soiling          – multi-day (> 20 h) slow decline, clear sky (irr > 200)
                           AND ratio between 0.05 and 0.90
        shading          – issue lasts ≤ 4 h (short recurring daily dip)
        weather_dip      – everything else (explained by low irr or high cloud)

    Adds CONTRACT column: type
    """
    if issues.empty:
        return issues

    issues = issues.copy()
    labels = []
    for _, r in issues.iterrows():
        ratio = r["mean_actual"] / (r["mean_forecast"] + 1e-9)
        if ratio < 0.20 and r["mean_irradiance"] > 200:
            labels.append("equipment_fault")
        elif 0.05 <= ratio < 0.95 and r["duration_hours"] > 10 and r["mean_irradiance"] > 200:
            labels.append("soiling")
        elif r["duration_hours"] <= 4:
            labels.append("shading")
        else:
            labels.append("weather_dip")

    issues["type"] = labels
    return issues


# ════════════════════════════════════════════════════════════════════════════
# STEP 5  –  Prioritise by cost
# ════════════════════════════════════════════════════════════════════════════

def prioritize(issues: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate revenue lost per issue and rank from worst to least severe.

    kwh_lost  = (mean_forecast - mean_actual) × duration_hours  (clipped ≥ 0)
    cost_lost = kwh_lost × PRICE_PER_KWH

    Returns a tidy CONTRACT table:
        issue_id, type, start, end, duration_hours, kwh_lost, cost_lost, rank
    """
    if issues.empty:
        return issues

    issues = issues.copy()
    issues["kwh_lost"]  = ((issues["mean_forecast"] - issues["mean_actual"])
                           * issues["duration_hours"]).clip(lower=0).round(2)
    issues["cost_lost"] = (issues["kwh_lost"] * PRICE_PER_KWH).round(2)
    issues = issues.sort_values("cost_lost", ascending=False).reset_index(drop=True)
    issues["rank"] = issues.index + 1

    return issues[["issue_id", "type", "start", "end",
                   "duration_hours", "kwh_lost", "cost_lost", "rank"]]


# ════════════════════════════════════════════════════════════════════════════
# STEP 6  –  Optimise schedule
# ════════════════════════════════════════════════════════════════════════════

def optimize(df: pd.DataFrame) -> dict:
    """
    Use tomorrow's forecast to suggest two simple actions:

    1. best_solar_window  – best consecutive 3-hour block by forecast kWh
       → run high-load appliances then (free solar energy)

    2. battery_topup_window – estimate evening shortfall (18:00-22:00)
       and whether it's worth topping up from the grid at the cheap rate
       (OFFPEAK_TARIFF) before evening peak (PEAK_TARIFF)

    Returns a dict with keys:
        best_solar_window   : {"start": str, "end": str, "kwh": float}
        battery_topup       : {"suggested": bool, "window": str,
                               "est_shortfall_kwh": float, "savings": float}

    "Tomorrow" = the last calendar day in the DataFrame.
    """
    # Isolate the last day in the data (proxy for "tomorrow's forecast")
    last_day  = df["timestamp"].dt.date.max()
    tomorrow  = df[df["timestamp"].dt.date == last_day].copy()

    # ── Best 3-hour solar window ──────────────────────────────────────────────
    daytime = tomorrow[tomorrow["forecast"] > 0.5].reset_index(drop=True)
    best_start_idx = 0
    best_kwh       = 0.0

    for i in range(len(daytime) - 2):
        window_kwh = daytime.loc[i : i + 2, "forecast"].sum()
        if window_kwh > best_kwh:
            best_kwh       = window_kwh
            best_start_idx = i

    if len(daytime) > 2:
        ws = daytime.loc[best_start_idx, "timestamp"]
        we = daytime.loc[best_start_idx + 2, "timestamp"]
        solar_window = {
            "start": str(ws),
            "end":   str(we),
            "kwh":   round(best_kwh, 2),
        }
    else:
        solar_window = {"start": "N/A", "end": "N/A", "kwh": 0.0}

    # ── Evening battery shortfall & cheap-rate top-up ─────────────────────────
    # Assume a home/small-farm battery sized at 10 kWh, 80 % usable
    BATTERY_USABLE_KWH = 8.0
    # Assume average evening demand is 1.5 kW for 4 hours = 6 kWh
    EVENING_DEMAND_KWH = 6.0

    # How much the battery is charged = surplus during the best solar window
    # (capped at usable capacity)
    battery_soc = min(solar_window["kwh"] * 0.9, BATTERY_USABLE_KWH)   # 90 % charge efficiency

    shortfall    = max(EVENING_DEMAND_KWH - battery_soc, 0.0)
    saving       = round(shortfall * (PEAK_TARIFF - OFFPEAK_TARIFF), 2)
    suggest_topup = shortfall > 0.5   # only bother if shortfall > 0.5 kWh

    battery_topup = {
        "suggested":          suggest_topup,
        "window":             "14:00–16:00 (cheap-rate)",
        "est_shortfall_kwh":  round(shortfall, 2),
        "savings":            saving,
    }

    return {
        "best_solar_window":  solar_window,
        "battery_topup":      battery_topup,
    }


# ════════════════════════════════════════════════════════════════════════════
# STEP 7  –  run_scenario  (CONTRACT entry point)
# ════════════════════════════════════════════════════════════════════════════

def run_scenario(name: str) -> tuple:
    """
    Run the full pipeline for one scenario and return (plan, issues).

    Parameters
    ----------
    name : str
        One of "normal", "dusty", or "fault".

    Returns
    -------
    plan : dict
        {
          "scenario":     name,
          "model_mae":    float,
          "baseline_mae": float,
          "df":           pd.DataFrame,   # full timeseries with all columns
          "optimize":     dict,           # output of optimize()
        }
    issues : pd.DataFrame
        CONTRACT table with columns:
            issue_id, type, start, end, duration_hours,
            kwh_lost, cost_lost, rank
    """
    print(f"\n── Running scenario: {name} ──")

    df                          = load_data(name)
    df, model_mae, baseline_mae = train_and_forecast(df)
    raw                         = flag_issues(df)
    categorised                 = categorize(raw)
    ranked                      = prioritize(categorised)
    sched                       = optimize(df)

    plan = {
        "scenario":     name,
        "model_mae":    model_mae,
        "baseline_mae": baseline_mae,
        "df":           df,
        "optimize":     sched,
    }

    return plan, ranked
