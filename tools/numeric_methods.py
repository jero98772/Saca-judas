import random
from math import *
from manim import *
import numpy as np
from typing import Callable, Tuple



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
    return [x, converged, max_iter], step_by_step ,(0,0)

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
        return "Not valid Input"
    
    L = np.zeros((n, n))
    U = np.eye(n)  # Diagonal will be 1s
    
    for j in range(n):
        # Calculate elements in L below diagonal
        for i in range(j, n):
            s = sum(L[i, k] * U[k, j] for k in range(j))
            L[i, j] = A[i, j] - s
        
        # Check for zero pivot
        if abs(L[j, j]) < 1e-10:
            return "Not valid Input Zero pivot encountered at position {}".format(j)
        
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
        return "Not valid Input Matrix must be square"
    if not np.allclose(A, A.T):
        return "Not valid Input Matrix must be symmetric"
    
    L = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i+1):
            s = sum(L[i, k] * L[j, k] for k in range(j))
            
            if i == j:  # Diagonal elements
                # Check for positive definiteness
                diag_val = A[i, i] - s
                if diag_val <= 1e-10:
                    return "Not valid Input Matrix not positive definite"
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
        return "Not valid Input Matrix must be square"
    
    L = np.eye(n)  # Diagonal will be 1s
    U = np.zeros((n, n))
    
    for i in range(n):
        # Calculate elements in U for row i
        for j in range(i, n):
            s = sum(L[i, k] * U[k, j] for k in range(i))
            U[i, j] = A[i, j] - s
        
        # Check for zero pivot
        if abs(U[i, i]) < 1e-10:
            return "Not valid Input Zero pivot encountered at position {}".format(i)
        
        # Calculate elements in L for column i
        for j in range(i+1, n):
            s = sum(L[j, k] * U[k, i] for k in range(i))
            L[j, i] = (A[j, i] - s) / U[i, i]
    
    return L, U

import numpy as np

def jacobi(A, b, x0, tol=1e-6, max_iter=1000):
    """
    Solves a system of linear equations Ax = b using the Jacobi iterative method.
    
    Parameters:
    A : numpy.ndarray
        Coefficient matrix (n x n)
    b : numpy.ndarray
        Right-hand side vector (n,)
    x0 : numpy.ndarray
        Initial guess for solution (n,)
    tol : float, optional
        Tolerance for stopping criterion (default 1e-6)
    max_iter : int, optional
        Maximum number of iterations (default 1000)
        
    Returns:
    x : numpy.ndarray
        Approximate solution vector
    converged : bool
        True if method converged within tolerance, False otherwise
    k : int
        Number of iterations performed
    """
    n = A.shape[0]
    x = x0.copy()
    x_new = np.zeros_like(x)
    
    # Extract diagonal and off-diagonal components
    D = np.diag(A)
    R = A - np.diagflat(D)
    
    for k in range(max_iter):
        x_new = (b - np.dot(R, x)) / D
        
        # Compute residual and check convergence
        residual = np.linalg.norm(A @ x_new - b)
        if residual < tol:
            return x_new, True, k+1
        
        x = x_new.copy()
    
    # If max iterations reached
    return x_new, False, max_iter

def gauss_seidel(A, b, x0, tol=1e-6, max_iter=1000):
    """
    Solves a system of linear equations Ax = b using the Gauss-Seidel iterative method.
    
    Parameters:
    A : numpy.ndarray
        Coefficient matrix (n x n)
    b : numpy.ndarray
        Right-hand side vector (n,)
    x0 : numpy.ndarray
        Initial guess for solution (n,)
    tol : float, optional
        Tolerance for stopping criterion (default 1e-6)
    max_iter : int, optional
        Maximum number of iterations (default 1000)
        
    Returns:
    x : numpy.ndarray
        Approximate solution vector
    converged : bool
        True if method converged within tolerance, False otherwise
    k : int
        Number of iterations performed
    """
    n = A.shape[0]
    x = x0.copy()
    
    for k in range(max_iter):
        x_old = x.copy()
        for i in range(n):
            # Sum of elements before i (using updated values)
            s1 = np.dot(A[i, :i], x[:i])
            # Sum of elements after i (using old values)
            s2 = np.dot(A[i, i+1:], x_old[i+1:])
            x[i] = (b[i] - s1 - s2) / A[i, i]
        
        # Compute residual and check convergence
        residual = np.linalg.norm(A @ x - b)
        if residual < tol:
            return x, True, k+1
    
    # If max iterations reached
    return x, False, max_iter

