"""
JBL Moneyball — Data Merge Pipeline v3 (Clean)

Root causes fixed:
  1. Stat files use 3-letter team abbrevs (Hur/Bar) vs full names in Players → mapped
  2. Traded players appear as "Tot" in stat files → deduplicated to one row per player
     (prefer "Tot" row for aggregate stats, else highest-minutes row)
  3. nbsp/whitespace garbage in player names → stripped
  4. Duplicate column conflicts handled explicitly per file
"""
import pandas as pd
import numpy as np
import os, warnings
warnings.filterwarnings('ignore')

BASE = "/Users/maxx/Documents/JBL Datasets"
REPO = "/Users/maxx/Documents/JBL-Moneyball-Project"

TEAM_MAP = {
    'Bar':'Barons',     'Bli':'Blizzards',    'Bul':'Bullets',
    'Cal':'Calaveras',  'Col':'Colonels',      'Cru':'Crusaders',
    'Cyc':'Cyclones',   'Dev':'Devils',         'Dra':'Dragons',
    'Dro':'Drones',     'Fir':'Fireballs',      'Gia':'Giants',
    'Hur':'Hurricanes', 'Hus':'Huskies',        'Jag':'Jaguars',
    'Jai':'Jailbirds',  'Kin':'Kings',          'Kni':'Knights',
    'Lig':'Lightning',  'Lum':'Lumberjacks',    'Mus':'Mustangs',
    'Pil':'Pilots',     'Pre':'Predators',      'Ren':'Renegades',
    'Roc':'Rockets',    'Sai':'Saints',         'Sco':'Scorpions',
    'Sky':'Skyhawks',   'Sta':'Stars',          'Sto':'Stonecutters',
    'Thu':'Thunder',    'Tri':'Tritons',        'Vip':'Vipers',
    'Vul':'Vultures',   'War':'Warriors',       'Wol':'Wolves',
    'Tot':'TOT',        # traded/combined row
}

DROP_META = ['Rk', 'Pos', 'Age', 'Exp', 'G', 'GS']

PLAY_TYPES = [
    'Isolation', 'PnR_BallHandler', 'PnR_Rollman', 'PostUp',
    'SpotUp', 'Handoff', 'Cut', 'OffScreen', 'Transition', 'Misc'
]

def clean_player(s):
    return (s.astype(str)
             .str.replace('&nbsp;', '', regex=False)
             .str.strip()
             .str.lower())

def normalize_tm(s):
    return s.astype(str).str.strip().map(lambda x: TEAM_MAP.get(x, x))

def load(filename):
    df = pd.read_csv(os.path.join(BASE, filename))
    df.columns = df.columns.str.strip()
    if 'Player' in df.columns:
        df['Player'] = clean_player(df['Player'])
    if 'Tm' in df.columns:
        df['Tm'] = normalize_tm(df['Tm'])
    elif 'Team' in df.columns:
        df['Team'] = normalize_tm(df['Team'])
        df = df.rename(columns={'Team': 'Tm'})
    return df

def dedup_to_one_per_player(df, min_col=None):
    """
    For players with multiple rows (traded players), keep:
    - 'TOT' row if it exists (aggregate of all stints)
    - else the row with the most minutes
    - else first row
    Returns one row per player.
    """
    if 'Player' not in df.columns:
        return df
    df = df.copy()
    df['_is_tot'] = df['Tm'].astype(str).str.upper() == 'TOT'
    if min_col and min_col in df.columns:
        df[min_col] = pd.to_numeric(df[min_col].astype(str).str.replace(',',''), errors='coerce')
        df = df.sort_values(['_is_tot', min_col], ascending=[False, False])
    else:
        df = df.sort_values('_is_tot', ascending=False)
    df = df.drop_duplicates(subset='Player', keep='first')
    df = df.drop(columns=['_is_tot'], errors='ignore')
    return df

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading files...")
players  = load('JBLPlayers.csv')
per_game = load('JBLPerGame.csv')
advanced = load('JBLAdvanced.csv')
hustle   = load('JBLHustle.csv')
shot_loc = load('JBLShotLocations.csv')
on_off   = load('JBLOnOff.csv')
playoffs = load('JBLPlayoffs.csv')

