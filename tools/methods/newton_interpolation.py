import numpy as np
from sympy import symbols, simplify, expand

# ----------------- Helpers de formateo -----------------

def fmt_num(v):
    """Convierte 3.0 → '3', -2.0 → '-2', pero deja decimales reales."""
    v = float(v)
    if v.is_integer():
        return str(int(v))
    return str(v)

def fmt_x_minus(value):
    """Devuelve (x - a) o (x + a) según el signo, con formato limpio."""
    v = float(value)
    if v >= 0:
        return f"(x - {fmt_num(v)})"
    else:
        return f"(x + {fmt_num(abs(v))})"

# --------------------------------------------------------

def divided_differences_safe(x, y, eps=1e-14, max_value=1e12):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    n = len(x)

    diff = np.zeros((n, n))
    diff[:, 0] = y

    for j in range(1, n):
        for i in range(n - j):
            denom = x[i + j] - x[i]
            num = diff[i + 1][j - 1] - diff[i][j - 1]

            if abs(denom) < eps:
                return None, "danger", f"Denominator too small in f[x{i}, x{i+j}] → {denom}"

            value = num / denom

            if abs(value) > max_value:
                return None, "danger", f"Excessively large value detected: {value}"

            diff[i][j] = value

    return diff, "success", "Computation completed successfully."


def build_newton_interpolant(x, diff):
    x_sym = symbols('x')
    n = len(x)
    b = [diff[0, i] for i in range(n)]

    # ----- Polinomio simbólico -----
    P = b[0]
    prod = 1

    for i in range(1, n):
        prod *= (x_sym - x[i - 1])
        P += b[i] * prod

    expr_sym = simplify(expand(P))

    # ----- String de la forma de Newton -----
    newton_terms = []

    for i in range(n):
        bi = fmt_num(b[i])
        if i == 0:
            newton_terms.append(f"{bi}")
        else:
            factors = "".join([fmt_x_minus(x[j]) for j in range(i)])
            newton_terms.append(f"{bi}*{factors}")

    newton_poly_str = " + ".join(newton_terms)

    return {
        "symbolic_expression": str(expr_sym),
        "polynomial_newton": f"P(x) = {newton_poly_str}"
    }


def newton_interpolant_object(x, y):
    diff, status, message = divided_differences_safe(x, y)

    if status != "success":
        return {
            "status": status,
            "message": message,
            "symbolic_expression": None,
            "polynomial_newton": None
        }

    result = build_newton_interpolant(x, diff)

    return {
        "status": "success",
        "message": message,
        "symbolic_expression": result["symbolic_expression"],
        "polynomial_newton": result["polynomial_newton"]
    }