def SOR(A, b, x0, omega, tol=1e-6, max_iter=1000):
    """
    Solves a system of linear equations Ax = b using Successive Over-Relaxation (SOR).
    
    Parameters:
    A : numpy.ndarray
        Coefficient matrix (n x n)
    b : numpy.ndarray
        Right-hand side vector (n,)
    x0 : numpy.ndarray
        Initial guess for solution (n,)
    omega : float
        Relaxation factor (typically 0 < omega < 2)
    tol : float, optional
        Tolerance for stopping criterion (default 1e-6)
    max_iter : int, optional
        Maximum number of iterations (default 1000)
        
    Returns:
    x : numpy.ndarray
        Approximate solution vector
    converged : bool
        True if method converged within tolerance, False otherwise
    k : int
        Number of iterations performed
    """
    n = A.shape[0]
    x = x0.copy()
    
    for k in range(max_iter):
        x_old = x.copy()
        for i in range(n):
            # Sum of elements before i (using updated values)
            s1 = np.dot(A[i, :i], x[:i])
            # Sum of elements after i (using old values)
            s2 = np.dot(A[i, i+1:], x_old[i+1:])
            # Gauss-Seidel update
            x_gs = (b[i] - s1 - s2) / A[i, i]
            # SOR update
            x[i] = (1 - omega) * x_old[i] + omega * x_gs
        
        # Compute residual and check convergence
        residual = np.linalg.norm(A @ x - b)
        if residual < tol:
            return x, True, k+1
    
    # If max iterations reached
    return x, False, max_iter

import numpy as np

def vandermonde(x, y, degree=None):
    """
    Computes polynomial interpolation using the Vandermonde matrix method.
    
    Parameters:
    x : array_like
        x-coordinates of data points (1D array)
    y : array_like
        y-coordinates of data points (1D array, same length as x)
    degree : int, optional
        Degree of the interpolating polynomial. Default is len(x)-1
        
    Returns:
    coeffs : ndarray
        Coefficients of the interpolating polynomial in descending order
        (a[0] + a[1]*x + ... + a[n]*x^n)
        
    Raises:
    ValueError: If x and y have different lengths
    ValueError: If degree is greater than number of points minus one
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    if len(x) != len(y):
        return "Not valid Inputx and y must have the same length"
    
    if degree is None:
        degree = len(x) - 1
    elif degree > len(x) - 1:
        return "Not valid Input Degree cannot exceed number of points minus one"
    
    # Construct Vandermonde matrix
    V = np.vander(x, degree + 1, increasing=True)
    
    # Solve for coefficients (least squares if overdetermined)
    coeffs = np.linalg.lstsq(V, y, rcond=None)[0]
    
    return coeffs

def lagrange(x, y, t):
    """
    Evaluates the Lagrange interpolating polynomial at given point(s).
    
    Parameters:
    x : array_like
        x-coordinates of data points (1D array)
    y : array_like
        y-coordinates of data points (1D array, same length as x)
    t : float or array_like
        Point(s) at which to evaluate the interpolating polynomial
        
    Returns:
    float or ndarray
        Interpolated value(s) at point(s) t
        
    Raises:
    ValueError: If x and y have different lengths
    """
    x = np.asarray(x)
    y = np.asarray(y)
    t = np.asarray(t)
    
    if len(x) != len(y):
        return "Not valid Input x and y must have the same length"
    
    n = len(x)
    result = np.zeros_like(t, dtype=float)
    
    for i in range(n):
        # Compute Lagrange basis polynomial L_i(t)
        L = np.ones_like(t)
        for j in range(n):
            if i != j:
                L *= (t - x[j]) / (x[i] - x[j])
        result += y[i] * L
    
    return result

import numpy as np

def lineal_tracers(x, y):
    """
    Computes linear spline interpolation between given data points.
    
    Parameters:
    x : array_like
        x-coordinates of data points (must be strictly increasing)
    y : array_like
        y-coordinates of data points (same length as x)
        
    Returns:
    function
        A piecewise linear function that can be evaluated at any point
        
    Raises:
    ValueError: If x and y have different lengths
    ValueError: If x is not strictly increasing
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    if len(x) != len(y):
        return "Not valid Input x and y must have the same length"
    if not np.all(np.diff(x) > 0):
        return "Not valid Input x must be strictly increasing"
    
    n = len(x) - 1
    slopes = np.zeros(n)
    intercepts = np.zeros(n)
    
    # Calculate slopes and intercepts for each segment
    for i in range(n):
        slopes[i] = (y[i+1] - y[i]) / (x[i+1] - x[i])
        intercepts[i] = y[i] - slopes[i] * x[i]
    
    # Create piecewise function
    def spline_evaluator(t):
        t = np.asarray(t)
        result = np.zeros_like(t)
        
        # Handle points below first x
        mask = t < x[0]
        result[mask] = y[0]
        
        # Handle points between segments
        for i in range(n):
            mask = (t >= x[i]) & (t <= x[i+1])
            result[mask] = slopes[i] * t[mask] + intercepts[i]
        
        # Handle points above last x
        mask = t > x[-1]
        result[mask] = y[-1]
        
        return result
    
    return spline_evaluator

