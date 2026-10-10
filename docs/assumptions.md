# Assumptions for the Impact Estimate

Every number here is TO CONFIRM until we have a source. Do not quote any of these in the pitch until the "Status" column says Confirmed.

| Assumption | Value | Source or reason | Status |
|------------|-------|------------------|--------|
| Home system size (kW) | TO CONFIRM | [e.g. typical size from an interview or an official source] | Not researched |
| Electricity tariff (price per kWh) | TO CONFIRM | [e.g. local utility tariff page, link here] | Not researched |
| Cost of one panel cleaning | TO CONFIRM | [e.g. quote from a local cleaner, link or name] | Not researched |
| Typical energy loss from dust (%) | TO CONFIRM | [e.g. published study or installer guidance, link here] | Not researched |
| Days of earlier detection vs. owner noticing alone | TO CONFIRM | [from interviews, or from our own test results in results/metrics.md] | Not researched |
| Average daily output of the example system (kWh) | TO CONFIRM | [from the dataset we use, state which one] | Not researched |
| Currency and unit used in the demo | TO CONFIRM | [e.g. RM per kWh] | Not decided |

## How the impact estimate will be built

Fill in once the values above are confirmed. Keep it simple enough to explain out loud.

```
Money lost per day  = daily output (kWh) x dust loss (%) x tariff (per kWh)
Money lost from late detection = money lost per day x days of earlier detection
Net benefit of cleaning = money lost from late detection - cleaning cost
```

This formula is a draft structure only. The team should check that it matches how the model actually calculates "money lost" and change it if not. TO CONFIRM.

## Rules for this file
- If a value comes from an interview, write the interview ID in the source column.
- If a value comes from the internet, paste the link and the date we read it.
- If we are guessing, say "team estimate" and show it as a range, not a single number.
- Whatever we say in the pitch must match this table.
