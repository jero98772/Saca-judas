import numpy as np

def crout(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    logs = []

    L = np.zeros((n, n))       
    U = np.eye(n)              

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

    
    for j in range(n):
      
        for i in range(j, n):
            L[i, j] = A[i, j] - np.sum(L[i, :j] * U[:j, j])
        
        
        for i in range(j+1, n):
            if np.isclose(L[j, j], 0):
                logs.append({
                    "step": f"Step {j+1}",
                    "message": f"Zero pivot at L[{j},{j}]. Method fails."
                })
                return {"solution": None, "logs": logs}
            U[j, i] = (A[j, i] - np.sum(L[j, :j] * U[:j, i])) / L[j, j]

        logs.append({
            "step": f"Step {j+1}",
            "A": A.copy().round(decimals).tolist(),
            "L": L.copy().round(decimals).tolist(),
            "U": U.copy().round(decimals).tolist(),
            "b": b.copy().round(decimals).tolist(),
            "message": f"Column {j+1} processed."
        })

    #Ly = b
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - np.dot(L[i, :i], y[:i])
    
    logs.append({
        "step": "Forward Substitution",
        "y": y.round(decimals).tolist(),
        "message": "Forward substitution complete (Ly = b)."
    })

    #Ux = y
    x = np.zeros(n)
    for i in reversed(range(n)):
        x[i] = y[i] - np.dot(U[i, i+1:], x[i+1:])
    
    logs.append({
        "step": "Backward Substitution",
        "x": x.round(decimals).tolist(),
        "message": "Backward substitution complete (Ux = y)."
    })

    return {
        "solution": x.round(decimals).tolist(),
        "logs": logs
    }
