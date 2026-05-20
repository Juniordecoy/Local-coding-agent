from flask import Flask, render_template, request

from main import handle_user_message

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    ai_response = ""
    files_used = []
    activity_log = []
    agent_status = {
        "chat": "idle",
        "file": "idle",
        "memory": "idle",
        "tool": "idle"
    }

    user_message = ""

    if request.method == "POST":
        user_message = request.form.get("user_message", "")

        result = handle_user_message(user_message)

        agent_status["chat"] = "thinking"

        if result["files_used"]:
            agent_status["file"] = "searching"

        if "memory" in user_message.lower():
            agent_status["memory"] = "active"

        if "tool" in user_message.lower():
            agent_status["tool"] = "running"

        ai_response = result["response"]
        files_used = result["files_used"]

        activity_log.append(f"User asked: {user_message}")

        for file in files_used:
            activity_log.append(f"AI searched file: {file}")

        activity_log.append("AI generated response")

    return render_template(
        "index.html",
        ai_response=ai_response,
        files_used=files_used,
        user_message=user_message,
        activity_log=activity_log,
        agent_status=agent_status
    )


if __name__ == "__main__":
    app.run(debug=True)