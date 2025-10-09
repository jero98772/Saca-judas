import numpy as np

def lu_partial_pivot(A: list, b: list, decimals: int):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

    L = np.eye(n)
    U = A.copy()
    P = np.eye(n)

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


    for k in range(n):

        max_row = np.argmax(np.abs(U[k:, k])) + k
        if max_row != k:

            U[[k, max_row], :] = U[[max_row, k], :]

            if k > 0:
                L[[k, max_row], :k] = L[[max_row, k], :k]

            P[[k, max_row], :] = P[[max_row, k], :]

            b[[k, max_row]] = b[[max_row, k]]


        for i in range(k+1, n):
            if np.isclose(U[k, k], 0):
                factor = 0
            else:
                factor = U[i, k] / U[k, k]
            L[i, k] = factor
            U[i, k:] -= factor * U[k, k:]

        logs.append({
            "step": f"Step {k+1}",
            "A": U.copy().round(decimals).tolist(),
            "L": L.copy().round(decimals).tolist(),
            "U": U.copy().round(decimals).tolist(),
            "b": b.copy().round(decimals).tolist(),
            "message": f"Elimination in column {k+1} complete with partial pivoting."
        })

    #Ly = Pb
    y = np.zeros(n)
    Pb = np.dot(P, b)
    for i in range(n):
        y[i] = Pb[i] - np.dot(L[i, :i], y[:i])

    logs.append({
        "step": "Forward Substitution",
        "y": y.round(decimals).tolist(),
        "message": "Forward substitution complete (Ly = Pb)."
    })

    #Ux = y
    x = np.zeros(n)
    for i in reversed(range(n)):
        if np.isclose(U[i, i], 0):
            logs.append({
                "step": "Backward Substitution",
                "A": U.copy().round(decimals).tolist(),
                "b": b.copy().round(decimals).tolist(),
                "message": f"Zero pivot at row {i+1}. Method fails."
            })
            return {"solution": None, "logs": logs}
        x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i, i]

    logs.append({
        "step": "Backward Substitution",
        "x": x.round(decimals).tolist(),
        "message": "Backward substitution complete (Ux = y)."
    })

    return {
        "solution": x.round(decimals).tolist(),
        "logs": logs
    }
