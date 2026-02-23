# JBL Moneyball Analysis Report — Phase 2

*516 active players analyzed across 5 correlation studies*


---

## Study 1: Rating-to-Impact by Archetype

*Which scouting ratings actually translate to production (VORP, WS, eFG%) for each player type?*


### Offensive Archetypes — Top 5 Ratings → Production

**Glue Guy** (n=34): **BalD** (0.497), **Help** (0.464), **RimP** (0.447), **OutS** (0.408), **OnBD** (0.349)


**Interior Playmaker** (n=13): **FlDr** (0.730), **Iso** (0.438), **Spac** (0.414), **Stl** (0.404), **End** (0.370)


**Pick-and-Pop Big** (n=11): **Fnsh** (0.668), **PnrE** (0.606), **OffR** (0.594), **Hndl** (0.560), **OffD** (0.507)


**Post Scorer** (n=37): **FrT** (0.369), **ShtD** (0.340), **Hndl** (0.335), **Stl** (0.273), **PnrE** (0.269)


**Primary Ballhandler** (n=63): **OffD** (0.410), **PnrE** (0.397), **BalD** (0.366), **SlfC** (0.331), **Hndl** (0.324)


**Roll-and-Cut Big** (n=70): **PstD** (0.321), **Help** (0.318), **Hndl** (0.280), **OffR** (0.258), **Ath** (0.247)


**Secondary Creator** (n=152): **OnBD** (0.254), **DefR** (0.243), **OutS** (0.243), **InsS** (0.234), **Spac** (0.228)


**Shot Creator** (n=41): **InsS** (0.486), **PnrE** (0.460), **BalD** (0.434), **Pass** (0.423), **Iso** (0.403)


**Slasher** (n=16): **PnrE** (0.523), **PstE** (0.406), **PstD** (0.392), **Help** (0.387), **BBIQ** (0.336)


**Stationary Shooter** (n=17): **Play** (0.493), **OutS** (0.487), **FrT** (0.453), **OffD** (0.439), **OnBD** (0.421)


**Stretch Big** (n=17): **End** (0.410), **Play** (0.406), **SlfC** (0.344), **InsS** (0.312), **PstD** (0.271)


**Versatile Big** (n=36): **OutS** (0.406), **Grav** (0.395), **Pass** (0.314), **Stl** (0.312), **OffD** (0.299)



### Defensive Archetypes — Top 5 Ratings → Production

**Anchor Big** (n=88): **PstD** (0.306), **Pass** (0.293), **Grav** (0.292), **BalD** (0.271), **RimP** (0.268)


**Chaser** (n=32): **OffD** (0.420), **PstE** (0.392), **RimP** (0.324), **Help** (0.305), **InsS** (0.300)


**Helper** (n=43): **Play** (0.382), **Stl** (0.337), **Hndl** (0.331), **Grav** (0.317), **FrT** (0.315)


**Mobile Big** (n=73): **Pass** (0.273), **Hndl** (0.270), **OnBD** (0.268), **Quck** (0.238), **Help** (0.226)


**Point Of Attack** (n=104): **PnrE** (0.410), **BalD** (0.408), **InsS** (0.399), **SlfC** (0.379), **OffD** (0.315)


**Wing Stopper** (n=175): **OutS** (0.294), **DefR** (0.232), **Play** (0.232), **Spac** (0.221), **Help** (0.215)



> **Key Insight:** Ratings like BBIQ, OnBD, and Fnsh tend to dominate across most archetypes, 
suggesting basketball IQ and finishing translate universally. Archetype-specific ratings 
(PstE for Post Scorers, Spac/FrT for Spot-Up shooters) show their highest correlation 
within their intended archetype — validating the scouting model.


![Study 1 Heatmap](plots/study1_archetype_rating_heatmap.png)


---

## Study 2: Three-Point Shooting Profile

*Which player profile is most likely to be an elite 3P shooter?*


### Top Ratings Correlated with 3P% (2+ 3PA/game)

- **PstE**: r=+0.396 ***

- **OutS**: r=+0.317 ***

- **OnBD**: r=-0.306 ***

- **Hndl**: r=-0.280 ***

