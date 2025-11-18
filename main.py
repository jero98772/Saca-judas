from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException


import pandas as pd
import numpy as np
from typing import Dict, Callable, Optional
import json

from tools.tools import get_function_names 
from tools.sympyUtilities import (
    latex_to_callable_function, derivatePythonExpr
)


# ===================== Ecuaciones no lineales =====================
from tools.methods.newton import newton_method_controller
from tools.methods.modified_newton import newton_multiple_controller
from tools.methods.bisection import bisection_controller
from tools.methods.secant import secant_method_controller
from tools.methods.false_position import false_position_controller
from tools.methods.incremental_search import incremental_search
from tools.methods.fixed_point import run_fixed_point_web

# ===================== Sistemas de ecuaciones lineales =====================
from tools.methods.gaussian_elimination_simple import gauss_simple
from tools.methods.gaussian_elimination_with_pivot_partial import gauss_partial
from tools.methods.gaussian_elimination_with_pivot_total import gauss_total

from tools.methods.crout import crout
from tools.methods.doolittle import doolittle
from tools.methods.gauss_seidel import gauss_seidel
from tools.methods.SOR import sor

# ===== Nuevas funciones compute_* que retornan dict (para los endpoints /eval) =====
from tools.methods.lu_partial import compute_gauss_pivote_parcial
from tools.methods.lu_simple import compute_lu_simple
from tools.methods.vandermonde import compute_vandermonde
from tools.methods.lineal_tracers import compute_trazadores_lineales
from tools.methods.cholesky import compute_cholesky
from tools.methods.jacobi import compute_jacobi
from tools.methods.newton_interpolation import newton_interpolant_object 
from tools.methods.lagrange import lagrange_interpolation_object 


#Trazadores
from tools.methods.cubic_tracers import cubic_spline_method, save_cubic_tracer

METHOD_CATEGORIES = {
    'Solution_of_Nonlinear_Equations': [
        'newton', 'modified_newton', 'bisection', 'secant',
        'false_position', 'incremental_search', 'fixed_point'
    ],
    'Solution_of_linear_system_equations': [
        'gaussian_elimination_simple', 'gaussian_elimination_with_pivot_partial',
        'gaussian_elimination_with_pivot_total', 'lu_simple', 'lu_partial','crout',
        'doolittle', 'gauss_seidel', 'SOR', 'cholesky', 'jacobi'
    ],
    'Interpolation': [
        'vandermonde', 'lineal_tracers', 'newton_interpolation',
        'lagrange', 'cubic_tracers', 'cuadratic_tracers'
    ]
}

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#Funciones auxiliares (Por favor no lo toquen que todo expltota)
# ============================================================
# FUNCIONES AUXILIARES PARA EL ENDPOINT gauss_simple_post
# ============================================================

import numpy as np
import pandas as pd
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def to_float_safe(x):
    if x is None:
        return None
    if isinstance(x, (int, float, np.floating, np.integer)):
        return float(x)
    s = str(x).strip()
    if s == "":
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def df_to_html(df: pd.DataFrame, decimals: int = 6):
    float_fmt = f"%.{decimals}f"
    # redondea para evitar representaciones largas y utiliza float_format
    return df.round(decimals).to_html(index=False, classes="gauss-table", border=0, float_format=float_fmt)

def df_to_json(df: pd.DataFrame):
    return {"columns": list(df.columns.astype(str)), "rows": df.values.tolist()}

def serialize_value(val, decimals: int = 6):
    """
    Serializa DataFrame/Series/ndarray a {'html','json'} o lista/primitivo.
    Si no es ninguno de esos, devuelve tal cual (serializable).
    """
    if isinstance(val, pd.DataFrame):
        return {"html": df_to_html(val, decimals), "json": df_to_json(val)}
    if isinstance(val, pd.Series):
        df = val.to_frame(name=val.name if val.name else "value")
        return {"html": df_to_html(df, decimals), "json": df_to_json(df)}
    if isinstance(val, np.ndarray):
        return val.tolist()
    # para tipos simples (list, dict, str, int, float) devolvemos tal cual
    return val

