from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from tools.tools import get_function_names 
from tools.sympyUtilities import validate_math_function, derivateLatex, latex_to_sympy_str, latex_to_callable_function, derivatePythonExpr
from tools.numeric_methods import *
from tools.llm_tools import chat_answer

from tools.methods.newton import newton_method_controller
from tools.methods.newton import bisection_controller
from tools.methods.secant import secant_method_controller
from tools.methods.incremental_search import incremental_search
from tools.methods.fixed_point import run_fixed_point_web
from tools.methods.gaussian_elimination_with_pivot_total import run_gauss_pivote_web

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
        
    print(function)
        
    answer = derivatePythonExpr(function)    
    
    print(answer)

    return JSONResponse(content={"result": answer})

@app.post("/eval/newton_method", response_class=HTMLResponse)
async def newton_method_post(request: Request, function: str = Form(...), x0:float = Form(...), Nmax:int= Form(...), tol:float= Form(...), nrows:int = Form(...)):
    answer = newton_method_controller(function=function, x0=x0, Nmax =Nmax, tol=tol, nrows=nrows)
    print(answer)
    
    return JSONResponse(content=answer)

@app.post("/eval/bisection", response_class=HTMLResponse)
async def bisection_post(request: Request, function: str = Form(...), a: float = Form(...), b: float = Form(...), nmax: int = Form(...), tolerance: float = Form(...), last_n_rows: int = Form(...)):

    answer = bisection_controller(function=function, a=a, b=b, nmax=nmax, tolerance=tolerance, last_n_rows=last_n_rows)
    print(answer)


    return JSONResponse(content=answer)



@app.get("/methods/punto-fijo", response_class=HTMLResponse)
def get_punto_fijo(request: Request):
    return templates.TemplateResponse("methods/fixed_point.html", {"request": request, "form": {}, "result": None})

@app.post("/methods/punto-fijo", response_class=HTMLResponse)
def post_punto_fijo(request: Request, g: str = Form(""), f: str = Form(""),
                    x0: float = Form(...), tol: float = Form(1e-6),
                    max_iter: int = Form(100), use_relative_error: str = Form(None)):
    result = run_fixed_point_web(g_text=g, f_text=f, x0=x0, tol=tol, max_iter=max_iter,
                                 use_relative_error=bool(use_relative_error))
    return templates.TemplateResponse("methods/fixed_point.html",
            {"request": request, "form": {"g": g, "f": f, "x0": x0, "tol": tol, "max_iter": max_iter,
                                          "use_relative_error": bool(use_relative_error)},
             "result": result})

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

@app.get("/calculations/fixed_point", response_class=HTMLResponse)
async def fixed_point_page(request: Request):
    # Ruta explícita: evita el f-string y cualquier error en el try/except dinámico
    return templates.TemplateResponse(
        "methods/fixed_point.html",
        {"request": request, "method_name": "fixed_point", "form": {}, "result": None}
    )
#ajuste
@app.get("/calculations/gauss_pivote", response_class=HTMLResponse)
async def gauss_pivote_get(request: Request):
    return templates.TemplateResponse(
        "methods/gaussian_elimination_with_pivot_total.html",  
        {"request": request, "form": {}, "result": None}
    )

@app.post("/eval/gauss_pivote", response_class=HTMLResponse)
async def gauss_pivote_eval(request: Request, matrix: str = Form(...)):
    result = run_gauss_pivote_web(matrix)
    return templates.TemplateResponse(
        "methods/gaussian_elimination_with_pivot_total.html",  
        {"request": request, "form": {"matrix": matrix}, "result": result}
    )
#------------------------------------------------------------------------------------
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


@app.post("/eval/incremental_search")
async def incremental_search_post(request: Request, function: str = Form(...), x0: float = Form(...), delta_x: float = Form(...),max_iter: int = Form(...),tolerance: float = Form(...),nrows: int = Form(...)):
        
        print(function,type(function),x0,type(x0),delta_x,type(delta_x),max_iter,type(max_iter),tolerance,type(tolerance))
        #f = latex_to_sympy_str(function)
        f = latex_to_callable_function(function)

        print(f)
        answer = incremental_search(f=f, x0=x0, delta_x=delta_x, max_iter=max_iter, tolerance=tolerance)
        """
        if answer.get("history"):
            history = answer["history"]
            if len(history.get("x", [])) > nrows:
                start_idx = len(history["x"]) - nrows
                answer["history"] = {
                    "x": history["x"][start_idx:],
                    "errorAbs": history["errorAbs"][start_idx:],
                    "iterations": history["iterations"][start_idx:]
                }
        """
        print(f"Answer: {answer}")
        
        return JSONResponse(content=answer)
        


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
