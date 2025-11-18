# tools/methods/vandermonde.py
# -*- coding: utf-8 -*-
"""
Interpolation with Vandermonde matrix — uses YOUR implementation if it exists
(for example in tools/methods/Vandermonde_mio.py or vandermonde_mio.py) and
just wraps it to return a JSON-friendly dict.

Exports:
- compute_vandermonde(x, y, decimals=6) -> dict with:
  {
    "coeficientes": [a0, a1, ..., a_{n-1}],
    "V": [[...], ...],
    "polinomio": "p(x) = ...",
    "grado": n-1
  }
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
import numpy as np
import importlib
import inspect

# ========= CANDIDATES: module and names your function might have =========
CANDIDATE_MODULES = [
    "tools.methods.Vandermonde_mio",
    "tools.methods.vandermonde_mio",
    "tools.methods.vandermonde_user",
    # in case you left it at the project root:
    "Vandermonde_mio",
    "vandermonde_mio",
    "vandermonde_user",
]

MAIN_FUNC_NAMES = [
    # functions that might return coefficients, V and/or a dict:
    "vandermonde_mio",
    "resolver_vandermonde",
    "interpolacion_vandermonde",
    "calcular_vandermonde",
    "calc_vandermonde",
    "compute_vandermonde_mio",
]

V_ONLY_FUNC_NAMES = [
    # functions that might only build the Vandermonde matrix:
    "matriz_vandermonde",
    "construir_vandermonde",
    "build_vandermonde",
]

# ========= support utilities (do not replace your logic) =========
def _to_2d_list(M: np.ndarray):
    return [[float(c) for c in row] for row in M]

def _vandermonde_matrix(x: List[float], n: Optional[int] = None) -> np.ndarray:
    x_arr = np.array(x, dtype=float)
    if n is None:
        n = len(x_arr)
    return np.vander(x_arr, N=n, increasing=True)  # [1, x, x^2, ...]

def _poly_to_string(coeffs: np.ndarray, var: str = "x", decimals: int = 6) -> str:
    terms = []
    for i, a in enumerate(coeffs):
        a = float(a)
        if abs(a) < 1e-12:
            continue
        s = f"{a:.{decimals}f}".rstrip("0").rstrip(".") or "0"
        if i == 0:
            term = s
        elif i == 1:
            term = f"{s} {var}"
        else:
            term = f"{s} {var}^{i}"
        terms.append(term)
    if not terms:
        return f"p({var}) = 0"
    return f"p({var}) = " + " + ".join(terms).replace("+ -", "- ")

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

def _call_user_main(fn: Callable, x: List[float], y: List[float], decimals: int) -> Dict[str, Any]:
    """
    Tries several common signatures for YOUR function:
      - fn(x, y)
      - fn(x, y, decimals)
      - fn(x, y, True/False)
    Accepts returns: dict, (coef,), (coef, V), (coef, V, poly), etc.
    Normalizes to a standard dict.
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.keys())

    tries = []
    if len(params) >= 2:
        tries.append((x, y))
    if len(params) >= 3:
        # first we try with decimals in case your function uses it
        tries.append((x, y, decimals))
        # boolean alternative (track/verbose/etc.)
        tries.append((x, y, True))

    for args in tries:
        try:
            out = fn(*args)
            # 1) if it is already a dict with our keys
            if isinstance(out, dict):
                res = {}
                coef = out.get("coeficientes") or out.get("coef") or out.get("a")
                if coef is not None:
                    coef = np.array(coef, dtype=float)
                    res["coeficientes"] = [float(v) for v in coef]
                    res["grado"] = len(coef) - 1
                V = out.get("V") or out.get("vandermonde") or out.get("matriz")
                if V is not None:
                    res["V"] = [[float(c) for c in row] for row in V]
                poly = out.get("polinomio") or out.get("poly") or out.get("poly_str")
                if poly is None and coef is not None:
                    poly = _poly_to_string(coef, "x", decimals)
                if poly is not None:
                    res["polinomio"] = poly
                return res

            # 2) if it is a tuple/list with multiple outputs
            if isinstance(out, (list, tuple)):
                coef = None
                V = None
                poly = None
                # map by length:
                if len(out) >= 1:
                    coef = np.array(out[0], dtype=float)
                if len(out) >= 2:
                    V = np.array(out[1], dtype=float)
                if len(out) >= 3 and isinstance(out[2], (str, bytes)):
                    poly = out[2].decode() if isinstance(out[2], bytes) else out[2]

                res = {}
                if coef is not None:
                    res["coeficientes"] = [float(v) for v in coef]
                    res["grado"] = len(coef) - 1
                if V is not None:
                    res["V"] = _to_2d_list(V)
                if poly is None and coef is not None:
                    poly = _poly_to_string(coef, "x", decimals)
                if poly is not None:
                    res["polinomio"] = poly
                if res:
                    return res
        except Exception:
            continue

    raise RuntimeError("Could not call your Vandermonde function with known signatures.")

def _call_user_V_only(fnV: Callable, x: List[float], y: List[float], decimals: int) -> Dict[str, Any]:
    """
    If your module only exposes the construction of V, we use it and then solve for coefficients.
    Supports signatures fnV(x) or fnV(x, n).
    """
    n = len(x)
    try:
        # typical attempts
        try:
            V = fnV(x, n)  # signature: (x, n)
        except TypeError:
            V = fnV(x)     # signature: (x)
        V = np.array(V, dtype=float)
    except Exception:
        # if it fails, we build it ourselves
        V = _vandermonde_matrix(x, n)

    # solve V a = y
    try:
        coef = np.linalg.solve(V, np.array(y, dtype=float))
    except np.linalg.LinAlgError as e:
        raise ValueError("The Vandermonde matrix is singular (repeated x or ill-conditioned).") from e

    return {
        "coeficientes": [float(v) for v in coef],
        "V": _to_2d_list(V),
        "polinomio": _poly_to_string(coef, "x", decimals),
        "grado": len(coef) - 1,
    }

# ========= main API (used by FastAPI) =========
def compute_vandermonde(x: List[float], y: List[float], decimals: int = 6) -> Dict[str, Any]:
    """
    Uses YOUR implementation if available; otherwise, solves with a fallback
    (without breaking the app).
    """
    if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) >= 2):
        raise ValueError("x and y must be non-empty lists of the same size (>= 2).")

    # 1) try to load your module
    user_mod = _import_first(CANDIDATE_MODULES)

    # 2) if there is a main user function, use it
    user_main = _get_first_callable(user_mod, MAIN_FUNC_NAMES) if user_mod else None
    if user_main:
        return _call_user_main(user_main, x, y, decimals)

    # 3) if there is only a V-matrix function, use it and solve
    user_vonly = _get_first_callable(user_mod, V_ONLY_FUNC_NAMES) if user_mod else None
    if user_vonly:
        return _call_user_V_only(user_vonly, x, y, decimals)

    # 4) fallback (in case you haven't added your module yet): solve directly
    V = _vandermonde_matrix(x)
    try:
        coef = np.linalg.solve(V, np.array(y, dtype=float))
    except np.linalg.LinAlgError as e:
        raise ValueError("The Vandermonde matrix is singular (repeated x or ill-conditioned).") from e

    return {
        "coeficientes": [float(v) for v in coef],
        "V": _to_2d_list(V),
        "polinomio": _poly_to_string(coef, "x", decimals),
        "grado": len(coef) - 1,
    }
