# client/src/utils/logger.py
"""
Профессиональный, лёгкий и настраиваемый логгер для приложения Markoff.

Особенности:
- Уровни логирования: ERROR, WARNING, INFO, DEBUG
- Категории: API, CACHE, DATA (можно включать/отключать)
- Автоматическое определение имени модуля-источника
- Цветной вывод в терминал (автоматически определяется)
- Разделение форматирования и вывода (принцип единственной ответственности)
- Кэширование логгеров по модулям для производительности

Пример использования:
    from src.utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Сообщение")
    logger.error("Ошибка")
    logger.api("GET /api/data")
"""
from datetime import datetime
import sys
from typing import Optional, Set, Dict, TextIO


class LogFormatter:
    """
    Отвечает за форматирование сообщений лога.
    
    Добавляет временную метку, иконку, уровень, имя модуля и само сообщение.
    Поддерживает цветной вывод для терминалов.
    """
    
    # ===== Константы =====
    
    # Коды цветов ANSI
    _COLOR_CODES: Dict[str, str] = {
        "ERROR": "\033[91m",    # Красный
        "WARNING": "\033[93m",   # Жёлтый
        "INFO": "\033[94m",      # Синий
        "SUCCESS": "\033[92m",   # Зелёный
        "DEBUG": "\033[90m",     # Серый
        "API": "\033[96m",       # Голубой
        "CACHE": "\033[95m",     # Фиолетовый
        "DATA": "\033[36m",      # Бирюзовый
        "STARTUP": "\033[95m",   # Фиолетовый
        "SHUTDOWN": "\033[91m",  # Красный
        "RESET": "\033[0m",      # Сброс цвета
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
        "STARTUP": "🚀",
        "SHUTDOWN": "👋",
    }
    
    _TIMESTAMP_FORMAT = "%H:%M:%S.%f"
    """Формат временной метки"""
    
    _MODULE_WIDTH = 20
    """Максимальная ширина имени модуля для выравнивания"""
    
    _LEVEL_WIDTH = 7
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
        # Формируем временную метку
        timestamp = datetime.now().strftime(self._TIMESTAMP_FORMAT)[:-3]
        
        # Получаем иконку
        icon = self._ICONS.get(level, "•")
        
        # Укорачиваем имя модуля для выравнивания
        module_short = module.split(".")[-1][:self._MODULE_WIDTH]
        
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


