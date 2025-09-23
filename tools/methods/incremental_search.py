import math

def incremental_search(f, x0, delta_x, max_iter=100, tolerance=1e-6):
    """
    Finds a root interval using incremental search to locate an interval [a, b]
    where f(a) and f(b) have opposite signs, indicating a root exists between them.
    
    Parameters:
        f: Function to evaluate.
        x0: Initial point.
        delta_x: Search step.
        max_iter: Maximum number of iterations.
        tolerance: Convergence tolerance (not used in this version).
    
    Returns:
        A dictionary with the message, the root interval [a, b], and search history.
    """
    # Incremental search to find an interval [a, b] with a sign change
    a = x0
    b = x0 + delta_x
    iter_count_inc = 0
    search_history = []
    
    while iter_count_inc < max_iter:
        search_history.append([a, b, f(a), f(b)])
        
        if f(a) * f(b) < 0:
            # Valid interval found - f(a) and f(b) have opposite signs
            return {
                "message": f"Root interval found: [{a:.6f}, {b:.6f}]",
                "interval": [a, b],
                "history": {
                    "search_points": search_history,
                    "iterations": iter_count_inc + 1
                }
            }
        
        a = b
        b = a + delta_x
        iter_count_inc += 1
    
    # No valid interval found
    return {
        "message": "No valid interval found after incremental search",
        "interval": None,
        "history": {
            "search_points": search_history,
            "iterations": iter_count_inc
        }
    }