#En este archivo intento programar el método de la raíz cúbica iterativa y 
#la serie de Taylor, con el objetivo de utilizarlo para el parcial.
from sympy import *

#! Raíz iterativa - método de Newton
def root (a:int, x0:int, p:int, ultimasFilas:int):
    
    errorAbs = 1000
    xAnterior = x0
    iteraciones = 0

    # Listas para almacenar los últimos n valores (hint implementado)
    historial_errorAbs = []
    historial_x = []
    historial_iteraciones = []

    while(True):

        #Cálculo de Xn+1
        x = (2*pow(xAnterior,3)+a)/(3*pow(xAnterior,2))

        #Cálculo de los errores absolutos
        errorAbs = abs(x - xAnterior)
        
        # Agregar valores al historial y mantener solo los últimos n valores
        historial_x.append(x)
        historial_errorAbs.append(errorAbs)
        historial_iteraciones.append(iteraciones)
        
        if len(historial_x) > ultimasFilas:
            historial_x.pop(0)
            historial_errorAbs.pop(0)
            historial_iteraciones.pop(0)
        
        # Condición de precisión corregida (era >= pero debe ser <)
        if(errorAbs < 0.5*pow(10, -p)):
            return {
                "message": "Se alcanzó la cantidad de decimales correctos",
                "value": x,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }

        #valor encontrado
        xAnterior = x 
        if(pow(x,3) == a):
            return {
                "message": "Valor de a^(1/3) encontrado",
                "value": x,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }
        

        #iteraciones máximas
        iteraciones += 1
        if(iteraciones > 10000):
            return {
                "message": "Máxima cantidad de iteraciones superadas",
                "value": x,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }

        print(x, " Error Absoluto: ", errorAbs)


    return x

#! Metodo de la Serie de Taylor

#TODO: Implementar el criterio de la inversa y intentar reducir el numero de operaciones, desde el codigo y desde la forma Horner

def methodTaylorSeries(funcExpr:str, center:int , x_value:int ,p:int, ultimasFilas:int):
    #Convierte un String en una expresion sympy

    x_symbol, y = symbols("x y")

    expr = sympify(funcExpr)

    iteraciones = 0
    errorAbs = 10000
    xAnterior = 0

    # Listas para almacenar los últimos n valores (hint implementado)
    historial_errorAbs = []
    historial_x = []
    historial_iteraciones = []

    while(True):

        expressionResult = expr.evalf(subs={x_symbol:center})

        constantFunction = pow((x_value - center), iteraciones) / factorial(iteraciones)

        x = xAnterior + (expressionResult * constantFunction)
        
        #Cálculo de los errores absolutos
        if iteraciones != 0:
            errorAbs = abs(x - historial_x[-1])
        
        # Agregar valores al historial y mantener solo los últimos n valores
        historial_errorAbs.append(errorAbs)
        historial_x.append(x)
        historial_iteraciones.append(iteraciones)
        
        if len(historial_x) > ultimasFilas:
            historial_x.pop(0)
            historial_errorAbs.pop(0)
            historial_iteraciones.pop(0)
        
        #El Error tolerable por el usuario es alcanzado
        if(errorAbs < 0.5*pow(10, -p)):
            return {
                "message": "Se alcanzó la cantidad de decimales correctos",
                "value": x,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }

        #valor encontrado
        # Evaluar la inversa de expr en x, y si da x_value es TRUE
        #TODO: Implementar la busqueda de una inversa adecuada para el dominio donde trabajara el metodo.
        # ecuacion = Eq(y, expr)

        # inversa = solve(ecuacion, x_symbol)

        # print(inversa)


        #iteraciones máximas
        iteraciones += 1
        if(iteraciones > 10000):
            return {
                "message": "Máxima cantidad de iteraciones superadas",
                "value": x,
                "historial": {
                    "x": historial_x,
                    "errorAbs": historial_errorAbs,
                    "iteraciones": historial_iteraciones
                }
            }

        xAnterior = x

        expr = diff(expr, x_symbol)

#ejemplo del video
resultado = methodTaylorSeries("1/(1 + x)", 0, -0.5, 4, 15)


# Imprimir los resultados en formato de tabla
print(f"{'Iteración':>10} | {'x':>20} | {'Error Absoluto':>20}")
print("-" * 60)
for i, (x, error, it) in enumerate(zip(resultado["historial"]["x"], resultado["historial"]["errorAbs"], resultado["historial"]["iteraciones"])):
    print(f"{it:10} | {x:>20} | {error:>20}")
