#!/usr/bin/env python3
"""Exporta la reconstrucción Bayesiana canónica de Proyecto Tenate a JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import pgmpy

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_SOURCE = REPO_ROOT / "model-source"

if str(MODEL_SOURCE) not in sys.path:
    sys.path.insert(0, str(MODEL_SOURCE))

import audit_hillclimb  # noqa: E402
import estimate_cpts  # noqa: E402
import prepare_dataset  # noqa: E402


FORMAT_NAME = "proyecto-tenate-bayesian-model"
SCHEMA_VERSION = 1
MODEL_VERSION = "1.0.0"
EXPECTED_PGMPY_VERSION = "1.1.2"


class ModelExportError(RuntimeError):
    """El modelo no puede exportarse sin violar sus invariantes."""


def canonical_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(payload: dict) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def build_payload(
    *,
    source_sha256: str,
    training_sha256: str,
    training,
    dag,
    bic_score: float,
    tie_events: int,
    cpts: list[dict],
) -> dict:
    by_node = {item["node"]: item for item in cpts}
    nodes = []
    for node in sorted(dag.nodes(), key=str):
        item = by_node[str(node)]
        nodes.append(
            {
                "id": str(node),
                "states": list(item["state_names"][str(node)]),
            }
        )

    return {
        "format": FORMAT_NAME,
        "schema_version": SCHEMA_VERSION,
        "model_version": MODEL_VERSION,
        "metadata": {
            "scientific_status": (
                "Reproducible reconstruction derived from the audited CSV; "
                "not an exact recovery of the published original model."
            ),
            "source": {
                "sha256": source_sha256,
                "records": int(len(training)),
                "original_columns": len(prepare_dataset.SOURCE_COLUMNS),
                "excluded_columns": ["Judge_ID"],
            },
            "training": {
                "sha256": training_sha256,
                "records": int(len(training)),
                "variables": int(len(training.columns)),
            },
            "learning": {
                "algorithm": "Hill-Climbing",
                "score": audit_hillclimb.SCORING_METHOD,
                "bic": float(bic_score),
                "tie_breaking": "canonical operation order",
                "tie_events": int(tie_events),
                "dag_sha256": audit_hillclimb.canonical_sha256(dag),
            },
            "parameters": {
                "estimator": "MaximumLikelihoodEstimator",
                "weighted": False,
                "cpt_sha256": estimate_cpts.canonical_sha256(cpts),
            },
            "software": {
                "python": platform.python_version(),
                "pgmpy": pgmpy.__version__,
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "networkx": nx.__version__,
            },
        },
        "nodes": nodes,
        "edges": [
            {"source": str(source), "target": str(target)}
            for source, target in sorted(dag.edges(), key=lambda edge: tuple(map(str, edge)))
        ],
        "cpts": cpts,
    }


def validate_payload(payload: dict) -> None:
    if payload.get("format") != FORMAT_NAME:
        raise ModelExportError("Formato de modelo inválido.")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ModelExportError("Versión de esquema inválida.")

    nodes = payload.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise ModelExportError("El modelo no contiene nodos.")

    node_ids = [item.get("id") for item in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ModelExportError("Existen identificadores de nodo duplicados.")

    node_states = {}
    for item in nodes:
        states = item.get("states")
        if not isinstance(states, list) or not states or len(states) != len(set(states)):
            raise ModelExportError(f"Estados inválidos para {item.get('id')!r}.")
        node_states[item["id"]] = states

    dag = nx.DiGraph()
    dag.add_nodes_from(node_ids)
    for edge in payload.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_states or target not in node_states:
            raise ModelExportError(f"Arista con nodo desconocido: {edge!r}")
        dag.add_edge(source, target)

    if not nx.is_directed_acyclic_graph(dag):
        raise ModelExportError("La estructura exportada no es un DAG.")

    cpts = payload.get("cpts")
    if not isinstance(cpts, list) or len(cpts) != len(node_ids):
        raise ModelExportError("Debe existir exactamente una CPT por nodo.")

    cpt_nodes = [item.get("node") for item in cpts]
    if set(cpt_nodes) != set(node_ids) or len(cpt_nodes) != len(set(cpt_nodes)):
        raise ModelExportError("La cobertura de nodos en las CPT es inválida.")

    for item in cpts:
        node = item["node"]
        parents = item.get("parents")
        expected_parents = sorted(dag.predecessors(node), key=str)
        if parents != expected_parents:
            raise ModelExportError(f"Padres inconsistentes en CPT de {node}.")

        state_names = item.get("state_names", {})
        if state_names.get(node) != node_states[node]:
            raise ModelExportError(f"Estados inconsistentes en CPT de {node}.")

        columns = 1
        for parent in parents:
            if state_names.get(parent) != node_states[parent]:
                raise ModelExportError(
                    f"Estados del padre {parent} inconsistentes en CPT de {node}."
                )
            columns *= len(node_states[parent])

        values = np.asarray(item.get("values"), dtype=float)
        expected_shape = (len(node_states[node]), columns)
        if values.shape != expected_shape:
            raise ModelExportError(
                f"Shape inválido en CPT de {node}: {values.shape} != {expected_shape}."
            )
        if not np.isfinite(values).all() or (values < 0.0).any() or (values > 1.0).any():
            raise ModelExportError(f"Probabilidades inválidas en CPT de {node}.")
        if not np.allclose(values.sum(axis=0), 1.0, atol=1e-15, rtol=0.0):
            raise ModelExportError(f"CPT no normalizada para {node}.")

    metadata = payload.get("metadata", {})
    if metadata.get("learning", {}).get("dag_sha256") != audit_hillclimb.canonical_sha256(dag):
        raise ModelExportError("El hash del DAG no coincide con el contenido.")
    if metadata.get("parameters", {}).get("cpt_sha256") != estimate_cpts.canonical_sha256(cpts):
        raise ModelExportError("El hash de CPT no coincide con el contenido.")


def reconstruct(source_csv: Path) -> dict:
    if pgmpy.__version__ != EXPECTED_PGMPY_VERSION:
        raise ModelExportError(
            f"pgmpy inesperado: {pgmpy.__version__}; esperado: {EXPECTED_PGMPY_VERSION}."
        )

    source_csv = source_csv.expanduser().resolve()
    source_sha256 = prepare_dataset.sha256_file(source_csv)
    training, training_sha256 = prepare_dataset.prepare_dataset(source_csv)

    if training_sha256 != estimate_cpts.EXPECTED_TRAINING_SHA256:
        raise ModelExportError("El hash del dataset de entrenamiento no coincide.")

    dag, bic_score, tie_events = audit_hillclimb.learn(
        training,
        audit_hillclimb.MODE_CANONICAL,
        trace_ties=False,
    )
    if audit_hillclimb.canonical_sha256(dag) != estimate_cpts.EXPECTED_DAG_SHA256:
        raise ModelExportError("El DAG reconstruido no coincide con el DAG congelado.")

    cpts, _max_diff, zero_parent_configs = estimate_cpts.canonical_cpts(dag, training)
    if zero_parent_configs:
        raise ModelExportError("Existen configuraciones de padres sin datos.")
    if estimate_cpts.canonical_sha256(cpts) != estimate_cpts.EXPECTED_CPT_SHA256:
        raise ModelExportError("Las CPT no coinciden con las CPT congeladas.")

    payload = build_payload(
        source_sha256=source_sha256,
        training_sha256=training_sha256,
        training=training,
        dag=dag,
        bic_score=bic_score,
        tie_events=tie_events,
        cpts=cpts,
    )
    validate_payload(payload)
    return payload


def parse_args():
    parser = argparse.ArgumentParser(
        description="Exporta el modelo Bayesiano reproducible de Proyecto Tenate."
    )
    parser.add_argument("source_csv", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("model.json"),
    )
    parser.add_argument(
        "--hash-output",
        type=Path,
        default=Path(__file__).with_name("model.sha256"),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        payload = reconstruct(args.source_csv)
    except (ModelExportError, prepare_dataset.DatasetPreparationError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    model_bytes = canonical_bytes(payload)
    model_sha256 = hashlib.sha256(model_bytes).hexdigest()

    output = args.output.expanduser().resolve()
    hash_output = args.hash_output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    hash_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(model_bytes)
    hash_output.write_text(f"{model_sha256}  {output.name}\n", encoding="utf-8", newline="\n")

    print(f"Modelo JSON       : {output}")
    print(f"Bytes             : {len(model_bytes)}")
    print(f"SHA-256 modelo    : {model_sha256}")
    print(f"Hash sidecar      : {hash_output}")
    print("RESULTADO: MODELO EXPORTADO Y VALIDADO CORRECTAMENTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
