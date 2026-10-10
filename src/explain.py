"""
explain.py
----------
Member B's file.

Provides build_briefing(plan, issues) -> str

Returns a friendly, plain-English message a homeowner can read and act on.
No AI, no API calls — just templates filled with real numbers.

CONTRACT columns used
---------------------
plan dict keys:
    sun_summary          str   e.g. "Partly cloudy, clearing by noon"
    forecast_kwh         float Expected solar energy tomorrow (kWh)
    best_window          str   e.g. "10 am – 1 pm"
    battery_shortfall_kwh float Extra energy needed from the grid (0 = none)
    grid_topup_hours     str   e.g. "7 pm – 9 pm"

issues DataFrame columns (top-ranked row is used):
    type         str   equipment_fault | soiling | shading | weather_dip
    gap_pct      float How far below normal output was (0-100 %)
    days         int   How many days the issue has been present
    cost_lost    float Estimated $ lost so far
    rank         int   1 = worst issue (we only show rank 1)
"""

import pandas as pd


# ── Main public function ──────────────────────────────────────────────────────

def build_briefing(plan: dict, issues: pd.DataFrame) -> str:
    """
    Build a short, friendly briefing string for tomorrow.

    Parameters
    ----------
    plan : dict
        Tomorrow's forecast summary (see CONTRACT above).
    issues : pd.DataFrame
        Prioritised issue table. May be empty. We only read rank-1 row.

    Returns
    -------
    str
        Multi-line plain-English message ready to display in the app.
    """

    lines = []   # We'll collect sections and join them at the end.

    # ── Section 1: Sun & Forecast ─────────────────────────────────────────────
    lines.append("☀️  Tomorrow's Solar Outlook")
    lines.append(
        f"Conditions: {plan['sun_summary']}. "
        f"Your panels should generate about {plan['forecast_kwh']:.1f} kWh."
    )
    lines.append("")   # blank line between sections

    # ── Section 2: Best window for heavy appliances ───────────────────────────
    lines.append("✅  Do:")
    lines.append(
        f"Run the dishwasher, washing machine, or EV charger between "
        f"{plan['best_window']} — that's when your solar will be strongest."
    )
    lines.append("")

    # ── Section 3: Battery / grid top-up (only shown when needed) ────────────
    shortfall = plan.get("battery_shortfall_kwh", 0)
    if shortfall > 0:
        lines.append("🔋  Battery Advice:")
        lines.append(
            f"Your battery may run short by about {shortfall:.1f} kWh tonight. "
            f"The grid will top it up around {plan['grid_topup_hours']} — "
            f"that's normal, nothing to do."
        )
        lines.append("")

    # ── Section 4: Issue check ────────────────────────────────────────────────
    if issues.empty:
        lines.append("✅  Check:")
        lines.append("Everything looks normal — no issues to report.")
    else:
        # Get the single most important issue (rank 1)
        top = issues.sort_values("rank").iloc[0]

        issue_type = top["type"]
        gap_pct    = float(top["gap_pct"])
        days       = int(top["days"])
        cost_lost  = float(top["cost_lost"])

        if issue_type == "weather_dip":
            # Weather dips need no action
            lines.append("✅  Check:")
            lines.append(
                "Your panels dipped a little recently, but it's just the weather — "
                "clouds or lower sun. No action needed."
            )
        else:
            # All other issue types need the homeowner to act
            lines.append("⚠️  Check:")
            lines.append(_issue_action(issue_type, gap_pct, days, cost_lost))
            lines.append("")
            lines.append("🔍  Why:")
            lines.append(_issue_evidence(issue_type, gap_pct, days, cost_lost))

    return "\n".join(lines)


# ── Issue action templates ────────────────────────────────────────────────────

def _issue_action(issue_type: str, gap_pct: float, days: int, cost_lost: float) -> str:
    """
    Return a one-sentence action recommendation for the homeowner.
    One template per issue type — plain, non-technical language.
    """
    if issue_type == "equipment_fault":
        return (
            f"Your inverter or a panel connection may have a fault "
            f"(output is {gap_pct:.0f}% below normal for {days} day(s), "
            f"costing roughly ${cost_lost:.2f}). "
            f"Call your installer to inspect the system."
        )
    elif issue_type == "soiling":
        return (
            f"Your panels look like they need a clean "
            f"(output is {gap_pct:.0f}% below normal for {days} day(s), "
            f"costing roughly ${cost_lost:.2f}). "
            f"Rinse them with a hose or book a panel clean."
        )
    elif issue_type == "shading":
        return (
            f"Something may be shading your panels in the morning or afternoon "
            f"(output is {gap_pct:.0f}% below normal for {days} day(s), "
            f"costing roughly ${cost_lost:.2f}). "
            f"Check for overgrown trees or new objects casting a shadow."
        )
    else:
        # Catch-all for any future issue types
        return (
            f"Output is {gap_pct:.0f}% below normal for {days} day(s) "
            f"(~${cost_lost:.2f} lost). Please check your panels or call your installer."
        )


