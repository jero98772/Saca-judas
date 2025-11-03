from sympy import *

def secant_method(f: str, x0: float, x1: float, tol: float, Nmax: int, lastNrows: int):
    Nmax = int(Nmax)
    x = symbols("x")
    func = lambdify(x, sympify(f), "math")

    history_iter = []
    history_x = []
    history_fx = []
    history_error = []

    for n in range(Nmax):
        try:
            f_x0 = func(x0)
            f_x1 = func(x1)
            if f_x1 - f_x0 == 0:
                return {
                    "message": "Division by zero occurred in denominator (f(x1) - f(x0))",
                    "value": x1,
                    "type": "danger",
                    "history": {
                        "iter": history_iter,
                        "xi": history_x,
                        "f(xi)": history_fx,
                        "E": history_error
                    }
                }

            x2 = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
            absError = abs(x2 - x1)

            # Save history (columns: iter, xi, f(xi), E)
            history_iter.append(n)
            history_x.append(x1)
            history_fx.append(f_x1)
            history_error.append(absError)

            # Limit history to last N rows
            if len(history_x) > lastNrows:
                history_iter.pop(0)
                history_x.pop(0)
                history_fx.pop(0)
                history_error.pop(0)

            if absError < tol:
                return {
                    "message": "Tolerance satisfied",
                    "value": x2,
                    "type": "success",
                    "history": {
                        "iter": history_iter,
                        "xi": history_x,
                        "f(xi)": history_fx,
                        "E": history_error
                    }
                }

            # Update points
            x0, x1 = x1, x2

        except ZeroDivisionError:
            return {
                "message": "Division by zero occurred during secant method calculation",
                "value": x1,
                "type":"danger",
                "history": {
                    "iter": history_iter,
                    "xi": history_x,
                    "f(xi)": history_fx,
                    "E": history_error
                }
            }

    return {
        "message": "Maximum number of iterations exceeded",
        "value": x2,
        "type":"danger",
        "history": {
            "iter": history_iter,
            "xi": history_x,
            "f(xi)": history_fx,
            "E": history_error
        }
    }


def secant_method_controller(function: str, x0: float, x1: float, Nmax: int, tol: float, nrows: int):
    # Debug prints
    print("=== Parameters received in secant_method_controller ===")
    print(f"function: {function}")
    print(f"x0: {x0}, x1: {x1}")
    print(f"Nmax: {Nmax}")
    print(f"tol: {tol}")
    print(f"nrows: {nrows}")
    print("=======================================================")

    # Call secant method
    answer = secant_method(function, x0, x1, tol, Nmax, nrows)

    return answer
