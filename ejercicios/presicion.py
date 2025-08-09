#En este archivo intento, programar el metodo de la reiz cubica iterativa y 
#la serie de taylor, con el objetivo de utilizarlo para el parcia.

#! Raiz iterativa - metodo de newton
def root (a:int, x0:int, p:int, ultimasFilas:int):
    
    errorAbs = 1000
    xAnterior = x0
    iteraciones = 0

    #TODO: Ciclo que se detenga cuando por precision alcansada, iteraciones maximas o valor encontrado
    while(True):

        #Calculo de Xn+1
        x = (2*pow(xAnterior,3)+a)/(3*pow(xAnterior,2))

        #Calculo de los errores absolutos
        #TODO: Preguntar la cantidad de ultimos errores que se desean guardar(Final de la tabla)
        errorAbs = abs(x - xAnterior)
        if(errorAbs >= 0.5*pow(10, -p)):
            return {
                "message": "Se alcanso la cantidad de decimales correctos",
                "value": x,
            }

        #valor encontrado
        xAnterior = x 
        if(pow(x,3) == a):
            return {
                "message": "Valor de a^(1/3) econtrado",
                "value": x,
            }
        

        #iteraciones maximas
        iteraciones += 1
        if(iteraciones > 10000):
            return {
                "message": "Maxima cantidad de iteraciones superadas",
                "value": x,
            }

        print(x, " Error Absoluto: ", errorAbs)


    return x

root(1398, 11, 14)


        




