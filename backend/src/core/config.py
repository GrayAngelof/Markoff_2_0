# backend/src/core/config.py
"""
Конфигурация приложения Markoff
Только чтение env переменных
Используется Pydantic BaseSettings для валидации окружения
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Центральная конфигурация приложения
    Читает переменные окружения с fallback значениями
    
    ENVIRONMENT переменные (docker):
    - DATABASE_URL: строка подключения PostgreSQL
    - ENVIRONMENT: development/production
    - PYTHONUNBUFFERED: логи без буферизации (устанавливается Docker)
    
    Принципы:
    1. Все настройки читаются из переменных окружения
    2. Для разработки есть значения по умолчанию
    3. Никаких жестко закодированных значений в коде
    """
    
    # База данных - обязательная переменная, но для разработки оставляем тестовую БД
    DATABASE_URL: str = "postgresql+psycopg2://markoff:1@192.168.2.4:5432/markoff2_0_db"
    
    # Окружение приложения
    ENVIRONMENT: str = "development"
    
    # Настройки FastAPI
    API_V1_PREFIX: str = ""  # Без префикса v1 согласно ТЗ
    PROJECT_NAME: str = "Markoff API"
    VERSION: str = "0.1.0"
    DEBUG: bool = True  # Включаем подробные ошибки для разработки
    
    # Настройки CORS (для доступа из клиента на Windows)
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        # В будущем добавим IP клиентской машины
    ]
    
    class Config:
        """Настройки Pydantic для чтения из .env файла"""
        env_file = ".env"
        case_sensitive = True

# Глобальный singleton конфига
# Создаем один экземпляр настроек для всего приложения
settings = Settings()