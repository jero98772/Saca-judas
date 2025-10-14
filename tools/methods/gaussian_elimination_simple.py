import numpy as np

def gauss_simple(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    logs = []

    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.tolist(),
                "b": b.tolist(),
                "message": f"Matrix A must be square. Received {A.shape[0]}x{A.shape[1]}."
            }]
        }


    if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.tolist(),
                "b": b.tolist(),
                "message": f"The size of vector b ({len(b)}) does not match the number of rows in A ({A.shape[0]})."
            }]
        }


    n = len(b)
    det = np.linalg.det(A)
    if np.isclose(det, 0):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.round(decimals).tolist(),
                "b": b.round(decimals).tolist(),
                "message": "det(A) ≈ 0, solutions can be unstable by higher divisions."
            }]
        }


    logs.append({
        "step": "Initial",
        "A": A.copy().round(decimals).tolist(),
        "b": b.copy().round(decimals).tolist(),
        "message": f"Initial system. Determinant = {det:.4f}"
    })

    
    for k in range(n - 1):
        if A[k, k] == 0:
            return {
                "solution": None,
                "logs": logs + [{
                    "step": f"Iteration {k+1}",
                    "A": A.copy().round(decimals).tolist(),
                    "b": b.copy().round(decimals).tolist(),
                    "message": f"Pivot at row {k+1} is zero. Method fails."
                }]
            }

        for i in range(k + 1, n):
            if A[i, k] == 0:
                continue
            m = A[i, k] / A[k, k]
            A[i, k:] = A[i, k:] - m * A[k, k:]
            b[i] = b[i] - m * b[k]


        logs.append({
            "step": f"Iteration {k+1}",
            "A": A.copy().round(decimals).tolist(),
            "b": b.copy().round(decimals).tolist(),
            "message": f"Elimination at column {k+1} complete."
        })


    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if A[i, i] == 0:
            return {
                "solution": None,
                "logs": logs + [{
                    "step": "Back Substitution",
                    "A": A.copy().round(decimals).tolist(),
                    "b": b.copy().round(decimals).tolist(),
                    "message": f"Zero pivot at row {i+1}. Method fails."
                }]
            }
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]

    logs.append({
        "step": "Back Substitution",
        "A": A.copy().round(decimals).tolist(),
        "b": b.copy().round(decimals).tolist(),
        "message": "Back substitution complete."
    })

    return {
        "solution": x.round(decimals).tolist(),
        "logs": logs
    }


def print_augmented_matrix(A, b, decimals):
    "Print the matrix A with the vector b"
    for row, bi in zip(A, b):
        row_str = "  ".join(f"{val:.{decimals}f}" for val in row)
        print(f"{row_str} | {bi:.{decimals}f}")