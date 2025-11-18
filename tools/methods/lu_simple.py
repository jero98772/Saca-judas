# tools/methods/lu_simple.py
# -*- coding: utf-8 -*-
"""
LU Simple (sin pivoteo) para la web.
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
import numpy as np
import importlib, inspect, sys

# ------------------------------------------------------------
# 1) Buscar tu código (en ESTE archivo o en submódulos "mio")
# ------------------------------------------------------------
USER_MAIN_NAMES = [
    "lu_simple_mio",
    "gauss_simple",
    "lu_simple",
    "lu_doolittle",
    "doolittle"
]

USER_FACT_NAMES = [
    "factorizacion_lu_simple",
    "factorizacion_lu",
    "factorizar_lu_simple",
    "factorizar_lu"
]

USER_FWD_NAMES = ["sustitucion_adelante", "forward_substitution", "sustitucion_hacia_adelante"]
USER_BWD_NAMES = ["sustitucion_atras", "back_substitution", "sustitucion_hacia_atras"]

CANDIDATE_MODULES = [
    "tools.methods.gauss_simple_mio",
    "tools.methods.lu_simple_mio",
    "tools.methods.lu_simple",
    "gauss_simple_mio",
    "lu_simple_mio",
    "lu_simple",
]

def _get_fn(mod, names) -> Optional[Callable]:
    for n in names:
        fn = getattr(mod, n, None)
        if callable(fn):
            return fn
    return None

def _import_first_available(mod_names):
    for m in mod_names:
        try:
            return importlib.import_module(m)
        except Exception:
            continue
    return None

# También mira si las funciones están definidas en ESTE archivo
_this_module = sys.modules[__name__]
LOCAL_MAIN = _get_fn(_this_module, USER_MAIN_NAMES)
LOCAL_FACT = _get_fn(_this_module, USER_FACT_NAMES)
LOCAL_FWD  = _get_fn(_this_module, USER_FWD_NAMES)
LOCAL_BWD  = _get_fn(_this_module, USER_BWD_NAMES)

MIO = _import_first_available(CANDIDATE_MODULES)
MIO_MAIN = _get_fn(MIO, USER_MAIN_NAMES) if MIO else None
MIO_FACT = _get_fn(MIO, USER_FACT_NAMES) if MIO else None
MIO_FWD  = _get_fn(MIO, USER_FWD_NAMES)  if MIO else None
MIO_BWD  = _get_fn(MIO, USER_BWD_NAMES)  if MIO else None

# ------------------------------------------------------------
# 2) Utilidades
# ------------------------------------------------------------
def _forward_substitution(L: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = L.shape[0]
    y = np.zeros(n, dtype=float)
    for i in range(n):
        s = b[i] - (L[i, :i] @ y[:i] if i > 0 else 0.0)
        diag = L[i, i] if abs(L[i, i]) > 1e-15 else 1.0
        y[i] = s / diag
    return y

def _back_substitution(U: np.ndarray, y: np.ndarray) -> np.ndarray:
    n = U.shape[0]
    x = np.zeros(n, dtype=float)
    for i in range(n - 1, -1, -1):
        s = y[i] - (U[i, i+1:] @ x[i+1:] if i < n - 1 else 0.0)
        if abs(U[i, i]) < 1e-15:
            raise ValueError("Matriz singular o casi singular en sustitución hacia atrás.")
        x[i] = s / U[i, i]
    return x

def _to_list(M: np.ndarray):
    return M.astype(float).tolist()

# ------------------------------------------------------------
# 3) Llamar a TU función con firmas comunes
# ------------------------------------------------------------
def _try_call_main(fn: Callable, A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[list]]:
    sig = inspect.signature(fn)
    params = list(sig.parameters.keys())
    tries = []
    if len(params) >= 2: tries.append((A, b))
    if len(params) == 1: tries.append((A,))
    if len(params) >= 3: tries.append((A, b, True))

    for args in tries:
        try:
            out = fn(*args)
            if isinstance(out, tuple):
                if len(out) == 2:
                    L, U = out; x = None; etapas = None
                elif len(out) == 3:
                    L, U, x = out; etapas = None
                else:
                    L, U, x, etapas = out[0], out[1], (out[2] if len(out) > 2 else None), (out[3] if len(out) > 3 else None)
                return np.array(L, float), np.array(U, float), (None if x is None else np.array(x, float)), etapas
        except Exception:
            continue
    raise RuntimeError("No se pudo invocar tu función principal de LU Simple con firmas conocidas.")

def _solve_with_helpers(L: np.ndarray, U: np.ndarray, b: np.ndarray) -> np.ndarray:
    fwd = LOCAL_FWD or MIO_FWD
    bwd = LOCAL_BWD or MIO_BWD
    try:
        y = np.array(fwd(L, b), float) if fwd else _forward_substitution(L, b)
    except Exception:
        y = _forward_substitution(L, b)
    try:
        x = np.array(bwd(U, y), float) if bwd else _back_substitution(U, y)
    except Exception:
        x = _back_substitution(U, y)
    return x

# ------------------------------------------------------------
# 4) Fallback interno (LU Simple sin pivoteo)
# ------------------------------------------------------------
def _fallback_lu_simple(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray, list]:
    n = A.shape[0]
    U = A.copy().astype(float)
    L = np.eye(n, dtype=float)
    etapas = []

    for k in range(n-1):
        if abs(U[k, k]) < 1e-15:
            raise ValueError("No se puede factorizar: pivote cero. Use LU con pivoteo parcial.")
        
        for i in range(k+1, n):
            L[i, k] = U[i, k] / U[k, k]
            U[i, k:] = U[i, k:] - L[i, k] * U[k, k:]
        
        etapas.append({"matrix": _to_list(U)})
    
    return L, U, etapas

# ------------------------------------------------------------
# 5) API principal usada por FastAPI
# ------------------------------------------------------------
def compute_lu_simple(A: List[List[float]], b: List[float], track_etapas: bool = True) -> Dict[str, Any]:
    if not isinstance(A, list) or not A or not all(isinstance(r, list) for r in A):
        raise ValueError("A debe ser una lista de listas no vacía.")
    n = len(A)
    if any(len(r) != n for r in A):
        raise ValueError("A debe ser cuadrada.")
    if not isinstance(b, list) or len(b) != n:
        raise ValueError("b debe tener longitud n.")

    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)

    etapas = None

    # a) Tu función principal en este archivo
    if LOCAL_MAIN:
        L, U, x_opt, etapas = _try_call_main(LOCAL_MAIN, A_np, b_np)
        x = x_opt if x_opt is not None else _solve_with_helpers(L, U, b_np)

    # b) Tu función principal en módulo *_mio
    elif MIO_MAIN:
        L, U, x_opt, etapas = _try_call_main(MIO_MAIN, A_np, b_np)
        x = x_opt if x_opt is not None else _solve_with_helpers(L, U, b_np)

    else:
        # c) Solo factorizar (este archivo o módulo *_mio)
        fn_fact = LOCAL_FACT or MIO_FACT
        if fn_fact:
            out = fn_fact(A_np)
            if not isinstance(out, tuple) or len(out) < 2:
                raise RuntimeError("La función de factorización debe retornar al menos (L, U).")
            L = np.array(out[0], float)
            U = np.array(out[1], float)
            if len(out) >= 3 and track_etapas:
                etapas = out[2]
            x = _solve_with_helpers(L, U, b_np)
        else:
            # d) Fallback interno (para no romper)
            L, U, etapas = _fallback_lu_simple(A_np)
            x = _solve_with_helpers(L, U, b_np)

    # aumentada final [U | y]
    try:
        y = _forward_substitution(L, b_np)
        aumentada_final = np.hstack([U, y.reshape(-1, 1)])
    except Exception:
        aumentada_final = U

    res = {
        "x": _to_list(x),
        "L": _to_list(L),
        "U": _to_list(U),
        "aumentada_final": _to_list(aumentada_final),
    }
    if track_etapas and etapas:
        res["etapas"] = etapas
    return res