from __future__ import annotations
from typing import List, Dict, Any, Tuple
import numpy as np

def parse_augmented_matrix(text: str) -> np.ndarray:
    """
    Convierte texto a matriz aumentada (floats).
    Soporta separadores por espacio o coma. Una fila por línea.
    """
    rows = []
    for raw in text.strip().splitlines():
        if not raw.strip():
            continue
        parts = [p.strip() for p in raw.replace(",", " ").split()]
        rows.append([float(p) for p in parts])
    mat = np.array(rows, dtype=float)
    # validaciones básicas
    if mat.ndim != 2:
        raise ValueError("La matriz debe ser 2D.")
    n, m = mat.shape
    if m != n + 1:
        raise ValueError(f"Para un sistema de {n} ecuaciones, se esperan {n+1} columnas (incluyendo b).")
    return mat

def eliminacion_gaussiana_pivoteo_total_web(A: np.ndarray) -> Dict[str, Any]:
    """
    Ejecuta eliminación gaussiana con pivoteo total sobre la matriz aumentada A (n x (n+1)).
    Devuelve:
      - stages: lista de matrices por etapa (cada una como lista de listas redondeada)
      - swaps: info de intercambios por etapa
      - x: solución final (ordenada según permutaciones de columnas)
      - perm_cols: permutación de columnas aplicada (para reconstruir orden original)
    """
    A = A.copy()
    n, m = A.shape
    if m != n + 1:
        raise ValueError("La matriz debe ser de tamaño n x (n+1).")

    # Rastrear intercambios
    perm_rows = list(range(n))
    perm_cols = list(range(n))

    # Almacenar etapas (matrices y swaps)
    stages: List[Dict[str, Any]] = []
    stages.append({
        "k": 0,
        "matrix": A.copy(),
        "swap": {"rows": None, "cols": None},
        "note": "Matriz inicial"
    })

    # Eliminación con pivoteo total
    for k in range(n - 1):
        # Buscar pivote máximo en submatriz A[k:n, k:n]
        sub = np.abs(A[k:n, k:n])
        idx = np.unravel_index(np.argmax(sub), sub.shape)
        i_max = k + idx[0]
        j_max = k + idx[1]
        max_val = sub[idx]

        if max_val < 1e-12:
            raise ValueError("Pivote muy pequeño o cero. Sistema singular o mal condicionado.")

        swap_info = {"rows": None, "cols": None}

        # Intercambio de filas
        if i_max != k:
            A[[k, i_max], :] = A[[i_max, k], :]
            perm_rows[k], perm_rows[i_max] = perm_rows[i_max], perm_rows[k]
            swap_info["rows"] = (k, i_max)

        # Intercambio de columnas (solo en coeficientes, excluyendo término independiente)
        if j_max != k:
            A[:, [k, j_max]] = A[:, [j_max, k]]
            perm_cols[k], perm_cols[j_max] = perm_cols[j_max], perm_cols[k]
            swap_info["cols"] = (k, j_max)

        # Eliminación hacia abajo
        for i in range(k + 1, n):
            if abs(A[k, k]) > 1e-16:
                f = A[i, k] / A[k, k]
                A[i, k:m] = A[i, k:m] - f * A[k, k:m]

        stages.append({
            "k": k + 1,
            "matrix": A.copy(),
            "swap": swap_info,
            "note": f"Etapa {k+1}"
        })

    # Sustitución regresiva
    y = np.zeros(n, dtype=float)
    for i in range(n - 1, -1, -1):
        s = float(np.dot(A[i, i+1:n], y[i+1:n])) if i+1 < n else 0.0
        if abs(A[i, i]) < 1e-16:
            raise ValueError("Cero en la diagonal durante sustitución regresiva.")
        y[i] = (A[i, n] - s) / A[i, i]

    # Reordenar solución a las variables originales según perm_cols
    x = np.zeros(n, dtype=float)
    for i in range(n):
        x[perm_cols[i]] = y[i]

    return {
        "stages": [ _stage_to_serializable(st) for st in stages ],
        "solution": x.tolist(),
        "perm_cols": perm_cols,
        "perm_rows": perm_rows,
    }

def _stage_to_serializable(st: Dict[str, Any]) -> Dict[str, Any]:
    M = st["matrix"]
    return {
        "k": st["k"],
        "note": st["note"],
        "swap": st["swap"],
        "matrix": [[float(v) for v in row] for row in M]
    }

def run_gauss_pivote_web(text_matrix: str) -> Dict[str, Any]:
    """
    Punto de entrada para la vista web. Recibe el texto de la matriz aumentada.
    Devuelve contexto para la plantilla: etapas, solución, etc.
    """
    A = parse_augmented_matrix(text_matrix)
    result = eliminacion_gaussiana_pivoteo_total_web(A)
    return {
        "n": A.shape[0],
        "m": A.shape[1],
        "stages": result["stages"],
        "solution": result["solution"],
        "perm_cols": result["perm_cols"],
        "perm_rows": result["perm_rows"],
    }