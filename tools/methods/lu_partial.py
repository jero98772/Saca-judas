import numpy as np

def lu_partial(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

    # Inicializar matrices
    L = np.zeros((n, n))
    U = np.zeros((n, n))
    P = np.eye(n)

    # Pivoteo parcial + eliminación
    for k in range(n):
        # === Pivoteo parcial ===
        max_row = np.argmax(np.abs(A[k:, k])) + k
        if max_row != k:
            A[[k, max_row]] = A[[max_row, k]]
            P[[k, max_row]] = P[[max_row, k]]
            if k > 0:
                L[[k, max_row], :k] = L[[max_row, k], :k]
            b[[k, max_row]] = b[[max_row, k]]

        # === Calcular elementos de L y U ===
        # L[i,k] para i >= k
        for i in range(k, n):
            suma = sum(L[i, p] * U[p, k] for p in range(k))
            L[i, k] = A[i, k] - suma

        # U[k,j] para j >= k
        for j in range(k, n):
            if np.isclose(L[k, k], 0):
                raise ValueError(f"Pivote nulo en fila {k+1}.")
            suma = sum(L[k, p] * U[p, j] for p in range(k))
            U[k, j] = (A[k, j] - suma) / L[k, k]

        logs.append({
            "step": f"Step {k+1}",
            "L": L.copy().round(decimals).tolist(),
            "U": U.copy().round(decimals).tolist(),
            "message": f"Elimination in column {k+1} complete (LU with partial pivoting)."
        })

    # === Sustitución hacia adelante ===
    Pb = np.dot(P, b)
    y = np.zeros(n)
    for i in range(n):
        suma = np.dot(L[i, :i], y[:i])
        y[i] = (Pb[i] - suma) / L[i, i]

    # === Sustitución hacia atrás ===
    x = np.zeros(n)
    for i in reversed(range(n)):
        suma = np.dot(U[i, i+1:], x[i+1:])
        x[i] = y[i] - suma

    logs.append({
        "step": "Result",
        "x": x.round(decimals).tolist(),
        "message": "Solution computed successfully (LU with partial pivoting)."
    })

    return {
        "solution": x.round(decimals).tolist(),
        "L": L.round(decimals),
        "U": U.round(decimals),
        "P": P,
        "logs": logs
    }

