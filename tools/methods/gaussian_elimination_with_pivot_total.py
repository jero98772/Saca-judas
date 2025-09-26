import numpy as np

def gauss_pivot_total(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

    col_order = list(range(n))

    # Determinant check
    det = np.linalg.det(A)
    if det == 0:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.round(decimals).tolist(),
                "b": b.round(decimals).tolist(),
                "message": "Matrix is not invertible (det = 0)."
            }]
        }

    logs.append({
        "step": "Initial",
        "A": A.round(decimals).tolist(),
        "b": b.round(decimals).tolist(),
        "message": f"Initial system. Determinant = {det:.4f}"
    })

    for k in range(n - 1):
        # --- Total pivoting: find the largest absolute value in the submatrix A[k:, k:] ---
        sub_matrix = np.abs(A[k:, k:])
        max_idx = np.unravel_index(np.argmax(sub_matrix), sub_matrix.shape)
        max_row = max_idx[0] + k
        max_col = max_idx[1] + k

        if A[max_row, max_col] == 0:
            return {
                "solution": None,
                "logs": logs + [{
                    "step": f"Iteration {k+1}",
                    "A": A.round(decimals).tolist(),
                    "b": b.round(decimals).tolist(),
                    "message": "All pivots in submatrix are zero. Method fails."
                }]
            }

        # Swap rows if needed
        if max_row != k:
            A[[k, max_row]] = A[[max_row, k]]
            b[[k, max_row]] = b[[max_row, k]]
            logs.append({
                "step": f"Iteration {k+1} - Pivoting Row",
                "A": A.round(decimals).tolist(),
                "b": b.round(decimals).tolist(),
                "message": f"Swapped row {k+1} with row {max_row+1}."
            })

        # Swap columns if needed
        if max_col != k:
            A[:, [k, max_col]] = A[:, [max_col, k]]
            col_order[k], col_order[max_col] = col_order[max_col], col_order[k]
            logs.append({
                "step": f"Iteration {k+1} - Pivoting Column",
                "A": A.round(decimals).tolist(),
                "b": b.round(decimals).tolist(),
                "message": f"Swapped column {k+1} with column {max_col+1}."
            })

        # Forward elimination
        for i in range(k + 1, n):
            if A[i, k] == 0:
                continue
            m = A[i, k] / A[k, k]
            A[i, k:] -= m * A[k, k:]
            b[i] -= m * b[k]

        logs.append({
            "step": f"Iteration {k+1}",
            "A": A.round(decimals).tolist(),
            "b": b.round(decimals).tolist(),
            "message": f"Elimination at column {k+1} complete."
        })

    # Back substitution
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if A[i, i] == 0:
            return {
                "solution": None,
                "logs": logs + [{
                    "step": "Back Substitution",
                    "A": A.round(decimals).tolist(),
                    "b": b.round(decimals).tolist(),
                    "message": f"Zero pivot at row {i+1}. Method fails."
                }]
            }
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]

    # Reorder solution according to column swaps
    x_final = np.zeros(n)
    for i, col in enumerate(col_order):
        x_final[col] = x[i]

    logs.append({
        "step": "Back Substitution",
        "A": A.round(decimals).tolist(),
        "b": b.round(decimals).tolist(),
        "message": "Back substitution complete. Solution reordered according to column swaps."
    })

    return {
        "solution": x_final.round(decimals).tolist(),
        "logs": logs
    }


def gaussian_elimination_with_pivot_total_controller(A: list, b: list, decimals: int = 6):
    """
    Controller for Gaussian elimination with total pivoting.
    """
    result = gauss_total(A, b, decimals)

    if result.get("solution") is not None:
        result["message"] = "Gaussian elimination with total pivoting completed successfully."
    else:
        result["message"] = "Gaussian elimination with total pivoting failed."

    return result
