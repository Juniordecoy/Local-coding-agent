from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from main import handle_user_message

import json

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

@app.route("/send-message", methods=["POST"])
def send_message():
    data = request.get_json()

    user_message = data.get("message", "")

    result = handle_user_message(user_message)

    return jsonify(result)

@app.route("/stream-message", methods=["POST"])
def stream_message():
    data = request.get_json()
    user_message = data.get("message", "")

    def generate():
        yield f"data: {json.dumps({'type': 'agent', 'agent': 'tool', 'status': 'working'})}\n\n"

        if "file" in user_message.lower() or "main.py" in user_message.lower() or user_message.startswith("multi agent"):
            yield f"data: {json.dumps({'type': 'agent', 'agent': 'file', 'status': 'working'})}\n\n"

        if "memory" in user_message.lower():
            yield f"data: {json.dumps({'type': 'agent', 'agent': 'memory', 'status': 'working'})}\n\n"

        yield f"data: {json.dumps({'type': 'agent', 'agent': 'chat', 'status': 'working'})}\n\n"

        result = handle_user_message(user_message)

        yield f"data: {json.dumps({
            'type': 'response',
            'response': result['response'],
            'events': result.get('activity_events', []),
            'files_used': result.get('files_used', [])
        })}\n\n"

        yield f"data: {json.dumps({'type': 'agent', 'agent': 'memory', 'status': 'saving'})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)