from sympy import *

from sympy import *

def false_position(f: str, a: float, b: float, nmax: int, last_n_rows: int, tolerance: float):
    x = symbols("x")
    f_math = lambdify(x, sympify(f), "math")

    # History containers
    list_iter, list_a, list_b, list_root, list_fx, list_abs = [], [], [], [], [], []

    # Initial checks
    if f_math(a) * f_math(b) > 0:
        return {
            "iterations": [],
            "a_values": [],
            "roots": [],
            "b_values": [],
            "fxm": [],
            "errors": [],
            "final_root": None,
            "message": "Function does not change sign on the interval [a, b]"
        }

    x0 = a
    for i in range(nmax):
        fa, fb = f_math(a), f_math(b)

        # Compute the false position
        root = b - fb * (b - a) / (fb - fa)
        f_root = f_math(root)
        abs_error = abs(root - x0)

        # Save iteration data
        list_iter.append(i + 1)
        list_a.append(a)
        list_b.append(b)
        list_root.append(root)
        list_fx.append(f_root)
        list_abs.append(abs_error)

        # Check tolerance
        if abs_error < tolerance or f_root == 0:
            return {
                "iterations": list_iter[-last_n_rows:],
                "a_values": list_a[-last_n_rows:],
                "roots": list_root[-last_n_rows:],
                "b_values": list_b[-last_n_rows:],
                "fxm": list_fx[-last_n_rows:],
                "errors": list_abs[-last_n_rows:],
                "final_root": root,
                "message": "Convergence, tolerance satisfied"
            }

        # Update interval
        if fa * f_root < 0:
            b = root
        else:
            a = root

        x0 = root

    return {
        "iterations": list_iter[-last_n_rows:],
        "a_values": list_a[-last_n_rows:],
        "roots": list_root[-last_n_rows:],
        "b_values": list_b[-last_n_rows:],
        "fxm": list_fx[-last_n_rows:],
        "errors": list_abs[-last_n_rows:],
        "final_root": root,
        "message": "Max iterations reached"
    }



def false_position_controller(function: str, a: float, b: float, nmax: int, last_n_rows: int, tolerance: float):
    # Debug prints
    print("=== Parameters received in false_position_controller ===")
    print(f"function: {function}")
    print(f"a: {a}")
    print(f"b: {b}")
    print(f"nmax: {nmax}")
    print(f"last_n_rows: {last_n_rows}")
    print(f"tolerance: {tolerance}")
    print("=======================================================")

    answer = false_position(function, a, b, nmax, last_n_rows, tolerance)

    return answer
