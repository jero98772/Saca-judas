from sympy.parsing.latex import parse_latex
from sympy import *

#TODO: Este metodo deberia, verificar continuidad, encontrar intervalo adeacuado
def validate_math_function(expr_str: str) -> bool:
    try:
        sympify(expr_str)
        return True
    except SympifyError:
        return False

#Convierte de LaTeX a Sympy, deriva y vuelve a LateX
#No hay soporte para PI, que tontos
def derivateLatex(f: str):   
     
    f = f.replace(r"\pi", "pi")

    #!Experimental Sympy feature
    df = parse_latex(f, backend="lark")
    
    p, i = symbols("p i")
    
    if Symbol('e') in df.free_symbols:
        df = df.subs(Symbol('e'), E)

    if df.has(p*i):
        df = df.subs(p*i, pi)

    x= symbols("x")
    
    dfexpr = diff(df,x)
    
    return latex(dfexpr) 

def latex_to_sympy_str(f: str) -> str:
    """
    Convierte una expresión en LaTeX a un string que sympy pueda volver a procesar.
    Ejemplo: r"e^{-x} + \sin{x}" -> "exp(-x) + sin(x)"
    """
    # Normalizar símbolos especiales
    f = f.replace(r"\pi", "pi")

    # Parsear con Sympy
    expr = parse_latex(f, backend="lark")

    # Normalizar constante e -> E
    if Symbol('e') in expr.free_symbols:
        expr = expr.subs(Symbol('e'), E)

    # Normalizar producto pi (p*i) en caso raro
    p, i = symbols("p i")
    if expr.has(p*i):
        expr = expr.subs(p*i, pi)

    # Retornar en formato str legible por sympy
    return str(expr)

