from file_tools import read_file


def get_base_template_rules(base_template="doit_portal\\templates\\base.html"):
    content = read_file(base_template)

    if content == "File not found.":
        return (
            "Base template not found. Assume child templates should extend base.html "
            "and define title/content blocks only."
        )

    rules = []

    if "<html" in content.lower():
        rules.append("- base.html already owns the <html> tag.")

    if "<head" in content.lower():
        rules.append("- base.html already owns the <head> tag.")

    if "<body" in content.lower():
        rules.append("- base.html already owns the <body> tag.")

    if "{% block title" in content:
        rules.append("- base.html provides a title block.")

    if "{% block content" in content:
        rules.append("- base.html provides a content block.")

    rules.append("- Child templates should extend base.html.")
    rules.append("- Child templates should not create duplicate html/head/body tags.")

    return "\n".join(rules)