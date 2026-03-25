# utils/logger.py
"""
Профессиональный, лёгкий и настраиваемый логгер для приложения Markoff.

Особенности:
- Уровни логирования: ERROR, WARNING, INFO, DEBUG
- Категории: API, CACHE, DATA, DB, SYSTEM, PERFORMANCE
- Категории имеют свои собственные уровни, независимые от глобального
- Автоматическое определение имени модуля-источника
- Цветной вывод в терминал (автоматически определяется)
- Разделение форматирования и вывода (принцип единственной ответственности)
- Кэширование логгеров по модулям для производительности
- Контекстный менеджер для временного изменения уровня
- Измерение времени выполнения операций (всегда логируется при DEBUG или отдельно)
- Поддержка исключений с traceback

Пример использования:
    from src.utils.logger import get_logger, LogLevel, CategoryLevel
    
    logger = get_logger(__name__)
    logger.info("Сообщение")
    logger.error("Ошибка")
    logger.api("GET /api/data")
    
    # Настройка уровней для категорий
    Logger.set_category_level("api", LogLevel.INFO)
    Logger.set_category_level("performance", LogLevel.INFO)
    
    # Измерение времени выполнения
    with logger.measure_time("обработка данных"):
        # какой-то код
        pass
"""
from datetime import datetime
import sys
import traceback
import time
from typing import Optional, Set, Dict, TextIO, Union, Any
from contextlib import contextmanager
from enum import IntEnum


class LogLevel(IntEnum):
    """Уровни логирования."""
    ERROR = 1
    """Только критические ошибки"""
    
    WARNING = 2
    """Ошибки и предупреждения"""
    
    INFO = 3
    """Основная информация (по умолчанию)"""
    
    DEBUG = 4
    """Всё, включая отладочную информацию"""


class CategoryLevel:
    """
    Управление уровнями логирования для разных категорий.
    
    Каждая категория может иметь свой уровень, независимый от глобального.
    """
    
    # Категории и их уровни по умолчанию
    _default_levels = {
        "api": LogLevel.INFO,        # API запросы по умолчанию INFO
        "cache": LogLevel.DEBUG,     # Кэш по умолчанию DEBUG
        "data": LogLevel.INFO,       # Данные по умолчанию INFO
        "db": LogLevel.WARNING,      # База данных по умолчанию WARNING
        "system": LogLevel.INFO,     # Система по умолчанию INFO
        "performance": LogLevel.INFO # Производительность по умолчанию INFO
    }
    
    _levels: Dict[str, LogLevel] = _default_levels.copy()
    
    @classmethod
    def set_level(cls, category: str, level: LogLevel) -> None:
        """
        Устанавливает уровень логирования для категории.
        
        Args:
            category: Имя категории
            level: Уровень логирования
        """
        cls._levels[category] = level
    
    @classmethod
    def get_level(cls, category: str) -> LogLevel:
        """
        Возвращает уровень логирования для категории.
        
        Args:
            category: Имя категории
            
        Returns:
            LogLevel: Уровень логирования
        """
        return cls._levels.get(category, LogLevel.INFO)
    
    @classmethod
    def reset_to_defaults(cls) -> None:
        """Сбрасывает уровни категорий к значениям по умолчанию."""
        cls._levels = cls._default_levels.copy()


class LogFormatter:
    """
    Отвечает за форматирование сообщений лога.
    
    Добавляет временную метку, иконку, уровень, имя модуля и само сообщение.
    Поддерживает цветной вывод для терминалов.
    """
    
    # ===== Константы =====
    
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
    """Формат временной метки"""
    
    _MODULE_WIDTH = 30
    """Максимальная ширина имени модуля для выравнивания"""
    
    _LEVEL_WIDTH = 12
    """Ширина поля уровня для выравнивания"""
    
    def __init__(self, use_colors: bool = False) -> None:
        """
        Инициализирует форматтер логов.
        
        Args:
            use_colors: Включать ли цветной вывод
        """
        self._use_colors = use_colors and sys.stdout.isatty()
        """Флаг использования цветов (только для терминала)"""
    
    def format(self, level: str, module: str, message: str) -> str:
        """
        Форматирует сообщение лога.
        
        Args:
            level: Уровень или категория (ERROR, INFO, API, и т.д.)
            module: Имя модуля-источника
            message: Текст сообщения
            
        Returns:
            str: Отформатированная строка лога
        """
        # Формируем временную метку (с миллисекундами)
        timestamp = datetime.now().strftime(self._TIMESTAMP_FORMAT)[:-3]
        
        # Получаем иконку
        icon = self._ICONS.get(level, "•")
        
        # Форматируем имя модуля для отображения
        display_module = self._format_module_name(module)
        module_short = display_module[:self._MODULE_WIDTH]
        
        # Формируем строку лога
        log_line = (
            f"{timestamp} {icon} [{level:>{self._LEVEL_WIDTH}}] "
            f"[{module_short:<{self._MODULE_WIDTH}}] {message}"
        )
        
        # Добавляем цвета, если нужно
        if self._use_colors and level in self._COLOR_CODES:
            color = self._COLOR_CODES[level]
            reset = self._COLOR_CODES["RESET"]
            log_line = f"{color}{log_line}{reset}"
        
        return log_line
    
    def _format_module_name(self, module_name: str) -> str:
        """
        Форматирует имя модуля для отображения.
        
        Args:
            module_name: Полное имя модуля
            
        Returns:
            str: Отформатированное имя для отображения
        """
        # Убираем префикс 'src.' если есть
        if module_name.startswith("src."):
            module_name = module_name[4:]
        
        # Заменяем точки на слеши для лучшей читаемости
        return module_name.replace(".", "/")