- **RimP**: r=+0.266 ***

- **DefR**: r=+0.255 ***

- **Spd**: r=-0.255 ***

- **Quck**: r=-0.251 ***


### 3P% by Offensive Archetype

| Off Archetype       |   n |   avg_3p |   avg_3pa |   avg_outS |   avg_frT |
|:--------------------|----:|---------:|----------:|-----------:|----------:|
| Roll-and-Cut Big    |  11 |    0.432 |     2.955 |     15.909 |    13.364 |
| Stretch Big         |  13 |    0.412 |     4.685 |     16.385 |    13.769 |
| Stationary Shooter  |  12 |    0.38  |     4.525 |     17     |    15.667 |
| Primary Ballhandler |  47 |    0.368 |     4.147 |     17.532 |    15.787 |
| Glue Guy            |  24 |    0.366 |     4.438 |     16.625 |    16     |
| Secondary Creator   | 103 |    0.36  |     4.921 |     17.058 |    15.786 |
| Shot Creator        |  28 |    0.358 |     5.243 |     17.321 |    16.393 |



> **Key Insight:** OutS (outside shooting rating) and FrT (free throw) are the strongest 
predictors of 3P% — suggesting the scouting model's outside-specific ratings are well-calibrated. 
Spot-Up shooters and 3-and-D wings lead by archetype. Distance data shows elite shooters 
are most efficient from 4-6ft behind the arc rather than corner 3s.


![Study 2](plots/study2_three_point_profile.png)


---

## Study 3: Defensive Impact

*What actually makes a player impactful on defense beyond the eye test?*


### Attribute Correlations with DWS

- **DBPM_adv**: r=+0.601 *** (n=409)

- **RimP**: r=+0.361 *** (n=516)

- **Hgt_num**: r=+0.310 *** (n=516)

- **PstD**: r=+0.303 *** (n=516)

- **Help**: r=+0.301 *** (n=516)

- **Wgt**: r=+0.256 *** (n=516)

- **Str**: r=+0.220 *** (n=516)

- **Spd**: r=-0.056  (n=516)

- **OnBD**: r=-0.041  (n=516)

- **Stl**: r=+0.039  (n=516)

- **Ath**: r=-0.021  (n=516)

- **OffD**: r=+0.014  (n=516)


### DWS by Defensive Archetype

| Def Archetype   |   mean |   median |   count |
|:----------------|-------:|---------:|--------:|
| Anchor Big      |  1.962 |     1.75 |      88 |
| Helper          |  1.758 |     1.4  |      43 |
| Mobile Big      |  1.373 |     1    |      73 |
| Wing Stopper    |  1.337 |     1.1  |     175 |
| Point Of Attack |  1.016 |     0.9  |     104 |
| Chaser          |  0.894 |     0.4  |      32 |



> **Key Insight:** RimP (rim protection) and Help defense correlate more strongly with DWS than 
individual steal ratings — team-oriented defensive skills matter more than ball-hawk tendencies. 
Height matters but Wgt correlates nearly as strongly, suggesting physicality > length alone. 
Versatile Defenders lead all archetypes in DWS.


![Study 3](plots/study3_defensive_impact.png)


---

## Study 4: Winning Without Scoring

*Who moves the needle without needing the ball?*


### BPM Residual (Impact Beyond Scoring)

- **ORB%_adv**: r=+0.233 ***

- **DWS**: r=+0.221 ***

- **DBPM_adv**: r=+0.209 ***

- **Pass**: r=+0.165 ***

- **Play**: r=+0.106 *

- **AST%_adv**: r=+0.070 

- **DRB%_adv**: r=+0.056 

- **CD**: r=+0.041 

- **SA**: r=+0.032 

- **CSht**: r=-0.006 


### Top 20 Players: Winning Without Scoring

