# tools/methods/lu_partial.py
# -*- coding: utf-8 -*-
"""
LU with partial pivoting for the web.

- If it finds YOUR implementation (lu_parcial_mio, gauss_con_pivote_parcial, etc.),
  it uses it and returns a JSON-friendly dict.
- If it does not find it, it uses an internal fallback so the page does not break.
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
import numpy as np
import importlib, inspect, sys

# ------------------------------------------------------------
# 1) Look for your code (in THIS file or in "mio" submodules)
# ------------------------------------------------------------
USER_MAIN_NAMES = [
    "lu_parcial_mio",
    "gauss_con_pivote_parcial",
    "lu_parcial",
    "lu_pivote_parcial",
]
USER_FACT_NAMES = [
    "factorizacion_lu_pivote_parcial",
    "factorizacion_lu_parcial",
    "factorizar_lu_pivote_parcial",
    "factorizar_lu_parcial",
]
USER_FWD_NAMES = ["sustitucion_adelante", "forward_substitution", "sustitucion_hacia_adelante"]
USER_BWD_NAMES = ["sustitucion_atras", "back_substitution", "sustitucion_hacia_atras"]

CANDIDATE_MODULES = [
    # same package
    "tools.methods.gauss_con_pivote_parcial_mio",
    "tools.methods.lu_parcial_mio",
    "tools.methods.lu_partial_mio",
    # in case you left it at project root
    "gauss_con_pivote_parcial_mio",
    "lu_parcial_mio",
    "lu_partial_mio",
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

# Also check if the functions are defined in THIS file (if you pasted your code here)
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
# 2) Utilities (only if your module does not provide these)
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
            raise ValueError("Singular or nearly singular matrix in back substitution.")
        x[i] = s / U[i, i]
    return x

def _to_list(M: np.ndarray):
    return M.astype(float).tolist()

# ------------------------------------------------------------
# 3) Call YOUR function with common signatures
# ------------------------------------------------------------
def _try_call_main(fn: Callable, A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Optional[np.ndarray], Optional[list]]:
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
                if len(out) == 3:
                    L, U, P = out; x = None; etapas = None
                elif len(out) == 4:
                    L, U, P, x = out; etapas = None
                else:
                    L, U, P, x, etapas = out[0], out[1], out[2], (out[3] if len(out) > 3 else None), (out[4] if len(out) > 4 else None)
                return np.array(L, float), np.array(U, float), np.array(P, float), (None if x is None else np.array(x, float)), etapas
        except Exception:
            continue
    raise RuntimeError("Could not call your main LU function with known signatures.")

def _solve_with_helpers(L: np.ndarray, U: np.ndarray, P: np.ndarray, b: np.ndarray) -> np.ndarray:
    fwd = LOCAL_FWD or MIO_FWD
    bwd = LOCAL_BWD or MIO_BWD
    Pb = P @ b
    try:
        y = np.array(fwd(L, Pb), float) if fwd else _forward_substitution(L, Pb)
    except Exception:
        y = _forward_substitution(L, Pb)
    try:
        x = np.array(bwd(U, y), float) if bwd else _back_substitution(U, y)
    except Exception:
        x = _back_substitution(U, y)
    return x

# ------------------------------------------------------------
# 4) Internal fallback (if there is no user-code available)
#     -> Factorizes with partial pivoting and solves
# ------------------------------------------------------------
def _fallback_lu(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, list]:
    n = A.shape[0]
    U = A.copy().astype(float)
    L = np.eye(n, dtype=float)
    P = np.eye(n, dtype=float)
    etapas = []

    for k in range(n-1):
        piv = np.argmax(np.abs(U[k:, k])) + k
        if abs(U[piv, k]) < 1e-15:
            raise ValueError("Cannot factorize: zero pivot.")
        if piv != k:
            U[[k, piv], :] = U[[piv, k], :]
            P[[k, piv], :] = P[[piv, k], :]
            if k > 0:
                L[[k, piv], :k] = L[[piv, k], :k]
        for i in range(k+1, n):
            L[i, k] = U[i, k] / U[k, k]
            U[i, k:] = U[i, k:] - L[i, k]*U[k, k:]
        etapas.append({"matrix": _to_list(U)})
    return L, U, P, etapas

# ------------------------------------------------------------
# 5) Main API used by FastAPI
# ------------------------------------------------------------
def compute_gauss_pivote_parcial(A: List[List[float]], b: List[float], track_etapas: bool = True) -> Dict[str, Any]:
    if not isinstance(A, list) or not A or not all(isinstance(r, list) for r in A):
        raise ValueError("A must be a non-empty list of lists.")
    n = len(A)
    if any(len(r) != n for r in A):
        raise ValueError("A must be square.")
    if not isinstance(b, list) or len(b) != n:
        raise ValueError("b must have length n.")

    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)

    etapas = None

    # a) Your main function in this file
    if LOCAL_MAIN:
        L, U, P, x_opt, etapas = _try_call_main(LOCAL_MAIN, A_np, b_np)
        x = x_opt if x_opt is not None else _solve_with_helpers(L, U, P, b_np)

    # b) Your main function in *_mio module
    elif MIO_MAIN:
        L, U, P, x_opt, etapas = _try_call_main(MIO_MAIN, A_np, b_np)
        x = x_opt if x_opt is not None else _solve_with_helpers(L, U, P, b_np)

    else:
        # c) Only factorization (this file or *_mio module)
        fn_fact = LOCAL_FACT or MIO_FACT
        if fn_fact:
            out = fn_fact(A_np)
            if not isinstance(out, tuple) or len(out) < 3:
                raise RuntimeError("The factorization function must return at least (L, U, P).")
            L = np.array(out[0], float)
            U = np.array(out[1], float)
            P = np.array(out[2], float)
            if len(out) >= 4 and track_etapas:
                etapas = out[3]
            x = _solve_with_helpers(L, U, P, b_np)
        else:
            # d) Internal fallback (to avoid breaking)
            L, U, P, etapas = _fallback_lu(A_np)
            x = _solve_with_helpers(L, U, P, b_np)

    # final augmented [U | y]
    try:
        Pb = P @ b_np
        y = _forward_substitution(L, Pb)
        aumentada_final = np.hstack([U, y.reshape(-1, 1)])
    except Exception:
        aumentada_final = U

    res = {
        "x": _to_list(x),
        "L": _to_list(L),
        "U": _to_list(U),
        "P": _to_list(P),
        "aumentada_final": _to_list(aumentada_final),
    }
    if track_etapas and etapas:
        res["etapas"] = etapas
    return res

# compat
def lu_partial(A: List[List[float]], b: List[float], decimals: int = 6):
    return compute_gauss_pivote_parcial(A, b, track_etapas=True)
