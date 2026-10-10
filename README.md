# ☀️ Tomorrow's Solar Plan: Solar Prediction Model

**Dormathon 2026 · Track 1: Predictive Model (Predict Early, Decide Better)**

🔗 **Live app:** https://dormathon-modelprototype.streamlit.app/

A prototype that predicts tomorrow's solar output, spots problems that quietly reduce it, and tells a home solar owner what to do about them in plain language.

---

## Table of contents

1. [The problem and the user](#the-problem-and-the-user)
2. [What it does](#what-it-does)
3. [How to run](#how-to-run)
4. [How it works: Detect, Categorize, Prioritize, Explain](#how-it-works-detect-categorize-prioritize-explain)
5. [Results](#results)
6. [Repo structure](#repo-structure)
7. [What we deliberately did not build](#what-we-deliberately-did-not-build)
8. [Data and honesty note](#data-and-honesty-note)
9. [Limitations](#limitations)
10. [Team](#team)

---

## The problem and the user

**User:** a home solar owner who does not closely watch their system.

**Problem:** output can drop for days before the owner notices, and the owner may not know the cause or what to do about it.

Evidence from real people:

- A 2015 [Pecan Street study](https://pecanstreet.org/tags/app) found that minor solar faults can cut production for days or weeks, and in most cases the homeowners had no idea. Its CEO called it "a $5 issue to fix" that still loses the owner value.
- One homeowner reported a big drop in output that only came to light through a large utility bill ([The Cool Down, 2026](https://www.thecooldown.com/green-home/tesla-solar-output-repair-case-stalled/)).
- Another found their system had not reported production since 2021 ([The Cool Down](https://www.thecooldown.com/?p=790893)).

**The question we are trying to answer:** does the model help someone make a better decision, and can we prove it? Our proof is in [`results/metrics.md`](results/metrics.md).

## What it does

For a home solar owner, the tool:

1. **Forecasts** tomorrow's solar output.
2. **Flags and categorizes** problems that reduce output.
3. **Ranks** those problems by how much money they cost.
4. **Tells the owner what to do**, in plain language.

There is no dashboard and no login. The owner gets a short answer they can act on.

The app shows one briefing card with four parts: **Outlook** (tomorrow's expected output), **Do** (the best time to run heavy appliances), **Battery** (whether a grid top-up is needed), and **Check** (the problem found and why). The Check card is orange for a problem and green when all is clear.

---

## How to run

### Option 1: Open the live app

https://dormathon-modelprototype.streamlit.app/

Press one of the three scenario buttons (**Normal day**, **Dusty panels**, **Inverter fault**) to see the result. If the app shows a "wake up" button, click it and wait a moment.

### Option 2: Run it on your computer

Requires Python 3.10 or newer and Git. On Mac or Linux, use `python3` instead of `py`.

```
git clone <repo-link>
cd <repo-folder>
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Run the last two commands from the project's top-level folder (the one containing `app.py`). The app opens in your browser.

### Optional: print the evaluation report

```
py -m src.evaluate
```

This prints the accuracy and detection results and writes them to `results/metrics.md`.

---

## How it works: Detect, Categorize, Prioritize, Explain

| Step | What it means | How we do it |
|------|---------------|--------------|
| **Forecast** | Know what output to expect | A Random Forest model (scikit-learn) learns from irradiance, cloud cover, temperature and hour of day. It is trained on the first 40 days and tested on the last 20, and compared against a simple "same hour yesterday" baseline. |
| **Detect** | Notice that output is lower than it should be | Compares actual output with the forecast for each hour. An hour is flagged when output is below 40% of forecast for at least 3 hours in a row, or below 90% of forecast for at least 5 hours in a row. Flagged periods less than 14 hours apart are merged, so multi-day dust build-up shows up as one issue. |
| **Categorize** | Say what kind of problem it is | Simple rules sort each issue into **equipment fault** (output near zero despite good sun), **soiling** (a long, gradual shortfall in clear weather), **shading** (a short dip of 4 hours or less), or **weather dip** (everything else, no action needed). |
| **Prioritize** | Rank problems by money lost | Energy lost = (forecast − actual) × hours affected. Money lost = energy lost × the electricity price (US$0.12/kWh in the code). Issues are ranked by money lost, and the app shows the top-ranked one. |
| **Explain** | Tell the owner what to do in plain language | Message templates in `src/explain.py` fill in the real numbers (gap, days affected, money lost). No AI service or API is used. |

The **Do** and **Battery** advice comes from a schedule optimiser that finds the best 3-hour solar window for tomorrow and estimates whether the battery will fall short in the evening.

**Impact example (assumed):** for an example home, a fault costs about RM 154 over 14 days, and one cleaning pays for itself after about 60 days of 22% dust loss. All impact assumptions are listed in [`docs/assumptions.md`](docs/assumptions.md).

---

## Results

Measured on our test data (details in [`results/metrics.md`](results/metrics.md)):

- **Detection:** caught 2 of 2 injected faults (one dust build-up, one equipment fault).
- **False alarms:** 1 on the clean "normal" scenario.
- **Robustness:** still caught the fault with extra noise added and 5% of rows dropped.
- **Forecast accuracy:** the model is compared against the "same hour yesterday" baseline; see `results/metrics.md` for the numbers.

---

## Repo structure

```
.
├── app.py                  # The Streamlit app (demo)
├── requirements.txt        # Python libraries to install
├── .gitignore              # Keeps cache and secret files out of Git
├── data/                   # Three simulated datasets: normal, dusty, fault
├── src/
│   ├── pipeline.py         # Data loading, forecast, detection, ranking, schedule
│   ├── adapter.py          # Converts pipeline output into the briefing format
│   ├── explain.py          # Turns results into the plain-language briefing
│   └── evaluate.py         # Accuracy, detection, false alarm and robustness tests
├── results/
│   └── metrics.md          # Proof numbers used in the pitch
├── docs/
│   ├── interview_guide.md  # Interview questions, notes template, app comparison
│   ├── assumptions.md      # Impact estimate assumptions
│   ├── demo_script.md      # 2-minute pitch script
│   ├── qa_prep.md          # Likely judge questions and draft answers
│   └── slides_outline.md   # 5-slide outline
└── README.md
```

---

## What we deliberately did not build

We built only what is needed to prove the idea and run the demo.

- **No login or user accounts.** The owner should get an answer immediately.
- **No generic dashboard.** The owner needs a decision, not a page of charts.
- **No live connection to a real inverter.** The demo uses simulated data.
- **No mobile app or notifications.** The demo is a single web app.
- **No deep learning model.** A Random Forest is enough for 60 days of hourly data, trains in seconds, and is easy to explain.

## Data and honesty note

- All data is **simulated**: 60 days of hourly readings (irradiance, cloud cover, temperature, output). The "dusty" scenario has a slow output decline injected, and the "fault" scenario has a sudden near-zero drop injected.
- The faults were injected by us, so detection results show the method works on known problems, not that it works on every real system.
- All impact numbers are assumptions listed in `docs/assumptions.md` until we have a source.

## Limitations

- Data is simulated, not from a real solar installation, and the detection rules are tuned for our three demo scenarios.
- The simulated system is sized like a small solar array, so the kWh numbers are larger than a typical home. The logic is the same at any size.
- The battery size, evening demand and electricity tariffs are assumptions.
- The categorization rules are simple and may confuse some problems (for example, shading versus a weather dip).

## Team

| Member | Name | Focus |
|--------|------|-------|
| A | Jun Xi | Model and logic (`src/pipeline.py`, `src/evaluate.py`) |
| B | Hong Jun | App and briefing (`app.py`, `src/explain.py`) |
| C | Cheng Hao | Research, docs and pitch |