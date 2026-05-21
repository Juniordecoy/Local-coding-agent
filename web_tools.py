from file_tools import list_project_files, read_file


def get_web_files():
    files = list_project_files()

    html_files = []
    css_files = []
    js_files = []

    for file in files:
        if file.endswith(".html"):
            html_files.append(file)

        elif file.endswith(".css"):
            css_files.append(file)

        elif file.endswith(".js"):
            js_files.append(file)

    return {
        "html": html_files,
        "css": css_files,
        "js": js_files
    }

def summarize_web_structure():
    web_files = get_web_files()

    return (
        "WEBSITE STRUCTURE:\n\n"
        f"HTML controls page layout/templates: {web_files['html']}\n"
        f"CSS controls visual styling: {web_files['css']}\n"
        f"JavaScript controls browser behavior: {web_files['js']}\n"
        "\nTypical flow:\n"
        "HTML builds the page → CSS styles it → JS handles clicks/events → Python handles backend logic."
    )

def trace_frontend_connections():
    web_files = get_web_files()

    result = "FRONTEND CONNECTIONS:\n\n"

    for html_file in web_files["html"]:
        content = read_file(html_file)

        result += f"{html_file}\n"

        for css_file in web_files["css"]:
            css_name = css_file.split("\\")[-1]

            if css_name in content:
                result += f"  uses CSS: {css_file}\n"

        for js_file in web_files["js"]:
            js_name = js_file.split("\\")[-1]

            if js_name in content:
                result += f"  uses JS: {js_file}\n"

        result += "\n"

    return result

def show_web_files():
    web_files = get_web_files()

    result = "WEBSITE FILES:\n\n"

    result += "HTML FILES:\n"
    for file in web_files["html"]:
        result += f"- {file}\n"

    result += "\nCSS FILES:\n"
    for file in web_files["css"]:
        result += f"- {file}\n"

    result += "\nJS FILES:\n"
    for file in web_files["js"]:
        result += f"- {file}\n"

    return result

def summarize_python_files():
    files = list_project_files()

    python_files = []

    for file in files:
        if file.endswith(".py"):
            python_files.append(file)

    result = "PYTHON FILE SUMMARY:\n\n"

    for file in python_files:
        if file == "main.py":
            result += "- main.py = main app runner, command routing, and message handling\n"
        elif file == "ai.py":
            result += "- ai.py = AI model calls and tool choice helpers\n"
        elif file == "file_tools.py":
            result += "- file_tools.py = reading, listing, and searching project files\n"
        elif file == "memory.py":
            result += "- memory.py = long-term conversation memory storage\n"
        elif file == "working_memory.py":
            result += "- working_memory.py = short-term task/session memory\n"
        elif file == "workflows.py":
            result += "- workflows.py = higher-level multi-step agent workflows\n"
        elif file == "ui.py":
            result += "- ui.py = possible user interface or display helper file\n"
        elif file == "web_tools.py":
            result += "- web_tools.py = website/front-end analysis tools\n"
        else:
            result += f"- {file} = Python helper or test file\n"

    return result

def find_text_usage(search_text):
    files = list_project_files()

    result = f"TEXT FOUND: '{search_text}'\n\n"
    found_any = False

    for file in files:
        try:
            content = read_file(file)
            lines = content.splitlines()

            file_matches = []

            for line_number, line in enumerate(lines, start=1):
                if search_text.lower() in line.lower():
                    file_matches.append((line_number, line.strip()))

            if file_matches:
                found_any = True
                result += f"{file}\n"

                for line_number, line in file_matches:
                    result += f"  line {line_number}: {line}\n"

                result += "\n"

        except:
            pass

    if not found_any:
        return f"No files contain: {search_text}"

    return result

def find_function_usage(function_name):
    files = list_project_files()

    result = f"FUNCTION FOUND: '{function_name}'\n\n"
    found_any = False

    patterns = [
        f"def {function_name}",
        f"function {function_name}",
        f"const {function_name}",
        f"let {function_name}",
        f"var {function_name}",
        f"{function_name}("
    ]

    for file in files:
        try:
            content = read_file(file)
            lines = content.splitlines()

            file_matches = []

            for line_number, line in enumerate(lines, start=1):
                clean_line = line.strip()

                for pattern in patterns:
                    if pattern in clean_line:
                        file_matches.append((line_number, clean_line))
                        break

            if file_matches:
                found_any = True
                result += f"{file}\n"

                for line_number, line in file_matches:
                    result += f"  line {line_number}: {line}\n"

                result += "\n"

        except:
            pass

    if not found_any:
        return f"No function found matching: {function_name}"

    return result

