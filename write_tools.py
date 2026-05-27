from ai import ask_ai
from pathlib import Path
from review_config import REVIEW_DIR
from validation_tools import (
    validate_draft_content_detailed, extract_validation_warnings, extract_validation_warning_by_index,
    validate_patch_content
)


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
- Return ONLY raw Jinja/HTML code.
- Do not use markdown fences.
- Do not explain the code.
- Must start with: {{% extends "base.html" %}}
- Must include: {{% block title %}}{page_title}{{% endblock %}}
- Must include: {{% block content %}}
- Must end with: {{% endblock %}}
- Include a visible form if the request needs one.
- Include employee name input with id="employee_name" and name="employee_name".
- Include date input with id="quiz_date" and name="quiz_date".
- Include honeypot input named do_not_fill.
- Use action="{{{{ url_for('{page_name}') }}}}".
- Link CSS with url_for('static', filename='css/{css_filename}').
- Link JS with url_for('static', filename='js/{js_filename}').
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
- Return ONLY raw JavaScript code.
- Do not use markdown fences.
- Do not explain the code.
- Do not treat honeypot like a checkbox.
- Honeypot is a hidden text input named do_not_fill.
- Use DOMContentLoaded listener.
- Add submit protection that disables the submit button after form submit.
- Use querySelector instead of getElementById where possible.
- Keep code simple and production-safe.
"""

    route_prompt = f"""
Create a Flask route draft for this page.

Route/function name: {page_name}
Template: {html_filename}
User request: {user_request}

Rules:
- Return ONLY route code.
- Do not use markdown fences.
- Do not explain the code.
- Do not import Flask.
- Do not create app = Flask(__name__).
- Do not include app.run().
- Assume app, request, and render_template already exist.
- Use @app.route("/{page_name}", methods=["GET", "POST"]).
- On POST, use form_data = request.form.to_dict().
- Check honeypot with: if form_data.get("do_not_fill"):
- If honeypot has value, return "Blocked", 400.
- On successful POST, render template with success=True and form_data=form_data.
- On GET, render template with success=False.
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

    validation_report = build_validation_report([
        (html_filename, html_content),
        (css_filename, css_content),
        (js_filename, js_content),
        (route_filename, route_content),
    ])

    results = []

    results.append(save_review_draft(html_filename, html_content))
    results.append(save_review_draft(css_filename, css_content))
    results.append(save_review_draft(js_filename, js_content))
    results.append(save_review_draft(route_filename, route_content))

    results.append(
        save_review_draft(
            f"{page_name}_VALIDATION_REPORT.txt",
            validation_report
        )
    )

    return "\n".join(results)

def clean_ai_code(ai_text):
    content = ai_text.strip()

    if content.startswith("```"):
        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines)

    content = content.replace("```html", "")
    content = content.replace("```jinja", "")
    content = content.replace("```", "")

    lines = []

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("Here is"):
            continue

        if stripped.startswith("This code"):
            continue

        lines.append(line)

    content = "\n".join(lines)

    return content.strip()

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

def build_validation_report(file_results):
    report_lines = ["AI DRAFT VALIDATION REPORT", ""]

    for filename, content in file_results:
        result = validate_draft_content_detailed(filename, content)

        report_lines.append(f"{filename}:")

        if result["errors"]:
            report_lines.append("ERRORS:")
            for error in result["errors"]:
                report_lines.append(f"- ERROR: {error}")

        if result["warnings"]:
            report_lines.append("WARNINGS:")
            for warning in result["warnings"]:
                report_lines.append(f"- WARNING: {warning}")

        if result["info"]:
            report_lines.append("INFO:")
            for item in result["info"]:
                report_lines.append(f"- INFO: {item}")

        if not result["errors"] and not result["warnings"] and not result["info"]:
            report_lines.append("- No major warnings found.")

        report_lines.append("")

    return "\n".join(report_lines)

