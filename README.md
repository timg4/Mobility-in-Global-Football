# Global Player Mobility in Football
### A League-to-League Network Analysis

**Interdisciplinary Project** — WU Wien × TU Wien
**Author:** Tim Greß (12412672)
**Supervisors:** Sebastian Hattinger (WU Wien) · Prof. Emanuel Sallinger (TU Wien)

---

## Overview

This project analyses global player mobility in football as a directed, weighted network. Each node is a league, each edge is the volume of player transfers between two leagues. The network is used to test four structural hypotheses about market concentration, bridge leagues, community structure and lower-tier pathways across 32 seasons (1994/95–2025/26).

Edges are weighted by **transfer counts**, not fees: fees are disclosed for only ~5 % of transfers and are missing in a systematic way that would bias the results against smaller and non-European leagues.

**Data source:** Transfermarkt, provided by the Institute of International Business, WU Vienna (proprietary, not included in this repository)
**Method:** CRISP-DM · igraph · Leiden community detection · degree-preserving null model · Mann-Kendall trend test

| | |
|---|---|
| Analysis window | 1 Jan 1995 – 27 Jan 2026 (32 seasons) |
| League-to-league transfers (strict) | 586,520 |
| Used in the network (after removing pseudo-leagues) | 482,770 |
| Leagues / countries | 691 / 118 |
| Communities detected (Leiden) | 17 |

---

## Research Questions & Hypotheses

| # | Hypothesis | Short description |
|---|-----------|-------------------|
| H1 | Concentration | Incoming transfer flows are highly concentrated among a small number of leagues |
| H2 | Bridge Leagues | Some mid-level leagues act as bridges between regions and/or tier systems |
| H3 | Community Structure | The network exhibits non-random community structure exceeding a degree-preserving null model |
| H4 | Lower-League Pathways | Transfers from lower tiers are predominantly domestic and upward |

---

## Repository Structure

```
├── 01_data_preparation.ipynb   # Data extraction, cleaning, edge list export
├── 02_analysis.ipynb           # Network analysis, hypothesis tests, visualisations
├── results/
│   ├── figures/                # All generated plots (PNG + interactive HTML)
│   └── tables/                 # Exported result tables (CSV)
├── Global_Player_Mobility_in_Football.pdf # Project Report         
└── proposal/                   # Original project proposal
```


---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

---

## Running the Analysis

Run the notebooks **in order** from the project root:

1. **`01_data_preparation.ipynb`** — reads `data/tu_data.db` (private)
   Cleans the raw transfer records, imputes missing competition IDs, fixes the date encoding, sets the analysis window and exports four edge-list CSVs to `data/prepared/`.

2. **`02_analysis.ipynb`** — reads `data/prepared/` and `data/tu_data.db`
   Builds the graphs, runs H1–H4 plus the loan analysis, and writes all figures and tables to `results/`.

---

## Key Results

| Hypothesis | Verdict |
|-----------|---------|
| H1 – Concentration | **Not supported** by the ex-ante thresholds (HHI = 0.0096, Top-5 = 12.4 %), but concentration declines monotonically over the whole window (Mann-Kendall τ = −0.93, p < 0.0001) |
| H2 – Bridge Leagues | **Supported (qualified)** — brokerage peaks among mid-standing leagues (inverted-U, quadratic coef −0.53, peak at 52 % standing, permutation p = 0.004) |
| H3 – Community Structure | **Supported** — Q = 0.2768 vs. null mean 0.0692 (z = 158.6, p < 0.001, 1,000 rewirings); 26/26 seasons above the null mean |
| H4 – Lower-League Pathways | **Supported** — domestic share rises from 56.3 % (tier 1) to 91.9 % (tier 5+); 56.5 % of tier-5+ moves are upward |

Full results: `results/tables/hypothesis_results.csv`

### H2 in two steps

