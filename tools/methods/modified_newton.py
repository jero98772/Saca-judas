from sympy import *

def newton_multiple_method(
    f: str,
    x0: float,
    tol: float,
    Nmax: int,
    ultimasNfilas: int,
    df: str = None,
    d2f: str = None
):
    Nmax = int(Nmax)
    x = symbols("x")
    f_sym = sympify(f)
    denom = 0
    # Función
    func = lambdify(x, f_sym, "math")

    # Derivadas: usar las dadas o calcular
    if df is not None:
        f1 = lambdify(x, sympify(df), "math")
    else:
        f1 = lambdify(x, diff(f_sym, x), "math")

    if d2f is not None:
        f2 = lambdify(x, sympify(d2f), "math")
    else:
        f2 = lambdify(x, diff(f_sym, x, 2), "math")

    # Historial
    historial_x = []
    historial_iteraciones = []
    historial_errorAbs = []
    historial_denom = []

    for n in range(Nmax):
        try:
            denom = (f1(x0)**2 - func(x0)*f2(x0))
            if denom == 0:
                return {
                    "message": "Denominator equal to 0 (f'(x)^2 - f(x)f''(x) = 0)",
                    "value": x0,
                    "type": "danger",
                    "historial": {
                        "x": historial_x,
                        "errorAbs": historial_errorAbs,
                        "iteraciones": historial_iteraciones,
                        "denominadores": historial_denom
                    }
                }

            x1 = x0 - (func(x0) * f1(x0)) / denom

        except OverflowError:
            return {
                "message": "too Big or to small denominator (f'(x)^2 - f(x)f''(x) = 0)",
                "value": x0,
                "type":"danger",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones,
                    "denominadores": historial_denom
                }
            }
        except Exception as e:
            return {
                "message": f"Error en la iteración: {str(e)}",
                "value": x0,
                "type": "danger",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones,
                    "denominadores": historial_denom
                }
            }

        errorAbs = abs(x1 - x0)

        # Guardar en historial
        historial_x.append(x0)
        historial_errorAbs.append(errorAbs)
        historial_iteraciones.append(n)
        historial_denom.append(denom)

        if len(historial_x) > ultimasNfilas:
            historial_x.pop(0)
            historial_errorAbs.pop(0)
            historial_iteraciones.pop(0)
            historial_denom.pop(0)   

        # Verificar tolerancia
        if abs(func(x1)) < tol:
            return {
                "message": "Tolerancia satisfecha",
                "value": x1,
                "type": "success",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones,
                    "denominadores": historial_denom
                }
            }

        x0 = x1

    return {
        "message": "Cantidad de iteraciones superadas",
        "value": x1,
        "type": "info",
        "historial": {
            "x": historial_x,
            "errorAbs": historial_errorAbs,
            "iteraciones": historial_iteraciones,
            "denominadores": historial_denom
        }
    }


def newton_multiple_controller(
    function: str,
    x0: float,
    Nmax: int,
    tol: float,
    nrows: int,
    df: str = None,
    d2f: str = None
):
    # 🐞 Debug print
    print("\n[DEBUG] Parámetros recibidos en newton_multiple_controller:")
    print(f"  function = {function}")
    print(f"  df       = {df}")
    print(f"  d2f      = {d2f}")
    print(f"  x0       = {x0}")
    print(f"  Nmax     = {Nmax}")
    print(f"  tol      = {tol}")
    print(f"  nrows    = {nrows}\n")

    return newton_multiple_method(function, x0, tol, Nmax, nrows, df, d2f)

