import numpy as np

def gauss_seidel(A: list, b: list, tolerance: float, x_0: list, n_max: int, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    x_0 = np.array(x_0, dtype=float)
    n = len(b)
    logs = []

    # --- Validaciones básicas ---
    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{"step": "Check", "message": f"Matrix must be square. Received {A.shape[0]}x{A.shape[1]}."}]
        }

    if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{"step": "Check", "message": f"Vector b size ({len(b)}) does not match matrix size ({A.shape[0]})."}]
        }

    if A.shape[0] != len(x_0):
        return {
            "solution": None,
            "logs": [{"step": "Check", "message": f"Initial approximation size ({len(x_0)}) does not match matrix size ({A.shape[0]})."}]
        }

    # --- Descomposición de A ---
    D = np.diag(np.diag(A))
    L = np.tril(A, -1)
    U = np.triu(A, 1)

    # --- Matriz de iteración y vector constante ---
    DL_inv = np.linalg.inv(D + L)
    T_GS = -np.dot(DL_inv, U)
    c = np.dot(DL_inv, b)

    # --- Propiedades de T_GS ---
    eigen_vals_TGS = np.linalg.eigvals(T_GS)
    spectral_radius = max(abs(eigen_vals_TGS))
    norm2_TGS = np.linalg.norm(T_GS, 2)

    logs.append({
        "step": "Iteration Matrix",
        "T_GS": np.round(T_GS, decimals).tolist(),
        "message": f"Spectral radius ρ(T_GS) = {spectral_radius:.6f},  ||T_GS||₂ = {norm2_TGS:.6f}"
    })

    # --- Iteraciones ---
    x = x_0.copy()
    for iteration in range(1, n_max + 1):
        x_new = np.zeros_like(x)
        for i in range(n):
            sum1 = np.dot(A[i, :i], x_new[:i])  # usa los valores ya actualizados
            sum2 = np.dot(A[i, i+1:], x[i+1:])  # usa los valores viejos
            x_new[i] = (b[i] - sum1 - sum2) / A[i, i]

        error = np.linalg.norm(x_new - x, ord=2)
        logs.append({
            "step": f"Iteration {iteration}",
            "x": np.round(x_new, decimals).tolist(),
            "error": round(error, decimals)
        })

        if error < tolerance:
            return {
                "solution": np.round(x_new, decimals).tolist(),
                "iterations": iteration,
                "logs": logs
            }

        x = x_new

    logs.append({
        "step": "Warning",
        "message": "Maximum number of iterations reached without convergence."
    })

    return {
        "solution": np.round(x, decimals).tolist(),
        "iterations": n_max,
        "logs": logs
    }
