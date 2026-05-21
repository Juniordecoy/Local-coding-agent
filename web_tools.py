import re
from file_tools import list_project_files, read_file
from project_config import TARGET_PROJECT_DIR


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

def project_file_counts():
    files = list_project_files()

    counts = {
        "Python": 0,
        "HTML": 0,
        "CSS": 0,
        "JavaScript": 0,
        "JSON": 0,
        "Text": 0,
        "Other": 0,
    }

    for file in files:
        if file.endswith(".py"):
            counts["Python"] += 1
        elif file.endswith(".html"):
            counts["HTML"] += 1
        elif file.endswith(".css"):
            counts["CSS"] += 1
        elif file.endswith(".js"):
            counts["JavaScript"] += 1
        elif file.endswith(".json"):
            counts["JSON"] += 1
        elif file.endswith(".txt"):
            counts["Text"] += 1
        else:
            counts["Other"] += 1

    result = "PROJECT FILE COUNTS:\n\n"

    for file_type, count in counts.items():
        result += f"{file_type}: {count}\n"

    return result

def largest_files(limit=10):
    files = list_project_files()

    file_sizes = []

    for file in files:
        try:
            full_path = TARGET_PROJECT_DIR / file

            size = full_path.stat().st_size

            file_sizes.append({
                "file": file,
                "size": size
            })

        except:
            pass

    file_sizes.sort(key=lambda item: item["size"], reverse=True)

    result = f"LARGEST FILES (Top {limit}):\n\n"

    for item in file_sizes[:limit]:
        size_kb = round(item["size"] / 1024, 2)

        result += f"- {item['file']} ({size_kb} KB)\n"

    return result

def explain_file_role(filename):
    content = read_file(filename)
    lower_file = filename.lower()

    if content == "File not found.":
        return f"File not found: {filename}"

    line_count = len(content.splitlines())

    if lower_file.endswith(".py"):
        file_type = "Python backend/helper file"
    elif lower_file.endswith(".html"):
        file_type = "HTML template/page file"
    elif lower_file.endswith(".css"):
        file_type = "CSS styling file"
    elif lower_file.endswith(".js"):
        file_type = "JavaScript browser behavior file"
    elif lower_file.endswith(".json"):
        file_type = "JSON data/config file"
    else:
        file_type = "General project file"

    result = f"FILE ROLE: {filename}\n\n"
    result += f"Type: {file_type}\n"
    result += f"Lines: {line_count}\n\n"

    if "@app.route" in content:
        result += "- Contains Flask routes.\n"

    if "def " in content:
        result += "- Contains Python functions.\n"

    if "render_template" in content:
        result += "- Renders HTML templates.\n"

    if "request.form" in content or "request.files" in content:
        result += "- Handles form submissions or uploaded files.\n"

    if "send_form_email" in content or "resend" in content.lower():
        result += "- Appears connected to email sending.\n"

    if "{% extends" in content:
        result += "- Extends a base Jinja template.\n"

    if "{% block" in content:
        result += "- Uses Jinja template blocks.\n"

    if "<form" in content:
        result += "- Contains an HTML form.\n"

    if "fetch(" in content:
        result += "- Uses frontend fetch/API calls.\n"

    if "addEventListener" in content:
        result += "- Contains JavaScript event listeners.\n"

    if result.endswith("\n\n"):
        result += "No obvious role markers found.\n"

    return result

def file_complexity(filename):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    lower_file = filename.lower()

    line_count = len(lines)
    function_count = content.count("def ")
    route_count = content.count("@app.route")
    import_count = content.count("import ")

    result = f"FILE COMPLEXITY: {filename}\n\n"
    result += f"Lines: {line_count}\n"

    if lower_file.endswith(".py"):
        result += f"Functions: {function_count}\n"
        result += f"Routes: {route_count}\n"
        result += f"Imports: {import_count}\n"

    if line_count > 1000:
        complexity = "HIGH"
    elif line_count > 300:
        complexity = "MEDIUM"
    else:
        complexity = "LOW"

    result += f"\nComplexity: {complexity}\n"

    return result

def list_routes(filename):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    routes = []

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if clean_line.startswith("@app.route"):
            routes.append((line_number, clean_line))

    if not routes:
        return f"No Flask routes found in: {filename}"

    result = f"FLASK ROUTES: {filename}\n\n"

    for line_number, route in routes:
        result += f"line {line_number}: {route}\n"

    result += f"\nTotal Routes: {len(routes)}"

    return result

