#!/usr/bin/env python3
"""Validate the al: catalog and project it to JSON for the browser engine.

The TriG catalog is the source of truth. This script:
  1. loads the al: ontology, controlled vocabularies, and scales from the
     ontology repository;
  2. validates the catalog against shapes/al-core.shacl.ttl and stops on any
     violation;
  3. projects the catalog to content/al/catalog.json, a bounded, sorted,
     deterministic structure the adaptive-learning engine consumes.

Usage:
  python scripts/build_catalog.py [--ontology ../adaptive-learning-ontology]
"""

from __future__ import annotations

import argparse
import os
import hashlib
import json
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Dataset, Graph

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog/informatics-unit-03.trig"
OUTPUT = ROOT / "content/al/catalog.json"

PREFIXES = """
PREFIX al:      <https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema:  <https://schema.org/>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
"""


def vocabulary(ontology: Path) -> Graph:
    g = Graph()
    for path in [ontology / "ontology/al-core.ttl", ontology / "vocab/al-schemes.ttl", *sorted((ontology / "vocab/scales").glob("*.ttl"))]:
        g.parse(path)
    return g


def rows(graph: Graph, query: str) -> list[dict[str, str]]:
    result = graph.query(PREFIXES + query)
    return [{str(v): (None if r[v] is None else str(r[v])) for v in result.vars} for r in result]


