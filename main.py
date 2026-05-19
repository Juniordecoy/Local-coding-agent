from ai import ask_ai, chat_with_memory, choose_tool
from memory import load_memory, save_memory
from file_tools import read_notes, read_file, list_project_files, search_project_files, search_project_files_with_scores
from workflows import explain_file, summarize_project, analyze_project, analyze_file, answer_about_main_file, answer_with_auto_retrieval

notes = read_notes()

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful local AI assistant. "
            "Keep answers beginner-friendly and concise. "
            "You specialize in Python, Flask, HTML, CSS, JavaScript, and beginner-friendly web development help.\n\n"
            "Here are local notes you can use:\n"
            f"{notes}"
        )
    }
]

messages.extend(load_memory())

AUTO_RETRIEVAL_KEYWORDS = [
    "memory",
    "file",
    "files",
    "notes",
    "project"
]

def show_files():
    files = list_project_files()

    result = "PROJECT FILES:\n"

    for file in files:
        result += f"- {file}\n"

    return result

def explain_command(user_message):
    filename = user_message.replace("explain ", "", 1)

    ai_message = explain_file(filename)

    return ai_message

def read_command(user_message):
    filename = user_message.replace("read ", "", 1)

    ai_message = analyze_file(filename)

    return ai_message

def search_command(user_message):
    keyword = user_message.replace("search ", "", 1)

    matches = search_project_files(keyword)

    if not matches:
        return "No matching files found."

    result = "MATCHING FILES:\n"

    for match in matches:
        result += f"- {match}\n"

    return result

def debug_search_command(user_message):
    keyword = user_message.replace("debug search ", "", 1)

    matches = search_project_files_with_scores(keyword)

    if not matches:
        return "No matching files found."

    result = "DEBUG SEARCH RESULTS:\n"

    for match in matches:
        result += f"- {match['file']} | score: {match['score']}\n"

    return result

def run_tool(tool_name, tool_input):
    if tool_name not in TOOLS:
        return f"Unknown tool: {tool_name}"

    tool_function = TOOLS[tool_name]

    if tool_name == "list_project_files":
        return tool_function()

    return tool_function(tool_input)

ARGUMENT_COMMANDS = {
    "debug search ": debug_search_command,
    "explain ": explain_command,
    "read ": read_command,
    "search ": search_command,
}

TOOLS = {
    "read_file": read_file,
    "list_project_files": list_project_files,
    "search_project_files": search_project_files,
}

COMMANDS = {
    "summarize project": summarize_project,
    "analyze project": analyze_project,
    "files": show_files
}

print("Local AI Assistant")
print("Type 'exit' to quit.\n")

while True:
    user_message = input("You: ")

    if user_message.lower() == "exit":
        save_memory(messages)
        print("Memory saved. Goodbye.")
        break

    if user_message.startswith("choose tool "):
        request = user_message.replace("choose tool ", "", 1)

        chosen_tool = choose_tool(
            user_message=request,
            available_tools=TOOLS.keys()
        )

        print(f"\nCHOSEN TOOL: {chosen_tool}\n")

        continue

    if user_message.startswith("run tool "):
        tool_name = user_message.replace("run tool ", "", 1)

        result = run_tool(
            tool_name=tool_name,
            tool_input="main.py"
        )

        print(f"\nTOOL RESULT:\n{result}\n")

        continue

    if user_message.startswith("agent "):
        request = user_message.replace("agent ", "", 1)

        chosen_tool = choose_tool(
            user_message=request,
            available_tools=TOOLS.keys()
        )

        tool_result = run_tool(
            tool_name=chosen_tool,
            tool_input="main.py"
        )

        print(f"\nCHOSEN TOOL: {chosen_tool}")
        print(f"\nTOOL RESULT:\n{tool_result}\n")

        continue

    command_handled = False

    for command, handler in ARGUMENT_COMMANDS.items():
        if user_message.startswith(command):
            result = handler(user_message)

            print(f"\nRESULT:\n{result}\n")

            command_handled = True
            break

    if command_handled:
        continue

    if user_message.lower() in COMMANDS:
        result = COMMANDS[user_message.lower()]()

        print(f"\nRESULT:\n{result}\n")

        continue

    if "main.py" in user_message:
        ai_message = answer_about_main_file()

        print(f"\nAI RESPONSE:\n{ai_message}\n")

        continue

    if any(word in user_message.lower() for word in AUTO_RETRIEVAL_KEYWORDS):
        matches, ai_message = answer_with_auto_retrieval(
            user_message=user_message,
            keywords=AUTO_RETRIEVAL_KEYWORDS
        )

        print("\nUSING FILES:")
        for match in matches:
            print(f"- {match}")
        print()

        print(f"\nAI RESPONSE:\n{ai_message}\n")

        continue

    messages.append({
        "role": "user",
        "content": user_message
    })

    ai_message = chat_with_memory(messages)

    print(f"\nAI: {ai_message}\n")

    messages.append({
        "role": "assistant",
        "content": ai_message
    })

    save_memory(messages)