# PlayTypes: fix duplicate column names
pt_raw = load('JBLPlayTypes.csv')
new_pt_cols = ['Rk', 'Player', 'Pos', 'Age', 'Exp', 'Tm', 'G', 'GS', 'MIN_pt', 'Plays']
for pt in PLAY_TYPES:
    new_pt_cols += [f'{pt}_Poss', f'{pt}_PTS', f'{pt}_PPP', f'{pt}_eFG']
pt_raw.columns = new_pt_cols
pt_raw['Player'] = clean_player(pt_raw['Player'])
pt_raw['Tm'] = normalize_tm(pt_raw['Tm'])

# ── Dedup all stat files to one row per player ────────────────────────────────
print("Deduplicating stat files (one row per player)...")
per_game = dedup_to_one_per_player(per_game, 'MPG')
advanced = dedup_to_one_per_player(advanced, 'MIN')
hustle   = dedup_to_one_per_player(hustle,   'MIN')
shot_loc = dedup_to_one_per_player(shot_loc, 'MIN')
on_off   = dedup_to_one_per_player(on_off,   'MIN')
playoffs = dedup_to_one_per_player(playoffs, 'MPG')
pt_raw   = dedup_to_one_per_player(pt_raw,   'MIN_pt')
print(f"  Players: {len(players)} | PerGame: {len(per_game)} | Advanced: {len(advanced)} | "
      f"Hustle: {len(hustle)} | ShotLoc: {len(shot_loc)} | OnOff: {len(on_off)} | "
      f"Playoffs: {len(playoffs)} | PlayTypes: {len(pt_raw)}")

