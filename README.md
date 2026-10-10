# Solar Prediction Model

A hackathon prototype for **Track 1: Predictive Model (renewable energy forecasting and optimization)**.

## What it does

For a home solar owner, the tool:
1. Forecasts tomorrow's solar output.
2. Flags and categorizes problems that reduce output.
3. Ranks those problems by how much money they cost.
4. Tells the owner what to do, in plain language.

## The problem and the user

**User:** A home solar owner who does not closely watch their system.
**Problem:** Output can drop for days before the owner notices and the owner may not know the cause or what to do about it.

**The question we are trying to answer:** Does the model help someone make a better decision, and can we prove it? Our proof is in `results/metrics.md`

## How to install and run

```
git clone <repo-link>
py -m pip install -r RequiredLib.txt
py -m streamlit run app.py
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

## How it addresses Detect, Categorize, Prioritize, Explain

| Step | What it means | How we do it |
|------|---------------|--------------|
| **Detect** | Notice that output is lower than it should be | [HOW WE DETECT, TO CONFIRM] |
| **Categorize** | Say what kind of problem it is | [PROBLEM TYPES WE COVER, TO CONFIRM] |
| **Prioritize** | Rank problems by money lost | [HOW MONEY LOST IS CALCULATED, see docs/assumptions.md, TO CONFIRM] |
| **Explain** | Tell the owner what to do in plain language | [HOW THE MESSAGE IS GENERATED, TO CONFIRM] |
