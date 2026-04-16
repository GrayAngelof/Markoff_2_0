# client/src/data/entity_graph.py
"""
Фасад графа сущностей — координатор store, relations, validity, load_state.

Только координация: не содержит логики хранения, связей, валидности или состояния загрузки.
Все операции потокобезопасны через RLock.
"""

# ===== ИМПОРТЫ =====
from collections import defaultdict
from datetime import datetime
from threading import RLock
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, TypedDict

from src.core import EventBus
from src.core.rules.hierarchy import get_child_type, get_parent_type
from src.core.types import NodeIdentifier, NodeType
from src.core.types.nodes import NodeID
from src.shared.comparison import has_changed
from src.shared.validation import validate_positive_int
from utils.logger import get_logger

from .graph.consistency import ConsistencyChecker
from .graph.decorators import validate_ids
from .graph.load_state import LoadState, LoadStateIndex
from .graph.relations import RelationIndex, RelationStats
from .graph.schema import get_node_type, get_parent_id
from .graph.store import EntityStore, StoreStats
from .graph.validity import ValidityIndex, ValidityStats


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ТИПЫ =====
class EntityGraphStats(TypedDict):
    """Полная статистика графа сущностей."""
    store: StoreStats
    relations: RelationStats
    validity: ValidityStats
    load_state: Dict[str, int]
    total_entities: int
    valid_count: int


