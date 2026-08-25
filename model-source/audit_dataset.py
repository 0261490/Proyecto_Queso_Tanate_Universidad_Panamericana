#!/usr/bin/env python3
"""
Proyecto Tenate — Auditoría reproducible de la base de datos científica.

Este script NO modifica el CSV, NO entrena la Red Bayesiana y NO exporta JSON.
Su objetivo es verificar la integridad estructural de la base recibida antes de
usarla en la auditoría científica de la Sección 2.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS = [
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

DEMOGRAPHIC_COLUMNS = [
    "Gender",
    "Age",
    "Standardized_City",
]

EXPECTED_BINARY_STATES = {"Yes", "No"}


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 leyendo el archivo en bloques y sin modificarlo."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def print_header(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def format_percent(count: int, total: int) -> str:
    if total == 0:
        return "0.00%"
    return f"{(count / total) * 100:.2f}%"


def audit_dataset(path: Path, expected_rows: int) -> bool:
    """Audita el CSV. Devuelve True cuando las validaciones estructurales pasan."""
    errors: list[str] = []
    warnings: list[str] = []

    print_header("PROYECTO TENATE — AUDITORÍA DE BASE DE DATOS (SOLO LECTURA)")
    print(f"Archivo       : {path}")
    print(f"Tamaño        : {path.stat().st_size} bytes")
    print(f"SHA-256       : {sha256_file(path)}")

    try:
        # utf-8-sig también acepta UTF-8 normal y elimina un posible BOM.
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR al leer CSV: {type(exc).__name__}: {exc}")
        return False

    print(f"Filas         : {len(df)}")
    print(f"Columnas      : {len(df.columns)}")

    print_header("1. ESTRUCTURA")

    if len(df) == expected_rows:
        print(f"[OK] Número de filas esperado: {expected_rows}")
    else:
        errors.append(
            f"Se esperaban {expected_rows} filas y se encontraron {len(df)}."
        )
        print(f"[ERROR] {errors[-1]}")

    observed_columns = list(df.columns)

    missing_columns = [
        column for column in EXPECTED_COLUMNS if column not in observed_columns
    ]
    extra_columns = [
        column for column in observed_columns if column not in EXPECTED_COLUMNS
    ]

    if observed_columns == EXPECTED_COLUMNS:
        print("[OK] Columnas y orden coinciden con el esquema esperado.")
    else:
        if missing_columns:
            errors.append(f"Columnas faltantes: {missing_columns}")
            print(f"[ERROR] {errors[-1]}")
        if extra_columns:
            warnings.append(f"Columnas adicionales: {extra_columns}")
            print(f"[ADVERTENCIA] {warnings[-1]}")
        if not missing_columns and not extra_columns:
            warnings.append(
                "Las columnas esperadas existen, pero su orden es diferente."
            )
            print(f"[ADVERTENCIA] {warnings[-1]}")

    print()
    print("Columnas observadas:")
    for index, column in enumerate(observed_columns, start=1):
        print(f"{index:02d}. {column}")

    print_header("2. INTEGRIDAD")

    missing_cells = int(df.isna().sum().sum())
    if missing_cells == 0:
        print("[OK] No existen valores faltantes.")
    else:
        errors.append(f"Se encontraron {missing_cells} valores faltantes.")
        print(f"[ERROR] {errors[-1]}")

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows == 0:
        print("[OK] No existen filas completamente duplicadas.")
    else:
        warnings.append(f"Se encontraron {duplicate_rows} filas duplicadas.")
        print(f"[ADVERTENCIA] {warnings[-1]}")

    if "Judge_ID" in df.columns:
        duplicate_ids = int(df["Judge_ID"].duplicated().sum())
        blank_ids = int(
            df["Judge_ID"].fillna("").astype(str).str.strip().eq("").sum()
        )

        if duplicate_ids == 0:
            print("[OK] Judge_ID no contiene duplicados.")
        else:
            errors.append(f"Judge_ID contiene {duplicate_ids} duplicados.")
            print(f"[ERROR] {errors[-1]}")

        if blank_ids == 0:
            print("[OK] Judge_ID no contiene valores vacíos.")
        else:
            errors.append(f"Judge_ID contiene {blank_ids} valores vacíos.")
            print(f"[ERROR] {errors[-1]}")

    print_header("3. VARIABLES Q1–Q8")

    for column in BINARY_COLUMNS:
        if column not in df.columns:
            print(f"[ERROR] {column}: columna ausente.")
            continue

        values = set(df[column].dropna().astype(str).str.strip().unique())
        unexpected = values - EXPECTED_BINARY_STATES

        print()
        print(column)

        counts = df[column].value_counts(dropna=False)
        for state in ("Yes", "No"):
            count = int(counts.get(state, 0))
            print(
                f"  {state:<3} = {count:>3} / {len(df)} "
                f"({format_percent(count, len(df))})"
            )

        if not unexpected:
            print("  [OK] Estados limitados a Yes/No.")
        else:
            errors.append(
                f"{column} contiene estados inesperados: {sorted(unexpected)}"
            )
            print(f"  [ERROR] {errors[-1]}")

    print_header("4. VARIABLES DEMOGRÁFICAS")

    for column in DEMOGRAPHIC_COLUMNS:
        if column not in df.columns:
            print(f"[ERROR] {column}: columna ausente.")
            continue

        print()
        print(column)
        counts = df[column].value_counts(dropna=False)

        for state, count in counts.items():
            state_text = "<NA>" if pd.isna(state) else str(state)
            print(
                f"  {state_text}: {int(count)} "
                f"({format_percent(int(count), len(df))})"
            )

    print_header("5. FRECUENCIA CONDICIONAL EMPÍRICA")

    q2 = "Q2_Purchase_Intention"
    q8 = "Q8_Sensory_Uniqueness"

    if q2 in df.columns and q8 in df.columns:
        q8_yes = df[df[q8] == "Yes"]
        total_q8_yes = len(q8_yes)
        q2_yes_given_q8_yes = int((q8_yes[q2] == "Yes").sum())
        q2_no_given_q8_yes = int((q8_yes[q2] == "No").sum())

        print(f"Registros con {q8} = Yes: {total_q8_yes}")

        if total_q8_yes:
            p_yes = q2_yes_given_q8_yes / total_q8_yes
            p_no = q2_no_given_q8_yes / total_q8_yes

            print(
                "Frecuencia empírica "
                f"P({q2}=Yes | {q8}=Yes) = {p_yes:.10f} "
                f"({p_yes * 100:.4f}%)"
            )
            print(
                "Frecuencia empírica "
                f"P({q2}=No  | {q8}=Yes) = {p_no:.10f} "
                f"({p_no * 100:.4f}%)"
            )

    print()
    print(
        "IMPORTANTE: estas son frecuencias directas del CSV. "
        "NO equivalen automáticamente a la inferencia posterior de la "
        "Red Bayesiana publicada."
    )
    print(
        "La referencia P(Q2=Yes | Q8=Yes) ≈ 62.6% deberá comprobarse "
        "con el modelo científico original cuando sea recibido."
    )

    print_header("6. RESULTADO")

    if errors:
        print("AUDITORÍA ESTRUCTURAL: REQUIERE REVISIÓN")
        print()
        print("Errores:")
        for error in errors:
            print(f"- {error}")
    else:
        print("AUDITORÍA ESTRUCTURAL: OK")

    if warnings:
        print()
        print("Advertencias:")
        for warning in warnings:
            print(f"- {warning}")

    print()
    print(
        "Este resultado valida la integridad estructural de la base, "
        "no su equivalencia científica con la versión utilizada en el artículo."
    )

    return not errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Auditor de solo lectura para la base de datos científica "
            "de Proyecto Tenate."
        )
    )
    parser.add_argument(
        "csv",
        type=Path,
        help="Ruta al archivo CSV original.",
    )
    parser.add_argument(
        "--expected-rows",
        type=int,
        default=169,
        help="Número esperado de registros. Valor por defecto: 169.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.csv.expanduser().resolve()

    if not path.exists():
        print(f"ERROR: el archivo no existe: {path}", file=sys.stderr)
        return 2

    if not path.is_file():
        print(f"ERROR: la ruta no corresponde a un archivo: {path}", file=sys.stderr)
        return 2

    if path.suffix.lower() != ".csv":
        print(
            f"ERROR: se esperaba un archivo .csv y se recibió: {path.suffix}",
            file=sys.stderr,
        )
        return 2

    ok = audit_dataset(path, expected_rows=args.expected_rows)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
