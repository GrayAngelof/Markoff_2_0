# client/src/controllers/tree_controller.py
"""
Контроллер дерева объектов.
Решает, что делать при раскрытии, выборе и обновлении узлов.
"""
from typing import Optional, Dict, Any

from src.core.event_bus import EventBus
from src.core.events import UIEvents, SystemEvents
from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM
from src.data.graph.schema import get_child_type
from src.services.data_loader import DataLoader
from src.data.entity_graph import EntityGraph
from src.controllers.base import BaseController

from utils.logger import get_logger


class TreeController(BaseController):
    """
    Контроллер дерева объектов.
    
    Логика:
    - При раскрытии узла → загрузить детей (через DataLoader)
    - При выборе узла → загрузить детали (если нужно)
    - При обновлении → инвалидировать и перезагрузить
    """
    
    def __init__(self, event_bus: EventBus, loader: DataLoader, graph: EntityGraph):
        """
        Инициализирует контроллер дерева.
        
        Args:
            event_bus: Шина событий
            loader: Загрузчик данных
            graph: Граф сущностей (для проверок)
        """
        super().__init__(event_bus)
        
        self._loader = loader
        self._graph = graph
        
        # Подписки на события UI
        self._subscribe(UIEvents.NODE_EXPANDED, self._on_node_expanded)
        self._subscribe(UIEvents.NODE_SELECTED, self._on_node_selected)
        self._subscribe(UIEvents.GET_SELECTED_NODE, self._on_get_selected_node)
        
        # Подписка на запросы обновления (частично)
        self._subscribe(UIEvents.REFRESH_REQUESTED, self._on_refresh_requested)
        
        self._logger.info("TreeController инициализирован")
    
    # ===== Обработчики событий =====
    
    def _on_node_expanded(self, event: Dict[str, Any]) -> None:
        """
        Пользователь раскрыл узел - загружаем детей при необходимости.
        
        Event data: {
            'node_type': NodeType,
            'node_id': int
        }
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
            
            # DataLoader сам сгенерирует события DATA_LOADING/DATA_LOADED
            self._loader.load_children(node_type, node_id, child_type)
        else:
            # Дети есть - проверяем валидность
            if not all(self._graph.is_valid(child_type, cid) for cid in existing_ids):
                self._logger.info(f"Дети для {node_type}#{node_id} невалидны, перезагрузка")
                self._loader.reload_node(node_type, node_id)
            else:
                self._logger.debug(f"Дети для {node_type}#{node_id} уже в графе")
    
    def _on_node_selected(self, event: Dict[str, Any]) -> None:
        """
        Пользователь выбрал узел - загружаем детали при необходимости.
        
        Event data: {
            'node_type': NodeType,
            'node_id': int,
            'data': object (базовые данные)
        }
        """
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        
        self._logger.debug(f"Выбран узел {node_type}#{node_id}")
        
        # Для комнат всегда грузим детали (статус, площадь)
        if node_type == ROOM:
            self._logger.info(f"Загрузка деталей для комнаты {node_id}")
            self._loader.load_details(node_type, node_id)
        
        # Для этажей тоже можно грузить детали (описание)
        elif node_type == FLOOR:
            # Проверяем, есть ли уже детали
            floor = self._graph.get(node_type, node_id)
            if floor and not floor.description:
                self._logger.info(f"Загрузка деталей для этажа {node_id}")
                self._loader.load_details(node_type, node_id)
        
        # Можно добавить другие типы по необходимости
        # elif node_type == BUILDING:
        #     ...
    
    def _on_refresh_requested(self, event: Dict[str, Any]) -> None:
        """
        Обрабатывает запросы на обновление.
        
        Event data: {
            'mode': 'current' | 'visible' | 'full',
            'node_type': NodeType (optional for current),
            'node_id': int (optional for current)
        }
        """
        mode = event['data'].get('mode', 'current')
        
        if mode == 'current':
            self._handle_refresh_current(event['data'])
        elif mode == 'visible':
            # visible обрабатывается в refresh_controller
            pass
        elif mode == 'full':
            # full обрабатывается в data_loader через events
            pass
    
    def _handle_refresh_current(self, data: Dict[str, Any]) -> None:
        """
        Обновление текущего узла.
        
        Args:
            data: Данные события с node_type и node_id
        """
        node_type = data.get('node_type')
        node_id = data.get('node_id')
        
        if not node_type or not node_id:
            self._logger.warning("Недостаточно данных для обновления текущего узла")
            return
        
        self._logger.info(f"Обновление текущего узла {node_type}#{node_id}")
        
        # Инвалидируем в графе
        self._graph.invalidate(node_type, node_id)
        
        # Перезагружаем
        if node_type == COMPLEX:
            child_type = get_child_type(node_type)
            if child_type:
                self._loader.load_children(node_type, node_id, child_type)
        else:
            self._loader.load_details(node_type, node_id)
    
    def _on_get_selected_node(self, event: Dict[str, Any]) -> None:
        """
        Запрос текущего выбранного узла.
        Ответ отправляется через sys.current_selection.
        """
        # Этот метод будет вызван, когда кто-то запросит текущий узел
        # В реальности мы не храним состояние выбора в контроллере,
        # поэтому просто игнорируем - ответ должен дать тот, у кого есть состояние
        self._logger.debug("Получен запрос выбранного узла, игнорируется")
    
    def get_selected_node_context(self, node_type: NodeType, node_id: int) -> Dict[str, Any]:
        """
        Собирает контекст для узла (имена родителей).
        Полезно для панели деталей.
        
        Args:
            node_type: Тип узла
            node_id: ID узла
            
        Returns:
            Dict с ключами: complex_name, building_name, floor_num
        """
        context = {
            'complex_name': None,
            'building_name': None,
            'floor_num': None
        }
        
        # Собираем предков
        ancestors = self._graph.get_ancestors(node_type, node_id)
        
        for anc_type, anc_id in ancestors:
            entity = self._graph.get(anc_type, anc_id)
            if not entity:
                continue
            
            if anc_type == COMPLEX:
                context['complex_name'] = entity.name
            elif anc_type == BUILDING:
                context['building_name'] = entity.name
            elif anc_type == FLOOR:
                context['floor_num'] = entity.number
        
        self._logger.debug(f"Контекст для {node_type}#{node_id}: {context}")
        return context