# Phase 1: Data Quality Report

## Summary

All critical columns are now populated. Previous merge failures were caused by **three different team name formats** across the CSV files.

---

## Root Cause

| File | Team Name Format | Example |
|------|-----------------|---------|
| JBLPlayers.csv | Full name | `Hurricanes` |
| JBLPerGame.csv | Full name | `Hurricanes` |
| JBLOnOff.csv | Full name | `Hurricanes` |
| JBLPlayoffs.csv | Full name | `Hurricanes` |
| JBLAdvanced.csv | 3-letter abbrev | `Hur` |
| JBLHustle.csv | 3-letter abbrev | `Hur` |
| JBLShotLocations.csv | 3-letter abbrev | `Hur` |
| JBLPlayTypes.csv | 3-letter abbrev | `Hur` |

**Fix:** Built a complete 37-entry abbreviation → full name mapping. All team names normalized to canonical full names before any merge operation.

**Secondary issue:** `JBLPlayTypes.csv` had 10 groups of duplicate column names (`Pos, PTS, PPP, eFG` repeated). Renamed each group by play type:
- Iso, PnR_Ball, PnR_Roll, PostUp, SpotUp, Handoff, Cut, OffScreen, Transition, Misc

**Third issue:** In `JBLPlayers.csv`, the column named `WS` actually contains height/rating data — actual Win Shares are in `WS.1`. Fixed by using `WS.1` as `WS_actual`.

---

## CSV Audit

| File | Rows | Cols | Empty Cols | Notes |
|------|------|------|------------|-------|
| JBLPlayers.csv | 587 | 94 | 0 | Base file. Includes FA/practice squad. Tm = "Team" col with full names |
| JBLPerGame.csv | 413 | 29 | 0 | Active rostered players only. Full team names |
| JBLAdvanced.csv | 413 | 45 | 0 | 3-letter team abbreviations |
| JBLHustle.csv | 413 | 19 | 0 | 3-letter abbreviations |
| JBLShotLocations.csv | 413 | 51 | 0 | 3-letter abbreviations. Distance % cols had generic names (`%`, `%.1`, etc.) — renamed |
| JBLPlayTypes.csv | 413 | 50 | 0 | 3-letter abbreviations. 10 duplicate column groups — renamed by play type |
| JBLOnOff.csv | 406 | 14 | 0 | Full team names. 7 fewer players than per-game (min minutes threshold) |
| JBLLineups.csv | 2380 | 28 | 0 | Team-level lineup data (no Player column — not merged into player dataset) |
| JBLPlayoffs.csv | 216 | 29 | 0 | Full team names. Only playoff qualifiers |

---

## Final Merged Dataset

- **Shape:** 587 players × 281 columns
- **Merge key:** Player (lowercase + strip) + Tm (canonical full name)

---

## Critical Column Null Counts

> Note: 46% null rate is expected — the stats files cover 413 active rostered players,
> while JBLPlayers has 587 total (includes free agents and inactive roster).

| Column Group | Null Count | Null % | Status |
|---|---|---|---|
| PM, BoxC, OL, Spc, aTOV, Adj3P% (Advanced) | 270/587 | 46.0% | ✅ Expected |
| SA, SAPG, CSht, CSPG, DFL, DFPG, LBR, LBPG, CD, CDPG (Hustle) | 270/587 | 46.0% | ✅ Expected |
| RimM, RimA, Rim%, ClsM, ClsA, Cls%, MidM, MidA, Mid%, LngM, LngA, Lng% (ShotLoc) | 270/587 | 46.0% | ✅ Expected |
| 2PM/2PA/% for 0-2ft, 2-4ft, 4-6ft, 6+ft (distance breakdown) | 270/587 | 46.0% | ✅ Expected |
| 3PM, 3PA (ShotLoc) | 269-270/587 | ~46% | ✅ Expected |
| 3P% (from JBLPlayers base) | 71/587 | 12.1% | ✅ Expected (non-shooters) |
| Iso_PTS, PnR_Ball_PTS, SpotUp_PTS, Transition_PTS (PlayTypes) | 270/587 | 46.0% | ✅ Expected |
| On Net, Off Net, Floor Net (OnOff) | 181/587 | 30.8% | ✅ Expected (min threshold) |

---

## Anomalies Flagged for Analysis

1. **WS column corruption in JBLPlayers:** `WS` = height/rating composite string (e.g., `"87 - 7'3"`). `WS.1` = actual Win Shares. This is a naming collision in the source data.
2. **Free Agents in base file:** JBLPlayers includes 174 players not in any stats file (Free Agents + practice squad). They will have NaN for all stats columns but valid scouting ratings.
3. **Multi-team players (TOT rows):** PerGame/Advanced include "Total" rows for traded players. These merge correctly under `TOT` but their team-specific splits are not captured.
4. **JBLPlayTypes Pos columns:** The "Pos" in each play type group represents play count (possessions), not position. Renamed as `{PlayType}_Plays` for clarity.
5. **JBLOnOff 7 fewer players:** Likely a minimum minutes threshold applied (~7 players below cutoff).
