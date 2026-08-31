#!/usr/bin/env python3
"""
Proyecto Tenate — Preparación reproducible del dataset científico.

Este script:
- verifica que el CSV de entrada sea exactamente la fuente auditada;
- valida su estructura e integridad;
- excluye Judge_ID de la vista de entrenamiento;
- conserva sin cambios los estados y categorías científicas;
- genera, opcionalmente, un CSV de entrenamiento determinista.

NO entrena la Red Bayesiana.
NO modifica el CSV original.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import sys
from pathlib import Path

import pandas as pd


EXPECTED_SOURCE_SHA256 = (
    "2a74e34d0cb9dad5f98bdd8d0cf4691c5ffc929ead195ea39de603974ca716be"
)

EXPECTED_ROWS = 169

SOURCE_COLUMNS = [
    "Judge_ID",
    "Gender",
    "Age",
    "Standardized_City",
    "Q1_Traditional_Mexican",
    "Q2_Purchase_Intention",
    "Q3_Recommendation",
    "Q4_Gastronomic_Heritage",
    "Q5_Authenticity_Elaboration",
    "Q6_Commercial_Potential",
    "Q7_Culture_Preservation",
    "Q8_Sensory_Uniqueness",
]

TRAINING_COLUMNS = [
    "Gender",
    "Age",
    "Standardized_City",
    "Q1_Traditional_Mexican",
    "Q2_Purchase_Intention",
    "Q3_Recommendation",
    "Q4_Gastronomic_Heritage",
    "Q5_Authenticity_Elaboration",
    "Q6_Commercial_Potential",
    "Q7_Culture_Preservation",
    "Q8_Sensory_Uniqueness",
]

BINARY_COLUMNS = [
    "Q1_Traditional_Mexican",
    "Q2_Purchase_Intention",
    "Q3_Recommendation",
    "Q4_Gastronomic_Heritage",
    "Q5_Authenticity_Elaboration",
    "Q6_Commercial_Potential",
    "Q7_Culture_Preservation",
    "Q8_Sensory_Uniqueness",
]

EXPECTED_BINARY_STATES = {"Yes", "No"}


class DatasetPreparationError(ValueError):
    """Error de validación o preparación reproducible del dataset."""


def sha256_bytes(data: bytes) -> str:
    """Calcula SHA-256 de bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 del archivo sin modificarlo."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_source_csv(path: Path) -> pd.DataFrame:
    """Carga el CSV como texto, conservando las categorías tal como aparecen."""
    try:
        return pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    except Exception as exc:  # noqa: BLE001
        raise DatasetPreparationError(
            f"No fue posible leer el CSV: {type(exc).__name__}: {exc}"
        ) from exc


def validate_source_dataframe(df: pd.DataFrame) -> None:
    """Valida la estructura científica mínima de la fuente."""
    if len(df) != EXPECTED_ROWS:
        raise DatasetPreparationError(
            f"Número de filas inválido: esperado={EXPECTED_ROWS}, observado={len(df)}"
        )

    observed_columns = list(df.columns)
    if observed_columns != SOURCE_COLUMNS:
        raise DatasetPreparationError(
            "Las columnas o su orden no coinciden con el esquema científico esperado."
        )

    missing_cells = int(df.isna().sum().sum())
    if missing_cells:
        raise DatasetPreparationError(
            f"Se encontraron {missing_cells} valores faltantes."
        )

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows:
        raise DatasetPreparationError(
            f"Se encontraron {duplicate_rows} filas completamente duplicadas."
        )

    duplicate_ids = int(df["Judge_ID"].duplicated().sum())
    if duplicate_ids:
        raise DatasetPreparationError(
            f"Judge_ID contiene {duplicate_ids} valores duplicados."
        )

    blank_ids = int(
        df["Judge_ID"].fillna("").astype(str).str.strip().eq("").sum()
    )
    if blank_ids:
        raise DatasetPreparationError(
            f"Judge_ID contiene {blank_ids} valores vacíos."
        )

    for column in BINARY_COLUMNS:
        observed_states = set(df[column].dropna().astype(str).unique())
        unexpected = observed_states - EXPECTED_BINARY_STATES
        if unexpected:
            raise DatasetPreparationError(
                f"{column} contiene estados inesperados: {sorted(unexpected)}"
            )


