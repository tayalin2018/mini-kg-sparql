#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD

EX = Namespace("http://example.org/eng#")

def build_graph():
    g = Graph()
    g.bind("ex", EX)
    g.bind("rdfs", RDFS)

    # Classes
    for cls in ["Part", "Assembly", "Material", "Manufacturer"]:
        g.add((EX[cls], RDF.type, RDFS.Class))

    # Properties
    for prop in ["hasPart", "usesMaterial", "manufacturedBy"]:
        g.add((EX[prop], RDF.type, RDF.Property))
    for prop in ["weightKg", "costUSD", "qty", "country", "grade"]:
        g.add((EX[prop], RDF.type, RDF.Property))

    # Materials
    aluminum = EX.Material_M001
    stainless = EX.Material_M003
    g.add((aluminum, RDF.type, EX.Material))
    g.add((aluminum, RDFS.label, Literal("Aluminum")))
    g.add((aluminum, EX.grade, Literal("6061")))
    g.add((stainless, RDF.type, EX.Material))
    g.add((stainless, RDFS.label, Literal("StainlessSteel")))
    g.add((stainless, EX.grade, Literal("304")))

    # Manufacturers
    acme = EX.Manufacturer_C001
    northforge = EX.Manufacturer_C002
    g.add((acme, RDF.type, EX.Manufacturer))
    g.add((acme, RDFS.label, Literal("Acme Industrial")))
    g.add((acme, EX.country, Literal("DE")))
    g.add((northforge, RDF.type, EX.Manufacturer))
    g.add((northforge, RDFS.label, Literal("NorthForge")))
    g.add((northforge, EX.country, Literal("US")))

    # Parts
    P001 = EX.Part_P001  # Linear Actuator LA100
    g.add((P001, RDF.type, EX.Part))
    g.add((P001, RDFS.label, Literal("Linear Actuator LA100")))
    g.add((P001, EX.weightKg, Literal(2.3, datatype=XSD.decimal)))
    g.add((P001, EX.costUSD, Literal(120.0, datatype=XSD.decimal)))
    g.add((P001, EX.usesMaterial, aluminum))
    g.add((P001, EX.manufacturedBy, acme))

    P003 = EX.Part_P003  # Aluminum Bracket BR25
    g.add((P003, RDF.type, EX.Part))
    g.add((P003, RDFS.label, Literal("Aluminum Bracket BR25")))
    g.add((P003, EX.weightKg, Literal(0.5, datatype=XSD.decimal)))
    g.add((P003, EX.costUSD, Literal(12.5, datatype=XSD.decimal)))
    g.add((P003, EX.usesMaterial, aluminum))
    g.add((P003, EX.manufacturedBy, northforge))

    P004 = EX.Part_P004  # Stainless Bolt M8x20
    g.add((P004, RDF.type, EX.Part))
    g.add((P004, RDFS.label, Literal("Stainless Bolt M8x20")))
    g.add((P004, EX.weightKg, Literal(0.03, datatype=XSD.decimal)))
    g.add((P004, EX.costUSD, Literal(0.5, datatype=XSD.decimal)))
    g.add((P004, EX.usesMaterial, stainless))
    g.add((P004, EX.manufacturedBy, northforge))

    P006 = EX.Part_P006  # O-Ring OR12
    g.add((P006, RDF.type, EX.Part))
    g.add((P006, RDFS.label, Literal("O-Ring OR12")))
    g.add((P006, EX.weightKg, Literal(0.01, datatype=XSD.decimal)))
    g.add((P006, EX.costUSD, Literal(0.2, datatype=XSD.decimal)))
    g.add((P006, EX.usesMaterial, stainless))  # simplified
    g.add((P006, EX.manufacturedBy, northforge))

    # Assembly A100
    A100 = EX.Assembly_A100
    g.add((A100, RDF.type, EX.Assembly))
    g.add((A100, RDFS.label, Literal("Robotic Gripper RG-1")))

    # Composition with quantities
    g.add((A100, EX.hasPart, P001)); g.add((P001, EX.qty, Literal(1, datatype=XSD.integer)))
    g.add((A100, EX.hasPart, P003)); g.add((P003, EX.qty, Literal(2, datatype=XSD.integer)))
    g.add((A100, EX.hasPart, P004)); g.add((P004, EX.qty, Literal(6, datatype=XSD.integer)))
    g.add((A100, EX.hasPart, P006)); g.add((P006, EX.qty, Literal(4, datatype=XSD.integer)))

    return g

