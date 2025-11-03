from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

import html as html_lib
import pandas as pd
import numpy as np
from typing import Dict, Callable

from tools.tools import get_function_names 
from tools.sympyUtilities import validate_math_function, derivateLatex, latex_to_sympy_str, latex_to_callable_function, derivatePythonExpr
from tools.numeric_methods import *
from tools.llm_tools import chat_answer


#Ecuaciones no lineales
from tools.methods.newton import newton_method_controller
from tools.methods.modified_newton import newton_multiple_controller
from tools.methods.bisection import bisection_controller
from tools.methods.secant import secant_method_controller
from tools.methods.false_position import false_position_controller
from tools.methods.incremental_search import incremental_search
from tools.methods.fixed_point import run_fixed_point_web

#Sistemas de ecuaciones lineales
from tools.methods.gaussian_elimination_simple import gauss_simple
from tools.methods.gaussian_elimination_with_pivot_partial import gauss_partial
from tools.methods.gaussian_elimination_with_pivot_total import gauss_total
from tools.methods.lu_simple import lu_simple
from tools.methods.lu_partial import lu_partial
from tools.methods.crout import crout
from tools.methods.doolittle import doolittle
from tools.methods.jacobi import jacobi
from tools.methods.gauss_seidel import gauss_seidel
from tools.methods.cholesky import cholesky
from tools.methods.SOR import sor

from typing import Optional

# from tools.java_methods.java_utils import start_jvm, shutdown_jvm
# from tools.java_methods.muller.Muller import muller_controller


import json


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/options", response_class=HTMLResponse)
async def options(request: Request):
    function_names = get_function_names("tools/methods")
    print(function_names)
    return templates.TemplateResponse("options.html", {"request": request,"function_names": function_names})


@app.get("/calculations/{method_name}", response_class=HTMLResponse)
async def method_page(request: Request, method_name: str):
    try:
        methodPage = templates.TemplateResponse(f"methods/{method_name}.html", {"request": request, "method_name": method_name})
    except Exception as e:
        return templates.TemplateResponse("404.html", {"request": request, "message": "Método no encontrado"}, status_code=404)
    return methodPage


@app.post("/calculations/derivate", response_class=HTMLResponse)
async def newton_method_post(request: Request, function: str = Form(...)):
    answer = derivatePythonExpr(function)    
    return JSONResponse(content={"result": answer})

@app.post("/eval/newton_method", response_class=HTMLResponse)
async def newton_method_post(request: Request, function: str = Form(...), x0:float = Form(...), Nmax:int= Form(...), tol:float= Form(...), nrows:int = Form(...)):
    answer = newton_method_controller(function=function, x0=x0, Nmax =Nmax, tol=tol, nrows=nrows)
    
    return JSONResponse(content=answer)

@app.post("/eval/modified_newton", response_class=HTMLResponse)
async def newton_method_post(request: Request, function: str = Form(...), df:Optional[str] = Form(None), d2f:Optional[str] = Form(None), x0:float = Form(...), Nmax:int= Form(...), tol:float= Form(...), nrows:int = Form(...)):
    answer = newton_multiple_controller(function=function, x0=x0, Nmax =Nmax, tol=tol, nrows=nrows, df=df, d2f=d2f)
    
    return JSONResponse(content=answer)

@app.post("/eval/bisection", response_class=HTMLResponse)
async def bisection_post(request: Request, function: str = Form(...), a: float = Form(...), b: float = Form(...), nmax: int = Form(...), tolerance: float = Form(...), last_n_rows: int = Form(...)):
    answer = bisection_controller(function=function, a=a, b=b, nmax=nmax, tolerance=tolerance, last_n_rows=last_n_rows)
    print(answer)
    return JSONResponse(content=answer)

@app.post("/eval/muller", response_class=HTMLResponse)
async def muller_post(request: Request, 
                      function: str = Form(...), 
                      p0: float = Form(...), 
                      p1: float = Form(...), 
                      p2: float = Form(...), 
                      nmax: int = Form(...), 
                      tolerance: float = Form(...), 
                      last_n_rows: int = Form(...)):
    answer = muller_controller(function=function, p0=p0, p1=p1, p2=p2, 
                              nmax=nmax, tolerance=tolerance, last_n_rows=last_n_rows)
    print(answer)
    return JSONResponse(content=answer)


@app.post("/eval/gauss_simple", response_class=JSONResponse)
async def gauss_simple_post(request: Request):
    try:
       
        try:
            data = await request.json()
        except Exception:
            return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A")
        b = data.get("b")
        decimals = data.get("decimals", 6)

       
        if A is None or b is None:
            return JSONResponse(content={"error": "Parameters 'A' and 'b' are required."}, status_code=400)

        if not (isinstance(A, list) and all(isinstance(row, list) for row in A) and A):
            return JSONResponse(content={"error": "Matrix 'A' must be a non-empty list of lists."}, status_code=400)
        if not (isinstance(b, list) and b):
            return JSONResponse(content={"error": "Vector 'b' must be a non-empty list."}, status_code=400)

        
        cols = len(A[0])
        if not all(len(row) == cols for row in A):
            return JSONResponse(content={"error": "All rows in 'A' must have the same length."}, status_code=400)

       
        def is_number(x):
            try:
                float(x)
                return True
            except (TypeError, ValueError):
                return False

        for i, row in enumerate(A):
            for j, val in enumerate(row):
                if not is_number(val):
                    return JSONResponse(
                        content={"error": f"Non-numeric value at A[{i+1}][{j+1}] → {repr(val)}"},
                        status_code=400
                    )
        for i, val in enumerate(b):
            if not is_number(val):
                return JSONResponse(
                    content={"error": f"Non-numeric value at b[{i+1}] → {repr(val)}"},
                    status_code=400
                )

   
        try:
            decimals = int(decimals)
            if not (0 <= decimals <= 10):
                raise ValueError
        except (TypeError, ValueError):
            return JSONResponse(
                content={"error": "Parameter 'decimals' must be an integer between 0 and 10."},
                status_code=400
            )

        
        result = gauss_simple(A, b, decimals)

       
        for log in result["logs"]:
            if "matrix" in log and isinstance(log["matrix"], pd.DataFrame):
           
                float_fmt = f"%.{decimals}f"
                log["matrix"] = log["matrix"].to_html(
                    index=False,
                    classes="gauss-table",
                    border=0,
                    float_format=float_fmt
                )

        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)

    
