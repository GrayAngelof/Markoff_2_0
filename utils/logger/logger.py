# utils/logger.py
"""
Профессиональный, лёгкий и настраиваемый логгер для приложения Markoff.

Особенности:
- Уровни логирования: ERROR, WARNING, INFO, DEBUG
- Категории: API, CACHE, DATA, DB, SYSTEM, PERFORMANCE, LINK
- Категории имеют свои собственные уровни
- Автоматическое определение имени модуля-источника
- Цветной вывод в терминал
- Кэширование логгеров по модулям
- Измерение времени выполнения операций
- Поддержка исключений с traceback
"""

# ===== ИМПОРТЫ =====
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional, Set, TextIO, Union


# ===== КОНСТАНТЫ =====
class LogLevel(IntEnum):
    """Уровни логирования."""
    ERROR = 1      # Только критические ошибки
    WARNING = 2    # Ошибки и предупреждения
    INFO = 3       # Основная информация (по умолчанию)
    DEBUG = 4      # Всё, включая отладочную информацию


# ===== КАТЕГОРИИ =====
class CategoryLevel:
    """
    Управление уровнями логирования для разных категорий.

    Каждая категория может иметь свой уровень, независимый от глобального.
    """

    # Категории и их уровни по умолчанию
    _default_levels: Dict[str, LogLevel] = {
        "api": LogLevel.INFO,         # API запросы
        "cache": LogLevel.DEBUG,      # Кэш
        "data": LogLevel.INFO,        # Данные
        "db": LogLevel.WARNING,       # База данных
        "system": LogLevel.INFO,      # Система
        "performance": LogLevel.INFO, # Производительность
        "link": LogLevel.INFO,        # Связи между компонентами
    }

    _levels: Dict[str, LogLevel] = _default_levels.copy()

    @classmethod
    def set_level(cls, category: str, level: LogLevel) -> None:
        """Устанавливает уровень логирования для категории."""
        cls._levels[category] = level

    @classmethod
    def get_level(cls, category: str) -> LogLevel:
        """Возвращает уровень логирования для категории."""
        return cls._levels.get(category, LogLevel.INFO)

    @classmethod
    def reset_to_defaults(cls) -> None:
        """Сбрасывает уровни категорий к значениям по умолчанию."""
        cls._levels = cls._default_levels.copy()


# ===== ФОРМАТТЕР =====
class LogFormatter:
    """
    Отвечает за форматирование сообщений лога.

    Добавляет временную метку, иконку, уровень, имя модуля и сообщение.
    Поддерживает цветной вывод для терминалов.
    """

    # Коды цветов ANSI
    _COLOR_CODES: Dict[str, str] = {
        "ERROR": "\033[91m",      # Красный
        "WARNING": "\033[93m",     # Жёлтый
        "INFO": "\033[94m",        # Синий
        "SUCCESS": "\033[92m",     # Зелёный
        "DEBUG": "\033[90m",       # Серый
        "API": "\033[96m",         # Голубой
        "CACHE": "\033[95m",       # Фиолетовый
        "DATA": "\033[36m",        # Бирюзовый
        "DB": "\033[33m",          # Жёлто-оранжевый
        "SYSTEM": "\033[35m",      # Маджента
        "PERFORMANCE": "\033[33m", # Жёлтый
        "STARTUP": "\033[95m",     # Фиолетовый
        "SHUTDOWN": "\033[91m",    # Красный
        "LINK": "\033[96m",        # Голубой
        "RESET": "\033[0m",        # Сброс цвета
    }

    # Иконки для разных уровней и категорий
    _ICONS: Dict[str, str] = {
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "DEBUG": "🔧",
        "API": "📡",
        "DATA": "📦",
        "CACHE": "💾",
        "DB": "🗄️",
        "SYSTEM": "⚙️",
        "PERFORMANCE": "⏱️",
        "STARTUP": "🚀",
        "SHUTDOWN": "👋",
        "LINK": "🔗",
    }

    _TIMESTAMP_FORMAT = "%H:%M:%S.%f"
    _MODULE_WIDTH = 30
    _LEVEL_WIDTH = 12

    def __init__(self, use_colors: bool = False) -> None:
        """Инициализирует форматтер логов."""
        self._use_colors = use_colors and sys.stdout.isatty()

    def format(self, level: str, module: str, message: str) -> str:
        """Форматирует сообщение лога."""
        timestamp = datetime.now().strftime(self._TIMESTAMP_FORMAT)[:-3]
        icon = self._ICONS.get(level, "•")

        display_module = self._format_module_name(module)
        module_short = display_module[:self._MODULE_WIDTH]

        log_line = (
            f"{timestamp} {icon} [{level:>{self._LEVEL_WIDTH}}] "
            f"[{module_short:<{self._MODULE_WIDTH}}] {message}"
        )

        if self._use_colors and level in self._COLOR_CODES:
            log_line = f"{self._COLOR_CODES[level]}{log_line}{self._COLOR_CODES['RESET']}"

        return log_line

    def _format_module_name(self, module_name: str) -> str:
        """Форматирует имя модуля для отображения."""
        if module_name.startswith("src."):
            module_name = module_name[4:]
        return module_name.replace(".", "/")


