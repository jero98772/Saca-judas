import numpy as np

def gauss_simple(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)

    det = np.linalg.det(A)
    if np.isclose(det, 0):
        print("\n=== Check ===")
        print("A =")
        print_augmented_matrix(A, b, decimals)
        print("det(A) ≈ 0 → las soluciones pueden ser inestables por divisiones grandes.")
        return None

    print(f"\n=== Initial ===")
    print(f"Determinant = {det:.4f}")
    print("Sistema inicial [A | b]:")
    print_augmented_matrix(A, b, decimals)

    # Eliminación hacia adelante
    for k in range(n - 1):
        if np.isclose(A[k, k], 0):
            print(f"\n=== Iteration {k+1} ===")
            print(f"El pivote en la fila {k+1} es cero. El método falla.")
            return None

        for i in range(k + 1, n):
            if np.isclose(A[i, k], 0):
                continue
            m = A[i, k] / A[k, k]
            A[i, k:] = A[i, k:] - m * A[k, k:]
            b[i] = b[i] - m * b[k]

        print(f"\n=== Iteration {k+1} ===")
        print(f"Eliminación en la columna {k+1} completada.")
        print_augmented_matrix(A, b, decimals)

    # Sustitución regresiva
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if np.isclose(A[i, i], 0):
            print("\n=== Back Substitution ===")
            print(f"Pivote cero en la fila {i+1}. El método falla.")
            return None
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]

    print("\n=== Back Substitution ===")
    print("Sustitución regresiva completa.")
    print("Solución x =", x.round(decimals))

    return x.round(decimals).tolist()

def gauss_partial(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)

    det = np.linalg.det(A)
    if np.isclose(det, 0):
        print("\n=== Check ===")
        print("A =")
        print_augmented_matrix(A, b, decimals)
        print("det(A) ≈ 0 → las soluciones pueden ser inestables por divisiones grandes.")
        return None

    print(f"\n=== Initial ===")
    print(f"Determinant = {det:.4f}")
    print("Sistema inicial [A | b]:")
    print_augmented_matrix(A, b, decimals)

    for k in range(n - 1):
        max_row = np.argmax(np.abs(A[k:, k])) + k

        if np.allclose(A[k:, k], 0):
            print(f"\n=== Iteration {k+1} ===")
            print(f"Todos los elementos en la columna {k+1} desde la fila {k+1} hacia abajo son cero. Método falla.")
            return None

        if np.isclose(A[max_row, k], 0):
            print(f"\n=== Iteration {k+1} ===")
            print(f"No se encontró un pivote no nulo en la columna {k+1}. Método falla.")
            return None

        if max_row != k:
            A[[k, max_row]] = A[[max_row, k]]
            b[[k, max_row]] = b[[max_row, k]]
            print(f"\n=== Pivot {k+1} ===")
            print(f"Filas {k+1} y {max_row+1} intercambiadas (pivoteo parcial).")
            print_augmented_matrix(A, b, decimals)

        if np.allclose(A[k+1:, k], 0):
            print(f"\n=== Iteration {k+1} ===")
            print(f"La columna {k+1} ya tiene ceros debajo del pivote. Se omite eliminación.")
            continue

        for i in range(k + 1, n):
            if np.isclose(A[i, k], 0):
                continue
            m = A[i, k] / A[k, k]
            A[i, k:] -= m * A[k, k:]
            b[i] -= m * b[k]

        print(f"\n=== Iteration {k+1} ===")
        print(f"Eliminación en la columna {k+1} completada.")
        print_augmented_matrix(A, b, decimals)

    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if np.isclose(A[i, i], 0):
            print("\n=== Back Substitution ===")
            print(f"Pivote nulo (o casi nulo) en la fila {i+1}. Método falla.")
            return None
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]

    print("\n=== Back Substitution ===")
    print("Sustitución regresiva completa.")
    print("Solución x =", x.round(decimals))

    return x.round(decimals).tolist()

