import numpy as np

def sor(A, b, omega, x_0, tolerance, n_max, norma="inf"):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    x_0 = np.array(x_0, dtype=float)
    n = len(b)
    logs = []

    # --- Validaciones ---
    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{"step": "Check", "message":
                     f"Matrix must be square. Received {A.shape[0]}x{A.shape[1]}."}]
        }

    if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{"step": "Check", "message":
                     f"Vector b size ({len(b)}) does not match matrix size ({A.shape[0]})."}]
        }

    if A.shape[0] != len(x_0):
        return {
            "solution": None,
            "logs": [{"step": "Check", "message":
                     f"Initial approximation size ({len(x_0)}) does not match matrix size ({A.shape[0]})."}]
        }

    if not (0 < omega < 2):
        return {
            "solution": None,
            "logs": [{"step": "Check", "message":
                     f"Relaxation parameter ω must satisfy 0 < ω < 2. Received ω = {omega}"}]
        }

    # --- Matrices D, L, U ---
    D = np.diag(np.diag(A))
    L = -np.tril(A, -1)
    U = -np.triu(A, 1)

    # --- Matriz de iteración SOR ---
    try:
        DL_omega_inv = np.linalg.inv(D - omega * L)
    except np.linalg.LinAlgError:
        return {
            "solution": None,
            "logs": [{"step": "Check", "message": "Matrix (D - ωL) is singular. SOR cannot proceed."}]
        }

    T_SOR = DL_omega_inv @ ((1 - omega) * D + omega * U)
    c = omega * (DL_omega_inv @ b)

    # --- Radio espectral ---
    eigen_vals = np.linalg.eigvals(T_SOR)
    spectral_radius = max(abs(eigen_vals))
    norm_T = _vec_norm(T_SOR, norma)

    logs.append({
        "step": "Iteration Matrix",
        "T_SOR": T_SOR.tolist(),
        "message": f"Spectral radius ρ(T_SOR) = {spectral_radius},   ||T_SOR||{norma} = {norm_T}"
    })

    if spectral_radius >= 1:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "message": f"SOR does not converge because ρ(T_SOR) = {spectral_radius} ≥ 1"
            }]
        }

    # --- Iteraciones SOR ---
    x = x_0.copy()

    for iteration in range(1, n_max + 1):
        x_old = x.copy()

        for i in range(n):
            sum1 = np.dot(A[i, :i], x[:i])
            sum2 = np.dot(A[i, i+1:], x_old[i+1:])
            x[i] = (1 - omega) * x_old[i] + (omega / A[i, i]) * (b[i] - sum1 - sum2)

        error = _vec_norm(x - x_old, norma)

        logs.append({
            "step": f"Iteration {iteration}",
            "x": x.tolist(),
            "error": error
        })

        if error < tolerance:
            return {
                "solution": x.tolist(),
                "iterations": iteration,
                "logs": logs
            }

    # --- No convergió ---
    logs.append({
        "step": "Warning",
        "message": "Maximum number of iterations reached without convergence."
    })

    return {
        "solution": x.tolist(),
        "iterations": n_max,
        "logs": logs
    }


def _vec_norm(v: np.ndarray, norma: str = "inf") -> float:
    if norma == "1":
        return float(np.linalg.norm(v, 1))
    if norma == "2":
        return float(np.linalg.norm(v, 2))
    return float(np.linalg.norm(v, np.inf))