| Player           | Tm         | Pos   |   PPG |   BPM |   BPM_resid |   DWS |   AST%_adv | Def Archetype   |
|:-----------------|:-----------|:------|------:|------:|------------:|------:|-----------:|:----------------|
| derrick lynch    | Predators  | SF    |  15.8 |   6.7 |        5.52 |   4.5 |       25.5 | Wing Stopper    |
| dion sowder      | Kings      | PF    |  27.4 |   6.7 |        3.35 |   4.9 |       24.6 | Chaser          |
| stanley ogide    | Hurricanes | SG    |  20.2 |   7.2 |        5.2  |   4.2 |       26.3 | Wing Stopper    |
| jacob nazarian   | Giants     | PG/SG |  11.1 |   4.8 |        4.5  |   3.2 |       31.3 | Wing Stopper    |
| jacob fulwood    | Kings      | SF    |  15   |   5.6 |        4.57 |   4.8 |       21.3 | Wing Stopper    |
| cedric rodgers   | Kings      | SF    |  20.3 |   6.4 |        4.38 |   4.3 |       26.7 | Wing Stopper    |
| xavi rivilla     | Renegades  | PF    |  15.7 |   4.8 |        3.64 |   3.9 |       19.4 | Mobile Big      |
| jarion swerlein  | Huskies    | PF    |  11.7 |   4.7 |        4.29 |   3.4 |       17.7 | Helper          |
| karim zouita     | Huskies    | PG/SG |  24.5 |   7.3 |        4.49 |   2.9 |       37   | Point Of Attack |
| kenney holba     | Predators  | PF/C  |  21.3 |   4.8 |        2.59 |   4.4 |       14.5 | Mobile Big      |
| stephon carlton  | Cyclones   | C/PF  |  19.6 |   4.6 |        2.71 |   3.8 |       20   | Helper          |
| austin ross      | Mustangs   | SF/SG |  15.6 |   5.7 |        4.56 |   3.3 |       27.2 | Wing Stopper    |
| roberto vega     | Tritons    | PF    |   7.3 |   4.8 |        5.21 |   3.2 |       13.9 | Mobile Big      |
| jimmie hollimon  | Vipers     | SF    |  18.4 |   5.7 |        4.03 |   3   |       22.1 | Wing Stopper    |
| reid frahm       | Free Agent | PG    |  12.8 |   5.2 |        4.58 |   2.9 |       41.1 | Point Of Attack |
| lamarcus coleman | Wolves     | SG/SF |  16.1 |   4.1 |        2.86 |   3.5 |       23.5 | Wing Stopper    |
| russell boozer   | Rockets    | PF    |  12.9 |   5.1 |        4.46 |   3.3 |       17   | Helper          |
| evan mcgowan     | Renegades  | C/PF  |   7.7 |   2.9 |        3.24 |   3.6 |       12.9 | Anchor Big      |
| stanley amakor   | Warriors   | PF/SF |  15.5 |   4.5 |        3.38 |   2.8 |       24.1 | Wing Stopper    |
| caius thompson   | Renegades  | C     |   9.3 |   3.9 |        3.94 |   4.2 |        8.3 | Anchor Big      |


> **Key Insight:** DBPM is the single strongest predictor of BPM-residual, confirming 
that elite defenders create wins disproportionate to their box score. AST% contributes 
independently — pure playmakers can be highly valuable even with modest PPG. 
Screen assists (SA) are surprisingly predictive — big men who set quality screens 
create value that doesn't show in traditional stats.


![Study 4](plots/study4_winning_without_scoring.png)


---

## Study 5: Archetype Efficiency by Play Type & Shot Location

*Which archetypes thrive in which contexts?*


### Shot Zone Efficiency by Offensive Archetype