def gauss_total(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    marks = np.arange(n)

    det = np.linalg.det(A)
    if np.isclose(det, 0):
        print("\n=== Check ===")
        print("A =")
        print_augmented_matrix(A, b, decimals)
        print("Matrix is not invertible (det ≈ 0).")
        return None

    print(f"\n=== Initial ===")
    print(f"Determinant = {det:.4f}")
    print("Initial system [A | b]:")
    print_augmented_matrix(A, b, decimals)

    for k in range(n - 1):
        submatrix = np.abs(A[k:, k:])
        p, q = np.unravel_index(np.argmax(submatrix), submatrix.shape)
        p += k
        q += k

        if np.isclose(A[p, q], 0):
            print(f"\n=== Iteration {k+1} ===")
            print(f"Pivot at position ({p+1},{q+1}) is zero. Method fails.")
            return None

        if q != k:
            A[:, [k, q]] = A[:, [q, k]]
            marks[[k, q]] = marks[[q, k]]

        if p != k:
            A[[k, p], :] = A[[p, k], :]
            b[[k, p]] = b[[p, k]]

        print(f"\n=== Pivot {k+1} ===")
        print(f"Swapped column {k+1} ↔ {q+1} and row {k+1} ↔ {p+1} for total pivoting.")
        print_augmented_matrix(A, b, decimals)

        for i in range(k + 1, n):
            if np.isclose(A[i, k], 0):
                continue
            m = A[i, k] / A[k, k]
            A[i, k:] -= m * A[k, k:]
            b[i] -= m * b[k]

        print(f"\n=== Iteration {k+1} ===")
        print(f"Elimination at column {k+1} complete.")
        print_augmented_matrix(A, b, decimals)

    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if np.isclose(A[i, i], 0):
            print("\n=== Back Substitution ===")
            print(f"Zero (or near-zero) pivot at row {i+1}. Method fails.")
            return None
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]

    x_final = np.zeros(n)
    for i in range(n):
        x_final[marks[i]] = x[i]

    print("\n=== Back Substitution ===")
    print("Back substitution complete.")
    print("Final solution x =", x_final.round(decimals))

    return x_final.round(decimals).tolist()


def lu_simple(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)

    L = np.eye(n)
    U = A.copy()

    det = np.linalg.det(A)
    if np.isclose(det, 0):
        print("\n=== Check ===")
        print("A =", A.round(decimals))
        print("b =", b.round(decimals))
        print("Matrix is not invertible (det ≈ 0).")
        return None

    print(f"\n=== Initial ===")
    print(f"Determinant = {det:.4f}")
    print("A =\n", A.round(decimals))
    print("b =", b.round(decimals))

    for k in range(n):
        for i in range(k + 1, n):
            if np.isclose(U[k, k], 0):
                factor = 0
            else:
                factor = U[i, k] / U[k, k]
            L[i, k] = factor
            U[i, k:] -= factor * U[k, k:]
            A[i, k:] = U[i, k:]

        print(f"\n=== Step {k+1} ===")
        print(f"Elimination in column {k+1} complete.")
        print("A =\n", A.round(decimals))
        print("L =\n", L.round(decimals))
        print("U =\n", U.round(decimals))

    # Ly = b
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - np.dot(L[i, :i], y[:i])

    print("\n=== Forward Substitution ===")
    print("y =", y.round(decimals))
    print("Forward substitution complete (Ly = b).")

    # Ux = y
    x = np.zeros(n)
    for i in reversed(range(n)):
        if np.isclose(U[i, i], 0):
            print("\n=== Backward Substitution ===")
            print("Zero pivot at row", i+1, ". Method fails.")
            return None
        x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i, i]

    print("\n=== Backward Substitution ===")
    print("x =", x.round(decimals))
    print("Backward substitution complete (Ux = y).")

    print("\n=== Final Solution ===")
    print("x =", x.round(decimals))

    return x.round(decimals).tolist()

def print_augmented_matrix(A, b, decimals):
    for row, bi in zip(A, b):
        row_str = "  ".join(f"{val:.{decimals}f}" for val in row)
        print(f"{row_str} | {bi:.{decimals}f}")
    print()

import numpy as np