def build_training_view(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la vista científica de entrenamiento.

    Judge_ID se excluye. No se recodifican estados ni categorías.
    """
    training = df.loc[:, TRAINING_COLUMNS].copy()

    if training.shape != (EXPECTED_ROWS, len(TRAINING_COLUMNS)):
        raise DatasetPreparationError(
            "La vista de entrenamiento no tiene dimensiones 169 x 11."
        )

    if "Judge_ID" in training.columns:
        raise DatasetPreparationError(
            "Judge_ID no debe formar parte de la vista de entrenamiento."
        )

    return training


def canonical_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Serializa la vista de entrenamiento de forma determinista.

    - UTF-8 sin BOM
    - sin índice
    - orden de filas conservado
    - orden de columnas científico fijo
    - salto de línea LF
    """
    buffer = io.StringIO(newline="")
    df.to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue().encode("utf-8")


def write_canonical_csv(data: bytes, output: Path) -> None:
    """Escribe el dataset derivado solo después de completar las validaciones."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)


def prepare_dataset(
    source: Path,
    *,
    expected_source_sha256: str = EXPECTED_SOURCE_SHA256,
    output: Path | None = None,
) -> tuple[pd.DataFrame, str]:
    """
    Valida la fuente y prepara la vista de entrenamiento.

    Devuelve:
        (training_dataframe, training_sha256)
    """
    source = source.expanduser().resolve()

    if not source.exists():
        raise DatasetPreparationError(f"El archivo no existe: {source}")

    if not source.is_file():
        raise DatasetPreparationError(
            f"La ruta no corresponde a un archivo: {source}"
        )

    if source.suffix.lower() != ".csv":
        raise DatasetPreparationError(
            f"Se esperaba un archivo .csv y se recibió: {source.suffix}"
        )

    observed_source_sha256 = sha256_file(source)
    if observed_source_sha256.lower() != expected_source_sha256.lower():
        raise DatasetPreparationError(
            "SHA-256 de la fuente no coincide con el CSV científico auditado.\n"
            f"Esperado : {expected_source_sha256.lower()}\n"
            f"Observado: {observed_source_sha256.lower()}"
        )

    source_df = load_source_csv(source)
    validate_source_dataframe(source_df)

    training_df = build_training_view(source_df)
    training_bytes = canonical_csv_bytes(training_df)
    training_sha256 = sha256_bytes(training_bytes)

    if output is not None:
        output = output.expanduser().resolve()
        write_canonical_csv(training_bytes, output)

    return training_df, training_sha256


def print_summary(
    source: Path,
    training: pd.DataFrame,
    training_sha256: str,
    output: Path | None,
) -> None:
    """Muestra evidencia reproducible de la preparación."""
    print("=" * 78)
    print("PROYECTO TENATE — PREPARACIÓN REPRODUCIBLE DEL DATASET")
    print("=" * 78)
    print(f"Fuente                  : {source}")
    print(f"SHA-256 fuente          : {sha256_file(source)}")
    print(f"Filas fuente            : {EXPECTED_ROWS}")
    print(f"Columnas fuente         : {len(SOURCE_COLUMNS)}")
    print()
    print("Transformación aplicada:")
    print("  - Judge_ID excluido de la vista de entrenamiento")
    print("  - orden de filas conservado")
    print("  - categorías demográficas conservadas")
    print("  - estados Q1-Q8 conservados como Yes/No")
    print("  - sin imputación")
    print("  - sin recodificación científica")
    print()
    print(f"Filas entrenamiento     : {len(training)}")
    print(f"Columnas entrenamiento  : {len(training.columns)}")
    print(f"SHA-256 entrenamiento   : {training_sha256}")
    print()
    print("Columnas de entrenamiento:")
    for index, column in enumerate(training.columns, start=1):
        print(f"{index:02d}. {column}")

    if output is None:
        print()
        print("Archivo derivado         : NO ESCRITO (modo verificación)")
    else:
        print()
        print(f"Archivo derivado         : {output}")
        print("Formato                   : CSV UTF-8, LF, sin índice")

    print()
    print("RESULTADO: DATASET DE ENTRENAMIENTO PREPARADO CORRECTAMENTE")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepara de manera reproducible la vista de entrenamiento "
            "de Proyecto Tenate a partir del CSV científico auditado."
        )
    )
    parser.add_argument(
        "csv",
        type=Path,
        help="Ruta al CSV científico original.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Ruta opcional para escribir el CSV derivado de entrenamiento. "
            "Si se omite, solo se valida y calcula su SHA-256."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.csv.expanduser().resolve()
    output = args.output.expanduser().resolve() if args.output else None

    try:
        training, training_sha256 = prepare_dataset(
            source,
            output=output,
        )
    except DatasetPreparationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print_summary(
        source=source,
        training=training,
        training_sha256=training_sha256,
        output=output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
