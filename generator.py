import ollama
from config import LLM_MODEL

response = ollama.chat(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": "What is Artificial Intelligence?"}],
)

print(response["message"]["content"])
