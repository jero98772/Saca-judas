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

import numpy as np

def newton_method(F, J, x0, tol=1e-6, max_iter=50):
    """
    Newton's method for solving systems of nonlinear equations.
    
    Parameters:
    F : function
        Vector function F(x) which returns a numpy array of function values at x.
    J : function
        Jacobian matrix function J(x) which returns the Jacobian matrix at x.
    x0 : numpy array
        Initial guess for the solution.
    tol : float, optional
        Tolerance for stopping criterion (default is 1e-6).
    max_iter : int, optional
        Maximum number of iterations (default is 50).
        
    Returns:
    x : numpy array
        The approximate solution.
    converged : bool
        True if the method converged within tolerance, False otherwise.
    iterations : int
        Number of iterations performed.
    """
    x = x0.copy()
    Fx = F(x)
    for k in range(max_iter):
        Fx_norm = np.linalg.norm(Fx)
        if Fx_norm < tol:
            return x, True, k
        
        Jx = J(x)
        dx = np.linalg.solve(Jx, -Fx)
        x += dx
        Fx = F(x)
    
    Fx_norm = np.linalg.norm(Fx)
    converged = Fx_norm < tol
    return x, converged, max_iter

import numpy as np

def LU_gaussian_simple(A):
    """
    Performs LU decomposition of a square matrix using Gaussian elimination without pivoting.
    
    This function decomposes matrix A into a lower triangular matrix L (with unit diagonal)
    and an upper triangular matrix U such that A = L * U.
    
    Parameters:
    A : numpy.ndarray
        A square matrix of shape (n, n) to be decomposed
        
    Returns:
    tuple (L, U) or str:
        If successful: 
            L : numpy.ndarray - Lower triangular matrix with 1s on diagonal (shape (n, n))
            U : numpy.ndarray - Upper triangular matrix (shape (n, n))
        If error:
            str - Error message describing the problem
            
    Raises:
        ValueError: If input is not a square matrix
        ValueError: If a zero pivot is encountered during elimination
        
    Example:
    >>> A = np.array([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]])
    >>> L, U = LU_gaussian_simple(A)
    >>> np.allclose(A, L @ U)
    True
    """
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
    """
    Performs LU decomposition with partial pivoting for numerical stability.
    
    Decomposes matrix A into a permutation matrix P, a lower triangular matrix L (with unit diagonal),
    and an upper triangular matrix U such that P * A = L * U.
    
    Parameters:
    A : numpy.ndarray
        A square matrix of shape (n, n) to be decomposed
        
    Returns:
    tuple (P, L, U) or str:
        If successful:
            P : numpy.ndarray - Permutation matrix (shape (n, n))
            L : numpy.ndarray - Lower triangular matrix with 1s on diagonal (shape (n, n))
            U : numpy.ndarray - Upper triangular matrix (shape (n, n))
        If error:
            str - Error message describing the problem
            
    Raises:
        ValueError: If input is not a square matrix
        ValueError: If matrix is singular (all pivots near zero)
        
    Example:
    >>> A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> P, L, U = LU_parcial_pivot(A)
    >>> np.allclose(P @ A, L @ U)
    True
    """
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

import numpy as np

