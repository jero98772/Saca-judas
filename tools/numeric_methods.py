import random
from math import *

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

def LU_gaussian_simple():
    """Placeholder for LU with gaussian simple Method implementation."""
    pass

def LU_parcial_pivot():
    """Placeholder for LU with parcial pivot Method implementation."""
    pass

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