The originally planned KPI (mid-tier share among the top-25 leagues by betweenness) returned a lift of ≈ 0.9×. Inspection showed that betweenness on a count-weighted graph ranks large hubs rather than bridges, and that "mid-level" in the proposal means intermediate **global standing** (Portugal, the Netherlands, Belgium are first divisions but classic stepping stones), not domestic tier 2–4. Following the iterative logic of CRISP-DM the analysis returned to the modelling phase:

- **Standing** = median market value of a league's incoming players. Transfermarkt has a market value for ~86 % of transferred players, so unlike fees it is not systematically missing for smaller leagues. It is used only as a node attribute — the edges stay count-weighted.
- **Bridge score** = √(share of outflow going *up* and across communities × share of inflow coming *from below* and across communities). A pure hub or a pure sink collapses one factor, and domestic pyramid churn is excluded because it stays inside one community.
- Tested on 51 first divisions with ≥ 1,000 cross-league transfers, against a permutation null that shuffles the standing labels.

Both steps are kept in the notebook (section 03b), so the revision is traceable.

### Loans (exploratory)

Loans are flagged explicitly in the data, which allows following each loaned player:

| | |
|---|---|
| Loan episodes | 126,364 |
| Return to the parent club | 95.2 % (domestic 95.0 %, international 96.1 %) |
| Median loan length | 181 days |
| Domestic loans | 79.4 % |
| Direction | 50.1 % to a lower division · 41.3 % same level · 8.6 % upward |
| Later permanent move to the loan club | 15.2 % |

Loans are the mirror image of H4: permanent lower-tier moves go upward, loans go downward and come back.

---

## Outputs

**Figures** (`results/figures/`)

| File | Content |
|---|---|
| `fig_inflow_top20.png` | Top-20 leagues by incoming transfers (H1) |
| `fig_flow_heatmap.png` | League-to-league flow heatmap, top 15 × 15 |
| `fig_h2_betweenness.png` | Top-25 leagues by betweenness centrality (H2, initial step) |
| `fig_h2_bridge_standing.png` | Bridge score vs. global standing, inverted-U (H2, revised) |
| `fig_community_sizes.png` | Community sizes and dominant leagues (H3) |
| `fig_h4_tier_domestic.png` | Domestic vs. international share by source tier (H4) |
| `fig_loan_direction.png` | Loan direction along the league pyramid |
| `fig_loan_exporters.png` | Top loan-exporting leagues |
| `fig_season_trends.png` | Per-season concentration and modularity trends |
| `fig_community_metagraph.html` | Interactive community meta-graph |
| `fig_community_map.html` | Interactive choropleth of dominant community per country |

**Tables** (`results/tables/`)

| File | Content |
|---|---|
| `hypothesis_results.csv` | KPI, robustness and verdict per hypothesis |
| `community_membership.csv` | Leiden communities with labels, sizes and top leagues |
| `h2_bridge_standing.csv` | Bridge score and standing for the 51 leagues in the H2 universe |
| `loan_summary.csv` | Loan return rates, duration, direction |

---

## Data & Acknowledgement

The transfer dataset used in this project originates from Transfermarkt and was provided by the **Institute of International Business, WU Vienna**. It was made available under a Data and Intellectual Property Agreement for external research use. The research project is led by Sebastian Hattinger and supervised by Dr. Jakob Müllner (Institute of International Business, WU Vienna).

- The dataset is **not part of this repository** and is not redistributed — `data/` is git-ignored.
- Only aggregated results are published here (network measures, coefficients, league-level summaries and figures). No raw records and no individual-level data points.
- All intellectual property rights in the data, its structure and any derived results remain with the Institute of International Business, WU Vienna.
- Any further use, distribution or publication of the data or of derived results requires prior written consent from the Institute. Commercial use is not permitted.

---

## Reproducibility

All stochastic steps use `seed = 12412672`. Leiden partitioning, the degree-preserving null model (1,000 rewirings) and the H2 permutation test (500 permutations) reproduce exactly given the same seed and data. Both notebooks use paths relative to the project root.
