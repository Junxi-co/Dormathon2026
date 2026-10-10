"""
pipeline.py
-----------
All data loading, forecasting, issue detection, and prioritisation logic.
Keep functions small and well-commented so beginners can follow along.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# ── Tunable constants ─────────────────────────────────────────────────────────
PRICE_PER_KWH = 0.12          # USD – change this to your local electricity price
DATA_PATH = Path("data/solar_data.csv")
RANDOM_SEED = 42
# ─────────────────────────────────────────────────────────────────────────────


# ── 1. Load or generate data ──────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    """
    Load solar_data.csv from the data folder.
    If the file doesn't exist, generate 30 days of fake hourly data
    with two injected problems so we always have something to demo.

    Returns a DataFrame with columns:
        timestamp, irradiance, cloud_cover, temperature, actual_output
    """
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
        return df

    print("data/solar_data.csv not found – generating fake data…")
    df = _generate_fake_data()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df


def _generate_fake_data() -> pd.DataFrame:
    """
    Create 30 days × 24 hours of plausible solar farm data with:
      - Problem 1: sudden drop on day 10 (equipment fault simulation)
      - Problem 2: slow decline starting day 20 (soiling simulation)
    """
    rng = np.random.default_rng(RANDOM_SEED)
    hours = 30 * 24  # 720 rows

    timestamps = pd.date_range("2026-01-01", periods=hours, freq="h")

    # Hour-of-day (0-23) drives a simple sun curve
    hour_of_day = timestamps.hour

    # Irradiance peaks midday, drops to 0 at night (W/m²)
    irradiance = np.clip(
        800 * np.sin(np.pi * (hour_of_day - 6) / 12) + rng.normal(0, 30, hours),
        0, None
    )

    # Cloud cover 0-1 (higher = more cloud)
    cloud_cover = np.clip(rng.beta(2, 5, hours), 0, 1)

    # Temperature in °C
    temperature = 20 + 8 * np.sin(np.pi * (hour_of_day - 6) / 12) + rng.normal(0, 2, hours)

    # Base output in kWh roughly proportional to irradiance, reduced by cloud
    base_output = irradiance * (1 - 0.6 * cloud_cover) * 0.05 + rng.normal(0, 2, hours)
    base_output = np.clip(base_output, 0, None)

    # ── Inject Problem 1: sudden drop on day 10, hours 8-18 ──
    day10_mask = (timestamps >= "2026-01-10 08:00") & (timestamps <= "2026-01-10 18:00")
    base_output[day10_mask] *= 0.05   # near-zero output

    # ── Inject Problem 2: slow soiling decline from day 20 onward ──
    day20_start = pd.Timestamp("2026-01-20")
    hours_since_day20 = np.maximum((timestamps - day20_start).total_seconds() / 3600, 0)
    soiling_factor = np.clip(1 - 0.008 * hours_since_day20, 0.5, 1)
    base_output *= soiling_factor

    df = pd.DataFrame({
        "timestamp":     timestamps,
        "irradiance":    irradiance.round(2),
        "cloud_cover":   cloud_cover.round(3),
        "temperature":   temperature.round(2),
        "actual_output": base_output.round(3),
    })
    return df


# ── 2. Train model and forecast ───────────────────────────────────────────────

def train_and_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Train a RandomForestRegressor on weather features to predict actual_output.
    Also compute a naive baseline (shift output by 24 hours = previous day).

    Uses the first 20 days for training, last 10 days for testing.

    Adds columns to df:
        forecast       – model prediction for every row (NaN for training rows)
        baseline       – previous-day naive prediction

    Returns (df, model_mae, baseline_mae) – errors on the test set only.
    """
    feature_cols = ["irradiance", "cloud_cover", "temperature"]

    # Add hour-of-day as a feature so the model knows about the sun cycle
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    feature_cols.append("hour")

    # Split: first 20 days train, last 10 days test
    split_date = df["timestamp"].min() + pd.Timedelta(days=20)
    train = df[df["timestamp"] < split_date]
    test  = df[df["timestamp"] >= split_date]

    model = RandomForestRegressor(n_estimators=100, random_state=RANDOM_SEED)
    model.fit(train[feature_cols], train["actual_output"])

    # Predict on full dataset so we can show a forecast line for all days
    df["forecast"] = model.predict(df[feature_cols])
    df["forecast"] = df["forecast"].clip(lower=0)

    # Naive baseline: actual output from 24 hours ago
    df["baseline"] = df["actual_output"].shift(24)

    # Compute errors on the test portion only (baseline needs 24 h warmup)
    test_df = df[df["timestamp"] >= split_date].dropna(subset=["baseline"])
    model_mae    = mean_absolute_error(test_df["actual_output"], test_df["forecast"])
    baseline_mae = mean_absolute_error(test_df["actual_output"], test_df["baseline"])

    return df, round(model_mae, 3), round(baseline_mae, 3)