def project(graph: Graph, source_digest: str) -> dict:
    framework = rows(graph, "SELECT ?iri ?title ?scale WHERE { ?iri a al:CapabilityFramework ; dcterms:title ?title ; al:usesScale ?scale }")[0]
    levels = rows(graph, f"""SELECT ?iri ?notation ?label ?ordinal WHERE {{
        ?iri skos:inScheme <{framework['scale']}> ; skos:notation ?notation ; skos:prefLabel ?label ; al:ordinal ?ordinal }}""")
    capabilities = rows(graph, """SELECT ?iri ?notation ?label ?ordinal WHERE {
        ?iri a al:Capability ; skos:notation ?notation ; skos:prefLabel ?label ; al:ordinal ?ordinal }""")
    prerequisites = rows(graph, "SELECT ?capability ?prerequisite WHERE { ?capability al:prerequisite ?prerequisite }")
    audiences = rows(graph, "SELECT ?iri ?label WHERE { ?iri a al:Audience ; rdfs:label ?label }")
    targets = rows(graph, """SELECT ?iri ?audience ?capability ?level ?critical WHERE {
        ?iri a al:CapabilityTarget ; al:forAudience ?audience ; al:targetCapability ?capability ; al:targetLevel ?level .
        OPTIONAL { ?iri al:isCritical ?critical } }""")
    activities = rows(graph, """SELECT ?iri ?title ?ordinal ?kind ?url WHERE {
        ?iri a al:LearningActivity ; dcterms:title ?title ; al:ordinal ?ordinal ; al:activityKind ?kind .
        OPTIONAL { ?iri schema:url ?url } }""")
    assesses = rows(graph, "SELECT ?activity ?capability WHERE { ?activity a al:LearningActivity ; al:assessesCapability ?capability }")
    notebooks = rows(graph, """SELECT ?activity ?language ?path WHERE {
        ?activity al:usesAsset ?asset . ?asset schema:programmingLanguage ?language ; schema:contentUrl ?path }""")
    rules = rows(graph, """SELECT ?iri ?activity ?criterion ?capability ?stage ?action ?outcome ?maxGuidance WHERE {
        ?activity al:hasEvidenceRule ?iri .
        ?iri al:supportsCriterion ?criterion ; al:evidenceStage ?stage ; al:requiredAction ?action ;
             al:acceptedOutcome ?outcome ; al:maximumGuidance ?maxGuidance .
        ?criterion al:criterionCapability ?capability }""")
    policy = rows(graph, "SELECT ?iri ?version WHERE { ?iri a al:EstimatorPolicy ; al:policyVersion ?version }")[0]
    ceilings = rows(graph, f"""SELECT ?stage ?level WHERE {{
        <{policy['iri']}> al:hasStageCeiling ?c . ?c al:ceilingStage ?stage ; al:ceilingLevel ?level }}""")

    def group(items, key, value):
        out: dict[str, list[str]] = {}
        for item in items:
            out.setdefault(item[key], []).append(item[value])
        return {k: sorted(v) for k, v in out.items()}

    prereq_by_cap = group(prerequisites, "capability", "prerequisite")
    cap_by_activity = group(assesses, "activity", "capability")
    target_audiences = group(targets, "iri", "audience")
    outcomes_by_rule = group(rules, "iri", "outcome")
    rules_by_activity = group(rules, "activity", "iri")

    unique_targets = {t["iri"]: t for t in targets}
    unique_rules = {r["iri"]: r for r in rules}

    return {
        "schema": "al-catalog-projection/0.1",
        "sourceDigest": source_digest,
        "framework": {"iri": framework["iri"], "title": framework["title"], "scale": framework["scale"]},
        "levels": sorted(({"iri": l["iri"], "notation": l["notation"], "label": l["label"], "ordinal": int(l["ordinal"])} for l in levels),
                         key=lambda l: l["ordinal"]),
        "capabilities": sorted(({"iri": c["iri"], "notation": c["notation"], "label": c["label"], "ordinal": int(c["ordinal"]),
                                 "prerequisites": prereq_by_cap.get(c["iri"], [])} for c in capabilities), key=lambda c: c["ordinal"]),
        "audiences": sorted(audiences, key=lambda a: a["iri"]),
        "targets": sorted(({"iri": t["iri"], "audiences": target_audiences[t["iri"]], "capability": t["capability"],
                            "level": t["level"], "critical": t["critical"] == "true"} for t in unique_targets.values()),
                          key=lambda t: t["iri"]),
        "activities": sorted(({"iri": a["iri"], "title": a["title"], "ordinal": int(a["ordinal"]), "kind": a["kind"],
                               "capabilities": cap_by_activity.get(a["iri"], []),
                               "notebooks": {n["language"]: n["path"] for n in notebooks if n["activity"] == a["iri"]},
                               "rules": rules_by_activity.get(a["iri"], []),
                               **({"url": a["url"]} if a["url"] else {})} for a in activities), key=lambda a: a["ordinal"]),
        "rules": sorted(({"iri": r["iri"], "activity": r["activity"], "criterion": r["criterion"], "capability": r["capability"],
                          "stage": r["stage"], "requiredAction": r["action"], "acceptedOutcomes": outcomes_by_rule[r["iri"]],
                          "maximumGuidance": int(r["maxGuidance"])} for r in unique_rules.values()), key=lambda r: r["iri"]),
        "policy": {"iri": policy["iri"], "version": policy["version"],
                   "ceilings": dict(sorted((c["stage"], c["level"]) for c in ceilings))},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ontology", type=Path, default=Path(os.environ.get("AL_ONTOLOGY_DIR", ROOT.parent / "adaptive-learning-ontology")))
    args = parser.parse_args()

    vocab = vocabulary(args.ontology)
    shapes = Graph().parse(args.ontology / "shapes/al-core.shacl.ttl")
    dataset = Dataset(default_union=True)
    dataset.parse(CATALOG, format="trig")
    data = Graph()
    for triple in dataset.triples((None, None, None)):
        data.add(triple)
    for triple in vocab:
        data.add(triple)

    conforms, _, text = validate(data, shacl_graph=shapes, ont_graph=vocab, inference="rdfs", advanced=True)
    if not conforms:
        print(text, file=sys.stderr)
        return 1

    digest = hashlib.sha256(CATALOG.read_bytes()).hexdigest()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(project(data, digest), indent=2, ensure_ascii=False) + "\n")
    print(f"catalog conforms to al-core shapes; wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
