import numpy as np

def gauss_partial_pivoting(A: list, b: list, decimals: int = 6):
    """
    Gaussian Elimination with partial pivoting.
    Returns solution and detailed logs for each step.
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

    logs.append({
        "step": "Initial",
        "A": A.round(decimals).tolist(),
        "b": b.round(decimals).tolist(),
        "message": "Initial system."
    })

    # Forward elimination with partial pivoting
    for k in range(n - 1):
        # --- Partial pivoting ---
        max_row = np.argmax(abs(A[k:, k])) + k
        if A[max_row, k] == 0:
            return {
                "solution": None,
                "logs": logs + [{
                    "step": f"Iteration {k+1}",
                    "A": A.round(decimals).tolist(),
                    "b": b.round(decimals).tolist(),
                    "message": f"All pivots in column {k+1} are zero. Method fails."
                }]
            }

        # Swap rows if needed
        if max_row != k:
            A[[k, max_row]] = A[[max_row, k]]
            b[[k, max_row]] = b[[max_row, k]]
            logs.append({
                "step": f"Iteration {k+1} - Pivoting",
                "A": A.round(decimals).tolist(),
                "b": b.round(decimals).tolist(),
                "message": f"Swapped row {k+1} with row {max_row+1}."
            })

        # --- Elimination ---
        for i in range(k + 1, n):
            if A[i, k] == 0:
                continue
            m = A[i, k] / A[k, k]
            A[i, k:] = A[i, k:] - m * A[k, k:]
            b[i] = b[i] - m * b[k]

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

    logs.append({
        "step": "Back Substitution",
        "A": A.round(decimals).tolist(),
        "b": b.round(decimals).tolist(),
        "message": "Back substitution complete."
    })

    return {
        "solution": x.round(decimals).tolist(),
        "logs": logs
    }


def gauss_parcial_controller(A: list, b: list, decimals: int = 6):
    
    result = gauss_parcial(A, b, decimals)

    if result.get("solution") is not None:
        result["message"] = "Gaussian elimination with partial pivoting completed successfully."
    else:
        result["message"] = "Gaussian elimination with partial pivoting failed."

    return result