def crout(A):
    """
    Performs Crout decomposition of a square matrix.
    
    Decomposes matrix A into a lower triangular matrix L and an upper triangular matrix U 
    with 1s on the diagonal of U such that A = L * U.
    
    Parameters:
    A : numpy.ndarray
        A square matrix of shape (n, n) to be decomposed
        
    Returns:
    L, U : numpy.ndarray
        L: Lower triangular matrix (shape (n, n))
        U: Upper triangular matrix with 1s on diagonal (shape (n, n))
        
    Raises:
    ValueError: If input is not a square matrix
    ValueError: If matrix is singular (zero pivot encountered)
    
    Example:
    >>> A = np.array([[7, 3, -1], [2, 5, 1], [4, -1, 6]])
    >>> L, U = crout(A)
    >>> np.allclose(A, L @ U)
    True
    """
    n = A.shape[0]
    if n != A.shape[1]:
        raise ValueError("Matrix must be square")
    
    L = np.zeros((n, n))
    U = np.eye(n)  # Diagonal will be 1s
    
    for j in range(n):
        # Calculate elements in L below diagonal
        for i in range(j, n):
            s = sum(L[i, k] * U[k, j] for k in range(j))
            L[i, j] = A[i, j] - s
        
        # Check for zero pivot
        if abs(L[j, j]) < 1e-10:
            raise ValueError("Zero pivot encountered at position {}".format(j))
        
        # Calculate elements in U above diagonal
        for i in range(j+1, n):
            s = sum(L[j, k] * U[k, i] for k in range(j))
            U[j, i] = (A[j, i] - s) / L[j, j]
    
    return L, U

def cholesky(A):
    """
    Performs Cholesky decomposition of a symmetric positive-definite matrix.
    
    Decomposes matrix A into a lower triangular matrix L such that A = L * Lᵀ.
    
    Parameters:
    A : numpy.ndarray
        A symmetric positive-definite square matrix of shape (n, n)
        
    Returns:
    L : numpy.ndarray
        Lower triangular matrix (shape (n, n))
        
    Raises:
    ValueError: If input is not square
    ValueError: If matrix is not symmetric
    ValueError: If matrix is not positive definite
    
    Example:
    >>> A = np.array([[4, 12, -16], [12, 37, -43], [-16, -43, 98]])
    >>> L = cholesky(A)
    >>> np.allclose(A, L @ L.T)
    True
    """
    n = A.shape[0]
    if n != A.shape[1]:
        raise ValueError("Matrix must be square")
    if not np.allclose(A, A.T):
        raise ValueError("Matrix must be symmetric")
    
    L = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i+1):
            s = sum(L[i, k] * L[j, k] for k in range(j))
            
            if i == j:  # Diagonal elements
                # Check for positive definiteness
                diag_val = A[i, i] - s
                if diag_val <= 1e-10:
                    raise ValueError("Matrix not positive definite")
                L[i, j] = np.sqrt(diag_val)
            else:  # Off-diagonal elements
                L[i, j] = (A[i, j] - s) / L[j, j]
    
    return L

def doolittle(A):
    """
    Performs Doolittle decomposition of a square matrix.
    
    Decomposes matrix A into a lower triangular matrix L (with 1s on diagonal)
    and an upper triangular matrix U such that A = L * U.
    
    Parameters:
    A : numpy.ndarray
        A square matrix of shape (n, n) to be decomposed
        
    Returns:
    L, U : numpy.ndarray
        L: Lower triangular matrix with 1s on diagonal (shape (n, n))
        U: Upper triangular matrix (shape (n, n))
        
    Raises:
    ValueError: If input is not a square matrix
    ValueError: If matrix is singular (zero pivot encountered)
    
    Example:
    >>> A = np.array([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]])
    >>> L, U = doolittle(A)
    >>> np.allclose(A, L @ U)
    True
    """
    n = A.shape[0]
    if n != A.shape[1]:
        raise ValueError("Matrix must be square")
    
    L = np.eye(n)  # Diagonal will be 1s
    U = np.zeros((n, n))
    
    for i in range(n):
        # Calculate elements in U for row i
        for j in range(i, n):
            s = sum(L[i, k] * U[k, j] for k in range(i))
            U[i, j] = A[i, j] - s
        
        # Check for zero pivot
        if abs(U[i, i]) < 1e-10:
            raise ValueError("Zero pivot encountered at position {}".format(i))
        
        # Calculate elements in L for column i
        for j in range(i+1, n):
            s = sum(L[j, k] * U[k, i] for k in range(i))
            L[j, i] = (A[j, i] - s) / U[i, i]
    
    return L, U
    
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