def draft_ai_html_file(page_name, page_title, user_request):
    html_filename = f"{page_name}.html"

    html_prompt = f"""
Create a real Flask/Jinja HTML page.

Page name: {page_name}
Page title: {page_title}
User request: {user_request}

Rules:
- Return ONLY raw Jinja/HTML code.
- Do not use markdown fences.
- Do not explain the code.
- Must start with: {{% extends "base.html" %}}
- Must include: {{% block title %}}{page_title}{{% endblock %}}
- After the title block, immediately start:
  {{% block content %}}
- Do NOT create <body>, <html>, or <head> tags.
- All visible page content must exist inside the content block.
- The LAST line of the template must be:
  {{% endblock %}}
- Include semantic HTML structure.
- Include proper labels and accessible inputs.
- Honeypot must be hidden from users with style="display:none;".
- Use url_for('{page_name}') for forms.
- Link CSS using:
  {{{{ url_for('static', filename='css/{page_name}.css') }}}}
- Link JS using:
  {{{{ url_for('static', filename='js/{page_name}.js') }}}}
"""

    html_content = ask_ai(
        "You are an expert Flask/Jinja HTML developer. Return only valid HTML/Jinja code.",
        html_prompt
    )

    html_content = clean_ai_code(html_content)

    html_content = add_review_header(
        html_filename,
        html_content
    )

    validation_report = build_validation_report([
        (html_filename, html_content),
    ])

    results = []

    results.append(
        save_review_draft(
            html_filename,
            html_content
        )
    )

    results.append(
        save_review_draft(
            f"{page_name}_HTML_VALIDATION.txt",
            validation_report
        )
    )

    return "\n".join(results)

def draft_ai_code_review(filename, code_content, validation_content=""):
    review_filename = filename.replace(".", "_") + "_PATCH_REVIEW.txt"

    review_prompt = f"""
Review this generated draft file.

ONLY review issues explicitly listed in the validation report.

Do NOT invent new issues.
Do NOT suggest architectural improvements.
Do NOT suggest framework changes.
Do NOT suggest accessibility enhancements unless listed in the validation report.
Do NOT suggest security systems unless listed in the validation report.

Filename: {filename}

Validation report:
{validation_content}

Code:
{code_content}

Rules:
- Do not rewrite production files.
- Identify the problems clearly.
- Do NOT redesign the page.
- Do NOT add new features.
- Only fix issues found in the validation report.
- Keep changes minimal and localized.
- Preserve existing structure whenever possible.
- Return:
  ISSUE:
  FIX:
  PATCH:
- PATCH should contain only the corrected sections.
- Focus only on this file.
- Keep the review practical and beginner-friendly.

Project Constraints:
- This project uses simple Flask/Jinja patterns.
- Do NOT introduce Flask-WTF unless explicitly requested.
- Do NOT introduce csrf_token systems unless explicitly requested.
- Prefer plain HTML forms and request.form handling.
- Keep patches compatible with existing lightweight portal architecture.
- Do not redesign the framework stack.
- Respect the current project style and simplicity.
"""

    review_content = ask_ai(
        "You are a careful senior code reviewer for Flask/Jinja/HTML/CSS/JS/Python drafts.",
        review_prompt
    )

    review_content = clean_ai_code(review_content)

    return save_review_draft(review_filename, review_content)

def draft_validator_driven_review(filename, code_content, validation_content):
    review_filename = filename.replace(".", "_") + "_VALIDATOR_REVIEW.txt"

    warnings = extract_validation_warnings(validation_content)

    if not warnings:
        return save_review_draft(
            review_filename,
            "No validation warnings found. No patch needed."
        )

    warnings_text = "\n".join(f"- {warning}" for warning in warnings)

    review_prompt = f"""
You are reviewing a generated draft file.

ONLY address these validator warnings:
{warnings_text}

Filename:
{filename}

Code:
{code_content}

Project Rules:
- This is a Flask/Jinja project.
- Child templates extend base.html.
- Child templates must not include <!DOCTYPE html>, <html>, <head>, or <body>.
- Do not use Django syntax.
- Do not use Flask-WTF unless explicitly requested.
- Do not add CSRF systems unless explicitly requested.
- Do not invent extra issues.
- Do not redesign the file.
- Only patch the exact warning(s).

Return format:
WARNING:
WHY IT MATTERS:
PATCH:
"""

    review_content = ask_ai(
        "You are a validator-driven patch reviewer. Only fix listed warnings.",
        review_prompt
    )

    review_content = clean_ai_code(review_content)

    return save_review_draft(review_filename, review_content)

