# Assumptions for the Impact Estimate

Every number here is TO CONFIRM until we have a source. Do not quote any of these in the pitch until the "Status" column says Confirmed.

| Assumption | Value | Source or reason | Status |
|---|---|---|---|
| Home system size (kW) | 4–12 kW; example home 4.7 kWp | Cleaning-company size guide (4, 6, 8, 12 kW by house type); Borneo Post example of 10 panels, 4.7 kWp | Researched, TO CONFIRM (vendor and news source) |
| Residential system cap | 12 kW single-phase, or 75% of approved load, whichever is lower | Trexon NEM guide (an installer blog) | Researched, TO CONFIRM against SEDA |
| Electricity tariff (price per kWh) | 27.03 + 4.55 + 12.85 = 44.43 sen/kWh (about RM 0.44), up to 1,500 kWh/month, before tax, AFA, rebates. RM 10/month retail charge on top. | TNB domestic tariff from 1 July 2025, reported by SoyaCincau | Researched, TO CONFIRM against tnb.com.my |
| Value of expo| Value of exported solar (sen/kWh) | RM 0.27 to RM 0.44 per kWh | Assumption: high end is the sourced tariff (used at home), low end is the energy charge only. Real NEM export rate not found. | Assumed, TO CONFIRM against SEDA |rted solar (sen/kWh) | [NOT FOUND, no numeric rate on the pages I read] | Under NEM, exports are credited against the bill, not paid as cash. Check SEDA. | Not researched |
| Cost of one panel cleaning | RM 150–400 per session by system size; about RM 300/year for 2 cleans | Trexon maintenance guide (installer, so a vendor estimate; its own FAQ and table disagree slightly) | Researched, TO CONFIRM with a real quote |
| Cleaning frequency | 1–2 times per year | Same Trexon guide | Researched, TO CONFIRM |
| Typical energy loss from dust (%) | About 5% typical; about 2% with year-round rain | NREL, as cited by Aurora Solar | Researched |
| Dust loss measured in Malaysia | 4.53% performance drop in a monthly test on a rooftop | UTP study "Impact of Soiling Rate on Solar PV Panel in Malaysia" (abstract only, year about 2018) | Researched, TO CONFIRM full paper |
| Upper range for dust loss | Up to 10–15% | Evo Energy (a UK installer, not a study) | Weak source, do not lead with it |
| Daily output per kW installed | About 5.46 kWh/day per kW (Sepang). About 25.7 kWh/day for a 4.7 kWp home. | Profile Solar model for Sepang, my average of its four seasonal values | TO CONFIRM, see note below |
| Days of earlier detection vs. owner noticing alone | About 14 days (owner notices after about 15 days on average, tool flags in about 1 day) | Our assumption, not a public study. Owner delay is a monthly-check scenario. Replace the 1-day tool lag with the real figure from results/metrics.md. | Assumed, TO CONFIRM || Average daily output of the example system (kWh) | Pick one: 317 (our CSVs, commercial size), 180 (metrics.md), or about 25.7 (home size) | State which dataset | Not decided |
| Currency and unit used in the demo | RM per kWh | Matches the tariff source | Decided |

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
