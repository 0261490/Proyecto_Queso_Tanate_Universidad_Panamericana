#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

import pgmpy
from pgmpy.estimators import BIC, HillClimbSearch
from pgmpy.utils import get_dataset_type

import prepare_dataset

SCORING_METHOD = "bic-d"
TABU_LENGTH = 100
MAX_INDEGREE = None
EPSILON = 1e-4
MAX_ITER = 1_000_000
USE_CACHE = True
SHOW_PROGRESS = False

MODE_PGMPY = "pgmpy"
MODE_CANONICAL = "canonical"
SUPPORTED_MODES = (MODE_PGMPY, MODE_CANONICAL)


def operation_key(item):
    operation, _delta = item
    op_type, (source, target) = operation
    order = {"+": 0, "-": 1, "flip": 2}
    return (order.get(op_type, 99), str(source), str(target))


class AuditedHillClimbSearch(HillClimbSearch):
    def __init__(self, data, *, mode=MODE_PGMPY, trace_ties=False, use_cache=True):
        if mode not in SUPPORTED_MODES:
            raise ValueError(f"Modo inválido: {mode}")
        super().__init__(data, use_cache=use_cache)
        self.mode = mode
        self.trace_ties = trace_ties
        self.call_number = 0
        self.tie_events = 0

    def _legal_operations(self, *args, **kwargs):
        self.call_number += 1
        operations = list(super()._legal_operations(*args, **kwargs))

        if operations:
            best_delta = max(item[1] for item in operations)
            winners = [item for item in operations if item[1] == best_delta]

            if len(winners) > 1:
                self.tie_events += 1
                if self.trace_ties:
                    print()
                    print(
                        f"[EMPATE] iteración={self.call_number} "
                        f"score_delta={best_delta:.15f} "
                        f"candidatos={len(winners)}"
                    )
                    for operation, delta in sorted(winners, key=operation_key):
                        print(f"  {operation!r} score_delta={delta:.15f}")

        if self.mode == MODE_CANONICAL:
            operations.sort(key=operation_key)

        yield from operations


def canonical_payload(dag):
    return {
        "nodes": sorted(str(node) for node in dag.nodes()),
        "edges": sorted((str(a), str(b)) for a, b in dag.edges()),
    }


def canonical_sha256(dag):
    raw = json.dumps(
        canonical_payload(dag),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def learn(training, mode, trace_ties):
    estimator = AuditedHillClimbSearch(
        training,
        mode=mode,
        trace_ties=trace_ties,
        use_cache=USE_CACHE,
    )
    dag = estimator.estimate(
        scoring_method=SCORING_METHOD,
        start_dag=None,
        tabu_length=TABU_LENGTH,
        max_indegree=MAX_INDEGREE,
        expert_knowledge=None,
        epsilon=EPSILON,
        max_iter=MAX_ITER,
        show_progress=SHOW_PROGRESS,
    )
    return dag, float(BIC(training).score(dag)), estimator.tie_events


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--mode", choices=SUPPORTED_MODES, default=MODE_PGMPY)
    parser.add_argument("--trace-ties", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.runs < 1:
        print("ERROR: --runs debe ser >= 1.", file=sys.stderr)
        return 2

    source = args.csv.expanduser().resolve()
    try:
        training, training_sha = prepare_dataset.prepare_dataset(source)
    except prepare_dataset.DatasetPreparationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("=" * 78)
    print("PROYECTO TENATE — AUDITORÍA HILL-CLIMBING + BIC")
    print("=" * 78)
    print(f"Python                  : {platform.python_version()}")
    print(f"pgmpy                   : {pgmpy.__version__}")
    print(f"PYTHONHASHSEED          : {os.environ.get('PYTHONHASHSEED', '<no definido>')}")
    print(f"Modo                    : {args.mode}")
    print(f"Trazar empates          : {args.trace_ties}")
    print(f"SHA-256 entrenamiento   : {training_sha}")
    print(f"Tipo pgmpy detectado    : {get_dataset_type(training)}")

    hashes = []
    scores = []

    for run_number in range(1, args.runs + 1):
        dag, score, ties = learn(training, args.mode, args.trace_ties)
        dag_hash = canonical_sha256(dag)
        hashes.append(dag_hash)
        scores.append(score)

        print()
        print(f"EJECUCIÓN {run_number}")
        print(f"Nodos                   : {len(dag.nodes())}")
        print(f"Aristas                 : {len(dag.edges())}")
        print(f"BIC del DAG             : {score:.10f}")
        print(f"SHA-256 canónico DAG    : {dag_hash}")
        print(f"Iteraciones con empate  : {ties}")
        print("Aristas canónicas:")
        for source_node, target_node in canonical_payload(dag)["edges"]:
            print(f"  {source_node} -> {target_node}")

    print()
    print("RESUMEN")
    print(f"Ejecuciones             : {args.runs}")
    print(f"DAG distintos           : {len(set(hashes))}")
    print(f"BIC distintos           : {len(set(scores))}")
    print(
        "Resultado               : "
        + (
            "MISMO DAG EN TODAS LAS EJECUCIONES"
            if len(set(hashes)) == 1
            else "SE OBTUVIERON DAG DIFERENTES"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
