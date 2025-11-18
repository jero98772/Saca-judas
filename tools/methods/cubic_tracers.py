import numpy as np
import logging
import json

def cubic_spline_method(x, y):

    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    n = len(x)
    h = np.diff(x)

    # Matriz del sistema
    A = np.zeros((n, n))
    b_vec = np.zeros(n)

    # Condiciones naturales: c0 = 0, cn = 0
    A[0,0] = 1
    A[-1,-1] = 1
    b_vec[0] = 0
    b_vec[-1] = 0

    # Llenar el sistema del PDF
    for i in range(1, n - 1):
        A[i, i - 1] = h[i - 1]
        A[i, i]     = 2 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        b_vec[i] = 3 * (
            (y[i + 1] - y[i]) / h[i] -
            (y[i] - y[i - 1]) / h[i - 1]
        )

    # Resolver para c_i
    c = np.linalg.solve(A, b_vec)

    # Calcular los coeficientes a_i, b_i, d_i
    coefficients = []
    for i in range(n - 1):
        a_i = y[i]
        b_i = (y[i + 1] - y[i]) / h[i] - h[i] * (2*c[i] + c[i+1]) / 3
        d_i = (c[i+1] - c[i]) / (3 * h[i])
        coefficients.append((a_i, b_i, c[i], d_i))

    return coefficients



logging.basicConfig(
    filename="splines.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)



logging.basicConfig(
    filename="splines.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def save_single_tracer(tracer_obj, path="splines.log"):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(tracer_obj, ensure_ascii=False) + "\n")


def save_cubic_tracer(x, coefficients, decimals=None):

    logs = []
    
    for i, tup in enumerate(coefficients):
        a, b, c, d = tup
        
        a = float(a)
        b = float(b)
        c = float(c)
        d = float(d)

        if isinstance(decimals, int):
            a = round(a, decimals)
            b = round(b, decimals)
            c = round(c, decimals)
            d = round(d, decimals)

        log_entry = {
            "segment": int(i),
            "interval": [float(x[i]), float(x[i+1])],
            "coefficients": {"a": a, "b": b, "c": c, "d": d},
            "message": f"Spline segment {i} computed."
        }

        logs.append(log_entry)

        try:
            save_single_tracer(log_entry, path="splines.log")
        except Exception:
            pass

    return logs