def combine_A_b(log: dict, decimals: int = 6):
    """
    Si no existe `matrix` en el log, intenta construirla a partir de A_json y b_json.
    No sobrescribe si ya existe `matrix` (HTML string).
    """
    # Si ya existe matrix en forma HTML o JSON, no tocar
    if "matrix" in log or "matrix_html" in log or "matrix_json" in log:
        return

    try:
        Ajson = log.get("A_json")
        bjson = log.get("b_json")

        if Ajson and bjson:
            colsA = Ajson.get("columns", [])
            rowsA = Ajson.get("rows", [])
            rowsB = bjson.get("rows", [])

            combined_cols = colsA + ["b"]
            combined_rows = []
            max_r = max(len(rowsA), len(rowsB))
            for i in range(max_r):
                rowA = rowsA[i] if i < len(rowsA) else [None] * len(colsA)
                rowB = rowsB[i] if i < len(rowsB) else [None]
                combined_rows.append(rowA + [rowB[0] if rowB else None])

            df_comb = pd.DataFrame(combined_rows, columns=combined_cols)
            log["matrix_json"] = {"columns": combined_cols, "rows": combined_rows}
            log["matrix"] = df_to_html(df_comb, decimals)
            return

        # si no hay nada con qué construir, dejar placeholder controlado
        log["matrix_json"] = {"columns": [], "rows": []}
        log["matrix"] = "<p style='color:gray;font-style:italic;'>No matrix available for this step.</p>"
    except Exception:
        log["matrix_json"] = {"columns": [], "rows": []}
        log["matrix"] = "<p style='color:gray;font-style:italic;'>No matrix available for this step.</p>"

# ===================== VISTAS =====================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/options", response_class=HTMLResponse)
async def options(request: Request):
    function_names = get_function_names("tools/methods")
    # Organizar métodos por categorías
    categorized_methods = {
        'All': function_names,
        'Solution_of_Nonlinear_Equations': [m for m in function_names if m in METHOD_CATEGORIES['Solution_of_Nonlinear_Equations']],
        'Solution_of_linear_system_equations': [m for m in function_names if m in METHOD_CATEGORIES['Solution_of_linear_system_equations']],
        'Interpolation': [m for m in function_names if m in METHOD_CATEGORIES['Interpolation']]
    }
    return templates.TemplateResponse(
        "options.html",
        {
            "request": request,
            "function_names": function_names,
            "categories": categorized_methods
        }
    )

@app.get("/calculations/{method_name}", response_class=HTMLResponse)
async def method_page(request: Request, method_name: str):
    try:
        return templates.TemplateResponse(f"methods/{method_name}.html", {"request": request, "method_name": method_name})
    except Exception:
        return templates.TemplateResponse("404.html", {"request": request, "message": "Método no encontrado"}, status_code=404)

# ===================== ENDPOINTS EXISTENTES =====================
@app.post("/calculations/derivate", response_class=HTMLResponse)
async def derivate_post(request: Request, function: str = Form(...)):
    answer = derivatePythonExpr(function)
    return JSONResponse(content={"result": answer})

@app.post("/eval/newton_method", response_class=HTMLResponse)
async def newton_method_post(request: Request, function: str = Form(...), x0: float = Form(...), Nmax: int = Form(...), tol: float = Form(...), nrows: int = Form(...)):
    answer = newton_method_controller(function=function, x0=x0, Nmax=Nmax, tol=tol, nrows=nrows)
    return JSONResponse(content=answer)

@app.post("/eval/modified_newton", response_class=HTMLResponse)
async def modified_newton_post(request: Request, function: str = Form(...), df: Optional[str] = Form(None), d2f: Optional[str] = Form(None), x0: float = Form(...), Nmax: int = Form(...), tol: float = Form(...), nrows: int = Form(...)):
    answer = newton_multiple_controller(function=function, x0=x0, Nmax=Nmax, tol=tol, nrows=nrows, df=df, d2f=d2f)
    return JSONResponse(content=answer)

