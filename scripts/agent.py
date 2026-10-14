import ollama

from docctl_mcp.server import audit_folder, check_naming

TOOLS = {"audit_folder": audit_folder, "check_naming": check_naming}

messages = [{"role": "user", "content": "Which documents in my project have problems?"}]

response = ollama.chat(model="qwen2.5:3b", messages=messages, tools=[audit_folder, check_naming])

messages.append(response.message)

for call in response.message.tool_calls or []:
        print("Model wants:", call.function.name)

        tool = TOOLS[call.function.name]
        result = tool(**call.function.arguments)
        messages.append({"role": "tool", "content": str(result), "tool_name": call.function.name})

final = ollama.chat(model="qwen2.5:3b", messages=messages)
print(final.message.content)