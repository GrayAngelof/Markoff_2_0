"""
Индекс валидности данных — отслеживание актуальности сущностей.

Это четвертый компонент Data слоя (после schema, store, relations).
ValidityIndex отвечает только за одно: знать, какие данные актуальны,
а какие требуют перезагрузки.

Принципы:
    - Хранит множества валидных ID для каждого типа
    - Позволяет точечно или веточно помечать данные как невалидные
    - Все операции потокобезопасны (RLock)
    - Для веточной инвалидации использует итеративный обход (не рекурсию)
    - Поддерживает bulk-операции для массовой загрузки

Зависимости:
    - threading — для RLock
    - core.types.NodeType — типы узлов
    - core.hierarchy — get_child_type
    - core.events — DataInvalidated
    - shared.validation — validate_positive_int
    - utils.logger — логирование

Потребители:
    - entity_graph.py (фасад) — через публичные методы
    - Никто не должен импортировать validity напрямую!

ВАЖНО:
    ValidityIndex не знает о связях между сущностями.
    Для рекурсивной инвалидации ветки он получает функцию get_children_fn,
    которая предоставляется извне (из RelationIndex через EntityGraph).
    Это позволяет сохранить чистоту ответственности.
"""

from threading import RLock
from typing import Dict, Set, List, Callable, Final, Iterable, TypedDict
from collections import deque

from src.core import EventBus
from src.core.events import DataInvalidated
from src.core.types import NodeType
from src.core.hierarchy import get_child_type
from src.shared.validation import validate_positive_int
from utils.logger import get_logger


# ============================================
# КОНСТАНТЫ
# ============================================

# Единый логгер для модуля
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

# Сообщения для логирования (без эмодзи)
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


# ============================================
# ТИПЫ ДЛЯ СТАТИСТИКИ
# ============================================

class ValidityStats(TypedDict):
    """Структура статистики индекса валидности."""
    total_valid: int
    by_type: Dict[str, int]
    types_configured: int


# ============================================
# ВАЛИДАЦИЯ ПРИ ИМПОРТЕ
# ============================================

