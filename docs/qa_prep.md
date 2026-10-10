# Judge Q&A Prep

These are draft answers. Edit them so they match what we actually built and measured. Anything marked TO CONFIRM must be checked before we say it out loud.

---

**1. Why didn't you use deep learning?**
Draft: We had a short build time and a small amount of data, and the owner needs a reason they can understand, not just a prediction. [MODEL WE USED, TO CONFIRM] lets us explain why something was flagged. If we had more real data, deep learning would be something to try later.

**2. How do you avoid false alarms?**
Draft: [HOW WE REDUCE FALSE ALARMS, e.g. a threshold, a rule that requires the drop to persist, TO CONFIRM]. We measured the false alarm rate at [NUMBER FROM results/metrics.md, TO CONFIRM]. A false alarm costs the owner trust, so we would rather [TRADE-OFF WE CHOSE, TO CONFIRM].

**3. How is this different from an inverter app?**
Draft: Inverter apps mostly show what already happened. [WHAT WE SAW, TO CONFIRM]. Ours forecasts tomorrow, categorizes the problem, ranks problems by money lost, and tells the owner what to do in plain language, with no dashboard to read.

**4. How realistic is your data?**
Draft: [BE HONEST: real, simulated, or a mix, and where it came from, TO CONFIRM]. If it is simulated, say so, explain what we modelled, and say what real data we would need to validate it.

**5. How do you know it actually helps someone make a better decision?**
Draft: We talked to [NUMBER, TO CONFIRM] solar owners and [WHAT THEY SAID, with real quote]. Our test results show [PROOF NUMBER FROM results/metrics.md, TO CONFIRM]. We have not yet tested it with owners over time, which is a next step.

**6. How did you calculate "money lost"?**
Draft: We use [FORMULA, see docs/assumptions.md]. The tariff, system size, and dust loss values are [SOURCES, TO CONFIRM]. They are assumptions and the owner's real numbers would replace them.

**7. What if the forecast is wrong?**
Draft: [HOW WE HANDLE FORECAST ERROR, e.g. we show a range or only act when the gap is large, TO CONFIRM]. Our forecast error was [NUMBER FROM results/metrics.md, TO CONFIRM].

**8. What would you build next?**
Draft: [TOP 2-3 NEXT STEPS, TO CONFIRM. Ideas to consider: test on real homes, connect to real inverter data, add more problem types, send the message by phone notification]. We deliberately left these out to focus on a demo that proves the core idea.

**9. Who is your user and why would they pay or care?**
Draft: A home solar owner who does not check their system closely. [WHAT THEY TOLD US, real quote]. The value is catching losses sooner. The size of that value is [NUMBER FROM docs/assumptions.md, TO CONFIRM].

**10. Why no dashboard or login?**
Draft: Our interviews and the hackathon advice we followed both pointed the same way: the owner needs a decision, not a chart. [WHAT INTERVIEWEES SAID, TO CONFIRM]. A short plain-language answer is faster to act on than a dashboard.

---

## Questions we still can't answer well (fill in after rehearsal)
- [QUESTION]
- [QUESTION]
