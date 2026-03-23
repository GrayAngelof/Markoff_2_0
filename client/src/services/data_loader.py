# client/src/services/data_loader.py
"""
DataLoader — фасад загрузки данных.

Единственный публичный компонент загрузчика.
Отвечает за:
- Проверку кэша (делегирует в EntityGraph)
- Эмиссию событий (DataLoading, DataLoaded, DataError)
- Оркестрацию вызовов NodeLoader и DictionaryLoader

НЕ отвечает за:
- Решение, полные ли данные (это EntityGraph)
- Конкретную логику загрузки (это NodeLoader/DictionaryLoader)
- Бизнес-логику (это контроллеры)
"""

from typing import List, Optional, Any, Callable

from core import EventBus, NodeType, NodeIdentifier
from core.types.nodes import NodeID 
from core.events import (
    DataLoading, DataLoaded, DataError,
    RefreshRequested, ConnectionChanged
)
from core.serializers import format_display
from models import Complex, Building, Floor, Room, Counterparty, ResponsiblePerson
from data import EntityGraph
from services.api_client import ApiClient
from services.loading.node_loader import NodeLoader
from services.loading.dictionary_loader import DictionaryLoader
from services.loading.utils import LoaderUtils
from utils.logger import get_logger

log = get_logger(__name__)