# ===== КЛАСС =====
class EntityGraph:
    """
    Фасад графа сущностей — координатор store, relations, validity, load_state.

    Только координация: не содержит логики хранения, связей, валидности или состояния загрузки.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, event_bus: EventBus) -> None:
        """Инициализирует пустой граф сущностей."""
        log.info("Инициализация EntityGraph")
        self._bus = event_bus
        self._lock = RLock()

        self._store = EntityStore()
        self._relations = RelationIndex()
        self._validity = ValidityIndex(event_bus)
        self._load_state = LoadStateIndex()

        self._consistency = ConsistencyChecker(
            self._store, self._relations, self._validity
        )

        log.system("EntityGraph инициализирован")

    def clear(self) -> None:
        """Полная очистка графа."""
        log.info("Очистка EntityGraph")

        def _clear() -> None:
            self._store.clear()
            self._relations.clear()
            self._validity.clear()
            self._load_state.clear()

        self._with_lock(_clear)
        log.success("EntityGraph очищен")

    # ---- CRUD ОПЕРАЦИИ ----
    def add_or_update(self, entity: Any) -> bool:
        """
        Добавляет или обновляет сущность в графе.

        Returns:
            True если данные изменились, False если без изменений
        """
        def _add() -> bool:
            node_type = get_node_type(entity)
            if node_type is None:
                log.error(f"Не удалось определить тип сущности {type(entity).__name__}")
                raise ValueError(f"Сущность {type(entity).__name__} должна иметь NODE_TYPE")

            entity_id = entity.id
            if entity_id is None:
                log.error(f"Сущность {node_type.value} не имеет id")
                raise ValueError(f"Сущность {node_type.value} должна иметь атрибут id")

            old = self._store.get(node_type, entity_id)

            if old is not None and not has_changed(old, entity):
                log.cache(f"{node_type.value}#{entity_id} без изменений, пропускаем")
                return False

            self._store.put(node_type, entity_id, entity)
            log.cache(f"PUT {node_type.value}#{entity_id} в хранилище")

            parent_id = get_parent_id(entity)
            if parent_id is not None:
                parent_type = get_parent_type(node_type)
                if parent_type:
                    self._relations.link(
                        node_type, entity_id, parent_type, parent_id
                    )

            self._validity.mark_valid(node_type, entity_id)
            log.success(f"{node_type.value}#{entity_id} добавлен/обновлён в графе")
            return True

        return self._with_lock(_add)

    def add_or_update_bulk(self, entities: List[Any]) -> Dict[str, Any]:
        """
        Добавляет или обновляет несколько сущностей.

        Returns:
            Dict со статистикой: total, added, updated, skipped, errors
        """
        if not entities:
            return {'total': 0, 'added': 0, 'updated': 0, 'skipped': 0, 'errors': []}

        sample_type = get_node_type(entities[0])
        type_name = sample_type.value if sample_type else "unknown"

        log.info(f"Пакетная обработка {len(entities)} {type_name}")

        stats = {
            'total': len(entities),
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': [],
        }

        added_ids = []
        updated_ids = []
        skipped_ids = []

        for entity in entities:
            try:
                node_type = get_node_type(entity)
                if node_type is None:
                    error = f"Не удалось определить тип сущности {type(entity).__name__}"
                    stats['errors'].append(error)
                    log.error(error)
                    continue

                entity_id = entity.id
                if entity_id is None:
                    error = f"Сущность {node_type.value} не имеет id"
                    stats['errors'].append(error)
                    log.error(error)
                    continue

                old = self._store.get(node_type, entity_id)

                if old is not None and not has_changed(old, entity):
                    stats['skipped'] += 1
                    skipped_ids.append(f"{node_type.value}#{entity_id}")
                    continue

                self._store.put(node_type, entity_id, entity)

                parent_id = get_parent_id(entity)
                if parent_id is not None:
                    parent_type = get_parent_type(node_type)
                    if parent_type:
                        self._relations.link(
                            node_type, entity_id, parent_type, parent_id
                        )

                self._validity.mark_valid(node_type, entity_id)

                if old is None:
                    stats['added'] += 1
                    added_ids.append(f"{node_type.value}#{entity_id}")
                else:
                    stats['updated'] += 1
                    updated_ids.append(f"{node_type.value}#{entity_id}")

            except Exception as e:
                error = f"Ошибка при обработке {getattr(entity, 'id', '?')}: {e}"
                stats['errors'].append(error)
                log.exception(error)

        # Агрегированный лог
        if added_ids:
            log.success(f"Добавлено {len(added_ids)} {type_name}: {', '.join(added_ids[:5])}" +
                       (f" и ещё {len(added_ids) - 5}" if len(added_ids) > 5 else ""))

        if updated_ids:
            log.info(f"Обновлено {len(updated_ids)} {type_name}: {', '.join(updated_ids[:5])}" +
                    (f" и ещё {len(updated_ids) - 5}" if len(updated_ids) > 5 else ""))

        if skipped_ids:
            log.cache(f"Пропущено {len(skipped_ids)} {type_name} (без изменений)")

        if stats['errors']:
            log.error(f"Ошибок: {len(stats['errors'])}")

        return stats

    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """Возвращает сущность по ID."""
        return self._with_lock(lambda: self._store.get(node_type, entity_id))

    def get_all(self, node_type: NodeType) -> List[Any]:
        """Возвращает все сущности указанного типа."""
        return self._with_lock(lambda: self._store.get_all(node_type))

    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """Возвращает все ID сущностей указанного типа."""
        return self._with_lock(lambda: self._store.get_all_ids(node_type))

    def has_entity(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет наличие сущности."""
        return self._with_lock(lambda: self._store.has(node_type, entity_id))

    def remove(self, node_type: NodeType, entity_id: int, cascade: bool = False) -> bool:
        """Удаляет сущность. Если cascade=True — удаляет всех потомков."""
        log.info(f"REMOVE {node_type.value}#{entity_id} (cascade={cascade})")

        def _remove() -> bool:
            if not self._store.has(node_type, entity_id):
                log.warning(f"{node_type.value}#{entity_id} не найден для удаления")
                return False

            if cascade:
                child_ids = self._relations.get_children(node_type, entity_id)
                child_type = get_child_type(node_type)
                if child_type and child_ids:
                    log.debug(f"Каскадное удаление {len(child_ids)} детей {child_type.value}")
                    for child_id in child_ids:
                        self.remove(child_type, child_id, cascade=True)

            self._relations.remove_node(node_type, entity_id)
            self._store.remove(node_type, entity_id)
            self._validity.mark_invalid(node_type, entity_id)
            self._load_state.reset(node_type, entity_id)
            log.success(f"{node_type.value}#{entity_id} удалён")
            return True

        return self._with_lock(_remove)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """Возвращает ID всех детей родителя."""
        result = self._with_lock(
            lambda: self._relations.get_children(parent_type, parent_id)
        )
        if result:
            log.debug(f"CHILDREN {parent_type.value}#{parent_id} → {len(result)} детей")
        return result

    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[NodeIdentifier]:
        """Возвращает родителя узла."""
        def _get() -> Optional[NodeIdentifier]:
            parent_info = self._relations.get_parent(child_type, child_id)
            if parent_info:
                parent_type, parent_id = parent_info
                return NodeIdentifier(parent_type, parent_id)
            return None

        return self._with_lock(_get)

    def get_ancestors(self, node_type: NodeType, node_id: int) -> List[NodeIdentifier]:
        """Возвращает всех предков от ближайшего к дальнему."""
        def _get() -> List[NodeIdentifier]:
            ancestors = []
            current_type, current_id = node_type, node_id

            while True:
                parent_info = self._relations.get_parent(current_type, current_id)
                if not parent_info:
                    break
                parent_type, parent_id = parent_info
                ancestors.append(NodeIdentifier(parent_type, parent_id))
                current_type, current_id = parent_type, parent_id

            return ancestors

        return self._with_lock(_get)

    # ---- ВАЛИДНОСТЬ ----
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет, валидна ли сущность."""
        return self._with_lock(
            lambda: self._validity.is_valid(node_type, entity_id)
        )

    def validate(self, node_type: NodeType, entity_id: int) -> None:
        """Помечает сущность как валидную."""
        log.info(f"VALIDATE {node_type.value}#{entity_id}")
        return self._with_lock(
            lambda: self._validity.mark_valid(node_type, entity_id)
        )

    def validate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """Помечает множество сущностей как валидные."""
        ids_list = list(ids)
        if ids_list:
            log.data(f"Валидация {node_type.value} ×{len(ids_list)}")
            if len(ids_list) <= 10:
                log.debug(f"   IDs: {', '.join(map(str, ids_list))}")
        return self._with_lock(
            lambda: self._validity.mark_valid_bulk(node_type, ids_list)
        )

    def invalidate(self, node_type: NodeType, entity_id: int) -> bool:
        """Инвалидирует сущность."""
        log.info(f"INVALIDATE {node_type.value}#{entity_id}")
        return self._with_lock(
            lambda: self._validity.mark_invalid(node_type, entity_id)
        )

    def invalidate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """Помечает множество сущностей как невалидные."""
        ids_list = list(ids)
        if ids_list:
            log.data(f"Инвалидация {node_type.value} ×{len(ids_list)}")
            if len(ids_list) <= 10:
                log.debug(f"   IDs: {', '.join(map(str, ids_list))}")
        return self._with_lock(
            lambda: self._validity.mark_invalid_bulk(node_type, ids_list)
        )

    def invalidate_branch(self, node_type: NodeType, entity_id: int) -> int:
        """Инвалидирует всю ветку сущностей."""
        log.info(f"INVALIDATE_BRANCH {node_type.value}#{entity_id}")
        return self._with_lock(
            lambda: self._validity.invalidate_branch(
                node_type, entity_id, self._relations.get_children
            )
        )

    # ---- СОСТОЯНИЕ ЗАГРУЗКИ ----
    def is_children_loaded(self, node_type: NodeType, node_id: int) -> bool:
        """Проверяет, загружены ли дети для узла."""
        return self._with_lock(
            lambda: self._load_state.is_loaded(node_type, node_id)
        )

    def mark_children_loading(self, node_type: NodeType, node_id: int) -> bool:
        """Помечает начало загрузки детей."""
        log.info(f"Загрузка детей {node_type.value}#{node_id}")
        return self._with_lock(
            lambda: self._load_state.mark_loading(node_type, node_id)
        )

    def mark_children_loaded(self, node_type: NodeType, node_id: int) -> None:
        """Помечает, что дети загружены."""
        log.success(f"Дети загружены {node_type.value}#{node_id}")
        return self._with_lock(
            lambda: self._load_state.mark_loaded(node_type, node_id)
        )

    def mark_children_load_failed(self, node_type: NodeType, node_id: int) -> None:
        """Помечает ошибку загрузки детей."""
        log.error(f"Ошибка загрузки детей {node_type.value}#{node_id}")
        return self._with_lock(
            lambda: self._load_state.mark_failed(node_type, node_id)
        )

    def reset_children_state(self, node_type: NodeType, node_id: int) -> None:
        """Сбрасывает состояние загрузки детей."""
        log.debug(f"Сброс состояния детей {node_type.value}#{node_id}")
        return self._with_lock(
            lambda: self._load_state.reset(node_type, node_id)
        )

    # ---- ВРЕМЕННЫЕ МЕТКИ ----
    def get_timestamp(self, node_type: NodeType, entity_id: int) -> Optional[datetime]:
        """Возвращает время последнего обновления сущности."""
        return self._with_lock(
            lambda: self._store.get_timestamp(node_type, entity_id)
        )

    # ---- СТАТИСТИКА И ДИАГНОСТИКА ----
    def get_stats(self) -> EntityGraphStats:
        """Возвращает полную статистику графа."""
        def _get() -> EntityGraphStats:
            store_stats = self._store.get_stats()
            relations_stats = self._relations.get_stats()
            validity_stats = self._validity.get_stats()
            load_state_stats = self._load_state.get_stats()

            return EntityGraphStats(
                store=store_stats,
                relations=relations_stats,
                validity=validity_stats,
                load_state=load_state_stats,
                total_entities=store_stats['total_entities'],
                valid_count=validity_stats['total_valid'],
            )

        return self._with_lock(_get)

    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()

        log.info("\n" + "=" * 50)
        log.info("EntityGraph Statistics")
        log.info("=" * 50)

        log.info("\nStore:")
        log.info(f"  • Всего сущностей: {stats['store']['total_entities']}")
        for type_name, count in stats['store']['by_type'].items():
            log.info(f"  • {type_name}: {count}")

        log.info("\nRelations:")
        log.info(f"  • Parent entries: {stats['relations']['parent_entries']}")
        log.info(f"  • Child entries: {stats['relations']['child_entries']}")

        log.info("\nValidity:")
        validity_stats = stats['validity']
        log.info(f"  • Всего валидных: {validity_stats['total_valid']}")
        for type_name, count in validity_stats['by_type'].items():
            if count > 0:
                log.info(f"  • {type_name}: {count}")

        log.info("\nLoad State:")
        load_state_stats = stats['load_state']
        log.info(f"  • NOT_LOADED: {load_state_stats['not_loaded']}")
        log.info(f"  • LOADING: {load_state_stats['loading']}")
        log.info(f"  • LOADED: {load_state_stats['loaded']}")

        log.info("=" * 50 + "\n")

    def check_consistency(self) -> Dict[str, Any]:
        """Проверяет консистентность графа."""
        log.info("Проверка консистентности графа...")
        return self._consistency.check()

    # ---- МЕТОДЫ ДЛЯ ЗАГРУЗЧИКА ----
    def get_if_full(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """
        Возвращает сущность только если она есть и полная.

        Полнота определяется в _has_full_details.
        """
        entity = self.get(node_type, node_id)
        if entity and self.is_valid(node_type, node_id):
            if self._has_full_details(entity, node_type):
                return entity
        return None

    def get_cached_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType
    ) -> List[Any]:
        """
        Возвращает детей только если ВСЕ они есть в кэше.

        Если хоть одного ребёнка нет — возвращает [] (неполные данные).
        """
        child_ids = self.get_children(parent_type, parent_id)
        if not child_ids:
            return []

        result = []
        for child_id in child_ids:
            child = self.get(child_type, child_id)
            if child is None:
                return []
            result.append(child)

        return result

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _with_lock(self, func):
        """Выполняет функцию под блокировкой."""
        with self._lock:
            return func()

    def _has_full_details(self, entity: Any, node_type: NodeType) -> bool:
        """Определяет, полные ли данные у сущности."""
        if node_type == NodeType.COMPLEX:
            return entity.description is not None or entity.address is not None
        if node_type == NodeType.BUILDING:
            return entity.description is not None or entity.address is not None
        if node_type == NodeType.FLOOR:
            return entity.description is not None
        if node_type == NodeType.ROOM:
            return entity.area is not None or entity.status_code is not None
        return False