from sympy import *

def bisection(f: str, a: float, b: float, nmax: int, last_n_rows: int, tolerance: float):

    if f is None or f.strip() == "":
        return {"message": "You must input a function"}
    if a is None:
        return {"message": "You must input the left interval endpoint (a)"}
    if b is None:
        return {"message": "You must input the right interval endpoint (b)"}
    if a >= b:
        return {"message": "Left endpoint 'a' must be less than right endpoint 'b'"}
    if nmax is None and tolerance is not None:
        from math import log, ceil
        nmax = ceil(log((b - a) / tolerance, 2))
    elif nmax <= 0:
        return {"message": "You must input a positive number of iterations (nmax)"}

    if last_n_rows is None or last_n_rows < 0:
        return {"message": "You must input a non-negative number for last_n_rows"}
    if tolerance is None or tolerance <= 0:
        return {"message": "You must input a positive tolerance"}


    x = symbols("x")
    f_math = lambdify(x, sympify(f), "math")

    if f_math(a) == 0:
        return {"message": f"Root found at a = {a}"}
    if f_math(b) == 0:
        return {"message": f"Root found at b = {b}"}


    if f_math(a) * f_math(b) > 0:
        return {"message": "The function must change sign in the interval [a, b]"}
    
    list_ite, list_a, list_b, list_root, list_abs = [], [], [], [], []

    x_0 = (a+b)/2  # initial midpoint
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
