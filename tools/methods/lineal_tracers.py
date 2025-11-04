# tools/methods/lineal_tracers.py
# -*- coding: utf-8 -*-
"""
Trazadores lineales (spline lineal) — usa TU implementación si existe
(por ejemplo en tools/methods/Trazadores_lineales_mio.py) y la envuelve para
devolver un dict JSON-friendly que consume la web.

Exporta:
- compute_trazadores_lineales(x, y, decimals=6) -> dict con:
  {
    "tramos": [
      {"intervalo": [xi, xi1], "pendiente": m, "intercepto": b}
    ],
    "ecuaciones": ["S0(x) = ...", "S1(x) = ...", ...],
    "x": [...], "y": [...]
  }
"""

from typing import List, Dict, Any, Optional, Callable
import numpy as np
import importlib
import inspect


# ========= dónde buscar TU módulo / función =========
CANDIDATE_MODULES = [
    "tools.methods.Trazadores_lineales_mio",
    "tools.methods.trazadores_lineales_mio",
    "tools.methods.lineal_tracers_mio",
    # por si lo dejaste en la raíz del repo
    "Trazadores_lineales_mio",
    "trazadores_lineales_mio",
    "lineal_tracers_mio",
]

MAIN_FUNC_NAMES = [
    # nombres típicos que podrías haber usado
    "trazadores_lineales_mio",
    "trazadores_lineales",
    "lineal_tracers_mio",
    "lineal_tracers",
    "spline_lineal",
    "spline_lineales",
    "construir_trazadores_lineales",
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

def _normalize_result_from_user(out, x: List[float], y: List[float], decimals: int) -> Dict[str, Any]:
    """
    Acepta varias formas de retorno (dict, tuplas/listas) y normaliza a:
    {
      "tramos": [{"intervalo":[xi,xi1], "pendiente":m, "intercepto":b}, ...],
      "ecuaciones": ["S0(x) = ...", ...],
      "x": x, "y": y
    }
    """
    def fmt_num(v: float) -> float:
        v = float(v)
        # no redondeo duro aquí; dejo el float tal cual para que el frontend decida cómo mostrar
        return v

    def tramo_str(i, m, b, xi, xi1):
        # S_i(x) = m x + b, x in [xi, xi1]
        m_s = f"{m:.{decimals}f}".rstrip("0").rstrip(".") or "0"
        b_s = f"{b:.{decimals}f}".rstrip("0").rstrip(".") or "0"
        return f"S{i}(x) = {m_s} x + {b_s},  x ∈ [{xi}, {xi1}]"

    res: Dict[str, Any] = {"x": list(map(float, x)), "y": list(map(float, y))}
    tramos = []
    ecuaciones = []

    # Caso 1: ya viene dict con claves conocidas
    if isinstance(out, dict):
        # posibles nombres:
        segs = out.get("tramos") or out.get("segments") or out.get("spline") or out.get("S")
        m_list = out.get("pendientes") or out.get("m") or out.get("slopes")
        b_list = out.get("interceptos") or out.get("b") or out.get("intercepts")
        eq_list = out.get("ecuaciones") or out.get("equations")

        if segs and isinstance(segs, list):
            # cada seg puede ser dict {"intervalo":[xi,xi1], "pendiente":m, "intercepto":b}
            for i, seg in enumerate(segs):
                if isinstance(seg, dict):
                    xi, xi1 = seg.get("intervalo", [x[i], x[i+1]])
                    m = seg.get("pendiente")
                    b = seg.get("intercepto")
                else:
                    # o forma [xi, xi1, m, b]
                    xi, xi1, m, b = seg
                tramos.append({"intervalo": [fmt_num(xi), fmt_num(xi1)],
                               "pendiente": fmt_num(m), "intercepto": fmt_num(b)})
                ecuaciones.append(tramo_str(i, float(m), float(b), float(xi), float(xi1)))

        elif m_list is not None and b_list is not None:
            # construir a partir de m y b
            m_list = list(map(float, m_list))
            b_list = list(map(float, b_list))
            for i in range(len(m_list)):
                xi, xi1 = float(x[i]), float(x[i+1])
                m, b = m_list[i], b_list[i]
                tramos.append({"intervalo": [xi, xi1], "pendiente": m, "intercepto": b})
                ecuaciones.append(tramo_str(i, m, b, xi, xi1))

        if eq_list and not ecuaciones:
            ecuaciones = list(map(str, eq_list))

        if tramos:
            res["tramos"] = tramos
        if ecuaciones:
            res["ecuaciones"] = ecuaciones

        return res

    # Caso 2: tupla/lista: [(m0,b0), (m1,b1), ...] o (m_list, b_list) o similar
    if isinstance(out, (list, tuple)):
        # (a) lista de pares (m,b) por tramo
        if out and all(isinstance(t, (list, tuple)) and len(t) >= 2 for t in out) and not isinstance(out[0], (float, int)):
            for i, t in enumerate(out):
                m, b = float(t[0]), float(t[1])
                xi, xi1 = float(x[i]), float(x[i+1])
                tramos.append({"intervalo": [xi, xi1], "pendiente": m, "intercepto": b})
                ecuaciones.append(tramo_str(i, m, b, xi, xi1))

        # (b) (m_list, b_list)
        elif len(out) >= 2 and isinstance(out[0], (list, tuple)) and isinstance(out[1], (list, tuple)):
            m_list = list(map(float, out[0]))
            b_list = list(map(float, out[1]))
            for i in range(len(m_list)):
                xi, xi1 = float(x[i]), float(x[i+1])
                m, b = m_list[i], b_list[i]
                tramos.append({"intervalo": [xi, xi1], "pendiente": m, "intercepto": b})
                ecuaciones.append(tramo_str(i, m, b, xi, xi1))

        if tramos:
            res["tramos"] = tramos
            res["ecuaciones"] = ecuaciones
            return res

    # si no pude normalizar, devuelvo lo que haya
    res["detalle"] = out
    return res


def _fallback_compute(x: List[float], y: List[float], decimals: int) -> Dict[str, Any]:
    """
    Fallback simple: arma el spline lineal con m_i = (y_{i+1} - y_i)/(x_{i+1}-x_i) y b_i = y_i - m_i x_i.
    """
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)
    n = len(x_arr)
    tramos = []
    ecuaciones = []
    for i in range(n-1):
        dx = x_arr[i+1] - x_arr[i]
        if abs(dx) < 1e-15:
            raise ValueError("Hay puntos x repetidos; no se puede construir el trazador lineal.")
        m = (y_arr[i+1] - y_arr[i]) / dx
        b = y_arr[i] - m * x_arr[i]
        tramos.append({"intervalo": [float(x_arr[i]), float(x_arr[i+1])],
                       "pendiente": float(m), "intercepto": float(b)})
        # string
        m_s = f"{m:.{decimals}f}".rstrip("0").rstrip(".") or "0"
        b_s = f"{b:.{decimals}f}".rstrip("0").rstrip(".") or "0"
        ecuaciones.append(f"S{i}(x) = {m_s} x + {b_s},  x ∈ [{x_arr[i]}, {x_arr[i+1]}]")

    return {"tramos": tramos, "ecuaciones": ecuaciones, "x": list(map(float, x)), "y": list(map(float, y))}


