# client/src/controllers/details_controller.py
"""
DetailsController — управление панелью детальной информации.

Тонкий контроллер — только вызывает сервисы, не принимает решений.
"""

from typing import Optional, cast
from src.core import EventBus
from src.core.types import Event, NodeIdentifier, NodeType
from src.core.events import (
    NodeSelected, TabChanged, BuildingDetailsLoaded,
    DataError, NodeDetailsLoaded
)
from src.core.types.exceptions import NotFoundError
from src.services import DataLoader
from src.services.types import BuildingWithOwnerResult
from src.controllers.base import BaseController
from utils.logger import get_logger

log = get_logger(__name__)


class DetailsController(BaseController):
    """
    Контроллер панели деталей.
    
    Отвечает за:
    - Запоминание текущего узла
    - Загрузку связанных данных (владельцы, контакты)
    - Реакцию на переключение вкладок
    """
    
    def __init__(
        self,
        bus: EventBus,
        loader: DataLoader
    ):
        """
        Инициализирует контроллер панели деталей.
        
        Args:
            bus: Шина событий
            loader: Загрузчик данных
        """
        super().__init__(bus)
        self._loader = loader
        self._current_node: Optional[NodeIdentifier] = None
        self._app_window = None
        
        # Сохраняем bound methods как атрибуты (сильные ссылки)
        self._bound_on_node_selected = self._on_node_selected
        self._bound_on_tab_changed = self._on_tab_changed
        
        # Подписки
        self._subscribe(NodeSelected, self._bound_on_node_selected)
        self._subscribe(TabChanged, self._bound_on_tab_changed)
        
        log.system("DetailsController инициализирован")
    
    def set_app_window(self, app_window):
        """Устанавливает ссылку на фасад окна (для подмены панелей)."""
        self._app_window = app_window
        log.link(f"AppWindow установлен для DetailsController")
    
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        """
        Обрабатывает выбор узла.
        
        1. Запоминает текущий узел
        2. Если это корпус — загружает владельца и контакты
        
        Args:
            event: Событие выбора узла
        """
        node = event.data.node
        node_display = f"{node.node_type.value}#{node.node_id}"
        
        log.info(f"Выбран узел для деталей: {node_display}")
        
        self._current_node = node
        
        # Для корпусов загружаем владельца и контакты
        if node.node_type == NodeType.BUILDING:
            self._load_building_details(node.node_id)
    
    def _on_tab_changed(self, event: Event[TabChanged]) -> None:
        """
        Обрабатывает переключение вкладки.
        
        При переключении на вкладку контактов (индекс 1)
        загружаем данные, если их ещё нет.
        
        Args:
            event: Событие переключения вкладки
        """
        tab_index = event.data.tab_index
        log.debug(f"Переключение на вкладку {tab_index}")
        
        # Вкладка контактов (индекс 1)
        if tab_index == 1 and self._current_node:
            if self._current_node.node_type == NodeType.BUILDING:
                log.data(f"Загрузка контактов для корпуса #{self._current_node.node_id}")
                self._load_building_details(self._current_node.node_id)
    
    def _load_building_details(self, building_id: int) -> None:
        """
        Загружает детали корпуса с владельцем и контактами.
        
        DataLoader сам решает, что загружать и проверяет кэш.
        
        Args:
            building_id: ID корпуса
        """
        log.api(f"Загрузка деталей корпуса #{building_id}")
        
        try:
            result = self._loader.load_building_with_owner(building_id)
            
            if result:
                building = result.building
                owner = result.owner
                responsible_persons = result.responsible_persons
                
                log.data(
                    f"Детали корпуса #{building_id} загружены: "
                    f"владелец={owner is not None}, "
                    f"контактов={len(responsible_persons)}"
                )
                
                self._bus.emit(BuildingDetailsLoaded(
                    building=building,
                    owner=owner,
                    responsible_persons=responsible_persons or []
                ))
            else:
                log.warning(f"Корпус #{building_id} не найден")
                if self._current_node:
                    self._emit_error(
                        self._current_node,
                        NotFoundError(f"Building {building_id} not found")
                    )
                    
        except Exception as e:
            log.error(f"Ошибка загрузки деталей корпуса #{building_id}: {e}")
            if self._current_node:
                self._emit_error(self._current_node, e)
    
    # ===== Публичные методы =====
    
    def get_current_node(self) -> Optional[NodeIdentifier]:
        """
        Возвращает текущий выбранный узел.
        
        Returns:
            Optional[NodeIdentifier]: Текущий узел или None
        """
        return self._current_node