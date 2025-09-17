from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from tools.tools import get_function_names 
from tools.sympyUtilities import validate_math_function, derivateLatex, latex_to_sympy_str
from tools.numeric_methods import *
from tools.llm_tools import chat_answer

import json

from controller import newton_method_controller

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/options", response_class=HTMLResponse)
async def options(request: Request):
    function_names = get_function_names("tools/methods")
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
    answer = derivateLatex(function)
    print(answer)
    return JSONResponse(content={"resultado": answer})

@app.post("/eval/newton_method", response_class=HTMLResponse)
async def newton_method_post(request: Request, function: str = Form(...), x0:float = Form(...), Nmax:int= Form(...), tol:float= Form(...), nrows:int = Form(...)):
    f = latex_to_sympy_str(function)
    answer = newton_method_controller(function=f, x0=x0, Nmax =Nmax, tol=tol, nrows=nrows)
    print(answer)
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
