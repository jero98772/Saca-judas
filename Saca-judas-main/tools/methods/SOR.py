import numpy as np

def sor(A, b, omega, x0=None, tolerance=1e-6, max_iter=1000):
    """
    Successive Over-Relaxation (SOR) method for solving Ax = b with JSON-compatible output.
    
    Parameters:
    A: coefficient matrix
    b: right-hand side vector
    omega: relaxation parameter (0 < omega < 2)
    x0: initial guess
    tolerance: convergence tolerance
    max_iter: maximum iterations
    
    Returns:
    dict: JSON-compatible result with message, value (solution), and historial
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    
    if x0 is None:
        x = np.zeros(n)
    else:
        x = np.array(x0, dtype=float)
    
    # Initialize history arrays
    historial_x = [x.copy().tolist()]
    historial_errorAbs = []
    historial_iteraciones = []
    
    for iteration in range(1, max_iter + 1):
        x_old = x.copy()
        
        for i in range(n):
            # Calculate sum of a_ij * x_j for j != i
            sum1 = sum(A[i][j] * x[j] for j in range(i))
            sum2 = sum(A[i][j] * x_old[j] for j in range(i+1, n))
            
            # SOR update formula
            x[i] = (1 - omega) * x_old[i] + (omega / A[i][i]) * (b[i] - sum1 - sum2)
        
        # Calculate error (infinity norm of the difference)
        error = np.linalg.norm(x - x_old, ord=np.inf)
        
        # Update history
        historial_x.append(x.copy().tolist())
        historial_errorAbs.append(error)
        historial_iterations.append(iteration)
        
        # Check convergence
        if error < tolerance:
            return {
                "message": "Tolerancia satisfecha",
                "value": x.tolist(),
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
    
    # If we reach here, the method didn't converge
    return {
        "message": "Máximo número de iteraciones alcanzado",
        "value": x.tolist(),
        "historial": {
            "x": historial_x,
            "errorAbs": historial_errorAbs,
            "iteraciones": historial_iteraciones
        }
    }