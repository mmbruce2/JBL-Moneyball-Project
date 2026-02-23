"""
JBL Moneyball — Data Merge Pipeline (Fixed)
Root cause fixed: stat files use 3-letter team abbreviations (Hur, Bar, etc.)
while Players/PerGame/OnOff use full names. All Tm values are now normalized
to full team names before any merge.
"""
import pandas as pd
import numpy as np
import os, warnings
warnings.filterwarnings('ignore')

BASE = "/Users/maxx/Documents/JBL Datasets"
REPO = "/Users/maxx/Documents/JBL-Moneyball-Project"

# ── Team abbreviation → full name map ────────────────────────────────────────
TEAM_MAP = {
    'Bar': 'Barons',    'Bli': 'Blizzards', 'Bul': 'Bullets',
    'Cal': 'Calaveras', 'Col': 'Colonels',  'Cru': 'Crusaders',
    'Cyc': 'Cyclones',  'Dev': 'Devils',    'Dra': 'Dragons',
    'Dro': 'Drones',    'Fir': 'Fireballs', 'Gia': 'Giants',
    'Hur': 'Hurricanes','Hus': 'Huskies',   'Jag': 'Jaguars',
    'Jai': 'Jailbirds', 'Kin': 'Kings',     'Kni': 'Knights',
    'Lig': 'Lightning', 'Lum': 'Lumberjacks','Mus': 'Mustangs',
    'Pil': 'Pilots',    'Pre': 'Predators', 'Ren': 'Renegades',
    'Roc': 'Rockets',   'Sai': 'Saints',    'Sco': 'Scorpions',
    'Sky': 'Skyhawks',  'Sta': 'Stars',     'Sto': 'Stonecutters',
    'Thu': 'Thunder',   'Tri': 'Tritons',   'Vip': 'Vipers',
    'Vul': 'Vultures',  'War': 'Warriors',  'Wol': 'Wolves',
}

# Play type column order (standard NBA play type sequence)
PLAY_TYPES = [
    'Isolation', 'PnR_BallHandler', 'PnR_Rollman', 'PostUp',
    'SpotUp', 'Handoff', 'Cut', 'OffScreen', 'Transition', 'Misc'
]

def normalize_team(series):
    """Map abbreviations to full names; leave full names as-is."""
    return series.astype(str).str.strip().map(
        lambda x: TEAM_MAP.get(x, x)
    )

def load(filename, normalize_tm=True):
    df = pd.read_csv(os.path.join(BASE, filename))
    df.columns = df.columns.str.strip()
    if 'Player' in df.columns:
        df['Player'] = df['Player'].astype(str).str.strip().str.lower()
    tm_col = 'Tm' if 'Tm' in df.columns else ('Team' if 'Team' in df.columns else None)
    if tm_col and normalize_tm:
        df[tm_col] = normalize_team(df[tm_col])
        if tm_col == 'Team':
            df = df.rename(columns={'Team': 'Tm'})
    return df

# ── METADATA cols to drop from secondary files (exist in base already) ───────
DROP_META = ['Rk', 'Pos', 'Age', 'Exp', 'G', 'GS']

def prep_secondary(df, suffix_cols=None):
    """Drop metadata cols; optionally add suffix to stat cols."""
    df = df.drop(columns=[c for c in DROP_META if c in df.columns], errors='ignore')
    if suffix_cols:
        df = df.rename(columns={c: f"{c}_{suffix_cols}" for c in df.columns
                                  if c not in ['Player', 'Tm', 'MIN']})
    return df

# ── Load all files ────────────────────────────────────────────────────────────
print("Loading files...")
players  = load('JBLPlayers.csv')
per_game = load('JBLPerGame.csv')
advanced = load('JBLAdvanced.csv')
hustle   = load('JBLHustle.csv')
shot_loc = load('JBLShotLocations.csv')
on_off   = load('JBLOnOff.csv')
playoffs = load('JBLPlayoffs.csv')

# ── Fix JBLPlayTypes: rename duplicate columns by play type ──────────────────
print("Fixing JBLPlayTypes column names...")
pt_raw = load('JBLPlayTypes.csv')
# Base cols: Rk, Player, Pos, Age, Exp, Tm, G, GS, MIN, Plays
# Then 10 groups of (Pos/Possessions, PTS, PPP, eFG) — one per play type
new_pt_cols = ['Rk', 'Player', 'Pos', 'Age', 'Exp', 'Tm', 'G', 'GS', 'MIN', 'Plays']
for pt in PLAY_TYPES:
    new_pt_cols += [f'{pt}_Poss', f'{pt}_PTS', f'{pt}_PPP', f'{pt}_eFG']
pt_raw.columns = new_pt_cols
pt_raw['Player'] = pt_raw['Player'].astype(str).str.strip().str.lower()
pt_raw['Tm'] = normalize_team(pt_raw['Tm'])

# ── Fix OnOff MIN column (has commas like "2,212") ───────────────────────────
on_off['MIN'] = on_off['MIN'].astype(str).str.replace(',', '').str.strip()

