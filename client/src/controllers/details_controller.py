# client/src/controllers/details_controller.py
"""
Контроллер панели детальной информации.
Решает, что показывать при загрузке данных и переключении вкладок.
"""
from typing import Dict, Any, Optional

from src.core.event_bus import EventBus
from src.core.events import SystemEvents, UIEvents
from src.data.entity_types import NodeType
from src.controllers.base import BaseController
from src.services.data_loader import DataLoader

from utils.logger import get_logger


class DetailsController(BaseController):
    """
    Контроллер панели деталей.
    
    Логика:
    - При загрузке детальных данных → отправить в панель
    - При переключении вкладки → загрузить данные для вкладки (в будущем)
    - При ошибке загрузки → показать сообщение
    """
    
    def __init__(self, event_bus: EventBus, loader: DataLoader):
        """
        Инициализирует контроллер панели деталей.
        
        Args:
            event_bus: Шина событий
            loader: Загрузчик данных (для будущих запросов)
        """
        super().__init__(event_bus)
        
        self._loader = loader
        self._current_node: Optional[tuple] = None  # (type, id)
        
        # Подписки
        self._subscribe(SystemEvents.DATA_LOADED, self._on_data_loaded)
        self._subscribe(SystemEvents.DATA_ERROR, self._on_data_error)
        self._subscribe(UIEvents.TAB_CHANGED, self._on_tab_changed)
        self._subscribe(UIEvents.NODE_SELECTED, self._on_node_selected)
        
        self._logger.info("DetailsController инициализирован")
    
    def _on_node_selected(self, event: Dict[str, Any]) -> None:
        """
        Запоминаем текущий выбранный узел.
        
        Event data: {
            'node_type': NodeType,
            'node_id': int,
            'data': object
        }
        """
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        
        self._current_node = (node_type, node_id)
        self._logger.debug(f"Текущий узел: {node_type}#{node_id}")
    
    def _on_data_loaded(self, event: Dict[str, Any]) -> None:
        """
        Данные загружены - отправляем в панель, если это детали текущего узла.
        
        Event data: {
            'node_type': NodeType,
            'node_id': int,
            'data': object,
            'is_detail': bool (optional)
        }
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
        
        # Здесь можно добавить логику форматирования или преобразования
        # Но основная работа будет в самой DetailsPanel через подписку
        
        # Можно также загрузить дополнительные данные для вкладок
        # Например, если текущая вкладка - "Пожарка", загрузить данные пожарной безопасности
    
    def _on_data_error(self, event: Dict[str, Any]) -> None:
        """
        Ошибка загрузки - показываем в панели.
        
        Event data: {
            'node_type': NodeType,
            'node_id': int,
            'error': str
        }
        """
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        error = event['data']['error']
        
        # Проверяем, что это для текущего узла
        if self._current_node != (node_type, node_id):
            return
        
        self._logger.error(f"Ошибка загрузки для {node_type}#{node_id}: {error}")
        
        # Генерируем событие для отображения ошибки в панели
        self._bus.emit('ui.show_error', {
            'title': 'Ошибка загрузки',
            'message': f'Не удалось загрузить данные: {error}'
        }, source='details_controller')
    
    def _on_tab_changed(self, event: Dict[str, Any]) -> None:
        """
        Пользователь переключил вкладку.
        
        Event data: {
            'tab_index': int
        }
        """
        tab_index = event['data']['tab_index']
        
        self._logger.debug(f"Переключена вкладка {tab_index}")
        
        # Здесь можно загрузить данные для соответствующей вкладки
        if self._current_node:
            node_type, node_id = self._current_node
            
            # Например, для вкладки "Пожарка" загрузить данные пожарной безопасности
            # if tab_index == 2:  # Пожарка
            #     self._loader.load_fire_safety_data(node_type, node_id)