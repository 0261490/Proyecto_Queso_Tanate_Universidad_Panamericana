#!/usr/bin/env python3
"""Golden cases for the complete questionnaire, independently evaluated by pgmpy.

This validates the exported reconstruction, not recovery of the published model.
The explicit contract below is deliberately independent of the TypeScript catalog.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pgmpy.inference import VariableElimination
from generate_python_reference import build_model

QUESTIONS = (
    ("traditionalMexican", "Q1_Traditional_Mexican"),
    ("recommendation", "Q3_Recommendation"),
    ("gastronomicHeritage", "Q4_Gastronomic_Heritage"),
    ("authenticElaboration", "Q5_Authenticity_Elaboration"),
    ("commercialPotential", "Q6_Commercial_Potential"),
    ("culturePreservation", "Q7_Culture_Preservation"),
    ("sensoryUniqueness", "Q8_Sensory_Uniqueness"),
)
TARGET = "Q2_Purchase_Intention"


def generate(model_path: Path):
    raw = model_path.read_bytes()
    model = json.loads(raw)
    inference = VariableElimination(build_model(model))

    def probability(evidence):
        factor = inference.query([TARGET], evidence=evidence, show_progress=False)
        return float(factor.values[list(factor.state_names[TARGET]).index("Yes")])

    cases = []
    for mask in range(128):
        answers = {key: bool(mask & (1 << bit)) for bit, (key, _) in enumerate(QUESTIONS)}
        evidence = {variable: "Yes" if answers[key] else "No" for key, variable in QUESTIONS}
        cases.append({"id": f"assessment_{mask:03d}", "answers": answers,
                      "evidence": evidence, "probability": probability(evidence)})
    q8 = probability({"Q8_Sensory_Uniqueness": "Yes"})
    return {
        "generator": "pgmpy VariableElimination",
        "model_sha256": hashlib.sha256(raw).hexdigest(),
        "model_version": model["model_version"],
        "tolerance": 1e-12,
        "scientific_reference": {
            "query": "P(Q2=Yes | Q8=Yes)",
            "published_probability": 0.626,
            "reconstructed_probability": q8,
            "difference_percentage_points": (q8 - 0.626) * 100,
            "status": "documented_difference_not_exact_recovery",
        },
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_json", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true", help="Verify without overwriting the golden fixture")
    args = parser.parse_args()
    result = generate(args.model_json)
    if args.check:
        if json.loads(args.output.read_text(encoding="utf-8")) != result:
            raise SystemExit("Golden fixture differs: review model or generator; do not silently regenerate.")
        print("128 pgmpy golden cases verified; fixture unchanged.")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print("128 pgmpy golden cases generated.")
    print(json.dumps(result["scientific_reference"], indent=2))


if __name__ == "__main__":
    main()