# ── Rename ShotLocations % cols for clarity ──────────────────────────────────
shot_loc = shot_loc.rename(columns={
    '%':   'Pct_2PM_0_2ft',  '%.1': 'Pct_2PM_2_4ft',
    '%.2': 'Pct_2PM_4_6ft',  '%.3': 'Pct_2PM_6plus',
    '%.4': 'Pct_3PM_0_2ft',  '%.5': 'Pct_3PM_2_4ft',
    '%.6': 'Pct_3PM_4_6ft',  '%.7': 'Pct_3PM_6plus',
})
# Also rename 3PM/3PA/3P% in shot_loc to avoid conflict with PerGame
shot_loc = shot_loc.rename(columns={
    '3PM': 'SL_3PM', '3PA': 'SL_3PA', '3P%': 'SL_3P%',
    'FT':  'SL_FT',  'FTA': 'SL_FTA', 'FT%': 'SL_FT%',
    'MIN': 'MIN_shot'
})

# ── Rename column conflicts across files ──────────────────────────────────────
# Advanced has its own WS, MIN, TS%, etc.
advanced = advanced.rename(columns={
    'WS': 'WS_adv', 'WS/48': 'WS48_adv',
    'TS%': 'TS%_adv', 'ORtg': 'ORtg_adv', 'DRtg': 'DRtg_adv',
    'MIN': 'MIN_adv', 'Net': 'NetRtg_adv',
    'OWS': 'OWS_adv', 'DWS': 'DWS_adv',
    'PER': 'PER_adv', 'EWA': 'EWA_adv',
    'OBPM': 'OBPM_adv', 'DBPM': 'DBPM_adv', 'BPM': 'BPM_adv',
    'VORP': 'VORP_adv', 'ORB%': 'ORB%_adv', 'DRB%': 'DRB%_adv',
    'TRB%': 'TRB%_adv', 'AST%': 'AST%_adv', 'STL%': 'STL%_adv',
    'BLK%': 'BLK%_adv', 'TOV%': 'TOV%_adv', 'USG%': 'USG%_adv',
    'eFG%': 'eFG%_adv',
})
hustle = hustle.rename(columns={'MIN': 'MIN_hsl'})
on_off = on_off.rename(columns={'MIN': 'MIN_onoff'})

# Playoffs: prefix all stat cols
po_stats = [c for c in playoffs.columns if c not in ['Player', 'Tm', 'Rk', 'Pos', 'Age', 'Exp', 'G', 'GS']]
playoffs = playoffs.rename(columns={c: f'PO_{c}' for c in po_stats})

# PlayTypes: rename MIN
pt_raw = pt_raw.rename(columns={'MIN': 'MIN_pt'})

print("All files loaded and columns normalized.")

# ── Merge: JBLPlayers is the base (587 players) ──────────────────────────────
MERGE_KEY = ['Player', 'Tm']

def left_merge(base, df, label):
    df = df.drop(columns=[c for c in DROP_META if c in df.columns], errors='ignore')
    # Find a column unique to df (not in base) to use as match probe
    unique_cols = [c for c in df.columns if c not in MERGE_KEY and c not in base.columns]
    merged = pd.merge(base, df, on=MERGE_KEY, how='left', suffixes=('', f'_{label[:3]}'))
    if unique_cols:
        probe = unique_cols[0]
        matched = merged[probe].notna().sum()
    else:
        matched = len(merged)  # no unique col to probe, assume all matched
    print(f"  Merged {label}: {matched}/{len(base)} rows matched ({matched/len(base)*100:.1f}%)")
    return merged

print("\nMerging datasets onto JBLPlayers base (587 players)...")
merged = players.copy()
merged = left_merge(merged, per_game,  'JBLPerGame')
merged = left_merge(merged, advanced,  'JBLAdvanced')
merged = left_merge(merged, hustle,    'JBLHustle')
merged = left_merge(merged, shot_loc,  'JBLShotLocations')
merged = left_merge(merged, on_off,    'JBLOnOff')
merged = left_merge(merged, playoffs,  'JBLPlayoffs')
merged = left_merge(merged, pt_raw,    'JBLPlayTypes')

print(f"\nFinal merged shape: {merged.shape}")

# ── Feature Engineering ────────────────────────────────────────────────────────
print("\nEngineering features...")