@app.post("/eval/bisection", response_class=HTMLResponse)
async def bisection_post(request: Request, function: str = Form(...), a: float = Form(...), b: float = Form(...), nmax: int = Form(...), tolerance: float = Form(...), last_n_rows: int = Form(...)):
    answer = bisection_controller(function=function, a=a, b=b, nmax=nmax, tolerance=tolerance, last_n_rows=last_n_rows)
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

        # Validaciones básicas
        if not (isinstance(A, list) and all(isinstance(row, list) for row in A) and A):
            return JSONResponse(content={"error": "Matrix 'A' must be a non-empty list of lists."}, status_code=400)
        if not (isinstance(b, list) and b):
            return JSONResponse(content={"error": "Vector 'b' must be a non-empty list."}, status_code=400)

        cols = len(A[0])
        if not all(len(row) == cols for row in A):
            return JSONResponse(content={"error": "All rows in 'A' must have the same length."}, status_code=400)

        # Conversión a floats
        A_conv = []
        for i, row in enumerate(A):
            row_conv = []
            for j, val in enumerate(row):
                f = to_float_safe(val)
                if f is None:
                    return JSONResponse(content={"error": f"Non-numeric value at A[{i+1}][{j+1}] → {repr(val)}"}, status_code=400)
                row_conv.append(f)
            A_conv.append(row_conv)

        b_conv = []
        for i, val in enumerate(b):
            f = to_float_safe(val)
            if f is None:
                return JSONResponse(content={"error": f"Non-numeric value at b[{i+1}] → {repr(val)}"}, status_code=400)
            b_conv.append(f)

        try:
            decimals = int(decimals)
            if not (0 <= decimals <= 10):
                raise ValueError
        except (TypeError, ValueError):
            return JSONResponse(content={"error": "Parameter 'decimals' must be an integer between 0 and 10."}, status_code=400)

        # Llamada al cálculo (tu función)
        result = gauss_simple(A_conv, b_conv, decimals)

        # Serializar logs correctamente
        for log in result.get("logs", []):
            # hacemos una copia de las claves porque las modificaremos
            original_keys = list(log.keys())
            for k in original_keys:
                v = log.get(k)

                # serializamos el valor
                try:
                    ser = serialize_value(v, decimals)
                except Exception:
                    # fallback a str si algo raro
                    ser = str(v)

                # Si el serializador devolvió dict con html/json
                if isinstance(ser, dict) and "html" in ser and "json" in ser:
                    if k == "matrix":
                        # mantener la clave 'matrix' como HTML (compatibilidad frontend)
                        log["matrix"] = ser["html"]
                        log["matrix_json"] = ser["json"]
                    else:
                        # para A, b, u otros: crear sufijos y eliminar original
                        log[f"{k}_html"] = ser["html"]
                        log[f"{k}_json"] = ser["json"]
                        # eliminar la clave original para no duplicar
                        if k in log:
                            del log[k]
                else:
                    
                    log[k] = ser

            
            combine_A_b(log, decimals)

        # Responder con jsonable_encoder para asegurar serialización
        return JSONResponse(content=jsonable_encoder(result), status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
    
@app.post("/eval/gauss_total", response_class=JSONResponse)
async def gauss_total_post(request: Request):
    try:
    
        try:
            data = await request.json()
        except Exception:
            return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A")
        b = data.get("b")
        decimals = data.get("decimals", 6)

        if A is None or b is None:
            return JSONResponse(
                content={"error": "Parameters 'A' and 'b' are required."},
                status_code=400
            )


        if not (isinstance(A, list) and all(isinstance(row, list) for row in A) and A):
            return JSONResponse(content={"error": "Matrix 'A' must be a non-empty list of lists."}, status_code=400)
        if not (isinstance(b, list) and b):
            return JSONResponse(content={"error": "Vector 'b' must be a non-empty list."}, status_code=400)

        cols = len(A[0])
        if not all(len(row) == cols for row in A):
            return JSONResponse(content={"error": "All rows in 'A' must have the same length."}, status_code=400)


        A_conv = []
        for i, row in enumerate(A):
            row_conv = []
            for j, val in enumerate(row):
                f = to_float_safe(val)
                if f is None:
                    return JSONResponse(
                        content={"error": f"Non-numeric value at A[{i+1}][{j+1}] → {repr(val)}"},
                        status_code=400
                    )
                row_conv.append(f)
            A_conv.append(row_conv)

        b_conv = []
        for i, val in enumerate(b):
            f = to_float_safe(val)
            if f is None:
                return JSONResponse(
                    content={"error": f"Non-numeric value at b[{i+1}] → {repr(val)}"},
                    status_code=400
                )
            b_conv.append(f)

     
        try:
            decimals = int(decimals)
            if not (0 <= decimals <= 10):
                raise ValueError
        except (TypeError, ValueError):
            return JSONResponse(content={"error": "Parameter 'decimals' must be an integer between 0 and 10."}, status_code=400)

       
        result = gauss_total(A_conv, b_conv, decimals)

       
        for log in result.get("logs", []):
            original_keys = list(log.keys())
            for k in original_keys:
                v = log.get(k)
                try:
                    ser = serialize_value(v, decimals)
                except Exception:
                    ser = str(v)

                if isinstance(ser, dict) and "html" in ser and "json" in ser:
                    if k == "matrix":
                        log["matrix"] = ser["html"]
                        log["matrix_json"] = ser["json"]
                    else:
                        log[f"{k}_html"] = ser["html"]
                        log[f"{k}_json"] = ser["json"]
                        if k in log:
                            del log[k]
                else:
                    log[k] = ser

          
            combine_A_b(log, decimals)

        return JSONResponse(content=jsonable_encoder(result), status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
    
@app.post("/eval/gauss_partial", response_class=JSONResponse)
async def gauss_partial_post(request: Request):
    try:
    
        try:
            data = await request.json()
        except Exception:
            return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A")
        b = data.get("b")
        decimals = data.get("decimals", 6)

        if A is None or b is None:
            return JSONResponse(
                content={"error": "Parameters 'A' and 'b' are required."},
                status_code=400
            )


        if not (isinstance(A, list) and all(isinstance(row, list) for row in A) and A):
            return JSONResponse(content={"error": "Matrix 'A' must be a non-empty list of lists."}, status_code=400)
        if not (isinstance(b, list) and b):
            return JSONResponse(content={"error": "Vector 'b' must be a non-empty list."}, status_code=400)

        cols = len(A[0])
        if not all(len(row) == cols for row in A):
            return JSONResponse(content={"error": "All rows in 'A' must have the same length."}, status_code=400)


        A_conv = []
        for i, row in enumerate(A):
            row_conv = []
            for j, val in enumerate(row):
                f = to_float_safe(val)
                if f is None:
                    return JSONResponse(
                        content={"error": f"Non-numeric value at A[{i+1}][{j+1}] → {repr(val)}"},
                        status_code=400
                    )
                row_conv.append(f)
            A_conv.append(row_conv)

        b_conv = []
        for i, val in enumerate(b):
            f = to_float_safe(val)
            if f is None:
                return JSONResponse(
                    content={"error": f"Non-numeric value at b[{i+1}] → {repr(val)}"},
                    status_code=400
                )
            b_conv.append(f)

     
        try:
            decimals = int(decimals)
            if not (0 <= decimals <= 10):
                raise ValueError
        except (TypeError, ValueError):
            return JSONResponse(content={"error": "Parameter 'decimals' must be an integer between 0 and 10."}, status_code=400)

       
        result = gauss_partial(A_conv, b_conv, decimals)

       
        for log in result.get("logs", []):
            original_keys = list(log.keys())
            for k in original_keys:
                v = log.get(k)

                try:
                    ser = serialize_value(v, decimals)
                except Exception:
                    ser = str(v)

                if isinstance(ser, dict) and "html" in ser and "json" in ser:
                    if k == "matrix":
                        log["matrix"] = ser["html"]
                        log["matrix_json"] = ser["json"]
                    else:
                        log[f"{k}_html"] = ser["html"]
                        log[f"{k}_json"] = ser["json"]
                        if k in log:
                            del log[k]
                else:
                    log[k] = ser

          
            combine_A_b(log, decimals)

        return JSONResponse(content=jsonable_encoder(result), status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
    
@app.post("/eval/crout", response_class=JSONResponse)
async def crout_post(request: Request):
    try:
        # Parse JSON safely
        try:
            data = await request.json()
        except Exception:
            return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A")
        b = data.get("b")
        decimals = data.get("decimals", 6)

        # Check required parameters
        if A is None or b is None:
            return JSONResponse(
                content={"error": "Parameters 'A' and 'b' are required."},
                status_code=400
            )

        # Validate matrix A and vector b structure
        if not (isinstance(A, list) and all(isinstance(row, list) for row in A) and A):
            return JSONResponse(content={"error": "Matrix 'A' must be a non-empty list of lists."}, status_code=400)
        if not (isinstance(b, list) and b):
            return JSONResponse(content={"error": "Vector 'b' must be a non-empty list."}, status_code=400)

        cols = len(A[0])
        if not all(len(row) == cols for row in A):
            return JSONResponse(content={"error": "All rows in 'A' must have the same length."}, status_code=400)

        # Convert to float safely
        A_conv = []
        for i, row in enumerate(A):
            row_conv = []
            for j, val in enumerate(row):
                f = to_float_safe(val)
                if f is None:
                    return JSONResponse(
                        content={"error": f"Non-numeric value at A[{i+1}][{j+1}] → {repr(val)}"},
                        status_code=400
                    )
                row_conv.append(f)
            A_conv.append(row_conv)

        b_conv = []
        for i, val in enumerate(b):
            f = to_float_safe(val)
            if f is None:
                return JSONResponse(
                    content={"error": f"Non-numeric value at b[{i+1}] → {repr(val)}"},
                    status_code=400
                )
            b_conv.append(f)

        # Validate decimals
        try:
            decimals = int(decimals)
            if not (0 <= decimals <= 10):
                raise ValueError
        except (TypeError, ValueError):
            return JSONResponse(content={"error": "Parameter 'decimals' must be an integer between 0 and 10."}, status_code=400)

        # Compute Crout decomposition result
        result = crout(A_conv, b_conv, decimals)

        # Serialize DataFrames and combine A|b for visualization
        for log in result.get("logs", []):
            original_keys = list(log.keys())
            for k in original_keys:
                v = log.get(k)

                try:
                    ser = serialize_value(v, decimals)
                except Exception:
                    ser = str(v)

                if isinstance(ser, dict) and "html" in ser and "json" in ser:
                    if k == "matrix":
                        log["matrix"] = ser["html"]
                        log["matrix_json"] = ser["json"]
                    else:
                        log[f"{k}_html"] = ser["html"]
                        log[f"{k}_json"] = ser["json"]
                        if k in log:
                            del log[k]
                else:
                    log[k] = ser

            combine_A_b(log, decimals)

        return JSONResponse(content=jsonable_encoder(result), status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
    
@app.post("/eval/doolittle", response_class=JSONResponse)
async def doolittle_post(request: Request):
    try:
        # Parse JSON safely
        try:
            data = await request.json()
        except Exception:
            return JSONResponse(content={"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A")
        b = data.get("b")
        decimals = data.get("decimals", 6)

        # Check required parameters
        if A is None or b is None:
            return JSONResponse(
                content={"error": "Parameters 'A' and 'b' are required."},
                status_code=400
            )

        # Validate matrix A and vector b structure
        if not (isinstance(A, list) and all(isinstance(row, list) for row in A) and A):
            return JSONResponse(content={"error": "Matrix 'A' must be a non-empty list of lists."}, status_code=400)
        if not (isinstance(b, list) and b):
            return JSONResponse(content={"error": "Vector 'b' must be a non-empty list."}, status_code=400)

        cols = len(A[0])
        if not all(len(row) == cols for row in A):
            return JSONResponse(content={"error": "All rows in 'A' must have the same length."}, status_code=400)

        # Convert to float safely
        A_conv = []
        for i, row in enumerate(A):
            row_conv = []
            for j, val in enumerate(row):
                f = to_float_safe(val)
                if f is None:
                    return JSONResponse(
                        content={"error": f"Non-numeric value at A[{i+1}][{j+1}] → {repr(val)}"},
                        status_code=400
                    )
                row_conv.append(f)
            A_conv.append(row_conv)

        b_conv = []
        for i, val in enumerate(b):
            f = to_float_safe(val)
            if f is None:
                return JSONResponse(
                    content={"error": f"Non-numeric value at b[{i+1}] → {repr(val)}"},
                    status_code=400
                )
            b_conv.append(f)

        # Validate decimals
        try:
            decimals = int(decimals)
            if not (0 <= decimals <= 10):
                raise ValueError
        except (TypeError, ValueError):
            return JSONResponse(content={"error": "Parameter 'decimals' must be an integer between 0 and 10."}, status_code=400)

        # Compute Doolittle decomposition result
        result = doolittle(A_conv, b_conv, decimals)

        # Serialize DataFrames and combine A|b for visualization
        for log in result.get("logs", []):
            original_keys = list(log.keys())
            for k in original_keys:
                v = log.get(k)

                try:
                    ser = serialize_value(v, decimals)
                except Exception:
                    ser = str(v)

                if isinstance(ser, dict) and "html" in ser and "json" in ser:
                    if k == "matrix":
                        log["matrix"] = ser["html"]
                        log["matrix_json"] = ser["json"]
                    else:
                        log[f"{k}_html"] = ser["html"]
                        log[f"{k}_json"] = ser["json"]
                        if k in log:
                            del log[k]
                else:
                    log[k] = ser

            combine_A_b(log, decimals)

        return JSONResponse(content=jsonable_encoder(result), status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)


@app.post("/eval/incremental_search")
async def incremental_search_post(request: Request, function: str = Form(...), x0: float = Form(...), delta_x: float = Form(...), max_iter: int = Form(...), nrows: int = Form(...)):
    f = latex_to_callable_function(function)
    answer = incremental_search(f=f, x0=x0, delta_x=delta_x, max_iter=max_iter)
    return JSONResponse(content=answer)

@app.post("/eval/false_position", response_class=HTMLResponse)
async def false_position_post(request: Request, function: str = Form(...), a: float = Form(...), b: float = Form(...), nmax: int = Form(...), tolerance: float = Form(...), last_n_rows: int = Form(...)):
    answer = false_position_controller(function=function, a=a, b=b, nmax=nmax, tolerance=tolerance, last_n_rows=last_n_rows)
    return JSONResponse(content=answer)

@app.post("/eval/fixed_point", response_class=HTMLResponse)
async def eval_fixed_point(request: Request, g: str = Form(""), f: str = Form(""), x0: float = Form(...), tol: float = Form(1e-6), max_iter: int = Form(100), use_relative_error: str = Form(None)):
    result = run_fixed_point_web(g_text=g, f_text=f, x0=x0, tol=tol, max_iter=max_iter, use_relative_error=bool(use_relative_error))
    return templates.TemplateResponse(
        "methods/fixed_point.html",
        {"request": request,
         "form": {"g": g, "f": f, "x0": x0, "tol": tol, "max_iter": max_iter, "use_relative_error": bool(use_relative_error)},
         "result": result}
    )

@app.post("/eval/secant", response_class=HTMLResponse)
async def secant_method_post(request: Request, function: str = Form(...), x0: float = Form(...), x1: float = Form(...), Nmax: int = Form(...), tol: float = Form(...), nrows: int = Form(...)):
    answer = secant_method_controller(function=function, x0=x0, x1=x1, Nmax=Nmax, tol=tol, nrows=nrows)
    return JSONResponse(content=answer)



@app.get("/chat", response_class=HTMLResponse)
async def chat_recive(request: Request):
    function_names = get_function_names("tools/numeric_methods.py")
    return templates.TemplateResponse("chat.html", {"request": request, "function_names": function_names})


def _is_number(x):
    try:
        float(x); return True
    except (TypeError, ValueError):
        return False

def _validate_matrix(A):
    if not (isinstance(A, list) and A and all(isinstance(row, list) for row in A)):
        return "Matrix 'A' must be a non-empty list of lists."
    cols = len(A[0])
    if not all(len(row) == cols for row in A):
        return "All rows in 'A' must have the same length."
    for i, row in enumerate(A):
        for j, val in enumerate(row):
            if not _is_number(val):
                return f"Non-numeric value at A[{i+1}][{j+1}] → {repr(val)}"
    return None

def _validate_vector(name, v):
    if not (isinstance(v, list) and v):
        return f"Vector '{name}' must be a non-empty list."
    for i, val in enumerate(v):
        if not _is_number(val):
            return f"Non-numeric value at {name}[{i+1}] → {repr(val)}"
    return None


@app.post("/eval/lu_partial", response_class=JSONResponse)
async def lu_partial_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A"); b = data.get("b")
        err = _validate_matrix(A) or _validate_vector("b", b)
        if err: return JSONResponse({"error": err}, status_code=400)

        result = compute_gauss_pivote_parcial(A, b, track_etapas=True)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)
    
@app.post("/eval/lu_simple", response_class=JSONResponse)
async def lu_simple_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A"); b = data.get("b")
        err = _validate_matrix(A) or _validate_vector("b", b)
        if err: return JSONResponse({"error": err}, status_code=400)

        result = compute_lu_simple(A, b, track_etapas=True)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)

@app.post("/eval/vandermonde", response_class=JSONResponse)
async def vandermonde_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        x = data.get("x"); y = data.get("y")
        if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) > 0):
            return JSONResponse({"error": "x and y must be non-empty lists of the same length."}, status_code=400)
        for i, v in enumerate(x):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at x[{i+1}] → {repr(v)}"}, status_code=400)
        for i, v in enumerate(y):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at y[{i+1}] → {repr(v)}"}, status_code=400)

        result = compute_vandermonde(x, y)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)
    
