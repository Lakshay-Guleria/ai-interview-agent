"""
Centralized settings. Load once at startup, inject where needed.
"""
from pathlib import Path
from pydantic_settings import BaseSettings

# Absolute path to the backend folder
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    groq_api_key: str = ""
    gemini_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.7

    curriculum_path: str = "curriculum.json"
    candidates_path: str = "candidates.json"

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()