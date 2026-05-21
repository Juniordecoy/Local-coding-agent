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