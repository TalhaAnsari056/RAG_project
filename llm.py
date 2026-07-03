import ollama
from config import LLM_MODEL


def generate_answer(prompt):

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,
            "num_predict": 80,
            "num_ctx": 1024,
        },
    )

    return response["message"]["content"]