@app.post("/eval/newton_interpolant", response_class=JSONResponse)
async def newton_interpolant(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        x = data.get("x"); y = data.get("y")
        if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) > 0):
            return JSONResponse({"error": "x and y must be non-empty lists of the same length."}, status_code=400)
        for i, v in enumerate(x):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at x[{i+1}] → {repr(v)}"}, status_code=400)
        for i, v in enumerate(y):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at y[{i+1}] → {repr(v)}"}, status_code=400)

        result = newton_interpolant_object(x, y)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)
    
    
@app.post("/eval/lagrange", response_class=JSONResponse)
async def newton_interpolant(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        x = data.get("x"); y = data.get("y")
        if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) > 0):
            return JSONResponse({"error": "x and y must be non-empty lists of the same length."}, status_code=400)
        for i, v in enumerate(x):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at x[{i+1}] → {repr(v)}"}, status_code=400)
        for i, v in enumerate(y):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at y[{i+1}] → {repr(v)}"}, status_code=400)

        result = lagrange_interpolation_object(x, y)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)
    
    



@app.post("/eval/lineal_tracers", response_class=JSONResponse)
async def lineal_tracers_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        x = data.get("x"); y = data.get("y")
        if not (isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and len(x) >= 2):
            return JSONResponse({"error": "x and y must be lists with the same length (>= 2)."}, status_code=400)
        for i, v in enumerate(x):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at x[{i+1}] → {repr(v)}"}, status_code=400)
        for i, v in enumerate(y):
            if not _is_number(v):
                return JSONResponse({"error": f"Non-numeric value at y[{i+1}] → {repr(v)}"}, status_code=400)

        result = compute_trazadores_lineales(x, y)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)


