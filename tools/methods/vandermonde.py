# tools/methods/vandermonde.py
# -*- coding: utf-8 -*-
"""
Interpolación con matriz de Vandermonde — usa TU implementación si existe
(por ejemplo en tools/methods/Vandermonde_mio.py o vandermonde_mio.py) y
solo la envuelve para retornar un dict JSON-friendly.

Exporta:
- compute_vandermonde(x, y, decimals=6) -> dict con:
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

# ========= CANDIDATOS: módulo y nombres que podría tener tu función =========
CANDIDATE_MODULES = [
    "tools.methods.Vandermonde_mio",
    "tools.methods.vandermonde_mio",
    "tools.methods.vandermonde_user",
    # por si lo dejaste en la raíz del proyecto:
    "Vandermonde_mio",
    "vandermonde_mio",
    "vandermonde_user",
]

MAIN_FUNC_NAMES = [
    # funciones que podrían devolver coeficientes, V y/o dict:
    "vandermonde_mio",
    "resolver_vandermonde",
    "interpolacion_vandermonde",
    "calcular_vandermonde",
    "calc_vandermonde",
    "compute_vandermonde_mio",
]

V_ONLY_FUNC_NAMES = [
    # funciones que quizá solo construyen la matriz de Vandermonde:
    "matriz_vandermonde",
    "construir_vandermonde",
    "build_vandermonde",
]

# ========= utilidades de soporte (no reemplazan tu lógica) =========
def _to_2d_list(M: np.ndarray):
    return [[float(c) for c in row] for row in M]

def _vandermonde_matrix(x: List[float], n: Optional[int] = None) -> np.ndarray:
    x_arr = np.array(x, dtype=float)
    if n is None:
        n = len(x_arr)
    return np.vander(x_arr, N=n, increasing=False)  # [1, x, x^2, ...]

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
    Intenta varias firmas comunes para TU función:
      - fn(x, y)
      - fn(x, y, decimals)
      - fn(x, y, True/False)
    Acepta retornos: dict, (coef,), (coef, V), (coef, V, poly), etc.
    Normaliza a un dict estándar.
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.keys())

    tries = []
    if len(params) >= 2:
        tries.append((x, y))
    if len(params) >= 3:
        # primero intentamos con decimals por si tu función lo usa
        tries.append((x, y, decimals))
        # alternativa booleana (track/verbose/etc.)
        tries.append((x, y, True))

    for args in tries:
        try:
            out = fn(*args)
            # 1) si ya es dict con nuestras claves
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

            # 2) si es tupla/lista con varias salidas
            if isinstance(out, (list, tuple)):
                coef = None
                V = None
                poly = None
                # mapea por longitud:
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

    raise RuntimeError("No se pudo invocar tu función de Vandermonde con firmas conocidas.")

def _call_user_V_only(fnV: Callable, x: List[float], y: List[float], decimals: int) -> Dict[str, Any]:
    """
    Si tu módulo solo expone la construcción de V, la usamos y resolvemos coeficientes.
    Soporta firmas fnV(x) o fnV(x, n).
    """
    n = len(x)
    try:
        # intentos típicos
        try:
            V = fnV(x, n)  # firma: (x, n)
        except TypeError:
            V = fnV(x)     # firma: (x)
        V = np.array(V, dtype=float)
    except Exception:
        # si falla, construimos nosotros
        V = _vandermonde_matrix(x, n)

    # resolver V a = y
    try:
        coef = np.linalg.solve(V, np.array(y, dtype=float))
    except np.linalg.LinAlgError as e:
        raise ValueError("La matriz de Vandermonde es singular (x repetidos o mal condicionados).") from e

    return {
        "coeficientes": [float(v) for v in coef],
        "V": _to_2d_list(V),
        "polinomio": _poly_to_string(coef, "x", decimals),
        "grado": len(coef) - 1,
    }

# ========= API principal (usada por FastAPI) =========
def compute_vandermonde(x: List[float], y: List[float], decimals: int = 6) -> Dict[str, Any]:
    """
    Usa TU implementación si está disponible; si no, resuelve con fallback
    (sin romper la app).
    """
    if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) >= 2):
        raise ValueError("x e y deben ser listas no vacías del mismo tamaño (>= 2).")

    # 1) intenta cargar tu módulo
    user_mod = _import_first(CANDIDATE_MODULES)

    # 2) si hay función principal de usuario, úsala
    user_main = _get_first_callable(user_mod, MAIN_FUNC_NAMES) if user_mod else None
    if user_main:
        return _call_user_main(user_main, x, y, decimals)

    # 3) si solo hay función de matriz V, úsala y resuelve
    user_vonly = _get_first_callable(user_mod, V_ONLY_FUNC_NAMES) if user_mod else None
    if user_vonly:
        return _call_user_V_only(user_vonly, x, y, decimals)

    # 4) fallback (por si no metiste aún tu módulo): resolvemos directo
    V = _vandermonde_matrix(x)
    try:
        coef = np.linalg.solve(V, np.array(y, dtype=float))
    except np.linalg.LinAlgError as e:
        raise ValueError("La matriz de Vandermonde es singular (x repetidos o mal condicionados).") from e

    return {
        "coeficientes": [float(v) for v in coef],
        "V": _to_2d_list(V),
        "polinomio": _poly_to_string(coef, "x", decimals),
        "grado": len(coef) - 1,
    }
