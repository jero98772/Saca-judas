import numpy as np
import sympy as sp

def lagrange_interpolation(x_points, y_points):
    """
    Construye el polinomio de interpolación de Lagrange simbólicamente
    y devuelve su expresión en formato string de alta precisión.

    Parámetros:
    ------------
    x_points : list[float]
        Lista de coordenadas x de los puntos conocidos.
    y_points : list[float]
        Lista de coordenadas y de los puntos conocidos.

    Retorna:
    ---------
    dict :
        {
            "message": str,
            "polynomial": str,   # Expresión simbólica de P(x)
            "historial": dict    # Estructura informativa
        }
    """
    try:
        x_points = np.array(x_points, dtype=float)
        y_points = np.array(y_points, dtype=float)
        n = len(x_points)

        # Validaciones
        if n != len(y_points):
            return {
                "message": "Error: x_points y y_points deben tener la misma longitud",
                "polynomial": None,
                "historial": {
                    "x": [],
                    "errorAbs": [],
                    "iteraciones": []
                }
            }

        x = sp.Symbol('x')
        P = 0

        # Construir el polinomio de Lagrange simbólicamente
        for i in range(n):
            Li = 1
            for j in range(n):
                if i != j:
                    Li *= (x - sp.Float(x_points[j], 15)) / (sp.Float(x_points[i], 15) - sp.Float(x_points[j], 15))
            P += sp.Float(y_points[i], 15) * Li

        # Expandir para tener la forma polinómica completa
        P_simplified = sp.expand(P)

        # Convertir el polinomio a string con precisión completa
        polynomial_str = sp.srepr(P_simplified)  # Representación estructurada (opcional)
        polynomial_str = sp.ccode(P_simplified)  # C-like expression con alta precisión
        # Alternativa más directa:
        # polynomial_str = str(P_simplified)

        historial = {
            "x": x_points.tolist(),
            "errorAbs": [0] * n,
            "iteraciones": [1]
        }

        return {
            "message": "Polinomio de Lagrange generado exitosamente",
            "polynomial": str(P_simplified),
            "historial": historial
        }

    except Exception as e:
        return {
            "message": f"Error durante la generación del polinomio: {str(e)}",
            "polynomial": None,
            "historial": {
                "x": [],
                "errorAbs": [],
                "iteraciones": []
            }
        }

x = [1,2,3]
y = [1,8,27]

print(lagrange_interpolation(x,y))