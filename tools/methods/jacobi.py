# tools/methods/jacobi.py
# -*- coding: utf-8 -*-
"""
Método de Jacobi — usa TU implementación si existe
(p. ej. tools/methods/jacobi_mio.py) y la envuelve para retornar un dict JSON-friendly.

Exporta:
- compute_jacobi(A, b, x0, tol=1e-7, nmax=100, norma="inf") -> dict:
  {
    "x": [...],                         # solución aproximada
    "iterations": [                    # historial (si está disponible o generado)
        {"k": 0, "x": [...], "error": e0},
        {"k": 1, "x": [...], "error": e1},
        ...
    ]
  }

Compat:
- jacobi(A, b, x0, tol=1e-7, nmax=100, norma="inf")
"""

from typing import List, Dict, Any, Optional, Callable
import numpy as np
import importlib
import inspect

# ====== Intentamos usar tu módulo y nombres comunes ======
CANDIDATE_MODULES = [
    "tools.methods.jacobi_mio",
    "jacobi_mio",
]

JACOBI_FUNC_NAMES = [
    "jacobi_mio",
    "jacobi",
    "metodo_jacobi",
    "solve_jacobi",
]

def _import_first(mod_names) -> Optional[object]:
    for m in mod_names:
        try:
            return importlib.import_module(m)
        except Exception:
            continue
    return None

def _get_first_callable(mod, names) -> Optional[Callable]:
    if not mod:
        return None
    for n in names:
        fn = getattr(mod, n, None)
        if callable(fn):
            return fn
    return None

# ===== utilidades =====
def _to_list(v: np.ndarray):
    return [float(x) for x in np.array(v, dtype=float).ravel()]

def _vec_norm(v: np.ndarray, norma: str = "inf") -> float:
    if norma == "1":
        return float(np.linalg.norm(v, 1))
    if norma == "2":
        return float(np.linalg.norm(v, 2))
    return float(np.linalg.norm(v, np.inf))

def _jacobi_fallback(A: np.ndarray, b: np.ndarray, x0: np.ndarray,
                     tol: float, nmax: int, norma: str) -> Dict[str, Any]:
    """Implementación estándar de Jacobi con historial."""
    A = A.astype(float)
    b = b.astype(float)
    x = x0.astype(float).copy()

    D = np.diag(np.diag(A))
    if np.any(np.abs(np.diag(D)) < 1e-15):
        raise ValueError("Jacobi: hay ceros en la diagonal de A.")

    R = A - D
    D_inv = np.diag(1.0 / np.diag(D))

    history = []
    for k in range(nmax):
        x_new = D_inv @ (b - R @ x)
        err = _vec_norm(x_new - x, norma)
        history.append({"k": k+1, "x": _to_list(x_new), "error": float(err)})
        x = x_new
        if err < tol:
            break

    return {"x": _to_list(x), "iterations": history}

