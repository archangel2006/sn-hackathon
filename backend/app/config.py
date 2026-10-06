import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from sn-hackathon root if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Student Early-Warning & Support Agent"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("API_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "*"
    ]

    # LLM Settings (Supports Gemini Free Tier or OpenAI or Local Rule Engine)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")  # 'gemini', 'openai', or 'auto'

    # ServiceNow Instance Settings (Supports ServiceNow PDI or Mock Simulator)
    SERVICENOW_INSTANCE: str = os.getenv("SERVICENOW_INSTANCE", "")
    SERVICENOW_USER: str = os.getenv("SERVICENOW_USER", "")
    SERVICENOW_PASSWORD: str = os.getenv("SERVICENOW_PASSWORD", "")
    SERVICENOW_TABLE: str = os.getenv("SERVICENOW_TABLE", "u_student_support_case")

settings = Settings()
