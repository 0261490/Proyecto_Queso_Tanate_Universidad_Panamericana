#!/usr/bin/env python3
"""
Validación reproducible de la reconstrucción Bayesiana de Proyecto Tenate.

Este módulo NO intenta modificar el DAG ni las CPT para forzar coincidencia
con la publicación. Compara, de forma explícita y trazable:

1. estructura reconstruida vs. Fig. 1 publicada;
2. probabilidades marginales empíricas vs. porcentajes mostrados en Fig. 1;
3. inferencia exacta reconstruida para P(Q2 | Q8=Yes) vs. referencia publicada;
4. opcionalmente, validación cruzada 10-fold reconstruida de Q2.

La metodología publicada no documenta todos los detalles necesarios para una
reproducción exacta de sus métricas predictivas; por eso los resultados de este
script se reportan como "reconstruidos", no como "reproducidos".
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import networkx as nx
import numpy as np
import pgmpy
import sklearn
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold

import audit_hillclimb
import prepare_dataset


EXPECTED_PGMPY_VERSION = "1.1.2"
EXPECTED_SKLEARN_VERSION = "1.9.0"
EXPECTED_TRAINING_SHA256 = (
    "c8eb4a4e2107fde5817f87481db1a59485cf82e1ec41e9d42a672b578bb033e5"
)
EXPECTED_DAG_SHA256 = (
    "11fb5b49d2d51e4508563e4ba4b1d07eba1e36cf0e6da36703312c9c08136cdb"
)

TARGET = "Q2_Purchase_Intention"
SENSORY = "Q8_Sensory_Uniqueness"

PUBLISHED_POSTERIOR_Q2_YES_GIVEN_Q8_YES = 0.626
PUBLISHED_POSTERIOR_Q2_NO_GIVEN_Q8_YES = 0.374

PUBLISHED_CV = {
    "accuracy": 0.842,
    "log_loss": 0.32,
    "auc_roc": 0.89,
}

# Lectura dirigida de la Fig. 1 de la publicación.
# Se conserva separada de la descripción narrativa del artículo porque ambas
# representaciones no son completamente consistentes entre sí.
PUBLISHED_FIG1_EDGES = frozenset(
    {
        ("Age", "Q1_Traditional_Mexican"),
        ("Standardized_City", "Q1_Traditional_Mexican"),
        ("Q1_Traditional_Mexican", "Q4_Gastronomic_Heritage"),
        ("Q7_Culture_Preservation", "Q4_Gastronomic_Heritage"),
        ("Gender", "Q4_Gastronomic_Heritage"),
        ("Q5_Authenticity_Elaboration", "Q4_Gastronomic_Heritage"),
        ("Q4_Gastronomic_Heritage", TARGET),
        ("Q5_Authenticity_Elaboration", TARGET),
        ("Q6_Commercial_Potential", TARGET),
        (SENSORY, TARGET),
        (TARGET, "Q3_Recommendation"),
    }
)

PUBLISHED_FIG1_PERCENT = {
    "Gender": {
        "Female": 84,
        "Male": 16,
        "Prefiero no dec": 0,
    },
    "Age": {
        "18-21": 70,
        "22-25": 12,
        "26-29": 2,
        "30-34": 2,
        "35-40": 4,
        "41-45": 2,
        "46-50": 2,
        "More than 50": 5,
    },
    "Standardized_City": {
        "Guadalajara": 69,
        "Jalisco (Otro)": 0,
        "No especificado": 9,
        "Otro": 3,
        "Zapopan": 19,
    },
    "Q1_Traditional_Mexican": {"No": 54, "Yes": 46},
    TARGET: {"No": 40, "Yes": 60},
    "Q3_Recommendation": {"No": 68, "Yes": 32},
    "Q4_Gastronomic_Heritage": {"No": 90, "Yes": 10},
    "Q5_Authenticity_Elaboration": {"No": 49, "Yes": 51},
    "Q6_Commercial_Potential": {"No": 51, "Yes": 49},
    "Q7_Culture_Preservation": {"No": 7, "Yes": 93},
    SENSORY: {"No": 25, "Yes": 75},
}

# Nodos que, según la lectura visual de la Fig. 1 usada en esta reconstrucción,
# no tienen flechas entrantes.
PUBLISHED_FIG1_ROOTS_VISUAL = (
    "Age",
    "Gender",
    "Standardized_City",
    "Q5_Authenticity_Elaboration",
    "Q6_Commercial_Potential",
    "Q7_Culture_Preservation",
    SENSORY,
)


@dataclass(frozen=True)
class StructureComparison:
    published_edges: int
    reconstructed_edges: int
    common_edges: int
    only_published: tuple[tuple[str, str], ...]
    only_reconstructed: tuple[tuple[str, str], ...]
    precision: float
    recall: float
    f1: float
    jaccard: float
    symmetric_difference: int
    shd: int


def _sorted_edges(edges: Iterable[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(edges, key=lambda edge: (str(edge[0]), str(edge[1]))))


def compare_structure(dag: nx.DiGraph) -> StructureComparison:
    reconstructed = set(dag.edges())
    published = set(PUBLISHED_FIG1_EDGES)

    common = reconstructed & published
    only_published = published - reconstructed
    only_reconstructed = reconstructed - published

    precision = len(common) / len(reconstructed) if reconstructed else 0.0
    recall = len(common) / len(published) if published else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    union = reconstructed | published
    jaccard = len(common) / len(union) if union else 1.0

    # Para estas dos estructuras no hay pares comunes con orientación opuesta.
    # Por tanto, el SHD coincide con altas/bajas necesarias.
    pub_pairs = {frozenset(edge) for edge in published}
    rec_pairs = {frozenset(edge) for edge in reconstructed}
    reversed_pairs = 0
    for pair in pub_pairs & rec_pairs:
        u, v = tuple(pair)
        if ((u, v) in published) != ((u, v) in reconstructed):
            reversed_pairs += 1

    pub_only_pairs = pub_pairs - rec_pairs
    rec_only_pairs = rec_pairs - pub_pairs
    shd = len(pub_only_pairs) + len(rec_only_pairs) + reversed_pairs

    return StructureComparison(
        published_edges=len(published),
        reconstructed_edges=len(reconstructed),
        common_edges=len(common),
        only_published=_sorted_edges(only_published),
        only_reconstructed=_sorted_edges(only_reconstructed),
        precision=precision,
        recall=recall,
        f1=f1,
        jaccard=jaccard,
        symmetric_difference=len(published ^ reconstructed),
        shd=shd,
    )


def empirical_fig1_comparison(training):
    result = {}
    for variable, published_states in PUBLISHED_FIG1_PERCENT.items():
        states = {}
        all_round = True
        for state, published_percent in published_states.items():
            empirical = 100.0 * float((training[variable] == state).mean())
            rounds_equal = round(empirical) == published_percent
            all_round = all_round and rounds_equal
            states[state] = {
                "empirical_percent": empirical,
                "published_percent": float(published_percent),
                "difference_pp": empirical - float(published_percent),
                "rounds_equal": rounds_equal,
            }

        result[variable] = {
            "states": states,
            "distribution_rounds_equal": all_round,
        }
    return result


def build_pgmpy_model(dag: nx.DiGraph, training) -> DiscreteBayesianNetwork:
    model = DiscreteBayesianNetwork(list(dag.edges()))
    model.add_nodes_from(dag.nodes())

    estimator = MaximumLikelihoodEstimator(model, training)
    cpds = [
        estimator.estimate_cpd(node, weighted=False)
        for node in sorted(model.nodes(), key=str)
    ]
    model.add_cpds(*cpds)

    if not model.check_model():
        raise RuntimeError("El modelo pgmpy no pasó check_model().")

    return model


def probability_of_state(factor, variable: str, state: str) -> float:
    states = factor.state_names[variable]
    return float(factor.values[states.index(state)])


def full_model_probability_validation(training, dag):
    model = build_pgmpy_model(dag, training)
    infer = VariableElimination(model)

    prior = infer.query(
        variables=[TARGET],
        show_progress=False,
    )
    posterior = infer.query(
        variables=[TARGET],
        evidence={SENSORY: "Yes"},
        show_progress=False,
    )

    prior_yes = probability_of_state(prior, TARGET, "Yes")
    posterior_yes = probability_of_state(posterior, TARGET, "Yes")
    posterior_no = probability_of_state(posterior, TARGET, "No")

    return {
        "prior_q2_yes": prior_yes,
        "posterior_q2_yes_given_q8_yes": posterior_yes,
        "posterior_q2_no_given_q8_yes": posterior_no,
        "posterior_equals_prior": bool(
            np.isclose(prior_yes, posterior_yes, rtol=0.0, atol=1e-15)
        ),
        "difference_vs_published_probability": (
            posterior_yes - PUBLISHED_POSTERIOR_Q2_YES_GIVEN_Q8_YES
        ),
        "difference_vs_published_pp": (
            100.0
            * (posterior_yes - PUBLISHED_POSTERIOR_Q2_YES_GIVEN_Q8_YES)
        ),
        "relative_error_vs_published": (
            abs(posterior_yes - PUBLISHED_POSTERIOR_Q2_YES_GIVEN_Q8_YES)
            / PUBLISHED_POSTERIOR_Q2_YES_GIVEN_Q8_YES
        ),
        "q8_degree": int(dag.degree(SENSORY)),
        "q8_parents": tuple(sorted(dag.predecessors(SENSORY), key=str)),
        "q8_children": tuple(sorted(dag.successors(SENSORY), key=str)),
        "path_q8_to_q2": bool(nx.has_path(dag, SENSORY, TARGET)),
        "path_q2_to_q8": bool(nx.has_path(dag, TARGET, SENSORY)),
    }


def _metrics(y_true, probabilities):
    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    predictions = (probabilities >= 0.5).astype(int)

    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "log_loss": float(
            log_loss(
                y_true,
                np.column_stack([1.0 - probabilities, probabilities]),
                labels=[0, 1],
            )
        ),
        "auc_roc": float(roc_auc_score(y_true, probabilities)),
    }


def cross_validate_q2(training):
    y = training[TARGET]
    cv = StratifiedKFold(
        n_splits=10,
        shuffle=True,
        random_state=42,
    )

    pooled_true = []
    pooled_blanket = []
    pooled_parents = []

    fold_results = []

    for fold_number, (train_idx, test_idx) in enumerate(
        cv.split(training, y),
        start=1,
    ):
        train = training.iloc[train_idx].reset_index(drop=True)
        test = training.iloc[test_idx].reset_index(drop=True)

        dag, _score, _ties = audit_hillclimb.learn(
            train,
            audit_hillclimb.MODE_CANONICAL,
            trace_ties=False,
        )

        model = build_pgmpy_model(dag, train)
        infer = VariableElimination(model)

        parents = tuple(sorted(dag.get_parents(TARGET), key=str))
        blanket = tuple(sorted(dag.get_markov_blanket(TARGET), key=str))

        fold_true = []
        fold_blanket = []
        fold_parents = []

        for _, row in test.iterrows():
            truth = 1 if row[TARGET] == "Yes" else 0
            fold_true.append(truth)

            evidence_blanket = {}
            for variable in blanket:
                state = row[variable]
                known_states = model.get_cpds(variable).state_names[variable]
                if state not in known_states:
                    raise ValueError(
                        f"Fold {fold_number}: estado de test no visto en train "
                        f"para variable relevante {variable!r}: {state!r}"
                    )
                evidence_blanket[variable] = state

            query_blanket = infer.query(
                variables=[TARGET],
                evidence=evidence_blanket,
                show_progress=False,
            )
            fold_blanket.append(
                probability_of_state(query_blanket, TARGET, "Yes")
            )

            evidence_parents = {}
            for variable in parents:
                state = row[variable]
                known_states = model.get_cpds(variable).state_names[variable]
                if state not in known_states:
                    raise ValueError(
                        f"Fold {fold_number}: estado de test no visto en train "
                        f"para padre {variable!r}: {state!r}"
                    )
                evidence_parents[variable] = state

            query_parents = infer.query(
                variables=[TARGET],
                evidence=evidence_parents,
                show_progress=False,
            )
            fold_parents.append(
                probability_of_state(query_parents, TARGET, "Yes")
            )

        blanket_metrics = _metrics(fold_true, fold_blanket)
        parents_metrics = _metrics(fold_true, fold_parents)

        fold_results.append(
            {
                "fold": fold_number,
                "train_n": len(train),
                "test_n": len(test),
                "edge_count": len(dag.edges()),
                "q2_parents": parents,
                "q2_children": tuple(
                    sorted(dag.get_children(TARGET), key=str)
                ),
                "q2_markov_blanket": blanket,
                "blanket_metrics": blanket_metrics,
                "parents_metrics": parents_metrics,
            }
        )

        pooled_true.extend(fold_true)
        pooled_blanket.extend(fold_blanket)
        pooled_parents.extend(fold_parents)

    pooled_blanket_metrics = _metrics(pooled_true, pooled_blanket)
    pooled_parents_metrics = _metrics(pooled_true, pooled_parents)

    mean_blanket = {
        key: float(np.mean([fold["blanket_metrics"][key] for fold in fold_results]))
        for key in ("accuracy", "log_loss", "auc_roc")
    }
    std_blanket = {
        key: float(np.std([fold["blanket_metrics"][key] for fold in fold_results]))
        for key in ("accuracy", "log_loss", "auc_roc")
    }

    return {
        "policy": {
            "n_splits": 10,
            "shuffle": True,
            "random_state": 42,
            "structure_learning": "canonical Hill-Climbing + bic-d per fold",
            "cpt_estimation": "MaximumLikelihoodEstimator, weighted=False",
        },
        "folds": tuple(fold_results),
        "pooled_blanket": pooled_blanket_metrics,
        "pooled_parents": pooled_parents_metrics,
        "mean_blanket": mean_blanket,
        "std_blanket": std_blanket,
    }


def _print_structure(result: StructureComparison):
    print("=== VALIDACION ESTRUCTURAL VS FIG. 1 ===")
    print(f"Aristas publicadas       : {result.published_edges}")
    print(f"Aristas reconstruidas    : {result.reconstructed_edges}")
    print(f"Coincidentes             : {result.common_edges}")
    print(f"Precision                : {result.precision:.12f}")
    print(f"Recall                   : {result.recall:.12f}")
    print(f"F1                       : {result.f1:.12f}")
    print(f"Jaccard                  : {result.jaccard:.12f}")
    print(f"Diferencia simetrica     : {result.symmetric_difference}")
    print(f"SHD                      : {result.shd}")
    print("Solo publicadas:")
    for edge in result.only_published:
        print(f"  {edge[0]} -> {edge[1]}")
    print("Solo reconstruidas:")
    for edge in result.only_reconstructed:
        print(f"  {edge[0]} -> {edge[1]}")
    print()


def _print_marginals(result):
    print("=== CSV EMPIRICO VS PORCENTAJES DE FIG. 1 ===")
    matches = []
    mismatches = []

    for variable, info in result.items():
        ok = info["distribution_rounds_equal"]
        print(f"{variable}: coincide_al_redondear={ok}")
        (matches if ok else mismatches).append(variable)

    print(f"Coinciden: {len(matches)} de {len(result)}")
    print("Lista que coincide:", matches)
    print("Lista que no coincide:", mismatches)

    root_matches = [
        var
        for var in PUBLISHED_FIG1_ROOTS_VISUAL
        if result[var]["distribution_rounds_equal"]
    ]
    print()
    print("Raices segun lectura visual de Fig. 1:")
    print(f"Coinciden: {len(root_matches)} de {len(PUBLISHED_FIG1_ROOTS_VISUAL)}")
    print("Lista:", root_matches)
    print()


def _print_probability(result):
    print("=== VALIDACION PROBABILISTICA ===")
    print(f"P(Q2=Yes) reconstruido                 : {result['prior_q2_yes']:.12f}")
    print(
        "P(Q2=Yes | Q8=Yes) reconstruido       : "
        f"{result['posterior_q2_yes_given_q8_yes']:.12f}"
    )
    print(
        "P(Q2=No  | Q8=Yes) reconstruido       : "
        f"{result['posterior_q2_no_given_q8_yes']:.12f}"
    )
    print(
        "P(Q2=Yes | Q8=Yes) publicado          : "
        f"{PUBLISHED_POSTERIOR_Q2_YES_GIVEN_Q8_YES:.12f}"
    )
    print(
        "Diferencia reconstruido-publicado     : "
        f"{result['difference_vs_published_pp']:+.6f} pp"
    )
    print(f"Posterior = prior                      : {result['posterior_equals_prior']}")
    print(f"Grado total Q8                        : {result['q8_degree']}")
    print(f"Camino Q8 -> Q2                       : {result['path_q8_to_q2']}")
    print(f"Camino Q2 -> Q8                       : {result['path_q2_to_q8']}")
    print()


def _print_cv(result):
    print("=== VALIDACION 10-FOLD RECONSTRUIDA DE Q2 ===")
    print("StratifiedKFold(n_splits=10, shuffle=True, random_state=42)")
    print()

    for fold in result["folds"]:
        metrics = fold["blanket_metrics"]
        print(
            f"Fold {fold['fold']}: "
            f"train={fold['train_n']} test={fold['test_n']} "
            f"aristas={fold['edge_count']} "
            f"padres={list(fold['q2_parents'])} "
            f"blanket={list(fold['q2_markov_blanket'])} "
            f"| Accuracy={100.0 * metrics['accuracy']:.6f}% "
            f"Log-loss={metrics['log_loss']:.6f} "
            f"AUC={metrics['auc_roc']:.6f}"
        )

    print()
    print("Markov blanket — pooled 169 casos:")
    print(f"  Accuracy : {100.0 * result['pooled_blanket']['accuracy']:.12f}%")
    print(f"  Log-loss : {result['pooled_blanket']['log_loss']:.12f}")
    print(f"  AUC-ROC  : {result['pooled_blanket']['auc_roc']:.12f}")

    print()
    print("Markov blanket — promedio 10 folds:")
    print(f"  Accuracy : {100.0 * result['mean_blanket']['accuracy']:.12f}%")
    print(f"  Log-loss : {result['mean_blanket']['log_loss']:.12f}")
    print(f"  AUC-ROC  : {result['mean_blanket']['auc_roc']:.12f}")

    print()
    print("Markov blanket — desviacion estandar entre folds:")
    print(f"  Accuracy : {100.0 * result['std_blanket']['accuracy']:.12f} pp")
    print(f"  Log-loss : {result['std_blanket']['log_loss']:.12f}")
    print(f"  AUC-ROC  : {result['std_blanket']['auc_roc']:.12f}")

    print()
    print("Solo padres — pooled 169 casos:")
    print(f"  Accuracy : {100.0 * result['pooled_parents']['accuracy']:.12f}%")
    print(f"  Log-loss : {result['pooled_parents']['log_loss']:.12f}")
    print(f"  AUC-ROC  : {result['pooled_parents']['auc_roc']:.12f}")

    print()
    print("Referencia publicada:")
    print(f"  Accuracy : {100.0 * PUBLISHED_CV['accuracy']:.2f}%")
    print(f"  Log-loss : {PUBLISHED_CV['log_loss']:.2f}")
    print(f"  AUC-ROC  : {PUBLISHED_CV['auc_roc']:.2f}")
    print()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Valida la reconstruccion Bayesiana de Proyecto Tenate."
    )
    parser.add_argument(
        "source_csv",
        type=Path,
        help="CSV fuente verificado usado por prepare_dataset.py",
    )
    parser.add_argument(
        "--cross-validation",
        action="store_true",
        help="Ejecuta adicionalmente la validacion reconstruida 10-fold de Q2.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if pgmpy.__version__ != EXPECTED_PGMPY_VERSION:
        print(
            "ERROR: versión de pgmpy inesperada. "
            f"Esperada={EXPECTED_PGMPY_VERSION}, actual={pgmpy.__version__}."
        )
        return 1

    if sklearn.__version__ != EXPECTED_SKLEARN_VERSION:
        print(
            "ERROR: versión de scikit-learn inesperada. "
            f"Esperada={EXPECTED_SKLEARN_VERSION}, actual={sklearn.__version__}."
        )
        return 1

    try:
        training, training_sha = prepare_dataset.prepare_dataset(args.source_csv)
    except prepare_dataset.DatasetPreparationError as exc:
        print(f"ERROR: {exc}")
        return 1

    if training_sha != EXPECTED_TRAINING_SHA256:
        print(
            "ERROR: SHA-256 de entrenamiento inesperado. "
            f"Esperado={EXPECTED_TRAINING_SHA256}, actual={training_sha}."
        )
        return 1

    dag, _score, _ties = audit_hillclimb.learn(
        training,
        audit_hillclimb.MODE_CANONICAL,
        trace_ties=False,
    )

    dag_sha = audit_hillclimb.canonical_sha256(dag)
    if dag_sha != EXPECTED_DAG_SHA256:
        print(
            "ERROR: el DAG no coincide con la estructura canónica validada. "
            f"Esperado={EXPECTED_DAG_SHA256}, actual={dag_sha}."
        )
        return 1

    print("=== ENTORNO ===")
    print(f"pgmpy       : {pgmpy.__version__}")
    print(f"scikit-learn: {sklearn.__version__}")
    print(f"Filas        : {len(training)}")
    print(f"Variables    : {len(training.columns)}")
    print()

    structure = compare_structure(dag)
    marginals = empirical_fig1_comparison(training)
    probability = full_model_probability_validation(training, dag)

    _print_structure(structure)
    _print_marginals(marginals)
    _print_probability(probability)

    if args.cross_validation:
        cv_result = cross_validate_q2(training)
        _print_cv(cv_result)

    print("RESULTADO: VALIDACIÓN ESTRUCTURAL Y PROBABILÍSTICA COMPLETADA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
