import random
from math import *
import numpy as np

def iterative_sqrt(n,x,A):
    """Iterative SQRT algorithm implementation."""
    def formula(x,A):
        return sqrt(((x**3)+A)/(2*x))
    for i in range(n):
        x=formula(x,A)
    return x

def binary2decimal_float(binary_str: str) -> float:
    #check it maybe not work properly
    """Convert a binary string representation to a decimal floating-point number."""
    binary_str = binary_str.strip()
    if binary_str.startswith('-'):
        return -binary2decimal_float(binary_str[1:])

    if '.' in binary_str:
        integer_part, fractional_part = binary_str.split('.')
    else:
        integer_part, fractional_part = binary_str, ''

    # Convert integer part
    decimal_integer = int(integer_part, 2) if integer_part else 0

    # Convert fractional part
    decimal_fraction = 0
    for i, bit in enumerate(fractional_part):
        decimal_fraction += int(bit) * (2 ** -(i + 1))

    return decimal_integer + decimal_fraction

def decimal2binary_float(num: float, precision: int = 10) -> str:
    """Convert a decimal floating-point number to binary string representation."""
    if num < 0:
        return '-' + decimal2binary_float(-num, precision)

    integer_part = int(num)
    decimal_part = num - integer_part

    # Convert integer part to binary
    binary_integer = bin(integer_part)[2:]

    # Convert decimal part to binary
    binary_decimal = []
    count = 0
    while decimal_part and count < precision:
        decimal_part *= 2
        bit = int(decimal_part)
        binary_decimal.append(str(bit))
        decimal_part -= bit
        count += 1

    if binary_decimal:
        return f"{binary_integer}.{''.join(binary_decimal)}"
    else:
        return binary_integer

def newton_method():
    """Placeholder for Newton's Method implementation."""
    pass

def LU_gaussian_simple(A):
    #Need be tested
    n = A.shape[0]
    if n != A.shape[1]:
        return "Not valid Input"
    
    U = A.astype(float).copy()
    L = np.eye(n)
    
    for j in range(n-1):
        if abs(U[j, j]) < 1e-15:
            return "Not valid input :zero pivot encountered at position {}".format(j)
        for i in range(j+1, n):
            mult = U[i, j] / U[j, j]
            L[i, j] = mult
            U[i, j:] = U[i, j:] - mult * U[j, j:]
    
    return L, U

def LU_parcial_pivot(A):
    #Need be tested
    n = A.shape[0]
    if n != A.shape[1]:
        return "Not valid input"
    
    U = A.astype(float).copy()
    L = np.eye(n)
    perm = list(range(n))
    
    for j in range(n-1):
        pivot_row = j
        max_val = abs(U[j, j])
        for i in range(j+1, n):
            if abs(U[i, j]) > max_val:
                max_val = abs(U[i, j])
                pivot_row = i
        
        if max_val < 1e-15:
            return "Not valid input Matrix is singular to working precision"
        
        if pivot_row != j:
            U[[j, pivot_row], j:] = U[[pivot_row, j], j:]
            if j > 0:
                L[[j, pivot_row], :j] = L[[pivot_row, j], :j]
            perm[j], perm[pivot_row] = perm[pivot_row], perm[j]
        
        for i in range(j+1, n):
            mult = U[i, j] / U[j, j]
            L[i, j] = mult
            U[i, j:] = U[i, j:] - mult * U[j, j:]
    
    P = np.eye(n)[perm, :]
    return P, L, U

def crout():
    """Placeholder for crout Method implementation."""
    pass

def cholesky():
    """Placeholder for cholesky Method implementation."""
    pass

def doolittle():
    """Placeholder for doolittle Method implementation."""
    pass

def jacobi():
    """Placeholder for jacobi Method implementation."""
    pass

def gauss_seidel():
    """Placeholder for gauss-seidel Method implementation."""
    pass

def SOR():
    """Placeholder for SOR Method implementation."""
    pass

def vandermonde():
    """Placeholder for doolittle Method implementation."""
    pass

def lagrange():
    """Placeholder for jacobi lagrange implementation."""
    pass

def lineal_tracers():
    """Placeholder for lineal_tracers Method implementation."""
    pass

def cuadratic_tracers():
    """Placeholder for cuadratic_tracers Method implementation."""
    pass

def cubic_tracers():
    """Placeholder for cubic_tracers Method implementation."""
    pass

def incremental_search():
    """Placeholder for incremental_search Method implementation."""
    pass

def biseccion():
    """Placeholder for biseccion Method implementation."""
    pass

def fixed_point():
    """Placeholder for fixed_point Method implementation."""
    pass

def secante():
    """Placeholder for secante Method implementation."""
    pass

def multiples_roots():
    """Placeholder for multiples_roots Method implementation."""
    pass

def gaussian_elimination_simple():
    """Placeholder for gaussian_elimination_simple Method implementation."""
    pass

def gaussian_elimination_with_pivot_partial():
    """Placeholder for gaussian_elimination_with_pivot_partial Method implementation."""
    pass

def gaussian_elimination_with_pivot_total():
    """Placeholder for gaussian_elimination_with_pivot_total Method implementation."""
    pass

