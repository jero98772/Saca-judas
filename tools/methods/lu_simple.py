import numpy as np
import pandas as pd

def lu_simple(A: list, b: list, decimals: int = 6):
    """
    LU Factorization using simple (no) pivoting.
    Returns:
        solution -> vector x
        logs     -> detailed logs with matrices and messages
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    logs = []

    # --- Validations ---
    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": pd.DataFrame(A).round(decimals),
                "b": pd.Series(b).round(decimals),
                "message": f"Matrix A must be square. Received {A.shape[0]}x{A.shape[1]}."
            }]
        }

    if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": pd.DataFrame(A).round(decimals),
                "b": pd.Series(b).round(decimals),
                "message": f"Vector b size ({len(b)}) does not match matrix A rows ({A.shape[0]})."
            }]
        }

    n = len(b)
    det = np.linalg.det(A)
    tolerance = 1e-10

    if np.isclose(det, 0):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": pd.DataFrame(A).round(decimals),
                "b": pd.Series(b).round(decimals),
                "message": "det(A) ≈ 0. Matrix is singular or nearly singular."
            }]
        }

    elif abs(det) < tolerance:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": pd.DataFrame(A).round(decimals),
                "b": pd.Series(b).round(decimals),
                "message": f"det(A) ≈ {det:.2e}. The system may be ill-conditioned."
            }]
        }

    logs.append({
        "step": "Initial",
        "matrix": pd.DataFrame(np.column_stack((A, b)),
                               columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
        "message": f"Initial system. Determinant = {det:.4f}"
    })

    # --- Initialization ---
    L = np.eye(n)
    U = A.copy()

    # --- LU Factorization (no pivoting) ---
    for k in range(n - 1):
        pivot = U[k, k]

        if np.isclose(pivot, 0):
            logs.append({
                "step": f"Iteration {k+1}",
                "U": pd.DataFrame(U).round(decimals),
                "L": pd.DataFrame(L).round(decimals),
                "message": f"Zero pivot at row {k+1}. Method fails (no pivoting allowed)."
            })
            return {"solution": None, "logs": logs}

        # Compute multipliers and eliminate
        for i in range(k + 1, n):
            L[i, k] = U[i, k] / pivot
            U[i, k:] -= L[i, k] * U[k, k:]
            U[i, k] = 0  # Clean lower elements explicitly

        logs.append({
            "step": f"Iteration {k+1}",
            "U": pd.DataFrame(U).round(decimals),
            "L": pd.DataFrame(L).round(decimals),
            "message": f"Elimination at column {k+1} complete."
        })

    # --- Forward substitution: Ly = b ---
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - np.dot(L[i, :i], y[:i])

    logs.append({
        "step": "Forward Substitution",
        "message": "Forward substitution complete (Ly = b).",
        "y": pd.Series(y.round(decimals))
    })

    # --- Backward substitution: Ux = y ---
    x = np.zeros(n)
    for i in reversed(range(n)):
        if np.isclose(U[i, i], 0):
            logs.append({
                "step": "Backward Substitution",
                "U": pd.DataFrame(U).round(decimals),
                "message": f"Zero pivot at row {i+1}. Cannot solve."
            })
            return {"solution": None, "logs": logs}
        x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i, i]

    logs.append({
        "step": "Backward Substitution",
        "message": "Backward substitution complete (Ux = y).",
        "x": pd.Series(x.round(decimals))
    })

    return {
        "solution": x.round(decimals).tolist(),
        "logs": logs
    }
