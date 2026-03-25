# client/src/services/loading/node_loader.py
"""
Загрузчик физической иерархии (комплексы, корпуса, этажи, помещения).

Тупой исполнитель — не знает о типах узлов, всё приходит через конфигурацию.
Не содержит if-elif по типам, только вызовы переданных лоадеров.
"""

from typing import List, Optional, Any, Callable, Dict

from src.core import NodeType
from src.core.types.nodes import NodeID 
from src.models import Complex, Building, Floor, Room
from src.services.api_client import ApiClient
from src.data import EntityGraph
from utils.logger import get_logger

log = get_logger(__name__)


class NodeLoader:
    """
    Ядро загрузки физической иерархии.
    
    Тупой исполнитель — конфигурация (какие методы вызывать для каких типов)
    передаётся снаружи. Это позволяет:
    - Не менять NodeLoader при добавлении новых типов
    - Легко тестировать с моками
    - Держать код чистым и предсказуемым
    
    Архитектура:
        DataLoader создаёт словари child_loaders и detail_loaders,
        передаёт их в NodeLoader. NodeLoader просто вызывает переданные функции.
    """
    
    def __init__(
        self,
        api: ApiClient,
        graph: EntityGraph,
        child_loaders: Dict[NodeType, Callable[[ApiClient, NodeID], List[Any]]],
        detail_loaders: Dict[NodeType, Callable[[ApiClient, NodeID], Optional[Any]]],
    ):
        """
        Инициализирует загрузчик узлов.
        
        Args:
            api: HTTP клиент
            graph: Граф сущностей для сохранения
            child_loaders: Словарь {тип_ребёнка: функция_загрузки}
                          Функция принимает (api, parent_id) и возвращает список
            detail_loaders: Словарь {тип_узла: функция_загрузки_деталей}
                           Функция принимает (api, node_id) и возвращает объект
        """
        self._api = api
        self._graph = graph
        self._child_loaders = child_loaders
        self._detail_loaders = detail_loaders
        
        log.system("NodeLoader инициализирован")
        log.debug(f"Зарегистрировано child_loader'ов: {len(child_loaders)}")
        log.debug(f"Зарегистрировано detail_loader'ов: {len(detail_loaders)}")
    
    # ===== Списочные загрузчики (конкретные, для удобства) =====
    
    def load_complexes(self) -> List[Complex]:
        """Загружает все комплексы."""
        log.info("Загрузка комплексов")
        
        data = self._api.get_complexes()
        for item in data:
            self._graph.add_or_update(item)
        
        log.info(f"Загружено {len(data)} комплексов")
        return data
    
    def load_buildings(self, complex_id: NodeID) -> List[Building]:
        """Загружает корпуса комплекса."""
        log.info(f"Загрузка корпусов для комплекса {complex_id}")
        
        data = self._api.get_buildings(complex_id)
        for item in data:
            self._graph.add_or_update(item)
        
        log.info(f"Загружено {len(data)} корпусов для комплекса {complex_id}")
        return data
    
    def load_floors(self, building_id: NodeID) -> List[Floor]:
        """Загружает этажи корпуса."""
        log.info(f"Загрузка этажей для корпуса {building_id}")
        
        data = self._api.get_floors(building_id)
        for item in data:
            self._graph.add_or_update(item)
        
        log.info(f"Загружено {len(data)} этажей для корпуса {building_id}")
        return data
    
    def load_rooms(self, floor_id: NodeID) -> List[Room]:
        """Загружает помещения этажа."""
        log.info(f"Загрузка помещений для этажа {floor_id}")
        
        data = self._api.get_rooms(floor_id)
        for item in data:
            self._graph.add_or_update(item)
        
        log.info(f"Загружено {len(data)} помещений для этажа {floor_id}")
        return data
    
    # ===== Универсальные загрузчики (через DI) =====
    
    def load_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType,
    ) -> List[Any]:
        """
        Универсальная загрузка детей.
        
        Args:
            parent_type: Тип родителя (не используется, но для контекста)
            parent_id: ID родителя
            child_type: Тип детей (определяет, какой лоадер вызвать)
            
        Returns:
            List[Any]: Список загруженных детей
            
        Raises:
            KeyError: Если для child_type нет загрузчика
        """
        loader = self._child_loaders.get(child_type)
        if not loader:
            log.error(f"Не найден загрузчик для типа {child_type}")
            raise KeyError(f"No child loader for type: {child_type}")
        
        log.info(f"Загрузка {child_type.value} для {parent_type.value}#{parent_id}")
        
        data = loader(self._api, parent_id)
        for item in data:
            self._graph.add_or_update(item)
        
        log.info(f"Загружено {len(data)} {child_type.value} для {parent_type.value}#{parent_id}")
        return data
    
    def load_details(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """
        Универсальная загрузка деталей.
        
        Args:
            node_type: Тип узла (определяет, какой лоадер вызвать)
            node_id: ID узла
            
        Returns:
            Optional[Any]: Загруженные детали или None
            
        Raises:
            KeyError: Если для node_type нет загрузчика деталей
        """
        loader = self._detail_loaders.get(node_type)
        if not loader:
            log.error(f"Не найден загрузчик деталей для типа {node_type}")
            raise KeyError(f"No detail loader for type: {node_type}")
        
        log.debug(f"Загрузка деталей для {node_type.value}#{node_id}")
        
        data = loader(self._api, node_id)
        if data:
            self._graph.add_or_update(data)
            log.debug(f"Детали загружены для {node_type.value}#{node_id}")
        else:
            log.debug(f"Нет деталей для {node_type.value}#{node_id}")
        
        return data
    
    def get_stats(self) -> dict:
        """Возвращает статистику работы загрузчика."""
        # NodeLoader не собирает статистику, но метод нужен для интерфейса
        return {
            'api_calls': 0,  # можно добавить счетчики позже
            'cache_hits': 0,
            'nodes_loaded': 0,
        }