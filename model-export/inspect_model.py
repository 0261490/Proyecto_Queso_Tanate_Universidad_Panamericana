#!/usr/bin/env python3
"""
Proyecto Tenate — Inspector de modelo científico (solo lectura).

Objetivo:
- Recibir el archivo original de la Red Bayesiana cuando esté disponible.
- Calcular SHA-256 antes de cualquier transformación.
- Cargar formatos compatibles sin modificar el modelo.
- Reportar nodos, aristas, estados y CPDs.
- Ejecutar, cuando sea posible, la inferencia científica de referencia:
    P(Q2 = Yes | Q8 = Yes)

Este script NO exporta a JSON y NO reentrena el modelo.
"""

from __future__ import annotations

import argparse
import hashlib
import pickle
import sys
from pathlib import Path
from typing import Any

from pgmpy.inference import VariableElimination
from pgmpy.readwrite import BIFReader, XMLBIFReader, XDSLReader


Q2_CANDIDATES = ("Q2_Purchase_Intention", "Q2")
Q8_CANDIDATES = ("Q8_Sensory_Uniqueness", "Q8")


def sha256_file(path: Path) -> str:
    """Calcula el SHA-256 del archivo sin modificarlo."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_model(path: Path, allow_pickle: bool = False) -> tuple[Any, str]:
    """
    Carga un modelo en función de su extensión.

    Pickle se bloquea por defecto porque deserializar un .pkl puede ejecutar
    código. Solo debe habilitarse para un archivo cuya procedencia sea confiable.
    """
    suffix = path.suffix.lower()

    if suffix == ".bif":
        return BIFReader(path=str(path)).get_model(), "BIFReader"

    if suffix == ".xdsl":
        return XDSLReader(path=str(path)).get_model(), "XDSLReader"

    if suffix == ".xml":
        return XMLBIFReader(path=str(path)).get_model(), "XMLBIFReader"

    if suffix in {".pkl", ".pickle"}:
        if not allow_pickle:
            raise RuntimeError(
                "Carga de pickle bloqueada. Si el archivo proviene directamente "
                "de una fuente confiable, vuelve a ejecutar con --allow-pickle."
            )
        with path.open("rb") as handle:
            return pickle.load(handle), "pickle"

    raise ValueError(
        f"Formato no soportado actualmente: {suffix or '[sin extensión]'}. "
        "Formatos preparados: .bif, .xdsl, .xml, .pkl y .pickle."
    )


def find_node(nodes: list[Any], candidates: tuple[str, ...]) -> Any | None:
    """Busca un nodo por nombre exacto o comparación insensible a mayúsculas."""
    by_text = {str(node): node for node in nodes}

    for candidate in candidates:
        if candidate in by_text:
            return by_text[candidate]

    lower_map = {str(node).lower(): node for node in nodes}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]

    return None


def find_state(state_names: list[Any], desired: str) -> Any | None:
    """Busca un estado como Yes/No sin asumir capitalización."""
    for state in state_names:
        if str(state).strip().lower() == desired.lower():
            return state
    return None


def get_node_states(model: Any, node: Any) -> list[Any]:
    """
    Obtiene estados desde la CPD del nodo.
    No inventa estados si el modelo no los expone.
    """
    cpd = model.get_cpds(node)
    if cpd is None:
        return []

    state_names = getattr(cpd, "state_names", None) or {}
    if node in state_names:
        return list(state_names[node])

    node_text = str(node)
    if node_text in state_names:
        return list(state_names[node_text])

    return []


def print_header(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def audit_model(path: Path, model: Any, loader_name: str) -> bool:
    """Imprime la auditoría. Devuelve True si las validaciones básicas pasan."""
    overall_ok = True

    print_header("PROYECTO TENATE — AUDITORÍA DE MODELO CIENTÍFICO (SOLO LECTURA)")
    print(f"Archivo       : {path}")
    print(f"Tamaño        : {path.stat().st_size} bytes")
    print(f"SHA-256       : {sha256_file(path)}")
    print(f"Cargador      : {loader_name}")
    print(f"Tipo Python   : {type(model).__module__}.{type(model).__name__}")

    required_methods = ("nodes", "edges", "get_cpds")
    missing = [name for name in required_methods if not hasattr(model, name)]
    if missing:
        print(f"Interfaz modelo: ERROR — faltan métodos: {', '.join(missing)}")
        return False

    if hasattr(model, "check_model"):
        try:
            check_result = model.check_model()
            print(f"check_model() : OK ({check_result})")
        except Exception as exc:  # noqa: BLE001
            overall_ok = False
            print(f"check_model() : ERROR — {type(exc).__name__}: {exc}")
    else:
        overall_ok = False
        print("check_model() : NO DISPONIBLE")

    nodes = list(model.nodes())
    edges = list(model.edges())
    cpds = list(model.get_cpds())

    print_header(f"NODOS ({len(nodes)})")
    for index, node in enumerate(nodes, start=1):
        states = get_node_states(model, node)
        print(f"{index:02d}. {node!s}")
        print(f"    estados: {states if states else '[no disponibles]'}")

    print_header(f"ARISTAS / DAG ({len(edges)})")
    for index, (source, target) in enumerate(edges, start=1):
        print(f"{index:02d}. {source} -> {target}")

    print_header(f"CPDs ({len(cpds)})")
    if len(cpds) != len(nodes):
        overall_ok = False
        print(
            f"ADVERTENCIA: hay {len(nodes)} nodos pero {len(cpds)} CPDs. "
            "Esto requiere revisión científica."
        )

    for index, cpd in enumerate(cpds, start=1):
        variable = getattr(cpd, "variable", None)
        evidence = list(cpd.get_evidence()) if hasattr(cpd, "get_evidence") else []
        cardinality = getattr(cpd, "cardinality", None)
        state_names = getattr(cpd, "state_names", None)

        valid_text = "NO COMPROBADO"
        if hasattr(cpd, "is_valid_cpd"):
            try:
                valid_text = "OK" if bool(cpd.is_valid_cpd()) else "ERROR"
                if valid_text == "ERROR":
                    overall_ok = False
            except Exception as exc:  # noqa: BLE001
                overall_ok = False
                valid_text = f"ERROR ({type(exc).__name__}: {exc})"

        print(f"{index:02d}. CPD de: {variable}")
        print(f"    padres/evidencia: {evidence}")
        print(f"    cardinalidad    : {cardinality}")
        print(f"    estados         : {state_names}")
        print(f"    CPD válida      : {valid_text}")

    print_header("INFERENCIA CIENTÍFICA DE REFERENCIA")

    q2 = find_node(nodes, Q2_CANDIDATES)
    q8 = find_node(nodes, Q8_CANDIDATES)

    if q2 is None or q8 is None:
        print(
            "NO EJECUTADA: no se localizaron automáticamente ambos nodos Q2 y Q8."
        )
        print(f"Q2 detectado: {q2}")
        print(f"Q8 detectado: {q8}")
    else:
        q8_states = get_node_states(model, q8)
        yes_q8 = find_state(q8_states, "Yes")

        if yes_q8 is None:
            print(
                f"NO EJECUTADA: Q8 fue detectado como '{q8}', pero no se encontró "
                f"un estado equivalente a 'Yes'. Estados: {q8_states}"
            )
        else:
            try:
                inference = VariableElimination(model)
                result = inference.query(
                    variables=[q2],
                    evidence={q8: yes_q8},
                    show_progress=False,
                )

                result_state_names = getattr(result, "state_names", {}) or {}
                q2_states = list(result_state_names.get(q2, []))
                yes_q2 = find_state(q2_states, "Yes")
                no_q2 = find_state(q2_states, "No")

                print(f"Evidencia: {q8} = {yes_q8}")
                print(f"Objetivo : {q2}")
                print(f"Estados  : {q2_states}")

                if yes_q2 is not None:
                    p_yes = float(result.get_value(**{str(q2): yes_q2}))
                    print(f"P({q2} = {yes_q2} | {q8} = {yes_q8}) = {p_yes:.10f}")
                    print(f"Porcentaje = {p_yes * 100:.4f}%")
                    print("Referencia científica esperada ≈ 62.6%")
                    print(f"Diferencia absoluta = {abs(p_yes * 100 - 62.6):.4f} puntos %")
                else:
                    print("No se encontró un estado 'Yes' para Q2.")

                if no_q2 is not None:
                    p_no = float(result.get_value(**{str(q2): no_q2}))
                    print(f"P({q2} = {no_q2} | {q8} = {yes_q8}) = {p_no:.10f}")
                    print(f"Porcentaje = {p_no * 100:.4f}%")
            except Exception as exc:  # noqa: BLE001
                overall_ok = False
                print(
                    "ERROR durante la inferencia: "
                    f"{type(exc).__name__}: {exc}"
                )

    print_header("RESULTADO DE LA INSPECCIÓN")
    if overall_ok:
        print("Validaciones estructurales básicas: OK")
    else:
        print("Validaciones estructurales básicas: REQUIEREN REVISIÓN")

    print(
        "Nota: este resultado NO autoriza por sí solo el Apartado 2. "
        "La comparación científica final debe documentarse."
    )
    return overall_ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspector de solo lectura para el modelo científico de Proyecto Tenate."
        )
    )
    parser.add_argument(
        "model",
        type=Path,
        help="Ruta al archivo original (.bif, .xdsl, .xml, .pkl o .pickle).",
    )
    parser.add_argument(
        "--allow-pickle",
        action="store_true",
        help=(
            "Permite cargar .pkl/.pickle. Úsalo únicamente con archivos "
            "de procedencia confiable."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path: Path = args.model.expanduser().resolve()

    if not path.exists():
        print(f"ERROR: el archivo no existe: {path}", file=sys.stderr)
        return 2

    if not path.is_file():
        print(f"ERROR: la ruta no corresponde a un archivo: {path}", file=sys.stderr)
        return 2

    try:
        model, loader_name = load_model(path, allow_pickle=args.allow_pickle)
    except Exception as exc:  # noqa: BLE001
        print(
            f"ERROR al cargar el modelo: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 3

    try:
        audit_model(path, model, loader_name)
    except Exception as exc:  # noqa: BLE001
        print(
            f"ERROR durante la auditoría: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
