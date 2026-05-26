def validate_js_rules(content):
    warnings = []

    if "getElementById" in content:
        warnings.append("[JS] JS uses getElementById; verify matching IDs exist in HTML.")

    if ".checked" in content and "do_not_fill" in content:
        warnings.append(
            "[JS] Honeypot appears to be treated like a checkbox. "
            "Hidden honeypot fields should use .value checks instead."
        )

    return warnings