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

        if "{% extends" in content:
            if "<html" in content.lower():
                warnings.append("Child template extends base.html but includes an <html> tag.")

            if "<body" in content.lower():
                warnings.append("Child template extends base.html but includes a <body> tag.")

            if "<head" in content.lower():
                warnings.append("Child template extends base.html but includes a <head> tag.")

            if "<!doctype html" in content.lower():
                warnings.append(
                    "Child template extends base.html but includes <!DOCTYPE html>."
                )

        if "{% extends" in content and "<!DOCTYPE html>" in content:
            warnings.append("Child template extends base.html but includes <!DOCTYPE html>.")

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
                "Template contains Django csrf_token syntax. "
                "Remove csrf_token entirely for this project unless Flask-WTF was explicitly requested."
            )

        if "{{ employee_name }}" in content or "{{ date }}" in content:
            warnings.append(
                "Template expects employee_name/date variables that may not be provided by the Flask route. "
                "Use real input fields instead, unless the route explicitly sends these variables."
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

def validate_draft_content_detailed(filename, content):
    errors = []
    warnings = []
    info = []

    basic_warnings = validate_draft_content(filename, content)

    for warning in basic_warnings:
        if (
            "missing" in warning.lower()
            or "includes an <html>" in warning
            or "includes a <body>" in warning
            or "includes a <head>" in warning
            or "includes <!DOCTYPE html>" in warning
        ):
            errors.append(warning)
        else:
            warnings.append(warning)

    return {
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }

def extract_validation_warnings(validation_content):
    warnings = []

    for line in validation_content.splitlines():
        clean_line = line.strip()

        if clean_line.startswith("- WARNING:"):
            warning = clean_line.replace("- WARNING:", "", 1).strip()
            warnings.append(warning)

    return warnings

def extract_validation_warning_by_index(validation_content, index):
    warnings = extract_validation_warnings(validation_content)

    if index < 0 or index >= len(warnings):
        return None

    return warnings[index]