def cuadratic_tracers(x, y):
    """
    Computes quadratic spline interpolation with continuous first derivatives.
    
    Parameters:
    x : array_like
        x-coordinates of data points (must be strictly increasing)
    y : array_like
        y-coordinates of data points (same length as x)
        
    Returns:
    function
        A piecewise quadratic function that can be evaluated at any point
        
    Raises:
    ValueError: If x and y have different lengths
    ValueError: If x is not strictly increasing
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    if len(x) != len(y):
        return "Not valid Input x and y must have the same length"
    if not np.all(np.diff(x) > 0):
        return "Not valid Input x must be strictly increasing"
    
    n = len(x) - 1
    # Coefficients: a_i, b_i, c_i for each segment i
    a = np.zeros(n)
    b = np.zeros(n)
    c = np.zeros(n)  # c = y
    
    # Set first derivative at left endpoint to zero (arbitrary choice)
    b[0] = 0
    
    # Calculate coefficients for each segment
    for i in range(n):
        c[i] = y[i]
        if i > 0:
            # Continuity of first derivative at knot i
            b[i] = 2 * (y[i] - c[i-1]) / (x[i] - x[i-1]) - b[i-1]
        
        # Quadratic coefficient
        a[i] = (y[i+1] - c[i] - b[i] * (x[i+1] - x[i])) / ((x[i+1] - x[i]) ** 2)
    
    # Create piecewise function
    def spline_evaluator(t):
        t = np.asarray(t)
        result = np.zeros_like(t)
        
        # Handle points below first x
        mask = t < x[0]
        result[mask] = y[0]
        
        # Handle points between segments
        for i in range(n):
            mask = (t >= x[i]) & (t <= x[i+1])
            dx = t[mask] - x[i]
            result[mask] = a[i] * dx**2 + b[i] * dx + c[i]
        
        # Handle points above last x
        mask = t > x[-1]
        result[mask] = y[-1]
        
        return result
    
    return spline_evaluator

def cubic_tracers(x, y, bc_type='natural'):
    """
    Computes cubic spline interpolation with continuous first and second derivatives.
    
    Parameters:
    x : array_like
        x-coordinates of data points (must be strictly increasing)
    y : array_like
        y-coordinates of data points (same length as x)
    bc_type : str, optional
        Boundary condition type: 'natural' (default), 'clamped', or 'not-a-knot'
        
    Returns:
    function
        A piecewise cubic function that can be evaluated at any point
        
    Raises:
    ValueError: If x and y have different lengths
    ValueError: If x is not strictly increasing
    ValueError: For invalid bc_type
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    if len(x) != len(y):
        return "Not valid Input x and y must have the same length"
    if not np.all(np.diff(x) > 0):
        return "Not valid Input x must be strictly increasing"
    
    n = len(x) - 1
    h = np.diff(x)
    
    # Set up tridiagonal system for second derivatives
    A = np.zeros((n+1, n+1))
    B = np.zeros(n+1)
    
    # Internal points
    for i in range(1, n):
        A[i, i-1] = h[i-1]
        A[i, i] = 2 * (h[i-1] + h[i])
        A[i, i+1] = h[i]
        B[i] = 3 * ((y[i+1] - y[i]) / h[i] - (y[i] - y[i-1]) / h[i-1])
    
    # Boundary conditions
    if bc_type == 'natural':
        A[0, 0] = 1
        A[n, n] = 1
    elif bc_type == 'clamped':
        # Assuming derivative zero at endpoints (can be parameterized later)
        A[0, 0] = 2 * h[0]
        A[0, 1] = h[0]
        B[0] = 3 * ((y[1] - y[0]) / h[0])
        
        A[n, n-1] = h[-1]
        A[n, n] = 2 * h[-1]
        B[n] = 3 * ((y[-1] - y[-2]) / h[-1])
    elif bc_type == 'not-a-knot':
        A[0, 0] = -h[1]
        A[0, 1] = h[0] + h[1]
        A[0, 2] = -h[0]
        
        A[n, n-2] = -h[-1]
        A[n, n-1] = h[-2] + h[-1]
        A[n, n] = -h[-2]
    else:
        return "Not valid Input Invalid bc_type. Choose 'natural', 'clamped', or 'not-a-knot'"
    
    # Solve for second derivatives
    c2 = np.linalg.solve(A, B)
    
    # Calculate other coefficients
    a = np.zeros(n)
    b = np.zeros(n)
    c = np.zeros(n)
    d = np.zeros(n)
    
    for i in range(n):
        d[i] = y[i]
        c[i] = (y[i+1] - y[i]) / h[i] - h[i] * (2*c2[i] + c2[i+1]) / 3
        b[i] = c2[i]
        a[i] = (c2[i+1] - c2[i]) / (3 * h[i])
    
    # Create piecewise function
    def spline_evaluator(t):
        t = np.asarray(t)
        result = np.zeros_like(t)
        
        # Handle points below first x
        mask = t < x[0]
        result[mask] = y[0]
        
        # Handle points between segments
        for i in range(n):
            mask = (t >= x[i]) & (t <= x[i+1])
            dx = t[mask] - x[i]
            result[mask] = a[i]*dx**3 + b[i]*dx**2 + c[i]*dx + d[i]
        
        # Handle points above last x
        mask = t > x[-1]
        result[mask] = y[-1]
        
        return result
    
    return spline_evaluator

