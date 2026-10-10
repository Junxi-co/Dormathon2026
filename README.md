 Tomorrow's Solar Plan

A hackathon prototype for Track 1: Predictive Model (renewable energy forecasting and optimization).

 What it does

For a home solar owner, the tool:
1. Forecasts tomorrow's solar output.
2. Flags and categorizes problems that reduce output.
3. Ranks those problems by how much money they cost.
4. Tells the owner what to do, in plain language.

There is no dashboard and no login. The owner gets a short answer they can act on.

The problem and the user

User: A home solar owner who does not closely watch their system.
Problem:Output can drop for days before the owner notices, and the owner may not know the cause or what to do about it. A 2015 [Pecan Street study](https://pecanstreet.org/tags/app) found that minor solar faults can cut production for days or weeks, and in most cases the homeowners had no idea. Its CEO called it "a $5 issue to fix" that still loses the owner value. One homeowner reported a big drop in output that only came to light through a large utility bill ([The Cool Down, 2026](https://www.thecooldown.com/green-home/tesla-solar-output-repair-case-stalled/)). Another found their system had not reported production since 2021 ([The Cool Down](https://www.thecooldown.com/?p=790893)). Existing inverter apps [WHAT THEY DO AND DON'T DO, TO CONFIRM FROM OUR COMPARISON CHECKLIST].Evidence from real people: 

**The question we are trying to answer:** Does the model help someone make a better decision, and can we prove it? Our proof is in `results/metrics.md` [TO CONFIRM THIS FILE EXISTS AND IS FILLED IN].

## How to install and run

```
pip install -r requirements.txt
streamlit run app.py
```

Python version: [TO CONFIRM]

The app opens in your browser. Press one of the three scenario buttons to see the result.

## Repo structure

[TO CONFIRM: check this against the actual folders before submitting]

```
.
├── app.py                 # The Streamlit app (demo)
├── requirements.txt       # Python dependencies
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
| **Detect** | Notice that output is lower than it should be | [HOW WE DETECT, TO CONFIRM] |
| **Categorize** | Say what kind of problem it is | [PROBLEM TYPES WE COVER, TO CONFIRM] |
| **Prioritize** | Rank problems by money lost | [HOW MONEY LOST IS CALCULATED, see docs/assumptions.md, TO CONFIRM] |
| **Explain** | Tell the owner what to do in plain language | [HOW THE MESSAGE IS GENERATED, TO CONFIRM] |

## What we deliberately did not build

We built only what is needed to prove the idea and run the demo. [EDIT THIS LIST TO MATCH REALITY]

- **No login or user accounts.** The owner should get an answer immediately.
- **No generic dashboard.** The owner needs a decision, not a page of charts.
- **No live connection to a real inverter.** [TO CONFIRM: whether we use real or simulated data]
- **No mobile app or notifications.** The demo is a single web app.
- **No deep learning model.** [REASON, TO CONFIRM]

## Data and honesty note

[DESCRIBE THE DATA WE USE, real or simulated, and where it came from, TO CONFIRM.]
All impact numbers are assumptions listed in `docs/assumptions.md` and are marked TO CONFIRM until we have a source.

## Team

- Member A: Jun Xi, 
- Member B: Hong Jun, 
- Member C: Cheng Hao, product, validation and pitch