class LogOutput:
    """
    Отвечает за вывод отформатированных сообщений.
    
    Позволяет перенаправлять вывод в разные потоки (файл, консоль и т.д.)
    """
    
    def __init__(self, stream: TextIO = sys.stdout) -> None:
        """
        Инициализирует вывод логов.
        
        Args:
            stream: Поток для вывода (по умолчанию sys.stdout)
        """
        self._stream = stream
    
    def write(self, message: str) -> None:
        """
        Выводит сообщение в поток.
        
        Args:
            message: Сообщение для вывода
        """
        print(message, file=self._stream)
    
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
    Поддерживает глобальные настройки уровня и отключение категорий.
    
    Уровни (по возрастанию детализации):
    - ERROR: только ошибки
    - WARNING: ошибки и предупреждения
    - INFO: основная информация (по умолчанию)
    - DEBUG: отладочная информация
    
    Категории:
    - api: запросы к API
    - cache: операции с кэшем
    - data: работа с данными
    """
    
    # ===== Константы уровней =====
    ERROR = 1
    """Только критические ошибки"""
    
    WARNING = 2
    """Ошибки и предупреждения"""
    
    INFO = 3
    """Основная информация (по умолчанию)"""
    
    DEBUG = 4
    """Всё, включая отладочную информацию"""
    
    # ===== Константы категорий =====
    CATEGORIES = {"api", "cache", "data"}
    """Доступные категории логирования"""
    
    # ===== Глобальные настройки =====
    _level: int = INFO
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
    def set_level(cls, level: int) -> None:
        """
        Устанавливает глобальный уровень логирования.
        
        Args:
            level: Уровень (Logger.ERROR, Logger.INFO и т.д.)
        """
        cls._level = level
    
    @classmethod
    def get_level(cls) -> int:
        """
        Возвращает текущий уровень логирования.
        
        Returns:
            int: Текущий уровень
        """
        return cls._level
    
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
            category: Имя категории ('api', 'cache', 'data')
        """
        if category in cls.CATEGORIES:
            cls._disabled_categories.add(category)
    
    @classmethod
    def enable_category(cls, category: str) -> None:
        """
        Включает указанную категорию логирования.
        
        Args:
            category: Имя категории ('api', 'cache', 'data')
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
    
    # ===== Внутренние методы =====
    
    def _log(self, level_name: str, level_val: int, 
             message: str, category: Optional[str] = None) -> None:
        """
        Внутренний метод логирования.
        
        Args:
            level_name: Название уровня для отображения
            level_val: Числовое значение уровня
            message: Сообщение для логирования
            category: Категория (опционально)
        """
        # Проверяем уровень
        if level_val > self._level:
            return
        
        # Проверяем категорию
        if category and not self.is_category_enabled(category):
            return
        
        # Форматируем и выводим
        formatted = self._formatter.format(level_name, self._module_name, message)
        self._output.write(formatted)
    
    # ===== Основные уровни логирования =====
    
    def error(self, message: str) -> None:
        """
        Логирует ошибку (всегда показывается).
        
        Args:
            message: Сообщение об ошибке
        """
        self._log("ERROR", self.ERROR, message)
    
    def warning(self, message: str) -> None:
        """
        Логирует предупреждение.
        
        Args:
            message: Предупреждение
        """
        self._log("WARNING", self.WARNING, message)
    
    def info(self, message: str) -> None:
        """
        Логирует информационное сообщение.
        
        Args:
            message: Информация
        """
        self._log("INFO", self.INFO, message)
    
    def success(self, message: str) -> None:
        """
        Логирует сообщение об успехе (уровень INFO).
        
        Args:
            message: Сообщение об успехе
        """
        self._log("SUCCESS", self.INFO, message)
    
    def debug(self, message: str) -> None:
        """
        Логирует отладочное сообщение.
        
        Args:
            message: Отладочная информация
        """
        self._log("DEBUG", self.DEBUG, message)
    
    # ===== Категории =====
    
    def api(self, message: str) -> None:
        """
        Логирует сообщение категории API.
        
        Args:
            message: Информация о запросе к API
        """
        self._log("API", self.INFO, message, category="api")
    
    def data(self, message: str) -> None:
        """
        Логирует сообщение категории DATA.
        
        Args:
            message: Информация о работе с данными
        """
        self._log("DATA", self.INFO, message, category="data")
    
    def cache(self, message: str) -> None:
        """
        Логирует сообщение категории CACHE.
        
        Args:
            message: Информация о кэшировании
        """
        self._log("CACHE", self.INFO, message, category="cache")
    
    # ===== Специальные события =====
    
    def startup(self, message: str) -> None:
        """
        Логирует событие запуска приложения.
        
        Args:
            message: Информация о запуске
        """
        self._log("STARTUP", self.INFO, message)
    
    def shutdown(self, message: str) -> None:
        """
        Логирует событие завершения приложения.
        
        Args:
            message: Информация о завершении
        """
        self._log("SHUTDOWN", self.INFO, message)


# ===== Быстрый доступ =====

def get_logger(module_name: str) -> Logger:
    """
    Возвращает логгер для указанного модуля.
    
    Args:
        module_name: Имя модуля (обычно __name__)
        
    Returns:
        Logger: Экземпляр логгера
        
    Пример:
        logger = get_logger(__name__)
        logger.info("Сообщение")
    """
    return Logger.get_logger(module_name)