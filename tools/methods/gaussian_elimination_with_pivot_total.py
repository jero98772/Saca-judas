import numpy as np
import pandas as pd

def gauss_total(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    logs = []

    # --- Verificaciones iniciales ---
    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{ 
                "step": "Check",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(A.shape[1])] + ["b"]).round(decimals),
                "message": f"Matrix A must be square. Received {A.shape[0]}x{A.shape[1]}."
            }]
        }

    if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(A.shape[1])] + ["b"]).round(decimals),
                "message": f"The size of vector b ({len(b)}) does not match the number of rows in A ({A.shape[0]})."
            }]
        }

    n = len(b)
    marks = np.arange(n)

    # --- Determinante y estabilidad ---
    det = np.linalg.det(A)
    tolerance = 1e-10

    if np.isclose(det, 0):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": "det(A) = 0. The matrix is singular. The system may have no unique solution or no solution at all."
            }]
        }

    elif abs(det) < tolerance:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": f"det(A) ≈ {det:.2e}, the system is ill-conditioned and may present numerical instability."
            }]
        }

    # --- Registro inicial ---
    logs.append({
        "step": "Initial",
        "matrix": pd.DataFrame(np.column_stack((A, b)),
                               columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
        "message": f"Initial system. Determinant = {det:.4f}"
    })

    # --- Eliminación Gaussiana con pivoteo total ---
    for k in range(n - 1):
        submatrix = np.abs(A[k:, k:])
        p, q = np.unravel_index(np.argmax(submatrix), submatrix.shape)
        p += k
        q += k

        if np.isclose(A[p, q], 0):
            logs.append({
                "step": f"Iteration {k+1}",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": f"No non-zero pivot found near position ({p+1},{q+1}). Method fails."
            })
            return {"solution": None, "logs": logs}

        # --- Intercambio de columnas y filas ---
        if q != k:
            A[:, [k, q]] = A[:, [q, k]]
            marks[[k, q]] = marks[[q, k]]

        if p != k:
            A[[k, p], :] = A[[p, k], :]
            b[[k, p]] = b[[p, k]]

        logs.append({
            "step": f"Pivot {k+1}",
            "matrix": pd.DataFrame(np.column_stack((A, b)),
                                   columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
            "message": f"Swapped column {k+1} ↔ {q+1} and row {k+1} ↔ {p+1} for total pivoting."
        })

        pivot = A[k, k]
        if abs(pivot) < 1e-7:
            logs.append({
                "step": f"Iteration {k+1}",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": f"Warning: Pivot at position ({k+1},{k+1}) is very small ({pivot:.2e}). Numerical instability may occur."
            })

        # --- Eliminación hacia adelante ---
        for i in range(k + 1, n):
            if np.isclose(A[i, k], 0):
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

    # --- Sustitución regresiva ---
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if np.isclose(A[i, i], 0):
            logs.append({
                "step": "Back Substitution",
                "matrix": pd.DataFrame(np.column_stack((A, b)),
                                       columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
                "message": f"Zero (or near-zero) pivot at row {i+1}. Method fails."
            })
            return {"solution": None, "logs": logs}

        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]

    # --- Reordenar las variables según los intercambios de columnas ---
    x_final = np.zeros(n)
    for i in range(n):
        x_final[marks[i]] = x[i]

    logs.append({
        "step": "Back Substitution",
        "matrix": pd.DataFrame(np.column_stack((A, b)),
                               columns=[f"x{i+1}" for i in range(n)] + ["b"]).round(decimals),
        "message": "Back substitution complete."
    })

    return {
        "solution": x_final.round(decimals).tolist(),
        "logs": logs
    }
