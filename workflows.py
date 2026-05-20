from ai import ask_ai
from file_tools import read_file, list_project_files, search_project_files


def build_project_context(files):
    project_context = ""

    for file in files:
        if file.endswith((".py", ".txt")):
            file_content = read_file(file)

            project_context += f"\n--- {file} ---\n"
            project_context += file_content
            project_context += "\n"

    return project_context


def explain_file(filename):
    file_content = read_file(filename)

    tool_message = (
        f"Filename: {filename}\n\n"
        "Explain this file in a focused, beginner-friendly way.\n"
        "Do not invent anything not shown in the file.\n\n"
        f"File contents:\n{file_content}"
    )

    ai_message = ask_ai(
        system_prompt=(
            "You are a careful coding tutor. "
            "Only explain the code that is actually provided."
        ),
        user_prompt=tool_message
    )

    return ai_message

def summarize_project():
    files = list_project_files()
    project_context = build_project_context(files)

    ai_message = ask_ai(
        system_prompt=(
            "You are a senior Python coding assistant. "
            "Summarize this local project clearly and concisely. "
            "Explain the architecture, major components, and overall purpose. "
            "Only use the provided files."
        ),
        user_prompt=project_context
    )

    return ai_message

def analyze_project():
    files = list_project_files()

    project_context = "Project Files and Contents:\n\n"

    for file in files:
        if file.endswith((".py", ".txt")):
            file_content = read_file(file)

            project_context += f"--- {file} ---\n"
            project_context += file_content
            project_context += "\n\n"

    ai_message = ask_ai(
        system_prompt=(
            "You are a coding assistant analyzing a local Python project. "
            "Based only on the provided files, explain what the project does."
        ),
        user_prompt=project_context
    )

    return ai_message

def analyze_file(filename):
    file_content = read_file(filename)

    tool_message = (
        f"Filename: {filename}\n\n"
        "Analyze the actual file contents below. "
        "Do not explain how to read files in Python. "
        "Only summarize or explain what the provided file contains.\n\n"
        f"File contents:\n{file_content}"
    )

    ai_message = ask_ai(
        system_prompt=(
            "You are a careful coding tutor. "
            "Only explain the code that is actually provided."
        ),
        user_prompt=tool_message
    )

    return ai_message

def answer_about_main_file():
    file_content = read_file("main.py")

    tool_message = (
        "The user is asking about main.py.\n\n"
        "Filename: main.py\n\n"
        "Actual file contents start below:\n\n"
        f"{file_content}\n\n"
        "Actual file contents end here."
    )

    ai_message = ask_ai(
        system_prompt=(
            "You are a careful coding tutor. "
            "Only explain the code that is actually provided."
        ),
        user_prompt=tool_message
    )

    return ai_message

def answer_with_auto_retrieval(user_message, keywords):
    matches = []

    for keyword in keywords:
        if keyword in user_message.lower():
            matches.extend(search_project_files(keyword))

    matches = list(dict.fromkeys(matches))
    matches = matches[:3]

    project_context = ""

    for match in matches:
        content = read_file(match)

        project_context += f"\n--- {match} ---\n"
        project_context += content
        project_context += "\n"

    ai_message = ask_ai(
        system_prompt=(
            "You are a careful coding tutor. "
            "Only answer using the provided project files."
        ),
        user_prompt=(
            f"User question:\n{user_message}\n\n"
            f"Relevant project files:\n{project_context}"
        )
    )

    return matches, ai_message

def multi_file_agent_answer(user_message, search_keyword):
    search_results = search_project_files(search_keyword)

    if not search_results:
        return [], "No files found."

    top_files = search_results[:2]

    combined_context = ""

    for file in top_files:
        file_content = read_file(file)

        combined_context += f"\n--- {file} ---\n"
        combined_context += file_content
        combined_context += "\n"

    ai_message = ask_ai(
        system_prompt=(
            "You are a careful coding assistant. "
            "Answer the user's question using only the provided project files. "
            "Do not explain general computer science concepts unless the files discuss them. "
            "Focus on what this project's code is doing."
        ),
        user_prompt=(
            f"User question:\n{user_message}\n\n"
            f"Files used: {top_files}\n\n"
            f"Combined file contents:\n{combined_context}"
        )
    )

    return top_files, ai_message