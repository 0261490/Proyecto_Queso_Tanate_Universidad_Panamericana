#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_SOURCE = REPO_ROOT / "model-source"

if str(MODEL_SOURCE) not in sys.path:
    sys.path.insert(0, str(MODEL_SOURCE))

import validate_model as vm  # noqa: E402


class TestValidateModel(unittest.TestCase):
    def test_identical_structure_has_perfect_metrics(self):
        dag = nx.DiGraph()
        dag.add_edges_from(vm.PUBLISHED_FIG1_EDGES)

        result = vm.compare_structure(dag)

        self.assertEqual(result.common_edges, len(vm.PUBLISHED_FIG1_EDGES))
        self.assertEqual(result.only_published, ())
        self.assertEqual(result.only_reconstructed, ())
        self.assertEqual(result.precision, 1.0)
        self.assertEqual(result.recall, 1.0)
        self.assertEqual(result.f1, 1.0)
        self.assertEqual(result.jaccard, 1.0)
        self.assertEqual(result.shd, 0)

    def test_reversed_edge_counts_as_one_structural_change(self):
        dag = nx.DiGraph()
        published = set(vm.PUBLISHED_FIG1_EDGES)
        source, target = next(iter(published))
        published.remove((source, target))
        dag.add_edges_from(published)
        dag.add_edge(target, source)

        result = vm.compare_structure(dag)

        self.assertEqual(result.shd, 1)
        self.assertEqual(result.symmetric_difference, 2)

    def test_probability_metrics_use_half_threshold(self):
        metrics = vm._metrics(
            [0, 0, 1, 1],
            [0.1, 0.49, 0.5, 0.9],
        )

        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertGreaterEqual(metrics["auc_roc"], 0.0)
        self.assertLessEqual(metrics["auc_roc"], 1.0)
        self.assertTrue(np.isfinite(metrics["log_loss"]))

    def test_isolated_q8_does_not_change_q2_probability(self):
        training = pd.DataFrame(
            {
                vm.TARGET: ["No", "No", "Yes", "Yes", "Yes"],
                vm.SENSORY: ["No", "Yes", "No", "Yes", "Yes"],
            }
        )
        dag = nx.DiGraph()
        dag.add_nodes_from([vm.TARGET, vm.SENSORY])

        result = vm.full_model_probability_validation(training, dag)

        self.assertTrue(result["posterior_equals_prior"])
        self.assertEqual(result["q8_degree"], 0)
        self.assertFalse(result["path_q8_to_q2"])
        self.assertAlmostEqual(result["prior_q2_yes"], 3 / 5)


if __name__ == "__main__":
    unittest.main()
