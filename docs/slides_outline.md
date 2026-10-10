# Slides Outline (5 slides)

Numbers marked **[DATA]** were measured by us from the CSV files. **[METRICS]** come from `results/metrics.md`. **[ASSUMED]** come from `docs/assumptions.md` and must be said out loud as assumptions. Anything marked TO CONFIRM must be checked before it goes on a slide.

---

## Slide 1: The Problem

**Headline:** A solar system can lose a fifth of its output for days, and nothing tells the owner.

- **~22%** below normal for one dusty week. About 540 kWh lost, Feb 10-16. **[DATA]**
- **~97%** drop during an inverter fault. Jan 31, 10 hours: 9 kWh made vs ~302 expected. **[DATA]**
- Public example: a 2015 Pecan Street study found small solar faults went unnoticed for days or weeks. Its CEO called one "a $5 issue to fix". ([source](https://pecanstreet.org/tags/app))
- We have not interviewed owners, so we do not claim a quote.

*Footer:* Source: our 60-day hourly test data (simulated? TO CONFIRM).

---

## Slide 2: The Gap

**Headline:** Existing apps show what already happened, not what to do next.

- **What inverter apps do:** [WHAT WE SAW, TO CONFIRM]
- **What they don't do:** [FROM OUR COMPARISON CHECKLIST, TO CONFIRM]
- **Our app, one screen:**
  - Outlook: tomorrow's expected output
  - Check: the problem found, and its cost
  - Do: what to do about it
  - Battery: how to use stored power

*Footer:* Public example: Pecan Street, 2015, owners did not notice small faults for days or weeks.

---

## Slide 3: The Demo

**Headline:** One screen, three buttons, a plain-language answer.

- **Normal day:** [WHAT THE BRIEFING SAYS, TO CONFIRM]
- **Dusty panels:** [SOILING FLAGGED, WHAT IT SAYS, TO CONFIRM]
- **Inverter fault:** [FAULT FLAGGED, WHAT IT SAYS, TO CONFIRM]
- The Check card turns orange when a problem is found and green when all is clear. No login.

*Note:* Live demo. Run each button once after confirming the live pipeline is connected. Do not quote the app's built-in fallback numbers.

---

## Slide 4: The Proof

**Headline:** On test data with faults we added on purpose, the tool found both and named them correctly.

- **2 of 2** injected faults caught, with the right type: soiling and equipment fault. **[METRICS]**
- **54.4% lower** forecast error on normal days vs "same hour yesterday". **[METRICS]**
- **46.9% lower** on the fault scenario. **[METRICS]**
- **Worse** on the dusty scenario. Say so if asked. **[METRICS]**
- **1 false alarm** on clean data. **[METRICS]**
- **Robust:** fault still caught with noise and 5% of rows dropped. **[METRICS]**

*Footer:* Source: `results/metrics.md`. Data: 60 days hourly, Jan 1 to Mar 1, 2026 [HONEST DESCRIPTION, e.g. simulated, TO CONFIRM].

---

## Slide 5: Impact and Next Steps

**Headline:** The app tells an owner when dust is worth cleaning, and catches faults that cost far more.

- **~60 days** of 22% dust loss before one RM 150 cleaning pays for itself. **[ASSUMED]**
- A fault costs about **RM 154** over 14 days. **[ASSUMED]**
- Example home: 4.7 kWp, 25.7 kWh/day, RM 0.44/kWh, 14 days earlier detection. All TO CONFIRM (see `docs/assumptions.md`).
- **Next steps:** [NEXT STEP 1, TO CONFIRM] / [NEXT STEP 2, TO CONFIRM] / [NEXT STEP 3, TO CONFIRM]
- **Not built on purpose:** login, live inverter connection, notifications [EDIT TO MATCH README]

*Footer:* Loss per day = output x dust loss x tariff. [TEAM NAMES]

---

## Fix these before presenting

1. **App fallback numbers are placeholders** (22/26/24.5 kWh, 34% and 91% gaps, $8.40 and $12.60). Do not quote them. The app may show dollars while our assumptions use RM.
2. **Three different daily-output numbers exist:** about 317 kWh/day in the data, 180 in `metrics.md`, about 25.7 for the home example. Pick one and make `docs/assumptions.md` match.
3. **Dust loss does not stop on Feb 17 in the data** (about 18% below normal through Mar 1), while `metrics.md` says Feb 10-17. Ask Member A.
4. **The app footer says "No AI".** Be ready to explain what the model is.
5. **Loss is our estimate** against the Jan 1 to Feb 9 baseline efficiency. It is not a number the app produces.
