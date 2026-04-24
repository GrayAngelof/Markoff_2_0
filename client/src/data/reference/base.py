# client/src/data/reference/base.py
"""
Базовый класс для всех реестров справочников.

Предоставляет общую функциональность:
- Загрузку данных через переданную функцию
- Хранение в словаре {id: DTO}
- Доступ по ID
- Проверку готовности (warmup)
- База не знает о структуре DTO (нет .name). Маппинг ID → человекочитаемое значение — ответственность Projections.
"""

# ===== ИМПОРТЫ =====
from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, Optional, Protocol, TypeVar, runtime_checkable


# ===== ПРОТОКОЛЫ =====
@runtime_checkable
class HasId(Protocol):
    """Протокол для объектов, имеющих атрибут id (только для чтения)."""

    @property
    def id(self) -> int:
        """Уникальный идентификатор."""
        ...


# ===== ТИПЫ =====
T = TypeVar('T', bound=HasId)


# ===== КЛАСС =====
class BaseRegistry(ABC, Generic[T]):
    """
    Базовый реестр для read-only справочников.

    Отвечает за:
    - Загрузку данных через переданную функцию
    - Хранение в словаре {id: DTO}
    - Доступ по ID

    Важно: Реестр не знает о структуре DTO (нет .name).
    Маппинг ID → человекочитаемое значение — ответственность Projections.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, loader: Callable[[], list[T]]) -> None:
        """
        Инициализирует реестр.

        Args:
            loader: Функция, которая загружает список DTO из API
        """
        self._loader = loader
        self._items: Dict[int, T] = {}
        self._is_ready: bool = False

    def warmup(self) -> None:
        """Загружает все элементы справочника."""
        items = self._loader()
        self._items = {item.id: item for item in items}
        self._is_ready = True
        self._log_result(len(items))

    # ---- ПУБЛИЧНОЕ API ----
    def is_ready(self) -> bool:
        """Проверяет, загружен ли реестр."""
        return self._is_ready

    def get(self, item_id: Optional[int]) -> Optional[T]:
        """
        Возвращает DTO по ID.

        Args:
            item_id: ID справочной записи (может быть None)

        Returns:
            DTO или None, если ID не найден

        Raises:
            RuntimeError: Если реестр не загружен (warmup не вызван)
        """
        if not self._is_ready:
            raise RuntimeError(f"{self.__class__.__name__} не загружен. Вызови warmup()")
        if item_id is None:
            return None
        return self._items.get(item_id)

    # ---- ЗАЩИЩЁННЫЕ МЕТОДЫ ----
    @abstractmethod
    def _log_result(self, count: int) -> None:
        """Логирует результат загрузки. Реализуется в наследниках."""
        pass