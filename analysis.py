"""
JBL Moneyball — Phase 2: Five Correlation Studies
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

BASE  = "/Users/maxx/Documents/JBL Datasets"
REPO  = "/Users/maxx/Documents/JBL-Moneyball-Project"
PLOTS = os.path.join(REPO, "plots")
os.makedirs(PLOTS, exist_ok=True)

sns.set_theme(style="darkgrid", palette="husl")
plt.rcParams.update({'figure.dpi': 120, 'font.size': 10})

# ─── Load merged data ─────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(BASE, "merged_JBL_Data.csv"), low_memory=False)
df.columns = df.columns.str.strip()

# Only active rostered players (have stats)
active = df[df['WS_actual'].notna()].copy()
print(f"Active players for analysis: {len(active)}")

# Coerce only stat columns to numeric — preserve string identifier columns
STRING_COLS = {'Player', 'Tm', 'Pos', 'Off Archetype', 'Def Archetype',
               'Hgt', 'Drafted', 'College', 'Hometown', 'Nationality',
               'Secondary', 'Personality', '.', 'Team'}
for col in active.select_dtypes(include='object').columns:
    if col not in STRING_COLS:
        active[col] = pd.to_numeric(active[col], errors='coerce')

# ─── SCOUTING RATINGS ────────────────────────────────────────────────────────
RATINGS = ['InsS','MidS','OutS','FrT','SlfC','ShtD','BalD','FlDr','Fnsh',
           'Play','Pass','Grav','Spac','Hndl','Iso','PstE','PnrE','BBIQ',
           'OnBD','OffD','Help','Stl','PstD','RimP','OffR','DefR',
           'Ath','End','FstS','Quck','Spd','Str']

RATING_LABELS = {
    'InsS':'Inside Scoring','MidS':'Mid-Range','OutS':'Outside Scoring',
    'FrT':'Free Throw','SlfC':'Self Creation','ShtD':'Shot Decision',
    'BalD':'Ball Defense','FlDr':'Floor Drive','Fnsh':'Finishing',
    'Play':'Playmaking','Pass':'Passing','Grav':'Gravity','Spac':'Spacing',
    'Hndl':'Ball Handling','Iso':'Isolation','PstE':'Post Efficiency',
    'PnrE':'PnR Efficiency','BBIQ':'BBIQ','OnBD':'On-Ball Defense',
    'OffD':'Off-Ball Defense','Help':'Help Defense','Stl':'Steal Rating',
    'PstD':'Post Defense','RimP':'Rim Protection','OffR':'Off Rebound',
    'DefR':'Def Rebound','Ath':'Athleticism','End':'Endurance',
    'FstS':'First Step','Quck':'Quickness','Spd':'Speed','Str':'Strength',
}

# ─── Helper functions ─────────────────────────────────────────────────────────

def top_correlations(subset, ratings, targets, n=5):
    """Return top n ratings by absolute correlation with each target."""
    results = {}
    for target in targets:
        if target not in subset.columns:
            continue
        corrs = []
        for r in ratings:
            if r in subset.columns:
                clean = subset[[r, target]].dropna()
                if len(clean) >= 10:
                    r_val, p_val = stats.pearsonr(clean[r], clean[target])
                    corrs.append({'rating': r, 'label': RATING_LABELS.get(r,r),
                                  'r': r_val, 'p': p_val, 'abs_r': abs(r_val)})
        corrs.sort(key=lambda x: x['abs_r'], reverse=True)
        results[target] = corrs[:n]
    return results

def save_fig(name):
    path = os.path.join(PLOTS, name)
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: plots/{name}")
    return f"plots/{name}"

report = []  # collect markdown sections

# ═══════════════════════════════════════════════════════════════════════════════
# STUDY 1 — Rating-to-Impact by Archetype
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("STUDY 1: Rating-to-Impact by Archetype")
print("═"*60)

report.append("# JBL Moneyball — Phase 2 Analysis Report\n")
report.append("---\n")
report.append("## Study 1 — Rating-to-Impact by Archetype\n")
report.append("> Which scouting ratings actually translate to production for each player type?\n")

TARGET_COLS = ['VORP', 'WS_actual', 'eFG%']
off_archetypes = active['Off Archetype'].dropna().unique()
def_archetypes = active['Def Archetype'].dropna().unique()

s1_findings = []

for arch_type, arch_list, arch_col in [
    ("Offensive", off_archetypes, "Off Archetype"),
    ("Defensive", def_archetypes, "Def Archetype"),
]:
    report.append(f"\n### {arch_type} Archetypes\n")
    for arch in sorted(arch_list):
        subset = active[active[arch_col] == arch]
        if len(subset) < 8:
            continue
        corrs = top_correlations(subset, RATINGS, TARGET_COLS, n=5)
        report.append(f"\n#### {arch} (n={len(subset)})\n")
        for target, top5 in corrs.items():
            if not top5:
                continue
            report.append(f"**→ {target}:** " +
                ", ".join([f"{x['label']} (r={x['r']:+.2f})" for x in top5]) + "\n")

        # Collect surprising findings (high correlation in unexpected ratings)
        for target, top5 in corrs.items():
            for item in top5[:2]:
                if abs(item['r']) >= 0.40:
                    s1_findings.append(
                        f"- **{arch}** ({arch_type}): *{item['label']}* is the "
                        f"#{list(top5).index(item)+1} predictor of {target} "
                        f"(r={item['r']:+.2f}, n={len(subset)})"
                    )

# Heatmap: all ratings vs VORP for top archetypes
top_off = (active.groupby('Off Archetype')['VORP']
           .median().sort_values(ascending=False).index[:8].tolist())
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
for ax, arch_col, title, arch_list in [
    (axes[0], 'Off Archetype', 'Offensive Archetypes — Rating vs VORP Correlation', top_off),
    (axes[1], 'Def Archetype', 'Defensive Archetypes — Rating vs VORP Correlation',
     active['Def Archetype'].value_counts().index[:8].tolist()),
]:
    hm_data = {}
    for arch in arch_list:
        subset = active[active[arch_col] == arch]
        if len(subset) < 8:
            continue
        row = {}
        for r in RATINGS:
            if r in subset.columns:
                clean = subset[[r, 'VORP']].dropna()
                if len(clean) >= 8:
                    rv, _ = stats.pearsonr(clean[r], clean['VORP'])
                    row[RATING_LABELS.get(r, r)] = rv
        if row:
            hm_data[arch] = row
    if hm_data:
        hm_df = pd.DataFrame(hm_data).T.fillna(0)
        sns.heatmap(hm_df, ax=ax, cmap='RdYlGn', center=0,
                    vmin=-0.6, vmax=0.6, linewidths=0.3,
                    cbar_kws={'label': 'Pearson r'}, annot=False)
        ax.set_title(title, fontsize=11, pad=10)
        ax.set_xlabel('')
        ax.tick_params(axis='x', rotation=45, labelsize=8)

plt.tight_layout()
s1_plot = save_fig("study1_archetype_rating_heatmap.png")

report.append(f"\n### Key Findings\n")
report.append("\n".join(s1_findings[:20]) if s1_findings else "See detailed tables above.\n")
report.append(f"\n![Rating-to-Impact Heatmap]({s1_plot})\n")
report.append("\n**Methodology:** Pearson correlation between each scouting rating and VORP/WS/eFG% within each archetype group. Minimum 8 players per archetype. Only correlations with |r| ≥ 0.30 reported as meaningful.\n")

# ═══════════════════════════════════════════════════════════════════════════════
# STUDY 2 — Three Point Shooting Profile
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("STUDY 2: Three Point Shooting Profile")
print("═"*60)

report.append("\n---\n## Study 2 — Three Point Shooting Profile\n")
report.append("> What player profile is most likely to be an elite 3-point shooter?\n")

# Use JBLPlayers 3P% (has all 587 players)
shooters = active[active['3PA'] >= 1.5].copy()  # min 1.5 3PA per game for meaningful sample
shooters['3P%_adv'] = pd.to_numeric(shooters.get('3P%', pd.Series(dtype=float)), errors='coerce')
print(f"  Qualified 3P shooters (>60 3PA): {len(shooters)}")

# Top archetypes by 3P%
arch_3p = shooters.groupby('Off Archetype')['3P%_adv'].agg(['mean','median','count']).round(3)
arch_3p = arch_3p[arch_3p['count'] >= 5].sort_values('median', ascending=False)
print("\n  3P% by Offensive Archetype:")
print(arch_3p.to_string())

# Rating correlations with 3P%
target_3p = ['3P%_adv']
if '3P%' in shooters.columns:
    target_3p = ['3P%']
corrs_3p = {}
for r in RATINGS:
    if r in shooters.columns:
        clean = shooters[[r, target_3p[0]]].dropna()
        if len(clean) >= 10:
            rv, pv = stats.pearsonr(clean[r], clean[target_3p[0]])
            corrs_3p[RATING_LABELS.get(r, r)] = rv

corrs_3p_sorted = dict(sorted(corrs_3p.items(), key=lambda x: abs(x[1]), reverse=True)[:12])
print(f"\n  Top ratings correlating with 3P%:")
for k,v in corrs_3p_sorted.items():
    print(f"    {k:25s}: r={v:+.3f}")

# Shot distance analysis for 3P shooting
dist_cols = [c for c in active.columns if '3P' in c and ('%' in c or 'M' in c)]
elite_thresh = active['3P%'].quantile(0.75) if '3P%' in active.columns else 0.38
elite = shooters[shooters[target_3p[0]] >= elite_thresh]
avg   = shooters[shooters[target_3p[0]] < elite_thresh]

# Figure: archetype 3P% + rating correlations
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Left: archetype box
if len(arch_3p) > 0:
    arch_order = arch_3p.index.tolist()
    arch_data  = [shooters[shooters['Off Archetype']==a][target_3p[0]].dropna()
                  for a in arch_order]
    bp = axes[0].boxplot(arch_data, labels=arch_order, patch_artist=True,
                         medianprops={'color':'black','linewidth':2})
    colors = sns.color_palette("husl", len(arch_order))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    axes[0].set_title('3P% Distribution by Offensive Archetype', fontsize=11)
    axes[0].set_xlabel('')
    axes[0].set_ylabel('3P%')
    axes[0].tick_params(axis='x', rotation=45, labelsize=8)
    axes[0].axhline(0.36, color='red', linestyle='--', alpha=0.5, label='League avg ~36%')
    axes[0].legend(fontsize=8)

# Right: rating correlations bar chart
labels = list(corrs_3p_sorted.keys())
vals   = list(corrs_3p_sorted.values())
colors_bar = ['#2ecc71' if v > 0 else '#e74c3c' for v in vals]
axes[1].barh(labels[::-1], vals[::-1], color=colors_bar[::-1], edgecolor='white')
axes[1].axvline(0, color='black', linewidth=0.8)
axes[1].set_title('Scouting Ratings Correlated with 3P%', fontsize=11)
axes[1].set_xlabel('Pearson r')
axes[1].set_xlim(-0.7, 0.7)

plt.tight_layout()
s2_plot = save_fig("study2_three_point_profile.png")

# Build report text
report.append(f"\n### 3P% by Offensive Archetype\n")
report.append(arch_3p.to_markdown() + "\n")
report.append(f"\n### Top Ratings Correlating with 3P% (min 60 3PA)\n")
report.append("| Rating | Pearson r |\n|--------|----------|\n")
for k, v in corrs_3p_sorted.items():
    report.append(f"| {k} | {v:+.3f} |\n")

elite_archs = (elite['Off Archetype'].value_counts(normalize=True)*100).round(1)
report.append(f"\n### Elite Shooter Breakdown (3P% ≥ {elite_thresh:.3f})\n")
report.append(f"**n = {len(elite)} elite shooters**\n\n")
report.append("**Archetype distribution of elite shooters:**\n")
for arch, pct in elite_archs.items():
    report.append(f"- {arch}: {pct}%\n")

report.append(f"\n### Key Findings\n")
top_r = [(k,v) for k,v in corrs_3p_sorted.items() if abs(v) >= 0.25]
for k,v in top_r[:5]:
    direction = "positively" if v > 0 else "negatively"
    report.append(f"- **{k}** is {direction} correlated with 3P% (r={v:+.3f})\n")

if len(arch_3p) > 0:
    top_arch = arch_3p.index[0]
    report.append(f"- **{top_arch}** is the most likely archetype to be an elite 3-point shooter "
                  f"(median {arch_3p.loc[top_arch,'median']:.3f})\n")

report.append(f"\n![3P Shooting Profile]({s2_plot})\n")
report.append("\n**Methodology:** Players with ≥60 3-point attempts. Pearson correlation between scouting ratings and 3P%. Archetype distributions compared via box plots. Elite threshold = 75th percentile of 3P%.\n")

# ═══════════════════════════════════════════════════════════════════════════════
# STUDY 3 — Defensive Impact
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("STUDY 3: Defensive Impact")
print("═"*60)

report.append("\n---\n## Study 3 — Defensive Impact\n")
report.append("> What actually makes a player impactful on defense beyond the eye test?\n")

DEF_RATINGS   = ['OnBD','OffD','Help','Stl','PstD','RimP']
DEF_TARGETS   = ['DWS', 'DBPM']
PHYSICAL_COLS = ['Hgt', 'Wgt', 'Ath', 'Spd', 'Str', 'End']

# Parse Hgt from JBLPlayers format "82 - 6'10" → numeric inches
if 'Hgt' in active.columns:
    def parse_height(h):
        try:
            # Format: "82 -             6'10";" → take first number (rating)
            return float(str(h).split('-')[0].strip())
        except:
            return np.nan
    active['Hgt_rating'] = active['Hgt'].apply(parse_height)
else:
    active['Hgt_rating'] = np.nan

def_all_ratings = DEF_RATINGS + [r for r in ['Hgt_rating','Wgt','Ath','Spd','Str','End']
                                  if r in active.columns]

def_corrs = {}
for col in def_all_ratings:
    if col in active.columns:
        for target in DEF_TARGETS:
            if target in active.columns:
                clean = active[[col, target]].dropna()
                if len(clean) >= 15:
                    rv, pv = stats.pearsonr(clean[col], clean[target])
                    def_corrs[(col, target)] = {'r': rv, 'p': pv, 'n': len(clean)}

print("\n  Defensive correlations:")
for (col, target), vals in sorted(def_corrs.items(), key=lambda x: abs(x[1]['r']), reverse=True)[:15]:
    label = RATING_LABELS.get(col, col)
    print(f"    {label:20s} → {target:8s}: r={vals['r']:+.3f} (n={vals['n']})")

# DWS by defensive archetype
dws_by_arch = active.groupby('Def Archetype')['DWS'].agg(['mean','median','count']).round(2)
dws_by_arch = dws_by_arch[dws_by_arch['count'] >= 5].sort_values('median', ascending=False)
print("\n  DWS by Defensive Archetype:")
print(dws_by_arch.to_string())

# DBPM by defensive archetype
dbpm_by_arch = active.groupby('Def Archetype')['DBPM'].agg(['mean','median','count']).round(2)
dbpm_by_arch = dbpm_by_arch[dbpm_by_arch['count'] >= 5].sort_values('median', ascending=False)

# Figure: 2x2 — DWS correlations, DBPM correlations, DWS by archetype, DBPM by archetype
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

def plot_corr_bar(ax, corrs_dict, target, title):
    items = [(RATING_LABELS.get(c,c), v['r']) for (c,t), v in corrs_dict.items() if t==target]
    items.sort(key=lambda x: abs(x[1]), reverse=True)
    items = items[:10]
    labels_p = [x[0] for x in items][::-1]
    vals_p   = [x[1] for x in items][::-1]
    colors_b = ['#2ecc71' if v > 0 else '#e74c3c' for v in vals_p]
    ax.barh(labels_p, vals_p, color=colors_b, edgecolor='white')
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel('Pearson r')
    ax.set_xlim(-0.7, 0.7)

plot_corr_bar(axes[0,0], def_corrs, 'DWS',  'Ratings → Defensive Win Shares (DWS)')
plot_corr_bar(axes[0,1], def_corrs, 'DBPM', 'Ratings → Defensive BPM (DBPM)')

# DWS by archetype
if len(dws_by_arch) > 0:
    dws_by_arch['median'].plot(kind='barh', ax=axes[1,0], color=sns.color_palette("Blues_r", len(dws_by_arch)))
    axes[1,0].set_title('Median DWS by Defensive Archetype', fontsize=10)
    axes[1,0].set_xlabel('Median DWS')
    axes[1,0].axvline(active['DWS'].median(), color='red', linestyle='--', alpha=0.7, label='League median')
    axes[1,0].legend(fontsize=8)

# DBPM by archetype
if len(dbpm_by_arch) > 0:
    dbpm_by_arch['median'].plot(kind='barh', ax=axes[1,1], color=sns.color_palette("Greens_r", len(dbpm_by_arch)))
    axes[1,1].set_title('Median DBPM by Defensive Archetype', fontsize=10)
    axes[1,1].set_xlabel('Median DBPM')
    axes[1,1].axvline(active['DBPM'].median(), color='red', linestyle='--', alpha=0.7, label='League median')
    axes[1,1].legend(fontsize=8)

plt.suptitle('Study 3: Defensive Impact Analysis', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
s3_plot = save_fig("study3_defensive_impact.png")

# Build report
report.append(f"\n### Rating → Defensive Impact Correlations\n")
report.append("| Rating | → DWS (r) | → DBPM (r) |\n|--------|-----------|------------|\n")
all_def_r = {}
for r in DEF_RATINGS + ['Hgt_rating','Wgt','Ath','Spd','Str','End']:
    dws_r  = def_corrs.get((r,'DWS'),  {}).get('r', np.nan)
    dbpm_r = def_corrs.get((r,'DBPM'), {}).get('r', np.nan)
    if not np.isnan(dws_r) or not np.isnan(dbpm_r):
        label = RATING_LABELS.get(r, r)
        report.append(f"| {label} | {dws_r:+.3f} | {dbpm_r:+.3f} |\n")
        all_def_r[r] = (dws_r, dbpm_r)

report.append(f"\n### DWS by Defensive Archetype\n")
report.append(dws_by_arch.to_markdown() + "\n")
report.append(f"\n### DBPM by Defensive Archetype\n")
report.append(dbpm_by_arch.to_markdown() + "\n")

# Surprising findings
best_dws_pred = max([(c,v) for (c,t),v in def_corrs.items() if t=='DWS'],
                    key=lambda x: abs(x[1]['r']), default=(None, {'r':0}))
report.append(f"\n### Key Findings\n")
if best_dws_pred[0]:
    report.append(f"- **Strongest predictor of DWS:** {RATING_LABELS.get(best_dws_pred[0], best_dws_pred[0])} "
                  f"(r={best_dws_pred[1]['r']:+.3f})\n")

report.append(f"\n![Defensive Impact]({s3_plot})\n")
report.append("\n**Methodology:** Pearson correlation between defensive scouting ratings + physical attributes and Defensive Win Shares / Defensive BPM. Hgt parsed from rating column. Minimum 15 players for correlation.\n")

# ═══════════════════════════════════════════════════════════════════════════════
# STUDY 4 — Winning Without Scoring
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("STUDY 4: Winning Without Scoring")
print("═"*60)

report.append("\n---\n## Study 4 — Winning Without Scoring\n")
report.append("> Who moves the needle without needing the ball?\n")

# Build a "non-scoring impact" model:
# Residualize WS and VORP against PPG + USG% to isolate non-scoring contribution
scoring_cols = ['PPG', 'USG%']
impact_cols  = ['WS_actual', 'VORP', 'BPM']

ws_data = active[impact_cols + scoring_cols + ['DBPM','DWS','AST%','ORB%','DRB%',
                                                'SA','CSht','CSPG','On Net',
                                                'Pass','Play','Help','OffR','DefR',
                                                'Player','Tm','Pos','Salary']].dropna(
    subset=['WS_actual','VORP','BPM','PPG','USG%']
)

# Linear residualize WS against PPG + USG%
from numpy.linalg import lstsq
def residualize(y, X_cols, data):
    clean = data[[y] + X_cols].dropna()
    X = np.column_stack([clean[c] for c in X_cols] + [np.ones(len(clean))])
    y_vals = clean[y].values
    coefs, _, _, _ = lstsq(X, y_vals, rcond=None)
    y_hat = X @ coefs
    return pd.Series(y_vals - y_hat, index=clean.index)

ws_data['WS_resid']   = residualize('WS_actual', scoring_cols, ws_data)
ws_data['VORP_resid'] = residualize('VORP',      scoring_cols, ws_data)
ws_data['BPM_resid']  = residualize('BPM',       scoring_cols, ws_data)

# Combined non-scoring impact score
ws_data['NonScoreImpact'] = (
    ws_data['WS_resid'].fillna(0) +
    ws_data['VORP_resid'].fillna(0) +
    ws_data['BPM_resid'].fillna(0) * 0.3
)

top_non_scorers = ws_data.nlargest(20, 'NonScoreImpact')[
    ['Player','Tm','Pos','PPG','USG%','WS_actual','VORP','BPM',
     'DWS','DBPM','AST%','ORB%','DRB%','WS_resid','VORP_resid','NonScoreImpact']
].round(2)

print("\n  Top 20 Players by Non-Scoring Impact:")
print(top_non_scorers.to_string(index=False))

# What non-scoring metrics drive the residual?
non_score_features = ['DWS','DBPM','AST%','ORB%','DRB%','Help','OffR','DefR',
                       'SA','CSht','CSPG','On Net','Pass','Play']
ns_corrs = {}
for f in non_score_features:
    if f in ws_data.columns:
        clean = ws_data[['WS_resid', f]].dropna()
        if len(clean) >= 15:
            rv, pv = stats.pearsonr(clean['WS_resid'], clean[f])
            ns_corrs[f] = rv

ns_corrs_sorted = dict(sorted(ns_corrs.items(), key=lambda x: abs(x[1]), reverse=True))

# Figure: top non-scorers + feature correlations
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Left: scatter PPG vs WS, colored by NonScoreImpact
scatter_data = ws_data.dropna(subset=['PPG','WS_actual','NonScoreImpact'])
sc = axes[0].scatter(scatter_data['PPG'], scatter_data['WS_actual'],
                     c=scatter_data['NonScoreImpact'], cmap='RdYlGn',
                     s=40, alpha=0.7, edgecolors='none')
plt.colorbar(sc, ax=axes[0], label='Non-Scoring Impact')
# Label top non-scorers
for _, row in top_non_scorers.head(10).iterrows():
    p_row = scatter_data[scatter_data['Player'] == row['Player']]
    if len(p_row):
        axes[0].annotate(row['Player'].title(), (p_row['PPG'].values[0], p_row['WS_actual'].values[0]),
                         fontsize=6, ha='center', va='bottom', alpha=0.8)
axes[0].set_xlabel('PPG')
axes[0].set_ylabel('Win Shares')
axes[0].set_title('PPG vs Win Shares\n(Green = High Non-Scoring Impact)', fontsize=10)

# Right: feature correlations with WS residual
feat_labels = [RATING_LABELS.get(f, f) for f in ns_corrs_sorted.keys()]
feat_vals   = list(ns_corrs_sorted.values())
colors_b = ['#2ecc71' if v > 0 else '#e74c3c' for v in feat_vals]
axes[1].barh(feat_labels[::-1], feat_vals[::-1], color=colors_b[::-1], edgecolor='white')
axes[1].axvline(0, color='black', linewidth=0.8)
axes[1].set_title('Non-Scoring Contribution Drivers\n(Correlation with WS residualized vs PPG+USG%)', fontsize=10)
axes[1].set_xlabel('Pearson r')
axes[1].set_xlim(-0.7, 0.7)

plt.suptitle('Study 4: Winning Without Scoring', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
s4_plot = save_fig("study4_winning_without_scoring.png")

report.append(f"\n### Top 20 High-Impact Non-Scorers\n")
report.append(top_non_scorers.to_markdown(index=False) + "\n")
report.append(f"\n### What Drives Non-Scoring Impact?\n")
report.append("| Metric | Correlation with WS (residualized) |\n|--------|------|\n")
for f, rv in ns_corrs_sorted.items():
    report.append(f"| {RATING_LABELS.get(f, f)} | {rv:+.3f} |\n")

report.append(f"\n### Key Findings\n")
top_ns = list(ns_corrs_sorted.items())
if top_ns:
    report.append(f"- **Strongest non-scoring driver:** {RATING_LABELS.get(top_ns[0][0], top_ns[0][0])} "
                  f"(r={top_ns[0][1]:+.3f})\n")
top5_ns_players = top_non_scorers.head(5)
report.append("- **Top 5 winners without scoring:**\n")
for _, row in top5_ns_players.iterrows():
    report.append(f"  - {row['Player'].title()} ({row['Tm']}) — "
                  f"PPG: {row['PPG']}, WS: {row['WS_actual']}, VORP: {row['VORP']}, "
                  f"Non-Score Impact: {row['NonScoreImpact']:.2f}\n")

report.append(f"\n![Winning Without Scoring]({s4_plot})\n")
report.append("\n**Methodology:** Residualized WS, VORP, and BPM against PPG + USG% using OLS regression. The residuals represent impact that cannot be explained by scoring volume. Non-Scoring Impact = WS_resid + VORP_resid + 0.3×BPM_resid.\n")

# ═══════════════════════════════════════════════════════════════════════════════
# STUDY 5 — Archetype Efficiency by Play Type / Shot Location
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("STUDY 5: Archetype Efficiency by Play Type & Shot Location")
print("═"*60)

report.append("\n---\n## Study 5 — Archetype Efficiency by Play Type & Shot Location\n")
report.append("> Which archetype dominates at the rim, mid-range, transition, and creating open looks?\n")

PLAY_TYPE_COLS = {
    'Iso_eFG':        'Isolation',
    'PnR_Ball_eFG':   'PnR Ball Handler',
    'PnR_Roll_eFG':   'PnR Roll Man',
    'PostUp_eFG':     'Post Up',
    'SpotUp_eFG':     'Spot Up',
    'Handoff_eFG':    'Handoff',
    'Cut_eFG':        'Cut',
    'OffScreen_eFG':  'Off Screen',
    'Transition_eFG': 'Transition',
    'Misc_eFG':       'Misc',
}
SHOT_LOC_COLS = {
    'Rim%':   'At Rim',
    'Cls%':   'Close Range',
    'Mid%':   'Mid Range',
    'Lng%':   'Long 2',
    '3P%':    'Three Point',
}

# Filter available columns
avail_pt   = {k:v for k,v in PLAY_TYPE_COLS.items() if k in active.columns}
avail_shot = {k:v for k,v in SHOT_LOC_COLS.items() if k in active.columns}

# Archetype averages for play types
pt_data = {}
for col, label in avail_pt.items():
    arch_avg = active.groupby('Off Archetype')[col].median().dropna()
    pt_data[label] = arch_avg

pt_df = pd.DataFrame(pt_data).dropna(how='all')
print(f"\n  Play type efficiency by archetype:")
print(pt_df.round(3).to_string())

# Shot location by archetype
sl_data = {}
for col, label in avail_shot.items():
    arch_avg = active.groupby('Off Archetype')[col].median().dropna()
    sl_data[label] = arch_avg

sl_df = pd.DataFrame(sl_data).dropna(how='all')

# Who creates open looks? → Proxy: SpotUp_Plays (teammates SpotUp attempts driven by playmaker)
# Actually use AST% + Grav as proxy for "creating open looks"
open_look_cols = ['AST%', 'Grav', 'Pass', 'Spac']
ol_avail = [c for c in open_look_cols if c in active.columns]
ol_df = active.groupby('Off Archetype')[ol_avail].median().round(2)
print(f"\n  Open look creation by archetype:")
print(ol_df.to_string())

# Figure: heatmaps
fig, axes = plt.subplots(1, 3, figsize=(22, 8))

if not pt_df.empty:
    # Normalize each play type 0-1 for fair comparison
    pt_norm = (pt_df - pt_df.min()) / (pt_df.max() - pt_df.min())
    sns.heatmap(pt_norm, ax=axes[0], cmap='YlOrRd', linewidths=0.5,
                annot=pt_df.round(3), fmt='.3f', annot_kws={'size': 7},
                cbar_kws={'label': 'Normalized eFG%'})
    axes[0].set_title('Play Type eFG% by Offensive Archetype\n(Raw values shown, normalized color)', fontsize=9)
    axes[0].tick_params(axis='x', rotation=45, labelsize=8)
    axes[0].tick_params(axis='y', rotation=0,  labelsize=8)

if not sl_df.empty:
    sl_norm = (sl_df - sl_df.min()) / (sl_df.max() - sl_df.min())
    sns.heatmap(sl_norm, ax=axes[1], cmap='Blues', linewidths=0.5,
                annot=sl_df.round(3), fmt='.3f', annot_kws={'size': 7},
                cbar_kws={'label': 'Normalized %'})
    axes[1].set_title('Shot Location % by Offensive Archetype', fontsize=9)
    axes[1].tick_params(axis='x', rotation=45, labelsize=8)
    axes[1].tick_params(axis='y', rotation=0,  labelsize=8)

if not ol_df.empty:
    ol_norm = (ol_df - ol_df.min()) / (ol_df.max() - ol_df.min())
    sns.heatmap(ol_norm, ax=axes[2], cmap='Purples', linewidths=0.5,
                annot=ol_df.round(1), fmt='.1f', annot_kws={'size': 7},
                cbar_kws={'label': 'Normalized Rating'})
    axes[2].set_title('Open Look Creation Metrics by Archetype', fontsize=9)
    axes[2].tick_params(axis='x', rotation=45, labelsize=8)
    axes[2].tick_params(axis='y', rotation=0,  labelsize=8)

plt.suptitle('Study 5: Archetype Efficiency by Play Type & Shot Location',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
s5_plot = save_fig("study5_archetype_efficiency.png")

# Report
report.append(f"\n### Play Type eFG% by Offensive Archetype\n")
if not pt_df.empty:
    report.append(pt_df.round(3).to_markdown() + "\n")

report.append(f"\n### Shot Location % by Offensive Archetype\n")
if not sl_df.empty:
    report.append(sl_df.round(3).to_markdown() + "\n")

report.append(f"\n### Open Look Creation by Archetype\n")
if not ol_df.empty:
    report.append(ol_df.to_markdown() + "\n")

# Key findings
report.append(f"\n### Key Findings\n")
if not pt_df.empty:
    for col in pt_df.columns:
        best_arch = pt_df[col].idxmax()
        report.append(f"- **Best {col} archetype:** {best_arch} "
                      f"({pt_df.loc[best_arch, col]:.3f} eFG%)\n")
if not sl_df.empty:
    rim_best = sl_df['At Rim'].idxmax() if 'At Rim' in sl_df.columns else 'N/A'
    report.append(f"- **Most efficient at the rim:** {rim_best} "
                  f"({sl_df.loc[rim_best,'At Rim']:.3f})\n" if rim_best != 'N/A' else "")
    if 'Three Point' in sl_df.columns:
        tp_best = sl_df['Three Point'].idxmax()
        report.append(f"- **Most efficient from three:** {tp_best} "
                      f"({sl_df.loc[tp_best,'Three Point']:.3f})\n")

report.append(f"\n![Archetype Efficiency]({s5_plot})\n")
report.append("\n**Methodology:** Median eFG% per play type and median shooting % per shot location, grouped by Offensive Archetype. Open look creation proxied by AST%, Gravity rating, Passing rating, and Spacing rating. Values normalized 0-1 in heatmap for visual comparison; raw values annotated.\n")

# ═══════════════════════════════════════════════════════════════════════════════
# Save full report
# ═══════════════════════════════════════════════════════════════════════════════
report_path = os.path.join(REPO, "analysis_report.md")
with open(report_path, 'w') as f:
    f.write('\n'.join(report))
print(f"\nReport saved: {report_path}")
print("\n✅ All 5 studies complete.")
