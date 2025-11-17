import numpy as np
import pandas as pd

def doolittle(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    logs = []


    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "matrix": pd.DataFrame(
                    np.column_stack((A, b)),
                    columns=[f"x{i+1}" for i in range(A.shape[1])] + ["b"]
                ).round(decimals),
                "message": f"Matrix A must be square. Received {A.shape[0]}x{A.shape[1]}."
            }]
        }

    if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "matrix": pd.DataFrame(
                    np.column_stack((A, b)),
                    columns=[f"x{i+1}" for i in range(A.shape[1])] + ["b"]
                ).round(decimals),
                "message": f"The size of vector b ({len(b)}) does not match the number of rows in A ({A.shape[0]})."
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
                "matrix": pd.DataFrame(
                    np.column_stack((A, b)),
                    columns=[f"x{i+1}" for i in range(n)] + ["b"]
                ).round(decimals),
                "message": "Matrix is not invertible (det ≈ 0)."
            }]
        }

    elif abs(det) < tolerance:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "matrix": pd.DataFrame(
                    np.column_stack((A, b)),
                    columns=[f"x{i+1}" for i in range(n)] + ["b"]
                ).round(decimals),
                "message": f"det(A) ≈ {det:.2e}. The system is ill-conditioned and may present numerical instability."
            }]
        }


    logs.append({
        "step": "Initial",
        "matrix": pd.DataFrame(
            np.column_stack((A, b)),
            columns=[f"x{i+1}" for i in range(n)] + ["b"]
        ).round(decimals),
        "message": f"Initial system. Determinant = {det:.4f}"
    })


    L = np.eye(n)
    U = np.zeros((n, n))

    for j in range(n):

        for k in range(j, n):
            U[j, k] = A[j, k] - np.sum(L[j, :j] * U[:j, k])


        for i in range(j + 1, n):
            if np.isclose(U[j, j], 0):
                return {
                    "solution": None,
                    "logs": logs + [{
                        "step": f"Step {j+1}",
                        "matrix": pd.DataFrame(
                            np.column_stack((A, b)),
                            columns=[f"x{i+1}" for i in range(n)] + ["b"]
                        ).round(decimals),
                        "message": f"Zero pivot at U[{j},{j}]. Method fails."
                    }]
                }
            L[i, j] = (A[i, j] - np.sum(L[i, :j] * U[:j, j])) / U[j, j]

        logs.append({
            "step": f"Step {j+1}",
            "L": pd.DataFrame(L).round(decimals),
            "U": pd.DataFrame(U).round(decimals),
            "message": f"Column {j+1} processed."
        })


    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - np.dot(L[i, :i], y[:i])

    logs.append({
        "step": "Forward Substitution",
        "message": "Forward substitution complete (Ly = b).",
        "y": pd.Series(y.round(decimals))
    })


    x = np.zeros(n)
    for i in reversed(range(n)):
        if np.isclose(U[i, i], 0):
            return {
                "solution": None,
                "logs": logs + [{
                    "step": "Backward Substitution",
                    "message": f"Zero pivot at U[{i},{i}]. Method fails."
                }]
            }
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
