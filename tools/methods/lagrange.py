import numpy as np

def lagrange_interpolation(x_points, y_points, x):
    """
    Lagrange interpolation polynomial with JSON-compatible output.
    
    Parameters:
    x_points: array of x coordinates of data points
    y_points: array of y coordinates of data points
    x: point(s) to evaluate interpolation at
    
    Returns:
    dict: JSON-compatible result with message, value (interpolated value), and historial
    """
    try:
        x_points = np.array(x_points)
        y_points = np.array(y_points)
        n = len(x_points)
        
        # Check if inputs are valid
        if len(x_points) != len(y_points):
            return {
                "message": "Error: x_points and y_points must have the same length",
                "value": None,
                "historial": {
                    "x": [],
                    "errorAbs": [],
                    "iteraciones": []
                }
            }
        
        # For direct methods, we don't have iteration history like iterative methods
        # So we'll create a simplified historial structure
        historial = {
            "x": x_points.tolist(),  # The input x points
            "errorAbs": [0] * n,  # No error in interpolation at known points
            "iteraciones": [1]  # Just one "iteration" for direct method
        }
        
        if np.isscalar(x):
            result = 0.0
            for i in range(n):
                # Calculate Lagrange basis polynomial Li(x)
                Li = 1.0
                for j in range(n):
                    if i != j:
                        Li *= (x - x_points[j]) / (x_points[i] - x_points[j])
                result += y_points[i] * Li
            
            return {
                "message": "Interpolación exitosa",
                "value": result,
                "historial": historial
            }
        else:
            x = np.array(x)
            result = np.zeros_like(x)
            for i in range(n):
                Li = np.ones_like(x)
                for j in range(n):
                    if i != j:
                        Li *= (x - x_points[j]) / (x_points[i] - x_points[j])
                result += y_points[i] * Li
            
            return {
                "message": "Interpolación exitosa",
                "value": result.tolist(),
                "historial": historial
            }
    
    except Exception as e:
        return {
            "message": f"Error durante la interpolación: {str(e)}",
            "value": None,
            "historial": {
                "x": [],
                "errorAbs": [],
                "iteraciones": []
            }
        }