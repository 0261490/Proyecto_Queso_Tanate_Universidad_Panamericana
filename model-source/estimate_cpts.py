#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pgmpy
from pgmpy.estimators import MaximumLikelihoodEstimator

import audit_hillclimb
import prepare_dataset


EXPECTED_PGMPY_VERSION = "1.1.2"

EXPECTED_TRAINING_SHA256 = (
    "c8eb4a4e2107fde5817f87481db1a59485cf82e1ec41e9d42a672b578bb033e5"
)

EXPECTED_DAG_SHA256 = (
    "11fb5b49d2d51e4508563e4ba4b1d07eba1e36cf0e6da36703312c9c08136cdb"
)

EXPECTED_CPT_SHA256 = (
    "a35320e2de8b2bc7c3af0093b968b1b46d28f8a8911a8ebbc19710861a88e61c"
)

ABS_TOL = 1e-15


class CPTReconstructionError(RuntimeError):
    """Error de validación durante la reconstrucción reproducible de CPT."""


def canonical_cpts(dag, training):
    """
    Estima CPT mediante MLE y devuelve una representación canónica.

    Política:
    - weighted=False;
    - nodos ordenados lexicográficamente;
    - padres ordenados lexicográficamente;
    - estados determinados por pgmpy 1.1.2;
    - ninguna configuración de padres puede carecer de observaciones;
    - cada CPT debe coincidir con las frecuencias empíricas normalizadas.
    """
    estimator = MaximumLikelihoodEstimator(dag, training)

    result = []
    global_max_diff = 0.0
    total_zero_parent_configs = 0

    for node in sorted(dag.nodes(), key=str):
        parents = sorted(dag.get_parents(node), key=str)

        counts = estimator.state_counts(node, weighted=False)
        count_values = counts.to_numpy(dtype=float)

        zero_mask = (count_values == 0).all(axis=0)
        zero_count = int(zero_mask.sum())
        total_zero_parent_configs += zero_count

        if zero_count:
            missing = list(counts.columns[zero_mask])
            raise CPTReconstructionError(
                f"{node}: existen {zero_count} configuraciones de padres "
                f"sin observaciones: {missing!r}"
            )

        empirical = count_values / count_values.sum(axis=0, keepdims=True)

        cpd = estimator.estimate_cpd(node, weighted=False)
        cpd_values = np.asarray(cpd.get_values(), dtype=float)

        if empirical.shape != cpd_values.shape:
            raise CPTReconstructionError(
                f"{node}: shape empírico {empirical.shape} "
                f"!= shape CPT {cpd_values.shape}"
            )

        max_diff = float(np.max(np.abs(empirical - cpd_values)))
        global_max_diff = max(global_max_diff, max_diff)

        if max_diff > ABS_TOL:
            raise CPTReconstructionError(
                f"{node}: CPT no coincide con frecuencias empíricas. "
                f"max_abs_diff={max_diff:.17g}"
            )

        column_sums = cpd_values.sum(axis=0)

        if not np.allclose(
            column_sums,
            1.0,
            atol=ABS_TOL,
            rtol=0.0,
        ):
            raise CPTReconstructionError(
                f"{node}: CPT no normalizada correctamente."
            )

        result.append(
            {
                "node": str(node),
                "parents": [str(parent) for parent in parents],
                "state_names": {
                    str(variable): list(cpd.state_names[variable])
                    for variable in [node] + parents
                },
                "values": cpd_values.tolist(),
            }
        )

    return result, global_max_diff, total_zero_parent_configs


def canonical_bytes(cpts):
    return json.dumps(
        cpts,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(cpts):
    return hashlib.sha256(canonical_bytes(cpts)).hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Reconstruye de manera reproducible las CPT de Proyecto Tenate "
            "sobre el DAG canónico validado en el Subapartado 2.3."
        )
    )
    parser.add_argument(
        "csv",
        type=Path,
        help="Ruta al CSV científico original auditado.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Ruta opcional para escribir la representación canónica de CPT. "
            "Si se omite, solo se valida y calcula su SHA-256."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if pgmpy.__version__ != EXPECTED_PGMPY_VERSION:
        print(
            "ERROR: versión de pgmpy inesperada. "
            f"Esperada={EXPECTED_PGMPY_VERSION}, "
            f"actual={pgmpy.__version__}.",
            file=sys.stderr,
        )
        return 1

    source = args.csv.expanduser().resolve()

    try:
        training, training_sha = prepare_dataset.prepare_dataset(source)
    except prepare_dataset.DatasetPreparationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if training_sha != EXPECTED_TRAINING_SHA256:
        print(
            "ERROR: SHA-256 de entrenamiento inesperado. "
            f"Esperado={EXPECTED_TRAINING_SHA256}, "
            f"actual={training_sha}.",
            file=sys.stderr,
        )
        return 1

    dag, bic_score, tie_events = audit_hillclimb.learn(
        training,
        audit_hillclimb.MODE_CANONICAL,
        trace_ties=False,
    )

    dag_sha = audit_hillclimb.canonical_sha256(dag)

    if dag_sha != EXPECTED_DAG_SHA256:
        print(
            "ERROR: el DAG aprendido no coincide con el DAG canónico "
            "validado en 2.3. "
            f"Esperado={EXPECTED_DAG_SHA256}, "
            f"actual={dag_sha}.",
            file=sys.stderr,
        )
        return 1

    try:
        cpts, max_diff, zero_parent_configs = canonical_cpts(
            dag,
            training,
        )
    except CPTReconstructionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    cpt_payload = canonical_bytes(cpts)
    cpt_sha = hashlib.sha256(cpt_payload).hexdigest()

    if cpt_sha != EXPECTED_CPT_SHA256:
        print(
            "ERROR: SHA-256 canónico de CPT inesperado. "
            f"Esperado={EXPECTED_CPT_SHA256}, "
            f"actual={cpt_sha}.",
            file=sys.stderr,
        )
        return 1

    print("=" * 78)
    print("PROYECTO TENATE — ESTIMACIÓN REPRODUCIBLE DE CPT")
    print("=" * 78)
    print(f"Python                         : {platform.python_version()}")
    print(f"pgmpy                          : {pgmpy.__version__}")
    print("Estimador                      : MaximumLikelihoodEstimator")
    print("weighted                       : False")
    print(f"SHA-256 entrenamiento          : {training_sha}")
    print(f"Nodos DAG                      : {len(dag.nodes())}")
    print(f"Aristas DAG                    : {len(dag.edges())}")
    print(f"BIC DAG                        : {bic_score:.10f}")
    print(f"SHA-256 canónico DAG           : {dag_sha}")
    print(f"Iteraciones con empate         : {tie_events}")
    print(f"CPT estimadas                  : {len(cpts)}")
    print(
        "Configuraciones sin datos      : "
        f"{zero_parent_configs}"
    )
    print(f"Máx. diferencia empírica/CPT   : {max_diff:.17g}")
    print(f"Bytes canónicos CPT            : {len(cpt_payload)}")
    print(f"SHA-256 canónico CPT           : {cpt_sha}")

    if args.output is None:
        print("Archivo CPT                     : NO ESCRITO (modo verificación)")
    else:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(cpt_payload)
        print(f"Archivo CPT                     : {output}")

    print()
    print("RESULTADO: CPT RECONSTRUIDAS Y VALIDADAS CORRECTAMENTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())