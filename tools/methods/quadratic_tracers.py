import numpy as np
import logging
import json

def quadratic_spline_method(x, y):

    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    n = len(x)
    h = np.diff(x)

    a = y.copy()
    b = np.zeros(n - 1)
    c = np.zeros(n - 1)

    # Condición natural estándar
    b[0] = 0.0  

    for i in range(n - 1):
        # Fórmula correcta del coeficiente cuadrático
        c[i] = (y[i+1] - y[i] - b[i] * h[i]) / (h[i]**2)

        if i < n - 2:
            # Continuidad de la derivada
            b[i+1] = b[i] + 2 * c[i] * h[i]


    coefficients = [(a[i], b[i], c[i]) for i in range(n - 1)]

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


def save_quadratic_tracer(x, coefficients, decimals=None):

    logs = []

    for i, tup in enumerate(coefficients):
        a, b, c = tup

        a = float(a)
        b = float(b)
        c = float(c)

        if isinstance(decimals, int):
            a = round(a, decimals)
            b = round(b, decimals)
            c = round(c, decimals)

        log_entry = {
            "segment": int(i),
            "interval": [float(x[i]), float(x[i+1])],
            "coefficients": {"a": a, "b": b, "c": c},
            "message": f"Quadratic spline segment {i} computed."
        }

        logs.append(log_entry)

        try:
            save_single_tracer(log_entry, path="splines.log")
        except Exception:
            pass

    return logs
