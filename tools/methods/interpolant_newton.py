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

# --- ejemplo de uso con tus datos ---
x = [1, 1.2, 1.4, 1.6, 1.8, 2]
y = [0.6747, 0.8491, 1.1214, 1.4921, 1.9607, 2.5258]

diff, tabla = divided_differences(x, y)
print("\n Divided differences table:\n")
print(tabla.to_string(index=False))

P_sym, P_newton_str = interpolant_newton_newform(x, diff)
print("\nPolinomio (forma simbólica simplificada):")
print(f"P(x) = {P_sym}")

print("\nPolinomio en forma Newton (coeficientes b_i):")
print("Pn(x) =", P_newton_str)
