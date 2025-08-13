from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tools.tools import get_function_names 
from tools.numeric_methods import *
from tools.llm_tools import chat_answer

import json

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
    function_names = get_function_names("tools/numeric_methods.py")
    return templates.TemplateResponse("options.html", {"request": request,"function_names": function_names})

@app.get("/calculations/{function_names}", response_class=HTMLResponse)
async def calculations(request: Request,function_names: str):
    answer = ""
    return templates.TemplateResponse("calculations_methods_interface.html", {"request": request,"answer":answer})

@app.post("/calculations/{function_names}", response_class=HTMLResponse)
async def calculations(request: Request,function_names: str,values: str = Form(...)):
    print(values)
    data = list(map(int,values.split()))
    print(data)
    try:
        answer = globals()[function_names](*data)   
    except:
        answer = "No valid input, input must be separate by comma, for example 1 2 3, in iterative sqrt"
    return templates.TemplateResponse(
        "calculations_methods_interface.html",
        {"request": request, "answer": answer}
    )

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
