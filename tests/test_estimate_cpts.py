#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_SOURCE = REPO_ROOT / "model-source"

if str(MODEL_SOURCE) not in sys.path:
    sys.path.insert(0, str(MODEL_SOURCE))

import estimate_cpts as ec  # noqa: E402


class TestEstimateCPTs(unittest.TestCase):
    def test_canonical_bytes_are_deterministic(self):
        cpts_a = [
            {
                "node": "A",
                "parents": [],
                "state_names": {"A": ["No", "Yes"]},
                "values": [[0.25], [0.75]],
            }
        ]

        cpts_b = [
            {
                "values": [[0.25], [0.75]],
                "state_names": {"A": ["No", "Yes"]},
                "parents": [],
                "node": "A",
            }
        ]

        self.assertEqual(
            ec.canonical_bytes(cpts_a),
            ec.canonical_bytes(cpts_b),
        )
        self.assertEqual(
            ec.canonical_sha256(cpts_a),
            ec.canonical_sha256(cpts_b),
        )

    def test_cpt_hash_is_independent_of_dag_insertion_order(self):
        data = pd.DataFrame(
            {
                "A": ["No", "No", "Yes", "Yes"],
                "B": ["No", "Yes", "No", "Yes"],
            }
        )

        dag_a = DiscreteBayesianNetwork([("A", "B")])
        dag_a.add_nodes_from(["A", "B"])

        dag_b = DiscreteBayesianNetwork()
        dag_b.add_nodes_from(["B", "A"])
        dag_b.add_edges_from([("A", "B")])

        cpts_a, diff_a, zero_a = ec.canonical_cpts(dag_a, data)
        cpts_b, diff_b, zero_b = ec.canonical_cpts(dag_b, data)

        self.assertEqual(ec.canonical_sha256(cpts_a), ec.canonical_sha256(cpts_b))
        self.assertEqual(diff_a, 0.0)
        self.assertEqual(diff_b, 0.0)
        self.assertEqual(zero_a, 0)
        self.assertEqual(zero_b, 0)

    def test_cpts_equal_empirical_frequencies(self):
        data = pd.DataFrame(
            {
                "A": ["No", "No", "Yes", "Yes", "Yes"],
                "B": ["No", "Yes", "Yes", "Yes", "No"],
            }
        )

        dag = DiscreteBayesianNetwork([("A", "B")])
        dag.add_nodes_from(["A", "B"])

        cpts, max_diff, zero_configs = ec.canonical_cpts(dag, data)

        self.assertEqual(max_diff, 0.0)
        self.assertEqual(zero_configs, 0)

        by_node = {item["node"]: item for item in cpts}

        self.assertEqual(by_node["A"]["state_names"]["A"], ["No", "Yes"])

        np.testing.assert_allclose(
            np.asarray(by_node["A"]["values"], dtype=float).reshape(-1),
            np.asarray([2 / 5, 3 / 5]),
            atol=ec.ABS_TOL,
            rtol=0.0,
        )

        np.testing.assert_allclose(
            np.asarray(by_node["B"]["values"], dtype=float),
            np.asarray(
                [
                    [1 / 2, 1 / 3],
                    [1 / 2, 2 / 3],
                ]
            ),
            atol=ec.ABS_TOL,
            rtol=0.0,
        )

    def test_all_cpt_columns_are_normalized(self):
        data = pd.DataFrame(
            {
                "A": ["No", "No", "Yes", "Yes"],
                "B": ["No", "Yes", "No", "Yes"],
                "C": ["No", "Yes", "Yes", "Yes"],
            }
        )

        dag = DiscreteBayesianNetwork(
            [
                ("A", "C"),
                ("B", "C"),
            ]
        )
        dag.add_nodes_from(["A", "B", "C"])

        cpts, _max_diff, zero_configs = ec.canonical_cpts(dag, data)

        self.assertEqual(zero_configs, 0)

        for item in cpts:
            values = np.asarray(item["values"], dtype=float)
            sums = values.sum(axis=0)
            np.testing.assert_allclose(
                sums,
                1.0,
                atol=ec.ABS_TOL,
                rtol=0.0,
            )

    def test_missing_parent_configuration_is_rejected(self):
        data = pd.DataFrame(
            {
                "A": ["No", "No", "Yes"],
                "B": ["No", "Yes", "No"],
                "C": ["No", "Yes", "Yes"],
            }
        )

        dag = DiscreteBayesianNetwork(
            [
                ("A", "C"),
                ("B", "C"),
            ]
        )
        dag.add_nodes_from(["A", "B", "C"])

        with self.assertRaises(ec.CPTReconstructionError):
            ec.canonical_cpts(dag, data)


if __name__ == "__main__":
    unittest.main()