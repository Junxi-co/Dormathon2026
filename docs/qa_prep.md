# Judge Q&A Prep

These are draft answers. Anything marked TO CONFIRM must be checked before we say it out loud. Money numbers are assumptions (see `docs/assumptions.md`) and must be said as assumptions.

---

**1. Why didn't you use deep learning?**
Draft: We had a short build time and a small amount of data, and the owner needs a reason they can understand, not just a prediction. [MODEL WE USED, TO CONFIRM with Member A] lets us explain why something was flagged. With more real data, deep learning would be something to try later.

**2. How do you avoid false alarms?**
Draft: [HOW WE REDUCE FALSE ALARMS, e.g. a threshold, a rule that requires the drop to persist, TO CONFIRM with Member A]. On clean data we got 1 false alarm. A false alarm costs the owner trust, so [TRADE-OFF WE CHOSE, TO CONFIRM].

**3. How is this different from an inverter app?**
Draft: Inverter apps mostly show what already happened. [WHAT WE SAW, TO CONFIRM]. Ours gives one screen with tomorrow's outlook, a Check card that says what kind of problem was found (green for all clear, orange for a problem), and what to do about it in plain language. No dashboard to read, no login.

**4. How realistic is your data?**
Draft: [HONEST ANSWER, TO CONFIRM with Member A]. If it is simulated, say so: it is 60 days of hourly readings (Jan 1 to Mar 1, 2026) with a dusty period and an inverter fault we added on purpose. It shows the idea works, but it is not proof on real homes. We would need real inverter data from real homes to validate it.

**5. How do you know it actually helps someone make a better decision?**
Draft: We have not yet interviewed solar owners, so we do not claim that. What we have measured: on our test data it caught both injected faults with the right type, with 1 false alarm on clean data, and it still caught the fault with noise added and 5% of rows dropped. The next step is to test it with real owners over time.

**6. How did you calculate "money lost"?**
Draft: Money lost per day = daily output x dust loss x tariff. For an example 4.7 kWp home we assumed 25.7 kWh/day, RM 0.44/kWh (the 2025 TNB domestic tariff) and 14 days of earlier detection. These are assumptions, and an owner's real numbers would replace them.

**7. What if the forecast is wrong?**
Draft: [HOW WE HANDLE FORECAST ERROR, e.g. we only act when the gap is large, TO CONFIRM]. Our forecast error was 54.4% lower than "same hour yesterday" on normal days and 46.9% lower on the fault scenario. It was worse on the dusty scenario. We are open about that. It is the next thing to improve.

**8. What would you build next?**
Draft: [CONFIRM WITH TEAM]. Ideas: test on real homes, connect to real inverter data, improve the forecast on dusty days, add more problem types, send the message to the owner's phone. We deliberately left these out to focus on a demo that proves the core idea.

**9. Who is your user and why would they pay or care?**
Draft: A home solar owner who does not check their system closely. The value is catching problems sooner. For an example home, a fault left for 14 days costs about RM 150 (assumed), and the app also tells the owner when dust has lasted long enough to be worth cleaning (about 60 days at 22% loss, assumed).

**10. Why no dashboard or login?**
Draft: The owner needs a decision, not a chart. A short plain-language answer is faster to act on than a dashboard. [WHAT WE SAW IN INVERTER APPS, TO CONFIRM].

---

## Questions we still can't answer well (rehearse these)
- **"Your forecast was worse on the dusty scenario. Why?"** We don't know yet. [REASON, TO CONFIRM with Member A]. It is the first thing we would fix.
- **"Is a 22% dust loss realistic?"** It is higher than the typical 5% from NREL and 4.5% from a Malaysian study. We call it our simulated worst case, not a typical figure.
- **"A dusty week costs less than one cleaning. So what does the app save?"** Correct, a short dusty spell does not pay for a cleaning (assumed RM 18 vs RM 150+). The app's value is telling the owner when dust has gone on long enough to be worth cleaning, and catching faults, which cost far more.
- **"Why is the dust loss still there after Feb 17 in your
