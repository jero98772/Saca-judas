import numpy as np

def gauss_simple(A: list, b: list, decimals: int = 6):
    
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

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
        if A[k, k] == 0:
            return {
                "solution": None,
                "logs": logs + [{
                    "step": f"Iteration {k+1}",
                    "A": A.round(decimals).tolist(),
                    "b": b.round(decimals).tolist(),
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


def gauss_simple_controller(A: list, b: list, decimals: int = 6):
    """
    Controller for Gaussian Elimination (simple).
    Wraps gauss_simple() and prepares the response.
    """
    result = gauss_simple(A, b, decimals)

    if result.get("solution") is not None:
        result["message"] = "Gaussian elimination completed successfully."
    else:
        result["message"] = "Gaussian elimination failed."

    return result
