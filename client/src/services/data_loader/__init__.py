# client/src/services/data_loader/__init__.py
"""
Интеграционный DataLoader - фасад для загрузки данных.
Объединяет обработку событий, логику загрузки и утилиты.
"""
from PySide6.QtCore import QObject
from typing import Dict, Any

from src.core.event_bus import EventBus
from src.core.events import SystemEvents
from src.data.entity_graph import EntityGraph
from src.services.api_client import ApiClient
from src.services.data_loader.loader import NodeLoader
from src.services.data_loader.events import EventHandler
from src.services.data_loader.utils import LoaderUtils

from utils.logger import get_logger


log = get_logger(__name__)


class DataLoader(QObject):
    """
    Интеграционный DataLoader - фасад для загрузки данных.
    
    Композиция:
    - NodeLoader: основная логика загрузки
    - EventHandler: обработка событий
    - LoaderUtils: вспомогательные функции
    
    Роли:
    1. Координирует работу компонентов
    2. Управляет жизненным циклом подписок
    3. Предоставляет единый интерфейс наружу
    """
    
    def __init__(self, event_bus: EventBus, api_client: ApiClient, graph: EntityGraph) -> None:
        """
        Инициализирует DataLoader.
        
        Args:
            event_bus: Шина событий
            api_client: HTTP-клиент
            graph: Граф сущностей
        """
        super().__init__()
        
        self._bus = event_bus
        self._api = api_client
        self._graph = graph
        
        # Создаём компоненты
        self._loader = NodeLoader(api_client, graph)
        self._utils = LoaderUtils()
        self._events = EventHandler(event_bus, self._loader, self._utils)
        
        log.success("DataLoader инициализирован (компонентная архитектура)")
    
    def cleanup(self) -> None:
        """Очищает ресурсы и отписывается от событий."""
        self._events.cleanup()
        log.debug("DataLoader: ресурсы очищены")
    
    # ===== Публичные методы (делегирование) =====
    
    def load_complexes(self) -> None:
        """Загружает все комплексы."""
        self._loader.load_complexes()
    
    def load_children(self, parent_type, parent_id, child_type) -> None:
        """Загружает дочерние элементы."""
        self._loader.load_children(parent_type, parent_id, child_type)
    
    def load_details(self, node_type, node_id) -> None:
        """Загружает детальную информацию."""
        self._loader.load_details(node_type, node_id)
    
    def reload_node(self, node_type, node_id) -> None:
        """Перезагружает узел."""
        self._loader.reload_node(node_type, node_id)
    
    def reload_branch(self, node_type, node_id) -> None:
        """Перезагружает ветку."""
        self._loader.reload_branch(node_type, node_id)
    
    # ===== Статистика =====
    
    def get_loader_stats(self) -> Dict[str, Any]:
        """Возвращает статистику работы загрузчика."""
        return {
            'loader': self._loader.get_stats(),
            'utils': self._utils.get_stats(),
            'graph_stats': self._graph.get_stats()
        }