def _issue_evidence(issue_type: str, gap_pct: float, days: int, cost_lost: float) -> str:
    """
    Return a plain-language 'Why' sentence that explains the evidence
    behind the issue detection — no jargon.
    """
    if issue_type == "equipment_fault":
        return (
            f"Your system's actual output suddenly dropped to almost nothing "
            f"for {days} day(s) even when the sky was clear and sunny. "
            f"Weather alone can't explain a drop that large ({gap_pct:.0f}% below expected), "
            f"so the most likely cause is a hardware problem."
        )
    elif issue_type == "soiling":
        return (
            f"Over the last {days} day(s), output has been creeping down slowly "
            f"({gap_pct:.0f}% below expected) even on good-weather days. "
            f"A gradual slide like this usually means dust, bird droppings, or grime "
            f"building up on the panel surface."
        )
    elif issue_type == "shading":
        return (
            f"Output dips at certain times of day ({gap_pct:.0f}% below expected) "
            f"even though the overall weather looks fine. "
            f"A consistent time-based pattern over {days} day(s) suggests something "
            f"is blocking direct sunlight on part of your roof."
        )
    else:
        return (
            f"Output has been {gap_pct:.0f}% below the expected level for {days} day(s), "
            f"which doesn't match the weather forecast for your area."
        )


# ── Standalone test (run: python src/explain.py) ─────────────────────────────

if __name__ == "__main__":
    # Hardcoded example that matches the CONTRACT so we can test
    # without waiting for pipeline.py to be wired up.

    example_plan = {
        "sun_summary":           "Partly cloudy, clearing by noon",
        "forecast_kwh":          18.5,
        "best_window":           "10 am – 1 pm",
        "battery_shortfall_kwh": 2.3,
        "grid_topup_hours":      "8 pm – 10 pm",
    }

    # Example 1 — soiling issue
    example_issues_soiling = pd.DataFrame([{
        "type":      "soiling",
        "gap_pct":   34.0,
        "days":      5,
        "cost_lost": 8.40,
        "rank":      1,
    }])

    # Example 2 — equipment fault
    example_issues_fault = pd.DataFrame([{
        "type":      "equipment_fault",
        "gap_pct":   91.0,
        "days":      1,
        "cost_lost": 12.60,
        "rank":      1,
    }])

    # Example 3 — weather dip only (no action needed)
    example_issues_weather = pd.DataFrame([{
        "type":      "weather_dip",
        "gap_pct":   20.0,
        "days":      1,
        "cost_lost": 1.20,
        "rank":      1,
    }])

    # Example 4 — shading issue
    example_issues_shading = pd.DataFrame([{
        "type":      "shading",
        "gap_pct":   28.0,
        "days":      3,
        "cost_lost": 5.10,
        "rank":      1,
    }])

    # Example 5 — no shortfall, no issues
    example_plan_clean = {**example_plan, "battery_shortfall_kwh": 0}

    print("=" * 60)
    print("SCENARIO: Soiling")
    print("=" * 60)
    print(build_briefing(example_plan, example_issues_soiling))

    print("\n" + "=" * 60)
    print("SCENARIO: Equipment Fault")
    print("=" * 60)
    print(build_briefing(example_plan, example_issues_fault))

    print("\n" + "=" * 60)
    print("SCENARIO: Weather Dip (no action needed)")
    print("=" * 60)
    print(build_briefing(example_plan, example_issues_weather))

    print("\n" + "=" * 60)
    print("SCENARIO: Shading")
    print("=" * 60)
    print(build_briefing(example_plan, example_issues_shading))

    print("\n" + "=" * 60)
    print("SCENARIO: Perfect day (no issues, no shortfall)")
    print("=" * 60)
    print(build_briefing(example_plan_clean, pd.DataFrame()))