@app.post("/eval/cholesky", response_class=JSONResponse)
async def cholesky_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A"); b = data.get("b")
        err = _validate_matrix(A) or _validate_vector("b", b)
        if err: return JSONResponse({"error": err}, status_code=400)
        if len(A) != len(A[0]) or len(A) != len(b):
            return JSONResponse({"error": "A must be square and size(A) must match len(b)."}, status_code=400)

        result = compute_cholesky(A, b, track_etapas=True)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)


@app.post("/eval/jacobi", response_class=JSONResponse)
async def jacobi_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A"); b = data.get("b"); x0 = data.get("x0")
        tol = data.get("tol", 1e-7); nmax = data.get("nmax", 100); norma = data.get("norma", "inf")

        err = _validate_matrix(A) or _validate_vector("b", b) or _validate_vector("x0", x0)
        if err: return JSONResponse({"error": err}, status_code=400)

        try:
            tol = float(tol); nmax = int(nmax)
            if norma not in ("inf", "2", "1"): norma = "inf"
        except Exception:
            return JSONResponse({"error": "Invalid 'tol', 'nmax' or 'norma'."}, status_code=400)

        if len(A) != len(A[0]) or len(A) != len(b) or len(A) != len(x0):
            return JSONResponse({"error": "A must be square and size(A) must match len(b) and len(x0)."}, status_code=400)

        result = compute_jacobi(A, b, x0, tol=tol, nmax=nmax, norma=norma)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)
    
    