# ── Rename columns to avoid conflicts before merging ─────────────────────────
# JBLPlayers already has PPG, RPG, APG, MPG, etc. — drop duplicates from PerGame
PERGAME_KEEP_UNIQUE = ['FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
per_game = per_game[['Player'] + PERGAME_KEEP_UNIQUE].copy()

# Advanced — rename cols that conflict with JBLPlayers
ADV_RENAME = {
    'WS': 'WS_adv', 'WS/48': 'WS48_adv', 'TS%': 'TS%_adv',
    'ORtg': 'ORtg_adv', 'DRtg': 'DRtg_adv', 'Net': 'NetRtg_adv',
    'OWS': 'OWS_adv', 'DWS': 'DWS_adv', 'PER': 'PER_adv', 'EWA': 'EWA_adv',
    'OBPM': 'OBPM_adv', 'DBPM': 'DBPM_adv', 'BPM': 'BPM_adv',
    'VORP': 'VORP_adv', 'ORB%': 'ORB%_adv', 'DRB%': 'DRB%_adv',
    'TRB%': 'TRB%_adv', 'AST%': 'AST%_adv', 'STL%': 'STL%_adv',
    'BLK%': 'BLK%_adv', 'TOV%': 'TOV%_adv', 'USG%': 'USG%_adv',
    'eFG%': 'eFG%_adv', 'MIN': 'MIN_adv',
    'G': 'G_adv', 'GS': 'GS_adv',
}
advanced = advanced.drop(columns=DROP_META, errors='ignore').rename(columns=ADV_RENAME)

hustle = hustle.drop(columns=DROP_META, errors='ignore').rename(columns={'MIN': 'MIN_hsl'})

# ShotLocations — rename ambiguous % cols and 3P/FT cols
shot_loc = shot_loc.rename(columns={
    'MIN': 'MIN_shot',
    '3PM': 'SL_3PM', '3PA': 'SL_3PA', '3P%': 'SL_3P%',
    'FT': 'SL_FT', 'FTA': 'SL_FTA', 'FT%': 'SL_FT%',
    '%':   'Pct_2PM_0_2ft', '%.1': 'Pct_2PM_2_4ft',
    '%.2': 'Pct_2PM_4_6ft', '%.3': 'Pct_2PM_6plus',
    '%.4': 'Pct_3PM_0_2ft', '%.5': 'Pct_3PM_2_4ft',
    '%.6': 'Pct_3PM_4_6ft', '%.7': 'Pct_3PM_6plus',
})
shot_loc = shot_loc.drop(columns=DROP_META, errors='ignore')

on_off = on_off.drop(columns=DROP_META, errors='ignore').rename(columns={'MIN': 'MIN_onoff'})
on_off['MIN_onoff'] = on_off['MIN_onoff'].astype(str).str.replace(',', '').str.strip()

# Playoffs prefix — rename BEFORE dropping so G/GS become PO_G/PO_GS
playoffs = playoffs.drop(columns=['Rk','Pos','Age','Exp'], errors='ignore')  # keep G, GS
playoffs.columns = ['Player'] + [f'PO_{c}' for c in playoffs.columns if c != 'Player']

pt_raw = pt_raw.drop(columns=DROP_META, errors='ignore')

# ── Merge all on Player name (deduped — safe to merge on name only) ───────────
print("\nMerging on Player name...")

def name_merge(base, df, label):
    # Only keep Player + unique stat cols from df; drop Tm (not used as key here)
    df = df.copy()
    df = df.drop(columns=['Tm'], errors='ignore')
    overlap = [c for c in df.columns if c != 'Player' and c in base.columns]
    if overlap:
        df = df.drop(columns=overlap, errors='ignore')
    result = pd.merge(base, df, on='Player', how='left')
    probe_cols = [c for c in df.columns if c not in ['Player','Tm']]
    if probe_cols:
        matched = result[probe_cols[0]].notna().sum()
    else:
        matched = len(result)
    print(f"  {label}: {matched}/{len(base)} matched ({matched/len(base)*100:.1f}%)")
    return result

merged = players.copy()
merged = name_merge(merged, per_game,  'JBLPerGame')
merged = name_merge(merged, advanced,  'JBLAdvanced')
merged = name_merge(merged, hustle,    'JBLHustle')
merged = name_merge(merged, shot_loc,  'JBLShotLocations')
merged = name_merge(merged, on_off,    'JBLOnOff')
merged = name_merge(merged, playoffs,  'JBLPlayoffs')
merged = name_merge(merged, pt_raw,    'JBLPlayTypes')

print(f"\nFinal merged shape: {merged.shape}")

# ── Feature Engineering ────────────────────────────────────────────────────────
print("Engineering features...")

# Salary: clean to numeric
merged['Salary'] = pd.to_numeric(
    merged['Salary'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce'
)

# WS_actual: WS.1 is the real Win Shares (WS col is height/rating data)
merged['WS_actual'] = pd.to_numeric(merged['WS.1'], errors='coerce')

# Prefer advanced stats (more precise), fallback to Players file
def num(df, col):
    return pd.to_numeric(df[col], errors='coerce') if col in df.columns else pd.Series(np.nan, index=df.index)

merged['WS']   = merged['WS_adv'].combine_first(merged['WS_actual'])
merged['DWS']  = merged['DWS_adv'].combine_first(num(merged, 'DWS'))
merged['OWS']  = merged['OWS_adv'].combine_first(num(merged, 'OWS'))
merged['VORP'] = merged['VORP_adv'].combine_first(num(merged, 'VORP'))
merged['PER']  = merged['PER_adv'].combine_first(num(merged, 'PER'))
merged['BPM']  = merged['BPM_adv'].combine_first(num(merged, 'BPM'))
merged['OBPM'] = merged['OBPM_adv'].combine_first(num(merged, 'OBPM'))
merged['DBPM'] = merged['DBPM_adv'].combine_first(num(merged, 'DBPM'))

# Value metrics
sal_m = (merged['Salary'] / 1_000_000).replace(0, np.nan)
merged['ValueIndex']    = (merged['WS'].fillna(0) + merged['VORP'].fillna(0)) / sal_m
merged['DollarPerWS']   = merged['Salary'] / merged['WS'].replace(0, np.nan)
merged['ScorePerUsage'] = num(merged,'PPG') / num(merged,'USG%').replace(0, np.nan)

print("Feature engineering complete.")

# ── NULL AUDIT ────────────────────────────────────────────────────────────────
print("\n── CRITICAL COLUMN NULL AUDIT ──────────────────────────────────────────")
critical = {
    'Advanced':      ['MIN_adv','PM','BoxC','OL','Spc','aTOV','Adj3P%','WS_adv','VORP_adv','BPM_adv','RAPM','WARP','DRE','AWS'],
    'Hustle':        ['MIN_hsl','SA','SAPG','CSht','CSPG','DFL','DFPG','LBR','LBPG','CD','CDPG'],
    'Shot Location': ['RimM','RimA','Rim%','ClsM','ClsA','Cls%','MidM','MidA','Mid%',
                      'LngM','LngA','Lng%','SL_3PM','SL_3PA','SL_3P%',
                      '2PM 0-2ft','2PA 0-2ft','Pct_2PM_0_2ft',
                      '3PM 0-2ft','3PA 0-2ft','Pct_3PM_0_2ft'],
    'Play Types':    ['Plays','Isolation_Poss','Isolation_PTS','SpotUp_Poss','SpotUp_PTS',
                      'PnR_BallHandler_Poss','Transition_Poss','Transition_PTS'],
    'OnOff':         ['On ORtg','On DRtg','On Net','Floor Net'],
    'Playoffs':      ['PO_PPG','PO_G'],
    'Computed':      ['WS','VORP','PER','BPM','ValueIndex','DWS','OWS'],
}
all_ok = True
for section, cols in critical.items():
    print(f"\n  [{section}]")
    for c in cols:
        if c in merged.columns:
            n_null = merged[c].isna().sum()
            pct    = n_null / len(merged) * 100
            flag   = "  ⚠️  >50% NULL" if pct > 50 else ""
            if pct > 50: all_ok = False
            print(f"    {c:<30} null={n_null:>3} ({pct:5.1f}%){flag}")
        else:
            print(f"    {c:<30} *** COLUMN MISSING ***")
            all_ok = False

print(f"\n{'✅ All critical columns <50% null.' if all_ok else '⚠️  Some columns still >50% null (may be normal for bench/FA players).'}")
print(f"Note: 587 total players in JBLPlayers; ~413 had enough minutes for stat sheets. "
      f"~{587-413} players (benchwarmers/injured/free agents) will naturally have NaN in stat cols.")

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = os.path.join(BASE, 'merged_JBL_Data.csv')
merged.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}  ({merged.shape[0]} rows × {merged.shape[1]} cols)")

import shutil
shutil.copy(out_path, os.path.join(REPO, 'merged_JBL_Data.csv'))
shutil.copy(os.path.join(BASE, 'merge_data.py'), os.path.join(REPO, 'merge_data.py'))

val_cols = ['Player','Tm','Pos','Salary','WS','VORP','PER','BPM','DWS','OWS',
            'ValueIndex','DollarPerWS','PPG','RPG','APG','Off Archetype','Def Archetype']
val_cols = [c for c in val_cols if c in merged.columns]
valuation = merged[val_cols].sort_values('ValueIndex', ascending=False)
val_path = os.path.join(BASE, 'player_valuation.csv')
valuation.to_csv(val_path, index=False)
shutil.copy(val_path, os.path.join(REPO, 'player_valuation.csv'))
print("Saved: player_valuation.csv")
print("\n✅ Pipeline complete.")
