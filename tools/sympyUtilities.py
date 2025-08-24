from sympy import sympify, SympifyError

#TODO: Este metodo deberia, verificar continuidad, encontrar intervalo adeacuado
def validate_math_function(expr_str: str) -> bool:
    try:
        sympify(expr_str)
        return True
    except SympifyError:
        return False

