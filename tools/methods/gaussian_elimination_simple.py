import numpy as np
import pandas as pd

def gauss_simple(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    logs = []

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
                "message": f"The size of vector b ({len(b)}) does not match the number of rows in A ({A.shape[0]})."
            }]
        }

    n = len(b)
    det = np.linalg.det(A)

# Tolerancia para considerar el determinante "cercano a cero"
    tolerance = 1e-10

    if det == 0:
        return {
        "solution": None,
        "logs": [{
            "step": "Check",
            "A": pd.DataFrame(A).round(decimals),
            "b": pd.Series(b).round(decimals),
            "message": "det(A) = 0. The matrix is singular. The system may have no unique solution or the system does not have solution."
        }]
    }

    elif abs(det) < tolerance:
        return {
        "solution": None,
        "logs": [{
            "step": "Check",
            "A": pd.DataFrame(A).round(decimals),
            "b": pd.Series(b).round(decimals),
            "message": f"det(A) ≈ {det:.2e}, the system is ill-conditioned and may present numerical instability."
        }]
    }


    logs.append({
        "step": "Initial",
        "matrix": pd.DataFrame(np.column_stack((A, b)), 
                               columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
        "message": f"Initial system. Determinant = {det:.4f}"
    })

    # Eliminación progresiva
    for k in range(n - 1):
        pivot = A[k, k]

        if pivot == 0:
            logs.append({
                "step": f"Iteration {k+1}",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": f"Pivot at row {k+1} is zero. Method fails."
            })
            return {"solution": None, "logs": logs}

        # Comprobación de pivote pequeño
        if abs(pivot) < 1e-7:
            logs.append({
                "step": f"Iteration {k+1}",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": f"Warning: Pivot at row {k+1} is very small ({pivot:.2e}). Numerical instability may occur."
            })

        for i in range(k + 1, n):
            if A[i, k] == 0:
                continue
            m = A[i, k] / pivot
            A[i, k:] -= m * A[k, k:]
            b[i] -= m * b[k]

        logs.append({
            "step": f"Iteration {k+1}",
            "matrix": pd.DataFrame(np.column_stack((A, b)),
                                   columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
            "message": f"Elimination at column {k+1} complete."
        })

    # Sustitución regresiva
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if A[i, i] == 0:
            logs.append({
                "step": "Back Substitution",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": f"Zero pivot at row {i+1}. Method fails."
            })
            return {"solution": None, "logs": logs}
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]

    logs.append({
        "step": "Back Substitution",
        "matrix": pd.DataFrame(np.column_stack((A, b)),
                               columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
        "message": "Back substitution complete."
    })

    return {
        "solution": x.round(decimals).tolist(),
        "logs": logs
    }
