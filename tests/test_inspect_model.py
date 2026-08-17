import contextlib
import importlib.util
import io
import pickle
import tempfile
import unittest
from pathlib import Path

from pgmpy.factors.discrete import TabularCPD
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.readwrite import BIFWriter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSPECTOR_PATH = PROJECT_ROOT / "model-export" / "inspect_model.py"


def load_inspector_module():
    spec = importlib.util.spec_from_file_location("inspect_model", INSPECTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar el inspector desde: {INSPECTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_smoke_model():
    model = DiscreteBayesianNetwork(
        [("Q8_Sensory_Uniqueness", "Q2_Purchase_Intention")]
    )

    cpd_q8 = TabularCPD(
        variable="Q8_Sensory_Uniqueness",
        variable_card=2,
        values=[[0.25], [0.75]],
        state_names={"Q8_Sensory_Uniqueness": ["No", "Yes"]},
    )

    cpd_q2 = TabularCPD(
        variable="Q2_Purchase_Intention",
        variable_card=2,
        values=[[0.55, 0.374], [0.45, 0.626]],
        evidence=["Q8_Sensory_Uniqueness"],
        evidence_card=[2],
        state_names={
            "Q2_Purchase_Intention": ["No", "Yes"],
            "Q8_Sensory_Uniqueness": ["No", "Yes"],
        },
    )

    model.add_cpds(cpd_q8, cpd_q2)
    assert model.check_model()
    return model


def write_bif(model, path):
    writer = BIFWriter(model)
    if hasattr(writer, "write"):
        writer.write(str(path))
    else:
        writer.write_bif(str(path))


class InspectModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inspector = load_inspector_module()

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.model = build_smoke_model()
        self.bif_path = self.temp_path / "tenate_smoke.bif"
        write_bif(self.model, self.bif_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sha256_is_stable(self):
        first = self.inspector.sha256_file(self.bif_path)
        second = self.inspector.sha256_file(self.bif_path)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_bif_loads_with_expected_structure(self):
        model, loader_name = self.inspector.load_model(self.bif_path)
        self.assertEqual(loader_name, "BIFReader")
        self.assertTrue(model.check_model())

        self.assertEqual(
            set(model.nodes()),
            {"Q8_Sensory_Uniqueness", "Q2_Purchase_Intention"},
        )

        self.assertEqual(
            set(model.edges()),
            {("Q8_Sensory_Uniqueness", "Q2_Purchase_Intention")},
        )

        self.assertEqual(
            self.inspector.get_node_states(model, "Q8_Sensory_Uniqueness"),
            ["No", "Yes"],
        )

        self.assertEqual(
            self.inspector.get_node_states(model, "Q2_Purchase_Intention"),
            ["No", "Yes"],
        )

    def test_reference_inference_is_62_6_percent(self):
        model, loader_name = self.inspector.load_model(self.bif_path)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = self.inspector.audit_model(
                self.bif_path,
                model,
                loader_name,
            )

        text = output.getvalue()
        self.assertTrue(result)
        self.assertIn("Porcentaje = 62.6000%", text)
        self.assertIn("Diferencia absoluta = 0.0000 puntos %", text)
        self.assertIn("Porcentaje = 37.4000%", text)
        self.assertIn("Validaciones estructurales básicas: OK", text)

    def test_pickle_is_blocked_by_default(self):
        pickle_path = self.temp_path / "trusted_test_model.pkl"

        with pickle_path.open("wb") as handle:
            pickle.dump(self.model, handle)

        with self.assertRaises(RuntimeError):
            self.inspector.load_model(
                pickle_path,
                allow_pickle=False,
            )


if __name__ == "__main__":
    unittest.main()
