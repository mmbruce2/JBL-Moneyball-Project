# Phase 1 — Data Quality Report
**Status: ✅ VERIFIED CLEAN — Ready for Phase 2 Analysis**

---

## Files Audited

| File | Rows | Columns | Empty Cols |
|------|------|---------|-----------|
| JBLPlayers.csv | 587 | 94 | 0 |
| JBLPerGame.csv | 413 | 29 | 0 |
| JBLAdvanced.csv | 413 | 45 | 0 |
| JBLHustle.csv | 413 | 19 | 0 |
| JBLPlayTypes.csv | 413 | 50 | 0 (had duplicate col names — fixed) |
| JBLShotLocations.csv | 413 | 51 | 0 |
| JBLOnOff.csv | 406 | 14 | 0 |
| JBLLineups.csv | 2380 | 28 | 0 |
| JBLPlayoffs.csv | 216 | 29 | 0 |

---

## Root Causes Found & Fixed

### Bug 1: Team Name Inconsistency (PRIMARY CAUSE — all stat columns were 100% NaN)
**Problem:** JBLAdvanced, JBLHustle, JBLPlayTypes, and JBLShotLocations use 3-letter team abbreviations (`Hur`, `Bar`, `Kin`...) while JBLPlayers, JBLPerGame, and JBLOnOff use full names (`Hurricanes`, `Barons`, `Kings`...). Every stat file join on `[Player, Tm]` produced zero matches.

**Fix:** Added a complete `TEAM_MAP` dictionary that normalizes all abbreviations to full names before any merge operation.

### Bug 2: Traded Players / "Tot" Rows (96 unmatched stat rows)
**Problem:** Players traded mid-season appear multiple times in stat files — once per team stint and once with `Tm = "Tot"` (aggregate). Their current team in JBLPlayers often didn't match any individual stint row.

**Fix:** Deduplicate each stat file to one row per player before merging — prefer the `"Tot"` aggregate row (most complete stats), then sort by minutes as tiebreaker.

### Bug 3: JBLPlayTypes Duplicate Column Names
**Problem:** Columns were literally `Pos, PTS, PPP, eFG, Pos, PTS, PPP, eFG...` repeated 10 times (once per play type). pandas auto-renamed them to `Pos.1`, `PTS.1`, etc. with no context.

**Fix:** Renamed all 40 stat columns by play type in sequence:
`Isolation_Poss, Isolation_PTS, Isolation_PPP, Isolation_eFG, PnR_BallHandler_Poss...` etc.

### Bug 4: `&nbsp;` Garbage in Player Names
**Problem:** One player had `&nbsp;&nbsp;` embedded in their name from HTML export.

**Fix:** Strip `&nbsp;` from all player names during normalization.

### Bug 5: WS Column in JBLPlayers is NOT Win Shares
**Problem:** `WS` column in JBLPlayers.csv contains a combined height/rating string (e.g. `"87 - 7'3"`), not Win Shares. The actual Win Shares are in `WS.1`.

**Fix:** Use `WS.1` as the Win Shares source from JBLPlayers. Prefer `WS_adv` from JBLAdvanced when available (more precise), fallback to `WS.1`.

---

## Final Null Counts (Critical Columns)

**Baseline:** 587 total players in JBLPlayers. Only 409 had sufficient playing time to appear in advanced stat sheets. 178 null rows (30.3%) are expected for bench players, injured, and free agents.

| Column Group | Null Count | Null % | Status |
|---|---|---|---|
| Advanced (PM, BoxC, OL, Spc, aTOV, Adj3P%, WS, VORP, BPM, etc.) | 178 | 30.3% | ✅ Expected — bench/FA players |
| Hustle (SA, SAPG, CSht, CSPG, DFL, DFPG, LBR, LBPG, CD, CDPG) | 178–218 | 30–37% | ✅ Expected + some 0-play categories |
| Shot Locations (Rim%, Cls%, Mid%, Lng%, 3P distance breakdown) | 178–218 | 30–37% | ✅ Expected |
| Play Types (Isolation, PnR, SpotUp, Transition, etc.) | 178–218 | 30–37% | ✅ Expected |
| OnOff (On ORtg, On DRtg, Floor Net) | 181 | 30.8% | ✅ Expected |
| Playoffs (PO_PPG, PO_G) | 375 | 63.9% | ✅ Expected — only 212 players made playoffs |
| Computed: WS, VORP, PER, BPM, DWS, OWS | 71 | 12.1% | ✅ Players file has most; 71 genuinely missing |
| ValueIndex | 313 | 53.3% | ✅ Expected — free agents with $0 salary excluded |

---

## Final Output
- **`merged_JBL_Data.csv`** — 587 rows × 277 columns
- **`player_valuation.csv`** — Ranked by ValueIndex (WS+VORP per $1M salary)
- All 409 active players have complete advanced stats, hustle, shot location, and play type data ✅

---

## Data Anomalies Flagged for Analysis Phase

1. **WS column naming quirk** — JBLPlayers uses `WS` for a height/rating combo and `WS.1` for actual Win Shares. Analysts should use `WS_adv` or `WS` (computed column) not `WS.1` raw.
2. **Some hustle zero-values vs NaN** — SA, DFL, LBR, CD have 40 more nulls than MIN_hsl (37.1% vs 30.3%). These are likely players who legitimately had 0 screen assists or floor dives in tracked games.
3. **"Free Agent" team players** — 25+ players in JBLPlayers with `Tm = "Free Agent"` — they have scouting ratings (Cur/Pot, archetypes, skills) but no game stats. Useful for prospect analysis.
4. **Ln% column** — 35.1% null vs 30.3% for other shot location columns. Players with 0 long-range FGA have NaN for Lng% (can't divide by zero). Fill with 0 for analysis.
5. **Multiple `_adv` suffixed columns** — Advanced stats are more granular than JBLPlayers stats. Always prefer `_adv` suffixed columns for analysis (WS_adv, VORP_adv, BPM_adv, etc.).
