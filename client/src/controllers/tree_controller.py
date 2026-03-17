# client/src/controllers/tree_controller.py (исправленный)
"""
Контроллер дерева объектов.
Обновлён для работы с владельцами корпусов.
"""
from typing import Optional, Dict, Any

from src.core.event_bus import EventBus
from src.core.events import UIEvents, SystemEvents
from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM, COUNTERPARTY
from src.data.graph.schema import get_child_type
from src.services.data_load import DataLoader
from src.data.entity_graph import EntityGraph
from src.controllers.base import BaseController

from utils.logger import get_logger


class TreeController(BaseController):
    """
    Контроллер дерева объектов.
    
    Логика:
    - При раскрытии узла → загрузить детей (с владельцами для корпусов)
    - При выборе узла → загрузить детали и информацию о владельце
    - При обновлении → инвалидировать и перезагрузить
    """
    
    def __init__(self, event_bus: EventBus, loader: DataLoader, graph: EntityGraph):
        """
        Инициализирует контроллер дерева.
        
        Args:
            event_bus: Шина событий
            loader: Загрузчик данных
            graph: Граф сущностей
        """
        super().__init__(event_bus)
        
        self._loader = loader
        self._graph = graph
        
        # Подписки на события UI
        self._subscribe(UIEvents.NODE_EXPANDED, self._on_node_expanded)
        self._subscribe(UIEvents.NODE_SELECTED, self._on_node_selected)
        self._subscribe(UIEvents.GET_SELECTED_NODE, self._on_get_selected_node)
        self._subscribe(UIEvents.REFRESH_REQUESTED, self._on_refresh_requested)
        
        self._logger.info("TreeController инициализирован (с поддержкой владельцев)")
    
    # ===== Обработчики событий =====
    
    def _on_node_expanded(self, event: Dict[str, Any]) -> None:
        """
        Пользователь раскрыл узел - загружаем детей при необходимости.
        Для корпусов автоматически загружаем владельцев.
        """
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        
        self._logger.debug(f"Раскрыт узел {node_type}#{node_id}")
        
        # Определяем тип детей
        child_type = get_child_type(node_type)
        if not child_type:
            self._logger.debug(f"Тип {node_type} не может иметь детей")
            return
        
        # Проверяем, нужно ли загружать
        existing_ids = self._graph.get_children(node_type, node_id)
        
        if not existing_ids:
            # Нет детей в графе - загружаем
            self._logger.info(f"Загрузка детей для {node_type}#{node_id}")
            children = self._loader.load_children(node_type, node_id, child_type)
            
            # Для корпусов отправляем событие о загрузке владельцев
            if child_type == BUILDING and children:
                self._notify_owners_loaded(children)
        else:
            # Дети есть - проверяем валидность
            if not all(self._graph.is_valid(child_type, cid) for cid in existing_ids):
                self._logger.info(f"Дети для {node_type}#{node_id} невалидны, перезагрузка")
                self._loader.reload_node(node_type, node_id)
            else:
                self._logger.debug(f"Дети для {node_type}#{node_id} уже в графе")
    
    def _on_node_selected(self, event: Dict[str, Any]) -> None:
        """
        Пользователь выбрал узел - загружаем детали и информацию о владельце.
        """
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        node_data = event['data'].get('data')
        
        self._logger.debug(f"Выбран узел {node_type}#{node_id}")
        
        # Собираем контекст для узла (имена родителей)
        context = self.get_selected_node_context(node_type, node_id)
        
        # Для корпусов загружаем информацию о владельце
        if node_type == BUILDING and node_data:
            self._load_building_owner_info(node_id, node_data, context)
        
        # Для комнат грузим детали
        elif node_type == ROOM:
            self._logger.info(f"Загрузка деталей для комнаты {node_id}")
            self._loader.load_details(node_type, node_id)
        
        # Для этажей грузим детали если нужно
        elif node_type == FLOOR:
            floor = self._graph.get(node_type, node_id)
            if floor and not floor.description:
                self._logger.info(f"Загрузка деталей для этажа {node_id}")
                self._loader.load_details(node_type, node_id)
    
    def _load_building_owner_info(self, building_id: int, building_data, context: Dict[str, Optional[str]]) -> None:
        """
        Загружает информацию о владельце корпуса.
        
        Args:
            building_id: ID корпуса
            building_data: Данные корпуса
            context: Контекст иерархии
        """
        if not hasattr(building_data, 'owner_id') or not building_data.owner_id:
            self._logger.debug(f"Корпус {building_id} не имеет владельца")
            return
        
        self._logger.info(f"Загрузка информации о владельце для корпуса {building_id}")
        
        # Загружаем данные о владельце
        owner = self._loader.load_counterparty(building_data.owner_id)
        
        if owner:
            # Отправляем событие с информацией о владельце
            self._bus.emit('ui.building_owner_loaded', {
                'building_id': building_id,
                'owner': owner,
                'context': context
            }, source='tree_controller')
    
    def _notify_owners_loaded(self, buildings: list) -> None:
        """
        Уведомляет о загрузке владельцев для списка корпусов.
        
        Args:
            buildings: Список загруженных корпусов
        """
        for building in buildings:
            if hasattr(building, 'owner_id') and building.owner_id:
                self._bus.emit('ui.building_owner_loaded', {
                    'building_id': building.id,
                    'owner_id': building.owner_id
                }, source='tree_controller')
    
    def _on_refresh_requested(self, event: Dict[str, Any]) -> None:
        """Обрабатывает запросы на обновление."""
        mode = event['data'].get('mode', 'current')
        
        if mode == 'current':
            self._handle_refresh_current(event['data'])
    
    def _handle_refresh_current(self, data: Dict[str, Any]) -> None:
        """Обновление текущего узла."""
        node_type = data.get('node_type')
        node_id = data.get('node_id')
        
        if not node_type or not node_id:
            self._logger.warning("Недостаточно данных для обновления текущего узла")
            return
        
        self._logger.info(f"Обновление текущего узла {node_type}#{node_id}")
        
        # Инвалидируем в графе
        self._graph.invalidate(node_type, node_id)
        
        # Если это корпус, инвалидируем также данные владельца
        if node_type == BUILDING:
            building = self._graph.get(node_type, node_id)
            if building and hasattr(building, 'owner_id') and building.owner_id:
                self._graph.invalidate(COUNTERPARTY, building.owner_id)  # <-- ИСПРАВЛЕНО: используем константу
        
        # Перезагружаем
        if node_type == COMPLEX:
            child_type = get_child_type(node_type)
            if child_type:
                self._loader.load_children(node_type, node_id, child_type)
        else:
            self._loader.load_details(node_type, node_id)
    
    def _on_get_selected_node(self, event: Dict[str, Any]) -> None:
        """Запрос текущего выбранного узла."""
        self._logger.debug("Получен запрос выбранного узла")
    
    def get_selected_node_context(self, node_type: NodeType, node_id: int) -> Dict[str, Optional[str]]:
        """
        Собирает контекст для узла (имена родителей).
        
        Returns:
            Dict с ключами: complex_name, building_name, floor_num, owner_name
            Все значения могут быть None
        """
        context: Dict[str, Optional[str]] = {  # <-- ИСПРАВЛЕНО: явная типизация
            'complex_name': None,
            'building_name': None,
            'floor_num': None,
            'owner_name': None,
            'complex_owner': None
        }
        
        # Собираем предков
        ancestors = self._graph.get_ancestors(node_type, node_id)
        
        for anc_type, anc_id in ancestors:
            entity = self._graph.get(anc_type, anc_id)
            if not entity:
                continue
            
            if anc_type == COMPLEX:
                context['complex_name'] = str(entity.name) if entity.name else None
                # У комплекса тоже может быть владелец
                if hasattr(entity, 'owner_id') and entity.owner_id:
                    owner = self._loader.load_counterparty(entity.owner_id)
                    if owner:
                        context['complex_owner'] = owner.short_name
                        
            elif anc_type == BUILDING:
                context['building_name'] = str(entity.name) if entity.name else None
                # У корпуса может быть владелец
                if hasattr(entity, 'owner_id') and entity.owner_id:
                    owner = self._loader.load_counterparty(entity.owner_id)
                    if owner:
                        context['owner_name'] = owner.short_name
                        
            elif anc_type == FLOOR:
                context['floor_num'] = str(entity.number) if hasattr(entity, 'number') else None
        
        self._logger.debug(f"Контекст для {node_type}#{node_id}: {context}")
        return context