class DataLoader:
    """
    Фасад загрузки данных.
    
    Контроллеры вызывают только этот класс. Все решения о кэше
    делегируются в EntityGraph — DataLoader только спрашивает.
    """
    
    def __init__(self, bus: EventBus, api: ApiClient, graph: EntityGraph):
        """
        Инициализирует фасад загрузки.
        
        Args:
            bus: Шина событий для эмиссии событий
            api: HTTP клиент
            graph: Граф сущностей (единый источник правды)
        """
        self._bus = bus
        self._graph = graph
        self._utils = LoaderUtils()
        
        # Конфигурация для NodeLoader (DI)
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
        
        log.success("DataLoader initialized with DI configuration")
    
    # ===== Вспомогательный метод для эмиссии событий =====
    
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
        
        Args:
            node_type: Тип загружаемого узла (строка)
            node_id: ID загружаемого узла
            fn: Функция загрузки
            *args, **kwargs: Аргументы для функции
            
        Returns:
            Any: Результат функции загрузки
        """
        node_display = f"{node_type}#{node_id}"
        log.debug(f"Emitting DataLoading for {node_display}")
        self._bus.emit(DataLoading(node_type=node_type, node_id=node_id))
        
        try:
            result = fn(*args, **kwargs)
            
            count = len(result) if isinstance(result, list) else (1 if result else 0)
            log.debug(f"Emitting DataLoaded for {node_display} (count={count})")
            self._bus.emit(DataLoaded(
                node_type=node_type,
                node_id=node_id,
                payload=result,
                count=count
            ))
            
            return result
            
        except Exception as e:
            log.error(f"Error loading {node_display}: {e}")
            self._bus.emit(DataError(
                node_type=node_type,
                node_id=node_id,
                error=str(e)
            ))
            raise
    
    # ===== Загрузка комплексов (корневые узлы) =====
    
    def load_complexes(self) -> List[Complex]:
        """
        Загружает все комплексы.
        
        Проверяет кэш через EntityGraph.get_all().
        Если данные есть — возвращает из кэша.
        Если нет — загружает через API.
        
        Returns:
            List[Complex]: Список комплексов (может быть пустым)
        """
        # Вся логика кэша в EntityGraph
        cached = self._graph.get_all(NodeType.COMPLEX)
        if cached:
            log.cache(f"Complexes in cache: {len(cached)}")
            return cached
        
        return self._with_events(
            NodeType.COMPLEX.value,
            0,
            self._node_loader.load_complexes
        )
    
    # ===== Ленивая загрузка детей =====
    
    def load_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType,
    ) -> List[Any]:
        """
        Загружает детей для родителя (ленивая загрузка).
        
        Проверяет кэш через EntityGraph.get_cached_children().
        Если все дети в кэше — возвращает их.
        Если нет — загружает через API.
        
        Args:
            parent_type: Тип родителя (COMPLEX, BUILDING, FLOOR)
            parent_id: ID родителя
            child_type: Тип детей (BUILDING, FLOOR, ROOM)
            
        Returns:
            List[Any]: Список детей
        """
        node_display = f"{parent_type.value}#{parent_id}"
        
        # Делегируем проверку кэша в EntityGraph
        cached = self._graph.get_cached_children(parent_type, parent_id, child_type)
        if cached:
            log.cache(f"Children of {node_display} in cache: {len(cached)}")
            return cached
        
        return self._with_events(
            parent_type.value,
            parent_id,
            self._node_loader.load_children,
            parent_type, parent_id, child_type
        )
    
    # ===== Детальная загрузка =====
    
    def load_details(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """
        Загружает детальную информацию об объекте.
        
        Проверяет кэш через EntityGraph.get_if_full().
        Если данные есть и полные — возвращает из кэша.
        Если нет — загружает через API.
        
        Args:
            node_type: Тип узла (COMPLEX, BUILDING, FLOOR, ROOM)
            node_id: ID узла
            
        Returns:
            Optional[Any]: Детальные данные или None
        """
        node_display = f"{node_type.value}#{node_id}"
        
        # Делегируем проверку полноты в EntityGraph
        cached = self._graph.get_if_full(node_type, node_id)
        if cached:
            log.cache(f"Full details for {node_display} in cache")
            return cached
        
        return self._with_events(
            node_type.value,
            node_id,
            self._node_loader.load_details,
            node_type, node_id
        )
    
    # ===== Контрагенты и ответственные лица =====
    
    def load_counterparty(self, counterparty_id: NodeID) -> Optional[Counterparty]:
        """
        Загружает контрагента.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            Optional[Counterparty]: Контрагент или None
        """
        cached = self._graph.get(NodeType.COUNTERPARTY, counterparty_id)
        if cached:
            log.cache(f"Counterparty {counterparty_id} in cache")
            return cached
        
        return self._with_events(
            NodeType.COUNTERPARTY.value,
            counterparty_id,
            self._dict_loader.load_counterparty,
            counterparty_id
        )
    
    def load_responsible_persons(self, counterparty_id: NodeID) -> List[ResponsiblePerson]:
        """
        Загружает ответственных лиц для контрагента.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            List[ResponsiblePerson]: Список ответственных лиц
        """
        cached = self._graph.get_cached_children(
            NodeType.COUNTERPARTY, counterparty_id, NodeType.RESPONSIBLE_PERSON
        )
        if cached:
            log.cache(f"Responsible persons for counterparty {counterparty_id} in cache: {len(cached)}")
            return cached
        
        return self._with_events(
            NodeType.RESPONSIBLE_PERSON.value,
            counterparty_id,
            self._dict_loader.load_responsible_persons,
            counterparty_id
        )
    
    # ===== Перезагрузка данных =====
    
    def reload_node(self, node_type: NodeType, node_id: NodeID) -> None:
        """
        Перезагружает узел (инвалидирует и загружает заново).
        
        Args:
            node_type: Тип узла
            node_id: ID узла
        """
        log.info(f"Reloading node {node_type.value}#{node_id}")
        
        # Инвалидируем в графе
        self._graph.invalidate(node_type, node_id)
        
        # Загружаем заново
        self.load_details(node_type, node_id)
    
    def reload_branch(self, node_type: NodeType, node_id: NodeID) -> None:
        """
        Перезагружает всю ветку (инвалидирует рекурсивно и загружает).
        
        Args:
            node_type: Тип корневого узла ветки
            node_id: ID корневого узла
        """
        log.info(f"Reloading branch {node_type.value}#{node_id}")
        
        # Инвалидируем всю ветку
        count = self._graph.invalidate_branch(node_type, node_id)
        log.info(f"Invalidated {count} entities in branch")
        
        # Загружаем корневой узел заново
        self.load_details(node_type, node_id)
    
    # ===== Управление =====
    
    def clear_cache(self) -> None:
        """Очищает все кэши в загрузчике."""
        self._utils.clear_cache()
        log.debug("DataLoader cache cleared")
    
    def get_stats(self) -> dict:
        """Возвращает статистику работы загрузчика."""
        return {
            'loader': self._node_loader.get_stats() if hasattr(self._node_loader, 'get_stats') else {},
            'utils': self._utils.get_stats(),
        }
    
    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()
        
        log.info("\n" + "=" * 60)
        log.info("📊 DataLoader Statistics")
        log.info("=" * 60)
        
        log.info("\n🛠️  LoaderUtils:")
        log.info(f"  • Detail checks:  {stats['utils']['detail_checks']}")
        log.info(f"  • Detail cache hits: {stats['utils']['detail_cache_hits']}")
        log.info(f"  • Cache size:     {stats['utils']['cache_size']}")
        
        log.info("=" * 60)