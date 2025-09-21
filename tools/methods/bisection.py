from sympy import *

def bisection(f: str, a: float, b: float, nmax: int, last_n_rows: int, tolerance: float):

    x = symbols("x")
    f_math = lambdify(x, sympify(f), "math")

    
    list_ite, list_a, list_b, list_root, list_abs = [], [], [], [], []

    x_0 = a
    for i in range(nmax):
        middle = (a+b)/2
        abs_error = abs(x_0 - middle)
        
        if f_math(a) * f_math(middle) < 0:
            b = middle
        else:
            a = middle

        list_ite.append(i+1)
        list_a.append(a)
        list_b.append(b)
        list_root.append(middle)
        list_abs.append(abs_error)

        if abs_error < tolerance:
            return {
                "iterations": list_ite[-last_n_rows:],
                "roots": list_root[-last_n_rows:],
                "errors": list_abs[-last_n_rows:],
                "final_root": middle,
                "message": "Converged"
            }

        x_0 = middle

    return {
        "iterations": list_ite[-last_n_rows:],
        "roots": list_root[-last_n_rows:],
        "errors": list_abs[-last_n_rows:],
        "final_root": middle,
        "message": "Max iterations reached"
    }


def bisection_controller(function: str, a: float, b: float, nmax: int, last_n_rows: int, tolerance: float):
    # Debug prints
    print("=== Parámetros recibidos en bisection_controller ===")
    print(f"function: {function}")
    print(f"a: {a}")
    print(f"b: {b}")
    print(f"nmax: {nmax}")
    print(f"last_n_rows: {last_n_rows}")
    print(f"tolerance: {tolerance}")
    print("====================================================")
    
    answer = bisection(function, a, b, nmax, last_n_rows, tolerance)

    return answer
