from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse ,StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from openai import OpenAI

from tools.tools import *
from tools.numeric_methods import *

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

#from typing import List, Dict, Optional
#chat_history: Dict[str, List[Dict[str, str]]] = {}

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
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "function_names": function_names}
    )

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    message = data.get("message")
    
    # Initialize session if it doesn't exist
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    # Add user message to history
    chat_history[session_id].append({"role": "user", "content": message})
    
    # Return the user message immediately to confirm receipt
    return {"status": "message received", "user_message": message}

@app.get("/stream/{session_id}")
async def stream_response(session_id: str, model: str = "openai"):
    # Check if session exists
    if session_id not in chat_history:
        return StreamingResponse(content=stream_error("Session not found"), media_type="text/event-stream")
    
    # Get messages from history
    messages = chat_history[session_id]
    
    # If no messages, return error
    if not messages:
        return StreamingResponse(content=stream_error("No messages in session"), media_type="text/event-stream")
    
    # Generate streaming response based on model choice
    return StreamingResponse(
        content=generate_stream(session_id, messages, model),
        media_type="text/event-stream"
    )

async def generate_stream(session_id, messages, model="openai"):
    # Get streaming response from LLM based on model choice
    try:
        full_response = ""
        
        if model == "gemini":
            # Use Gemini model
            async for text in chat_answer_gemini(messages):
                if text:
                    full_response += text
                    yield f"data: {json.dumps({'content': text})}\n\n"
        else:
            # Use OpenAI/LM Studio model
            completion_stream = chat_answer(messages)
            for chunk in completion_stream:
                if hasattr(chunk.choices[0].delta, "content"):
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
        
        # Store the complete response in history
        chat_history[session_id].append({"role": "assistant", "content": full_response})
        
        # Signal completion
        yield f"data: {json.dumps({'status': 'complete'})}\n\n"
    
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def stream_error(error_message):
    yield f"data: {json.dumps({'error': error_message})}\n\n"
