#!/usr/bin/env python3
"""
Pruebas automáticas para model-source/prepare_dataset.py.

Las pruebas usan exclusivamente datos sintéticos.
No requieren ni modifican el CSV científico original.
"""

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "model-source" / "prepare_dataset.py"

spec = importlib.util.spec_from_file_location("prepare_dataset", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"No se pudo cargar el módulo: {MODULE_PATH}")

prepare_dataset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare_dataset)


def make_synthetic_dataframe() -> pd.DataFrame:
    """Construye 169 filas sintéticas con el esquema científico esperado."""
    rows: list[dict[str, str]] = []

    genders = ["Female", "Male"]
    ages = ["18-21", "22-25", "26-29"]
    cities = ["Guadalajara", "Zapopan", "Otro"]

    for index in range(prepare_dataset.EXPECTED_ROWS):
        yes_no = "Yes" if index % 2 == 0 else "No"

        rows.append(
            {
                "Judge_ID": f"J{index + 1:03d}",
                "Gender": genders[index % len(genders)],
                "Age": ages[index % len(ages)],
                "Standardized_City": cities[index % len(cities)],
                "Q1_Traditional_Mexican": yes_no,
                "Q2_Purchase_Intention": "Yes" if index % 3 else "No",
                "Q3_Recommendation": "Yes" if index % 4 else "No",
                "Q4_Gastronomic_Heritage": "Yes" if index % 5 else "No",
                "Q5_Authenticity_Elaboration": "Yes" if index % 6 else "No",
                "Q6_Commercial_Potential": "Yes" if index % 7 else "No",
                "Q7_Culture_Preservation": "Yes" if index % 8 else "No",
                "Q8_Sensory_Uniqueness": "Yes" if index % 9 else "No",
            }
        )

    return pd.DataFrame(rows, columns=prepare_dataset.SOURCE_COLUMNS)


def write_source_csv(path: Path, df: pd.DataFrame) -> str:
    """Escribe fixture UTF-8/LF y devuelve su SHA-256."""
    csv_text = df.to_csv(index=False, lineterminator="\n")
    data = csv_text.encode("utf-8")
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


class PrepareDatasetTests(unittest.TestCase):
    def test_training_view_has_169_rows_11_columns_and_no_judge_id(self) -> None:
        df = make_synthetic_dataframe()

        prepare_dataset.validate_source_dataframe(df)
        training = prepare_dataset.build_training_view(df)

        self.assertEqual(training.shape, (169, 11))
        self.assertEqual(list(training.columns), prepare_dataset.TRAINING_COLUMNS)
        self.assertNotIn("Judge_ID", training.columns)

    def test_training_view_preserves_scientific_values(self) -> None:
        df = make_synthetic_dataframe()
        training = prepare_dataset.build_training_view(df)

        expected = df.loc[:, prepare_dataset.TRAINING_COLUMNS]
        pd.testing.assert_frame_equal(training, expected)

    def test_prepare_dataset_is_deterministic(self) -> None:
        df = make_synthetic_dataframe()

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.csv"
            source_hash = write_source_csv(source, df)

            first_df, first_hash = prepare_dataset.prepare_dataset(
                source,
                expected_source_sha256=source_hash,
            )
            second_df, second_hash = prepare_dataset.prepare_dataset(
                source,
                expected_source_sha256=source_hash,
            )

            pd.testing.assert_frame_equal(first_df, second_df)
            self.assertEqual(first_hash, second_hash)

            canonical = prepare_dataset.canonical_csv_bytes(first_df)
            self.assertEqual(first_hash, hashlib.sha256(canonical).hexdigest())

    def test_wrong_source_hash_is_rejected(self) -> None:
        df = make_synthetic_dataframe()

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.csv"
            write_source_csv(source, df)

            with self.assertRaises(prepare_dataset.DatasetPreparationError):
                prepare_dataset.prepare_dataset(
                    source,
                    expected_source_sha256="0" * 64,
                )

    def test_unexpected_binary_state_is_rejected(self) -> None:
        df = make_synthetic_dataframe()
        df.loc[0, "Q8_Sensory_Uniqueness"] = "Maybe"

        with self.assertRaises(prepare_dataset.DatasetPreparationError):
            prepare_dataset.validate_source_dataframe(df)

    def test_duplicate_judge_id_is_rejected(self) -> None:
        df = make_synthetic_dataframe()
        df.loc[1, "Judge_ID"] = df.loc[0, "Judge_ID"]

        with self.assertRaises(prepare_dataset.DatasetPreparationError):
            prepare_dataset.validate_source_dataframe(df)

    def test_output_file_matches_canonical_training_bytes(self) -> None:
        df = make_synthetic_dataframe()

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.csv"
            output = Path(tmp) / "training.csv"
            source_hash = write_source_csv(source, df)

            training, training_hash = prepare_dataset.prepare_dataset(
                source,
                expected_source_sha256=source_hash,
                output=output,
            )

            expected_bytes = prepare_dataset.canonical_csv_bytes(training)

            self.assertTrue(output.exists())
            self.assertEqual(output.read_bytes(), expected_bytes)
            self.assertEqual(
                hashlib.sha256(output.read_bytes()).hexdigest(),
                training_hash,
            )


if __name__ == "__main__":
    unittest.main()
