from ai import ask_ai, chat_with_memory, choose_tool, choose_tool_input
from memory import load_memory, save_memory
from file_tools import read_notes, read_file, list_project_files, search_project_files
from workflows import answer_about_main_file, answer_with_auto_retrieval, multi_file_agent_answer
from working_memory import remember_working
from command_registry import ARGUMENT_COMMANDS, COMMANDS

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

TOOLS = {
    "read_file": read_file,
    "list_project_files": list_project_files,
    "search_project_files": search_project_files,
}

def run_tool(tool_name, tool_input):
    if tool_name not in TOOLS:
        return f"Unknown tool: {tool_name}"

    tool_function = TOOLS[tool_name]

    if tool_name == "list_project_files":
        return tool_function()

    if tool_name == "read_file":
        files = list_project_files()

        if tool_input not in files:
            matches = search_project_files(tool_input)

            if matches:
                tool_input = matches[0]
            else:
                return f"Could not find a file matching: {tool_input}"

    if tool_name == "search_project_files":
        if tool_input.lower() in ["none", ""]:
            return "Search tool needs a keyword."

    return tool_function(tool_input)

def extract_search_keyword(user_message):
    stop_words = {
        "how", "does", "do", "the", "a", "an", "in", "this",
        "project", "work", "works", "what", "is", "are",
        "tell", "me", "about"
    }

    words = user_message.lower().split()

    for word in words:
        if word not in stop_words:
            return word

    return user_message

def handle_user_message(user_message):
    if user_message.startswith("multi agent "):
        request = user_message.replace("multi agent ", "", 1)

        search_keyword = extract_search_keyword(request)
        remember_working("current_task", request)
        remember_working("last_search_keyword", search_keyword)

        top_files, ai_message = multi_file_agent_answer(
            user_message=request,
            search_keyword=search_keyword
        )

        remember_working("last_files_used", top_files)

        return {
            "type": "multi_agent",
            "response": ai_message,
            "search_keyword": search_keyword,
            "files_used": top_files,
            "activity_events": [
                "tool_agent:routed request",
                "file_agent:searched project files",
                "chat_agent:generated response",
                "memory_agent:saved working memory"
            ]
        }

    messages.append({
        "role": "user",
        "content": user_message
    })

    ai_message = chat_with_memory(messages)

    messages.append({
        "role": "assistant",
        "content": ai_message
    })

    save_memory(messages)

    return {
        "type": "chat",
        "response": ai_message,
        "search_keyword": None,
        "files_used": [],
        "activity_events": [
            "chat_agent:generated response",
            "memory_agent:saved conversation"
        ]
    }

def get_user_input():
    first_line = input("You: ")

    if first_line.lower() != "multi":
        return first_line

    print("Multiline mode. Type END on its own line to finish.")

    lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        lines.append(line)

    return "\n".join(lines)

if __name__ == "__main__":
    print("Local AI Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        user_message = get_user_input()

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

            tool_input = choose_tool_input(
                user_message=request,
                chosen_tool=chosen_tool
            )

            tool_result = run_tool(
                tool_name=chosen_tool,
                tool_input=tool_input
            )

            print(f"\nCHOSEN TOOL: {chosen_tool}")
            print(f"\nTOOL INPUT: {tool_input}")

            continue

        if user_message.startswith("multi agent "):
            result = handle_user_message(user_message)

            print(f"\nSEARCH KEYWORD: {result['search_keyword']}")

            print("\nFILES USED:")
            for file in result["files_used"]:
                print(f"- {file}")

            print(f"\nMULTI-STEP AGENT RESPONSE:\n{result['response']}\n")

            continue

        command_handled = False

        if user_message.lower() in COMMANDS:
            result = COMMANDS[user_message.lower()]()

            print(f"\nRESULT:\n{result}\n")

            continue

        for command, handler in ARGUMENT_COMMANDS.items():
            if user_message.startswith(command):
                result = handler(user_message)

                print(f"\nRESULT:\n{result}\n")

                command_handled = True
                break

        if command_handled:
            continue

        if "main.py" in user_message:
            ai_message = answer_about_main_file()

            remember_working("last_search_keyword", "main.py")
            remember_working("last_files_used", ["main.py"])

            print(f"\nAI RESPONSE:\n{ai_message}\n")

            continue

        if any(word in user_message.lower() for word in AUTO_RETRIEVAL_KEYWORDS):
            matches, ai_message = answer_with_auto_retrieval(
                user_message=user_message,
                keywords=AUTO_RETRIEVAL_KEYWORDS
            )

            remember_working("last_files_used", matches)
            remember_working("last_search_keyword", user_message)

            print("\nUSING FILES:")
            for match in matches:
                print(f"- {match}")
            print()

            print(f"\nAI RESPONSE:\n{ai_message}\n")

            continue

        result = handle_user_message(user_message)

        print(f"\nAI: {result['response']}\n")