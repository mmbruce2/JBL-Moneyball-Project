# JBL Moneyball Project

Moneyball-style player analysis for the JBL (Justice Basketball League) — identifying undervalued players, overpaid contracts, and building a data-driven roster construction framework.

---

## Files

| File | Description |
|------|-------------|
| `merge_data.py` | Data ingestion, merging, and feature engineering pipeline |
| `analysis.py` | All 5 correlation studies |
| `merged_JBL_Data.csv` | Full merged dataset (587 players × 281 columns) |
| `player_valuation.csv` | Player valuation rankings by ValueIndex |
| `data_quality_report.md` | Phase 1 audit — what was broken and how it was fixed |
| `analysis_report.md` | Phase 2 — all 5 study findings |
| `plots/` | Visualizations for each study |

---

## Datasets Merged
| File | Rows | Description |
|------|------|-------------|
| JBLPlayers.csv | 587 | Base player info, salary, scouting ratings |
| JBLPerGame.csv | 413 | Per-game stats |
| JBLAdvanced.csv | 413 | Advanced metrics (PER, BPM, VORP, WS, PM, BoxC, etc.) |
| JBLHustle.csv | 413 | Hustle stats (SA, CSht, DFL, LBR, CD, etc.) |
| JBLShotLocations.csv | 413 | Shot zone breakdown + distance ranges |
| JBLPlayTypes.csv | 413 | Efficiency by play type (Iso, PnR, Post, SpotUp, etc.) |
| JBLOnOff.csv | 406 | On/off court net rating splits |
| JBLPlayoffs.csv | 216 | Playoff per-game stats |

> **Root cause of original merge failure:** 3 different team name formats across files. Fixed via 37-entry abbreviation → full name mapping.

---

## Key Metric: ValueIndex

```
ValueIndex = (Win Shares + VORP) / (Salary in $M)
```

Higher = more production per dollar.

## Top Value Players

| Player | Team | Salary | WS | VORP | ValueIndex |
|--------|------|--------|----|------|------------|
| Devin Kavanagh | Renegades | $3.7M | 8.5 | 2.6 | **3.00** |
| Damon Lawson | Barons | $1.75M | 3.6 | 1.2 | 2.74 |
| Leandro Santoro | Drones | $1.75M | 3.4 | 0.9 | 2.46 |
| Ruben Smith | Dragons | $2.45M | 4.0 | 1.9 | 2.41 |
| Tanner Mitchell | Jailbirds | $2.25M | 4.6 | 0.6 | 2.31 |

---

## Phase 2 Studies

### Study 1 — Rating-to-Impact by Archetype
Which scouting ratings actually translate to production (VORP, WS, eFG%) for each offensive and defensive archetype?

### Study 2 — Three Point Shooting Profile
Which archetype + rating combinations produce the best 3-point shooters?
- **Best shooting archetype:** Stretch Big (median 3P%: 0.416), Pick-and-Pop Big (0.407)
- **Strongest predictor of 3P%:** Post Efficiency (r=+0.38), Outside Scoring (r=+0.35)
- **Counterintuitive:** On-Ball Defense rating is *negatively* correlated with 3P% (r=−0.27) — elite perimeter defenders tend not to be shooters

### Study 3 — Defensive Impact
What actually drives DWS and DBPM?
- **#1 predictor of DBPM:** Rim Protection (r=+0.57)
- **#2 predictor:** Height rating (r=+0.52), then Post Defense (r=+0.50)
- **Weight matters more than athleticism** for interior defensive impact
- **Best defensive archetype:** Anchor Big (median DWS: 1.75), Wing Stopper (1.10)

### Study 4 — Winning Without Scoring
WS/VORP/BPM residualized against PPG and USG% to isolate non-scoring impact.
- **Top non-scoring winner:** Reid Frahm (PG) — 12.8 PPG but Non-Score Impact 10.99
- These players generate wins through playmaking, defense, and rebounding without dominating the ball

### Study 5 — Archetype Efficiency by Play Type
Which archetype dominates which court zone and play type?
- **Post Bullies** are most efficient in Post Up situations (median eFG% 0.774)
- **Movement Shooters** dominate Off Screen (0.917 eFG%) and Misc (0.834)
- **Primary Ballhandlers** and **Shot Creators** create the most open looks (AST% 31.9 and 29.3)

---

## Setup

```bash
source jbl_env/bin/activate  # (venv lives in JBL Datasets folder)
pip install pandas fuzzywuzzy tabulate scipy matplotlib seaborn
python3 merge_data.py   # rebuild merged dataset
python3 analysis.py     # run all 5 studies
```
