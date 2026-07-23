# Global Player Mobility in Football
### A League-to-League Network Analysis

**Interdisciplinary Project** — WU Wien × TU Wien  
**Author:** Tim Greß (12412672)  
**Supervisors:** Sebastian Hattinger (WU Wien) · Prof. Emanuel Sallinger (TU Wien)

---

## Overview

This project analyses global player mobility in football as a directed, weighted network. Each node is a football league; each edge represents the volume of player transfers between two leagues. We apply community detection and hypothesis testing to characterise the structure and dynamics of the global transfer market across 31 seasons (1995–2026).

**Data source:** Transfermarkt  
**Method:** CRISP-DM · igraph · Leiden community detection · Mann-Kendall trend test

---

## Research Questions & Hypotheses

| # | Hypothesis | Short description |
|---|-----------|-------------------|
| H1 | Concentration | Incoming transfer flows are highly concentrated among a small number of leagues |
| H2 | Bridge Leagues | Mid-level leagues exhibit disproportionately high betweenness centrality |
| H3 | Community Structure | The network exhibits non-random community structure exceeding a degree-preserving null model |
| H4 | Lower-League Pathways | Transfers from lower-tier leagues are predominantly domestic |

---

## Repository Structure

```
├── 01_data_preparation.ipynb   # Data extraction, cleaning, edge list export
├── 02_analysis.ipynb           # Network analysis, hypothesis tests, visualisations
├── data/
│   ├── competition_mapping.csv # League metadata (name, country, tier)
│   └── prepared/               # Cleaned edge lists (input to 02_analysis)
│       ├── edge_all_strict.csv
│       ├── edge_all_with_unknown.csv
│       ├── edge_season_strict.csv
│       └── edge_season_with_unknown.csv
├── results/
│   ├── figures/                # All generated plots (PNG + interactive HTML)
│   └── tables/                 # Exported result tables (CSV)
└── proposal/                   # Original project proposal
```


---

## Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd Interdis

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the Analysis

Run the notebooks **in order** from the project root:

1. **`01_data_preparation.ipynb`** — dataset is private  
   Cleans raw transfer records, maps competitions, and exports four edge-list CSVs to `data/prepared/`.

2. **`02_analysis.ipynb`** — reads from `data/prepared/`  
   Builds the transfer network, runs hypothesis tests H1–H4, generates all figures and exports result tables to `results/`.

---

## Key Results

| Hypothesis | Verdict |
|-----------|---------|
| H1 – Concentration | Moderate concentration; top-5 leagues receive ~35 % of all cross-league inflows (HHI ≈ 0.05) |
| H2 – Bridge Leagues | Not strongly supported; mid-tier lift ≈ 1.04× (near baseline) |
| H3 – Community Structure | Supported (p < 0.05); observed modularity Q significantly exceeds null model |
| H4 – Lower-League Pathways | Supported; lower-tier leagues show substantially higher domestic transfer share |

Full results with robustness checks: `results/tables/hypothesis_results.csv`

---

## Reproducibility

All stochastic steps use `seed=12412672`. The Leiden community detection and null model permutations are fully reproducible given the same seed and data.
