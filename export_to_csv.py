#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Export SPARQL query results to CSV files.
Usage:
  python export_to_csv.py --assembly A100 --ttl kg.ttl --out out
"""
import argparse, csv, pathlib
from rdflib import Graph

EX_NS = "http://example.org/eng#"

def q_prefix():
    return """
    PREFIX ex: <http://example.org/eng#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    """

def make_queries(assembly_id: str):
    a_bind = f"BIND(ex:Assembly_{assembly_id} AS ?a)"
    return [
        ("q1_parts_materials",
         "Parts and their materials",
         q_prefix() + """
         SELECT ?partLabel ?materialLabel
         WHERE {
           ?p a ex:Part ;
              rdfs:label ?partLabel ;
              ex:usesMaterial ?m .
           ?m rdfs:label ?materialLabel .
         }
         ORDER BY ?partLabel
         """),
        ("q2_parts_qty",
         f"Parts + quantities for assembly {assembly_id}",
         q_prefix() + f"""
         SELECT ?assemblyLabel ?partLabel ?qty
         WHERE {{
           {a_bind}
           ?a rdfs:label ?assemblyLabel ;
              ex:hasPart ?p .
           ?p rdfs:label ?partLabel ;
              ex:qty ?qty .
         }}
         ORDER BY ?partLabel
         """),
        ("q3_total_weight",
         f"Total weight of assembly {assembly_id}",
         q_prefix() + f"""
         SELECT ?assemblyLabel (SUM(xsd:decimal(?w) * xsd:decimal(?q)) AS ?totalWeightKg)
         WHERE {{
           {a_bind}
           ?a rdfs:label ?assemblyLabel ;
              ex:hasPart ?p .
           ?p ex:weightKg ?w ;
              ex:qty ?q .
         }}
         GROUP BY ?assemblyLabel
         """),
        ("q4_total_cost",
         f"Total cost (USD) of assembly {assembly_id}",
         q_prefix() + f"""
         SELECT ?assemblyLabel (SUM(xsd:decimal(?c) * xsd:decimal(?q)) AS ?totalCostUSD)
         WHERE {{
           {a_bind}
           ?a rdfs:label ?assemblyLabel ;
              ex:hasPart ?p .
           ?p ex:costUSD ?c ;
              ex:qty ?q .
         }}
         GROUP BY ?assemblyLabel
         """),
        ("q5_country_of_origin",
         f"Countries of origin for parts in assembly {assembly_id}",
         q_prefix() + f"""
         SELECT ?country (COUNT(?p) AS ?numParts)
         WHERE {{
           {a_bind}
           ?a ex:hasPart ?p .
           ?p ex:manufacturedBy ?m .
           ?m <{EX_NS}country> ?country .
         }}
         GROUP BY ?country
         ORDER BY DESC(?numParts)
         """),
        ("q6_cheapest_by_material",
         "Cheapest part per material",
         q_prefix() + """
         SELECT ?materialLabel ?partLabel ?minCost
         WHERE {
           {
             SELECT ?m (MIN(?cost) AS ?minCost)
             WHERE {
               ?p a ex:Part ; ex:usesMaterial ?m ; ex:costUSD ?cost .
             }
             GROUP BY ?m
           }
           ?m rdfs:label ?materialLabel .
           ?p a ex:Part ;
              ex:usesMaterial ?m ;
              ex:costUSD ?cost ;
              rdfs:label ?partLabel .
           FILTER(?cost = ?minCost)
         }
         ORDER BY ?materialLabel ?partLabel
         """),
        ("q7_cost_weight_by_material",
         f"Cost & weight breakdown by material for assembly {assembly_id}",
         q_prefix() + f"""
         SELECT ?materialLabel
                (SUM(xsd:decimal(?c) * xsd:decimal(?q)) AS ?totalCostUSD)
                (SUM(xsd:decimal(?w) * xsd:decimal(?q)) AS ?totalWeightKg)
         WHERE {{
           {a_bind}
           ?a ex:hasPart ?p .
           ?p ex:usesMaterial ?m ;
              ex:costUSD ?c ;
              ex:weightKg ?w ;
              ex:qty ?q .
           ?m rdfs:label ?materialLabel .
         }}
         GROUP BY ?materialLabel
         ORDER BY DESC(?totalCostUSD)
         """),
    ]

def write_csv(path: pathlib.Path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        import csv
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow([("" if v is None else str(v)) for v in r])

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--assembly", default="A100", help="Assembly ID (e.g., A100)")
    ap.add_argument("--ttl", default="kg.ttl", help="Path to Turtle KG file")
    ap.add_argument("--out", default="out", help="Output directory for CSVs")
    args = ap.parse_args()

    g = Graph()
    g.parse(args.ttl, format="turtle")

    outdir = pathlib.Path(args.out)
    for slug, desc, q in make_queries(args.assembly):
        res = g.query(q)
        headers = [str(v) for v in res.vars]
        rows = list(res)
        out_path = outdir / f"{slug}.csv"
        write_csv(out_path, headers, rows)
        print(f"Wrote {out_path}  ({desc})")

if __name__ == "__main__":
    main()
