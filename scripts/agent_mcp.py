import asyncio
import sys

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=["-m", "docctl_mcp.server"])


async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()

            # 1. Translate the server's tool menu into Ollama's format
            tools = []
            for t in listed.tools:
                tools.append({"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.input_schema}})

            # 2. Ask the model, with the menu
            messages = [{"role": "user", "content": "Which documents in my project have problems?"}]
            response = ollama.chat(model="qwen2.5:3b", messages=messages, tools=tools)
            messages.append(response.message)

            # 3. Run each tool the model wants, via the MCP server
            for call in response.message.tool_calls or []:
                print("Model wants:", call.function.name)
                result = await session.call_tool(call.function.name, call.function.arguments)
                text = ""
                for piece in result.content:
                    text += piece.text + "\n"
                messages.append({"role": "tool", "content": text, "tool_name": call.function.name})
            final = ollama.chat(model="qwen2.5:3b", messages=messages)
            print(final.message.content)


asyncio.run(main())