def draft_single_warning_review(filename, code_content, validation_content, warning_number):
    review_filename = filename.replace(".", "_") + f"_WARNING_{warning_number}_REVIEW.txt"

    warning_index = warning_number - 1

    warning = extract_validation_warning_by_index(
        validation_content,
        warning_index
    )

    if not warning:
        return save_review_draft(
            review_filename,
            f"No validation warning found at number {warning_number}."
        )

    review_prompt = f"""
You are reviewing one validator warning from a generated draft file.

ONLY address this warning:
{warning}

Filename:
{filename}

Code:
{code_content}

Project Rules:
- This is a Flask/Jinja project.
- Child templates extend base.html.
- Child templates must not include <!DOCTYPE html>, <html>, <head>, or <body>.
- Do not use Django syntax.
- Do not use Flask-WTF unless explicitly requested.
- Do not add CSRF systems unless explicitly requested.
- Do not invent extra issues.
- Do not redesign the file.
- Only patch this exact warning.

Return format:
WARNING:
PATCH:
"""

    review_content = ask_ai(
        "You are a single-warning patch reviewer. Fix only the listed warning.",
        review_prompt
    )

    review_content = clean_ai_code(review_content)

    patch_warnings = validate_patch_content(review_content)

    if patch_warnings:
        review_content += "\n\nPATCH VALIDATION WARNINGS:\n"

        for warning in patch_warnings:
            review_content += f"- {warning}\n"

    return save_review_draft(review_filename, review_content)

def draft_quiz_from_reference(
    reference_html,
    new_quiz_name,
    new_quiz_title,
    new_questions
):
    reference_path = REVIEW_DIR / reference_html

    if not reference_path.exists():
        return f"Reference quiz not found: {reference_path}"

    reference_content = reference_path.read_text(encoding="utf-8")

#     prompt = f"""
# You are creating a new safety quiz page.
#
# Follow the reference quiz structure EXACTLY.
#
# Preserve:
# - wrapper structure
# - classes
# - form layout
# - honeypot layout
# - button structure
# - quiz formatting
#
# Only replace:
# - quiz title
# - visible quiz heading text
# - questions
# - answers
#
# REFERENCE QUIZ:
# {reference_content}
#
# NEW QUIZ NAME:
# {new_quiz_name}
#
# NEW QUIZ TITLE:
# {new_quiz_title}
#
# NEW QUESTIONS:
# {new_questions}
#
# CRITICAL QUESTION RULE:
# Use ONLY the questions and answer choices provided in NEW QUESTIONS.
# Do NOT invent new questions.
# Do NOT reuse questions from the reference quiz.
# Do NOT keep any old reference quiz question text.
# If NEW QUESTIONS contains only one question, the generated quiz must contain only one question.
#
# Question Input Format:
# - Questions may contain:
#   - Q1:
#   - A.
#   - B.
#   - C.
#   - D.
# - Convert these into the same radio button structure used in the reference quiz.
# - Preserve the existing formatting style exactly.
#
# Answer Key Rules:
# - If an ANSWER line is provided, do not display it on the page.
# - Keep the answer value letters as radio values: a, b, c, d.
# - Do not add scoring logic unless explicitly requested.
# - Do not change the visible quiz format to show correct answers.
#
# Open-Ended Question Rules:
# - Questions without A/B/C/D answer choices should use textarea fields.
# - Preserve the same textarea structure used in the reference quiz.
# - Textarea questions should still follow q-number naming patterns.
#
# Question Rules:
# - Multiple choice questions must use radio buttons.
# - Preserve the existing q1/q2/q3 naming pattern.
# - Preserve the existing label structure.
# - Preserve required attributes on the first radio option.
# - Open-ended questions should use textarea fields.
# - Keep the same quiz formatting style as the reference file.
#
# Rules:
# - Return ONLY raw Jinja/HTML.
# - Do not explain.
# - Do not redesign.
# - Keep the same formatting patterns.
# - Preserve the same class names.
# - Preserve the same honeypot pattern.
# - Preserve the same submit button structure.
# """

    generated_blocks = build_quiz_question_blocks(new_questions)

    quiz_content = replace_quiz_question_area(
        reference_content,
        generated_blocks
    )

    quiz_content = quiz_content.replace(
        "{% block title %}May Safety Quiz{% endblock %}",
        f"{{% block title %}}{new_quiz_title}{{% endblock %}}"
    )

    quiz_content = quiz_content.replace(
        "May 2026 Safety Quiz",
        new_quiz_title
    )

    filename = f"{new_quiz_name}.html"

    quiz_content = add_review_header(filename, quiz_content)

    validation_report = build_validation_report([
        (filename, quiz_content)
    ])

    results = []

    answer_key = extract_answer_key(new_questions)

    if answer_key:
        results.append(
            save_review_draft(
                f"{new_quiz_name}_ANSWER_KEY.txt",
                answer_key
            )
        )

    results.append(
        save_review_draft(filename, quiz_content)
    )

    results.append(
        save_review_draft(
            f"{new_quiz_name}_HTML_VALIDATION.txt",
            validation_report
        )
    )

    return "\n".join(results)

