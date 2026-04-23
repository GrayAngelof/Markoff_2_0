# backend/src/main.py
"""
Точка входа в FastAPI приложение Markoff.

Создаёт экземпляр FastAPI, подключает роутеры и middleware.
"""

# ===== ИМПОРТЫ =====
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.routers import dictionary_router, physical_router


# ===== КОНСТАНТЫ =====
# Создаём экземпляр FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ===== MIDDLEWARE =====
# Настройка CORS (Cross-Origin Resource Sharing)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ===== РОУТЕРЫ =====
app.include_router(dictionary_router)
app.include_router(physical_router)


# ===== ЭНДПОИНТЫ =====
@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Корневой эндпоинт для проверки работы API.

    Returns:
        Приветственное сообщение согласно ТЗ: {"message": "Markoff API is running"}
    """
    return {"message": "Markoff API is running"}


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Эндпоинт для проверки здоровья сервиса (используется Docker для healthcheck)."""
    return {"status": "healthy"}