def _validate_validity_types() -> None:
    """
    Проверяет, что все типы NodeType имеют место в индексе валидности.
    
    Это критическая проверка, которая обнаруживает ошибки конфигурации
    на этапе импорта модуля, а не в рантайме.
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


# Выполняем валидацию при импорте
_validate_validity_types()


# ============================================
# КЛАСС VALIDITY INDEX
# ============================================

class ValidityIndex:
    """
    Потокобезопасный индекс валидности сущностей с эмиссией событий.
    
    Отслеживает, какие данные актуальны и могут использоваться без перезагрузки.
    При изменении статуса валидности генерирует события DataInvalidated.
    
    Особенности:
        - Точечная инвалидация: mark_invalid(type, id)
        - Bulk-операции: mark_valid_bulk, mark_invalid_bulk
        - Веточная инвалидация (итеративная, не рекурсивная)
        - Проверка валидности: is_valid(type, id)
        - Эмиссия событий при инвалидации
    
    Пример:
        >>> bus = EventBus()
        >>> idx = ValidityIndex(bus)
        >>> idx.mark_valid(NodeType.COMPLEX, 42)
        >>> idx.is_valid(NodeType.COMPLEX, 42)
        True
        >>> idx.mark_invalid(NodeType.COMPLEX, 42)
        >>> idx.is_valid(NodeType.COMPLEX, 42)
        False
        # Будет испущено событие DataInvalidated
    """
    
    def __init__(self, event_bus: EventBus) -> None:
        """
        Инициализирует пустой индекс валидности.
        
        Args:
            event_bus: Шина событий для уведомлений об инвалидации
        """
        self._bus = event_bus
        self._lock = RLock()
        
        # Множества валидных ID для каждого типа
        self._valid: Dict[NodeType, Set[int]] = {
            node_type: set() for node_type in _VALID_TYPES
        }
        
        log.system(_LOG_INIT.format(types=len(_VALID_TYPES)))
    
    
    # ============================================
    # ОСНОВНЫЕ ОПЕРАЦИИ
    # ============================================
    
    def mark_valid(self, node_type: NodeType, entity_id: int) -> None:
        """
        Помечает сущность как валидную (актуальную).
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности (валидируется)
            
        Raises:
            ValidationError: Если entity_id не положительный
            KeyError: Если node_type не поддерживается
        """
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
        Помечает сущность как невалидную (устаревшую) и эмитит событие.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности (валидируется)
            
        Returns:
            bool: True если сущность была валидной (статус изменился),
                  False если уже была невалидной или не существовала
                  
        Raises:
            ValidationError: Если entity_id не положительный
            KeyError: Если node_type не поддерживается
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
                
                # Эмитируем событие об инвалидации
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
        """
        Проверяет, валидна ли сущность.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности (валидируется)
            
        Returns:
            bool: True если сущность валидна и может использоваться
            
        Raises:
            ValidationError: Если entity_id не положительный
            KeyError: Если node_type не поддерживается
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="is_valid"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")
            
            return entity_id in self._valid[node_type]
    
    
    # ============================================
    # BULK-ОПЕРАЦИИ (для массовой загрузки)
    # ============================================
    
    def mark_valid_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """
        Помечает множество сущностей как валидные.
        
        Args:
            node_type: Тип сущности
            ids: Итератор ID сущностей
            
        Returns:
            int: Количество добавленных ID
            
        Raises:
            KeyError: Если node_type не поддерживается
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
        
        Для каждой изменённой сущности эмитит отдельное событие.
        
        Args:
            node_type: Тип сущности
            ids: Итератор ID сущностей
            
        Returns:
            int: Количество удаленных ID
            
        Raises:
            KeyError: Если node_type не поддерживается
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
                        
                        # Эмитируем событие для каждого изменённого узла
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
    
    
    # ============================================
    # ВНУТРЕННИЙ МЕТОД ДЛЯ ОДИНОЧНОЙ ИНВАЛИДАЦИИ
    # ============================================
    
    def _invalidate_node(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Внутренний метод: инвалидирует один узел (без событий).
        
        Args:
            node_type: Тип узла
            entity_id: ID узла
            
        Returns:
            bool: True если узел был валидным (статус изменился)
        """
        if entity_id in self._valid[node_type]:
            self._valid[node_type].discard(entity_id)
            return True
        return False
    
    
    # ============================================
    # ВЕТОЧНАЯ ИНВАЛИДАЦИЯ (Итеративная)
    # ============================================
    
    def invalidate_branch(self, node_type: NodeType, entity_id: int,
                         get_children_fn: Callable[[NodeType, int], List[int]]) -> int:
        """
        Итеративно инвалидирует всю ветку сущностей (без рекурсии).
        
        Использует очередь для BFS-обхода дерева, что предотвращает
        переполнение стека при глубокой вложенности.
        Эмитит одно событие для всей ветки.
        
        Args:
            node_type: Тип корневого узла ветки
            entity_id: ID корневого узла (валидируется)
            get_children_fn: Функция для получения ID детей
                            (должна быть из RelationIndex)
            
        Returns:
            int: Количество сущностей, помеченных как невалидные
            
        Raises:
            ValidationError: Если entity_id не положительный
            KeyError: Если node_type не поддерживается
            
        Note:
            get_children_fn должна возвращать список ID детей.
            Для узлов без детей возвращает пустой список.
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
            # Используем очередь для BFS-обхода
            queue = deque()
            queue.append((node_type, entity_id))
            
            # Для отладки — собираем ID инвалидированных узлов
            invalidated_ids = []
            
            while queue:
                current_type, current_id = queue.popleft()
                
                # Инвалидируем текущий узел
                if self._invalidate_node(current_type, current_id):
                    count += 1
                    if log.is_debug_enabled():
                        invalidated_ids.append(f"{current_type.value}#{current_id}")
                
                # Получаем детей и добавляем в очередь
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
                    # Продолжаем обход, не прерываем всю операцию
            
            if count > 0:
                log.cache(_LOG_INVALIDATE_BRANCH.format(
                    type=node_type.value,
                    id=entity_id,
                    count=count
                ))
                
                # Эмитируем одно событие для всей ветки
                self._bus.emit(
                    DataInvalidated(
                        node_type=node_type,
                        node_id=entity_id,
                        count=count
                    ),
                    source="validity_index"
                )
                
                if log.is_debug_enabled() and invalidated_ids:
                    # Ограничиваем вывод для читаемости
                    preview = invalidated_ids[:10]
                    suffix = f"... и ещё {len(invalidated_ids) - 10}" if len(invalidated_ids) > 10 else ""
                    log.debug(f"Инвалидированы: {', '.join(preview)} {suffix}")
            
            return count
    
    
    # ============================================
    # ОПЕРАЦИИ УПРАВЛЕНИЯ
    # ============================================
    
    def get_valid_ids(self, node_type: NodeType) -> List[int]:
        """
        Возвращает список всех валидных ID для указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            List[int]: Список валидных ID (порядок не гарантирован)
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._valid:
                log.error(_LOG_UNSUPPORTED_TYPE.format(
                    type=node_type.value,
                    operation="get_valid_ids"
                ))
                raise KeyError(f"Тип {node_type} не поддерживается ValidityIndex")
            
            return list(self._valid[node_type])
    
    def clear(self) -> None:
        """
        Полностью очищает индекс валидности.
        
        Все сущности становятся невалидными.
        """
        with self._lock:
            for node_type in self._valid:
                self._valid[node_type].clear()
            
            log.cache(_LOG_CLEAR)
    
    def get_stats(self) -> ValidityStats:
        """
        Возвращает статистику индекса валидности.
        
        Returns:
            ValidityStats: Статистика использования
            
        Пример:
            >>> stats = idx.get_stats()
            >>> stats['total_valid']
            42
            >>> stats['by_type']['complex']
            5
        """
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
        """
        Возвращает общее количество валидных сущностей.
        
        Returns:
            int: Сумма валидных объектов всех типов
        """
        with self._lock:
            return sum(len(s) for s in self._valid.values())