@app.post("/eval/gauss_seidel", response_class=JSONResponse)
async def gauss_seidel_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A"); b = data.get("b"); x0 = data.get("x0")
        tol = data.get("tol", 1e-7); 
        nmax = data.get("nmax", 100); 
        norma = data.get("norma", "inf")
        decimals = data.get("decimales")
        err = _validate_matrix(A) or _validate_vector("b", b) or _validate_vector("x0", x0)
        if err: return JSONResponse({"error": err}, status_code=400)

        try:
            tol = float(tol); nmax = int(nmax); decimals=int(decimals)
            if norma not in ("inf", "2", "1"): norma = "inf"
        except Exception:
            return JSONResponse({"error": "Invalid 'tol', 'nmax', 'decimals' or 'norma'."}, status_code=400)

        if len(A) != len(A[0]) or len(A) != len(b) or len(A) != len(x0):
            return JSONResponse({"error": "A must be square and size(A) must match len(b) and len(x0)."}, status_code=400)

        result = gauss_seidel(A=A, b=b, tolerance=tol, x_0=x0,n_max=nmax, decimals=decimals ,norma=norma)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)
    
@app.post("/eval/SOR", response_class=JSONResponse)
async def gauss_seidel_eval(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

        A = data.get("A"); b = data.get("b"); x0 = data.get("x0")
        tol = data.get("tol", 1e-7); 
        nmax = data.get("nmax", 100); 
        norma = data.get("norma", "inf")
        omega = data.get("omega", 1)

        
        err = _validate_matrix(A) or _validate_vector("b", b) or _validate_vector("x0", x0)
        
        if err: return JSONResponse({"error": err}, status_code=400)

        try:
            tol = float(tol); nmax = int(nmax); omega=float(omega)
            if norma not in ("inf", "2", "1"): norma = "inf"
        except Exception:
            return JSONResponse({"error": "Invalid 'tol', 'nmax', or 'norma'."}, status_code=400)

        if len(A) != len(A[0]) or len(A) != len(b) or len(A) != len(x0):
            return JSONResponse({"error": "A must be square and size(A) must match len(b) and len(x0)."}, status_code=400)

        result = sor(A=A, b=b, omega=omega, tolerance=tol, x_0=x0,n_max=nmax,norma=norma)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)
    
    #Endpoint para trazadores
