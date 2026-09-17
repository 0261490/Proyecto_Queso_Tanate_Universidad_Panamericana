#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_SOURCE = REPO_ROOT / "model-source"
EXPORTER_PATH = REPO_ROOT / "model-export" / "export_model.py"

if str(MODEL_SOURCE) not in sys.path:
    sys.path.insert(0, str(MODEL_SOURCE))

import estimate_cpts  # noqa: E402


def load_exporter():
    spec = importlib.util.spec_from_file_location("export_model", EXPORTER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


em = load_exporter()


def synthetic_payload():
    training = pd.DataFrame(
        {
            "A": ["No", "No", "Yes", "Yes"],
            "B": ["No", "Yes", "No", "Yes"],
        }
    )
    dag = DiscreteBayesianNetwork([("A", "B")])
    dag.add_nodes_from(["A", "B"])
    cpts, _diff, _zero = estimate_cpts.canonical_cpts(dag, training)
    return em.build_payload(
        source_sha256="source",
        training_sha256="training",
        training=training,
        dag=dag,
        bic_score=-1.0,
        tie_events=0,
        cpts=cpts,
    )


class TestExportModel(unittest.TestCase):
    def test_canonical_json_is_independent_of_dict_insertion_order(self):
        a = {"a": 1, "b": {"x": 2, "y": 3}}
        b = {"b": {"y": 3, "x": 2}, "a": 1}
        self.assertEqual(em.canonical_bytes(a), em.canonical_bytes(b))
        self.assertEqual(em.canonical_sha256(a), em.canonical_sha256(b))

    def test_valid_payload_passes(self):
        payload = synthetic_payload()
        em.validate_payload(payload)

    def test_cycle_is_rejected(self):
        payload = synthetic_payload()
        payload["edges"].append({"source": "B", "target": "A"})
        with self.assertRaises(em.ModelExportError):
            em.validate_payload(payload)

    def test_non_normalized_cpt_is_rejected(self):
        payload = synthetic_payload()
        broken = copy.deepcopy(payload)
        broken["cpts"][0]["values"][0][0] = 0.8
        with self.assertRaises(em.ModelExportError):
            em.validate_payload(broken)

    def test_component_hash_tampering_is_rejected(self):
        payload = synthetic_payload()
        payload["metadata"]["learning"]["dag_sha256"] = "incorrect"
        with self.assertRaises(em.ModelExportError):
            em.validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
