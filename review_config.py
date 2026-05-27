from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

REVIEW_DIR = BASE_DIR / "review_drafts"

REVIEW_DIR.mkdir(parents=True, exist_ok=True)