class LogOutput:
    """
    Отвечает за вывод отформатированных сообщений.
    
    Позволяет перенаправлять вывод в разные потоки (файл, консоль и т.д.)
    """
    
    def __init__(self, stream: Optional[TextIO] = None) -> None:
        """
        Инициализирует вывод логов.
        
        Args:
            stream: Поток для вывода (по умолчанию sys.stdout)
        """
        self._stream = stream or sys.stdout
    
    def write(self, message: str) -> None:
        """
        Выводит сообщение в поток.
        
        Args:
            message: Сообщение для вывода
        """
        print(message, file=self._stream)
        self._stream.flush()  # Немедленный вывод
    
    def set_stream(self, stream: TextIO) -> None:
        """
        Изменяет поток вывода.
        
        Args:
            stream: Новый поток для вывода
        """
        self._stream = stream


class Logger:
    """
    Основной класс логгера для модулей приложения.
    
    Предоставляет методы для логирования с разными уровнями и категориями.
    Поддерживает глобальные настройки уровня и индивидуальные настройки категорий.
    
    Уровни (по возрастанию детализации):
    - ERROR: только ошибки
    - WARNING: ошибки и предупреждения
    - INFO: основная информация (по умолчанию)
    - DEBUG: отладочная информация
    
    Категории с собственными уровнями:
    - api: запросы к API (по умолчанию INFO)
    - cache: операции с кэшем (по умолчанию DEBUG)
    - data: работа с данными (по умолчанию INFO)
    - db: работа с базой данных (по умолчанию WARNING)
    - system: системные операции (по умолчанию INFO)
    - performance: метрики производительности (по умолчанию INFO)
    """
    
    # ===== Константы =====
    ERROR = LogLevel.ERROR
    WARNING = LogLevel.WARNING
    INFO = LogLevel.INFO
    DEBUG = LogLevel.DEBUG
    
    CATEGORIES = {"api", "cache", "data", "db", "system", "performance"}
    """Доступные категории логирования"""
    
    # ===== Глобальные настройки =====
    _level: LogLevel = LogLevel.INFO
    """Текущий уровень логирования"""
    
    _disabled_categories: Set[str] = set()
    """Множество отключённых категорий"""
    
    _formatter = LogFormatter(use_colors=False)
    """Форматтер сообщений"""
    
    _output = LogOutput()
    """Вывод сообщений"""
    
    _loggers: Dict[str, 'Logger'] = {}
    """Кэш созданных логгеров по именам модулей"""
    
    def __init__(self, module_name: str) -> None:
        """
        Инициализирует логгер для конкретного модуля.
        
        Args:
            module_name: Имя модуля (обычно __name__)
        """
        self._module_name = module_name
    
    @classmethod
    def get_logger(cls, module_name: str) -> 'Logger':
        """
        Возвращает или создаёт логгер для указанного модуля.
        
        Args:
            module_name: Имя модуля
            
        Returns:
            Logger: Экземпляр логгера
        """
        if module_name not in cls._loggers:
            cls._loggers[module_name] = Logger(module_name)
        return cls._loggers[module_name]
    
    # ===== Настройка логирования =====
    
    @classmethod
    def set_level(cls, level: LogLevel) -> None:
        """
        Устанавливает глобальный уровень логирования.
        
        Args:
            level: Уровень (Logger.ERROR, Logger.INFO и т.д.)
        """
        cls._level = level
    
    @classmethod
    def get_level(cls) -> LogLevel:
        """
        Возвращает текущий уровень логирования.
        
        Returns:
            LogLevel: Текущий уровень
        """
        return cls._level
    
    @classmethod
    def set_category_level(cls, category: str, level: LogLevel) -> None:
        """
        Устанавливает уровень логирования для конкретной категории.
        
        Args:
            category: Имя категории
            level: Уровень логирования
        """
        if category in cls.CATEGORIES:
            CategoryLevel.set_level(category, level)
    
    @classmethod
    def get_category_level(cls, category: str) -> LogLevel:
        """
        Возвращает уровень логирования для категории.
        
        Args:
            category: Имя категории
            
        Returns:
            LogLevel: Уровень логирования категории
        """
        return CategoryLevel.get_level(category)
    
    @classmethod
    def enable_colors(cls, enable: bool = True) -> None:
        """
        Включает или выключает цветной вывод.
        
        Args:
            enable: True - включить цвета, False - выключить
        """
        cls._formatter = LogFormatter(use_colors=enable)
    
    @classmethod
    def set_output_stream(cls, stream: TextIO) -> None:
        """
        Устанавливает поток для вывода логов.
        
        Args:
            stream: Поток вывода (sys.stdout, открытый файл и т.д.)
        """
        cls._output.set_stream(stream)
    
    @classmethod
    def disable_category(cls, category: str) -> None:
        """
        Отключает указанную категорию логирования.
        
        Args:
            category: Имя категории
        """
        if category in cls.CATEGORIES:
            cls._disabled_categories.add(category)
    
    @classmethod
    def enable_category(cls, category: str) -> None:
        """
        Включает указанную категорию логирования.
        
        Args:
            category: Имя категории
        """
        cls._disabled_categories.discard(category)
    
    @classmethod
    def is_category_enabled(cls, category: str) -> bool:
        """
        Проверяет, включена ли указанная категория.
        
        Args:
            category: Имя категории
            
        Returns:
            bool: True если категория включена
        """
        return category not in cls._disabled_categories
    
    @classmethod
    def is_debug_enabled(cls) -> bool:
        """
        Проверяет, включён ли DEBUG уровень.
        
        Returns:
            bool: True если DEBUG уровень активен
        """
        return cls._level >= cls.DEBUG
    
    @classmethod
    @contextmanager
    def temporary_level(cls, level: LogLevel):
        """
        Контекстный менеджер для временного изменения уровня логирования.
        
        Args:
            level: Временный уровень логирования
            
        Example:
            with Logger.temporary_level(Logger.DEBUG):
                logger.debug("Эта отладочная информация будет показана")
        """
        old_level = cls._level
        cls._level = level
        try:
            yield
        finally:
            cls._level = old_level
    
    # ===== Внутренние методы =====
    
    def _should_log(self, level: LogLevel, category: Optional[str] = None) -> bool:
        """
        Определяет, нужно ли логировать сообщение.
        
        Args:
            level: Уровень сообщения
            category: Категория (опционально)
            
        Returns:
            bool: True если нужно логировать
        """
        # Проверяем отключение категории
        if category and not self.is_category_enabled(category):
            return False
        
        # Для категорий используем их собственный уровень
        if category:
            category_level = CategoryLevel.get_level(category)
            return level.value <= category_level.value
        
        # Для обычных уровней используем глобальный уровень
        return level.value <= self._level.value
    
    def _log(self, level_name: str, level: LogLevel, 
             message: Union[str, Any], category: Optional[str] = None) -> None:
        """
        Внутренний метод логирования.
        
        Args:
            level_name: Название уровня для отображения
            level: Уровень сообщения
            message: Сообщение для логирования
            category: Категория (опционально)
        """
        # Преобразуем сообщение в строку, если это не строка
        if not isinstance(message, str):
            message = str(message)
        
        # Проверяем, нужно ли логировать
        if not self._should_log(level, category):
            return
        
        # Форматируем и выводим
        formatted = self._formatter.format(level_name, self._module_name, message)
        self._output.write(formatted)
    
    # ===== Основные уровни логирования =====
    
    def error(self, message: Union[str, Exception]) -> None:
        """
        Логирует ошибку (всегда показывается при уровне ERROR и выше).
        
        Args:
            message: Сообщение об ошибке или исключение
        """
        self._log("ERROR", LogLevel.ERROR, message)
    
    def exception(self, message: str) -> None:
        """
        Логирует ошибку с полным traceback (для отладки).
        
        Args:
            message: Сообщение об ошибке
        """
        exc_info = traceback.format_exc()
        if exc_info and exc_info != "NoneType: None\n":
            full_message = f"{message}\n{exc_info}"
        else:
            full_message = message
        self._log("ERROR", LogLevel.ERROR, full_message)
    
    def warning(self, message: Union[str, Any]) -> None:
        """
        Логирует предупреждение.
        
        Args:
            message: Предупреждение
        """
        self._log("WARNING", LogLevel.WARNING, message)
    
    def info(self, message: Union[str, Any]) -> None:
        """
        Логирует информационное сообщение.
        
        Args:
            message: Информация
        """
        self._log("INFO", LogLevel.INFO, message)
    
    def success(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение об успехе (уровень INFO).
        
        Args:
            message: Сообщение об успехе
        """
        self._log("SUCCESS", LogLevel.INFO, message)
    
    def debug(self, message: Union[str, Any]) -> None:
        """
        Логирует отладочное сообщение.
        
        Args:
            message: Отладочная информация
        """
        self._log("DEBUG", LogLevel.DEBUG, message)
    
    # ===== Категории с собственными уровнями =====
    
    def api(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение категории API.
        Уровень логирования для API можно настроить отдельно.
        
        Args:
            message: Информация о запросе к API
        """
        self._log("API", CategoryLevel.get_level("api"), message, category="api")
    
    def data(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение категории DATA.
        Уровень логирования для DATA можно настроить отдельно.
        
        Args:
            message: Информация о работе с данными
        """
        self._log("DATA", CategoryLevel.get_level("data"), message, category="data")
    
    def cache(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение категории CACHE.
        Уровень логирования для CACHE можно настроить отдельно.
        
        Args:
            message: Информация о кэшировании
        """
        self._log("CACHE", CategoryLevel.get_level("cache"), message, category="cache")
    
    def db(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение категории DB (база данных).
        Уровень логирования для DB можно настроить отдельно.
        
        Args:
            message: Информация о работе с базой данных
        """
        self._log("DB", CategoryLevel.get_level("db"), message, category="db")

    def link(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение категории LINK (подписки, связи между компонентами).
        
        Args:
            message: Информация о связи/подписке
        """
        self._log("LINK", CategoryLevel.get_level("link"), message, category="link")
    
    def system(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение категории SYSTEM.
        Уровень логирования для SYSTEM можно настроить отдельно.
        
        Args:
            message: Информация о системных операциях
        """
        self._log("SYSTEM", CategoryLevel.get_level("system"), message, category="system")
    
    def performance(self, message: Union[str, Any]) -> None:
        """
        Логирует сообщение категории PERFORMANCE (метрики производительности).
        Уровень логирования для PERFORMANCE можно настроить отдельно.
        
        Args:
            message: Метрика производительности
        """
        self._log("PERFORMANCE", CategoryLevel.get_level("performance"), message, category="performance")
    
    # ===== Специальные события =====
    
    def startup(self, message: Union[str, Any]) -> None:
        """
        Логирует событие запуска приложения.
        
        Args:
            message: Информация о запуске
        """
        self._log("STARTUP", LogLevel.INFO, message)
    
    def shutdown(self, message: Union[str, Any]) -> None:
        """
        Логирует событие завершения приложения.
        
        Args:
            message: Информация о завершении
        """
        self._log("SHUTDOWN", LogLevel.INFO, message)
    
    # ===== Вспомогательные методы =====
    
    @contextmanager
    def measure_time(self, operation_name: str, level: Optional[LogLevel] = None):
        """
        Контекстный менеджер для измерения времени выполнения операции.
        
        Args:
            operation_name: Название операции
            level: Уровень логирования (если не указан, используется уровень категории performance)
            
        Example:
            # Будет логироваться на уровне INFO (если так настроено)
            with logger.measure_time("загрузка данных"):
                data = load_data()
            
            # Принудительно логировать на DEBUG
            with logger.measure_time("детальная операция", level=LogLevel.DEBUG):
                process_data()
        """
        start = time.time()
        try:
            yield
        finally:
            elapsed = (time.time() - start) * 1000
            
            # Определяем уровень для логирования
            log_level = level or CategoryLevel.get_level("performance")
            
            # Логируем через performance категорию
            if log_level == LogLevel.DEBUG:
                self.performance(f"{operation_name} выполнена за {elapsed:.2f}ms")
            elif log_level == LogLevel.INFO:
                self.performance(f"{operation_name} выполнена за {elapsed:.2f}ms")
            elif log_level == LogLevel.WARNING:
                # Для медленных операций можно использовать WARNING
                if elapsed > 1000:  # больше секунды
                    self.performance(f"⚠️ {operation_name} выполнена медленно за {elapsed:.2f}ms")
                else:
                    self.performance(f"{operation_name} выполнена за {elapsed:.2f}ms")
            else:
                self.performance(f"{operation_name} выполнена за {elapsed:.2f}ms")


# ===== Быстрый доступ =====

def get_logger(module_name: str) -> Logger:
    """
    Возвращает логгер для указанного модуля.
    
    Args:
        module_name: Имя модуля (обычно __name__)
        
    Returns:
        Logger: Экземпляр логгера
        
    Example:
        logger = get_logger(__name__)
        logger.info("Сообщение")
    """
    return Logger.get_logger(module_name)


# ===== Инициализация по умолчанию =====

# Включаем цвета для интерактивных терминалов
Logger.enable_colors(True)