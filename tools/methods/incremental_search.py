import math

def incremental_search(f, x0, delta_x, max_iter=100, tolerance=1e-6):

    a = x0
    b = x0 + delta_x
    iter_count = 0
    search_history = []
    intervals_found = []
    

    while iter_count < max_iter:
        fa = f(a)
        fb = f(b)
        search_history.append([a, b, fa, fb])
        

        if fa * fb < 0:
            intervals_found.append([a, b])
        
       
        a = b
        b = a + delta_x
        iter_count += 1
    
   
    if intervals_found:
        interval_strings = [f"[{interval[0]:.6f}, {interval[1]:.6f}]" for interval in intervals_found]
        message = f"Se encontraron {len(intervals_found)} intervalo(s): " + ", ".join(interval_strings)
    else:
        message = f"No se encontraron intervalos con cambio de signo en {max_iter} iteraciones"
    
    return {
        "message": message,
        "intervals": intervals_found, 
        "interval": intervals_found[0] if intervals_found else None, 
        "history": {
            "search_points": search_history,
            "iterations": iter_count,
            "total_intervals": len(intervals_found)
        }
    }