# Clean salary
merged['Salary'] = pd.to_numeric(
    merged['Salary'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce'
)

# WS_actual from WS.1 (WS col in JBLPlayers is height data, WS.1 is actual Win Shares)
merged['WS_actual'] = pd.to_numeric(merged['WS.1'], errors='coerce')

# Numeric conversions
num_cols = ['VORP', 'PER', 'BPM', 'PPG', 'RPG', 'APG', 'USG%',
            'eFG%', 'TS%', '3P%', 'FG%', 'FT%',
            'WS_adv', 'WS48_adv', 'DWS_adv', 'OWS_adv',
            'VORP_adv', 'PER_adv', 'BPM_adv', 'OBPM_adv', 'DBPM_adv',
            'PM', 'BoxC', 'OL', 'Spc', 'aTOV', 'Adj3P%',
            'SA', 'SAPG', 'CSht', 'CSPG', 'DFL', 'DFPG', 'LBR', 'LBPG', 'CD', 'CDPG',
            'RimM', 'RimA', 'Rim%', 'ClsM', 'ClsA', 'Cls%',
            'MidM', 'MidA', 'Mid%', 'LngM', 'LngA', 'Lng%']
for c in num_cols:
    if c in merged.columns:
        merged[c] = pd.to_numeric(merged[c], errors='coerce')

# Use advanced stats where available (more precise), fall back to Players file
merged['WS']   = merged['WS_adv'].fillna(merged['WS_actual'])
merged['DWS']  = merged['DWS_adv'].fillna(pd.to_numeric(merged.get('DWS', pd.Series(dtype=float)), errors='coerce'))
merged['OWS']  = merged['OWS_adv'].fillna(pd.to_numeric(merged.get('OWS', pd.Series(dtype=float)), errors='coerce'))
merged['VORP'] = merged['VORP_adv'].fillna(pd.to_numeric(merged['VORP'], errors='coerce'))
merged['PER']  = merged['PER_adv'].fillna(pd.to_numeric(merged['PER'],  errors='coerce'))
merged['BPM']  = merged['BPM_adv'].fillna(pd.to_numeric(merged['BPM'],  errors='coerce'))

# Value Index: (WS + VORP) per $1M salary
sal_m = (merged['Salary'] / 1_000_000).replace(0, np.nan)
merged['ValueIndex']    = (merged['WS'].fillna(0) + merged['VORP'].fillna(0)) / sal_m
merged['DollarPerWS']   = merged['Salary'] / merged['WS'].replace(0, np.nan)
merged['ScorePerUsage'] = merged['PPG'] / pd.to_numeric(merged['USG%'], errors='coerce').replace(0, np.nan)

print("Feature engineering complete.")

# ── Verification: null counts on critical columns ─────────────────────────────
print("\n── CRITICAL COLUMN NULL AUDIT ──────────────────────────────────────────")
critical = {
    'Advanced':      ['PM', 'BoxC', 'OL', 'Spc', 'aTOV', 'Adj3P%', 'WS_adv', 'VORP_adv', 'BPM_adv'],
    'Hustle':        ['MIN_hsl', 'SA', 'SAPG', 'CSht', 'CSPG', 'DFL', 'DFPG', 'LBR', 'LBPG', 'CD', 'CDPG'],
    'Shot Location': ['RimM', 'RimA', 'Rim%', 'ClsM', 'ClsA', 'Cls%',
                      'MidM', 'MidA', 'Mid%', 'LngM', 'LngA', 'Lng%',
                      'SL_3PM', 'SL_3PA', 'SL_3P%',
                      '2PM 0-2ft', '2PA 0-2ft', 'Pct_2PM_0_2ft',
                      '3PM 0-2ft', '3PA 0-2ft', 'Pct_3PM_0_2ft'],
    'Play Types':    ['Isolation_Poss', 'Isolation_PTS', 'SpotUp_Poss', 'SpotUp_PTS',
                      'Transition_Poss', 'Transition_PTS'],
    'OnOff':         ['On ORtg', 'On DRtg', 'On Net', 'Floor Net'],
    'Computed':      ['WS', 'VORP', 'PER', 'BPM', 'ValueIndex'],
}
all_ok = True
for section, cols in critical.items():
    print(f"\n  [{section}]")
    for c in cols:
        if c in merged.columns:
            n_null = merged[c].isna().sum()
            pct    = n_null / len(merged) * 100
            flag   = " ⚠️  >50% NULL" if pct > 50 else ""
            if pct > 50: all_ok = False
            print(f"    {c:<28} null={n_null:>3} ({pct:5.1f}%){flag}")
        else:
            print(f"    {c:<28} *** COLUMN MISSING ***")
            all_ok = False

print(f"\n{'✅ All critical columns populated.' if all_ok else '⚠️  Some columns need attention.'}")

# ── Save outputs ──────────────────────────────────────────────────────────────
out_path = os.path.join(BASE, 'merged_JBL_Data.csv')
merged.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}  ({merged.shape[0]} rows × {merged.shape[1]} cols)")

# Player valuation ranking
val_cols = ['Player', 'Tm', 'Pos', 'Salary', 'WS', 'VORP', 'PER', 'BPM',
            'DWS', 'OWS', 'ValueIndex', 'DollarPerWS', 'PPG', 'RPG', 'APG',
            'Off Archetype', 'Def Archetype']
val_cols = [c for c in val_cols if c in merged.columns]
valuation = merged[val_cols].copy().sort_values('ValueIndex', ascending=False)
valuation.to_csv(os.path.join(BASE, 'player_valuation.csv'), index=False)
print(f"Saved: player_valuation.csv")

print("\nDone.")
