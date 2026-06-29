import ollama


def generate_answer(prompt):

    response = ollama.chat(
        model="qwen3:8b", messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]