def lu_partial_pivot(A: list, b: list, decimals: int = 6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)

    L = np.eye(n)
    U = A.copy()
    P = np.eye(n)

    det = np.linalg.det(A)
    if np.isclose(det, 0):
        print("Matrix is not invertible (det ≈ 0).")
        return None

    print(f"Initial system. Determinant = {det:.4f}")
    print("A | b:")
    print_augmented_matrix(A, b, decimals)
    print()

    for k in range(n):

        max_row = np.argmax(np.abs(U[k:, k])) + k
        if max_row != k:
            U[[k, max_row], :] = U[[max_row, k], :]
            if k > 0:
                L[[k, max_row], :k] = L[[max_row, k], :k]
            P[[k, max_row], :] = P[[max_row, k], :]
            b[[k, max_row]] = b[[max_row, k]]

        for i in range(k+1, n):
            if np.isclose(U[k, k], 0):
                factor = 0
            else:
                factor = U[i, k] / U[k, k]
            L[i, k] = factor
            U[i, k:] -= factor * U[k, k:]

        print(f"Step {k+1}: Elimination in column {k+1} complete with partial pivoting.")
        print("L:")
        print(np.round(L, decimals))
        print("U:")
        print(np.round(U, decimals))
        print("P (Pivot matrix):")
        print(np.round(P, decimals))
        print()

    # Ly = Pb
    y = np.zeros(n)
    Pb = np.dot(P, b)
    for i in range(n):
        y[i] = Pb[i] - np.dot(L[i, :i], y[:i])

    print("Forward Substitution (Ly = Pb) complete.")
    print("y =", np.round(y, decimals))
    print()

    # Ux = y
    x = np.zeros(n)
    for i in reversed(range(n)):
        if np.isclose(U[i, i], 0):
            print(f"Zero pivot at row {i+1}. Method fails.")
            return None
        x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i, i]

    print("Backward Substitution (Ux = y) complete.")
    print("x =", np.round(x, decimals))
    print()

    print("Final Pivot Matrix (P):")
    print(np.round(P, decimals))
    print()

    return x.round(decimals).tolist()

import numpy as np

def jacobi(A, b, x0=None, tol=1e-6, max_iter=100, decimals=6):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)

    # inicial
    if x0 is None:
        x = np.zeros(n)
    else:
        x = np.array(x0, dtype=float)

    # comprobar diagonal no cero
    diag = np.diag(A)
    if np.any(np.isclose(diag, 0)):
        raise ValueError("La matriz A tiene algún a_ii ≈ 0 en la diagonal; Jacobi no se puede aplicar directamente.")

    # descomposición D y R
    D = np.diagflat(diag)
    R = A - D
    D_inv = np.diag(1.0 / diag)           # forma eficiente de invertir la diagonal
    T = - D_inv @ R                       # matriz iterativa
    c = D_inv @ b

    # radio espectral
    eigs = np.linalg.eigvals(T)
    rho = max(np.abs(eigs))

    print("=== Método de Jacobi (con error en norma 2 y radio espectral) ===")
    print("A | b:")
    for row, bi in zip(A, b):
        row_str = "  ".join(f"{val:.{decimals}f}" for val in row)
        print(f"{row_str} | {bi:.{decimals}f}")
    print()
    print("D =")
    print(np.round(D, decimals))
    print("\nR = A - D =")
    print(np.round(R, decimals))
    print()
    print("Matriz iterativa T = -D^{-1} R :")
    print(np.round(T, decimals))
    print("\nVector constante c = D^{-1} b :")
    print(np.round(c, decimals))
    print()
    print(f"Radio espectral ρ(T) = {rho:.6f}")
    if rho >= 1:
        print("AVISO: ρ(T) ≥ 1 → la convergencia no está garantizada (puede divergir).")
    else:
        print("ρ(T) < 1 → convergencia garantizada (condición suficiente).")
    print()
    print(f"Vector inicial x^(0) = {np.round(x, decimals)}")
    print()

    # iteraciones
    converged = False
    for k in range(1, max_iter + 1):
        x_new = T @ x + c
        error = np.linalg.norm(x_new - x, 2)   # norma 2 del cambio entre iteraciones

        print(f"Iteración {k}: x^(k) = {np.round(x_new, decimals)},  error (||x^(k)-x^(k-1)||_2) = {error:.{decimals}e}")

        if error < tol:
            print("\nConvergencia alcanzada.")
            converged = True
            x = x_new
            break

        x = x_new

    if not converged:
        print("\nNo se alcanzó convergencia en el número máximo de iteraciones.")

    print("\nSolución aproximada final x =", np.round(x, decimals))
    return {
        "x": x.round(decimals).tolist(),
        "rho": float(rho),
        "converged": bool(converged),
        "iterations": k
    }


