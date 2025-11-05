import numpy as np

def cubic_spline(x, y):
 
    logs = []
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

 
    if len(x) != len(y):
        raise ValueError("x and y must have the same length.")
    
    if len(x) < 2:
        raise ValueError("At least two points are required to construct a spline.")
    
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("Input data contains NaN values.")
    
    if np.any(np.isinf(x)) or np.any(np.isinf(y)):
        raise ValueError("Input data contains infinite values.")
    
    if np.any(np.diff(x) <= 0):
        raise ValueError("x values must be strictly increasing (no duplicates or reversed order).")
    
    logs.append("Validation: data verified successfully (no duplicates or invalid values).")


    n = len(x)
    h = np.diff(x)

    if np.any(np.isclose(h, 0, atol=1e-12)):
        raise ValueError("A nearly zero interval was detected; check x values.")
    
    if np.max(h) > 10 * np.median(h):
        logs.append("Large gap detected in x values, spline may be unstable.")


    A = np.zeros((n, n))
    b = np.zeros(n)


    A[0, 0] = 1
    A[-1, -1] = 1

    for i in range(1, n - 1):
        A[i, i - 1] = h[i - 1]
        A[i, i]     = 2 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        b[i] = 3 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])



    try:
        c = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        raise ArithmeticError("The system could not be solved (singular or ill-conditioned matrix).")

    if np.any(np.isnan(c)) or np.any(np.isinf(c)):
        raise ArithmeticError("The system produced invalid results (NaN or Inf).")


    coef = []
    for i in range(n - 1):
        a_i = y[i]
        b_i = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * c[i] + c[i + 1]) / 3
        d_i = (c[i + 1] - c[i]) / (3 * h[i])
        coef.append((a_i, b_i, c[i], d_i))

        spline_str = (
            f"S{i}(x) = {a_i:.6f} + {b_i:.6f}(x - {x[i]:.6f}) "
            f"+ {c[i]:.6f}(x - {x[i]:.6f})² + {d_i:.6f}(x - {x[i]:.6f})³"
        )
        interval_str = f"Interval: [{x[i]:.6f}, {x[i+1]:.6f}]"
        logs.append(f"{interval_str}\n{spline_str}")

    logs.append("Computation completed successfully.")
    return coef, logs
