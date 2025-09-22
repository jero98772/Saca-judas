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

    for n in range(Nmax):
        try:
            denom = (f1(x0)**2 - func(x0)*f2(x0))
            if denom == 0:
                return {
                    "message": "Denominador se anuló (f'(x)^2 - f(x)f''(x) = 0)",
                    "value": x0,
                    "type": "danger",
                    "historial": {
                        "x": historial_x,
                        "errorAbs": historial_errorAbs,
                        "iteraciones": historial_iteraciones
                    }
                }

            x1 = x0 - (func(x0) * f1(x0)) / denom
        except Exception as e:
            return {
                "message": f"Error en la iteración: {str(e)}",
                "value": x0,
                "type": "danger",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }

        errorAbs = abs(x1 - x0)

        # Guardar en historial
        historial_x.append(x0)
        historial_errorAbs.append(errorAbs)
        historial_iteraciones.append(n)

        if len(historial_x) > ultimasNfilas:
            historial_x.pop(0)
            historial_errorAbs.pop(0)
            historial_iteraciones.pop(0)

        # Verificar tolerancia
        if errorAbs < tol:
            return {
                "message": "Tolerancia satisfecha",
                "value": x1,
                "type": "success",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
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
            "iteraciones": historial_iteraciones
        }
    }


def newton_multiple_controller(function: str, x0: float, Nmax: int, tol: float, nrows: int, df: str = None, d2f: str = None):
    return newton_multiple_method(function, x0, tol, Nmax, nrows, df, d2f)
