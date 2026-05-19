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

def choose_tool(user_message, available_tools):
    tool_list = "\n".join(available_tools)

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a tool selector for a local AI coding assistant. "
                    "Choose the best tool for the user's request. "
                    "Only reply with the tool name. "
                    "Do not explain."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Available tools:\n{tool_list}\n\n"
                    f"User request:\n{user_message}"
                )
            }
        ]
    )

    return response["message"]["content"].strip()