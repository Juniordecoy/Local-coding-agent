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

def choose_tool_input(user_message, chosen_tool):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You choose the input argument for a tool. "
                    "Only reply with the input value. "
                    "Do not explain."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Chosen tool: {chosen_tool}\n"
                    f"User request: {user_message}\n\n"
                    "If the tool is read_file, return an exact filename from the project, like memory.py, main.py, or notes.txt. Do not return descriptions like ""memory file"". "
                    "If the tool is search_project_files, return the search keyword. "
                    "If the tool is list_project_files, return none."
                )
            }
        ]
    )

    return response["message"]["content"].strip()