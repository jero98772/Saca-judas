import math

def newton_prime(f, df, x0, tolerance=1e-7, max_iter=100):
    """
    Newton's method (Newton-Raphson) for finding roots with JSON-compatible output.
    
    Parameters:
    f: function
    df: derivative of function
    x0: initial guess
    tolerance: convergence tolerance
    max_iter: maximum iterations
    
    Returns:
    dict: JSON-compatible result with message, value, and iteration history
    """
    x = x0
    historial_x = [x0]
    historial_errorAbs = []
    historial_iteraciones = []
    
    for i in range(1, max_iter + 1):
        fx = f(x)
        dfx = df(x)
        
        if abs(dfx) < 1e-12:
            return {
                "message": f"Derivada demasiado pequeña en la iteración {i}",
                "value": None,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        
        x_new = x - fx / dfx
        error_abs = abs(x_new - x)
        
        # Update history
        historial_x.append(x_new)
        historial_errorAbs.append(error_abs)
        historial_iteraciones.append(i)
        
        if error_abs < tolerance:
            return {
                "message": "Tolerancia satisfecha",
                "value": x_new,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        
        x = x_new
    
    # If we reach here, the method didn't converge
    return {
        "message": "Máximo número de iteraciones alcanzado",
        "value": x,
        "historial": {
            "x": historial_x,
            "errorAbs": historial_errorAbs,
            "iteraciones": historial_iteraciones
        }
    }