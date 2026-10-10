# Assumptions for the Impact Estimate

Every number here is TO CONFIRM until we have a source. Do not quote any of these in the pitch until the "Status" column says Confirmed.

| Assumption | Value | Source or reason | Status |
|---|---|---|---|
| Home system size (kW) | 4–12 kW; example home 4.7 kWp | Cleaning-company size guide lists 4, 6, 8, 12 kW by house type (terrace to bungalow). Borneo Post example: 10 panels, 4.7 kWp. | Researched, TO CONFIRM (vendor and news source) |
| Electricity tariff (price per kWh) | 27.03 sen energy + 4.55 capacity + 12.85 network = 44.43 sen/kWh (about RM 0.44), before tax, AFA and rebates, up to 1,500 kWh/month. RM 10/month retail charge on top. | TNB domestic tariff from 1 July 2025, as reported by SoyaCincau | Researched, TO CONFIRM against tnb.com.my |
| Cost of one panel cleaning | RM 150–400 per session, depending on system size. About RM 300/year for 2 cleans. | Trexon Malaysia maintenance guide (a solar installer, so a vendor estimate) | Researched, TO CONFIRM with a real quote |
| Typical energy loss from dust (%) | About 5% typical; about 2% with year-round rain | NREL, as cited by Aurora Solar | Researched |
| Days of earlier detection vs. owner noticing alone | [NO PUBLIC FIGURE FOUND] | Needs our interviews or our own test results in results/metrics.md | Not researched |
| Average daily output of the example system (kWh) | [PICK ONE, see note below] | State which dataset | Not decided |
| Currency and unit used in the demo | RM per kWh | Matches the tariff source above | Decided |

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
