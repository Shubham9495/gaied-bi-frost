import ollama

def query_llama(prompt: str):
    response = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]