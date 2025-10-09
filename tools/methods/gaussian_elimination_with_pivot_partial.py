import numpy as np

def gauss_partial(A: list, b: list, decimals: int):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

    det = np.linalg.det(A)
    if np.isclose(det, 0):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.round(decimals).tolist(),
                "b": b.round(decimals).tolist(),
                "message": "Matrix is not invertible (det ≈ 0)."
            }]
        }

    logs.append({
        "step": "Initial",
        "A": A.copy().round(decimals).tolist(),
        "b": b.copy().round(decimals).tolist(),
        "message": f"Initial system. Determinant = {det:.4f}"
    })

    for k in range(n - 1):

      
        max_row = np.argmax(np.abs(A[k:, k])) + k

        if np.allclose(A[k:, k], 0):
            return {
                "solution": None,
                "logs": logs + [{
                    "step": f"Iteration {k+1}",
                    "A": A.copy().round(decimals).tolist(),
                    "b": b.copy().round(decimals).tolist(),
                    "message": f"All entries in column {k+1} from row {k+1} down are zero. Method fails."
                }]
            }


        if np.isclose(A[max_row, k], 0):
            return {
                "solution": None,
                "logs": logs + [{
                    "step": f"Iteration {k+1}",
                    "A": A.copy().round(decimals).tolist(),
                    "b": b.copy().round(decimals).tolist(),
                    "message": f"No non-zero pivot found in column {k+1}. Method fails."
                }]
            }


        if max_row != k:
            A[[k, max_row]] = A[[max_row, k]]
            b[[k, max_row]] = b[[max_row, k]]
            logs.append({
                "step": f"Pivot {k+1}",
                "A": A.copy().round(decimals).tolist(),
                "b": b.copy().round(decimals).tolist(),
                "message": f"Rows {k+1} and {max_row+1} swapped for partial pivoting."
            })


        if np.allclose(A[k+1:, k], 0):
            logs.append({
                "step": f"Iteration {k+1}",
                "A": A.copy().round(decimals).tolist(),
                "b": b.copy().round(decimals).tolist(),
                "message": f"Column {k+1} below pivot already zeros. Skipping elimination."
            })
            continue


        for i in range(k + 1, n):
            if np.isclose(A[i, k], 0):
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
        if np.isclose(A[i, i], 0):
            return {
                "solution": None,
                "logs": logs + [{
                    "step": "Back Substitution",
                    "A": A.copy().round(decimals).tolist(),
                    "b": b.copy().round(decimals).tolist(),
                    "message": f"Zero (or near-zero) pivot at row {i+1}. Method fails."
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
    """Print the matrix A with the vector b"""
    for row, bi in zip(A, b):
        row_str = "  ".join(f"{val:.{decimals}f}" for val in row)
        print(f"{row_str} | {bi:.{decimals}f}")
