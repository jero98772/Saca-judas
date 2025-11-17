import numpy as np
import logging
import json

def cubic_spline_method(x, y):
    """
    Computes the natural cubic spline coefficients for given x and y data.
    Returns a list of (a, b, c, d) tuples for each spline segment.
    """

    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    n = len(x)
    h = np.diff(x)

    # Initialize tridiagonal system
    A = np.zeros((n, n))
    b_vec = np.zeros(n)

    # Natural spline boundary conditions
    A[0, 0] = 1
    A[-1, -1] = 1

    # Fill system matrix
    for i in range(1, n - 1):
        A[i, i - 1] = h[i - 1]
        A[i, i] = 2 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        b_vec[i] = 3 * ((y[i + 1] - y[i]) / h[i] -
                        (y[i] - y[i - 1]) / h[i - 1])

    # Solve for c coefficients
    c = np.linalg.solve(A, b_vec)

    # Compute spline coefficients (a, b, c, d)
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


# logging config (opcional)
logging.basicConfig(
    filename="splines.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def save_single_tracer(tracer_obj, path="splines.log"):
    """
    Save a single tracer as one JSON object per line (JSONL).
    tracer_obj must be a plain Python dict containing only JSON-serializable values.
    """
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(tracer_obj, ensure_ascii=False) + "\n")


def save_cubic_tracer(x, coefficients, decimals=None):
    """
    Build logs in JS-friendly JSON format.
    - x: list of x nodes (numbers)
    - coefficients: list of tuples (a,b,c,d) (may contain numpy types)
    - decimals: if not None, round floats to that many decimals (int)
    Returns: list of dicts ready for JSON and for JS plotting.
    """
    logs = []
    # ensure plain python floats and lists
    for i, tup in enumerate(coefficients):
        a, b, c, d = tup
        # convert numpy types to native floats
        a = float(a)
        b = float(b)
        c = float(c)
        d = float(d)

        # optionally round for readability; if None, keep full precision
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

        # append to returned list (for endpoint response)
        logs.append(log_entry)

        # persist as JSON line (so file is valid JSONL and JS can parse it if needed)
        try:
            save_single_tracer(log_entry, path="splines.log")
        except Exception:
            # Ignore persistence errors but do not break the flow
            pass

    return logs
