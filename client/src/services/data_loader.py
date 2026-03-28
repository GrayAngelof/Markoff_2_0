# client/src/services/data_loader.py
"""
DataLoader — фасад загрузки данных.

Единственный публичный компонент загрузчика.
Отвечает за:
- Проверку кэша (делегирует в EntityGraph)
- Эмиссию событий (DataLoaded, DataError)
- Оркестрацию вызовов NodeLoader и DictionaryLoader

НЕ отвечает за:
- Решение, полные ли данные (это EntityGraph)
- Конкретную логику загрузки (это NodeLoader/DictionaryLoader)
- Бизнес-логику (это контроллеры)
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from src.core import EventBus, NodeIdentifier, NodeType
from src.core.events import DataError, DataLoaded
from src.core.types.nodes import NodeID
from src.data import EntityGraph
from src.models import Building, Complex, Counterparty, Floor, ResponsiblePerson, Room
from src.services.api_client import ApiClient
from src.services.loading.dictionary_loader import DictionaryLoader
from src.services.loading.node_loader import NodeLoader
from src.services.loading.utils import LoaderUtils
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ТИПЫ =====
@dataclass(frozen=True, slots=True)
class BuildingWithOwnerResult:
    """
    Типизированный результат загрузки корпуса с владельцем.

    Attributes:
        building: Загруженный корпус (обязательный)
        owner: Владелец корпуса (если есть)
        responsible_persons: Список ответственных лиц владельца
    """
    building: Building
    owner: Optional[Counterparty] = None
    responsible_persons: List[ResponsiblePerson] = field(default_factory=list)


# ===== КЛАСС =====
class DataLoader:
    """
    Фасад загрузки данных.

    Контроллеры вызывают только этот класс. Все решения о кэше
    делегируются в EntityGraph — DataLoader только спрашивает.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, api: ApiClient, graph: EntityGraph) -> None:
        """Инициализирует фасад загрузки."""
        log.system("DataLoader инициализация")

        self._bus = bus
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

        self._graph = graph
        self._utils = LoaderUtils()

        child_loaders = {
            NodeType.BUILDING: lambda a, pid: a.get_buildings(pid),
            NodeType.FLOOR: lambda a, pid: a.get_floors(pid),
            NodeType.ROOM: lambda a, pid: a.get_rooms(pid),
        }

        detail_loaders = {
            NodeType.COMPLEX: lambda a, nid: a.get_complex_detail(nid),
            NodeType.BUILDING: lambda a, nid: a.get_building_detail(nid),
            NodeType.FLOOR: lambda a, nid: a.get_floor_detail(nid),
            NodeType.ROOM: lambda a, nid: a.get_room_detail(nid),
        }

        self._node_loader = NodeLoader(api, graph, child_loaders, detail_loaders)
        self._dict_loader = DictionaryLoader(api, graph)

        log.success("DataLoader инициализирован")

    def cleanup(self) -> None:
        """Очищает ресурсы."""
        self.clear_cache()
        log.shutdown("DataLoader очищен")

    # ---- ЗАГРУЗКА КОРНЕВЫХ УЗЛОВ ----
    def load_complexes(self) -> List[Complex]:
        """Загружает все комплексы."""
        cached = self._graph.get_all(NodeType.COMPLEX)
        if cached:
            log.cache(f"Найдено {len(cached)} комплексов в кэше")
            return cached

        log.api("Загрузка комплексов через API")
        result = self._with_events(
            NodeType.COMPLEX.value,
            0,
            self._node_loader.load_complexes
        )
        log.data(f"Загружено {len(result)} комплексов")
        return result

    # ---- ЛЕНИВАЯ ЗАГРУЗКА ДЕТЕЙ ----
    def load_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType,
    ) -> List[Any]:
        """Загружает детей для родителя (ленивая загрузка)."""
        node_display = f"{parent_type.value}#{parent_id}"

        cached = self._graph.get_cached_children(parent_type, parent_id, child_type)
        if cached:
            log.cache(f"Найдено {len(cached)} детей {child_type.value} для {node_display} в кэше")
            return cached

        log.api(f"Загрузка детей {child_type.value} для {node_display} через API")
        result = self._with_events(
            parent_type.value,
            parent_id,
            self._node_loader.load_children,
            parent_type, parent_id, child_type
        )
        log.data(f"Загружено {len(result)} детей {child_type.value} для {node_display}")
        return result

    # ---- ДЕТАЛЬНАЯ ЗАГРУЗКА ----
    def load_details(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """Загружает детальную информацию об объекте."""
        node_display = f"{node_type.value}#{node_id}"

        cached = self._graph.get_if_full(node_type, node_id)
        if cached:
            log.cache(f"Полные детали для {node_display} найдены в кэше")
            return cached

        log.api(f"Загрузка деталей для {node_display} через API")
        result = self._with_events(
            node_type.value,
            node_id,
            self._node_loader.load_details,
            node_type, node_id
        )
        if result:
            log.data(f"Детали для {node_display} загружены")
        else:
            log.warning(f"Детали для {node_display} не найдены")
        return result

    # ---- КОНТРАГЕНТЫ И ОТВЕТСТВЕННЫЕ ЛИЦА ----
    def load_counterparty(self, counterparty_id: NodeID) -> Optional[Counterparty]:
        """Загружает контрагента."""
        cached = self._graph.get(NodeType.COUNTERPARTY, counterparty_id)
        if cached:
            log.cache(f"Контрагент #{counterparty_id} найден в кэше")
            return cached

        log.api(f"Загрузка контрагента #{counterparty_id} через API")
        result = self._with_events(
            NodeType.COUNTERPARTY.value,
            counterparty_id,
            self._dict_loader.load_counterparty,
            counterparty_id
        )
        if result:
            log.data(f"Контрагент #{counterparty_id} загружен")
        else:
            log.warning(f"Контрагент #{counterparty_id} не найден")
        return result

    def load_responsible_persons(self, counterparty_id: NodeID) -> List[ResponsiblePerson]:
        """Загружает ответственных лиц для контрагента."""
        cached = self._graph.get_cached_children(
            NodeType.COUNTERPARTY, counterparty_id, NodeType.RESPONSIBLE_PERSON
        )
        if cached:
            log.cache(f"{len(cached)} контактов для контрагента #{counterparty_id} найдено в кэше")
            return cached

        log.api(f"Загрузка контактов для контрагента #{counterparty_id} через API")
        result = self._with_events(
            NodeType.RESPONSIBLE_PERSON.value,
            counterparty_id,
            self._dict_loader.load_responsible_persons,
            counterparty_id
        )
        log.data(f"Загружено {len(result)} контактов для контрагента #{counterparty_id}")
        return result

    # ---- ЗАГРУЗКА КОРПУСА С ВЛАДЕЛЬЦЕМ ----
    def load_building_with_owner(self, building_id: NodeID) -> Optional[BuildingWithOwnerResult]:
        """
        Загружает корпус с его владельцем и ответственными лицами.

        Алгоритм:
        1. Проверяет кэш корпуса
        2. Если есть и полный — использует
        3. Если нет — загружает детали корпуса
        4. Если у корпуса есть owner_id — загружает владельца
        5. Если владелец загружен — загружает ответственных лиц
        """
        building = self.load_details(NodeType.BUILDING, building_id)
        if building is None:
            log.warning(f"Корпус #{building_id} не найден")
            return None

        result = BuildingWithOwnerResult(building=building)

        if building.owner_id:
            owner = self.load_counterparty(building.owner_id)

            if owner:
                result = BuildingWithOwnerResult(
                    building=building,
                    owner=owner,
                    responsible_persons=result.responsible_persons
                )

                persons = self.load_responsible_persons(owner.id)
                if persons:
                    result = BuildingWithOwnerResult(
                        building=building,
                        owner=owner,
                        responsible_persons=persons
                    )
                    log.data(f"Загружено {len(persons)} контактов для владельца {owner.short_name}")
            else:
                log.warning(f"Владелец #{building.owner_id} для корпуса #{building_id} не найден")

        log.data(f"Корпус #{building_id} загружен: владелец={result.owner is not None}, контактов={len(result.responsible_persons)}")
        return result

    # ---- НАВИГАЦИЯ ----
    def get_ancestors(self, node_type: NodeType, node_id: NodeID) -> List[NodeIdentifier]:
        """Возвращает всех предков узла (родитель, дедушка и т.д.)."""
        result = self._graph.get_ancestors(node_type, node_id)
        if result:
            log.debug(f"Найдено {len(result)} предков для {node_type.value}#{node_id}")
        return result

    # ---- ПЕРЕЗАГРУЗКА ДАННЫХ ----
    def reload_node(self, node_type: NodeType, node_id: NodeID) -> None:
        """Перезагружает узел (инвалидирует и загружает заново)."""
        node_display = f"{node_type.value}#{node_id}"

        self._graph.invalidate(node_type, node_id)
        log.cache(f"Узел {node_display} инвалидирован")

        self.load_details(node_type, node_id)

        log.info(f"Узел {node_display} перезагружен")

    def reload_branch(self, node_type: NodeType, node_id: NodeID) -> None:
        """Перезагружает всю ветку (инвалидирует рекурсивно и загружает)."""
        node_display = f"{node_type.value}#{node_id}"

        count = self._graph.invalidate_branch(node_type, node_id)
        log.cache(f"Инвалидировано {count} сущностей в ветке {node_display}")

        self.load_details(node_type, node_id)

        log.info(f"Ветка {node_display} перезагружена")

    # ---- УПРАВЛЕНИЕ ----
    def clear_cache(self) -> None:
        """Очищает все кэши в загрузчике."""
        self._utils.clear_cache()
        log.cache("Кэш DataLoader очищен")

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику работы загрузчика."""
        stats = {
            'loader': self._node_loader.get_stats() if hasattr(self._node_loader, 'get_stats') else {},
            'utils': self._utils.get_stats(),
        }
        return stats

    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()

        log.info("=== DataLoader Statistics ===")
        log.info(f"LoaderUtils:")
        log.info(f"  detail_checks: {stats['utils']['detail_checks']}")
        log.info(f"  detail_cache_hits: {stats['utils']['detail_cache_hits']}")
        log.info(f"  cache_size: {stats['utils']['cache_size']}")

        if stats['loader']:
            log.info(f"NodeLoader:")
            for key, value in stats['loader'].items():
                log.info(f"  {key}: {value}")
        log.info("=" * 30)

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _with_events(
        self,
        node_type: str,
        node_id: int,
        fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Обёртка для единообразной эмиссии событий загрузки.

        Эмитит DataLoaded при успехе, DataError при ошибке.
        """
        node_display = f"{node_type}#{node_id}"
        log.info(f"Загрузка {node_display}")

        try:
            result = fn(*args, **kwargs)

            if isinstance(result, list):
                count = len(result)
                log.data(f"Загружено {count} элементов для {node_display}")
            elif result is not None:
                count = 1
                log.data(f"Загружен {type(result).__name__} для {node_display}")
            else:
                count = 0
                log.data(f"Результат загрузки {node_display}: None")

            self._bus.emit(DataLoaded(
                node_type=node_type,
                node_id=node_id,
                payload=result,
                count=count,
            ))

            log.success(f"Загрузка {node_display} завершена")
            return result

        except Exception as e:
            log.error(f"Ошибка загрузки {node_display}: {e}")
            import traceback
            log.debug(traceback.format_exc())

            self._bus.emit(DataError(
                node_type=node_type,
                node_id=node_id,
                error=str(e),
            ))
            raise