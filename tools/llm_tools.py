import asyncio
import json
from typing import Optional, AsyncGenerator, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

from openai import OpenAI
from openai.types import Completion


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio"  # Changed to match your tools.py
        )
        self.available_tools = []
        self.messages = []

        self._session_context = None
        self._streams_context = None

    async def cleanup(self):
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
            self._session_context = None
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)
            self._streams_context = None

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""
        print("Connecting to MCP SSE server...")
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()
        print("Streams:", streams)  

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        print("Initializing SSE client...")
        await self.session.initialize()
        print("Initialized SSE client")
        
        # List available tools to verify connection
        await self.get_available_tools()
        await self.get_initial_prompts()
    
    async def get_initial_prompts(self):
        try:
            prompt = await self.session.get_prompt("get_initial_prompts")
            # Format messages for OpenAI
            messages = []
            for message in prompt.messages:
                messages.append({
                    "role": message.role,
                    "content": message.content.text
                })
            self.messages = messages
        except Exception as e:
            print(f"Could not get initial prompts: {e}")
            self.messages = []

    async def get_available_tools(self):
        """Get available tools from the server"""
        print("Fetching available server tools...")
        response = await self.session.list_tools()
        print("Connected to MCP server with tools:", [tool.name for tool in response.tools])

        # Format tools for OpenAI
        available_tools = [
            {
                "type": 'function',
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
                "strict": True,
            }
            for tool in response.tools
        ]
        self.available_tools = available_tools

    async def call_openai_stream(self):
        """Call OpenAI with streaming enabled"""
        return self.openai.chat.completions.create(
            model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",  # Match your model
            max_tokens=140,  # Match your settings
            temperature=1.1,  # Match your settings
            messages=self.messages,
            tools=self.available_tools if self.available_tools else None,
            stream=True  # Enable streaming
        )

    async def process_openai_stream_response(self, stream) -> AsyncGenerator[Dict[str, Any], None]:
        """Process streaming response from OpenAI with tool support"""
        collected_chunks = []
        tool_calls = []
        
        # Collect all chunks first
        for chunk in stream:
            collected_chunks.append(chunk)
            
            # Check if this chunk has content to stream
            if chunk.choices and chunk.choices[0].delta.content:
                yield {"content": chunk.choices[0].delta.content}
            
            # Check for tool calls
            if chunk.choices and chunk.choices[0].delta.tool_calls:
                for tool_call in chunk.choices[0].delta.tool_calls:
                    if len(tool_calls) <= tool_call.index:
                        tool_calls.extend([None] * (tool_call.index - len(tool_calls) + 1))
                    
                    if tool_calls[tool_call.index] is None:
                        tool_calls[tool_call.index] = {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        }
                    
                    if tool_call.function.name:
                        tool_calls[tool_call.index]["function"]["name"] = tool_call.function.name
                    if tool_call.function.arguments:
                        tool_calls[tool_call.index]["function"]["arguments"] += tool_call.function.arguments

        # Check if we need to handle tool calls
        if tool_calls and any(tc for tc in tool_calls if tc):
            # Reconstruct the assistant message
            assistant_message = {
                "role": "assistant",
                "content": "",
                "tool_calls": [tc for tc in tool_calls if tc]
            }
            
            # Add to messages
            self.messages.append(assistant_message)
            
            # Process each tool call
            for tool_call in assistant_message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                
                yield {"content": f"\n[Calling tool {tool_name}...]"}
                
                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                    tool_result = str(result.content) if hasattr(result, 'content') else str(result)
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result,
                    })
                    
                    yield {"content": f"\n[Tool completed]"}
                    
                except Exception as e:
                    yield {"content": f"\n[Tool error: {str(e)}]"}
            
            # Make another call to get the final response
            final_stream = await self.call_openai_stream()
            async for chunk in self.process_openai_stream_response(final_stream):
                yield chunk

    async def process_query_stream(self, messages: list) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a query with streaming response"""
        # Set messages from the chat history
        self.messages = messages.copy()
        
        # Call OpenAI with streaming
        stream = await self.call_openai_stream()
        
        # Process the streaming response
        async for chunk in self.process_openai_stream_response(stream):
            yield chunk


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None
_client_lock = asyncio.Lock()

async def get_mcp_client(server_url: str = "http://localhost:8080") -> MCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client
    
    async with _client_lock:
        if _mcp_client is None:
            _mcp_client = MCPClient()
            try:
                await _mcp_client.connect_to_sse_server(server_url)
            except Exception as e:
                print(f"Failed to connect to MCP server: {e}")
                print("Falling back to direct OpenAI client...")
                # Don't raise the error, just use the client without MCP tools
        
        return _mcp_client

def chat_answer(messages, use_mcp: bool = True, server_url: str = "http://localhost:8080"):
    """
    New chat_answer function that integrates MCP client with streaming support
    Falls back to direct OpenAI if MCP connection fails
    """
    if use_mcp:
        try:
            # Create a new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            async def _stream_with_mcp():
                try:
                    client = await get_mcp_client(server_url)
                    async for chunk in client.process_query_stream(messages):
                        # Convert async generator to sync by yielding dict with content
                        if 'content' in chunk:
                            # Create a mock chunk object similar to OpenAI's format
                            mock_chunk = type('MockChunk', (), {
                                'choices': [type('Choice', (), {
                                    'delta': type('Delta', (), {
                                        'content': chunk['content']
                                    })()
                                })()]
                            })()
                            yield mock_chunk
                except Exception as e:
                    print(f"MCP streaming error: {e}, falling back to direct OpenAI")
                    # Fall back to direct OpenAI client
                    from openai import OpenAI
                    fallback_client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
                    completion = fallback_client.chat.completions.create(
                        model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",
                        messages=messages,
                        temperature=1.1,
                        max_tokens=140,
                        stream=True,
                    )
                    for chunk in completion:
                        yield chunk
            
            # Run the async generator in the event loop
            return asyncio.run(_async_generator_to_sync(_stream_with_mcp()))
            
        except Exception as e:
            print(f"MCP integration error: {e}, falling back to direct OpenAI")
            use_mcp = False
    
    # Fallback to original direct OpenAI client
    if not use_mcp:
        from openai import OpenAI
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        completion = client.chat.completions.create(
            model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",
            messages=messages,
            temperature=1.1,
            max_tokens=140,
            stream=True,
        )
        return completion

async def _async_generator_to_sync(async_gen):
    """Convert async generator to sync generator"""
    async for item in async_gen:
        yield item