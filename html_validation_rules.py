def validate_html_rules(content):
    warnings = []

    if "{% extends" not in content:
        warnings.append("[HTML] HTML/Jinja missing {% extends %}.")

    if "{% extends" in content:
        if "<html" in content.lower():
            warnings.append("[HTML] Child template extends base.html but includes an <html> tag.")

        if "<body" in content.lower():
            warnings.append("[HTML] Child template extends base.html but includes a <body> tag.")

        if "<head" in content.lower():
            warnings.append(
                "[HTML] Child template extends base.html but includes a <head> tag. "
                "Remove the <head> section because base.html already provides it."
            )

        if "<!doctype html" in content.lower():
            warnings.append("[HTML] Child template extends base.html but includes <!DOCTYPE html>.")

    if "{% block content" not in content:
        warnings.append("[HTML] HTML/Jinja missing content block.")

    if "{% endblock" not in content:
        warnings.append("[HTML] HTML/Jinja missing endblock.")

    if "<form" in content and "do_not_fill" not in content:
        warnings.append("[HTML] Form page missing honeypot field.")

    if "form.hidden_tag()" in content:
        warnings.append("[HTML] HTML uses form.hidden_tag(), but draft routes do not provide a WTForms form object.")

    if (
            'name="do_not_fill"' in content
            and "display:none" not in content
            and "hidden" not in content
            and "left:-9999px" not in content
            and "position:absolute" not in content
    ):
        warnings.append("[HTML] Honeypot field may be visible; it should be hidden from real users.")

    if "csrf_token" in content:
        warnings.append(
            "[HTML] Template contains Django csrf_token syntax. "
            "Remove csrf_token entirely for this project unless Flask-WTF was explicitly requested."
        )

    if "{{ employee_name }}" in content or "{{ date }}" in content:
        warnings.append(
            "[HTML] Template expects employee_name/date variables that may not be provided by the Flask route. "
            "Use <input> fields instead of template output variables unless the route explicitly provides those values."
        )

    return warnings