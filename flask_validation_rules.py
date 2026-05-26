def validate_flask_rules(content):
    warnings = []

    if "@app.route" not in content:
        warnings.append("[FLASK] Python route draft missing @app.route.")

    if "request.form" in content and "do_not_fill" not in content:
        warnings.append("[FLASK] Form route may be missing honeypot check.")

    if "if 'do_not_fill' in form_data" in content:
        warnings.append(
            "[FLASK] Bad honeypot check: field existence is not enough; check value instead."
        )

    if "app.run(" in content:
        warnings.append("[FLASK] Route draft should not include app.run().")

    if "from flask import Flask" in content:
        warnings.append("[FLASK] Route draft should not create a new Flask app.")

    if (
        '"form_data": form_data' in content
        and 'form_data = request.form.to_dict()' in content
    ):
        warnings.append(
            "[FLASK] Route may use form_data outside POST before it is defined on GET."
        )

    return warnings