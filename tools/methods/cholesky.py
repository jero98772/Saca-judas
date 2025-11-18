# tools/methods/cholesky.py
# -*- coding: utf-8 -*-
"""
Cholesky decomposition — uses YOUR implementation if it exists
(e.g. tools/methods/cholesky_mio.py) and wraps it to return a JSON-friendly dict.

Exports:
- compute_cholesky(A, b, track_etapas=True) -> {
    "x": [...],
    "L": [[...], ...],
    "Lt": [[...], ...],
    "y": [...],
    "etapas": [ {"matrix": [[...], ...]}, ... ]   # optional if your code provides them
}
"""

from typing import List, Dict, Any, Optional, Callable
import numpy as np
import importlib
import inspect

# ====== We try to use your module and common names ======
CANDIDATE_MODULES = [
    "tools.methods.cholesky_mio",
    # in case you left it at project root:
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


# ====== minimal utilities (used only if your module does not provide these) ======
def _forward_substitution(L: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = L.shape[0]
    y = np.zeros(n, dtype=float)
    for i in range(n):
        s = b[i] - (L[i, :i] @ y[:i] if i > 0 else 0.0)
        if abs(L[i, i]) < 1e-15:
            raise ValueError("Lower triangular matrix is singular in forward substitution.")
        y[i] = s / L[i, i]
    return y


def _back_substitution(U: np.ndarray, y: np.ndarray) -> np.ndarray:
    n = U.shape[0]
    x = np.zeros(n, dtype=float)
    for i in range(n - 1, -1, -1):
        s = y[i] - (U[i, i + 1:] @ x[i + 1:] if i < n - 1 else 0.0)
        if abs(U[i, i]) < 1e-15:
            raise ValueError("Upper triangular matrix is singular in back substitution.")
        x[i] = s / U[i, i]
    return x


def _to_list(M: np.ndarray):
    return M.astype(float).tolist()


def _call_user_cholesky(fn: Callable, A: np.ndarray):
    """
    Tries common signatures:
      - fn(A) -> L
      - fn(A, True/False) -> L (and maybe etapas)
    Returns (L, etapas | None)
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
            # if it returns L directly
            if isinstance(out, (list, np.ndarray)):
                L = np.array(out, dtype=float)
                return L, None
            # if it returns tuple (L, etapas?) or dict
            if isinstance(out, tuple):
                L = np.array(out[0], dtype=float)
                etapas = out[1] if len(out) > 1 else None
                return L, etapas
            if isinstance(out, dict):
                # try to detect 'L' and 'etapas'
                L = np.array(out.get("L"), dtype=float)
                etapas = out.get("etapas")
                return L, etapas
        except Exception:
            continue
    raise RuntimeError("Could not call your Cholesky function with known signatures.")


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


# ====== COMPLEX formatting helpers (for detailed fallback) ======
def _format_complex(z, tol=1e-12) -> str:
    """Returns a neat string for real/complex numbers (e.g. '1.937106i')."""
    z = complex(z)
    r, im = z.real, z.imag

    if abs(im) < tol:  # almost real
        return f"{r:.6f}"
    if abs(r) < tol:   # almost purely imaginary
        sign = '' if im >= 0 else '-'
        return f"{sign}{abs(im):.6f}i"
    # real + imaginary part
    sign = '+' if im >= 0 else '-'
    return f"{r:.6f}{sign}{abs(im):.6f}i"


def _matrix_to_list_complex(M: np.ndarray):
    """Converts a matrix (real or complex) to a list of lists of strings."""
    M = np.asarray(M)
    out = []
    for i in range(M.shape[0]):
        row = []
        for j in range(M.shape[1]):
            row.append(_format_complex(M[i, j]))
        out.append(row)
    return out


def _vector_to_list_complex(v: np.ndarray):
    v = np.asarray(v).reshape(-1)
    return [_format_complex(x) for x in v]


def _cholesky_complex_with_steps(A_real: np.ndarray, b_real: np.ndarray) -> Dict[str, Any]:
    """
    Fallback: complex Cholesky with steps (L/U, original matrix, etc.).
    It does NOT raise an error if A is not SPD; it just records 'error' in the dict.
    """
    A = A_real.astype(np.complex128)
    b = b_real.astype(np.complex128).reshape(-1)

    n = A.shape[0]
    L = np.zeros_like(A, dtype=np.complex128)
    etapas = []
    error_msg = ""

    # Step 0: original matrix
    etapas.append({
        "k": 0,
        "A": _matrix_to_list_complex(A)
    })

    # Cholesky algorithm allowing complex numbers
    for k in range(n):
        # diagonal element
        s = 0.0 + 0.0j
        for j in range(k):
            s += L[k, j] * np.conj(L[k, j])
        diag_val = A[k, k] - s

        # SPD check: if diag.real <= 0, we mark error but continue
        if diag_val.real <= 0 and not error_msg:
            error_msg = "A is not symmetric positive definite (Cholesky failed)."

        L[k, k] = np.sqrt(diag_val)

        # lower columns
        for i in range(k + 1, n):
            s2 = 0.0 + 0.0j
            for j in range(k):
                s2 += L[i, j] * np.conj(L[k, j])
            L[i, k] = (A[i, k] - s2) / L[k, k]

        # Save step k+1 with L and U
        L_stage = L.copy()
        U_stage = L_stage.conj().T
        etapas.append({
            "k": k + 1,
            "L": _matrix_to_list_complex(L_stage),
            "U": _matrix_to_list_complex(U_stage)
        })

    # Solve system A x = b using L and Lᴴ
    # Ly = b
    y = np.linalg.solve(L, b)
    # Lᴴ x = y
    x = np.linalg.solve(L.conj().T, y)

    result: Dict[str, Any] = {
        "x": _vector_to_list_complex(x),
        "y": _vector_to_list_complex(y),
        "L": _matrix_to_list_complex(L),
        "Lt": _matrix_to_list_complex(L.conj().T),
        "etapas": etapas,
    }
    if error_msg:
        result["error"] = error_msg
    return result


# ====== main API (used by FastAPI) ======
def compute_cholesky(A: List[List[float]], b: List[float], track_etapas: bool = True) -> Dict[str, Any]:
    """
    Uses YOUR Cholesky decomposition to solve Ax=b.
    Returns a dict with x, L, Lt (=L.T), y and etapas (if available).

    If your module is not found or fails, it falls back to:
    - complex Cholesky with steps (L/U per step, including non-SPD cases).
    """
    if not isinstance(A, list) or not A or not all(isinstance(r, list) for r in A):
        raise ValueError("A must be a non-empty list of lists.")
    n = len(A)
    if any(len(r) != n for r in A):
        raise ValueError("A must be square.")
    if not isinstance(b, list) or len(b) != n:
        raise ValueError("b must have length n.")

    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)

    # 1) try to use your module/function as BEFORE
    user_mod = _import_first(CANDIDATE_MODULES)
    L = None
    etapas = None

    if user_mod:
        user_fn = _get_first_callable(user_mod, CHOLESKY_FUNC_NAMES)
        if user_fn:
            try:
                L, etapas = _call_user_cholesky(user_fn, A_np)
            except Exception:
                L, etapas = None, None

    # 2) if there is no module or it failed -> COMPLEX fallback with steps
    if L is None:
        result = _cholesky_complex_with_steps(A_np, b_np)
        if not track_etapas and "etapas" in result:
            result.pop("etapas", None)
        return result

    # 3) if your module exists: use it with your substitutions / the fallbacks
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
