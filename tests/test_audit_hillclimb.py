#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd
from pgmpy.base import DAG

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_SOURCE = REPO_ROOT / "model-source"

if str(MODEL_SOURCE) not in sys.path:
    sys.path.insert(0, str(MODEL_SOURCE))

import audit_hillclimb as ah  # noqa: E402


class TestAuditHillClimb(unittest.TestCase):
    def test_operation_key_orders_tied_directions_canonically(self):
        candidates = [
            (("+", ("Q4_Gastronomic_Heritage", "Q1_Traditional_Mexican")), 1.0),
            (("+", ("Q1_Traditional_Mexican", "Q4_Gastronomic_Heritage")), 1.0),
        ]
        ordered = sorted(candidates, key=ah.operation_key)
        self.assertEqual(
            ordered[0][0],
            ("+", ("Q1_Traditional_Mexican", "Q4_Gastronomic_Heritage")),
        )

    def test_canonical_order_resolves_equal_score_with_first_operation(self):
        candidates = [
            (("+", ("Q4", "Q1")), 20.0),
            (("+", ("Q1", "Q4")), 20.0),
        ]
        ordered = sorted(candidates, key=ah.operation_key)
        winner = max(ordered, key=lambda item: item[1])
        self.assertEqual(winner[0], ("+", ("Q1", "Q4")))

    def test_canonical_order_does_not_override_higher_score(self):
        candidates = [
            (("+", ("A", "B")), 10.0),
            (("+", ("Z", "A")), 11.0),
        ]
        ordered = sorted(candidates, key=ah.operation_key)
        winner = max(ordered, key=lambda item: item[1])
        self.assertEqual(winner[0], ("+", ("Z", "A")))

    def test_canonical_dag_hash_is_independent_of_edge_insertion_order(self):
        dag_a = DAG()
        dag_a.add_nodes_from(["A", "B", "C"])
        dag_a.add_edges_from([("A", "B"), ("B", "C")])

        dag_b = DAG()
        dag_b.add_nodes_from(["C", "B", "A"])
        dag_b.add_edges_from([("B", "C"), ("A", "B")])

        self.assertEqual(ah.canonical_payload(dag_a), ah.canonical_payload(dag_b))
        self.assertEqual(ah.canonical_sha256(dag_a), ah.canonical_sha256(dag_b))

    def test_canonical_mode_resolves_synthetic_direction_tie_reproducibly(self):
        data = pd.DataFrame(
            {
                "A": ["No"] * 40 + ["Yes"] * 40,
                "B": ["No"] * 40 + ["Yes"] * 40,
            }
        )

        hashes = set()
        edges = set()
        tie_counts = []

        for _ in range(3):
            dag, _score, tie_events = ah.learn(
                data,
                mode=ah.MODE_CANONICAL,
                trace_ties=False,
            )
            hashes.add(ah.canonical_sha256(dag))
            edges.add(tuple(ah.canonical_payload(dag)["edges"]))
            tie_counts.append(tie_events)

        self.assertEqual(len(hashes), 1)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges.pop(), (("A", "B"),))
        self.assertTrue(all(count >= 1 for count in tie_counts))


if __name__ == "__main__":
    unittest.main()
