import math

def newton_prime(f, df, x0, tolerance=1e-7, max_iter=100):
    """
    Newton's method (Newton-Raphson) for finding roots with JSON-compatible output.
    
    Parameters:
    f: function
    df: derivative of function
    x0: initial guess
    tolerance: convergence tolerance
    max_iter: maximum iterations
    
    Returns:
    dict: JSON-compatible result with message, value, and iteration history
    """
    x = x0
    historial_x = [x0]
    historial_errorAbs = []
    historial_iteraciones = []
    
    for i in range(1, max_iter + 1):
        fx = f(x)
        dfx = df(x)
        
        if abs(dfx) < 1e-12:
            return {
                "message": f"Derivada demasiado pequeña en la iteración {i}",
                "value": None,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        
        x_new = x - fx / dfx
        error_abs = abs(x_new - x)
        
        # Update history
        historial_x.append(x_new)
        historial_errorAbs.append(error_abs)
        historial_iteraciones.append(i)
        
        if error_abs < tolerance:
            return {
                "message": "Tolerancia satisfecha",
                "value": x_new,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        
        x = x_new
    
    # If we reach here, the method didn't converge
    return {
        "message": "Máximo número de iteraciones alcanzado",
        "value": x,
        "historial": {
            "x": historial_x,
            "errorAbs": historial_errorAbs,
            "iteraciones": historial_iteraciones
        }
    }
    
    import numpy as np
import pandas as pd
from sympy import symbols, simplify, expand

def divided_differences(x, y, decimales=4):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    n = len(x)
    diff = np.zeros((n, n))
    diff[:, 0] = y

    for j in range(1, n):
        for i in range(n - j):
            diff[i][j] = (diff[i + 1][j - 1] - diff[i][j - 1]) / (x[i + j] - x[i])

    columnas = ['x_i', 'y=f[x_i]'] + [f'{j}ra' if j == 1 else f'{j}da' for j in range(1, n)]
    tabla = pd.DataFrame('', index=range(n), columns=columnas)
    tabla['x_i'] = np.round(x, decimales)
    tabla['y=f[x_i]'] = np.round(y, decimales)

    for j in range(1, n):
        for i in range(j, n):
            valor = diff[i - j][j]
            tabla.loc[i, columnas[j + 1]] = f"{valor:.{decimales}f}"

    return diff, tabla

def interpolant_newton_newform(x, diff, decimales=6):
    """
    Devuelve:
      - expr_sym: expresión simbólica simplificada del polinomio P(x)
      - poly_str : cadena con la forma Newton solicitada:
                   Pn(x)=b0 + b1(x-x0) + b2(x-x0)(x-x1) + ...
    """
    x_sym = symbols('x')
    n = len(x)
    # b_i son las diferencias divididas de la primera fila
    b = [diff[0, i] for i in range(n)]

    # construir expresión simbólica
    P = b[0]
    prod = 1
    for i in range(1, n):
        prod *= (x_sym - x[i - 1])
        P += b[i] * prod
    expr_sym = simplify(expand(P))

    # construir cadena en forma Newton con formato numérico
    terms = [f"{b[0]:.{decimales}f}"]
    for i in range(1, n):
        factor = "".join([f"(x-{x[j]})" for j in range(i)])  # (x-x0)(x-x1)...
        terms.append(f"{b[i]:.{decimales}f}*{factor}")
    poly_str = " + ".join(terms)

    return expr_sym, poly_str



