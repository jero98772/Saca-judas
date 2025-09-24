import math

def incremental_search(f, x0, delta_x, max_iter=100, tolerance=1e-6):
    """
    Encuentra TODOS los intervalos con raíces usando búsqueda incremental.
    Busca intervalos [a, b] donde f(a) y f(b) tienen signos opuestos.
    
    Parameters:
        f: Función a evaluar.
        x0: Punto inicial.
        delta_x: Paso de búsqueda.
        max_iter: Número máximo de iteraciones (n_iteraciones).
        tolerance: Tolerancia de convergencia (no usado en esta versión).
    
    Returns:
        Diccionario con mensaje, todos los intervalos encontrados e historial.
    """
    a = x0
    b = x0 + delta_x
    iter_count = 0
    search_history = []
    intervals_found = []
    
    # Buscar durante exactamente max_iter iteraciones
    while iter_count < max_iter:
        fa = f(a)
        fb = f(b)
        search_history.append([a, b, fa, fb])
        
        # Si hay cambio de signo, guardar el intervalo
        if fa * fb < 0:
            intervals_found.append([a, b])
        
        # Avanzar al siguiente punto
        a = b
        b = a + delta_x
        iter_count += 1
    
    # Crear mensaje basado en los intervalos encontrados
    if intervals_found:
        interval_strings = [f"[{interval[0]:.6f}, {interval[1]:.6f}]" for interval in intervals_found]
        message = f"Se encontraron {len(intervals_found)} intervalo(s): " + ", ".join(interval_strings)
    else:
        message = f"No se encontraron intervalos con cambio de signo en {max_iter} iteraciones"
    
    return {
        "message": message,
        "intervals": intervals_found,  # Lista de todos los intervalos
        "interval": intervals_found[0] if intervals_found else None,  # Primer intervalo para compatibilidad
        "history": {
            "search_points": search_history,
            "iterations": iter_count,
            "total_intervals": len(intervals_found)
        }
    }