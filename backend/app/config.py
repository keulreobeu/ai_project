import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "project" / "seoul_festival.db"

if load_dotenv:
    load_dotenv(PROJECT_ROOT / "backend" / ".env")


def get_database_url() -> str:
    configured_url = os.getenv("DATABASE_URL", "").strip()
    if configured_url:
        return configured_url

    configured_path = os.getenv("DB_PATH", "").strip()
    if configured_path:
        db_path = Path(configured_path).expanduser()
        if not db_path.is_absolute():
            db_path = PROJECT_ROOT / db_path
    else:
        db_path = DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.resolve().as_posix()}"


def get_cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return ["http://127.0.0.1:5173", "http://localhost:5173"]


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip() or "gemini-3.5-flash"