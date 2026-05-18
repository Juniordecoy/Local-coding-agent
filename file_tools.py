from pathlib import Path

NOTES_FILE = Path("notes.txt")


def read_notes():
    if NOTES_FILE.exists():
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            return file.read()

    return ""

def read_file(filename):
    file_path = Path(filename)

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    return "File not found."

def list_project_files():
    files = []

    ignored_dirs = {
        ".venv",
        "__pycache__",
        ".idea",
        ".git"
    }

    allowed_extensions = {
        ".py",
        ".txt",
        ".html",
        ".css",
        ".js",
        ".json"
    }

    ignored_files = {
        "memory.json"
    }

    for item in Path(".").rglob("*"):

        if any(part in ignored_dirs for part in item.parts):
            continue

        if item.name in ignored_files:
            continue

        if item.is_file() and item.suffix in allowed_extensions:
            files.append(str(item))

    return files

def search_project_files(keyword):
    matches = []

    for file in list_project_files():
        content = read_file(file)

        filename_score = file.lower().count(keyword.lower()) * 5
        content_score = content.lower().count(keyword.lower())

        total_score = filename_score + content_score

        if total_score > 0:
            matches.append({
                "file": file,
                "score": total_score
            })

    matches.sort(key=lambda item: item["score"], reverse=True)

    return [match["file"] for match in matches]

def search_project_files_with_scores(keyword):
    matches = []

    for file in list_project_files():
        content = read_file(file)

        filename_score = file.lower().count(keyword.lower()) * 5
        content_score = content.lower().count(keyword.lower())

        total_score = filename_score + content_score

        if total_score > 0:
            matches.append({
                "file": file,
                "score": total_score
            })

    matches.sort(key=lambda item: item["score"], reverse=True)

    return matches