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

## How the impact estimate is built

All inputs are assumptions until the Status column above says Confirmed.

Inputs (example home): 4.7 kWp system, 25.7 kWh/day, RM 0.44/kWh, 14 days earlier detection, RM 150 per cleaning.

Money lost per day = daily output (kWh) x dust loss (%) x tariff (per kWh)
Money lost from late detection = money lost per day x days of earlier detection
Net benefit of cleaning = money lost from late detection - cleaning cost

| Case | Lost per day | Lost over 14 days | Net benefit of one cleaning | Break-even |
|---|---|---|---|---|
| Typical dust, 5% | RM 0.57 | RM 8 | -RM 142 | about 265 days |
| Our test data, 22% | RM 2.49 | RM 35 | -RM 115 | about 60 days |
| Inverter fault, 97% | RM 10.97 | RM 154 | not applicable (a repair cost, not a cleaning) | not applicable |

What this means: a short dusty spell costs less than one cleaning. The app's value is telling the owner when dust has lasted long enough to be worth cleaning, and catching faults that cost over RM 150 in two weeks.

Still TO CONFIRM: daily output (5.46 kWh/day per kW is a model figure for Sepang), the 14 days (replace the 1-day tool lag with our real detection lag), and the tariff, which is RM 0.44 if used at home or RM 0.27 if exported (real export rate not found).

