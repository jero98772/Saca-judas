from sympy import *

def newton_method(f:str, x0:float, tol:float, Nmax:int, ultimasNfilas:int, df:str= None):
    
    Nmax = int(Nmax)
    x = symbols("x")
    func = lambdify(x, sympify(f), "math")
    if df is None:
        deriv = lambdify(x, diff(sympify(f)), "math")
    else:
        deriv = lambdify(x, sympify(df), "math")
    
    historial_x = []
    historial_iteraciones = []
    historial_errorAbs = []
    
    
    for n in range(Nmax):
        
        try: 
            test = 1/deriv(x0)
        except OverflowError:
            return {
                "message": "f'(x0) is too Big or to small for f(x0)/f'(x0)",
                "value": x0,
                "type":"danger",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        except ZeroDivisionError:
            return {
                "message": "Division by 0 occurred, derivate equal to 0",
                "value": x0,
                "type":"danger",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        
        x1 = x0 - (func(x0)/deriv(x0))
        
        errorAbs = abs(x1 - x0)
    
        
        historial_x.append(x0)
        historial_errorAbs.append(errorAbs)
        historial_iteraciones.append(n)
        
        if len(historial_x) > ultimasNfilas:
            historial_x.pop(0)
            historial_errorAbs.pop(0)
            historial_iteraciones.pop(0)    
        
        if abs(x1 - x0) < tol:
            return {
                "message": "Tolerancia satisfecha",
                "value": x1,
                "type":"success",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }

        if int(n) >= int(Nmax):
            return {
                "message": "Cantidad de iteraciones superadas",
                "value": x1,
                "type":"info",
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        
        
        x0 = x1
    

def newton_method_controller(function: str, x0: float, Nmax: int, tol: float, nrows: int):

    # Llamar al método de Newton
    answer = newton_method(function, x0, tol, Nmax, nrows)

    return answer
