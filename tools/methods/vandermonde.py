import numpy as np

def vandermonde_interpolation(x, y):
    
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)


    V = np.vander(x, N=len(x), increasing=True)

    
    coef = np.linalg.solve(V, y)
    print(V)

    return coef



x = [1, 1.2, 1.4, 1.6, 1.8, 2]