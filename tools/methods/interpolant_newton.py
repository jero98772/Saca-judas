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


def interpolant_newton(x, diff):
    
    x_sym = symbols('x')
    n = len(x)
    P = diff[0][0]
    prod = 1
    for i in range(1, n):
        prod *= (x_sym - x[i - 1])
        P += diff[0][i] * prod
    return simplify(expand(P))




x = [1, 1.2, 1.4, 1.6, 1.8, 2]
y = [0.6747, 0.8491, 1.1214, 1.4921, 1.9607, 2.5258]

diff, tabla = divided_differences(x, y)

print("\n Divided differences table:\n")
print(tabla.to_string(index=False))

P = interpolant_newton(x, diff)

print("\n Polynomial interpolant Newton:\n")
print(f"P(x) = {P}")
