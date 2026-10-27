import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_DIR = DATA_DIR / "db"
SAMPLE_DOCS_DIR = BASE_DIR.parent / "sample_documents"
IS_VERCEL = os.getenv("VERCEL") == "1"

database_url = os.getenv("DATABASE_URL")
if IS_VERCEL and not database_url:
    raise RuntimeError("DATABASE_URL must be configured on Vercel for persistent storage.")

if not IS_VERCEL:
    DATA_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)
    DATABASE_DIR.mkdir(exist_ok=True)
    SAMPLE_DOCS_DIR.mkdir(exist_ok=True)

if database_url and database_url.startswith(("postgres://", "postgresql://")):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)


class Settings(BaseModel):
    APP_NAME: str = "PolicyDiff — Semantic Policy Change Detector"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = database_url or f"sqlite:///{DATABASE_DIR}/policydiff.db"
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15"))
    MAX_REQUEST_SIZE_MB: int = 4 if IS_VERCEL else 30
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt"}
    # NLP Configuration
    SEMANTIC_SIMILARITY_THRESHOLD_UNCHANGED: float = 0.93
    SEMANTIC_SIMILARITY_THRESHOLD_MODIFIED: float = 0.52
    LEXICAL_WEIGHT: float = 0.35
    SEMANTIC_WEIGHT: float = 0.65


settings = Settings()
