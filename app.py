"""
app.py
------
Streamlit dashboard for the Solar Decision Assistant.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd

# Our own modules
from src.pipeline import load_data, train_and_forecast, flag_issues, categorize, prioritize
from src.explain  import explain_issue

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Solar Decision Assistant",
    page_icon="☀️",
    layout="wide",
)

st.title("☀️ Solar Decision Assistant")
st.caption("Hackathon prototype – forecast, detect, explain, and prioritise solar farm issues.")

# ── Load and process data (cached so the page doesn't recompute every click) ──
@st.cache_data
def run_pipeline():
    """Run all pipeline steps once and cache the results."""
    df               = load_data()
    df, model_mae, baseline_mae = train_and_forecast(df)
    raw_issues       = flag_issues(df)
    categorised      = categorize(raw_issues)
    ranked           = prioritize(categorised)
    return df, model_mae, baseline_mae, ranked

df, model_mae, baseline_mae, ranked = run_pipeline()

# ── Section 1: Model quality ───────────────────────────────────────────────────
st.subheader("📊 Model vs Baseline")
st.metric(
    label="RandomForest MAE (lower is better)",
    value=f"{model_mae} kWh",
    delta=f"{round(baseline_mae - model_mae, 3)} kWh better than yesterday-naive baseline",
    delta_color="normal",
)
st.caption(f"Naive baseline (previous day's value) MAE: {baseline_mae} kWh")

st.divider()

# ── Section 2: Actual vs Forecast chart ───────────────────────────────────────
st.subheader("📈 Actual vs Forecast Output")

# Streamlit's line_chart needs a DataFrame indexed by time
chart_df = df.set_index("timestamp")[["actual_output", "forecast"]].rename(
    columns={"actual_output": "Actual (kWh)", "forecast": "Forecast (kWh)"}
)
st.line_chart(chart_df, use_container_width=True)

st.divider()

# ── Section 3: Ranked issues table ────────────────────────────────────────────
st.subheader("🚨 Detected Issues – Ranked by Revenue Lost")

if ranked.empty:
    st.success("No significant issues detected. 🎉")
else:
    # Display a styled table (Streamlit will format it nicely)
    display_cols = ["rank", "type", "start", "end", "duration_hours", "kwh_lost", "cost_lost"]
    st.dataframe(
        ranked[display_cols].style.format({
            "kwh_lost":  "{:.2f}",
            "cost_lost": "${:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ── Section 4: Explanations for each issue ────────────────────────────────
    st.subheader("💬 Plain-English Explanations")
    st.caption("What happened and what to do – powered by LLM (falls back to templates if API is unavailable).")

    for _, row in ranked.iterrows():
        issue_dict = row.to_dict()

        # Convert Timestamps to readable strings for the LLM prompt
        issue_dict["start"] = str(issue_dict["start"])
        issue_dict["end"]   = str(issue_dict["end"])

        with st.expander(
            f"Rank #{int(row['rank'])}  |  {row['type']}  |  "
            f"${row['cost_lost']:.2f} lost  |  {row['start']} → {row['end']}",
            expanded=(row["rank"] == 1),   # expand the top issue by default
        ):
            with st.spinner("Getting explanation…"):
                explanation = explain_issue(issue_dict)
            st.write(explanation)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Built at Dormathon 2026 · Data is synthetic for demo purposes.")