def route_summary(filename):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    categories = {
        "Public / Content Pages": [],
        "Forms": [],
        "OR / Logistics": [],
        "Admin": [],
        "Downloads / Files": [],
        "Dynamic Routes": [],
    }

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if not clean_line.startswith("@app.route"):
            continue

        lower_line = clean_line.lower()

        route_item = f"line {line_number}: {clean_line}"

        if "<" in clean_line and ">" in clean_line:
            categories["Dynamic Routes"].append(route_item)
        elif "admin" in lower_line:
            categories["Admin"].append(route_item)
        elif "download" in lower_line or "file" in lower_line or "pdf" in lower_line:
            categories["Downloads / Files"].append(route_item)
        elif "/or-" in lower_line or "/or" in lower_line or "/OR" in clean_line:
            categories["OR / Logistics"].append(route_item)
        elif 'methods=["get", "post"]' in lower_line or "methods=['get', 'post']" in lower_line:
            categories["Forms"].append(route_item)
        else:
            categories["Public / Content Pages"].append(route_item)

    result = f"ROUTE SUMMARY: {filename}\n\n"

    for category, routes in categories.items():
        result += f"{category}: {len(routes)}\n"

        for route in routes:
            result += f"  {route}\n"

        result += "\n"

    return result

def route_detail(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            result = f"ROUTE DETAIL: {route_name}\n\n"
            result += f"Route Line:\n{clean_line}\n\n"

            preview_lines = []

            for next_index in range(index + 1, min(index + 25, len(lines))):
                next_line = lines[next_index]

                if next_index > index + 1 and next_line.strip().startswith("@app.route"):
                    break

                preview_lines.append(next_line)

            result += "Code Preview:\n"

            for preview_line in preview_lines:
                result += preview_line + "\n"

            return result

    return f"Route not found: {route_name}"

def route_full(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            result = f"FULL ROUTE: {route_name}\n\n"

            for next_index in range(index, len(lines)):
                next_line = lines[next_index]

                if next_index > index and next_line.strip().startswith("@app.route"):
                    break

                result += next_line + "\n"

            return result

    return f"Route not found: {route_name}"

def route_templates(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            templates = []
            seen_templates = set()

            for next_index in range(index, len(lines)):
                next_line = lines[next_index].strip()

                if next_index > index and next_line.startswith("@app.route"):
                    break

                if "render_template(" in next_line or "render_form(" in next_line:
                    render_block = next_line

                    for look_ahead_index in range(next_index + 1, min(next_index + 6, len(lines))):
                        look_ahead_line = lines[look_ahead_index].strip()
                        render_block += " " + look_ahead_line

                        if ")" in look_ahead_line:
                            break

                    if render_block not in seen_templates:
                        templates.append(render_block)
                        seen_templates.add(render_block)

            result = f"ROUTE TEMPLATES: {route_name}\n\n"

            if templates:
                for template in templates:
                    result += template + "\n"
            else:
                result += "No templates found."

            return result

    return f"Route not found: {route_name}"

def template_routes(filename, template_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    matches = []
    seen_routes = set()
    current_route = None

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if clean_line.startswith("@app.route"):
            current_route = f"line {line_number}: {clean_line}"

        if template_name in clean_line and current_route:
            if current_route not in seen_routes:
                matches.append(current_route)
                seen_routes.add(current_route)

    if not matches:
        return f"No routes found using template: {template_name}"

    result = f"TEMPLATE ROUTES: {template_name}\n\n"

    for match in matches:
        result += match + "\n"

    return result

def template_extends(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()

    for line in lines:
        clean_line = line.strip()

        if clean_line.startswith("{% extends"):
            return (
                f"TEMPLATE EXTENDS: {template_file}\n\n"
                f"{clean_line}"
            )

    return f"No base template found in: {template_file}"

def template_blocks(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()

    blocks = []

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if clean_line.startswith("{% block"):
            blocks.append((line_number, clean_line))

    if not blocks:
        return f"No Jinja blocks found in: {template_file}"

    result = f"TEMPLATE BLOCKS: {template_file}\n\n"

    for line_number, block in blocks:
        result += f"line {line_number}: {block}\n"

    return result

def template_forms(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()
    forms = []

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if "<form" in clean_line or "</form>" in clean_line:
            forms.append((line_number, clean_line))

    if not forms:
        return f"No form tags found in: {template_file}"

    result = f"TEMPLATE FORMS: {template_file}\n\n"

    for line_number, form_line in forms:
        result += f"line {line_number}: {form_line}\n"

    return result

def template_inputs(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()

    inputs = []

    input_tags = [
        "<input",
        "<textarea",
        "<select",
    ]

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        for tag in input_tags:
            if tag in clean_line:
                inputs.append((line_number, clean_line))
                break

    if not inputs:
        return f"No form inputs found in: {template_file}"

    result = f"TEMPLATE INPUTS: {template_file}\n\n"

    for line_number, input_line in inputs:
        result += f"line {line_number}: {input_line}\n"

    return result

def template_required(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()

    required_fields = []

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if (
            ("<input" in clean_line or "<textarea" in clean_line or "<select" in clean_line)
            and "required" in clean_line
        ):
            required_fields.append((line_number, clean_line))

    if not required_fields:
        return f"No required fields found in: {template_file}"

    result = f"REQUIRED FIELDS: {template_file}\n\n"

    for line_number, field_line in required_fields:
        result += f"line {line_number}: {field_line}\n"

    return result

def template_hidden(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()

    hidden_fields = []

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if '<input' in clean_line and 'type="hidden"' in clean_line:
            hidden_fields.append((line_number, clean_line))

    if not hidden_fields:
        return f"No hidden inputs found in: {template_file}"

    result = f"HIDDEN INPUTS: {template_file}\n\n"

    for line_number, field_line in hidden_fields:
        result += f"line {line_number}: {field_line}\n"

    return result

def template_honeypot(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()

    honeypot_matches = []

    honeypot_terms = [
        "do_not_fill",
        "honeypot",
        "company",
    ]

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip().lower()

        for term in honeypot_terms:
            if term in clean_line:
                honeypot_matches.append((line_number, line.strip()))
                break

    if not honeypot_matches:
        return f"No honeypot fields found in: {template_file}"

    result = f"HONEYPOT FIELDS: {template_file}\n\n"

    for line_number, field_line in honeypot_matches:
        result += f"line {line_number}: {field_line}\n"

    return result

def route_form_map(filename, route_name):
    route_info = route_detail(filename, route_name)

    if "Route not found" in route_info:
        return route_info

    template_info = route_templates(filename, route_name)

    result = f"ROUTE FORM MAP: {route_name}\n\n"

    result += route_info + "\n\n"
    result += template_info + "\n\n"

    template_name = None

    for line in template_info.splitlines():
        if "render_form(" in line or "render_template(" in line:
            start = line.find('"')
            end = line.rfind('"')

            if start != -1 and end != -1 and end > start:
                template_name = line[start + 1:end]
                break

    if not template_name:
        result += "No template found."
        return result

    template_path = f"doit_portal\\templates\\{template_name}"

    result += template_forms(template_path) + "\n\n"
    result += template_required(template_path) + "\n\n"
    result += template_hidden(template_path) + "\n\n"
    result += template_honeypot(template_path)

    return result

def route_fields(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    route_lines = []

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            for next_index in range(index, len(lines)):
                next_line = lines[next_index]

                if next_index > index and next_line.strip().startswith("@app.route"):
                    break

                route_lines.append(next_line)

            break

    if not route_lines:
        return f"Route not found: {route_name}"

    route_text = "\n".join(route_lines)
    uses_form_to_dict = "request.form.to_dict()" in route_text

    backend_fields = set(re.findall(r'form_data\.get\(["\']([^"\']+)["\']\)', route_text))
    backend_fields.update(re.findall(r'request\.form\.get\(["\']([^"\']+)["\']\)', route_text))
    backend_files = set(re.findall(r'request\.files\.get\(["\']([^"\']+)["\']\)', route_text))

    template_info = route_templates(filename, route_name)

    template_name = None

    for line in template_info.splitlines():
        if "render_form(" in line or "render_template(" in line:
            start = line.find('"')
            end = line.rfind('"')

            if start != -1 and end != -1 and end > start:
                template_name = line[start + 1:end]
                break

    if not template_name:
        return f"No template found for route: {route_name}"

    template_path = f"doit_portal\\templates\\{template_name}"
    template_content = read_file(template_path)

    if template_content == "File not found.":
        return f"Template not found: {template_path}"

    template_fields = set(re.findall(r'name=["\']([^"\']+)["\']', template_content))

    result = f"ROUTE FIELDS: {route_name}\n\n"
    result += f"Template: {template_path}\n\n"

    result += "Backend form_data/request.form fields:\n"
    for field in sorted(backend_fields):
        result += f"- {field}\n"

    result += "\nBackend request.files fields:\n"
    for field in sorted(backend_files):
        result += f"- {field}\n"

    result += "\nTemplate name= fields:\n"
    for field in sorted(template_fields):
        result += f"- {field}\n"

    missing_in_template = (backend_fields | backend_files) - template_fields
    unused_in_backend = template_fields - (backend_fields | backend_files)

    result += "\nBackend fields missing from template:\n"
    if missing_in_template:
        for field in sorted(missing_in_template):
            result += f"- {field}\n"
    else:
        result += "- None\n"

    result += "\nTemplate fields not directly read in backend:\n"
    if unused_in_backend:
        for field in sorted(unused_in_backend):
            result += f"- {field}\n"
    else:
        result += "- None\n"

    if uses_form_to_dict:
        result += (
            "\nNote:\n"
            "- This route uses request.form.to_dict(), so template fields may still be captured "
            "even if they are not individually read with form_data.get(...).\n"
        )

    return result

def route_emails(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    route_lines = []

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            for next_index in range(index, len(lines)):
                next_line = lines[next_index]

                if next_index > index and next_line.strip().startswith("@app.route"):
                    break

                route_lines.append((next_index + 1, next_line))

            break

    if not route_lines:
        return f"Route not found: {route_name}"

    email_terms = [
        "send_form_email",
        "to_email",
        "FORM_EMAIL_MAP",
        "subject=",
        "submitter_email",
        "submitter_name",
    ]

    matches = []

    for line_number, line in route_lines:
        clean_line = line.strip()

        for term in email_terms:
            if term in clean_line:
                matches.append((line_number, clean_line))
                break

    if not matches:
        return f"No email-related lines found in route: {route_name}"

    result = f"ROUTE EMAILS: {route_name}\n\n"

    for line_number, email_line in matches:
        result += f"line {line_number}: {email_line}\n"

    return result

def route_redirects(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    route_lines = []

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            for next_index in range(index, len(lines)):
                next_line = lines[next_index]

                if next_index > index and next_line.strip().startswith("@app.route"):
                    break

                route_lines.append((next_index + 1, next_line))

            break

    if not route_lines:
        return f"Route not found: {route_name}"

    terms = [
        "redirect(",
        "url_for(",
        "flash(",
        "return render",
    ]

    matches = []

    for line_number, line in route_lines:
        clean_line = line.strip()

        for term in terms:
            if term in clean_line:
                matches.append((line_number, clean_line))
                break

    if not matches:
        return f"No redirect/render/flash lines found in route: {route_name}"

    result = f"ROUTE REDIRECTS / RESPONSES: {route_name}\n\n"

    for line_number, match_line in matches:
        result += f"line {line_number}: {match_line}\n"

    return result

def route_files(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    route_lines = []

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            for next_index in range(index, len(lines)):
                next_line = lines[next_index]

                if next_index > index and next_line.strip().startswith("@app.route"):
                    break

                route_lines.append((next_index + 1, next_line))

            break

    if not route_lines:
        return f"Route not found: {route_name}"

    terms = [
        "request.files",
        "save_uploaded_file",
        "UPLOAD",
        "FOLDER",
        "filename",
        "attachments",
    ]

    matches = []

    for line_number, line in route_lines:
        clean_line = line.strip()

        for term in terms:
            if term in clean_line:
                matches.append((line_number, clean_line))
                break

    if not matches:
        return f"No file-related lines found in route: {route_name}"

    result = f"ROUTE FILES: {route_name}\n\n"

    for line_number, match_line in matches:
        result += f"line {line_number}: {match_line}\n"

    return result

def route_security(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    route_lines = []

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            for next_index in range(index, len(lines)):
                next_line = lines[next_index]

                if next_index > index and next_line.strip().startswith("@app.route"):
                    break

                route_lines.append((next_index + 1, next_line))

            break

    if not route_lines:
        return f"Route not found: {route_name}"

    security_terms = [
        "do_not_fill",
        "honeypot",
        "blocked",
        "is_blocked_email",
        "security",
        "RECENT_",
        "submission_id",
        "session",
        "login",
        "auth",
        "password",
        "csrf",
        "limit",
    ]

    matches = []

    for line_number, line in route_lines:
        clean_line = line.strip()

        for term in security_terms:
            if term.lower() in clean_line.lower():
                matches.append((line_number, clean_line))
                break

    if not matches:
        return f"No security/protection logic found in route: {route_name}"

    result = f"ROUTE SECURITY / PROTECTION: {route_name}\n\n"

    for line_number, match_line in matches:
        result += f"line {line_number}: {match_line}\n"

    return result

def route_warnings(filename, route_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    route_lines = []

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("@app.route") and route_name in clean_line:
            for next_index in range(index, len(lines)):
                next_line = lines[next_index]

                if next_index > index and next_line.strip().startswith("@app.route"):
                    break

                route_lines.append((next_index + 1, next_line))

            break

    if not route_lines:
        return f"Route not found: {route_name}"

    warnings = []
    route_text = "\n".join(line for _, line in route_lines)
    route_line_count = len(route_lines)

    if route_line_count > 100:
        warnings.append(f"Long route: {route_line_count} lines. Consider reviewing for cleanup/refactor.")

    if "send_form_email" in route_text:
        warnings.append("Sends email. Review email subject, recipients, attachments, and failure handling.")

    if "request.files" in route_text:
        warnings.append("Handles file uploads. Review file validation, size limits, storage folder, and cleanup.")

    if "request.form.to_dict()" in route_text:
        warnings.append("Uses request.form.to_dict(). Most fields may be captured even if not individually referenced.")

    if "RECENT_" in route_text or "submission_id" in route_text:
        warnings.append("Has duplicate-submit/protection logic. Review for duplicate or stale entries.")

    if "do_not_fill" not in route_text and "honeypot" not in route_text:
        warnings.append("No obvious honeypot check found in route code.")

    seen_lines = set()
    duplicate_lines = []
    duplicate_watch_terms = [
        " = ",
        ".append(",
        ".update(",
        ".add(",
        "RECENT_",
    ]

    for line_number, line in route_lines:
        clean_line = line.strip()

        if not clean_line or clean_line.startswith("#"):
            continue

        should_check_duplicate = any(term in clean_line for term in duplicate_watch_terms)

        if not should_check_duplicate:
            continue

        if clean_line in seen_lines:
            duplicate_lines.append((line_number, clean_line))
        else:
            seen_lines.add(clean_line)

    result = f"ROUTE WARNINGS: {route_name}\n\n"

    if warnings:
        for warning in warnings:
            result += f"- {warning}\n"
    else:
        result += "- No major warnings found.\n"

    if duplicate_lines:
        result += "\nDuplicate-looking lines:\n"
        for line_number, duplicate_line in duplicate_lines:
            result += f"line {line_number}: {duplicate_line}\n"

    return result

def route_report(filename, route_name):
    result = f"ROUTE REPORT: {route_name}\n\n"

    result += route_detail(filename, route_name) + "\n\n"
    result += route_templates(filename, route_name) + "\n\n"
    result += route_fields(filename, route_name) + "\n\n"
    result += route_emails(filename, route_name) + "\n\n"
    result += route_files(filename, route_name) + "\n\n"
    result += route_redirects(filename, route_name) + "\n\n"
    result += route_security(filename, route_name) + "\n\n"
    result += route_warnings(filename, route_name)

    return result

def project_architecture():
    result = "PROJECT ARCHITECTURE\n\n"

    result += "BACKEND:\n"
    result += "- doit_portal/app.py = Main Flask application\n"
    result += "- doit_portal/helpers.py = Shared helper utilities\n"
    result += "- doit_portal/custom_form_helpers.py = Form-related helper logic\n\n"

    result += "FRONTEND:\n"
    result += "- doit_portal/templates/ = Jinja HTML templates\n"
    result += "- doit_portal/static/css/style.css = Main stylesheet\n"
    result += "- doit_portal/static/js/or_area.js = OR dashboard JavaScript\n\n"

    result += "FORM / EMAIL SYSTEM:\n"
    result += "- Flask routes handle forms and uploads\n"
    result += "- send_form_email() handles outgoing emails\n"
    result += "- FORM_EMAIL_MAP controls recipients\n"
    result += "- PDF generation exists for some forms\n\n"

    result += "UPLOADS / FILES:\n"
    result += "- Posting photos uploads\n"
    result += "- UCR uploads\n"
    result += "- PDF merge/download tools\n"
    result += "- File cleanup logic exists\n\n"

    result += "OR / LOGISTICS SYSTEM:\n"
    result += "- OR Dashboard\n"
    result += "- OR Calendar\n"
    result += "- OR Codes\n"
    result += "- OR Units\n"
    result += "- JSON-based scheduling/storage system\n\n"

    result += "ADMIN / LOGGING:\n"
    result += "- Admin dashboard\n"
    result += "- CSV exports\n"
    result += "- Security logs\n"
    result += "- Quiz logs\n"
    result += "- Accident report logs\n\n"

    result += "AI INSPECTION LAYER:\n"
    result += "- Route tracing\n"
    result += "- Template tracing\n"
    result += "- Form inspection\n"
    result += "- Email tracing\n"
    result += "- Warning detection\n"

    return result

def project_health():
    result = "PROJECT HEALTH REPORT\n\n"

    # File counts
    result += project_file_counts() + "\n\n"

    # Largest files
    result += largest_files() + "\n\n"

    # Main app complexity
    result += file_complexity("doit_portal\\app.py") + "\n\n"

    # Route summary
    result += route_summary("doit_portal\\app.py") + "\n\n"

    # Basic health observations
    result += "HEALTH OBSERVATIONS:\n"

    app_complexity = file_complexity("doit_portal\\app.py")

    if "Complexity: HIGH" in app_complexity:
        result += "- Main Flask app is becoming large. Consider future modularization.\n"

    result += "- Large monolithic route files may become harder to maintain.\n"
    result += "- Inspection tooling is growing well.\n"
    result += "- OR system architecture is beginning to separate logically.\n"
    result += "- Form/email/upload systems are heavily interconnected.\n"

    return result

def project_focus():
    result = "PROJECT FOCUS\n\n"

    result += "CURRENT STRONG AREA:\n"
    result += "- Inspection tools are becoming strong.\n"
    result += "- Route/template/form tracing is working.\n"
    result += "- Project health reporting is working.\n\n"

    result += "NEXT BEST FOCUS:\n"
    result += "- Improve OR section safely.\n"
    result += "- Use route reports before editing routes.\n"
    result += "- Build write/patch tools only after review tools are stable.\n\n"

    result += "WATCH AREAS:\n"
    result += "- app.py is large and route-heavy.\n"
    result += "- style.css is large and global.\n"
    result += "- Form/email/upload routes need careful edits.\n\n"

    result += "RECOMMENDED PATH:\n"
    result += "1. Keep improving route/template inspection.\n"
    result += "2. Add safe patch preview tools.\n"
    result += "3. Use agent to help build OR features.\n"
    result += "4. Add Excel/data agent later.\n"

    return result

def or_routes(filename):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    matches = []

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()
        lower_line = clean_line.lower()

        if clean_line.startswith("@app.route") and (
            "/or" in lower_line or "/OR" in clean_line
        ):
            matches.append((line_number, clean_line))

    if not matches:
        return f"No OR routes found in: {filename}"

    result = f"OR ROUTES: {filename}\n\n"

    for line_number, route_line in matches:
        result += f"line {line_number}: {route_line}\n"

    result += f"\nTotal OR Routes: {len(matches)}"

    return result

def or_report(filename):
    result = "OR / LOGISTICS REPORT\n\n"

    result += or_routes(filename) + "\n\n"

    result += "OR TEMPLATES:\n"
    or_template_keywords = [
        "or_",
        "or-",
    ]

    files = list_project_files()

    for file in files:
        lower_file = file.lower()

        if lower_file.endswith(".html") and "\\or_" in lower_file:
            result += f"- {file}\n"

    result += "\nOR STATIC FILES:\n"

    for file in files:
        lower_file = file.lower()

        if "or" in lower_file and (lower_file.endswith(".js") or lower_file.endswith(".css")):
            result += f"- {file}\n"

    result += "\nOR FOCUS NOTES:\n"
    result += "- OR has its own route group.\n"
    result += "- OR has dedicated templates.\n"
    result += "- OR has dedicated JavaScript behavior.\n"
    result += "- This section is a strong candidate for future modularization.\n"

    return result

def or_templates_detail():
    files = list_project_files()

    or_templates = []

    for file in files:
        lower_file = file.lower()

        if lower_file.endswith(".html") and "\\or_" in lower_file:
            or_templates.append(file)

    if not or_templates:
        return "No OR templates found."

    result = "OR TEMPLATE DETAILS\n\n"

    for template in or_templates:
        result += f"{template}\n"

        result += template_extends(template) + "\n"
        result += template_blocks(template) + "\n"
        result += template_forms(template) + "\n"

        result += "\n"

    return result

def or_form_fields():
    files = list_project_files()

    or_templates = []

    for file in files:
        lower_file = file.lower()

        if lower_file.endswith(".html") and "\\or_" in lower_file:
            or_templates.append(file)

    if not or_templates:
        return "No OR templates found."

    result = "OR FORM FIELDS\n\n"

    for template in or_templates:
        inputs_info = template_inputs(template)

        if "No form inputs found" not in inputs_info:
            result += inputs_info + "\n\n"

    return result

def or_required_fields():
    files = list_project_files()

    or_templates = []

    for file in files:
        lower_file = file.lower()

        if lower_file.endswith(".html") and "\\or_" in lower_file:
            or_templates.append(file)

    if not or_templates:
        return "No OR templates found."

    result = "OR REQUIRED FIELDS\n\n"

    for template in or_templates:
        required_info = template_required(template)

        if "No required fields found" not in required_info:
            result += required_info + "\n\n"

    return result

def or_route_reports(filename):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()
    routes = []

    for line in lines:
        clean_line = line.strip()
        lower_line = clean_line.lower()

        if clean_line.startswith("@app.route") and (
            "/or" in lower_line or "/OR" in clean_line
        ):
            start = clean_line.find("(")
            end = clean_line.find(",", start)

            if end == -1:
                end = clean_line.find(")", start)

            route_text = clean_line[start + 1:end].strip().strip('"').strip("'")
            routes.append(route_text)

    if not routes:
        return f"No OR routes found in: {filename}"

    result = "OR ROUTE REPORTS\n\n"

    for route in routes:
        result += route_report(filename, route)
        result += "\n" + ("=" * 60) + "\n\n"

    return result

def template_form_actions(template_file):
    content = read_file(template_file)

    if content == "File not found.":
        return f"File not found: {template_file}"

    lines = content.splitlines()
    actions = []

    for line_number, line in enumerate(lines, start=1):
        clean_line = line.strip()

        if "<form" in clean_line and "action=" in clean_line:
            actions.append((line_number, clean_line))

    if not actions:
        return f"No form actions found in: {template_file}"

    result = f"TEMPLATE FORM ACTIONS: {template_file}\n\n"

    for line_number, action_line in actions:
        result += f"line {line_number}: {action_line}\n"

    return result

def form_action_route(filename, endpoint_name):
    content = read_file(filename)

    if content == "File not found.":
        return f"File not found: {filename}"

    lines = content.splitlines()

    matches = []

    for index, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.startswith("def ") and clean_line.startswith(f"def {endpoint_name}("):
            # Look upward for the route decorator
            for back_index in range(index - 1, max(index - 5, -1), -1):
                back_line = lines[back_index].strip()

                if back_line.startswith("@app.route"):
                    matches.append((back_index + 1, back_line, index + 1, clean_line))
                    break

    if not matches:
        return f"No route function found matching endpoint: {endpoint_name}"

    result = f"FORM ACTION ROUTE: {endpoint_name}\n\n"

    for route_line_number, route_line, function_line_number, function_line in matches:
        result += f"line {route_line_number}: {route_line}\n"
        result += f"line {function_line_number}: {function_line}\n"

    return result

def template_action_map(app_file, template_file):
    template_content = read_file(template_file)

    if template_content == "File not found.":
        return f"File not found: {template_file}"

    lines = template_content.splitlines()
    endpoints = []

    for line in lines:
        clean_line = line.strip()

        if "<form" in clean_line and "url_for(" in clean_line:
            start = clean_line.find("url_for(")

            if start != -1:
                quote_start = clean_line.find("'", start)

                if quote_start == -1:
                    quote_start = clean_line.find('"', start)

                if quote_start != -1:
                    quote_char = clean_line[quote_start]

                    quote_end = clean_line.find(quote_char, quote_start + 1)

                    if quote_end != -1:
                        endpoint = clean_line[quote_start + 1:quote_end]
                        endpoints.append(endpoint)

    if not endpoints:
        return f"No form action endpoints found in: {template_file}"

    result = f"TEMPLATE ACTION MAP: {template_file}\n\n"

    for endpoint in endpoints:
        result += form_action_route(app_file, endpoint)
        result += "\n"

    return result