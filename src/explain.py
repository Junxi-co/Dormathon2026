"""
explain.py
----------
Calls the Grafilab LLM API to generate plain-English explanations for each
detected issue. Falls back to a simple template if the API is unavailable,
so the demo always works even without credentials.
"""

import os
import requests
from dotenv import load_dotenv

# Load .env file so GRAFILAB_API_KEY and other settings are available
load_dotenv()

# Read config from environment (set these in your .env file)
GRAFILAB_BASE_URL = os.getenv("GRAFILAB_BASE_URL", "https://api.grafilab.ai/v1")
GRAFILAB_MODEL    = os.getenv("GRAFILAB_MODEL",    "gpt-4o-mini")
GRAFILAB_API_KEY  = os.getenv("GRAFILAB_API_KEY",  "")


def explain_issue(issue: dict) -> str:
    """
    Given a dict describing one issue (from the prioritised table),
    ask the Grafilab LLM to explain what happened in 2-3 plain sentences
    and what the operator should do next.

    Falls back to a template string if the API call fails for any reason.

    Parameters
    ----------
    issue : dict
        Must contain keys: type, start, end, kwh_lost, cost_lost, rank

    Returns
    -------
    str
        A short plain-English explanation.
    """
    # Build a short prompt that any LLM will understand
    prompt = (
        f"You are advising a solar farm operator. "
        f"An issue was detected:\n"
        f"  Type       : {issue['type']}\n"
        f"  Start      : {issue['start']}\n"
        f"  End        : {issue['end']}\n"
        f"  Energy lost: {issue['kwh_lost']} kWh\n"
        f"  Revenue lost: ${issue['cost_lost']}\n"
        f"  Priority rank: {issue['rank']}\n\n"
        f"In 2-3 plain sentences (no jargon), explain what probably happened "
        f"and what the operator should do first. Be specific and actionable."
    )

    if not GRAFILAB_API_KEY:
        # No key configured – return a template so the demo still works
        return _fallback_explanation(issue)

    try:
        response = requests.post(
            f"{GRAFILAB_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {GRAFILAB_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GRAFILAB_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.4,
            },
            timeout=15,   # seconds – don't block the UI forever
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as err:
        # Any network error, bad key, timeout, etc. – show template instead
        print(f"[explain] API call failed ({err}), using fallback.")
        return _fallback_explanation(issue)


def _fallback_explanation(issue: dict) -> str:
    """
    A simple rule-based fallback so the UI always shows something useful
    even when the LLM API is not reachable.
    """
    templates = {
        "equipment_fault": (
            f"Output dropped to nearly zero between {issue['start']} and {issue['end']}, "
            f"losing about {issue['kwh_lost']} kWh (${issue['cost_lost']}). "
            "This looks like an equipment failure – check inverters and DC connections immediately."
        ),
        "soiling": (
            f"Output gradually fell below forecast from {issue['start']} to {issue['end']}, "
            f"costing roughly ${issue['cost_lost']}. "
            "Dust or dirt build-up on panels is the likely cause – schedule a cleaning."
        ),
        "weather_dip": (
            f"Low output between {issue['start']} and {issue['end']} aligns with low irradiance "
            f"or heavy cloud cover (${issue['cost_lost']} lost). "
            "No action needed – this is a normal weather effect."
        ),
    }
    return templates.get(
        issue["type"],
        f"An issue was detected from {issue['start']} to {issue['end']} "
        f"with {issue['kwh_lost']} kWh lost (${issue['cost_lost']}). Please review manually."
    )