@app.post("/eval/incremental_search")
async def incremental_search_post(request: Request, function: str = Form(...), x0: float = Form(...), delta_x: float = Form(...),max_iter: int = Form(...),nrows: int = Form(...)):
        print(function,type(function),x0,type(x0),delta_x,type(delta_x),max_iter,type(max_iter))
        f = latex_to_callable_function(function)

        print(f)
        answer = incremental_search(f=f, x0=x0, delta_x=delta_x, max_iter=max_iter)
        print(f"Answer: {answer}")
        
        return JSONResponse(content=answer)

@app.post("/eval/false_position", response_class=HTMLResponse)
async def false_position_post(
    request: Request,
    function: str = Form(...),
    a: float = Form(...),
    b: float = Form(...),
    nmax: int = Form(...),
    tolerance: float = Form(...),
    last_n_rows: int = Form(...)
):
    answer = false_position_controller(
        function=function,
        a=a,
        b=b,
        nmax=nmax,
        tolerance=tolerance,
        last_n_rows=last_n_rows
    )
    print(answer)

    return JSONResponse(content=answer)


@app.post("/eval/fixed_point", response_class=HTMLResponse)
async def eval_fixed_point(
    request: Request,
    g: str = Form(""),
    f: str = Form(""),
    x0: float = Form(...),
    tol: float = Form(1e-6),
    max_iter: int = Form(100),
    use_relative_error: str = Form(None),
):
    result = run_fixed_point_web(
        g_text=g, f_text=f, x0=x0, tol=tol, max_iter=max_iter,
        use_relative_error=bool(use_relative_error)
    )
    return templates.TemplateResponse(
        "methods/fixed_point.html",
        {"request": request,
         "form": {"g": g, "f": f, "x0": x0, "tol": tol, "max_iter": max_iter,
                  "use_relative_error": bool(use_relative_error)},
         "result": result}
    )


@app.post("/eval/secant", response_class=HTMLResponse)
async def secant_method_post(
    request: Request,
    function: str = Form(...),
    x0: float = Form(...),
    x1: float = Form(...),
    Nmax: int = Form(...),
    tol: float = Form(...),
    nrows: int = Form(...)
):
    answer = secant_method_controller(
        function=function,
        x0=x0,
        x1=x1,  
        Nmax=Nmax,
        tol=tol,
        nrows=nrows
    )
    return JSONResponse(content=answer)


@app.post("/eval/muller")
async def muller_post(
    request: Request, 
    function: str = Form(...), 
    p0: float = Form(...), 
    p1: float = Form(...), 
    p2: float = Form(...),
    max_iter: int = Form(...),
    nrows: int = Form(...),
    tolerance: float = Form(1e-6)
):
    """
    FastAPI endpoint for Muller's method
    
    Parameters:
    - function: String representation of the function (e.g., "x^3-x^2-x-1")
    - p0: First initial approximation for the root
    - p1: Second initial approximation for the root  
    - p2: Third initial approximation for the root
    - max_iter: Maximum number of iterations
    - nrows: Number of final rows to return
    - tolerance: Convergence tolerance (default: 1e-6)
    """
    
    print(f"Function: {function}, type: {type(function)}")
    print(f"p0: {p0}, type: {type(p0)}")
    print(f"p1: {p1}, type: {type(p1)}")
    print(f"p2: {p2}, type: {type(p2)}")
    print(f"max_iter: {max_iter}, type: {type(max_iter)}")
    print(f"nrows: {nrows}, type: {type(nrows)}")
    print(f"tolerance: {tolerance}, type: {type(tolerance)}")
    
    try:
        # Call Muller's method
        answer = muller_controller(
            function=function,
            p0=p0,
            p1=p1, 
            p2=p2,
            nmax=max_iter,
            last_n_rows=nrows,
            tolerance=tolerance
        )
        
        print(f"Answer: {answer}")
        
        return JSONResponse(content=answer)
        
    except Exception as e:
        error_response = {
            "iterations": [],
            "roots": [],
            "errors": [],
            "final_root": "Error",
            "message": f"Server error: {str(e)}"
        }
        return JSONResponse(content=error_response, status_code=500)
        

@app.get("/chat", response_class=HTMLResponse)
async def chat_recive(request: Request):
    function_names = get_function_names("tools/numeric_methods.py")
    print(function_names)
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "function_names": function_names}
    )

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    full_response = await client.process_query(messages)
    return {"response": full_response}

@app.exception_handler(404)
async def not_found(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

# @app.on_event("startup")
# async def startup_event():
#     """Initialize JVM when FastAPI starts"""
    
#     start_jvm()

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Shutdown JVM when FastAPI stops"""
#     if jpype.isJVMStarted():
#         jpype.shutdownJVM()
#         print("JVM shutdown successfully")