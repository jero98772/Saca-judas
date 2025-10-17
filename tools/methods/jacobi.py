import numpy as np

def jacobi(A: list, b: list, tolerance: float, x_0: list, n_max: int, decimals: int = 8):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    x_0 = np.array(x_0, dtype=float)
    n = len(b)
    logs = []


    if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "message": f"Matrix must be square. Received {A.shape[0]}x{A.shape[1]}."
            }]
        }

    if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "message": f"The size of vector b ({len(b)}) does not match the number of rows in the input matrix ({A.shape[0]})."
            }]
        }
    
    if A.shape[0] != len(x_0):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "message": f"The size of initial approximation ({len(x_0)}) does not match with the size of the matrix ({A.shape[0]})."
            }]
        }


    D = np.diag(np.diag(A))
    L_U = A - D
    D_inv = np.linalg.inv(D)

    T_J = -np.dot(D_inv, L_U)
    c = np.dot(D_inv, b)


    eigen_vals_TJ = np.linalg.eigvals(T_J)
    spectral_radius = max(abs(eigen_vals_TJ))
    norm2_TJ = np.linalg.norm(T_J, 2)

    logs.append({
        "step": "Iteration Matrix",
        "T_J": np.round(T_J, decimals).tolist(),
        "message": f"Spectral radius ρ(T_J) = {spectral_radius:.6f},  ||T_J||₂ = {norm2_TJ:.6f}"
    })


    x = x_0.copy()
    for iteration in range(1, n_max + 1):
        x_new = np.dot(T_J, x) + c
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

