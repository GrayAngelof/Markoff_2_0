# backend/src/main.py
"""
Точка входа в FastAPI приложение Markoff.

Создаёт экземпляр FastAPI, подключает роутеры и middleware.
"""

# ===== ИМПОРТЫ =====
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config import settings

# Новые роутеры
from src.app.reference_data import router as reference_data_router
from src.app.reference_entity.counterparty import router as counterparty_router
from src.app.reference_entity.responsible_person import router as responsible_person_router
from src.app.structure import router as structure_router


# ===== КОНСТАНТЫ =====
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ===== MIDDLEWARE =====
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ===== РОУТЕРЫ =====
# Reference Data (справочники)
app.include_router(reference_data_router)

# Reference Entity (сущности по ID)
app.include_router(counterparty_router)
app.include_router(responsible_person_router)

# Structure (физическая иерархия)
app.include_router(structure_router)


# ===== ЭНДПОИНТЫ =====
@app.get("/", tags=["root"])
async def root() -> dict:
    """Корневой эндпоинт для проверки работы API."""
    return {"message": "Markoff API is running"}


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Эндпоинт для проверки здоровья сервиса."""
    return {"status": "healthy"}