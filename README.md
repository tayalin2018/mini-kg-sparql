# Mini Knowledge Graph + SPARQL

This repo builds a tiny engineering knowledge graph (RDF) and answers practical questions with SPARQL.  
It models one assembly (A100 “Robotic Gripper RG-1”) and four parts with materials, manufacturers, cost, weight, and quantities.

---

## What it does

- **Models**: `Part`, `Assembly`, `Material`, `Manufacturer`
- **Relations**: `hasPart`, `usesMaterial`, `manufacturedBy`
- **Attributes**: `weightKg`, `costUSD`, `qty`, `country`, `grade`
- **Output graph**: `kg.ttl` (Turtle), **58 triples** (from the default dataset)
- **Answers** (via SPARQL):
  1. Parts → Materials  
  2. Parts + Quantities for A100  
  3. Total **weight** of A100  
  4. Total **cost** of A100 (USD)  
  5. Countries of origin for A100’s parts  
  6. Cheapest part per material  
  7. Cost & weight breakdown by material (A100)

---

## Results (from the default data)

### Q1 — Parts and their materials
| Part                     | Material       |
|-------------------------|----------------|
| Aluminum Bracket BR25   | Aluminum       |
| Linear Actuator LA100   | Aluminum       |
| O-Ring OR12             | StainlessSteel |
| Stainless Bolt M8x20    | StainlessSteel |

### Q2 — Parts + quantities for A100
| Part                   | Qty |
|------------------------|-----|
| Aluminum Bracket BR25  | 2   |
| Linear Actuator LA100  | 1   |
| O-Ring OR12            | 4   |
| Stainless Bolt M8x20   | 6   |

### Q3 — Total weight of A100
| Assembly               | Total Weight (kg) |
|------------------------|-------------------|
| Robotic Gripper RG-1   | **3.52**          |

### Q4 — Total cost of A100 (USD)
| Assembly               | Total Cost (USD) |
|------------------------|------------------|
| Robotic Gripper RG-1   | **148.8**        |

### Q5 — Countries of origin for A100 parts
| Country | # Parts |
|---------|--------:|
| US      | 3       |
| DE      | 1       |

### Q6 — Cheapest part per material
| Material       | Cheapest Part            | Min Cost (USD) |
|----------------|--------------------------|----------------:|
| Aluminum       | Aluminum Bracket BR25    | 12.5           |
| StainlessSteel | O-Ring OR12              | 0.2            |

### Q7 — A100 cost & weight by material
| Material       | Total Cost (USD) | Total Weight (kg) |
|----------------|------------------:|------------------:|
| Aluminum       | 145.0             | 3.30              |
| StainlessSteel | 3.8               | 0.22              |

> Check: 145.0 + 3.8 = **148.8 USD**, and 3.30 + 0.22 = **3.52 kg** (matches Q3 & Q4).

---

## How it works (at a glance)

- `mini_kg_demo.py` builds the graph with **rdflib**, writes `kg.ttl`, and executes the seven SPARQL queries against the in-memory graph.  
- `export_to_csv.py` (optional) re-runs the same queries and saves their results to `out/*.csv` for sharing or analysis.

---

## Files

- `mini_kg_demo.py` — build graph ➜ run queries ➜ print results ➜ write `kg.ttl`
- `export_to_csv.py` — run all queries ➜ write CSVs to `out/`
- `requirements.txt` — pinned dependency (`rdflib`)
- `kg.ttl` — generated RDF graph (58 triples with default data)
- `out/` — generated CSVs (git-ignored by default)

---

## Run (minimal)

```bash
pip install -r requirements.txt
python mini_kg_demo.py              # prints results, writes kg.ttl
# optional CSVs:
python export_to_csv.py --assembly A100 --ttl kg.ttl --out out