def trace_button(button_id):
    files = list_project_files()

    result = f"BUTTON TRACE: '{button_id}'\n\n"
    found_any = False

    search_terms = [
        button_id,
        f'getElementById("{button_id}")',
        f"getElementById('{button_id}')",
        f'id="{button_id}"',
        f"id='{button_id}'",
    ]

    for file in files:
        try:
            content = read_file(file)
            lines = content.splitlines()

            file_matches = []

            for line_number, line in enumerate(lines, start=1):
                clean_line = line.strip()

                for term in search_terms:
                    if term in clean_line:
                        file_matches.append((line_number, clean_line))
                        break

            if file_matches:
                found_any = True
                result += f"{file}\n"

                for line_number, line in file_matches:
                    result += f"  line {line_number}: {line}\n"

                result += "\n"

        except:
            pass

    if not found_any:
        return f"No button found matching: {button_id}"

    return result

def trace_route(route_name):
    files = list_project_files()

    result = f"ROUTE TRACE: '{route_name}'\n\n"
    found_any = False

    search_terms = [
        f'@app.route("{route_name}"',
        f"@app.route('{route_name}'",
    ]

    for file in files:
        try:
            content = read_file(file)
            lines = content.splitlines()

            file_matches = []

            for line_number, line in enumerate(lines, start=1):
                clean_line = line.strip()

                for term in search_terms:
                    if term in clean_line:
                        file_matches.append((line_number, clean_line))
                        break

            if file_matches:
                found_any = True
                result += f"{file}\n"

                for line_number, line in file_matches:
                    result += f"  line {line_number}: {line}\n"

                result += "\n"

        except:
            pass

    if not found_any:
        return f"No route found matching: {route_name}"

    return result

def trace_endpoint(endpoint):
    files = list_project_files()

    clean_endpoint = endpoint.strip()

    if not clean_endpoint.startswith("/"):
        clean_endpoint = "/" + clean_endpoint

    result = f"ENDPOINT TRACE: '{clean_endpoint}'\n\n"
    found_any = False

    search_terms = [
        f'@app.route("{clean_endpoint}"',
        f"@app.route('{clean_endpoint}'",
        f'fetch("{clean_endpoint}"',
        f"fetch('{clean_endpoint}'",
        f'url: "{clean_endpoint}"',
        f"url: '{clean_endpoint}'",
    ]

    for file in files:
        try:
            content = read_file(file)
            lines = content.splitlines()

            file_matches = []

            for line_number, line in enumerate(lines, start=1):
                clean_line = line.strip()

                for term in search_terms:
                    if term in clean_line:
                        file_matches.append((line_number, clean_line))
                        break

            if file_matches:
                found_any = True
                result += f"{file}\n"

                for line_number, line in file_matches:
                    result += f"  line {line_number}: {line}\n"

                result += "\n"

        except:
            pass

    if not found_any:
        return f"No endpoint found matching: {clean_endpoint}"

    return result

def trace_id(element_id):
    files = list_project_files()

    result = f"ID TRACE: '{element_id}'\n\n"
    found_any = False

    search_terms = [
        element_id,
        f'id="{element_id}"',
        f"id='{element_id}'",
        f'getElementById("{element_id}")',
        f"getElementById('{element_id}')",
        f'querySelector("#{element_id}")',
        f"querySelector('#{element_id}')",
    ]

    for file in files:
        try:
            content = read_file(file)
            lines = content.splitlines()

            file_matches = []

            for line_number, line in enumerate(lines, start=1):
                clean_line = line.strip()

                for term in search_terms:
                    if term in clean_line:
                        file_matches.append((line_number, clean_line))
                        break

            if file_matches:
                found_any = True
                result += f"{file}\n"

                for line_number, line in file_matches:
                    result += f"  line {line_number}: {line}\n"

                result += "\n"

        except:
            pass

    if not found_any:
        return f"No id found matching: {element_id}"

    return result