"""
app.py
------
Member B's Streamlit app for "Tomorrow's Solar Plan".

Looks like a phone message card — big readable text, no charts-heavy layout,
no sidebar, no login.

Run with:   streamlit run app.py
"""

import streamlit as st
import pandas as pd

# ── Try to import the real pipeline; fall back gracefully if not ready ────────
try:
    from src.pipeline import run_scenario   # will exist when Member A is done
    PIPELINE_READY = True
except ImportError:
    PIPELINE_READY = False

from src.explain import build_briefing
from src.adapter import adapt   # converts pipeline output -> explain.py format


# ── Button names -> names that pipeline.run_scenario() understands ────────────
SCENARIO_KEYS = {
    "Normal day":     "normal",
    "Dusty panels":   "dusty",
    "Inverter fault": "fault",
}


# ── Hardcoded fallback data (matches CONTRACT columns) ────────────────────────
# Used whenever pipeline.py is not ready yet, so the app always runs.

FALLBACK_SCENARIOS = {
    "Normal day": {
        "plan": {
            "sun_summary":           "Mostly sunny with light cloud in the morning",
            "forecast_kwh":          22.0,
            "best_window":           "10 am – 1 pm",
            "battery_shortfall_kwh": 1.5,
            "grid_topup_hours":      "9 pm – 10 pm",
        },
        "issues": pd.DataFrame([{
            "type":      "weather_dip",
            "gap_pct":   15.0,
            "days":      1,
            "cost_lost": 1.10,
            "rank":      1,
        }]),
    },
    "Dusty panels": {
        "plan": {
            "sun_summary":           "Clear blue sky all day",
            "forecast_kwh":          26.0,
            "best_window":           "11 am – 2 pm",
            "battery_shortfall_kwh": 0.0,
            "grid_topup_hours":      "",
        },
        "issues": pd.DataFrame([{
            "type":      "soiling",
            "gap_pct":   34.0,
            "days":      5,
            "cost_lost": 8.40,
            "rank":      1,
        }]),
    },
    "Inverter fault": {
        "plan": {
            "sun_summary":           "Sunny and warm — great solar day",
            "forecast_kwh":          24.5,
            "best_window":           "10 am – 1 pm",
            "battery_shortfall_kwh": 4.2,
            "grid_topup_hours":      "7 pm – 10 pm",
        },
        "issues": pd.DataFrame([{
            "type":      "equipment_fault",
            "gap_pct":   91.0,
            "days":      1,
            "cost_lost": 12.60,
            "rank":      1,
        }]),
    },
}


# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Solar Plan",
    page_icon="☀️",
    layout="centered",   # phone-card feel — centred, not wide
)

# ── Custom CSS: big friendly text, highlighted Check card ─────────────────────
st.markdown("""
<style>
    /* Main title */
    .solar-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    /* The briefing card */
    .briefing-card {
        background: #fffbf0;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        font-size: 1.05rem;
        line-height: 1.7;
        border: 1px solid #f0e6c0;
        white-space: pre-wrap;        /* keep the newlines from build_briefing */
    }
    /* The Check / warning card gets its own colour */
    .check-card {
        background: #fff4e5;
        border-left: 5px solid #ff9900;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-top: 0.5rem;
    }
    .check-ok {
        background: #f0fff4;
        border-left: 5px solid #38a169;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Helper: get plan + issues for a scenario name ────────────────────────────

def get_scenario(name: str):
    """
    Returns (plan dict, issues DataFrame) in the format explain.py expects.
    Uses the real pipeline if available, otherwise the hardcoded fallback.
    """
    if PIPELINE_READY:
        # run_scenario returns (plan, issues) — Member A's function.
        # adapt() converts them to the keys explain.py needs.
        return adapt(*run_scenario(SCENARIO_KEYS[name]))
    else:
        # Fallback: use our hardcoded demo data
        data = FALLBACK_SCENARIOS.get(name, FALLBACK_SCENARIOS["Normal day"])
        return data["plan"], data["issues"]


# ── Session state: remember which scenario is active ─────────────────────────
if "scenario" not in st.session_state:
    st.session_state.scenario = "Normal day"


# ── Top section: title + scenario buttons ────────────────────────────────────
st.markdown('<p class="solar-title">☀️ Solar Plan</p>', unsafe_allow_html=True)
st.caption("Tap a scenario to see what the day looks like.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🌤️  Normal day", use_container_width=True):
        st.session_state.scenario = "Normal day"

with col2:
    if st.button("🌫️  Dusty panels", use_container_width=True):
        st.session_state.scenario = "Dusty panels"

with col3:
    if st.button("⚡  Inverter fault", use_container_width=True):
        st.session_state.scenario = "Inverter fault"

# Show which scenario is active
st.markdown(f"**Active scenario:** {st.session_state.scenario}")
st.divider()


# ── Build the briefing ────────────────────────────────────────────────────────
plan, issues = get_scenario(st.session_state.scenario)
briefing     = build_briefing(plan, issues)

# Split the briefing into the "Check" section and everything before it,
# so we can style the Check section differently.
CHECK_MARKERS = ("⚠️  Check:", "✅  Check:")

check_start = -1
for marker in CHECK_MARKERS:
    idx = briefing.find(marker)
    if idx != -1:
        check_start = idx
        break

if check_start == -1:
    # No Check section — show everything in one card
    st.markdown(f'<div class="briefing-card">{briefing}</div>', unsafe_allow_html=True)
else:
    before_check = briefing[:check_start].strip()
    check_text   = briefing[check_start:].strip()

    # Determine card colour: orange for warnings, green for all-clear
    is_warning = check_text.startswith("⚠️")
    check_class = "check-card" if is_warning else "check-ok"

    # Main card (Outlook + Do + Battery sections)
    st.markdown(f'<div class="briefing-card">{before_check}</div>', unsafe_allow_html=True)

    # Check card (styled separately for visual priority)
    st.markdown(f'<div class="{check_class}">{check_text}</div>', unsafe_allow_html=True)


# ── Optional small chart: forecast kWh vs a reference bar ────────────────────
with st.expander("📊 Quick forecast glance", expanded=False):
    # Simple bar showing tomorrow's forecast vs a "typical good day" baseline
    typical_kwh = plan.get("typical_kwh", 24.0)
    chart_data = pd.DataFrame({
        "kWh": [plan["forecast_kwh"], typical_kwh],
    }, index=["Tomorrow", "Typical good day"])
    st.bar_chart(chart_data, use_container_width=True, height=160)
    st.caption(
        f"Tomorrow: {plan['forecast_kwh']:.1f} kWh  |  "
        f"Typical: {typical_kwh:.1f} kWh"
    )


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()

# Show a small note if we're running on fallback data
if not PIPELINE_READY:
    st.info(
        "ℹ️ pipeline.py is not wired up yet — showing demo data. "
        "Once run_scenario() is ready, the live data will appear here automatically.",
        icon="🔧",
    )

st.caption("Built at Dormathon 2026 · No AI, no login, no database · Just your solar numbers.")