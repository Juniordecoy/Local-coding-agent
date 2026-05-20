import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")


def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            messages = json.load(file)

        return messages[-12:]

    return []


def save_memory(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(messages, file, indent=2)