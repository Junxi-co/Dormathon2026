# 2-Minute Pitch Script

**Total time:** 2:00. Rehearse with a timer. Practise the demo section the most.
Anything in [BRACKETS] needs real input from us. Do not say a number out loud until it is confirmed.
Numbers marked "assumed" must be said as assumptions (see `docs/assumptions.md`).

---

## 0:00 - 0:20 | The person and their problem (20s)

*Say:*
"Meet [NAME OR 'a homeowner we interviewed']. They have solar panels on their roof. When we asked how they find out something is wrong, they told us: **'[INSERT REAL QUOTE]'**.
Their panels can lose output for days before anyone notices, and every day costs them money."

*Presenter note:* Use the real quote from the interview notes. If we only have a paraphrase, say "told us" and do not use quote marks.

---

## 0:20 - 0:35 | The gap in existing tools (15s)

*Say:*
"Inverter apps show what **already happened**. [WHAT WE SAW IN THE APP, TO CONFIRM]. They don't say what to expect tomorrow, what kind of problem it is, or what to do about it."

*Presenter note:* Only claim what we actually saw in the comparison checklist (`docs/interview_guide.md`).

---

## 0:35 - 1:25 | Live demo: three scenario buttons (50s)

*Say:*
"There's no login and no dashboard. You press a button and get a plain-language answer. These are three simulated scenarios."

| Time | Action | What to say |
|------|--------|-------------|
| 0:35-0:45 | Open the app and show the start screen | "Tomorrow's outlook for a home solar system." |
| 0:45-0:57 | Press **Normal day** | "On a normal day the Check card is green: nothing is wrong." |
| 0:57-1:09 | Press **Dusty panels** | "Now the Check card turns orange. It flags dust and says what to do." (Read the actual wording off the screen.) |
| 1:09-1:21 | Press **Inverter fault** | "Here it flags an equipment fault. That is a different problem, with a different action." (Read the actual wording off the screen.) |
| 1:21-1:25 | Point to the Check card | "Green means all clear. Orange means act." |

*Presenter note:* Run through all three buttons before going on stage. Do not read out any number on screen unless it matches `results/metrics.md` or `docs/assumptions.md` (the app's built-in fallback numbers are placeholders, and the app may show dollars while our assumptions use RM). Keep a screen recording as a backup in case of Wi-Fi or app problems. Backup file location: [PATH].

---

## 1:25 - 1:50 | The proof numbers (25s)

*Say:*
"Does it help someone make a better decision? Here's the proof, from our test results:
- Both faults we added on purpose were caught, with the right type.
- One false alarm on clean data.
- It still caught the fault with noise added and 5% of rows dropped.
- Impact, assumed for a 4.7 kWp home: about 60 days of heavy dust before one cleaning pays for itself, and a fault costs about RM 150 in two weeks.
We tested on [DESCRIBE DATA SOURCE HONESTLY, e.g. simulated hourly data over 60 days with faults we added on purpose, TO CONFIRM]."

*Presenter note:* Copy numbers from `results/metrics.md` and `docs/assumptions.md` and check they are marked Confirmed. Say "assumed" out loud for the impact line. Keep the weak result (forecast worse than "same hour yesterday" on the dusty scenario) for Q&A, do not hide it if asked.

---

## 1:50 - 2:00 | The close (10s)

*Say:*
"Tomorrow's Solar Plan: it tells a homeowner what to expect tomorrow, what is going wrong, and what to do. [ONE LINE ABOUT NEXT STEP, TO CONFIRM]. Thank you."

---

## Before presenting, checklist
- [ ] Real quote inserted
- [ ] All three scenario buttons tested in the final build
- [ ] Wording on screen for each scenario read once so we can describe it accurately
- [ ] Proof numbers copied from `results/metrics.md`
- [ ] Impact numbers match `docs/assumptions.md` and are said as "assumed"
- [ ] Currency on screen matches what we say (RM or $)
- [ ] Practised with a timer, finished at or under 2:00
- [ ] Backup screen recording ready
