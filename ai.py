import ollama

MODEL = "llama3.2:3b"

def ask_ai(system_prompt, user_prompt):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response["message"]["content"]

def chat_with_memory(messages):
    response = ollama.chat(
        model=MODEL,
        messages=messages
    )

    return response["message"]["content"]