# Ejemplo de uso:
A = [
    [14, 6, -2, 3],
    [0, 13.71, 2.42, -5.64],
    [0, 7, -24, 3.5],
    [0, -3.42, -1.85, 15.78]
]

b = [12, 29.42, -18, 13.14]

# gauss_simple(A, b, 6)


A = [
    [-7, 2, -3, 4],
    [5, -1, 14, -1],
    [1, 9, -7, 5],
    [-12, 13, -8, -4]
]

b = [-12, 13, 31, -32]

# gauss_partial(A,b,6)


A = [
    [-7, 2, -3, 4],
    [5, -1, 14, -1],
    [1, 9, -7, 13],
    [-12, 13, -8, -4]
]

b = [-12, 13, 31, -32]

# gauss_total(A, b, 6)


A = [
    [4, 3, -2, -7],
    [3, 12, 8, -3],
    [2, 3, -9, 3],
    [1, -2, -5, 6]
]

b = [20, 18, 31, 12]


# lu_simple(A,b,6)


A = [
    [-7, 2, -3, 4],
    [5, -1, 14, -1],
    [1, 9, -7, 5],
    [-12, 13, -8, -4]
]

b = [-12, 13, 31, -32]

# lu_partial_pivot(A,b,6)
A = [
    [10,-3,0,-1],
    [-3,15,2,9],
    [0,2,10,2],
    [-1,9,2,9]
]

b = [1,1,1,1]

A = [
    [10, -3, 0, -1],
    [-3, 15, 2, 9],
    [0, 2, 10, 2],
    [-1, 9, 2, 9]
]

b = [1,1,1,1]

x0 = [1, 2, 3, 4]  # Vector inicial dado: x con un cero arriba

# jacobi(A, b, x0=x0, tol=1e-6, max_iter=25)


import numpy as np

# Definir N
N = 59

# Definir matriz A y vector b
A = np.array([
    [10, -3,  0,  -1],
    [-3, 15,  2,   N],
    [0,   2,  N+1, 2],
    [-1,  N,  2,   9]
], dtype=float)

b = np.array([1, 1, 1, 1], dtype=float)

# Calcular valores propios
valores_propios = np.linalg.eigvals(A)

# print("Matriz A =\n", A)
# print("\nVector b =", b)
# print("\nValores propios de A =", valores_propios)

def gaussEliminationTridigonal(a,b,c,d):
    n = len(b)
    for k in range(n - 1):
        m = a[k]/b[k]
        b[k + 1] = b[k + 1] - (m*c[k])
        d[k + 1] = d[k + 1] - (m*d[k])
        
    print(b)
    print(d)     
        
    return b,d


A = [
    [5,  2,  0,   0,   0,   0],
    [1,  4,  2,   0,   0,   0],
    [0, -4, 10,   3,   0,   0],
    [0,  0,  3,  12,  -8,   0],
    [0,  0,  0,   5, -25,   4],
    [0,  0,  0,   0,   7,  12]
]

b = [12, 24, -8, 13, -30, 9]

gauss_simple(A, b)

a = [1,-4,3,5, 7 ]
b = [5,4,10,12,-25,12]
c = [2,2,3,-8,4]
d = [12, 24, -8, 13, -30, 9]

gaussEliminationTridigonal(a,b,c,d)


A = np.array([[1, -2],
              [3,  4]])

# Normas
n1 = np.linalg.norm(A, 1)       # norma 1 (máx suma de columnas)
ninf = np.linalg.norm(A, np.inf)  # norma infinita (máx suma de filas)
n2 = np.linalg.norm(A, 2)       # norma espectral
nf = np.linalg.norm(A, 'fro')   # norma de Frobenius