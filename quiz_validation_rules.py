def validate_quiz_rules(content):
    warnings = []

    if 'class="panel"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing standard panel wrapper."
        )

    if 'class="panel-title"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing standard panel-title headings."
        )

    if 'class="quiz-form"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing standard quiz-form class."
        )

    if 'class="hq-q"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing standard hq-q question wrappers."
        )

    if 'type="radio"' not in content:
        warnings.append(
            "[QUIZ] Quiz appears to be missing radio questions."
        )

    if "<textarea" not in content:
        warnings.append(
            "[QUIZ] Quiz missing textarea question/comment field."
        )

    if 'name="do_not_fill"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing honeypot field do_not_fill."
        )

    if 'class="submit-btn"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing standard submit-btn button class."
        )

    if 'method="POST"' not in content and 'method="post"' not in content:
        warnings.append(
            "[QUIZ] Quiz form missing POST method."
        )

    if 'class="success-msg"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing standard success message block."
        )

    if 'class="two-col"' not in content:
        warnings.append(
            "[QUIZ] Quiz missing standard two-col layout wrapper."
        )

    if '<form method="POST"' not in content and '<form method="post"' not in content:
        warnings.append(
            "[QUIZ] Quiz form does not match standard POST form structure."
        )

    if "Why" in content and "<textarea" not in content:
        warnings.append(
            "[QUIZ] Quiz may contain an open-ended question but is missing a textarea."
        )

    if "textarea" in content and "required" not in content:
        warnings.append(
            "[QUIZ] Textarea questions may be missing required attribute."
        )

    if content.count('class="hq-q"') < 1:
        warnings.append("[QUIZ] Quiz should contain at least one hq-q question block.")

    if content.count('type="radio"') > 0 and 'required' not in content:
        warnings.append("[QUIZ] Radio quiz questions may be missing required attributes.")

    if "url_for(" in content:
        warnings.append(
            "[QUIZ] Quiz reference pages usually use plain method=\"POST\" without custom url_for action. Verify route handling before adding action."
        )

    if "csrf_token" in content:
        warnings.append(
            "[QUIZ] Quiz should not include csrf_token unless specifically added to the project."
        )


    return warnings