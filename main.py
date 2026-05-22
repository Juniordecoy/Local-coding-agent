from ai import ask_ai, chat_with_memory, choose_tool, choose_tool_input
from memory import load_memory, save_memory
from file_tools import (
    read_notes, read_file, list_project_files,
    search_project_files, search_project_files_with_scores
)
from workflows import (
    explain_file, summarize_project, analyze_project,
    analyze_file, answer_about_main_file, answer_with_auto_retrieval,
    multi_file_agent_answer
)
from working_memory import remember_working, get_working, clear_working
from web_tools import (
    show_web_files, summarize_web_structure,
    trace_frontend_connections, summarize_python_files,
    project_file_counts, largest_files
)
from command_handlers import (
    find_usage_command, find_function_command, trace_button_command, trace_route_command, trace_endpoint_command,
    trace_id_command, explain_file_role_command, file_complexity_command, list_routes_command, route_summary_command,
    route_detail_command, route_full_command, route_templates_command, template_routes_command, template_extends_command,
    template_blocks_command, template_forms_command, template_inputs_command, template_required_command,
    template_hidden_command, template_honeypot_command, route_form_map_command, route_fields_command, route_emails_command,
    route_redirects_command, route_files_command, route_security_command, route_warnings_command, route_report_command,
    project_architecture_command, project_health_command, project_focus_command, or_routes_command, or_report_command,
    or_templates_detail_command, or_form_fields_command, or_required_fields_command, or_route_reports_command,
    template_form_actions_command, form_action_route_command, template_action_map_command, draft_template_command,
    draft_route_command, draft_css_command, draft_js_command, draft_page_bundle_command, draft_ai_page_command,
    draft_ai_html_command, review_draft_command,
)



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

def show_working_memory():
    return {
        "current_task": get_working("current_task"),
        "last_search_keyword": get_working("last_search_keyword"),
        "last_files_used": get_working("last_files_used"),
    }

def explain_last_file():
    files = get_working("last_files_used")

    if not files:
        return "No recent files found in working memory. Run a multi agent question first."

    last_file = files[0]

    print(f"\nDEBUG - explaining file: {last_file}")

    return explain_file(last_file)

def explain_file_by_number(file_number):
    files = get_working("last_files_used")

    if not files:
        return "No recent files found in working memory. Run a multi agent question first."

    index = file_number - 1

    if index < 0 or index >= len(files):
        return f"That file number is not available. Last files used: {files}"

    selected_file = files[index]

    print(f"\nDEBUG - explaining file: {selected_file}")

    return explain_file(selected_file)

def explain_first_file():
    return explain_file_by_number(1)


def explain_second_file():
    return explain_file_by_number(2)


def explain_third_file():
    return explain_file_by_number(3)

def clear_working_memory():
    clear_working()

    return "Working memory cleared."

ARGUMENT_COMMANDS = {
    "debug search ": debug_search_command, "explain file ": explain_file_role_command, "explain ": explain_command,
    "read ": read_command, "search ": search_command, "find usage ": find_usage_command, "find function ": find_function_command,
    "trace button ": trace_button_command, "trace route ": trace_route_command, "trace endpoint ": trace_endpoint_command,
    "trace id ": trace_id_command, "file complexity ": file_complexity_command, "list routes ": list_routes_command,
    "route summary ": route_summary_command, "route detail ": route_detail_command, "route full ": route_full_command,
    "route templates ": route_templates_command, "template routes ": template_routes_command, "template extends ": template_extends_command,
    "template blocks ": template_blocks_command, "template forms ": template_forms_command, "template inputs ": template_inputs_command,
    "template required ": template_required_command, "template hidden ": template_hidden_command, "template honeypot ": template_honeypot_command,
    "route form map ": route_form_map_command, "route fields ": route_fields_command, "route emails ": route_emails_command,
    "route redirects ": route_redirects_command, "route files ": route_files_command, "route security ": route_security_command,
    "route warnings ": route_warnings_command, "route report ": route_report_command, "or routes ": or_routes_command,
    "or report ": or_report_command, "or route reports ": or_route_reports_command, "template form actions ": template_form_actions_command,
    "form action route ": form_action_route_command, "template action map ": template_action_map_command, "draft template ": draft_template_command,
    "draft route ": draft_route_command, "draft css ": draft_css_command, "draft js ": draft_js_command, "draft page bundle ": draft_page_bundle_command,
    "draft ai page ": draft_ai_page_command, "draft ai html ": draft_ai_html_command, "review draft ": review_draft_command,
}

TOOLS = {
    "read_file": read_file,
    "list_project_files": list_project_files,
    "search_project_files": search_project_files,
}

COMMANDS = {
    "summarize project": summarize_project, "analyze project": analyze_project, "files": show_files, "working memory": show_working_memory,
    "explain last file": explain_last_file, "explain first file": explain_first_file, "explain second file": explain_second_file,
    "explain third file": explain_third_file, "clear working memory": clear_working_memory, "web files": show_web_files,
    "web summary": summarize_web_structure, "frontend connections": trace_frontend_connections, "python files": summarize_python_files,
    "project file counts": project_file_counts, "largest files": largest_files, "project architecture": project_architecture_command,
    "project health": project_health_command, "project focus": project_focus_command, "or templates detail": or_templates_detail_command,
    "or form fields": or_form_fields_command, "or required fields": or_required_fields_command,
}

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

if __name__ == "__main__":
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