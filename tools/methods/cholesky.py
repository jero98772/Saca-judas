# tools/methods/cholesky.py
# -*- coding: utf-8 -*-
"""
Descomposición de Cholesky — usa TU implementación si existe
(p. ej. tools/methods/cholesky_mio.py) y la envuelve para retornar un dict JSON-friendly.

Exporta:
- compute_cholesky(A, b, track_etapas=True) -> {
    "x": [...],
    "L": [[...], ...],
    "Lt": [[...], ...],
    "y": [...],
    "etapas": [ {"matrix": [[...], ...]}, ... ]   # opcional si tu código las trae
}
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
import numpy as np
import importlib
import inspect

# ====== Intentamos usar tu módulo y nombres comunes ======
CANDIDATE_MODULES = [
    "tools.methods.cholesky_mio",
    # por si lo dejaste en raíz:
    "cholesky_mio",
]

CHOLESKY_FUNC_NAMES = [
    "cholesky_mio",
    "cholesky",
    "descomposicion_cholesky",
    "factorizacion_cholesky",
]

FWD_NAMES = ["sustitucion_adelante", "forward_substitution", "sustitucion_hacia_adelante"]
BWD_NAMES = ["sustitucion_atras", "back_substitution", "sustitucion_hacia_atras"]

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

# ====== utilidades mínimas (se usan solo si tu módulo no trae estas) ======
def _forward_substitution(L: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = L.shape[0]
    y = np.zeros(n, dtype=float)
    for i in range(n):
        s = b[i] - (L[i, :i] @ y[:i] if i > 0 else 0.0)
        if abs(L[i, i]) < 1e-15:
            raise ValueError("Triangular inferior singular en sustitución hacia adelante.")
        y[i] = s / L[i, i]
    return y

def _back_substitution(U: np.ndarray, y: np.ndarray) -> np.ndarray:
    n = U.shape[0]
    x = np.zeros(n, dtype=float)
    for i in range(n - 1, -1, -1):
        s = y[i] - (U[i, i+1:] @ x[i+1:] if i < n - 1 else 0.0)
        if abs(U[i, i]) < 1e-15:
            raise ValueError("Triangular superior singular en sustitución hacia atrás.")
        x[i] = s / U[i, i]
    return x

def _to_list(M: np.ndarray):
    return M.astype(float).tolist()

def _call_user_cholesky(fn: Callable, A: np.ndarray):
    """
    Intenta firmas comunes:
      - fn(A) -> L
      - fn(A, True/False) -> L (y quizá etapas)
    Retorna (L, etapas | None)
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.keys())

    tries = []
    if len(params) >= 1:
        tries.append((A,))
    if len(params) >= 2:
        tries.append((A, True))
        tries.append((A, False))

    for args in tries:
        try:
            out = fn(*args)
            # si devuelve L directamente
            if isinstance(out, (list, np.ndarray)):
                L = np.array(out, dtype=float)
                return L, None
            # si devuelve tupla (L, etapas?) o dict
            if isinstance(out, tuple):
                L = np.array(out[0], dtype=float)
                etapas = out[1] if len(out) > 1 else None
                return L, etapas
            if isinstance(out, dict):
                # intenta detectar 'L' y 'etapas'
                L = np.array(out.get("L"), dtype=float)
                etapas = out.get("etapas")
                return L, etapas
        except Exception:
            continue
    raise RuntimeError("No se pudo invocar tu función de Cholesky con firmas conocidas.")

def _normalize_etapas(etapas):
    if not etapas:
        return None
    norm = []
    try:
        for st in etapas:
            if isinstance(st, dict) and "matrix" in st:
                norm.append({"matrix": st["matrix"]})
            else:
                norm.append({"matrix": np.array(st, float).tolist()})
    except Exception:
        pass
    return norm if norm else None

# ====== API principal (usada por FastAPI) ======
def compute_cholesky(A: List[List[float]], b: List[float], track_etapas: bool = True) -> Dict[str, Any]:
    """
    Usa TU descomposición de Cholesky para resolver Ax=b.
    Devuelve dict con x, L, Lt (=L.T), y y etapas (si están disponibles).
    """
    if not isinstance(A, list) or not A or not all(isinstance(r, list) for r in A):
        raise ValueError("A debe ser una lista de listas no vacía.")
    n = len(A)
    if any(len(r) != n for r in A):
        raise ValueError("A debe ser cuadrada.")
    if not isinstance(b, list) or len(b) != n:
        raise ValueError("b debe tener longitud n.")

    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)

    # 1) intentar usar tu módulo/función
    user_mod = _import_first(CANDIDATE_MODULES)
    L = None
    etapas = None

    if user_mod:
        user_fn = _get_first_callable(user_mod, CHOLESKY_FUNC_NAMES)
        if user_fn:
            L, etapas = _call_user_cholesky(user_fn, A_np)

    # 2) fallback si no hay tu módulo: usar numpy.linalg.cholesky
    if L is None:
        try:
            L = np.linalg.cholesky(A_np)
        except np.linalg.LinAlgError as e:
            raise ValueError("A no es simétrica definida positiva (falló Cholesky).") from e

    # 3) resolver: L y = b ; L^T x = y
    # intentar usar sustituciones del usuario si existen
    fwd = _get_first_callable(user_mod, FWD_NAMES) if user_mod else None
    bwd = _get_first_callable(user_mod, BWD_NAMES) if user_mod else None

    try:
        y = np.array(fwd(L, b_np), dtype=float) if fwd else _forward_substitution(L, b_np)
    except Exception:
        y = _forward_substitution(L, b_np)

    Lt = L.T.copy()
    try:
        x = np.array(bwd(Lt, y), dtype=float) if bwd else _back_substitution(Lt, y)
    except Exception:
        x = _back_substitution(Lt, y)

    result: Dict[str, Any] = {
        "x": x.astype(float).tolist(),
        "L": _to_list(L),
        "Lt": _to_list(Lt),
        "y": y.astype(float).tolist(),
    }
    if track_etapas:
        norm = _normalize_etapas(etapas)
        if norm:
            result["etapas"] = norm

    return result
