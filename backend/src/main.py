# backend/src/main.py
"""
Точка входа в FastAPI приложение Markoff
Создает экземпляр FastAPI, подключает роутеры и middleware
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .routers import physical_router, dictionary_router

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    openapi_url="/openapi.json",  # Документация OpenAPI
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc альтернатива
)

# Настройка CORS (Cross-Origin Resource Sharing)
# Позволяет клиенту из браузера/десктоп приложения обращаться к API
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],  # Разрешаем все HTTP методы (GET, POST, etc.)
        allow_headers=["*"],  # Разрешаем все заголовки
    )

# Подключаем роутеры
app.include_router(physical_router)
app.include_router(dictionary_router)

@app.get("/", tags=["root"])
async def root():
    """
    Корневой эндпоинт для проверки работы API
    
    Returns:
        dict: Приветственное сообщение
        
    Согласно ТЗ:
        {"message":"Markoff API is running"}
    """
    return {"message": "Markoff API is running"}

@app.get("/health", tags=["health"])
async def health_check():
    """
    Эндпоинт для проверки здоровья сервиса
    Используется Docker для healthcheck
    
    Returns:
        dict: Статус сервиса
    """
    return {"status": "healthy"}