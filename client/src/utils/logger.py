# client/src/utils/logger.py
"""
Простой логгер для приложения
Уровни логирования:
- ERROR: только ошибки (всегда включено)
- INFO: важные события (можно включить/выключить)
- DEBUG: отладочная информация (по умолчанию выключено)
"""
from datetime import datetime
from typing import Optional


class Logger:
    """Простой логгер с поддержкой уровней"""
    
    # Уровни логирования
    ERROR = 1   # всегда включено
    INFO = 2    # можно включить/выключить
    DEBUG = 3   # отладочная информация
    
    # Текущий уровень (можно менять извне)
    level = INFO  # По умолчанию показываем INFO и ERROR
    
    # Эмодзи для разных типов сообщений
    ICONS = {
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "success": "✅",
        "debug": "🔧",
        "api": "📡",
        "data": "📦",
        "cache": "💾",
    }
    
    @classmethod
    def set_level(cls, level: int):
        """Установить уровень логирования"""
        cls.level = level
    
    @classmethod
    def _log(cls, message: str, msg_level: int, icon: str = "info"):
        """Внутренний метод логирования"""
        if msg_level <= cls.level:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            icon_char = cls.ICONS.get(icon, "•")
            print(f"{icon_char} {message}")
    
    @classmethod
    def error(cls, message: str):
        """Критические ошибки (всегда показываем)"""
        cls._log(message, cls.ERROR, "error")
    
    @classmethod
    def warning(cls, message: str):
        """Предупреждения (всегда показываем)"""
        cls._log(message, cls.ERROR, "warning")
    
    @classmethod
    def info(cls, message: str):
        """Важные информационные сообщения"""
        cls._log(message, cls.INFO, "info")
    
    @classmethod
    def success(cls, message: str):
        """Успешные операции"""
        cls._log(message, cls.INFO, "success")
    
    @classmethod
    def debug(cls, message: str):
        """Отладочная информация (по умолчанию выключено)"""
        cls._log(message, cls.DEBUG, "debug")
    
    @classmethod
    def api(cls, message: str):
        """API запросы/ответы"""
        cls._log(message, cls.INFO, "api")
    
    @classmethod
    def data(cls, message: str):
        """Работа с данными"""
        cls._log(message, cls.INFO, "data")
    
    @classmethod
    def cache(cls, message: str):
        """Кэширование"""
        cls._log(message, cls.INFO, "cache")