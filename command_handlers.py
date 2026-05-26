from ai import ask_ai
from review_config import REVIEW_DIR
from project_rules import get_base_template_rules
from write_tools import (
    save_review_draft, draft_html_template, draft_flask_route, draft_css_file, draft_js_file, draft_page_bundle, draft_ai_page_bundle,
    draft_ai_html_file, draft_ai_code_review, draft_validator_driven_review, draft_single_warning_review, build_validation_report, draft_quiz_from_reference
)
from web_tools import (
    find_text_usage, find_function_usage, trace_button, trace_route, trace_endpoint, trace_id, explain_file_role,
    file_complexity, list_routes, route_summary, route_detail, route_full, route_templates, template_routes, template_extends,
    template_blocks, template_forms, template_inputs, template_required, template_hidden, template_honeypot, route_form_map,
    route_fields, route_emails, route_redirects, route_files, route_security, route_warnings, route_report, project_architecture,
    project_health, project_focus, or_routes, or_report, or_templates_detail, or_form_fields, or_required_fields,
    or_route_reports, template_form_actions, form_action_route, template_action_map,
)


###------------------------- Web Tools ------------------------###

def find_usage_command(user_message):
    search_text = user_message.replace("find usage ", "", 1)

    return find_text_usage(search_text)


def find_function_command(user_message):
    function_name = user_message.replace("find function ", "", 1)

    return find_function_usage(function_name)


def trace_button_command(user_message):
    button_id = user_message.replace("trace button ", "", 1)

    return trace_button(button_id)


def trace_route_command(user_message):
    route_name = user_message.replace("trace route ", "", 1)

    return trace_route(route_name)


def trace_endpoint_command(user_message):
    endpoint = user_message.replace("trace endpoint ", "", 1)

    return trace_endpoint(endpoint)

def trace_id_command(user_message):
    element_id = user_message.replace("trace id ", "", 1)

    return trace_id(element_id)

def explain_file_role_command(user_message):
    filename = user_message.replace("explain file ", "", 1)

    return explain_file_role(filename)

def file_complexity_command(user_message):
    filename = user_message.replace("file complexity ", "", 1)

    return file_complexity(filename)

def list_routes_command(user_message):
    filename = user_message.replace("list routes ", "", 1)

    return list_routes(filename)

def route_summary_command(user_message):
    filename = user_message.replace("route summary ", "", 1)

    return route_summary(filename)

