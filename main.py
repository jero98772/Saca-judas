from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse ,StreamingResponse
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

chat_history=dict()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/options", response_class=HTMLResponse)
async def options(request: Request):
    function_names = get_function_names("tools/numeric_methods.py")
    return templates.TemplateResponse("options.html", {"request": request,"function_names": function_names})

@app.get("/calculations/<function_names>", response_class=HTMLResponse)
async def calculations(request: Request,function_names: str):
    return templates.TemplateResponse("calculations_method.html", {"request": request})

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
    message = data.get("message")
    
    messages = [{"role": "user", "content": message}]
    
    # Get full response without streaming
    completion_stream = chat_answer(messages)
    full_response = ""
    
    for chunk in completion_stream:
        full_response += chunk
    
    return {"response": full_response}