# ========= API principal (usada por FastAPI) =========
def compute_trazadores_lineales(x: List[float], y: List[float], decimals: int = 6) -> Dict[str, Any]:
    """
    Usa TU implementación si está disponible; si no, aplica un fallback lineal estándar.
    """
    if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) >= 2):
        raise ValueError("x e y deben ser listas del mismo tamaño (>= 2).")
    # sugerencia: x estrictamente creciente
    if any((x[i+1] - x[i]) == 0 for i in range(len(x)-1)):
        raise ValueError("Hay valores de x repetidos; los trazadores requieren x estrictamente crecientes.")

    # 1) intenta cargar tu módulo
    user_mod = _import_first(CANDIDATE_MODULES)

    # 2) intenta tu función principal
    user_main = _get_first_callable(user_mod, MAIN_FUNC_NAMES) if user_mod else None
    if user_main:
        # Firma típica: f(x, y) ó f(x, y, decimals) ó f(x, y, True)
        sig = inspect.signature(user_main)
        params = list(sig.parameters.keys())
        tries = []
        if len(params) >= 2:
            tries.append((x, y))
        if len(params) >= 3:
            tries.append((x, y, decimals))
            tries.append((x, y, True))

        for args in tries:
            try:
                out = user_main(*args)
                return _normalize_result_from_user(out, x, y, decimals)
            except Exception:
                continue
        # si no hubo suerte con las firmas, caemos al fallback
        return _fallback_compute(x, y, decimals)

    # 3) fallback (no encontré tu módulo/función)
    return _fallback_compute(x, y, decimals)
