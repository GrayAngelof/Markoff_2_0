# client/src/services/data_loader/loader.py
"""
Основная логика загрузки данных (NodeLoader).
Теперь поддерживает загрузку владельцев и контрагентов.
"""
from typing import Optional, List, Dict, Any, Type
from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM
from src.data.graph.schema import get_child_type
from src.data.entity_graph import EntityGraph
from src.services.api_client import ApiClient
from src.models import Complex, Building, Floor, Room
from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson

from utils.logger import get_logger


log = get_logger(__name__)


# Временные типы для контрагентов (пока не добавлены в NodeType)
COUNTERPARTY_TYPE = "counterparty"
RESPONSIBLE_PERSON_TYPE = "responsible_person"


class NodeLoader:
    """
    Ядро загрузки данных.
    
    Отвечает за:
    - Выполнение API-запросов
    - Преобразование данных в модели
    - Сохранение в граф
    - Загрузку связанных данных (владельцы, контрагенты)
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
        
        # Временное хранилище для контрагентов (пока граф не расширен)
        self._counterparties: Dict[int, Counterparty] = {}
        self._responsible_persons: Dict[int, List[ResponsiblePerson]] = {}
        
        # Статистика
        self._stats = {
            'api_calls': 0,
            'cache_hits': 0,
            'nodes_loaded': 0,
            'details_loaded': 0,
            'owners_loaded': 0,
            'persons_loaded': 0
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
            if not data:
                log.warning("API вернул пустой список комплексов")
                return []
            
            complexes = [Complex.from_dict(item) for item in data]
            
            # Сохраняем в граф
            for complex_obj in complexes:
                self._graph.add_or_update(complex_obj)
                
                # Если у комплекса есть владелец, загружаем его
                if complex_obj.owner_id:
                    self._load_owner_if_needed(complex_obj.owner_id)
            
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
        Автоматически загружает владельцев для корпусов.
        
        Args:
            parent_type: Тип родителя
            parent_id: ID родителя
            child_type: Тип детей
            
        Returns:
            List: Загруженные дочерние элементы
        """
        log.debug(f"load_children: {parent_type}#{parent_id} -> {child_type}")
        
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
        
        self._stats['api_calls'] += 1
        
        try:
            # Для корпусов загружаем с включением данных о владельце
            if child_type == BUILDING:
                data = api_method(self._api, parent_id, include_owner=True)
            else:
                data = api_method(self._api, parent_id)
            
            if not data:
                log.warning(f"API вернул пустые данные для {parent_type}#{parent_id}")
                return []
            
            models = [model_class.from_dict(item) for item in data]
            
            # Сохраняем в граф и загружаем связанные данные
            for model in models:
                self._graph.add_or_update(model)
                
                # Если это корпус и у него есть владелец, загружаем данные владельца
                if child_type == BUILDING and isinstance(model, Building) and model.owner_id:
                    self._load_owner_if_needed(model.owner_id)
            
            self._stats['nodes_loaded'] += len(models)
            log.info(f"Загружено {len(models)} {child_type.value}")
            
            return models
            
        except Exception as e:
            log.error(f"Ошибка загрузки {child_type} для {parent_type}#{parent_id}: {e}")
            raise
    
    def load_details(self, node_type: NodeType, node_id: int) -> Optional[Any]:
        """
        Загружает детальную информацию об объекте.
        Для помещений может загружать данные об арендаторе.
        
        Args:
            node_type: Тип узла
            node_id: ID узла
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
            raise ValueError(f"Неизвестный класс модели для типа {node_type}")

        self._stats['api_calls'] += 1

        try:
            # Для помещений загружаем с включением данных об арендаторе
            if node_type == ROOM:
                data = api_method(self._api, node_id, include_tenant=True)
            else:
                data = api_method(self._api, node_id)
            
            if not data:
                log.warning(f"API вернул пустые данные для {node_type}#{node_id}")
                return None
            
            detailed = model_class.from_dict(data)
            
            # Сохраняем в граф
            self._graph.add_or_update(detailed)
            
            # Если это корпус и у него есть владелец, загружаем данные владельца
            if node_type == BUILDING and isinstance(detailed, Building) and detailed.owner_id:
                self._load_owner_if_needed(detailed.owner_id)
            
            self._stats['details_loaded'] += 1
            log.info(f"Загружены детали для {node_type}#{node_id}")
            
            return detailed
            
        except Exception as e:
            log.error(f"Ошибка загрузки деталей {node_type}#{node_id}: {e}")
            raise
    
    # ===== Методы для загрузки связанных данных =====
    
    def _load_owner_if_needed(self, owner_id: int) -> Optional[Counterparty]:
        """
        Загружает данные о владельце, если их нет в кэше.
        
        Args:
            owner_id: ID владельца (контрагента)
            
        Returns:
            Optional[Counterparty]: Загруженный контрагент или None
        """
        # Проверяем, есть ли уже в кэше
        if owner_id in self._counterparties:
            log.cache(f"Владелец #{owner_id} уже в кэше")
            return self._counterparties[owner_id]
        
        log.debug(f"Загрузка данных владельца #{owner_id}")
        self._stats['api_calls'] += 1
        
        try:
            data = self._api.get_counterparty(owner_id)
            if not data:
                log.warning(f"Не удалось загрузить владельца #{owner_id}")
                return None
            
            owner = Counterparty.from_dict(data)
            
            # Сохраняем в кэш
            self._counterparties[owner_id] = owner
            
            # Загружаем ответственных лиц для этого контрагента
            self._load_responsible_persons(owner_id)
            
            self._stats['owners_loaded'] += 1
            log.info(f"Загружен владелец: {owner.short_name}")
            
            return owner
            
        except Exception as e:
            log.error(f"Ошибка загрузки владельца #{owner_id}: {e}")
            return None
    
    def _load_responsible_persons(self, counterparty_id: int) -> List[ResponsiblePerson]:
        """
        Загружает список ответственных лиц для контрагента.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            List[ResponsiblePerson]: Список ответственных лиц
        """
        # Проверяем, есть ли уже в кэше
        if counterparty_id in self._responsible_persons:
            log.cache(f"Ответственные лица для контрагента #{counterparty_id} уже в кэше")
            return self._responsible_persons[counterparty_id]
        
        log.debug(f"Загрузка ответственных лиц для контрагента #{counterparty_id}")
        self._stats['api_calls'] += 1
        
        try:
            data = self._api.get_responsible_persons(counterparty_id)
            if not data:
                log.warning(f"API вернул пустые данные для ответственных лиц контрагента #{counterparty_id}")
                return []
            
            persons = [ResponsiblePerson.from_dict(item) for item in data]
            
            # Сохраняем в кэш
            self._responsible_persons[counterparty_id] = persons
            
            self._stats['persons_loaded'] += len(persons)
            log.info(f"Загружено {len(persons)} ответственных лиц")
            
            return persons
        
        except Exception as e:
            log.error(f"Ошибка загрузки ответственных лиц: {e}")
            return []
    
    def get_owner_for_building(self, building: Building) -> Optional[Counterparty]:
        """
        Получает владельца для корпуса (из кэша или загружает).
        
        Args:
            building: Объект корпуса
            
        Returns:
            Optional[Counterparty]: Владелец или None
        """
        if not building or not building.owner_id:
            return None
        
        return self._load_owner_if_needed(building.owner_id)
    
    def get_responsible_persons(self, counterparty_id: int) -> List[ResponsiblePerson]:
        """
        Получает ответственных лиц для контрагента.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            List[ResponsiblePerson]: Список ответственных лиц
        """
        return self._load_responsible_persons(counterparty_id)
    
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
            return (entity.description is not None or 
                   entity.address is not None or 
                   entity.owner_id is not None)
            
        elif node_type == FLOOR and isinstance(entity, Floor):
            return entity.description is not None
            
        elif node_type == ROOM and isinstance(entity, Room):
            return (entity.area is not None or 
                   entity.status_code is not None or
                   entity.description is not None)
            
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику загрузчика."""
        return self._stats.copy()
    
    def clear_cache(self) -> None:
        """Очищает кэш контрагентов и ответственных лиц."""
        self._counterparties.clear()
        self._responsible_persons.clear()
        log.debug("Кэш контрагентов очищен")