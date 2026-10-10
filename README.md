# Solar Prediction Model

A hackathon prototype for Track 1: Predictive Model (renewable energy forecasting and optimization).

Deployment Link: https://dormathon-modelprototype.streamlit.app/

Clone Repo method below.

## What it does

For a home solar owner, the tool:
1. Forecasts tomorrow's solar output.
2. Flags and categorizes problems that reduce output.
3. Ranks those problems by how much money they cost.
4. Tells the owner what to do, in plain language.

There is no dashboard and no login. The owner gets a short answer they can act on.

##The problem and the user

User: A home solar owner who does not closely watch their system.
Problem:Output can drop for days before the owner notices, and the owner may not know the cause or what to do about it. A 2015 [Pecan Street study](https://pecanstreet.org/tags/app) found that minor solar faults can cut production for days or weeks, and in most cases the homeowners had no idea. Its CEO called it "a $5 issue to fix" that still loses the owner value. One homeowner reported a big drop in output that only came to light through a large utility bill ([The Cool Down, 2026](https://www.thecooldown.com/green-home/tesla-solar-output-repair-case-stalled/)). Another found their system had not reported production since 2021 ([The Cool Down](https://www.thecooldown.com/?p=790893)). Existing inverter apps [WHAT THEY DO AND DON'T DO, TO CONFIRM FROM OUR COMPARISON CHECKLIST].Evidence from real people: 

**The question we are trying to answer:** Does the model help someone make a better decision, and can we prove it? Our proof is in `results/metrics.md`

## How to install and run

```
First Method: Run on terminal
git clone <repo-link>
py -m pip install -r requirements.txt
py -m streamlit run app.py

Second Method: Deployment Link
https://dormathon-modelprototype.streamlit.app/
```

The app opens in your browser. Press one of the three scenario buttons to see the result.

## Repo structure

```
.
├── app.py                 # The Streamlit app (demo)
├── src/                   # Model and logic code
├── results/
│   └── metrics.md         # Proof numbers used in the pitch
├── docs/
│   ├── interview_guide.md # Interview questions, notes template, app comparison
│   ├── assumptions.md     # Impact estimate assumptions (all TO CONFIRM until sourced)
│   ├── demo_script.md     # 2-minute pitch script
│   ├── qa_prep.md         # Likely judge questions and draft answers
│   └── slides_outline.md  # 5-slide outline
└── README.md
```
 How it addresses Detect, Categorize, Prioritize, Explain

| Step | What it means | How we do it |
|------|---------------|--------------|
| **Detect** | Notice that output is lower than it should be | Compares actual output with what we expect for that hour. On our test data it caught 2 of 2 injected faults, with 1 false alarm on clean data, and still caught the fault with noise added and 5% of rows dropped. [DETECTION METHOD, e.g. threshold or rule, TO CONFIRM with Member A] |
| **Categorize** | Say what kind of problem it is | Two problem types: dust on the panels (soiling) and an equipment fault (inverter). The Check card turns orange for a problem and green when all is clear. [ADD ANY OTHER TYPES THE CODE HANDLES, TO CONFIRM] |
| **Prioritize** | Rank problems by money lost | Money lost per day = daily output x dust loss x tariff, then x days of earlier detection (see `docs/assumptions.md`). Example home, assumed: a fault costs about RM 154 over 14 days, and one cleaning pays for itself after about 60 days of 22% dust loss. [CONFIRM THE APP SHOWS A RANKING, TO CONFIRM] |
| **Explain** | Tell the owner what to do in plain language | One briefing card with Outlook (tomorrow's expected output), Check (the problem found), Do (what to do) and Battery (how to use stored power). No login, no dashboard. [HOW THE MESSAGE IS GENERATED, e.g. written by rules in `src/explain.py`, TO CONFIRM] |

## What we deliberately did not build

We built only what is needed to prove the idea and run the demo.

- **No login or user accounts.** The owner should get an answer immediately.
- **No generic dashboard.** The owner needs a decision, not a page of charts.
- **No live connection to a real inverter.** [TO CONFIRM: whether we use real or simulated data]
- **No mobile app or notifications.** The demo is a single web app.
- **No deep learning model.** [REASON, TO CONFIRM]

## Data and honesty note

All impact numbers are assumptions listed in `docs/assumptions.md` and are marked TO CONFIRM until we have a source.

## Team

- Member A: Jun Xi
- Member B: Hong Jun 
- Member C: Cheng Hao
