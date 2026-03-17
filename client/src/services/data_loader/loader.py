# client/src/services/data_loader/loader.py
"""
Основная логика загрузки данных (NodeLoader).
Не зависит от Qt и событий - чистая бизнес-логика.
"""
from typing import Optional, List, Dict, Any
from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM
from src.data.graph.schema import get_child_type
from src.data.entity_graph import EntityGraph
from src.services.api_client import ApiClient
from src.models import Complex, Building, Floor, Room

from utils.logger import get_logger


log = get_logger(__name__)


class NodeLoader:
    """
    Ядро загрузки данных.
    
    Отвечает только за:
    - Выполнение API-запросов
    - Преобразование данных в модели
    - Сохранение в граф
    
    Не знает о:
    - Событиях
    - UI
    - Qt
    """
    
    # Маппинг NodeType на методы API для списков
    _LIST_API_MAP = {
        COMPLEX: (ApiClient.get_complexes, Complex, None),
        BUILDING: (ApiClient.get_buildings, Building, COMPLEX),
        FLOOR: (ApiClient.get_floors, Floor, BUILDING),
        ROOM: (ApiClient.get_rooms, Room, FLOOR),
    }
    
    # Маппинг NodeType на методы API для деталей
    _DETAIL_API_MAP = {
        COMPLEX: ApiClient.get_complex_detail,
        BUILDING: ApiClient.get_building_detail,
        FLOOR: ApiClient.get_floor_detail,
        ROOM: ApiClient.get_room_detail,
    }
    
    # Маппинг NodeType на классы моделей
    _MODEL_CLASS_MAP = {
        COMPLEX: Complex,
        BUILDING: Building,
        FLOOR: Floor,
        ROOM: Room,
    }
    
    def __init__(self, api_client: ApiClient, graph: EntityGraph) -> None:
        """
        Инициализирует загрузчик узлов.
        
        Args:
            api_client: HTTP-клиент
            graph: Граф сущностей
        """
        self._api = api_client
        self._graph = graph
        
        # Статистика
        self._stats = {
            'api_calls': 0,
            'cache_hits': 0,
            'nodes_loaded': 0,
            'details_loaded': 0
        }
        
        log.debug("NodeLoader инициализирован")
    
    # ===== Основные методы загрузки =====
    
    def load_complexes(self) -> List[Complex]:
        """
        Загружает все комплексы.
        
        Returns:
            List[Complex]: Загруженные комплексы
        """
        log.info("Загрузка комплексов...")
        self._stats['api_calls'] += 1
        
        try:
            data = self._api.get_complexes()
            complexes = [Complex.from_dict(item) for item in data]
            
            # Сохраняем в граф
            for complex_obj in complexes:
                self._graph.add_or_update(complex_obj)
            
            self._stats['nodes_loaded'] += len(complexes)
            log.success(f"Загружено {len(complexes)} комплексов")
            
            return complexes
            
        except Exception as e:
            log.error(f"Ошибка загрузки комплексов: {e}")
            raise
    
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
            
        Raises:
            ValueError: При недопустимой связи
        """
        log.debug(f"load_children: {parent_type}#{parent_id} -> {child_type}")
        
        # Проверяем связь
        expected_child = get_child_type(parent_type)
        if expected_child != child_type:
            raise ValueError(f"Недопустимая связь: {parent_type} -> {child_type}")
        
        # Проверяем кэш
        existing_ids = self._graph.get_children(parent_type, parent_id)
        if existing_ids and all(self._graph.is_valid(child_type, cid) for cid in existing_ids):
            self._stats['cache_hits'] += 1
            log.cache(f"Данные для {parent_type}#{parent_id} в кэше")
            return [self._graph.get(child_type, cid) for cid in existing_ids]
        
        # Загружаем с API
        api_method_info = self._LIST_API_MAP.get(child_type)
        if not api_method_info:
            raise ValueError(f"Неизвестный тип для загрузки: {child_type}")
        
        api_method, model_class, expected_parent = api_method_info
        
        # Проверяем родителя
        if expected_parent and expected_parent != parent_type:
            raise ValueError(f"Ожидался родитель {expected_parent}, получен {parent_type}")
        
        self._stats['api_calls'] += 1
        data = api_method(self._api, parent_id)
        models = [model_class.from_dict(item) for item in data]
        
        # Сохраняем в граф
        for model in models:
            self._graph.add_or_update(model)
        
        self._stats['nodes_loaded'] += len(models)
        log.info(f"Загружено {len(models)} {child_type.value}")
        
        return models
    
    def load_details(self, node_type: NodeType, node_id: int) -> Optional[Any]:
        """
        Загружает детальную информацию об объекте.
        
        Args:
            node_type: Тип узла
            node_id: ID узла
            
        Returns:
            Optional[Any]: Детальная информация или None
        """
        log.debug(f"load_details: {node_type}#{node_id}")
        
        # Проверяем кэш
        existing = self._graph.get(node_type, node_id)
        if existing and self._graph.is_valid(node_type, node_id):
            if self._has_details(existing, node_type):
                self._stats['cache_hits'] += 1
                log.cache(f"Детали для {node_type}#{node_id} в кэше")
                return existing
        
        # Загружаем с API
        api_method = self._DETAIL_API_MAP.get(node_type)
        if not api_method:
            raise ValueError(f"Детальная загрузка не поддерживается для {node_type}")
        
        model_class = self._MODEL_CLASS_MAP.get(node_type)
        if not model_class:
            raise ValueError(f"Неизвестный класс модели для {node_type}")
        
        self._stats['api_calls'] += 1
        data = api_method(self._api, node_id)
        
        if not data:
            log.warning(f"API вернул пустые данные для {node_type}#{node_id}")
            return None
        
        detailed = model_class.from_dict(data)
        
        # Сохраняем в граф
        self._graph.add_or_update(detailed)
        
        self._stats['details_loaded'] += 1
        log.info(f"Загружены детали для {node_type}#{node_id}")
        
        return detailed
    
    # ===== Методы перезагрузки =====
    
    def reload_node(self, node_type: NodeType, node_id: int) -> None:
        """
        Перезагружает узел (инвалидирует и загружает заново).
        """
        log.info(f"Перезагрузка узла {node_type}#{node_id}")
        
        self._graph.invalidate(node_type, node_id)
        
        if node_type == COMPLEX:
            child_type = get_child_type(node_type)
            if child_type:
                self.load_children(node_type, node_id, child_type)
        else:
            self.load_details(node_type, node_id)
    
    def reload_branch(self, node_type: NodeType, node_id: int) -> None:
        """
        Перезагружает всю ветку.
        """
        log.info(f"Перезагрузка ветки {node_type}#{node_id}")
        
        count = self._graph.invalidate_branch(node_type, node_id)
        log.debug(f"Инвалидировано {count} сущностей")
        
        self.reload_node(node_type, node_id)
    
    # ===== Вспомогательные методы =====
    
    def _has_details(self, entity: Any, node_type: NodeType) -> bool:
        """Проверяет, загружены ли детальные поля."""
        if node_type == COMPLEX and isinstance(entity, Complex):
            return entity.description is not None or entity.address is not None
            
        elif node_type == BUILDING and isinstance(entity, Building):
            return entity.description is not None or entity.address is not None
            
        elif node_type == FLOOR and isinstance(entity, Floor):
            return entity.description is not None
            
        elif node_type == ROOM and isinstance(entity, Room):
            return entity.area is not None or entity.status_code is not None
            
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику загрузчика."""
        return self._stats.copy()