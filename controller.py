from tools.methods.newton import newton_method

def newton_method_controller(function: str, x0: float, Nmax: int, tol: float, nrows: int):
    # Debug prints
    print("=== Parámetros recibidos en newton_method_controller ===")
    print(f"function: {function}")
    print(f"x0: {x0}")
    print(f"Nmax: {Nmax}")
    print(f"tol: {tol}")
    print(f"nrows: {nrows}")
    print("========================================================")

    # Llamar al método de Newton
    answer = newton_method(function, x0, tol, Nmax, nrows)

    return answer