def run_queries(g: Graph):
    prefix = """
    PREFIX ex: <http://example.org/eng#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    """

    q1 = prefix + """
    # 1) Parts and their materials
    SELECT ?partLabel ?materialLabel
    WHERE {
      ?p a ex:Part ;
         rdfs:label ?partLabel ;
         ex:usesMaterial ?m .
      ?m rdfs:label ?materialLabel .
    }
    ORDER BY ?partLabel
    """

    q2 = prefix + """
    # 2) Parts + quantities for assembly A100
    SELECT ?assemblyLabel ?partLabel ?qty
    WHERE {
      BIND(ex:Assembly_A100 AS ?a)
      ?a rdfs:label ?assemblyLabel ;
         ex:hasPart ?p .
      ?p rdfs:label ?partLabel ;
         ex:qty ?qty .
    }
    ORDER BY ?partLabel
    """

    q3 = prefix + """
    # 3) Total weight of assembly A100
    SELECT ?assemblyLabel (SUM(xsd:decimal(?w) * xsd:decimal(?q)) AS ?totalWeightKg)
    WHERE {
      BIND(ex:Assembly_A100 AS ?a)
      ?a rdfs:label ?assemblyLabel ;
         ex:hasPart ?p .
      ?p ex:weightKg ?w ;
         ex:qty ?q .
    }
    GROUP BY ?assemblyLabel
    """

    q4 = prefix + """
    # 4) Total cost of assembly A100 (USD)
    SELECT ?assemblyLabel (SUM(xsd:decimal(?c) * xsd:decimal(?q)) AS ?totalCostUSD)
    WHERE {
      BIND(ex:Assembly_A100 AS ?a)
      ?a rdfs:label ?assemblyLabel ;
         ex:hasPart ?p .
      ?p ex:costUSD ?c ;
         ex:qty ?q .
    }
    GROUP BY ?assemblyLabel
    """
    
    q5 = prefix + """
    # 5) Countries of origin for A100 parts
    SELECT ?country (COUNT(?p) AS ?numParts)
    WHERE {
      BIND(ex:Assembly_A100 AS ?a)
      ?a ex:hasPart ?p .
      ?p ex:manufacturedBy ?m .
      ?m <http://example.org/eng#country> ?country .
    }
    GROUP BY ?country
    ORDER BY DESC(?numParts)
    """

    q6 = prefix + """
    # 6) Cheapest part per material
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
    """

    q7 = prefix + """
    # 7) Cost & weight breakdown by material (A100)
    SELECT ?materialLabel
           (SUM(xsd:decimal(?c) * xsd:decimal(?q)) AS ?totalCostUSD)
           (SUM(xsd:decimal(?w) * xsd:decimal(?q)) AS ?totalWeightKg)
    WHERE {
      BIND(ex:Assembly_A100 AS ?a)
      ?a ex:hasPart ?p .
      ?p ex:usesMaterial ?m ;
         ex:costUSD ?c ;
         ex:weightKg ?w ;
         ex:qty ?q .
      ?m rdfs:label ?materialLabel .
    }
    GROUP BY ?materialLabel
    ORDER BY DESC(?totalCostUSD)
    """

    print("\n[Query 1] Parts and their materials")
    for row in g.query(q1):
        print(f"- {row.partLabel} — {row.materialLabel}")

    print("\n[Query 2] Parts + quantities for A100")
    for row in g.query(q2):
        print(f"- {row.partLabel}: qty {row.qty}")

    print("\n[Query 3] Total weight of A100")
    for row in g.query(q3):
        print(f"- {row.assemblyLabel}: {row.totalWeightKg} kg")

    print("\n[Query 4] Total cost of A100 (USD)")
    for row in g.query(q4):
        print(f"- {row.assemblyLabel}: {row.totalCostUSD} USD")

    print("\n[Query 5] Countries of origin for A100 parts")
    for row in g.query(q5):
        print(f"- {row.country}: {row.numParts} parts")

    print("\n[Query 6] Cheapest part per material")
    for row in g.query(q6):
        print(f"- {row.materialLabel}: {row.partLabel} at {row.minCost} USD")

    print("\n[Query 7] A100 cost & weight by material")
    for row in g.query(q7):
        print(f"- {row.materialLabel}: ${row.totalCostUSD} USD, {row.totalWeightKg} kg")

if __name__ == "__main__":
    g = build_graph()
    out = "kg.ttl"
    g.serialize(destination=out, format="turtle")
    print(f"Wrote {out} with {len(g)} triples.")
    run_queries(g)