def to_float_safe(value):
    """Attempts to convert to float safely."""
    try:
        return float(value)
    except:
        return None

@app.post("/eval/cubic_spline", response_class=JSONResponse)
async def cubic_spline_post(request: Request):
    try:
        # Parse JSON safely
        try:
            data = await request.json()
        except Exception:
            return JSONResponse(
                content={"error": "Invalid JSON body."},
                status_code=400
            )
        print(data)
        # Extract parameters
        x = data.get("x")
        y = data.get("y")

        # Required fields
        if x is None or y is None:
            return JSONResponse(
                content={"error": "Parameters 'x' and 'y' are required."},
                status_code=400
            )

        # Validate lists
        if not isinstance(x, list) or not isinstance(y, list):
            return JSONResponse(
                content={"error": "'x' and 'y' must be lists."},
                status_code=400
            )

        if len(x) != len(y):
            return JSONResponse(
                content={"error": "'x' and 'y' must have the same length."},
                status_code=400
            )

        if len(x) < 2:
            return JSONResponse(
                content={"error": "At least two points are required to build a cubic spline."},
                status_code=400
            )

        # Convert safely to float
        x_conv = []
        for i, val in enumerate(x):
            f = to_float_safe(val)
            if f is None:
                return JSONResponse(
                    content={"error": f"Non-numeric value in x[{i+1}] → {repr(val)}"},
                    status_code=400
                )
            x_conv.append(f)

        y_conv = []
        for i, val in enumerate(y):
            f = to_float_safe(val)
            if f is None:
                return JSONResponse(
                    content={"error": f"Non-numeric value in y[{i+1}] → {repr(val)}"},
                    status_code=400
                )
            y_conv.append(f)

        # Run cubic spline computation
        try:
            coefficients = cubic_spline_method(x_conv, y_conv)
        except Exception as e:
            return JSONResponse(
                content={"error": f"Cubic spline computation failed: {str(e)}"},
                status_code=400
            )

        # Build logs (no decimals)
        logs = save_cubic_tracer(x_conv, coefficients)

        # Final response
        result = {
            "coefficients": coefficients,
            "logs": logs
        }

        return JSONResponse(
            content=jsonable_encoder(result),
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"error": f"Internal server error: {str(e)}"},
            status_code=500
        )

# ===================== 404 =====================
@app.exception_handler(404)
async def not_found(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

