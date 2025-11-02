import numpy as np

def vandermonde_interpolation(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    # Matriz de Vandermonde (en orden creciente de potencias)
    V = np.vander(x, N=len(x), increasing=False)

    # Resolver el sistema V * coef = y
    coef = np.linalg.solve(V, y)

    # Configurar formato de impresión sin notación científica
    np.set_printoptions(precision=5, suppress=True)

    print("Matriz de Vandermonde (V):")
    print(V)

    print("\nCoeficientes del polinomio:")
    print(coef)

    # Construir el polinomio como texto
    poly_str = "P(x) = "
    for i, c in enumerate(coef):
        term = f"{c:.6f}"
        if i == 0:
            poly_str += f"{term}"
        else:
            poly_str += f" + ({term})·x^{i}"
    print("\nPolinomio de Vandermonde:")
    print(poly_str)

    return coef