# ===== ВЫВОД =====
class LogOutput:
    """Отвечает за вывод отформатированных сообщений."""

    def __init__(self, stream: Optional[TextIO] = None) -> None:
        """Инициализирует вывод логов."""
        self._stream = stream or sys.stdout

    def write(self, message: str) -> None:
        """Выводит сообщение в поток."""
        print(message, file=self._stream)
        self._stream.flush()

    def set_stream(self, stream: TextIO) -> None:
        """Изменяет поток вывода."""
        self._stream = stream


# ===== ЛОГГЕР =====
class Logger:
    """
    Основной класс логгера для модулей приложения.

    Предоставляет методы для логирования с разными уровнями и категориями.
    """

    ERROR = LogLevel.ERROR
    WARNING = LogLevel.WARNING
    INFO = LogLevel.INFO
    DEBUG = LogLevel.DEBUG

    CATEGORIES = {"api", "cache", "data", "db", "system", "performance", "link"}

    _level: LogLevel = LogLevel.INFO
    _disabled_categories: Set[str] = set()
    _formatter = LogFormatter(use_colors=False)
    _output = LogOutput()
    _loggers: Dict[str, 'Logger'] = {}

    def __init__(self, module_name: str) -> None:
        """Инициализирует логгер для конкретного модуля."""
        self._module_name = module_name

    @classmethod
    def get_logger(cls, module_name: str) -> 'Logger':
        """Возвращает или создаёт логгер для указанного модуля."""
        if module_name not in cls._loggers:
            cls._loggers[module_name] = Logger(module_name)
        return cls._loggers[module_name]

    # ---- НАСТРОЙКА ----
    @classmethod
    def set_level(cls, level: LogLevel) -> None:
        """Устанавливает глобальный уровень логирования."""
        cls._level = level

    @classmethod
    def get_level(cls) -> LogLevel:
        """Возвращает текущий уровень логирования."""
        return cls._level

    @classmethod
    def set_category_level(cls, category: str, level: LogLevel) -> None:
        """Устанавливает уровень логирования для категории."""
        if category in cls.CATEGORIES:
            CategoryLevel.set_level(category, level)

    @classmethod
    def get_category_level(cls, category: str) -> LogLevel:
        """Возвращает уровень логирования для категории."""
        return CategoryLevel.get_level(category)

    @classmethod
    def enable_colors(cls, enable: bool = True) -> None:
        """Включает или выключает цветной вывод."""
        cls._formatter = LogFormatter(use_colors=enable)

    @classmethod
    def set_output_stream(cls, stream: TextIO) -> None:
        """Устанавливает поток для вывода логов."""
        cls._output.set_stream(stream)

    @classmethod
    def disable_category(cls, category: str) -> None:
        """Отключает указанную категорию логирования."""
        if category in cls.CATEGORIES:
            cls._disabled_categories.add(category)

    @classmethod
    def enable_category(cls, category: str) -> None:
        """Включает указанную категорию логирования."""
        cls._disabled_categories.discard(category)

    @classmethod
    def is_category_enabled(cls, category: str) -> bool:
        """Проверяет, включена ли указанная категория."""
        return category not in cls._disabled_categories

    @classmethod
    def is_debug_enabled(cls) -> bool:
        """Проверяет, включён ли DEBUG уровень."""
        return cls._level >= cls.DEBUG

    @classmethod
    @contextmanager
    def temporary_level(cls, level: LogLevel):
        """Временно изменяет уровень логирования."""
        old_level = cls._level
        cls._level = level
        try:
            yield
        finally:
            cls._level = old_level

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _should_log(self, level: LogLevel, category: Optional[str] = None) -> bool:
        """Определяет, нужно ли логировать сообщение."""
        if category and not self.is_category_enabled(category):
            return False

        if category:
            return level.value <= CategoryLevel.get_level(category).value

        return level.value <= self._level.value

    def _log(self, level_name: str, level: LogLevel, message: Union[str, Any],
             category: Optional[str] = None) -> None:
        """Внутренний метод логирования."""
        if not isinstance(message, str):
            message = str(message)

        if not self._should_log(level, category):
            return

        formatted = self._formatter.format(level_name, self._module_name, message)
        self._output.write(formatted)

    # ---- ОСНОВНЫЕ УРОВНИ ----
    def error(self, message: Union[str, Exception]) -> None:
        """Логирует ошибку."""
        self._log("ERROR", LogLevel.ERROR, message)

    def exception(self, message: str) -> None:
        """Логирует ошибку с полным traceback."""
        exc_info = traceback.format_exc()
        if exc_info and exc_info != "NoneType: None\n":
            full_message = f"{message}\n{exc_info}"
        else:
            full_message = message
        self._log("ERROR", LogLevel.ERROR, full_message)

    def warning(self, message: Union[str, Any]) -> None:
        """Логирует предупреждение."""
        self._log("WARNING", LogLevel.WARNING, message)

    def info(self, message: Union[str, Any]) -> None:
        """Логирует информационное сообщение."""
        self._log("INFO", LogLevel.INFO, message)

    def success(self, message: Union[str, Any]) -> None:
        """Логирует сообщение об успехе."""
        self._log("SUCCESS", LogLevel.INFO, message)

    def debug(self, message: Union[str, Any]) -> None:
        """Логирует отладочное сообщение."""
        self._log("DEBUG", LogLevel.DEBUG, message)

    # ---- КАТЕГОРИИ ----
    def api(self, message: Union[str, Any]) -> None:
        """Логирует сообщение категории API."""
        self._log("API", CategoryLevel.get_level("api"), message, category="api")

    def data(self, message: Union[str, Any]) -> None:
        """Логирует сообщение категории DATA."""
        self._log("DATA", CategoryLevel.get_level("data"), message, category="data")

    def cache(self, message: Union[str, Any]) -> None:
        """Логирует сообщение категории CACHE."""
        self._log("CACHE", CategoryLevel.get_level("cache"), message, category="cache")

    def db(self, message: Union[str, Any]) -> None:
        """Логирует сообщение категории DB."""
        self._log("DB", CategoryLevel.get_level("db"), message, category="db")

    def link(self, message: Union[str, Any]) -> None:
        """Логирует сообщение категории LINK."""
        self._log("LINK", CategoryLevel.get_level("link"), message, category="link")

    def system(self, message: Union[str, Any]) -> None:
        """Логирует сообщение категории SYSTEM."""
        self._log("SYSTEM", CategoryLevel.get_level("system"), message, category="system")

    def performance(self, message: Union[str, Any]) -> None:
        """Логирует сообщение категории PERFORMANCE."""
        self._log("PERFORMANCE", CategoryLevel.get_level("performance"), message, category="performance")

    # ---- СПЕЦИАЛЬНЫЕ СОБЫТИЯ ----
    def startup(self, message: Union[str, Any]) -> None:
        """Логирует событие запуска приложения."""
        self._log("STARTUP", LogLevel.INFO, message)

    def shutdown(self, message: Union[str, Any]) -> None:
        """Логирует событие завершения приложения."""
        self._log("SHUTDOWN", LogLevel.INFO, message)

    # ---- ИЗМЕРЕНИЕ ВРЕМЕНИ ----
    @contextmanager
    def measure_time(self, operation_name: str, level: Optional[LogLevel] = None):
        """Измеряет время выполнения операции."""
        start = time.time()
        try:
            yield
        finally:
            elapsed = (time.time() - start) * 1000
            log_level = level or CategoryLevel.get_level("performance")
            self.performance(f"{operation_name} выполнена за {elapsed:.2f}ms")


# ===== БЫСТРЫЙ ДОСТУП =====
def get_logger(module_name: str) -> Logger:
    """Возвращает логгер для указанного модуля."""
    return Logger.get_logger(module_name)


# ===== ИНИЦИАЛИЗАЦИЯ ПО УМОЛЧАНИЮ =====
Logger.enable_colors(True)