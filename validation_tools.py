from html_validation_rules import validate_html_rules
from flask_validation_rules import validate_flask_rules
from js_validation_rules import validate_js_rules
from quiz_validation_rules import validate_quiz_rules

def validate_draft_content(filename, content):
    warnings = []

    lower_filename = filename.lower()

    if "```" in content:
        warnings.append("Contains markdown code fences.")

    if "Here is" in content or "This code" in content:
        warnings.append("May contain AI explanation text.")

    if lower_filename.endswith(".html"):
        warnings.extend(
            validate_html_rules(content)
        )

        if "quiz" in lower_filename:
            warnings.extend(
                validate_quiz_rules(content)
            )

    if lower_filename.endswith(".py"):
        warnings.extend(
            validate_flask_rules(content)
        )

    if lower_filename.endswith(".js"):
        warnings.extend(
            validate_js_rules(content)
        )

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

        if clean_line.startswith("- ERROR:"):
            warning = clean_line.replace("- ERROR:", "", 1).strip()
            warnings.append(warning)

    return warnings

def extract_validation_warning_by_index(validation_content, index):
    warnings = extract_validation_warnings(validation_content)

    if index < 0 or index >= len(warnings):
        return None

    return warnings[index]

def validate_patch_content(content):
    warnings = []

    if "csrf_token" in content:
        warnings.append(
            "[PATCH] Patch still contains csrf_token syntax after validator review."
        )

    if "<html" in content.lower() and "{% extends" in content:
        warnings.append(
            "[PATCH] Patch introduces full HTML tags into inherited template."
        )

    if "| safe" in content:
        warnings.append(
            "[PATCH] Patch introduces Jinja |safe filter which may bypass escaping."
        )

    if "url_for('safety_quiz_may_submission')" in content:
        warnings.append(
            "[PATCH] Patch introduced unknown route safety_quiz_may_submission."
        )

    if "{{ employee_name" in content:
        warnings.append(
            "[PATCH] Patch replaced input fields with template variables."
        )

    if "{{ comment" in content:
        warnings.append(
            "[PATCH] Patch replaced textarea input with template variable output."
        )

    if "form-group row" in content:
        warnings.append(
            "[PATCH] Patch introduced Bootstrap layout patterns not requested by project."
        )

    return warnings
