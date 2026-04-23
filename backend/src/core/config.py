# backend/src/core/config.py
"""
Конфигурация приложения Markoff.

Только чтение env переменных через Pydantic BaseSettings.
"""

# ===== ИМПОРТЫ =====
from pydantic_settings import BaseSettings


# ===== КЛАССЫ =====
class Settings(BaseSettings):
    """
    Центральная конфигурация приложения.

    Читает переменные окружения с fallback значениями.
    """

    # ---- БАЗА ДАННЫХ ----
    DATABASE_URL: str = "postgresql+psycopg2://markoff:1@192.168.2.4:5432/markoff2_0_db"

    # ---- ОКРУЖЕНИЕ ----
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ---- НАСТРОЙКИ FASTAPI ----
    API_V1_PREFIX: str = ""
    PROJECT_NAME: str = "Markoff API"
    VERSION: str = "0.1.0"

    # ---- НАСТРОЙКИ CORS ----
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    class Config:
        """Настройки Pydantic для чтения из .env файла."""
        env_file = ".env"
        case_sensitive = True


# ===== КОНСТАНТЫ =====
# Глобальный singleton конфига
settings = Settings()