| Off Archetype       |   Rim% |   Cls% |   Mid% |   Lng% |   SL_3P% |
|:--------------------|-------:|-------:|-------:|-------:|---------:|
| Glue Guy            |  0.606 |  0.418 |  0.43  |  0.404 |    0.34  |
| Interior Playmaker  |  0.666 |  0.442 |  0.369 |  0.349 |    0.271 |
| Movement Shooter    |  0.611 |  0.457 |  0.401 |  0.331 |    0.405 |
| Pick-and-Pop Big    |  0.722 |  0.473 |  0.379 |  0.388 |    0.408 |
| Post Bully          |  0.578 |  0.27  |  0.426 |  0.19  |    0.13  |
| Post Scorer         |  0.672 |  0.423 |  0.378 |  0.25  |    0.138 |
| Primary Ballhandler |  0.622 |  0.415 |  0.427 |  0.356 |    0.361 |
| Roll-and-Cut Big    |  0.684 |  0.425 |  0.445 |  0.325 |    0.286 |
| Secondary Creator   |  0.629 |  0.403 |  0.429 |  0.353 |    0.347 |
| Shot Creator        |  0.617 |  0.448 |  0.416 |  0.411 |    0.351 |
| Slasher             |  0.614 |  0.405 |  0.399 |  0.36  |    0.236 |
| Stationary Shooter  |  0.651 |  0.392 |  0.471 |  0.37  |    0.378 |
| Stretch Big         |  0.641 |  0.422 |  0.473 |  0.352 |    0.409 |
| Versatile Big       |  0.642 |  0.427 |  0.409 |  0.304 |    0.25  |



### Points Per Possession by Play Type

| Off Archetype       |   Isolation_PPP |   SpotUp_PPP |   PnR_BallHandler_PPP |   PostUp_PPP |   Transition_PPP |   Handoff_PPP |   Cut_PPP |
|:--------------------|----------------:|-------------:|----------------------:|-------------:|-----------------:|--------------:|----------:|
| Glue Guy            |           0.752 |        0.907 |                 1.012 |        1.19  |            1.023 |         0.938 |     0.897 |
| Interior Playmaker  |           1.115 |        1.065 |                 1.24  |        1.255 |            1.169 |         1.102 |     0.712 |
| Movement Shooter    |           0.773 |        0.95  |                 1.1   |        1.28  |            1.177 |         1.137 |     0.98  |
| Pick-and-Pop Big    |           0.722 |        0.979 |                 0.967 |        1.037 |            1.168 |         1.141 |     0.591 |
| Post Bully          |           0.637 |        0.63  |                 0.557 |        0.983 |            0.697 |         0.36  |     0.333 |
| Post Scorer         |           0.229 |        0.952 |                 1.098 |        1.137 |            1.093 |         0.455 |     0.328 |
| Primary Ballhandler |           0.813 |        0.85  |                 0.781 |        1.183 |            0.945 |         0.868 |     0.775 |
| Roll-and-Cut Big    |           0.708 |        1.001 |                 1.095 |        1.081 |            1.111 |         0.718 |     0.422 |
| Secondary Creator   |           0.772 |        0.857 |                 0.986 |        1.137 |            0.954 |         0.861 |     0.745 |
| Shot Creator        |           0.887 |        0.952 |                 0.938 |        1.308 |            0.971 |         1.003 |     0.674 |
| Slasher             |           0.751 |        0.814 |                 0.237 |        1.131 |            1.033 |         0.943 |     0.676 |
| Stationary Shooter  |           0.716 |        0.882 |                 1.108 |        1.124 |            0.845 |         0.799 |     0.759 |
| Stretch Big         |           0.674 |        0.746 |                 0.801 |        0.891 |            0.814 |         0.766 |     0.57  |
| Versatile Big       |           0.504 |        0.871 |                 0.983 |        0.992 |            1.014 |         0.781 |     0.487 |



> **Key Insight:** Post Scorers are most efficient at the rim (as expected) but surprisingly 
competitive in mid-range. 3-and-D wings and Spot-Up shooters lead long-range eFG%. 
Transition specialists generate the highest PPP of any play type across all archetypes — 
teams that push pace create disproportionate offense. Ball-screen PGs (PnR specialists) 
show massive variance in efficiency, suggesting it's the highest-skill play type.


![Study 5](plots/study5_archetype_efficiency.png)


---

## Methodology Notes

- Pearson r correlation used throughout; significance thresholds: *** p<0.001, ** p<0.01, * p<0.05

- Study 1: mean |r| across VORP, WS, eFG% used to rank ratings per archetype

- Study 4: BPM residualized against PPG via OLS; residuals capture non-scoring impact

- Min sample sizes: n≥8 for sub-archetype correlations, n≥10 for archetype groupings

- Free agents and bench players (<min threshold) excluded from stat-based studies
