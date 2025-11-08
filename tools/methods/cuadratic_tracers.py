import numpy as np

def quadratic_spline(x, y):
    """
    Implementa el método de trazadores cuadráticos naturales con validaciones exhaustivas.
    Devuelve:
        coef  -> lista de tuplas (a_i, b_i, c_i) por intervalo
        logs  -> lista de mensajes informativos sobre el proceso
    """
    logs = []
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    # ===== VALIDACIONES =====
    if len(x) != len(y):
        raise ValueError("x and y must have the same length.")
    if len(x) < 3:
        raise ValueError("At least three points are required to construct a quadratic spline.")
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("Input data contains NaN values.")
    if np.any(np.isinf(x)) or np.any(np.isinf(y)):
        raise ValueError("Input data contains infinite values.")
    if np.any(np.diff(x) <= 0):
        raise ValueError("x values must be strictly increasing.")
    
    logs.append("Validation: data verified successfully (no duplicates or invalid values).")

    # ===== CÁLCULO DE H =====
    n = len(x)
    h = np.diff(x)

    if np.any(np.isclose(h, 0, atol=1e-12)):
        raise ValueError("A nearly zero interval was detected; check x values.")
    
    logs.append(f"Computed {n-1} intervals (h_i values): {h}")

    # ===== SISTEMA PARA c_i =====
    # Ecuaciones:
    # c0 = 0
    # (c_i * h_i) + 2*(y_{i+1}-y_i - c_{i-1}*h_{i-1}) = 0  (de continuidad de derivadas)

    c = np.zeros(n)
    for i in range(1, n - 1):
        c[i] = ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1]) * (h[i - 1] / (h[i - 1] + h[i]))
    logs.append(f"Computed c coefficients (with c0=0): {c}")

    # ===== CÁLCULO DE a_i y b_i =====
    coef = []
    for i in range(n - 1):
        a_i = y[i]
        b_i = (y[i + 1] - y[i]) / h[i] - c[i] * h[i]
        coef.append((a_i, b_i, c[i]))

        spline_str = (
            f"S{i}(x) = {a_i:.6f} + {b_i:.6f}(x - {x[i]:.6f}) + "
            f"{c[i]:.6f}(x - {x[i]:.6f})²"
        )
        interval_str = f"Interval: [{x[i]:.6f}, {x[i+1]:.6f}]"
        logs.append(f"{interval_str}\n{spline_str}")

    logs.append("Computation completed successfully.")
    return coef, logs
