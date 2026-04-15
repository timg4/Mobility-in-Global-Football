# Neo4j Import Guide

## 1) Export graph tables from SQLite

Run from project root:

```powershell
python scripts/neo4j_export.py --db data/tu_data.db --mapping data/competition_mapping.csv --outdir data/neo4j_export
```

This writes:

- `data/neo4j_export/leagues.csv`
- `data/neo4j_export/seasons.csv`
- `data/neo4j_export/transfer_flows.csv`

## 2) Move files into Neo4j import directory

Copy the three CSV files into your Neo4j `import/` folder.
Example names assumed below:

- `file:///leagues.csv`
- `file:///seasons.csv`
- `file:///transfer_flows.csv`

## 3) Create constraints and import

Run in Neo4j Browser:

```cypher
CREATE CONSTRAINT league_id_unique IF NOT EXISTS
FOR (l:League) REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT season_id_unique IF NOT EXISTS
FOR (s:Season) REQUIRE s.id IS UNIQUE;
```

```cypher
LOAD CSV WITH HEADERS FROM 'file:///leagues.csv' AS row
MERGE (l:League {id: row.league_id})
SET l.name = row.league_name,
    l.country_id = CASE WHEN row.country_id = '' THEN NULL ELSE toInteger(row.country_id) END,
    l.tier = row.tier,
    l.prior_names = row.prior_league_names;
```

```cypher
LOAD CSV WITH HEADERS FROM 'file:///seasons.csv' AS row
MERGE (s:Season {id: row.season});
```

```cypher
LOAD CSV WITH HEADERS FROM 'file:///transfer_flows.csv' AS row
MATCH (src:League {id: row.source_league_id})
MATCH (dst:League {id: row.dest_league_id})
MATCH (s:Season {id: row.season})
MERGE (src)-[r:FLOW_TO {season: row.season}]->(dst)
SET r.edge_id = row.edge_id,
    r.n_transfers = toInteger(row.n_transfers),
    r.n_loans = toInteger(row.n_loans),
    r.fee_sum = CASE WHEN row.fee_sum = '' THEN NULL ELSE toFloat(row.fee_sum) END,
    r.fee_median = CASE WHEN row.fee_median = '' THEN NULL ELSE toFloat(row.fee_median) END,
    r.domestic_share = CASE WHEN row.domestic_share = '' THEN NULL ELSE toFloat(row.domestic_share) END,
    r.international_share = CASE WHEN row.international_share = '' THEN NULL ELSE toFloat(row.international_share) END,
    r.source_tier = row.source_tier,
    r.dest_tier = row.dest_tier
MERGE (src)-[:ACTIVE_IN]->(s)
MERGE (dst)-[:ACTIVE_IN]->(s);
```

## 4) Quick checks

```cypher
MATCH (l:League) RETURN count(l) AS leagues;
```

```cypher
MATCH (:League)-[r:FLOW_TO]->(:League) RETURN count(r) AS flow_edges;
```

```cypher
MATCH (a:League)-[r:FLOW_TO]->(b:League)
RETURN a.name AS source, b.name AS target, r.n_transfers AS transfers
ORDER BY r.n_transfers DESC
LIMIT 25;
```

## 5) Useful exploration query (community-like regions proxy)

Top dense pairings in one season:

```cypher
MATCH (a:League)-[r:FLOW_TO {season: '2022/2023'}]->(b:League)
RETURN a.name AS source, b.name AS target, r.n_transfers AS transfers
ORDER BY transfers DESC
LIMIT 100;
```