def incremental_search():
    """Placeholder for incremental_search Method implementation."""
    pass

def biseccion(f: Callable, a: float, b: float, xtol=0.001, maxiter=100) -> Tuple[float, int]:
    """
    Encuentra una raíz de la función f en el intervalo [a, b] utilizando el método de la bisección.

    :param f: La función cuya raíz se busca.
    :param a: Extremo izquierdo del intervalo.
    :param b: Extremo derecho del intervalo.
    :param xtol: Tolerancia de error en la raíz (diferencia mínima entre a y b).
    :param maxiter: Número máximo de iteraciones permitidas.
    :return: Una tupla que contiene la aproximación de la raíz y el número de iteraciones realizadas.
    :raise ValueError: Si f(a) y f(b) tienen el mismo signo, lo que significa que no hay una raíz en el intervalo.
    :raise Exception: Si se excede el número máximo de iteraciones permitidas.
    """

    if f(b) * f(a) > 0:
        raise ValueError('No existe raíz en el intervalo dado')

    nit = 0
    while nit <= maxiter:
        nit += 1
        c = (a + b) / 2
        if abs(f(c)) <= xtol:
            return c, nit
        elif f(c) * f(a) < 0:
            b = c
        else:
            a = c

    raise Exception("El número máximo de iteraciones permitidas ha sido excedido.")
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

