# Mini Knowledge Graph + SPARQL (Ultra-simple)

**Goal:** In one script, build a tiny engineering knowledge graph and run 3 SPARQL queries.
Good for a first KG portfolio piece.

## What this does
- Creates classes: `Part`, `Assembly`, `Material`, `Manufacturer`.
- Adds one assembly (A100 Robotic Gripper) and four parts.
- Writes the graph to `kg.ttl` (Turtle format).
- Runs **3 queries**:
  1) Parts and their materials
  2) Parts + quantities for assembly A100
  3) Total weight of assembly A100

## Step-by-step
1. Create and activate a virtual environment (optional but recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Windows: .venv\Scripts\activate
   ```

2. Install dependency
   ```bash
   pip install -r requirements.txt
   ```

3. Run the demo
   ```bash
   python mini_kg_demo.py
   ```

4. Inspect the KG
   - Open `kg.ttl` in a text editor to see the triples.
   - (Optional) Load `kg.ttl` into Apache Jena Fuseki or any RDF tool.

## Files
- `mini_kg_demo.py` — builds the graph and runs the SPARQL.
- `requirements.txt` — Python dependency.
- `kg.ttl` — created on first run.

## Next steps (when you're ready)
- Add more parts/assemblies.
- Add properties like `powerRating`, `serialNumber`, `supplierLeadTime`.
- Add queries that answer realistic questions (cost rollups, country-of-origin, etc.).
