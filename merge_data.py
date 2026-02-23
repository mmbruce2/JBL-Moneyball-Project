import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

BASE = os.path.expanduser('~/Documents/JBL Datasets')

def load(filename, rename_cols=None):
    df = pd.read_csv(os.path.join(BASE, filename))
    df.columns = df.columns.str.strip()
    if 'Player' in df.columns:
        df['Player'] = df['Player'].str.strip().str.lower()
    if rename_cols:
        df = df.rename(columns=rename_cols)
    return df

# ----- 1. Load each file, only keeping what we need -----

players = load('JBLPlayers.csv')
# JBLPlayers has 'Tm' = Team col named 'Team'
players = players.rename(columns={'Team': 'Tm'})
players['Tm'] = players['Tm'].astype(str).str.strip().str.upper()

per_game = load('JBLPerGame.csv')
per_game['Tm'] = per_game['Tm'].astype(str).str.strip().str.upper()

advanced = load('JBLAdvanced.csv')
advanced['Tm'] = advanced['Tm'].astype(str).str.strip().str.upper()

hustle = load('JBLHustle.csv')
hustle['Tm'] = hustle['Tm'].astype(str).str.strip().str.upper()

shot_loc = load('JBLShotLocations.csv')
shot_loc['Tm'] = shot_loc['Tm'].astype(str).str.strip().str.upper()

on_off = load('JBLOnOff.csv')
on_off['Tm'] = on_off['Tm'].astype(str).str.strip().str.upper()

playoffs = load('JBLPlayoffs.csv')
playoffs['Tm'] = playoffs['Tm'].astype(str).str.strip().str.upper()

print("All files loaded successfully.")

# ----- 2. Merge on Player + Tm -----
MERGE_KEY = ['Player', 'Tm']

# Shared columns to drop before merging (keep only in base)
SHARED_STATS = ['Rk', 'Pos', 'Age', 'Exp', 'G', 'GS']

def clean_merge(base, new_df, suffix):
    """Drop duplicate non-key cols from new_df, then merge."""
    drop_cols = [c for c in SHARED_STATS if c in new_df.columns]
    new_df = new_df.drop(columns=drop_cols, errors='ignore')
    return pd.merge(base, new_df, on=MERGE_KEY, how='left', suffixes=('', f'_{suffix}'))

merged = players.copy()
merged = clean_merge(merged, per_game,  'pg')
merged = clean_merge(merged, advanced,  'adv')
merged = clean_merge(merged, hustle,    'hsl')
merged = clean_merge(merged, shot_loc,  'shot')
merged = clean_merge(merged, on_off,    'onoff')

# Playoffs as separate columns with prefix
playoffs_clean = playoffs.drop(columns=SHARED_STATS, errors='ignore')
playoffs_clean.columns = [
    ('PO_' + c if c not in MERGE_KEY else c) for c in playoffs_clean.columns
]
merged = pd.merge(merged, playoffs_clean, on=MERGE_KEY, how='left')

print(f"Merged shape: {merged.shape}")
print(f"Total players: {merged['Player'].nunique()}")

# ----- 3. Feature Engineering -----

# Value Score: composite efficiency relative to salary
if 'Salary' in merged.columns:
    merged['Salary'] = pd.to_numeric(merged['Salary'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')

    # WS.1 is actual Win Shares in JBLPlayers (WS col is height data - naming quirk)
    ws_col = 'WS.1' if 'WS.1' in merged.columns else 'WS'
    merged['WS_actual'] = pd.to_numeric(merged[ws_col], errors='coerce')
    merged['VORP']      = pd.to_numeric(merged.get('VORP', pd.Series()), errors='coerce')
    merged['PER']       = pd.to_numeric(merged.get('PER',  pd.Series()), errors='coerce')
    merged['BPM']       = pd.to_numeric(merged.get('BPM',  pd.Series()), errors='coerce')

    # Dollars per Win Share
    merged['$/WS_calc'] = merged['Salary'] / merged['WS_actual'].replace(0, float('nan'))

    # Value Index: WS + VORP per $1M salary (higher = better deal)
    sal_millions = (merged['Salary'] / 1_000_000).replace(0, float('nan'))
    merged['ValueIndex'] = (merged['WS_actual'].fillna(0) + merged['VORP'].fillna(0)) / sal_millions

# Shooting efficiency features
for col in ['FG%', '3P%', 'FT%', 'TS%', 'eFG%']:
    if col in merged.columns:
        merged[col] = pd.to_numeric(merged[col], errors='coerce')

# Usage-adjusted scoring
if all(c in merged.columns for c in ['PPG', 'USG%']):
    merged['PPG']  = pd.to_numeric(merged['PPG'], errors='coerce')
    merged['USG%'] = pd.to_numeric(merged['USG%'], errors='coerce')
    merged['ScorePerUsage'] = merged['PPG'] / merged['USG%'].replace(0, float('nan'))

print("Feature engineering complete.")

# ----- 4. Player Valuation Rankings -----

val_cols = ['Player', 'Tm', 'Pos', 'Salary', 'WS_actual', 'VORP', 'PER', 'BPM', 'ValueIndex', '$/WS_calc', 'PPG', 'RPG', 'APG']
val_cols = [c for c in val_cols if c in merged.columns]

valuation = merged[val_cols].copy()
valuation = valuation.sort_values('ValueIndex', ascending=False)

print("\n--- Top 20 Best Value Players ---")
print(valuation.head(20).to_string(index=False))

# ----- 5. Save outputs -----

merged.to_csv(os.path.join(BASE, 'merged_JBL_Data.csv'), index=False)
valuation.to_csv(os.path.join(BASE, 'player_valuation.csv'), index=False)

# Summary markdown report
report_lines = [
    "# JBL Moneyball Analysis Report\n",
    f"**Total Players:** {merged['Player'].nunique()}  ",
    f"**Total Columns:** {merged.shape[1]}  \n",
    "## Top 20 Best Value Players (ValueIndex = WS+VORP per $1M salary)\n",
    valuation.head(20).to_markdown(index=False),
    "\n## Bottom 10 Overpaid Players\n",
    valuation.dropna(subset=['ValueIndex']).tail(10).to_markdown(index=False),
]
with open(os.path.join(BASE, 'analysis_report.md'), 'w') as f:
    f.write('\n'.join(str(l) for l in report_lines))

print("\nFiles saved:")
print("  - merged_JBL_Data.csv")
print("  - player_valuation.csv")
print("  - analysis_report.md")
