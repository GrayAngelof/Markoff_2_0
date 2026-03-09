# utils/Tester/common/test_common.py
"""
Единая база для всех тестов проекта.
Содержит декоратор @test и вспомогательные утилиты.
"""

import inspect
from dataclasses import dataclass
from typing import Callable, Optional, Set, Union
from pathlib import Path
from enum import Enum, auto
from functools import wraps

# Импортируем модель теста (циклический импорт? нужно проверить)
# from ..core.models import TestFunction


class TestMarker(Enum):
    """Стандартные маркеры для тестов"""
    SMOKE = auto()      # Быстрая проверка работоспособности
    REGRESSION = auto() # Проверка регрессий
    SLOW = auto()       # Медленные тесты
    NETWORK = auto()    # Тесты, требующие сети
    DATABASE = auto()   # Тесты, требующие БД
    INTEGRATION = auto() # Интеграционные тесты
    UNIT = auto()       # Модульные тесты
    FLAKY = auto()      # Нестабильные тесты
    SKIP = auto()       # Пропущенные тесты


@dataclass(frozen=True)
class TestMetadata:
    """Иммутабельные метаданные теста"""
    description: str = ""
    markers: frozenset[TestMarker] = frozenset()
    expected_failure: bool = False
    timeout: Optional[int] = None


def test(description: str = "", 
         markers: Optional[Set[Union[TestMarker, str]]] = None,
         expected_failure: bool = False,
         timeout: Optional[int] = None):
    """
    Декоратор для пометки функции как теста.
    
    Args:
        description: Описание теста (будет показано в отчете)
        markers: Набор маркеров для категоризации
        expected_failure: True если тест ожидаемо падает
        timeout: Специфичный таймаут для этого теста (в секундах)
    
    Example:
        @test("Проверка базовой подписки", markers={TestMarker.SMOKE, "fast"})
        def test_basic_subscription():
            ...
    """
    # Нормализуем маркеры
    normalized_markers = set()
    if markers:
        for m in markers:
            if isinstance(m, str):
                # Пробуем преобразовать строку в enum
                try:
                    normalized_markers.add(TestMarker[m.upper()])
                except KeyError:
                    # Если нет в enum, создаем кастомный маркер как строку
                    # Но лучше все-таки использовать enum
                    normalized_markers.add(m)
            else:
                normalized_markers.add(m)
    
    # Создаем иммутабельные метаданные
    metadata = TestMetadata(
        description=description,
        markers=frozenset(normalized_markers),
        expected_failure=expected_failure,
        timeout=timeout
    )
    
    def decorator(func: Callable) -> Callable:
        # Добавляем метаданные прямо в функцию
        func._test_metadata = metadata
        
        # Сохраняем описание как docstring, если его нет
        if description and not func.__doc__:
            func.__doc__ = description
        
        return func
    
    return decorator


# ========== Предикаты ==========

def is_test_function(obj) -> bool:
    """Проверяет, является ли объект тестовой функцией"""
    return hasattr(obj, '_test_metadata')


# ========== Чистые функции для интроспекции ==========

def extract_file_path(func) -> Optional[Path]:
    """Извлекает путь к файлу из функции"""
    try:
        # Сначала пробуем getsourcefile (возвращает исходник)
        source_file = inspect.getsourcefile(func)
        if source_file:
            return Path(source_file).resolve()
        
        # Fallback на getfile (возвращает файл, где определен объект)
        file_path = inspect.getfile(func)
        return Path(file_path).resolve()
    except (TypeError, OSError):
        return None


def extract_line_number(func) -> Optional[int]:
    """Извлекает номер строки определения функции"""
    try:
        return inspect.getsourcelines(func)[1]
    except (OSError, TypeError):
        return None


# ========== Фабрика для создания TestFunction ==========

def create_test_function(func: Callable):
    """
    Создает объект TestFunction из тестовой функции.
    Используется в discovery.py.
    
    Args:
        func: Функция, помеченная декоратором @test
        
    Returns:
        TestFunction: объект теста для системы тестирования
    """
    # Отложенный импорт для избежания циклических зависимостей
    from ..core.models import TestFunction
    
    if not is_test_function(func):
        raise ValueError(f"Функция {func.__name__} не является тестом")
    
    metadata = func._test_metadata
    
    return TestFunction(
        name=func.__name__,
        description=metadata.description,
        func=func,
        module_path=func.__module__,
        file_path=extract_file_path(func),
        line_number=extract_line_number(func),
        markers=metadata.markers,
        expected_failure=metadata.expected_failure,
        timeout=metadata.timeout
    )


# ========== Утилиты для тестов ==========

class TestHandler:
    """Базовый обработчик событий с подсчетом"""
    
    def __init__(self, name: str):
        self.name = name
        self.events = []
        # self.logger = get_logger(f"TestHandler.{name}")
    
    def handle(self, event):
        self.events.append(event)
    
    def count(self, event_type: str = None) -> int:
        if event_type:
            return sum(1 for e in self.events if e.get('type') == event_type)
        return len(self.events)
    
    def clear(self):
        self.events.clear()
    
    def last(self):
        """Возвращает последнее событие"""
        return self.events[-1] if self.events else None


def assert_event_count(handler: TestHandler, expected: int, event_type: str = None):
    """Проверяет количество полученных событий"""
    actual = handler.count(event_type)
    assert actual == expected, \
        f"Ожидалось {expected} событий {event_type or 'любых'}, получено {actual}"


def assert_event_contains(handler: TestHandler, expected_data: dict):
    """Проверяет, что последнее событие содержит ожидаемые данные"""
    last = handler.last()
    assert last is not None, "Нет событий"
    
    for key, value in expected_data.items():
        assert last.get(key) == value, \
            f"Поле {key}: ожидалось {value}, получено {last.get(key)}"


# Константы для тестов (пример, потом можно расширить)
TEST_EVENT = "test.event"
TEST_TOPIC = "test.topic"