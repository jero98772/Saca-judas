import numpy as np

def solve_triangular(T, b, lower=True):
    """
    Solve triangular system Tx = b.
    """
    n = len(b)
    x = np.zeros(n)
    
    if lower:
        # Forward substitution for lower triangular matrix
        for i in range(n):
            x[i] = (b[i] - np.dot(T[i, :i], x[:i])) / T[i, i]
    else:
        # Backward substitution for upper triangular matrix
        for i in range(n-1, -1, -1):
            x[i] = (b[i] - np.dot(T[i, i+1:], x[i+1:])) / T[i, i]
    
    return x

def solve_doolittle(A, b):
    """
    Solve Ax = b using Doolittle decomposition with JSON-compatible output.
    
    Parameters:
    A: coefficient matrix
    b: right-hand side vector
    
    Returns:
    dict: JSON-compatible result with message, value (solution), and historial
    """
    try:
        # Perform Doolittle decomposition
        L, U = doolittle(A)
        
        # Solve Ly = b (forward substitution)
        y = solve_triangular(L, b, lower=True)
        
        # Solve Ux = y (backward substitution)
        x = solve_triangular(U, y, lower=False)
        
        # Calculate residual
        residual = np.linalg.norm(np.dot(A, x) - b)
        
        # For direct methods, we don't have iteration history like iterative methods
        # So we'll create a simplified historial structure
        historial = {
            "x": [x.tolist()],  # Only the final solution
            "errorAbs": [residual],  # Only the final residual
            "iteraciones": [1]  # Just one "iteration" for direct method
        }
        
        return {
            "message": "Solución encontrada",
            "value": x.tolist(),
            "historial": historial
        }
    
    except Exception as e:
        return {
            "message": f"Error al resolver el sistema: {str(e)}",
            "value": None,
            "historial": {
                "x": [],
                "errorAbs": [],
                "iteraciones": []
            }
        }