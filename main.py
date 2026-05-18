from ai import ask_ai, chat_with_memory
from memory import load_memory, save_memory
from file_tools import read_notes, read_file, list_project_files, search_project_files, search_project_files_with_scores

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

print("Local AI Assistant")
print("Type 'exit' to quit.\n")

while True:
    user_message = input("You: ")

    if user_message.lower() == "exit":
        save_memory(messages)
        print("Memory saved. Goodbye.")
        break

    if user_message.startswith("debug search "):
        keyword = user_message.replace("debug search ", "", 1)

        matches = search_project_files_with_scores(keyword)

        print("\nDEBUG SEARCH RESULTS:")

        if matches:
            for match in matches:
                print(f"- {match['file']} | score: {match['score']}")
        else:
            print("No matching files found.")

        print()
        continue

    if user_message.startswith("search "):
        keyword = user_message.replace("search ", "", 1)

        matches = search_project_files(keyword)

        print("\nMATCHING FILES:")

        if matches:
            for match in matches:
                print(f"- {match}")
        else:
            print("No matching files found.")

        print()

        continue

    if user_message.lower() == "files":
        files = list_project_files()

        print("\nPROJECT FILES:")
        for file in files:
            print(f"- {file}")

        print()
        continue

    if user_message.lower() == "summarize project":
        files = list_project_files()

        project_context = ""

        for file in files:
            if file.endswith((".py", ".txt")):
                file_content = read_file(file)

                project_context += f"\n--- {file} ---\n"
                project_context += file_content
                project_context += "\n"

        ai_message = ask_ai(
            system_prompt=(
                "You are a careful coding tutor. "
                "Only explain the code that is actually provided."
            ),
            user_prompt=project_context
        )

        print(f"\nPROJECT SUMMARY:\n{ai_message}\n")

        continue

    if user_message.lower() == "analyze project":
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
                "You are a careful coding tutor. "
                "Only explain the code that is actually provided."
            ),
            user_prompt=project_context
        )

        print(f"\nPROJECT ANALYSIS:\n{ai_message}\n")

        continue

    if user_message.startswith("explain "):
        filename = user_message.replace("explain ", "", 1)

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

        print(f"\nCODE EXPLANATION:\n{ai_message}\n")

        continue

    if user_message.startswith("read "):
        filename = user_message.replace("read ", "", 1)

        file_content = read_file(filename)

        tool_message = (
            f"The user asked to read the file: {filename}\n\n"
            f"File contents:\n{file_content}"
        )

        ai_message = ask_ai(
            system_prompt=(
                "You are a careful coding tutor. "
                "Only explain the code that is actually provided."
            ),
            user_prompt=tool_message
        )

        print(f"\nAI FILE ANALYSIS:\n{ai_message}\n")

        continue

    if "main.py" in user_message:
        file_content = read_file("main.py")

        tool_message = (
            "The user is asking about main.py.\n\n"
            f"Filename: main.py\n\n"
            f"Actual file contents start below:\n\n"
            f"{file_content}\n\n"
            f"Actual file contents end here."
        )


        ai_message = ask_ai(
            system_prompt=(
                "You are a careful coding tutor. "
                "Only explain the code that is actually provided."
            ),
            user_prompt=tool_message
        )


        print(f"\nAI RESPONSE:\n{ai_message}\n")

        continue

    if any(word in user_message.lower() for word in AUTO_RETRIEVAL_KEYWORDS):
        matches = []

        for keyword in AUTO_RETRIEVAL_KEYWORDS:
            if keyword in user_message.lower():
                matches.extend(search_project_files(keyword))

        matches = list(dict.fromkeys(matches))
        matches = matches[:3]

        print("\nUSING FILES:")
        for match in matches:
            print(f"- {match}")
        print()

        project_context = ""

        for match in matches:
            content = read_file(match)

            project_context += f"\n--- {match} ---\n"
            project_context += content
            project_context += "\n"


        ai_message = ask_ai(
            system_prompt=(
                "You are a careful coding tutor. "
                "Only explain the code that is actually provided."
            ),
            user_prompt=project_context
        )


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