def parse_quiz_questions(question_text):
    questions = []
    current = None

    for line in question_text.splitlines():
        clean_line = line.strip()

        if not clean_line:
            continue

        if clean_line.upper().startswith("ANSWER:"):
            continue

        if clean_line.startswith("Q") and ":" in clean_line:
            if current:
                questions.append(current)

            current = {
                "question": "",
                "answers": []
            }
            continue

        if current is None:
            continue

        if clean_line.startswith(("A.", "B.", "C.", "D.")):
            current["answers"].append(clean_line)
        else:
            if current["question"]:
                current["question"] += " " + clean_line
            else:
                current["question"] = clean_line

    if current:
        questions.append(current)

    return questions

def build_quiz_question_blocks(question_text):
    parsed_questions = parse_quiz_questions(question_text)

    blocks = []

    for index, item in enumerate(parsed_questions, start=1):
        question = item["question"]
        answers = item["answers"]

        if answers:
            block = f'''      <div class="hq-q">
        <p><strong>{index}. {question}</strong></p>

        <label><input type="radio" name="q{index}" value="a" required> {answers[0]}</label>
        <label><input type="radio" name="q{index}" value="b"> {answers[1]}</label>
        <label><input type="radio" name="q{index}" value="c"> {answers[2]}</label>
        <label><input type="radio" name="q{index}" value="d"> {answers[3]}</label>
      </div>'''
        else:
            block = f'''      <div class="hq-q">
        <p><strong>{index}. {question}</strong></p>
        <textarea name="q{index}" rows="3" required></textarea>
      </div>'''

        blocks.append(block)

    return "\n\n".join(blocks)

def replace_quiz_question_area(reference_content, generated_blocks):
    start_marker = '      <div class="hq-q">'
    end_marker = '      <div style="position:absolute; left:-9999px;">'

    start_index = reference_content.find(start_marker)
    end_index = reference_content.find(end_marker)

    if start_index == -1 or end_index == -1:
        return ""

    before_questions = reference_content[:start_index]
    after_questions = reference_content[end_index:]

    return before_questions + generated_blocks + "\n\n" + after_questions

def extract_answer_key(question_text):
    answer_lines = []

    for line in question_text.splitlines():
        clean_line = line.strip()

        if clean_line.upper().startswith("ANSWER:"):
            answer_lines.append(clean_line)

    if not answer_lines:
        return ""

    return "\n".join(answer_lines)