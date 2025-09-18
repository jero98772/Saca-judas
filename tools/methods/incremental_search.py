import math

def incremental_search(f, x0, delta_x, max_iter=100, tolerance=1e-6):
    """
    Finds a root using incremental search to locate an interval,
    and then applies the bisection method to refine the solution.

    Parameters:
        f: Function to evaluate.
        x0: Initial point.
        delta_x: Search step.
        max_iter: Maximum number of iterations.
        tolerance: Convergence tolerance.

    Returns:
        A dictionary with the message, the root value, and the iteration history.
    """
    # Incremental search to find an interval [a, b] with a sign change
    a = x0
    b = x0 + delta_x
    iter_count_inc = 0
    while iter_count_inc < max_iter:
        if f(a) * f(b) < 0:
            break  # Valid interval found
        a = b
        b = a + delta_x
        iter_count_inc += 1
    else:
        return {
            "message": "No valid interval found after incremental search",
            "value": None,
            "history": {"x": [], "errorAbs": [], "iterations": []}
        }

    # Bisection method in the interval [a, b]
    history_x = []
    history_errorAbs = []
    history_iterations = []
    iter_count = 0
    error_abs = float('inf')
    c_prev = a

    while error_abs > tolerance and iter_count < max_iter:
        c = (a + b) / 2
        history_x.append(c)
        error_abs = abs(c - c_prev)
        history_errorAbs.append(error_abs)
        iter_count += 1
        history_iterations.append(iter_count)

        if f(c) == 0 or error_abs < tolerance:
            return {
                "message": "Tolerance satisfied",
                "value": c,
                "history": {
                    "x": history_x,
                    "errorAbs": history_errorAbs,
                    "iterations": history_iterations
                }
            }
        elif f(a) * f(c) < 0:
            b = c
        else:
            a = c
        c_prev = c

    return {
        "message": "Maximum number of iterations reached",
        "value": c,
        "history": {
            "x": history_x,
            "errorAbs": history_errorAbs,
            "iterations": history_iterations
        }
    }
