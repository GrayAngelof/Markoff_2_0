# client/src/controllers/details_controller.py
"""
Контроллер панели детальной информации.
Обновлён для отображения информации о владельцах и контактных лицах.
"""
from typing import Dict, Any, Optional

from src.core.event_bus import EventBus
from src.core.events import SystemEvents, UIEvents
from src.data.entity_types import NodeType
from src.controllers.base import BaseController
from src.services.data_load import DataLoader
from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson

from utils.logger import get_logger


class DetailsController(BaseController):
    """
    Контроллер панели деталей.
    
    Логика:
    - При загрузке детальных данных → отправить в панель
    - При загрузке владельца → обновить информацию о корпусе
    - При переключении вкладки → загрузить данные для вкладки
    """
    
    def __init__(self, event_bus: EventBus, loader: DataLoader):
        """
        Инициализирует контроллер панели деталей.
        
        Args:
            event_bus: Шина событий
            loader: Загрузчик данных
        """
        super().__init__(event_bus)
        
        self._loader = loader
        self._current_node: Optional[tuple] = None  # (type, id)
        self._current_context: Optional[Dict] = None
        
        # Подписки
        self._subscribe(SystemEvents.DATA_LOADED, self._on_data_loaded)
        self._subscribe(SystemEvents.DATA_ERROR, self._on_data_error)
        self._subscribe(UIEvents.TAB_CHANGED, self._on_tab_changed)
        self._subscribe(UIEvents.NODE_SELECTED, self._on_node_selected)
        self._subscribe('ui.building_owner_loaded', self._on_building_owner_loaded)
        
        self._logger.info("DetailsController инициализирован (с поддержкой владельцев)")
    
    def _on_node_selected(self, event: Dict[str, Any]) -> None:
        """Запоминаем текущий выбранный узел и его контекст."""
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        context = event['data'].get('context', {})
        
        self._current_node = (node_type, node_id)
        self._current_context = context
        
        self._logger.debug(f"Текущий узел: {node_type}#{node_id}")
    
    def _on_building_owner_loaded(self, event: Dict[str, Any]) -> None:
        """
        Загружена информация о владельце корпуса.
        Обновляем панель деталей, если это текущий корпус.
        """
        building_id = event['data']['building_id']
        owner_data = event['data'].get('owner')
        context = event['data'].get('context', {})
        
        # Проверяем, что это текущий корпус
        if self._current_node != (NodeType.BUILDING, building_id):
            return
        
        if not owner_data:
            return
        
        self._logger.info(f"Получены данные о владельце для корпуса {building_id}")
        
        # Загружаем ответственных лиц
        persons = self._loader._loader._load_responsible_persons(owner_data.id)
        
        # Отправляем в панель деталей
        self._bus.emit('ui.update_building_details', {
            'building_id': building_id,
            'owner': owner_data,
            'responsible_persons': persons,
            'context': context
        }, source='details_controller')
    
    def _on_data_loaded(self, event: Dict[str, Any]) -> None:
        """
        Данные загружены - отправляем в панель, если это детали текущего узла.
        """
        data = event['data']
        
        # Проверяем, что это детальные данные
        if not data.get('is_detail', False):
            return
        
        node_type = data['node_type']
        node_id = data['node_id']
        
        # Проверяем, что это текущий узел
        if self._current_node != (node_type, node_id):
            self._logger.debug(f"Данные для {node_type}#{node_id} не для текущего узла")
            return
        
        entity = data['data']
        
        self._logger.info(f"Обновление панели деталей для {node_type}#{node_id}")
        
        # Для корпусов загружаем информацию о владельце, если её ещё нет
        if node_type == NodeType.BUILDING and hasattr(entity, 'owner_id') and entity.owner_id:
            self._loader.get_owner_for_building(entity)
        
        # Для комнат загружаем информацию об арендаторе (в будущем)
        # if node_type == NodeType.ROOM and entity.status_code == 'occupied':
        #     self._loader.load_tenant_info(entity.id)
    
    def _on_data_error(self, event: Dict[str, Any]) -> None:
        """Ошибка загрузки - показываем в панели."""
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        error = event['data']['error']
        
        # Проверяем, что это для текущего узла
        if self._current_node != (node_type, node_id):
            return
        
        self._logger.error(f"Ошибка загрузки для {node_type}#{node_id}: {error}")
        
        self._bus.emit('ui.show_error', {
            'title': 'Ошибка загрузки',
            'message': f'Не удалось загрузить данные: {error}'
        }, source='details_controller')
    
    def _on_tab_changed(self, event: Dict[str, Any]) -> None:
        """Пользователь переключил вкладку."""
        tab_index = event['data']['tab_index']
        
        self._logger.debug(f"Переключена вкладка {tab_index}")
        
        # Здесь можно загрузить данные для соответствующей вкладки
        if self._current_node:
            node_type, node_id = self._current_node
            
            # Для вкладки "Контакты" показываем ответственных лиц
            if tab_index == 1 and node_type == NodeType.BUILDING:  # Юрики/Контакты
                building = self._loader._graph.get(node_type, node_id)
                if building and hasattr(building, 'owner_id') and building.owner_id:
                    persons = self._loader._loader._load_responsible_persons(building.owner_id)
                    self._bus.emit('ui.show_contacts', {
                        'persons': persons
                    }, source='details_controller')