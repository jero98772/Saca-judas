import jpype
import json
import os
import sys

def start_jvm():
    """Initialize JVM with the current directory in classpath"""
    if not jpype.isJVMStarted():
        # Get the current directory where the Java file should be compiled
        current_dir = os.getcwd()
        
        try:
            # Start JVM with current directory in classpath
            jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[current_dir])
            print("JVM started successfully")
        except Exception as e:
            print(f"Error starting JVM: {e}")
            raise RuntimeError(f"Error starting JVM: {e}")

def muller_method(function: str, p0: float, p1: float, p2: float, nmax: int, last_n_rows: int, tolerance: float):
    """
    Python interface for Muller's method implemented in Java
    
    Parameters:
    - function: String representation of the function (e.g., "x^3-x^2-x-1")
    - p0, p1, p2: Three initial approximations for the root
    - nmax: Maximum number of iterations
    - last_n_rows: Number of final rows to return
    - tolerance: Convergence tolerance
    
    Returns:
    - Dictionary with iterations, roots, errors, final_root, and message
    """
    
    # Start JVM if not already started
    start_jvm()
    
    try:
        # Get the Java class
        MullerClass = jpype.JClass("Muller")
        
        # Call Java method which returns JSON string
        json_result = MullerClass.mullerController(function, float(p0), float(p1), float(p2), 
                                                  int(nmax), int(last_n_rows), float(tolerance))
        
        # Parse JSON string to Python dictionary
        python_result = json.loads(str(json_result))
        
        return python_result
        
    except Exception as e:
        print(f"Error calling Java method: {e}")
        return {
            "iterations": [],
            "roots": [],
            "errors": [],
            "final_root": "Error",
            "message": f"Error: {str(e)}"
        }

def muller_controller(function: str, p0: float, p1: float, p2: float, nmax: int, last_n_rows: int, tolerance: float):
    """Controller function to match the bisection pattern"""
    return muller_method(function, p0, p1, p2, nmax, last_n_rows, tolerance)

def shutdown_jvm():
    """Shutdown JVM when done"""
    if jpype.isJVMStarted():
        jpype.shutdownJVM()
        print("JVM shutdown successfully")
"""
# Example usage
if __name__ == "__main__":
    print("=== Muller's Method Example ===")
    
    # Test with f(x) = x³ - x² - x - 1
    # Expected root ≈ 1.839
    function = "x^3-x^2-x-1"
    p0, p1, p2 = 0.0, 1.0, 2.0
    nmax = 50
    last_n_rows = 5
    tolerance = 1e-6
    
    print(f"\nFinding root of f(x) = {function}")
    print(f"Initial points: p0={p0}, p1={p1}, p2={p2}")
    print(f"Max iterations: {nmax}")
    print(f"Tolerance: {tolerance}")
    
    # Call Muller's method
    result = muller_controller(function, p0, p1, p2, nmax, last_n_rows, tolerance)
    
    print("\n=== Results (JSON Format) ===")
    print(json.dumps(result, indent=2))
    
    # Test with another function: x² - 2 (should find ±√2 ≈ ±1.414)
    print("\n" + "="*50)
    print("=== Second Example: f(x) = x² - 2 ===")
    
    function2 = "x^2-2"
    p0, p1, p2 = 0.0, 1.0, 2.0
    
    result2 = muller_controller(function2, p0, p1, p2, nmax, last_n_rows, tolerance)
    
    print(f"\nFinding root of f(x) = {function2}")
    print("=== Results (JSON Format) ===")
    print(json.dumps(result2, indent=2))
    
    # Shutdown JVM
    shutdown_jvm()
"""