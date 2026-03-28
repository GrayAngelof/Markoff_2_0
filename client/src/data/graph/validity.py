# client/src/data/graph/validity.py
"""
Индекс валидности данных — отслеживание актуальности сущностей.

ValidityIndex отвечает только за одно: знать, какие данные актуальны,
а какие требуют перезагрузки.

Принципы:
    - Хранит множества валидных ID для каждого типа
    - Позволяет точечно или веточно помечать данные как невалидные
    - Все операции потокобезопасны (RLock)
    - Для веточной инвалидации использует итеративный обход (не рекурсию)

ВАЖНО:
    ValidityIndex не знает о связях между сущностями.
    Для рекурсивной инвалидации ветки он получает функцию get_children_fn,
    которая предоставляется извне (из RelationIndex через EntityGraph).
"""

# ===== ИМПОРТЫ =====
from collections import deque
from threading import RLock
from typing import Callable, Dict, Final, Iterable, List, Set, TypedDict

from src.core import EventBus
from src.core.events import DataInvalidated
from src.core.hierarchy import get_child_type
from src.core.types import NodeType
from src.shared.validation import validate_positive_int
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

# Все типы, которые могут быть в индексе валидности
_VALID_TYPES: Final[list[NodeType]] = [
    NodeType.COMPLEX,
    NodeType.BUILDING,
    NodeType.FLOOR,
    NodeType.ROOM,
    NodeType.COUNTERPARTY,
    NodeType.RESPONSIBLE_PERSON,
]

# Шаблоны сообщений логирования
_LOG_MARK_VALID = "VALID: {type}#{id}"
_LOG_MARK_INVALID = "INVALID: {type}#{id}"
_LOG_MARK_VALID_BULK = "VALID BULK: {type} ×{count}"
_LOG_MARK_INVALID_BULK = "INVALID BULK: {type} ×{count}"
_LOG_INVALIDATE_BRANCH = "INVALIDATE_BRANCH: {type}#{id} → {count} сущностей"
_LOG_CLEAR = "ValidityIndex очищен"
_LOG_INIT = "ValidityIndex инициализирован: {types} типов"
_LOG_VALIDATION_ERROR = "ValidityIndex: отсутствуют типы {missing}"
_LOG_UNSUPPORTED_TYPE = "Неподдерживаемый тип {type} для операции {operation}"
_LOG_BULK_SKIP_ID = "BULK: пропущен ID {id}: {error}"
_LOG_CHILDREN_ERROR = "Ошибка при получении детей {type}#{id}: {error}"


# ===== ТИПЫ =====
class ValidityStats(TypedDict):
    """Статистика индекса валидности."""
    total_valid: int
    by_type: Dict[str, int]
    types_configured: int


# ===== ВНУТРЕННИЕ ФУНКЦИИ =====
def _validate_validity_types() -> None:
    """
    Проверяет, что все типы NodeType имеют место в индексе валидности.

    Вызывается при импорте модуля.
    """
    from src.core.types import NodeType as AllNodeTypes

    all_types = set(AllNodeTypes)
    configured_types = set(_VALID_TYPES)
    missing = all_types - configured_types

    if missing:
        missing_names = [t.value for t in missing]
        log.error(_LOG_VALIDATION_ERROR.format(missing=missing_names))
        raise RuntimeError(
            f"ValidityIndex не покрывает все типы: {missing_names}\n"
            f"Добавьте их в _VALID_TYPES в {__file__}"
        )

    log.info(f"ValidityIndex схема валидна: {len(_VALID_TYPES)} типов")


_validate_validity_types()


