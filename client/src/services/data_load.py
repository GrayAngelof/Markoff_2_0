# client/src/services/data_load.py
"""
Сервис загрузки данных - фасад для компонентной архитектуры.
"""
from typing import Dict, Any, Optional, List

from src.core.event_bus import EventBus
from src.data.entity_graph import EntityGraph
from src.data.entity_types import NodeType
from src.services.api_client import ApiClient

# Импортируем компоненты из пакета data_loader
from src.services.data_loader.loader import NodeLoader
from src.services.data_loader.events import EventHandler
from src.services.data_loader.utils import LoaderUtils

# Импортируем модели для типизации
from src.models.building import Building
from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson

from utils.logger import get_logger


log = get_logger(__name__)


class DataLoader:
    """
    Фасад для загрузки данных.
    
    Предоставляет единый интерфейс для:
    - Прямой загрузки данных (load_complexes, load_children, load_details)
    - Работы через события (автоматически через EventHandler)
    - Управления кэшем и статистикой
    - Доступа к связанным данным (владельцы, контактные лица)
    
    Все сложные взаимодействия делегируются компонентам.
    """
    
    def __init__(self, event_bus: EventBus, api_client: ApiClient, graph: EntityGraph) -> None:
        """
        Инициализирует DataLoader.
        
        Args:
            event_bus: Шина событий (для подписок)
            api_client: HTTP-клиент
            graph: Граф сущностей
        """
        self._bus = event_bus
        self._api = api_client
        self._graph = graph
        
        # Создаём компоненты
        self._loader = NodeLoader(api_client, graph)
        self._utils = LoaderUtils()
        self._events = EventHandler(event_bus, self._loader, self._utils)
        
        log.info("=" * 50)
        log.success("DataLoader инициализирован (компонентная архитектура)")
        log.info(f"  • NodeLoader: загрузчик узлов")
        log.info(f"  • EventHandler: обработчик событий")
        log.info(f"  • LoaderUtils: утилиты и кэш")
        log.info("=" * 50)
    
    # ===== Методы для прямой загрузки (делегируются NodeLoader) =====
    
    def load_complexes(self) -> List:
        """
        Загружает все комплексы.
        
        Returns:
            List[Complex]: Загруженные комплексы
        """
        log.debug("DataLoader.load_complexes делегировано NodeLoader")
        return self._loader.load_complexes()
    
    def load_children(self, parent_type: NodeType, parent_id: int, 
                      child_type: NodeType) -> List:
        """
        Загружает дочерние элементы для родителя.
        
        Args:
            parent_type: Тип родителя
            parent_id: ID родителя
            child_type: Тип детей
            
        Returns:
            List: Загруженные дочерние элементы
        """
        log.debug(f"DataLoader.load_children делегировано NodeLoader: {parent_type}#{parent_id} -> {child_type}")
        return self._loader.load_children(parent_type, parent_id, child_type)
    
    def load_details(self, node_type: NodeType, node_id: int) -> Optional[Any]:
        """
        Загружает детальную информацию об объекте.
        
        Args:
            node_type: Тип узла
            node_id: ID узла
            
        Returns:
            Optional[Any]: Детальная информация
        """
        log.debug(f"DataLoader.load_details делегировано NodeLoader: {node_type}#{node_id}")
        return self._loader.load_details(node_type, node_id)
    
    # ===== НОВЫЕ МЕТОДЫ для работы с контрагентами =====
    
    def get_owner_for_building(self, building: Building) -> Optional[Counterparty]:
        """
        Получает владельца для корпуса.
        
        Args:
            building: Объект корпуса
            
        Returns:
            Optional[Counterparty]: Владелец или None
        """
        log.debug(f"DataLoader.get_owner_for_building делегировано NodeLoader для корпуса {building.id}")
        return self._loader.get_owner_for_building(building)
    
    def load_counterparty(self, counterparty_id: int) -> Optional[Counterparty]:
        """
        Загружает контрагента по ID.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            Optional[Counterparty]: Контрагент или None
        """
        log.debug(f"DataLoader.load_counterparty делегировано NodeLoader для ID {counterparty_id}")
        return self._loader._load_owner_if_needed(counterparty_id)
    
    def get_responsible_persons(self, counterparty_id: int) -> List[ResponsiblePerson]:
        """
        Получает ответственных лиц для контрагента.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            List[ResponsiblePerson]: Список ответственных лиц
        """
        log.debug(f"DataLoader.get_responsible_persons делегировано NodeLoader для ID {counterparty_id}")
        return self._loader.get_responsible_persons(counterparty_id)
    
    # ===== Методы перезагрузки =====
    
    def reload_node(self, node_type: NodeType, node_id: int) -> None:
        """
        Перезагружает узел (инвалидирует и загружает заново).
        
        Args:
            node_type: Тип узла
            node_id: ID узла
        """
        log.info(f"DataLoader.reload_node: {node_type}#{node_id}")
        self._loader.reload_node(node_type, node_id)
    
    def reload_branch(self, node_type: NodeType, node_id: int) -> None:
        """
        Перезагружает всю ветку.
        
        Args:
            node_type: Тип узла
            node_id: ID узла
        """
        log.info(f"DataLoader.reload_branch: {node_type}#{node_id}")
        self._loader.reload_branch(node_type, node_id)
    
    # ===== Методы управления =====
    
    def cleanup(self) -> None:
        """Очищает ресурсы и отписывается от событий."""
        log.info("DataLoader.cleanup: очистка ресурсов")
        self._events.cleanup()
        self._loader.clear_cache()
        self._utils.clear_cache()
        log.debug("DataLoader: ресурсы очищены")
    
    def clear_cache(self) -> None:
        """Очищает внутренний кэш деталей."""
        log.debug("DataLoader.clear_cache: очистка кэша")
        self._loader.clear_cache()
        self._utils.clear_cache()
    
    # ===== Утилиты =====
    
    def has_details(self, entity: Any, node_type: NodeType) -> bool:
        """
        Проверяет, загружены ли детальные поля.
        
        Args:
            entity: Сущность для проверки
            node_type: Тип сущности
            
        Returns:
            bool: True если детали загружены
        """
        return self._utils.has_details(entity, node_type)
    
    def format_node_id(self, node_type: NodeType, node_id: int) -> str:
        """Форматирует идентификатор узла."""
        return self._utils.format_node_id(node_type, node_id)
    
    def parse_node_id(self, formatted: str) -> tuple:
        """Разбирает отформатированный идентификатор."""
        return self._utils.parse_node_id(formatted)
    
    # ===== Статистика =====
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает полную статистику работы загрузчика.
        
        Returns:
            Dict с ключами:
            - loader: статистика NodeLoader
            - utils: статистика LoaderUtils
            - graph_stats: статистика графа
        """
        stats = {
            'loader': self._loader.get_stats(),
            'utils': self._utils.get_stats(),
            'graph_stats': self._graph.get_stats()
        }
        
        log.debug(f"DataLoader stats: {stats['loader']['api_calls']} API calls, "
                 f"{stats['loader']['cache_hits']} cache hits")
        
        return stats
    
    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()
        
        log.info("\n" + "=" * 60)
        log.info("📊 DataLoader Statistics")
        log.info("=" * 60)
        
        log.info("\n🔧 NodeLoader:")
        log.info(f"  • API calls:      {stats['loader']['api_calls']}")
        log.info(f"  • Cache hits:     {stats['loader']['cache_hits']}")
        log.info(f"  • Nodes loaded:   {stats['loader']['nodes_loaded']}")
        log.info(f"  • Details loaded: {stats['loader']['details_loaded']}")
        log.info(f"  • Owners loaded:  {stats['loader'].get('owners_loaded', 0)}")
        log.info(f"  • Persons loaded: {stats['loader'].get('persons_loaded', 0)}")
        
        log.info("\n🛠️  LoaderUtils:")
        log.info(f"  • Detail checks:  {stats['utils']['detail_checks']}")
        log.info(f"  • Cache hits:     {stats['utils']['detail_cache_hits']}")
        log.info(f"  • Cache size:     {stats['utils']['cache_size']}")
        
        log.info("\n📦 EntityGraph:")
        log.info(f"  • Total entities: {stats['graph_stats']['total_entities']}")
        for node_type, count in stats['graph_stats']['by_type'].items():
            log.info(f"  • {node_type}: {count}")
        
        log.info("=" * 60 + "\n")
    
    # ===== Свойства для доступа к компонентам (для тестирования) =====
    
    @property
    def loader(self) -> NodeLoader:
        """Возвращает внутренний NodeLoader (для тестов)."""
        return self._loader
    
    @property
    def utils(self) -> LoaderUtils:
        """Возвращает внутренний LoaderUtils (для тестов)."""
        return self._utils
    
    @property
    def events(self) -> EventHandler:
        """Возвращает внутренний EventHandler (для тестов)."""
        return self._events