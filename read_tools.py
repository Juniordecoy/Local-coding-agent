from pathlib import Path
from docx import Document
from review_config import REVIEW_DIR


def read_quiz_question_file(question_file):
    file_path = REVIEW_DIR / question_file

    if not file_path.exists():
        return ""

    if file_path.suffix.lower() == ".txt":
        return file_path.read_text(encoding="utf-8")

    if file_path.suffix.lower() == ".docx":
        document = Document(file_path)

        lines = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                lines.append(text)

        return "\n".join(lines)

    return ""