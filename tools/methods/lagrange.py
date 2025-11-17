import numpy as np
import sympy as sp

def lagrange_interpolation_object(x_points, y_points):
    """
    Returns an OBJECT containing:
      - status
      - message
      - symbolic_expression (expanded)
      - polynomial_lagrange  ⟵ NOW an ARRAY of strings (L0, L1, L2…)
      - polynomial_combination (coeff*Li format)
    """

    try:
        x_points = np.array(x_points, dtype=float)
        y_points = np.array(y_points, dtype=float)

        n = len(x_points)
        if n != len(y_points):
            return {
                "status": "danger",
                "message": "x_points and y_points must have the same length.",
                "symbolic_expression": None,
                "polynomial_lagrange": None,
                "polynomial_combination": None
            }

        x = sp.Symbol('x')

        # ---------- Construcción de los L_i ----------
        lagrange_polys = []
        lagrange_poly_strings = []   # <-- ESTO AHORA SERÁ UN ARREGLO

        for i in range(n):
            Li = 1
            for j in range(n):
                if i != j:
                    Li *= (x - sp.Float(x_points[j], 15)) / (sp.Float(x_points[i], 15) - sp.Float(x_points[j], 15))

            Li_expanded = sp.expand(Li)
            lagrange_polys.append(Li_expanded)

            # Convertir Li a string con coeficientes formateados
            poly = sp.Poly(Li_expanded, x)
            coeffs = poly.all_coeffs()
            degree = len(coeffs) - 1

            terms = []
            for idx, c in enumerate(coeffs):
                power = degree - idx
                c = float(c)
                term = f"{c:.6f}"

                if power > 1:
                    term += f"x^{power}"
                elif power == 1:
                    term += "x"

                terms.append(term)

            poly_str = " + ".join(terms)
            lagrange_poly_strings.append(f"{poly_str}   //L{i}")  # <--- ARREGLO DE STRINGS

        # ---------- Combinación tipo y0*L0 + y1*L1 ----------
        combination = []
        for i in range(n):
            yi = float(y_points[i])
            if yi.is_integer():
                yi = int(yi)
            combination.append(f"{yi}*L{i}")

        combination_str = " + ".join(combination)

        # ---------- Polinomio completo expandido ----------
        P = sum(sp.Float(y_points[i], 15) * lagrange_polys[i] for i in range(n))
        symbolic_expression = str(sp.expand(P))

        return {
            "status": "success",
            "message": "Lagrange polynomial computed successfully.",
            "symbolic_expression": symbolic_expression,
            "polynomial_lagrange": lagrange_poly_strings,     # <--- AHORA ES ARREGLO
            "polynomial_combination": f"P(x) = {combination_str}"
        }

    except Exception as e:
        return {
            "status": "danger",
            "message": f"Error while generating Lagrange polynomial: {str(e)}",
            "symbolic_expression": None,
            "polynomial_lagrange": None,
            "polynomial_combination": None
        }
