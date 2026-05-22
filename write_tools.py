from ai import ask_ai
from review_config import REVIEW_DIR


def save_review_draft(filename, content):
    safe_filename = filename.replace("/", "_").replace("\\", "_")

    file_path = REVIEW_DIR / safe_filename

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    return f"Review draft saved: {file_path}"

def draft_html_template(filename, title):
    content = f"""{{% extends "base.html" %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
<section class="portal">
    <div class="form-card">
        <h1>{title}</h1>

        <p>Generated template draft.</p>
    </div>
</section>
{{% endblock %}}
"""

    return save_review_draft(filename, content)

def draft_flask_route(route_name, template_name):
    safe_route_name = route_name.strip().replace(" ", "_").lower()
    safe_template_name = template_name.strip()

    content = f'''@app.route("/{safe_route_name}", methods=["GET", "POST"])
def {safe_route_name}():
    if request.method == "POST":
        form_data = request.form.to_dict()

        return render_template(
            "{safe_template_name}",
            success=True,
            form_data=form_data
        )

    return render_template(
        "{safe_template_name}",
        success=False
    )
'''

    filename = f"{safe_route_name}_route_draft.py"

    return save_review_draft(filename, content)

def draft_css_file(filename, page_class="custom-page"):
    content = f""".{page_class} {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px;
}}

.{page_class} .form-card {{
    background: #ffffff;
    padding: 24px;
    border-radius: 10px;
}}

.{page_class} h1 {{
    margin-bottom: 12px;
}}

.{page_class} .question-block {{
    margin-bottom: 18px;
}}

.{page_class} label {{
    display: block;
    font-weight: 600;
    margin-bottom: 6px;
}}
"""

    return save_review_draft(filename, content)

def draft_js_file(filename):
    content = """document.addEventListener("DOMContentLoaded", function () {
    console.log("Draft page script loaded.");

    const form = document.querySelector("form");

    if (!form) {
        return;
    }

    form.addEventListener("submit", function () {
        const submitButton = form.querySelector("button[type='submit']");

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerText = "Submitting...";
        }
    });
});
"""

    return save_review_draft(filename, content)

def draft_page_bundle(page_name, page_title):
    html_filename = f"{page_name}.html"
    css_filename = f"{page_name}.css"
    js_filename = f"{page_name}.js"

    route_template_name = html_filename

    results = []

    results.append(
        draft_html_template(
            filename=html_filename,
            title=page_title
        )
    )

    results.append(
        draft_css_file(
            filename=css_filename,
            page_class=page_name
        )
    )

    results.append(
        draft_js_file(
            filename=js_filename
        )
    )

    results.append(
        draft_flask_route(
            route_name=page_name,
            template_name=route_template_name
        )
    )

    return "\n".join(results)

def draft_ai_page_bundle(page_name, page_title, user_request):
    html_filename = f"{page_name}.html"
    css_filename = f"{page_name}.css"
    js_filename = f"{page_name}.js"
    route_filename = f"{page_name}_route_draft.py"

    html_prompt = f"""
Create a real Flask/Jinja HTML page.

Page name: {page_name}
Page title: {page_title}
User request: {user_request}

Rules:
- Extend base.html
- Use block title and block content
- Include a form if the request needs one
- Include a honeypot field named do_not_fill
- Use url_for('{page_name}') for the form action
- Link to CSS file: {css_filename}
- Link to JS file: {js_filename}
- Return only the HTML code
"""

    css_prompt = f"""
Create CSS for this Flask page.

Page name: {page_name}
Page title: {page_title}
User request: {user_request}

Rules:
- Scope styles under .{page_name}
- Keep it clean and portal-friendly
- Return only CSS code
"""

    js_prompt = f"""
Create JavaScript for this Flask page.

Page name: {page_name}
Page title: {page_title}
User request: {user_request}

Rules:
- Add submit protection so the button disables after submit
- Keep it safe and simple
- Return only JavaScript code
"""

    route_prompt = f"""
Create a Flask route draft for this page.

Route/function name: {page_name}
Template: {html_filename}
User request: {user_request}

Rules:
- Use @app.route("/{page_name}", methods=["GET", "POST"])
- Use request.form.to_dict()
- Check honeypot field do_not_fill
- Return render_template("{html_filename}") on GET
- Return only Python code
"""

    html_content = ask_ai(
        "You are an expert Flask/Jinja HTML developer. Return only valid HTML/Jinja code.",
        html_prompt
    )

    css_content = ask_ai(
        "You are an expert CSS developer. Return only valid CSS code.",
        css_prompt
    )

    js_content = ask_ai(
        "You are an expert JavaScript developer. Return only valid JavaScript code.",
        js_prompt
    )

    route_content = ask_ai(
        "You are an expert Flask backend developer. Return only valid Python/Flask route code.",
        route_prompt
    )

    html_content = clean_ai_code(html_content)
    css_content = clean_ai_code(css_content)
    js_content = clean_ai_code(js_content)
    route_content = clean_ai_code(route_content)

    html_content = add_review_header(html_filename, html_content)
    css_content = add_review_header(css_filename, css_content)
    js_content = add_review_header(js_filename, js_content)
    route_content = add_review_header(route_filename, route_content)

    results = []

    results.append(save_review_draft(html_filename, html_content))
    results.append(save_review_draft(css_filename, css_content))
    results.append(save_review_draft(js_filename, js_content))
    results.append(save_review_draft(route_filename, route_content))

    return "\n".join(results)

def clean_ai_code(ai_text):
    cleaned = ai_text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines)

    return cleaned.strip()

def add_review_header(filename, content):
    header = f"""/*
AI REVIEW DRAFT
File: {filename}
Status: NOT APPROVED
Safe location: need_reviewed/
Do not paste into production until reviewed.
*/

"""

    if filename.endswith(".py"):
        header = f'''"""
AI REVIEW DRAFT
File: {filename}
Status: NOT APPROVED
Safe location: need_reviewed/
Do not paste into production until reviewed.
"""

'''

    if filename.endswith(".html"):
        header = f"""<!--
AI REVIEW DRAFT
File: {filename}
Status: NOT APPROVED
Safe location: need_reviewed/
Do not paste into production until reviewed.
-->

"""

    return header + content