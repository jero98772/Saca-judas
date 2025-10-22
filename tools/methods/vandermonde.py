import numpy as np

def vandermonde_interpolation(x, y):
    
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)


    V = np.vander(x, N=len(x), increasing=True)

    
    coef = np.linalg.solve(V, y)
    print(V)

    return coef



x = [1, 1.2, 1.4, 1.6, 1.8, 2]
y = [0.6747, 0.8491, 1.1214, 1.4921, 1.9607, 2.5258] 

coef = vandermonde_interpolation(x, y)

print("Coeficientes del polinomio:")
print(coef)


p = np.poly1d(coef[::-1])
print("\nPolinomio resultante:")
print(p)
print("\nP(5) =", p(5))
