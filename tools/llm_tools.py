import json
from openai import OpenAI


class SimpleMCPClient:
    def __init__(self, openai_base_url="http://localhost:1234/v1"):
        self.openai = OpenAI(
            base_url=openai_base_url,
            api_key="lm-studio"
        )
        self.available_tools = []

    def chat_with_tools(self, messages):
        """Chat with OpenAI without MCP tools"""
        current_messages = messages[:]
        
        # Call OpenAI
        response = self.openai.chat.completions.create(
            model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",
            messages=current_messages,
            temperature=1.1,
            max_tokens=500,
            stream=True
        )
        
        # Stream response
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def chat_answer(messages, server_url="http://localhost:8080"):
    """Simple function to chat without MCP tools"""
    client = SimpleMCPClient()
    return client.chat_with_tools(messages)