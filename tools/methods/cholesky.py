import numpy as np

def cholesky(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

    # Verificar que A sea cuadrada
    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "message": f"Matrix must be square. Received {A.shape[0]}x{A.shape[1]}."
            }]
        }

    # Verificar que A sea simétrica
    if not np.allclose(A, A.T, atol=1e-8):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.round(decimals).tolist(),
                "message": "Matrix is not symmetric, Cholesky factorization not applicable."
            }]
        }

    # Verificar definida positiva (todos los autovalores > 0)
    eigenvals = np.linalg.eigvals(A)
    if np.any(eigenvals <= 0):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.round(decimals).tolist(),
                "message": "Matrix is not positive definite, Cholesky factorization fails."
            }]
        }

    logs.append({
        "step": "Initial",
        "A": A.round(decimals).tolist(),
        "b": b.round(decimals).tolist(),
        "message": "Matrix is symmetric positive definite. Starting Cholesky factorization."
    })

    # Inicializar L
    L = np.zeros((n, n))
    
    # Calcular L (matriz triangular inferior)
    for i in range(n):
        for j in range(i + 1):
            suma = np.dot(L[i, :j], L[j, :j])
            if i == j:
                L[i, j] = np.sqrt(A[i, i] - suma)
            else:
                L[i, j] = (A[i, j] - suma) / L[j, j]

        logs.append({
            "step": f"Step {i+1}",
            "L": L.copy().round(decimals).tolist(),
            "message": f"Row {i+1} of L computed."
        })

    # U es la traspuesta de L
    U = L.T

    logs.append({
        "step": "Factorization Complete",
        "L": L.round(decimals).tolist(),
        "U": U.round(decimals).tolist(),
        "message": "Cholesky factorization A = L * Lᵀ complete."
    })

    # Resolver Ly = b
    y = np.zeros(n)
    for i in range(n):
        y[i] = (b[i] - np.dot(L[i, :i], y[:i])) / L[i, i]

    logs.append({
        "step": "Forward Substitution",
        "y": y.round(decimals).tolist(),
        "message": "Forward substitution complete (Ly = b)."
    })

    # Resolver Ux = y
    x = np.zeros(n)
    for i in reversed(range(n)):
        x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i, i]

    logs.append({
        "step": "Backward Substitution",
        "x": x.round(decimals).tolist(),
        "message": "Backward substitution complete (Ux = y)."
    })

    return {
        "solution": x.round(decimals).tolist(),
        "L": L.round(decimals).tolist(),
        "U": U.round(decimals).tolist(),
        "logs": logs
    }


#A tiene que ser simetrica
A = [
    [7, -2, -2, -1],
    [-2, 8, -2, -2],
    [-2, -2, 6, -2],
    [-1, -2, -2, 10]
]

b = [1, 1, 1, 1]

resultado = cholesky(A, b)
print("Solución:", resultado["solution"])
print("L:\n", np.array(resultado["L"]))
print("U:\n", np.array(resultado["U"]))
