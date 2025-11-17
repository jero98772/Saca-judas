import numpy as np
from sympy import symbols, simplify, expand

def divided_differences_safe(x, y, eps=1e-14, max_value=1e12):
    """
    Computes divided differences with numerical validations.
    Returns: diff, status, message
    status ∈ {"success", "danger", "info"}
    """

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
    """
    Builds:
    - symbolic expression P(x)
    - Newton form expression as string
    Returns dict.
    """

    x_sym = symbols('x')
    n = len(x)
    b = [diff[0, i] for i in range(n)]

    # Symbolic polynomial
    P = b[0]
    prod = 1
    for i in range(1, n):
        prod *= (x_sym - x[i - 1])
        P += b[i] * prod

    expr_sym = simplify(expand(P))

    # Newton string
    newton_terms = []
    for i in range(n):
        if i == 0:
            newton_terms.append(f"{b[i]}")
        else:
            factors = "".join([f"(x - {x[j]})" for j in range(i)])
            newton_terms.append(f"{b[i]}*{factors}")

    newton_poly_str = " + ".join(newton_terms)

    return {
        "symbolic_expression": str(expr_sym),
        "polynomial_newton": f"P(x) = {newton_poly_str}"
    }


def newton_interpolant_object(x, y):
    """
    Returns an OBJECT containing:
      - status  → "danger" | "success" | "info"
      - message
      - symbolic_expression (string)
      - polynomial_newton (string)
    """

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
        "symbolic_expression": result["symbolic_expression"],   # Example: "2*x**3 + 3*x**4"
        "polynomial_newton": result["polynomial_newton"]        # Newton form
    }
