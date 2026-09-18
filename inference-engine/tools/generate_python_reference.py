#!/usr/bin/env python3
"""Genera casos de referencia de pgmpy para validar el motor TypeScript."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork


CASES = (
    ("age_prior", "Age", {}),
    ("q2_prior", "Q2_Purchase_Intention", {}),
    (
        "q2_given_q8_yes",
        "Q2_Purchase_Intention",
        {"Q8_Sensory_Uniqueness": "Yes"},
    ),
    (
        "q1_given_q5_yes",
        "Q1_Traditional_Mexican",
        {"Q5_Authenticity_Elaboration": "Yes"},
    ),
    (
        "q4_given_q3_yes",
        "Q4_Gastronomic_Heritage",
        {"Q3_Recommendation": "Yes"},
    ),
    (
        "q4_given_q1_yes_q3_yes",
        "Q4_Gastronomic_Heritage",
        {
            "Q1_Traditional_Mexican": "Yes",
            "Q3_Recommendation": "Yes",
        },
    ),
    (
        "q6_given_q3_no",
        "Q6_Commercial_Potential",
        {"Q3_Recommendation": "No"},
    ),
)


def build_model(payload):
    edges = [(edge["source"], edge["target"]) for edge in payload["edges"]]
    model = DiscreteBayesianNetwork(edges)
    model.add_nodes_from(node["id"] for node in payload["nodes"])

    cpds = []
    for item in payload["cpts"]:
        node = item["node"]
        parents = item["parents"]
        kwargs = {
            "variable": node,
            "variable_card": len(item["state_names"][node]),
            "values": item["values"],
            "state_names": item["state_names"],
        }
        if parents:
            kwargs["evidence"] = parents
            kwargs["evidence_card"] = [
                len(item["state_names"][parent]) for parent in parents
            ]
        cpds.append(TabularCPD(**kwargs))

    model.add_cpds(*cpds)
    if not model.check_model():
        raise RuntimeError("El modelo reconstruido desde JSON no pasó check_model().")
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_json", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    model_bytes = args.model_json.read_bytes()
    payload = json.loads(model_bytes)
    infer = VariableElimination(build_model(payload))

    cases = []
    for case_id, variable, evidence in CASES:
        factor = infer.query(
            variables=[variable],
            evidence=evidence,
            show_progress=False,
        )
        cases.append(
            {
                "id": case_id,
                "variable": variable,
                "evidence": evidence,
                "states": list(factor.state_names[variable]),
                "probabilities": [float(value) for value in factor.values],
            }
        )

    result = {
        "generator": "pgmpy VariableElimination",
        "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
