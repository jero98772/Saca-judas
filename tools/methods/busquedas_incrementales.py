import math

def busquedas_incrementales(f, x0, delta_x, max_iter=100, tolerance=1e-6):
    """
    Encuentra una raíz usando búsqueda incremental para localizar un intervalo,
    y luego aplica el método de bisección para refinar la solución.

    Parameters:
        f: Función a evaluar.
        x0: Punto inicial.
        delta_x: Paso de búsqueda.
        max_iter: Máximo de iteraciones.
        tolerance: Tolerancia para la convergencia.

    Returns:
        Un diccionario con el mensaje, el valor de la raíz y el historial de iteraciones.
    """
    # Búsqueda incremental para encontrar un intervalo [a, b] con cambio de signo
    a = x0
    b = x0 + delta_x
    iter_count_inc = 0
    while iter_count_inc < max_iter:
        if f(a) * f(b) < 0:
            break  # Intervalo válido encontrado
        a = b
        b = a + delta_x
        iter_count_inc += 1
    else:
        return {
            "message": "No se encontró un intervalo válido después de la búsqueda incremental",
            "value": None,
            "historial": {"x": [], "errorAbs": [], "iteraciones": []}
        }

    # Método de bisección en el intervalo [a, b]
    historial_x = []
    historial_errorAbs = []
    historial_iteraciones = []
    iter_count = 0
    error_abs = float('inf')
    c_prev = a

    while error_abs > tolerance and iter_count < max_iter:
        c = (a + b) / 2
        historial_x.append(c)
        error_abs = abs(c - c_prev)
        historial_errorAbs.append(error_abs)
        iter_count += 1
        historial_iteraciones.append(iter_count)

        if f(c) == 0 or error_abs < tolerance:
            return {
                "message": "Tolerancia satisfecha",
                "value": c,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        elif f(a) * f(c) < 0:
            b = c
        else:
            a = c
        c_prev = c

    return {
        "message": "Máximo número de iteraciones alcanzado",
        "value": c,
        "historial": {
            "x": historial_x,
            "errorAbs": historial_errorAbs,
            "iteraciones": historial_iteraciones
        }
    }