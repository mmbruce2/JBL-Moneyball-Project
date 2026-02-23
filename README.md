# JBL Moneyball Project

Moneyball-style player analysis for the JBL (Justice Basketball League) — identifying undervalued players, overpaid contracts, and building a data-driven roster construction framework.

## Files

| File | Description |
|------|-------------|
| `merge_data.py` | Data ingestion, merging, and feature engineering pipeline |
| `merged_JBL_Data.csv` | Full merged dataset (587 players × 235 stats) |
| `player_valuation.csv` | Player valuation rankings by ValueIndex |
| `analysis_report.md` | Top value picks and overpaid players report |

## Datasets Merged
- `JBLPlayers.csv` — base player info, salary, ratings, skills
- `JBLPerGame.csv` — per-game stats
- `JBLAdvanced.csv` — advanced metrics (PER, BPM, VORP, WS, etc.)
- `JBLHustle.csv` — hustle stats
- `JBLShotLocations.csv` — shot zone breakdown
- `JBLOnOff.csv` — on/off court impact
- `JBLPlayoffs.csv` — playoff per-game stats

## Key Metric: ValueIndex

```
ValueIndex = (Win Shares + VORP) / (Salary in $M)
```

Higher ValueIndex = more production per dollar. Identifies undervalued players and bad contracts.

## Top Value Players

| Player | Team | Salary | WS | VORP | ValueIndex |
|--------|------|--------|----|------|------------|
| Devin Kavanagh | Renegades | $3.7M | 8.5 | 2.6 | 3.00 |
| Damon Lawson | Barons | $1.75M | 3.6 | 1.2 | 2.74 |
| Leandro Santoro | Drones | $1.75M | 3.4 | 0.9 | 2.46 |

## Setup

```bash
# Use the existing venv in the JBL Datasets folder
source jbl_env/bin/activate
pip install pandas fuzzywuzzy tabulate
python3 merge_data.py
```
