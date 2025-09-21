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


def derivatePythonExpr(f):
    x = symbols("x")
    return str(diff(f,x))


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

def latex_to_callable_function(latex_str):

    # Convert LaTeX to sympy string (assuming you have this function)
    sympy_str = latex_to_sympy_str(latex_str)
    print(f"Converted to sympy string: {sympy_str}")
    
    # Create sympy symbol
    x = Symbol('x')
    
    # Parse the string into a sympy expression
    expr = sympify(sympy_str)
    print(f"Sympy expression: {expr}")
    
    # Convert to callable function using lambdify
    # Using 'numpy' module for better numerical performance
    func = lambdify(x, expr, modules=['numpy', 'math'])
    
    # Test the function with a simple value to ensure it works
    try:
        test_result = func(1.0)
        print(f"Function test at x=1.0: {test_result}")
    except Exception as test_error:
        print(f"Function test failed: {test_error}")
        # Fallback to basic math module
        func = lambdify(x, expr, modules=['math'])
        test_result = func(1.0)
        print(f"Function test with math module at x=1.0: {test_result}")
    
    return func


def latex_to_callable_function(latex_str):

    # Skip LaTeX conversion for Python expressions
    if not any(latex_char in latex_str for latex_char in ['\\', '{', '}', '^']):
        # It's likely a Python expression, use it directly
        sympy_str = latex_str
    else:
        f = f.replace(r"\pi", "pi")
        
        # Try antlr backend first (more robust)
        expr = parse_latex(f, backend="antlr")
        
        # Check if it's actually a SymPy expression before accessing free_symbols
        if hasattr(expr, 'free_symbols'):
            # Normalizar constante e -> E
            if Symbol('e') in expr.free_symbols:
                expr = expr.subs(Symbol('e'), E)
            
            # Normalizar producto pi (p*i) en caso raro
            p, i = symbols("p i")
            if expr.has(p*i):
                expr = expr.subs(p*i, pi)
        
        sympy_str = str(expr)

    
    print(f"Using sympy string: {sympy_str}")
    
    x = Symbol('x')
    expr = sympify(sympy_str)
    func = lambdify(x, expr, modules=['numpy', 'math'])
    
    return func