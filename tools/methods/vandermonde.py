import numpy as np

def newton_interpolation(x, y):
    """
    Calcula el polinomio de interpolación de Newton a partir de puntos (x, y)
    Devuelve los coeficientes b y una función que evalúa el polinomio.
    """
    n = len(x)
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    # Crear tabla de diferencias divididas
    coef = np.zeros([n, n])
    coef[:, 0] = y

    for j in range(1, n):
        for i in range(n - j):
            coef[i][j] = (coef[i + 1][j - 1] - coef[i][j - 1]) / (x[i + j] - x[i])

    b = coef[0, :]  # Coeficientes de Newton

    # Construir función evaluadora del polinomio
    def p(val):
        total = b[0]
        for i in range(1, n):
            term = b[i]
            for j in range(i):
                term *= (val - x[j])
            total += term
        return total

    return b, p, coef


# --- Ejemplo con tus datos ---
x = [1, 2, 3, 4, 5, 6]
y = [-1, 1.5, 59/50, 2, 0, 1]

b, p, tabla = newton_interpolation(x, y)

print("Coeficientes de Newton (b):")
print(b)

print("\nTabla de diferencias divididas:")
print(tabla)

print(f"\nP(3.5) = {p(3.5)}")

import sympy as sp

x_sym = sp.Symbol('x')
poly = b[0]
for i in range(1, len(b)):
    term = b[i]
    for j in range(i):
        term *= (x_sym - x[j])
    poly += term

print("\nPolinomio de Newton expandido:")
print(sp.expand(poly))