def route_detail_command(user_message):
    parts = user_message.replace("route detail ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route detail <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_detail(filename, route_name)

def route_full_command(user_message):
    parts = user_message.replace("route full ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route full <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_full(filename, route_name)

def route_templates_command(user_message):
    parts = user_message.replace("route templates ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route templates <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_templates(filename, route_name)

def template_routes_command(user_message):
    parts = user_message.replace("template routes ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: template routes <filename> <template>"

    filename = parts[0]
    template_name = parts[1]

    return template_routes(filename, template_name)

def template_extends_command(user_message):
    template_file = user_message.replace("template extends ", "", 1)

    return template_extends(template_file)

def template_blocks_command(user_message):
    template_file = user_message.replace("template blocks ", "", 1)

    return template_blocks(template_file)

def template_forms_command(user_message):
    template_file = user_message.replace("template forms ", "", 1)

    return template_forms(template_file)

def template_inputs_command(user_message):
    template_file = user_message.replace("template inputs ", "", 1)

    return template_inputs(template_file)

def template_required_command(user_message):
    template_file = user_message.replace("template required ", "", 1)

    return template_required(template_file)

def template_hidden_command(user_message):
    template_file = user_message.replace("template hidden ", "", 1)

    return template_hidden(template_file)

def template_honeypot_command(user_message):
    template_file = user_message.replace("template honeypot ", "", 1)

    return template_honeypot(template_file)

def route_form_map_command(user_message):
    parts = user_message.replace("route form map ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route form map <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_form_map(filename, route_name)

def route_fields_command(user_message):
    parts = user_message.replace("route fields ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route fields <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_fields(filename, route_name)

def route_emails_command(user_message):
    parts = user_message.replace("route emails ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route emails <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_emails(filename, route_name)

def route_redirects_command(user_message):
    parts = user_message.replace("route redirects ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route redirects <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_redirects(filename, route_name)

def route_files_command(user_message):
    parts = user_message.replace("route files ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route files <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_files(filename, route_name)

def route_security_command(user_message):
    parts = user_message.replace("route security ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route security <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_security(filename, route_name)

def route_warnings_command(user_message):
    parts = user_message.replace("route warnings ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route warnings <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_warnings(filename, route_name)

def route_report_command(user_message):
    parts = user_message.replace("route report ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: route report <filename> <route>"

    filename = parts[0]
    route_name = parts[1]

    return route_report(filename, route_name)

def project_architecture_command():
    return project_architecture()

def project_health_command():
    return project_health()

def project_focus_command():
    return project_focus()

def or_routes_command(user_message):
    filename = user_message.replace("or routes ", "", 1)

    return or_routes(filename)

def or_report_command(user_message):
    filename = user_message.replace("or report ", "", 1)

    return or_report(filename)

def or_templates_detail_command():
    return or_templates_detail()

def or_form_fields_command():
    return or_form_fields()

def or_required_fields_command():
    return or_required_fields()

def or_route_reports_command(user_message):
    filename = user_message.replace("or route reports ", "", 1)

    return or_route_reports(filename)

def template_form_actions_command(user_message):
    template_file = user_message.replace("template form actions ", "", 1)

    return template_form_actions(template_file)

def form_action_route_command(user_message):
    parts = user_message.replace("form action route ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: form action route <filename> <endpoint_name>"

    filename = parts[0]
    endpoint_name = parts[1]

    return form_action_route(filename, endpoint_name)

def template_action_map_command(user_message):
    parts = user_message.replace("template action map ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: template action map <app_file> <template_file>"

    app_file = parts[0]
    template_file = parts[1]

    return template_action_map(app_file, template_file)





###------------------------- Write Tools ------------------------###

def draft_template_command(user_message):
    parts = user_message.replace("draft template ", "", 1).split(" ", 1)

    if len(parts) < 2:
        return "Usage: draft template <filename> <title>"

    filename = parts[0]
    title = parts[1]

    return draft_html_template(filename, title)

def draft_route_command(user_message):
    parts = user_message.split()

    if len(parts) < 4:
        return (
            "Usage:\n"
            "draft route route_name template_name.html"
        )

    route_name = parts[2]
    template_name = parts[3]

    result = draft_flask_route(
        route_name=route_name,
        template_name=template_name
    )

    return result

def draft_css_command(user_message):
    parts = user_message.split()

    if len(parts) < 3:
        return (
            "Usage:\n"
            "draft css filename.css"
        )

    filename = parts[2]

    result = draft_css_file(
        filename=filename
    )

    return result

def draft_js_command(user_message):
    parts = user_message.split()

    if len(parts) < 3:
        return (
            "Usage:\n"
            "draft js filename.js"
        )

    filename = parts[2]

    result = draft_js_file(
        filename=filename
    )

    return result

def draft_page_bundle_command(user_message):
    parts = user_message.split()

    if len(parts) < 5:
        return (
            "Usage:\n"
            "draft page bundle page_name Page Title"
        )

    page_name = parts[3]
    page_title = " ".join(parts[4:])

    result = draft_page_bundle(
        page_name=page_name,
        page_title=page_title
    )

    return result

def draft_ai_page_command(user_message):
    if "|" not in user_message:
        return (
            "Usage:\n"
            "draft ai page page_name Page Title | page instructions"
        )

    left_side, user_request = user_message.split("|", 1)

    parts = left_side.split()

    if len(parts) < 5:
        return (
            "Usage:\n"
            "draft ai page page_name Page Title | page instructions"
        )

    page_name = parts[3]
    page_title = " ".join(parts[4:]).strip()

    result = draft_ai_page_bundle(
        page_name=page_name,
        page_title=page_title,
        user_request=user_request.strip()
    )

    return result

def draft_ai_html_command(user_message):
    if "|" not in user_message:
        return (
            "Usage:\n"
            "draft ai html page_name Page Title | page instructions"
        )

    left_side, user_request = user_message.split("|", 1)

    parts = left_side.split()

    if len(parts) < 5:
        return (
            "Usage:\n"
            "draft ai html page_name Page Title | page instructions"
        )

    page_name = parts[3]
    page_title = " ".join(parts[4:]).strip()

    return draft_ai_html_file(
        page_name=page_name,
        page_title=page_title,
        user_request=user_request.strip()
    )

def review_draft_command(user_message):
    parts = user_message.split()

    if len(parts) < 4:
        return (
            "Usage:\n"
            "review draft html filename.html"
        )

    filename = parts[3]

    draft_path = REVIEW_DIR / filename

    if not draft_path.exists():
        return f"Draft file not found: {draft_path}"

    code_content = draft_path.read_text(encoding="utf-8")

    validation_filename = filename.replace(".html", "_HTML_VALIDATION.txt")
    validation_path = REVIEW_DIR / validation_filename

    validation_content = ""

    if validation_path.exists():
        validation_content = validation_path.read_text(encoding="utf-8")

    return draft_ai_code_review(
        filename=filename,
        code_content=code_content,
        validation_content=validation_content
    )

def review_html_structure_command(user_message):
    parts = user_message.split()

    if len(parts) < 4:
        return (
            "Usage:\n"
            "review html structure filename.html"
        )

    filename = parts[3]

    draft_path = REVIEW_DIR / filename

    if not draft_path.exists():
        return f"Draft file not found: {draft_path}"

    code_content = draft_path.read_text(encoding="utf-8")

    validation_filename = filename.replace(".html", "_HTML_VALIDATION.txt")
    validation_path = REVIEW_DIR / validation_filename

    validation_content = ""

    if validation_path.exists():
        validation_content = validation_path.read_text(encoding="utf-8")

    base_template_rules = get_base_template_rules()

    review_prompt = f"""
Review this HTML/Jinja draft ONLY for structure problems.

Filename:
{filename}

Validation report:
{validation_content}

Code:
{code_content}

Project Base Template Rules:
{base_template_rules}

Rules:
- ONLY review HTML/Jinja structure issues.
- Ignore security advice.
- Ignore Flask-WTF.
- Ignore CSRF systems.
- Ignore accessibility suggestions.
- Ignore styling suggestions.
- Ignore JavaScript suggestions.
- Do NOT redesign the page.
- Keep fixes minimal.

Focus on:
- Jinja blocks
- extends usage
- form structure
- broken template syntax
- invalid nesting
- missing content blocks
- incorrect url_for usage

Return format:
ISSUE:
FIX:
PATCH:

Project Structure Rules:
- base.html already contains:
  - <!DOCTYPE html>
  - <html>
  - <head>
  - <body>

- Child templates MUST NOT create:
  - <!DOCTYPE html>
  - <html>
  - <head>
  - <body>

- Child templates should ONLY:
  - extend base.html
  - define Jinja blocks

- A correct child template structure is:

  {{% extends "base.html" %}}

  {{% block title %}}
  Page Title
  {{% endblock %}}

  {{% block content %}}
  page content here
  {{% endblock %}}

- Do not recommend adding full HTML document tags.
"""

    review_content = ask_ai(
        "You are a careful Flask/Jinja structure reviewer.",
        review_prompt
    )

    review_filename = filename.replace(".", "_") + "_HTML_STRUCTURE_REVIEW.txt"

    return save_review_draft(
        review_filename,
        review_content
    )

def review_validator_command(user_message):
    parts = user_message.split()

    if len(parts) < 3:
        return (
            "Usage:\n"
            "review validator filename.html"
        )

    filename = parts[2]

    draft_path = REVIEW_DIR / filename

    if not draft_path.exists():
        return f"Draft file not found: {draft_path}"

    code_content = draft_path.read_text(encoding="utf-8")

    validation_filename = filename.replace(".html", "_HTML_VALIDATION.txt")
    validation_path = REVIEW_DIR / validation_filename

    if not validation_path.exists():
        return f"Validation report not found: {validation_path}"

    validation_content = validation_path.read_text(encoding="utf-8")

    return draft_validator_driven_review(
        filename=filename,
        code_content=code_content,
        validation_content=validation_content
    )

def review_validator_warning_command(user_message):
    parts = user_message.split()

    if len(parts) < 5:
        return (
            "Usage:\n"
            "review validator warning 1 filename.html"
        )

    warning_number = int(parts[3])
    filename = parts[4]

    draft_path = REVIEW_DIR / filename

    if not draft_path.exists():
        return f"Draft file not found: {draft_path}"

    code_content = draft_path.read_text(encoding="utf-8")

    validation_filename = filename.replace(".html", "_HTML_VALIDATION.txt")
    validation_path = REVIEW_DIR / validation_filename

    if not validation_path.exists():
        return f"Validation report not found: {validation_path}"

    validation_content = validation_path.read_text(encoding="utf-8")

    return draft_single_warning_review(
        filename=filename,
        code_content=code_content,
        validation_content=validation_content,
        warning_number=warning_number
    )

def validate_draft_command(user_message):
    parts = user_message.split()

    if len(parts) < 3:
        return (
            "Usage:\n"
            "validate draft filename.html"
        )

    filename = parts[2]

    draft_path = REVIEW_DIR / filename

    if not draft_path.exists():
        return f"Draft file not found: {draft_path}"

    content = draft_path.read_text(encoding="utf-8")

    report = build_validation_report([
        (filename, content)
    ])

    report_filename = filename.replace(".", "_") + "_VALIDATION.txt"

    return save_review_draft(
        report_filename,
        report
    )

def draft_quiz_from_reference_command(user_message):
    if "|" not in user_message:
        return (
            "Usage:\n"
            "draft quiz from reference reference_file.html | new_quiz_name | New Quiz Title | questions"
        )

    left_side, questions = user_message.split("|", 1)

    parts = left_side.split()

    if len(parts) < 5:
        return (
            "Usage:\n"
            "draft quiz from reference reference_file.html | new_quiz_name | New Quiz Title | questions"
        )

    reference_html = parts[4].strip()

    remaining_parts = questions.split("|")

    if len(remaining_parts) < 3:
        return (
            "Usage:\n"
            "draft quiz from reference reference_file.html | new_quiz_name | New Quiz Title | questions"
        )

    new_quiz_name = remaining_parts[0].strip()
    new_quiz_title = remaining_parts[1].strip()
    new_questions = remaining_parts[2].strip()

    return draft_quiz_from_reference(
        reference_html=reference_html,
        new_quiz_name=new_quiz_name,
        new_quiz_title=new_quiz_title,
        new_questions=new_questions
    )