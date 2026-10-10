"""
adapter.py
----------
Translates the output of pipeline.run_scenario() into the format that
explain.build_briefing() and app.py expect.

Why this exists
---------------
pipeline.py returns a `plan` dict with keys like df / optimize / model_mae,
and an `issues` table with start / end / duration_hours / kwh_lost.
explain.py expects a `plan` dict with sun_summary / forecast_kwh /
best_window / ... and an `issues` table with gap_pct / days / cost_lost.
This file bridges the two so neither teammate has to rewrite their code.

Usage (in app.py):
    from src.adapter import adapt
    plan, issues = adapt(*run_scenario(name))
"""

import pandas as pd

ISSUE_COLUMNS = ["type", "gap_pct", "days", "cost_lost", "rank"]


# ── Small helpers ─────────────────────────────────────────────────────────────

def _fmt_hour(ts) -> str:
    """Timestamp -> '10 am' / '1 pm'."""
    ts = pd.Timestamp(ts)
    hour = ts.hour % 12 or 12
    return f"{hour} {'am' if ts.hour < 12 else 'pm'}"


def _tomorrow(df: pd.DataFrame) -> pd.DataFrame:
    """'Tomorrow' = the last calendar day in the data (same rule as pipeline.optimize)."""
    last_day = df["timestamp"].dt.date.max()
    return df[df["timestamp"].dt.date == last_day]


def _sun_summary(day: pd.DataFrame) -> str:
    """Turn average daytime cloud cover into a short plain-English phrase."""
    daytime = day[day["irradiance"] > 0]
    if daytime.empty:
        daytime = day
    cloud = float(daytime["cloud_cover"].mean())
    if cloud < 0.20:
        return "Mostly sunny"
    if cloud < 0.40:
        return "Partly cloudy"
    return "Mostly cloudy"


def _best_window(optimize: dict) -> str:
    """Format pipeline's best 3-hour window as '10 am – 1 pm'."""
    w = optimize.get("best_solar_window", {})
    if w.get("start") in (None, "N/A"):
        return "11 am – 2 pm"   # sensible midday fallback
    start = pd.Timestamp(w["start"])
    # pipeline stores the START of the last hour, so add 1 h for the window end
    end = pd.Timestamp(w["end"]) + pd.Timedelta(hours=1)
    return f"{_fmt_hour(start)} – {_fmt_hour(end)}"


# ── Plan adapter ──────────────────────────────────────────────────────────────

def adapt_plan(plan: dict) -> dict:
    """
    Return a plan dict that has every key explain.py / app.py need.
    Keeps the original keys (df, optimize, model_mae, ...) as well.
    Safe to call on a plan that is already in the explain format.
    """
    if "sun_summary" in plan:          # already the right shape (e.g. fallback data)
        return plan

    df  = plan["df"]
    opt = plan.get("optimize", {})
    day = _tomorrow(df)

    topup     = opt.get("battery_topup", {})
    shortfall = topup.get("est_shortfall_kwh", 0.0) if topup.get("suggested") else 0.0
    # "14:00–16:00 (cheap-rate)" -> "14:00–16:00"
    topup_hours = str(topup.get("window", "")).split(" (")[0]

    daily_forecast = df.groupby(df["timestamp"].dt.date)["forecast"].sum()

    adapted = dict(plan)
    adapted.update(
        sun_summary=_sun_summary(day),
        forecast_kwh=float(day["forecast"].sum()),
        best_window=_best_window(opt),
        battery_shortfall_kwh=float(shortfall),
        grid_topup_hours=topup_hours,
        typical_kwh=float(daily_forecast.median()),   # for the app's comparison bar
    )
    return adapted


# ── Issues adapter ────────────────────────────────────────────────────────────

def adapt_issues(issues: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert pipeline's issue table (start, end, duration_hours, kwh_lost, ...)
    into explain's table: type, gap_pct, days, cost_lost, rank.
    Safe to call on a table that is already in the explain format.
    """
    if issues is not None and "gap_pct" in issues.columns:
        return issues                                   # already the right shape
    if issues is None or issues.empty:
        return pd.DataFrame(columns=ISSUE_COLUMNS)

    rows = []
    for _, r in issues.iterrows():
        start = pd.Timestamp(r["start"])
        end   = pd.Timestamp(r["end"])

        # How far below forecast was output during the event (daytime hours only)?
        window = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)
                    & (df["forecast"] > 1)]
        expected = float(window["forecast"].sum())
        gap = 100 * (1 - float(window["actual_output"].sum()) / expected) if expected > 0 else 0.0
        gap = min(max(gap, 0.0), 100.0)

        days = (end.normalize() - start.normalize()).days + 1   # calendar days touched

        rows.append({
            "type":      r["type"],
            "gap_pct":   round(gap, 1),
            "days":      days,
            "cost_lost": float(r["cost_lost"]),
            "rank":      int(r["rank"]),
        })

    return pd.DataFrame(rows, columns=ISSUE_COLUMNS)


# ── One-call convenience ──────────────────────────────────────────────────────

def adapt(plan: dict, issues: pd.DataFrame) -> tuple:
    """adapt(*run_scenario(name)) -> (plan, issues) in the explain.py format."""
    df = plan["df"] if "df" in plan else None
    new_plan = adapt_plan(plan)
    new_issues = adapt_issues(issues, df) if df is not None else issues
    return new_plan, new_issues
