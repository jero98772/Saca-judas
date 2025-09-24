import numpy as np

def gaussian_elimination_with_pivot_total(matrix_text: str, decimals: int = 6):
    """
    Gaussian Elimination with Total Pivoting from augmented matrix text.
    
    Args:
        matrix_text (str): Augmented matrix as text (n x n+1)
        decimals (int): Number of decimal places for rounding
    
    Returns:
        dict: Contains solution, stages, and permutation info
    """
    # Parse matrix from text
    rows = []
    for line in matrix_text.strip().splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.replace(",", " ").split()]
        rows.append([float(p) for p in parts])
    
    A = np.array(rows, dtype=float)
    n, m = A.shape
    
    # Validate dimensions
    if m != n + 1:
        return {
            "solution": None,
            "stages": [{
                "k": 0,
                "note": "Error",
                "matrix": A.round(decimals).tolist(),
                "swap": {"rows": None, "cols": None},
                "message": f"Invalid matrix dimensions: {n}x{m}. Expected {n}x{n+1}."
            }],
            "perm_cols": list(range(n)),
            "perm_rows": list(range(n))
        }
    
    # Initialize permutation tracking
    perm_rows = list(range(n))
    perm_cols = list(range(n))
    
    stages = []
    
    # Add initial stage
    stages.append({
        "k": 0,
        "note": "Initial matrix",
        "matrix": A.round(decimals).tolist(),
        "swap": {"rows": None, "cols": None},
        "message": f"Starting Gaussian elimination with total pivoting"
    })
    
    # Forward elimination with total pivoting
    for k in range(n - 1):
        # Find maximum pivot in submatrix A[k:n, k:n]
        sub_matrix = np.abs(A[k:n, k:n])
        if sub_matrix.size == 0:
            break
            
        max_idx = np.unravel_index(np.argmax(sub_matrix), sub_matrix.shape)
        i_max = k + max_idx[0]
        j_max = k + max_idx[1]
        max_val = sub_matrix[max_idx]
        
        # Check for singular matrix
        if max_val < 1e-12:
            return {
                "solution": None,
                "stages": stages + [{
                    "k": k + 1,
                    "note": f"Error at stage {k+1}",
                    "matrix": A.round(decimals).tolist(),
                    "swap": {"rows": None, "cols": None},
                    "message": "Matrix is singular or nearly singular"
                }],
                "perm_cols": perm_cols,
                "perm_rows": perm_rows
            }
        
        swap_info = {"rows": None, "cols": None}
        
        # Row swap if needed
        if i_max != k:
            A[[k, i_max], :] = A[[i_max, k], :]
            perm_rows[k], perm_rows[i_max] = perm_rows[i_max], perm_rows[k]
            swap_info["rows"] = (k, i_max)
        
        # Column swap if needed (only for coefficient matrix, not augmented column)
        if j_max != k:
            A[:, [k, j_max]] = A[:, [j_max, k]]
            perm_cols[k], perm_cols[j_max] = perm_cols[j_max], perm_cols[k]
            swap_info["cols"] = (k, j_max)
        
        # Elimination
        for i in range(k + 1, n):
            if abs(A[k, k]) > 1e-16:
                factor = A[i, k] / A[k, k]
                A[i, k:] = A[i, k:] - factor * A[k, k:]
        
        # Add stage
        stages.append({
            "k": k + 1,
            "note": f"Stage {k+1} - Pivot: ({i_max}, {j_max})",
            "matrix": A.round(decimals).tolist(),
            "swap": swap_info,
            "message": f"Elimination completed for column {k+1}"
        })
    
    # Back substitution
    y = np.zeros(n, dtype=float)
    for i in range(n - 1, -1, -1):
        if abs(A[i, i]) < 1e-16:
            return {
                "solution": None,
                "stages": stages + [{
                    "k": n,
                    "note": "Back substitution error",
                    "matrix": A.round(decimals).tolist(),
                    "swap": {"rows": None, "cols": None},
                    "message": f"Zero pivot at position ({i}, {i}) during back substitution"
                }],
                "perm_cols": perm_cols,
                "perm_rows": perm_rows
            }
        
        sum_ax = sum(A[i, j] * y[j] for j in range(i + 1, n))
        y[i] = (A[i, n] - sum_ax) / A[i, i]
    
    # Reorder solution according to column permutations
    x = np.zeros(n, dtype=float)
    for i in range(n):
        x[perm_cols[i]] = y[i]
    
    # Add final stage
    stages.append({
        "k": n,
        "note": "Back substitution completed",
        "matrix": A.round(decimals).tolist(),
        "swap": {"rows": None, "cols": None},
        "message": "Solution obtained successfully"
    })
    
    return {
        "solution": x.round(decimals).tolist(),
        "stages": stages,
        "perm_cols": perm_cols,
        "perm_rows": perm_rows
    }


def gaussian_elimination_with_pivot_total_controller(matrix: str, decimals: int = 6):
    """
    Controller for Gaussian Elimination with Total Pivoting.
    Wraps gaussian_elimination_with_pivot_total() and prepares the response.
    
    Args:
        matrix (str): Augmented matrix as text
        decimals (int): Number of decimal places for rounding
    
    Returns:
        dict: Response with solution, stages, and status message
    """
    try:
        result = gaussian_elimination_with_pivot_total(matrix, decimals)
        
        if result.get("solution") is not None:
            result["message"] = "Gaussian elimination with total pivoting completed successfully."
            result["type"] = "success"
        else:
            result["message"] = "Gaussian elimination with total pivoting failed."
            result["type"] = "danger"
        
        return result
        
    except Exception as e:
        return {
            "solution": None,
            "stages": [{
                "k": 0,
                "note": "Error",
                "matrix": [],
                "swap": {"rows": None, "cols": None},
                "message": f"Error processing matrix: {str(e)}"
            }],
            "perm_cols": [],
            "perm_rows": [],
            "message": f"Error: {str(e)}",
            "type": "danger"
        }