# ── 3. Flag underperformance issues ───────────────────────────────────────────

def flag_issues(df: pd.DataFrame, threshold: float = 0.4, min_hours: int = 3) -> pd.DataFrame:
    """
    Flag a row as an issue when actual_output is less than (threshold × forecast)
    AND forecast > 1 kWh (ignore night-time near-zero forecasts).

    Groups consecutive flagged hours into a single issue event.

    Returns a DataFrame of issue events with columns:
        issue_id, start, end, duration_hours, mean_actual, mean_forecast,
        mean_irradiance, mean_cloud
    """
    df = df.copy()

    # Mark rows where output is suspiciously low compared to forecast
    df["flagged"] = (
        (df["forecast"] > 1) &
        (df["actual_output"] < threshold * df["forecast"])
    )

    # Group consecutive flagged rows into events
    # A new event starts every time the flagged state changes from False → True
    df["event_id"] = (df["flagged"] & ~df["flagged"].shift(1, fill_value=False)).cumsum()
    df.loc[~df["flagged"], "event_id"] = 0  # 0 means "no issue"

    issues = []
    for eid, group in df[df["flagged"]].groupby("event_id"):
        if len(group) < min_hours:
            continue  # ignore blips shorter than min_hours
        issues.append({
            "issue_id":       eid,
            "start":          group["timestamp"].iloc[0],
            "end":            group["timestamp"].iloc[-1],
            "duration_hours": len(group),
            "mean_actual":    group["actual_output"].mean().round(3),
            "mean_forecast":  group["forecast"].mean().round(3),
            "mean_irradiance":group["irradiance"].mean().round(1),
            "mean_cloud":     group["cloud_cover"].mean().round(3),
        })

    return pd.DataFrame(issues)


# ── 4. Categorise issues ──────────────────────────────────────────────────────

def categorize(issues: pd.DataFrame) -> pd.DataFrame:
    """
    Label each issue with a fault type using simple rule-based logic:

    - equipment_fault : mean_actual is almost zero (< 5% of mean_forecast)
    - soiling         : mean_actual is 20-80% of forecast, issue lasts > 12 hours,
                        irradiance is reasonably good (> 200 W/m²)
    - weather_dip     : everything else (low irradiance or high cloud)
    """
    if issues.empty:
        return issues

    issues = issues.copy()
    conditions = []
    for _, row in issues.iterrows():
        ratio = row["mean_actual"] / (row["mean_forecast"] + 1e-9)

        if ratio < 0.05:
            conditions.append("equipment_fault")
        elif ratio < 0.80 and row["duration_hours"] > 12 and row["mean_irradiance"] > 200:
            conditions.append("soiling")
        else:
            conditions.append("weather_dip")

    issues["type"] = conditions
    return issues


# ── 5. Prioritise by cost ─────────────────────────────────────────────────────

def prioritize(issues: pd.DataFrame) -> pd.DataFrame:
    """
    For each issue, estimate:
      kwh_lost  = (mean_forecast – mean_actual) × duration_hours
      cost_lost = kwh_lost × PRICE_PER_KWH

    Then rank issues by cost_lost descending (rank 1 = worst first).

    Returns a tidy table with: issue_id, type, start, end, kwh_lost, cost_lost, rank
    """
    if issues.empty:
        return issues

    issues = issues.copy()
    issues["kwh_lost"] = (
        (issues["mean_forecast"] - issues["mean_actual"]) * issues["duration_hours"]
    ).clip(lower=0).round(2)

    issues["cost_lost"] = (issues["kwh_lost"] * PRICE_PER_KWH).round(2)

    issues = issues.sort_values("cost_lost", ascending=False).reset_index(drop=True)
    issues["rank"] = issues.index + 1

    # Return only the columns needed for the dashboard
    return issues[["issue_id", "type", "start", "end", "duration_hours",
                   "kwh_lost", "cost_lost", "rank"]]
