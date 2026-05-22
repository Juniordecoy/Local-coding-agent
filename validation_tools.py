def validate_draft_content(filename, content):
    warnings = []

    lower_filename = filename.lower()

    if "```" in content:
        warnings.append("Contains markdown code fences.")

    if "Here is" in content or "This code" in content:
        warnings.append("May contain AI explanation text.")

    if lower_filename.endswith(".html"):
        if "{% extends" not in content:
            warnings.append("HTML/Jinja missing {% extends %}.")

        if "{% block content" not in content:
            warnings.append("HTML/Jinja missing content block.")

        if "{% endblock" not in content:
            warnings.append("HTML/Jinja missing endblock.")

        if "<form" in content and "do_not_fill" not in content:
            warnings.append("Form page missing honeypot field.")

        if "form.hidden_tag()" in content:
            warnings.append("HTML uses form.hidden_tag(), but draft routes do not provide a WTForms form object.")

        if 'name="do_not_fill"' in content and "display:none" not in content and "hidden" not in content:
            warnings.append("Honeypot field may be visible; it should be hidden from real users.")

        if "csrf_token" in content:
            warnings.append(
                "Template may contain Django csrf_token syntax instead of Flask/Jinja patterns."
            )

        if "{{ employee_name }}" in content or "{{ date }}" in content:
            warnings.append(
                "Template expects variables that may not be provided by the Flask route."
            )

    if lower_filename.endswith(".py"):
        if "@app.route" not in content:
            warnings.append("Python route draft missing @app.route.")

        if "request.form" in content and "do_not_fill" not in content:
            warnings.append("Form route may be missing honeypot check.")

        if "if 'do_not_fill' in form_data" in content:
            warnings.append("Bad honeypot check: field existence is not enough; check value instead.")

        if "app.run(" in content:
            warnings.append("Route draft should not include app.run().")

        if "from flask import Flask" in content:
            warnings.append("Route draft should not create a new Flask app.")

        if '"form_data": form_data' in content and 'form_data = request.form.to_dict()' in content:
            warnings.append("Route may use form_data outside POST before it is defined on GET.")

    if lower_filename.endswith(".js"):
        if "getElementById" in content:
            warnings.append("JS uses getElementById; verify matching IDs exist in HTML.")

        if ".checked" in content and "do_not_fill" in content:
            warnings.append("Honeypot is being treated like a checkbox.")

    return warnings