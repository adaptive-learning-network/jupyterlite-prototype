#!/usr/bin/env python3
"""Validate an exported learner graph against the al-core SHACL shapes.

The export is checked together with the catalog it references, so class and
cross-graph constraints (targets, rules, policy ceilings) are evaluated.

Usage:
  python scripts/validate_export.py test-results/learner-export.nq [--ontology ../adaptive-learning-ontology]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Dataset, Graph

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("export", type=Path)
    parser.add_argument("--ontology", type=Path, default=Path(os.environ.get("AL_ONTOLOGY_DIR", ROOT.parent / "adaptive-learning-ontology")))
    args = parser.parse_args()

    vocab = Graph()
    for path in [args.ontology / "ontology/al-core.ttl", args.ontology / "vocab/al-schemes.ttl", *sorted((args.ontology / "vocab/scales").glob("*.ttl"))]:
        vocab.parse(path)
    shapes = Graph().parse(args.ontology / "shapes/al-core.shacl.ttl")

    dataset = Dataset(default_union=True)
    dataset.parse(ROOT / "catalog/outbreak-analysis.trig", format="trig")
    dataset.parse(args.export, format="nquads")
    data = Graph()
    for triple in dataset.triples((None, None, None)):
        data.add(triple)
    for triple in vocab:
        data.add(triple)

    conforms, _, text = validate(data, shacl_graph=shapes, ont_graph=vocab, inference="rdfs", advanced=True)
    print(f"{args.export}: {'conforms' if conforms else 'DOES NOT CONFORM'} to al-core shapes")
    if not conforms:
        print(text)
    return 0 if conforms else 1


if __name__ == "__main__":
    sys.exit(main())