# ===== КЛАСС =====
class ValidityIndex:
    """
    Потокобезопасный индекс валидности сущностей.

    Отслеживает, какие данные актуальны и могут использоваться без перезагрузки.
    При изменении статуса валидности генерирует события DataInvalidated.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, event_bus: EventBus) -> None:
        """Инициализирует пустой индекс валидности."""
        log.info("Инициализация ValidityIndex")
        self._bus = event_bus
        self._lock = RLock()

        # Множества валидных ID для каждого типа
        self._valid: Dict[NodeType, Set[int]] = {
            node_type: set() for node_type in _VALID_TYPES
        }

        log.system(_LOG_INIT.format(types=len(_VALID_TYPES)))

    def clear(self) -> None:
        """Полностью очищает индекс валидности."""
        with self._lock:
            for node_type in self._valid:
                self._valid[node_type].clear()
            log.cache(_LOG_CLEAR)

    # ---- ТОЧЕЧНЫЕ ОПЕРАЦИИ ----
    def mark_valid(self, node_type: NodeType, entity_id: int) -> None:
        """Помечает сущность как валидную (актуальную)."""
        entity_id = validate_positive_int(entity_id, "entity_id")

        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="mark_valid"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")

            self._valid[node_type].add(entity_id)
            log.cache(_LOG_MARK_VALID.format(type=node_type.value, id=entity_id))

    def mark_invalid(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Помечает сущность как невалидную (устаревшую).

        Returns:
            True если статус изменился, False если уже была невалидной
        """
        entity_id = validate_positive_int(entity_id, "entity_id")

        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="mark_invalid"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")

            if entity_id in self._valid[node_type]:
                self._valid[node_type].discard(entity_id)
                log.cache(_LOG_MARK_INVALID.format(type=node_type.value, id=entity_id))

                self._bus.emit(
                    DataInvalidated(
                        node_type=node_type,
                        node_id=entity_id,
                        count=1
                    ),
                    source="validity_index"
                )
                return True

            return False

    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет, валидна ли сущность."""
        entity_id = validate_positive_int(entity_id, "entity_id")

        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="is_valid"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")

            return entity_id in self._valid[node_type]

    # ---- BULK-ОПЕРАЦИИ ----
    def mark_valid_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """
        Помечает множество сущностей как валидные.

        Returns:
            Количество добавленных ID
        """
        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="mark_valid_bulk"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")

            count = 0
            valid_set = self._valid[node_type]

            for entity_id in ids:
                try:
                    entity_id = validate_positive_int(entity_id, "entity_id")
                    if entity_id not in valid_set:
                        valid_set.add(entity_id)
                        count += 1
                except Exception as e:
                    log.warning(_LOG_BULK_SKIP_ID.format(id=entity_id, error=e))

            if count > 0:
                log.cache(_LOG_MARK_VALID_BULK.format(
                    type=node_type.value,
                    count=count
                ))

            return count

    def mark_invalid_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """
        Помечает множество сущностей как невалидные.

        Returns:
            Количество удалённых ID
        """
        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="mark_invalid_bulk"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")

            count = 0
            valid_set = self._valid[node_type]

            for entity_id in ids:
                try:
                    entity_id = validate_positive_int(entity_id, "entity_id")
                    if entity_id in valid_set:
                        valid_set.discard(entity_id)
                        count += 1

                        self._bus.emit(
                            DataInvalidated(
                                node_type=node_type,
                                node_id=entity_id,
                                count=1
                            ),
                            source="validity_index"
                        )
                except Exception as e:
                    log.warning(_LOG_BULK_SKIP_ID.format(id=entity_id, error=e))

            if count > 0:
                log.cache(_LOG_MARK_INVALID_BULK.format(
                    type=node_type.value,
                    count=count
                ))

            return count

    # ---- ВЕТОЧНАЯ ИНВАЛИДАЦИЯ ----
    def invalidate_branch(
        self,
        node_type: NodeType,
        entity_id: int,
        get_children_fn: Callable[[NodeType, int], List[int]]
    ) -> int:
        """
        Итеративно инвалидирует всю ветку сущностей (BFS, без рекурсии).

        Args:
            node_type: Тип корневого узла
            entity_id: ID корневого узла
            get_children_fn: Функция для получения ID детей (из RelationIndex)

        Returns:
            Количество сущностей, помеченных как невалидные
        """
        entity_id = validate_positive_int(entity_id, "entity_id")

        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="invalidate_branch"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")

            count = 0
            queue = deque()
            queue.append((node_type, entity_id))

            while queue:
                current_type, current_id = queue.popleft()

                # Инвалидируем текущий узел
                if self._invalidate_node(current_type, current_id):
                    count += 1

                # Добавляем детей в очередь
                try:
                    child_type = get_child_type(current_type)
                    if child_type:
                        child_ids = get_children_fn(current_type, current_id)
                        for child_id in child_ids:
                            queue.append((child_type, child_id))
                except Exception as e:
                    log.error(_LOG_CHILDREN_ERROR.format(
                        type=current_type.value,
                        id=current_id,
                        error=e
                    ))

            if count > 0:
                log.cache(_LOG_INVALIDATE_BRANCH.format(
                    type=node_type.value,
                    id=entity_id,
                    count=count
                ))

                self._bus.emit(
                    DataInvalidated(
                        node_type=node_type,
                        node_id=entity_id,
                        count=count
                    ),
                    source="validity_index"
                )

            return count

    # ---- СТАТИСТИКА И УПРАВЛЕНИЕ ----
    def get_valid_ids(self, node_type: NodeType) -> List[int]:
        """Возвращает список всех валидных ID для указанного типа."""
        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="get_valid_ids"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")

            return list(self._valid[node_type])

    def get_stats(self) -> ValidityStats:
        """Возвращает статистику индекса валидности."""
        with self._lock:
            total_valid = sum(len(s) for s in self._valid.values())
            by_type = {
                node_type.value: len(valid_set)
                for node_type, valid_set in self._valid.items()
            }

            return ValidityStats(
                total_valid=total_valid,
                by_type=by_type,
                types_configured=len(self._valid),
            )

    def size(self) -> int:
        """Возвращает общее количество валидных сущностей."""
        with self._lock:
            return sum(len(s) for s in self._valid.values())

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _invalidate_node(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Внутренний метод: инвалидирует один узел (без событий).

        Returns:
            True если узел был валидным (статус изменился)
        """
        if entity_id in self._valid[node_type]:
            self._valid[node_type].discard(entity_id)
            return True
        return False