import ollama

response = ollama.chat(model="qwen2.5:3b", messages=[{"role": "user", "content": "Say hello in Danish"}])
print(response.message.content)
