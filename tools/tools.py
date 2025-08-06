import ast
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def get_function_names(filename):
    with open(filename, "r") as f:
        tree = ast.parse(f.read(), filename=filename)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def chat_answer(messages):
    """
    Function for test basic conection with llmstudio
    """
    completion = client.chat.completions.create(
        model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",
        messages=messages,
        temperature=1.1,
        max_tokens=140,
        stream=True,  # Enable streaming
    )
    return completion