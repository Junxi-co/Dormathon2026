# ☀️ Solar Decision Assistant

> Hackathon prototype built at Dormathon 2026.

Helps a solar farm operations manager:
- **Forecast** expected power output from weather data
- **Flag** hours where actual output is far below forecast
- **Categorise** each problem (equipment fault / soiling / weather dip)
- **Rank** problems by estimated revenue lost
- **Explain** what happened and what to do next, in plain English

---

## Quick start

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd Dormathon2026

# 2. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set up your Grafilab API key
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux
# Then edit .env and add your GRAFILAB_API_KEY

# 5. Run the app
streamlit run app.py
```

If `data/solar_data.csv` is missing the app auto-generates 30 days of synthetic data.

---

## Project structure

```
app.py              – Streamlit dashboard (UI only)
src/
  pipeline.py       – Data loading, forecasting, issue detection & ranking
  explain.py        – LLM explanations via Grafilab API
data/
  solar_data.csv    – Solar output + weather (auto-generated if absent)
requirements.txt
.env.example        – Template for API credentials
.gitignore
README.md
```

---

## Tweaking things

| What to change | Where |
|---|---|
| Electricity price ($/kWh) | `PRICE_PER_KWH` constant at top of `src/pipeline.py` |
| Underperformance threshold | `threshold` parameter in `flag_issues()` |
| LLM model or base URL | `.env` file |

---

*Data is 100% synthetic – for demo purposes only.*