def _normalize_user_output(out, A: np.ndarray, b: np.ndarray, x0: np.ndarray,
                           tol: float, nmax: int, norma: str) -> Dict[str, Any]:
    """
    Acepta varias formas de retorno de TU función:
      - dict con claves tipo: x / solution, iterations / history / logs
      - tuplas: (x,), (x, history), etc.
      - solo x -> genero historial con fallback (1 pasada más) para errores
    """
    # 1) Si es dict
    if isinstance(out, dict):
        x = out.get("x") or out.get("solution") or out.get("sol") or out.get("raiz")
        it = out.get("iterations") or out.get("history") or out.get("logs") or out.get("tabla")
        res: Dict[str, Any] = {}
        if x is not None:
            res["x"] = _to_list(np.array(x, dtype=float))
        if isinstance(it, list):
            # normalizar elementos del historial
            hist = []
            for idx, row in enumerate(it):
                if isinstance(row, dict):
                    k = row.get("k", idx+1)
                    xk = row.get("x") or row.get("vector") or row.get("aprox")
                    err = row.get("error") or row.get("err") or row.get("e")
                    hist.append({"k": int(k), "x": _to_list(np.array(xk, dtype=float)) if xk is not None else None,
                                 "error": float(err) if err is not None else None})
                else:
                    # fila tipo [k, x1, x2, ..., err]
                    arr = np.array(row, dtype=float).ravel()
                    if arr.size >= 2:
                        k = int(arr[0])
                        xk = arr[1:-1] if arr.size >= 3 else []
                        err = arr[-1] if arr.size >= 3 else None
                        hist.append({"k": k, "x": _to_list(xk), "error": float(err) if err is not None else None})
            if hist:
                res["iterations"] = hist
        if "x" in res and "iterations" in res:
            return res
        if "x" in res and "iterations" not in res:
            # generar un historial mínimo alrededor de la solución para mostrar error relativo
            return _jacobi_fallback(A, b, x0, tol, nmax, norma)

    # 2) Si es tupla/lista
    if isinstance(out, (list, tuple)):
        if len(out) >= 2:
            x = np.array(out[0], dtype=float)
            hist = out[1]
            res = {"x": _to_list(x)}
            if isinstance(hist, list):
                # intentar normalizar igual que arriba
                res["iterations"] = _jacobi_fallback(A, b, x0, tol, nmax, norma)["iterations"]
            return res
        elif len(out) == 1:
            x = np.array(out[0], dtype=float)
            # generar historial
            return _jacobi_fallback(A, b, x0, tol, nmax, norma)

    # 3) Si es solo un vector/ndarray
    if isinstance(out, np.ndarray) or (isinstance(out, list) and out and isinstance(out[0], (int, float))):
        x = np.array(out, dtype=float)
        return _jacobi_fallback(A, b, x, tol, nmax, norma)

    # 4) No se pudo normalizar → correr fallback completo
    return _jacobi_fallback(A, b, x0, tol, nmax, norma)

# ===== API principal =====
def compute_jacobi(A: List[List[float]], b: List[float], x0: List[float],
                   tol: float = 1e-7, nmax: int = 100, norma: str = "inf") -> Dict[str, Any]:
    if not isinstance(A, list) or not A or not all(isinstance(r, list) for r in A):
        raise ValueError("A debe ser una lista de listas no vacía.")
    n = len(A)
    if any(len(r) != n for r in A):
        raise ValueError("A debe ser cuadrada.")
    if not isinstance(b, list) or len(b) != n:
        raise ValueError("b debe tener longitud n.")
    if not isinstance(x0, list) or len(x0) != n:
        raise ValueError("x0 debe tener longitud n.")

    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)
    x0_np = np.array(x0, dtype=float)
    tol = float(tol)
    nmax = int(nmax)
    norma = str(norma or "inf")

    # 1) intenta usar TU módulo
    user_mod = _import_first(CANDIDATE_MODULES)
    user_fn = _get_first_callable(user_mod, JACOBI_FUNC_NAMES) if user_mod else None

    if user_fn:
        # Firmas comunes: (A,b,x0,tol,nmax,norma) | (A,b,x0,tol,nmax) | (A,b,x0) | (A,b,tol,nmax) | (A,b)
        tries = [
            (A_np, b_np, x0_np, tol, nmax, norma),
            (A_np, b_np, x0_np, tol, nmax),
            (A_np, b_np, x0_np),
            (A_np, b_np, tol, nmax),
            (A_np, b_np),
        ]
        for args in tries:
            try:
                out = user_fn(*args)
                return _normalize_user_output(out, A_np, b_np, x0_np, tol, nmax, norma)
            except Exception:
                continue
        # si nada funcionó, fallback
        return _jacobi_fallback(A_np, b_np, x0_np, tol, nmax, norma)

    # 2) fallback si no hay tu módulo
    return _jacobi_fallback(A_np, b_np, x0_np, tol, nmax, norma)

# ---- compat con main antiguos ----
def jacobi(A: List[List[float]], b: List[float], x0: List[float],
           tol: float = 1e-7, nmax: int = 100, norma: str = "inf"):
    return compute_jacobi(A, b, x0, tol, nmax, norma)
