# client/src/controllers/details_controller.py
"""
DetailsController — управление панелью детальной информации.

Ответственность:
- Координация отображения панели деталей при выборе узла
- Эмиссия события ShowDetailsPanel для переключения заглушки → панель
- Загрузка данных через DataLoader
- Отправка данных в DetailsPanel через события

Поток данных:
1. Пользователь выбирает узел в дереве
2. TreeView эмитит NodeSelected
3. DetailsController получает NodeSelected
4. Эмитит ShowDetailsPanel (AppWindow → CentralWidget переключает видимость)
5. Загружает данные через DataLoader
6. Отправляет View Models в DetailsPanel через события
"""

from typing import Optional, Any

from src.core import EventBus
from src.core.events import ShowDetailsPanel, NodeSelected, NodeDetailsLoaded
from src.core.types.event_structures import Event
from src.core.types.nodes import NodeIdentifier, NodeType

from src.controllers.base import BaseController
from src.services.data_loader import DataLoader
from src.ui.details.panel import DetailsPanel

from utils.logger import get_logger

log = get_logger(__name__)


class DetailsController(BaseController):
    """
    Контроллер панели деталей.
    
    Управляет:
    - Показом панели деталей при выборе узла (ShowDetailsPanel)
    - Загрузкой данных для выбранного узла
    - Отправкой данных в DetailsPanel через события
    """
    
    def __init__(self, bus: EventBus, loader: DataLoader) -> None:
        """
        Инициализирует контроллер панели деталей.
        
        Args:
            bus: Шина событий
            loader: Загрузчик данных
        """
        log.info("Инициализация DetailsController")
        
        super().__init__(bus)
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

        self._loader = loader
        self._details_panel: Optional[DetailsPanel] = None
        self._current_node: Optional[NodeIdentifier] = None
        
        # Подписка на выбор узла
        self._subscribe(NodeSelected, self._on_node_selected)
        
        log.success("DetailsController инициализирован")
    
    def set_details_panel(self, panel: DetailsPanel) -> None:
        """
        Устанавливает DetailsPanel для управления.
        
        Вызывается из bootstrap после создания AppWindow.
        
        Args:
            panel: Панель детальной информации
        """
        self._details_panel = panel
        log.link("DetailsController: DetailsPanel установлен")
    
    # ===== Обработчики событий =====
    
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        """
        Обрабатывает выбор узла в дереве.
        
        При выборе любого узла:
        1. Запоминаем текущий узел
        2. Эмитим ShowDetailsPanel для переключения заглушки → панель
        3. Загружаем данные узла
        
        Args:
            event: Событие выбора узла
        """
        node = event.data.node
        self._current_node = node
        
        log.info(f"DetailsController: выбран узел {node.node_type.value}#{node.node_id}")
        
        # 1. Эмитим событие показа панели (AppWindow подписан)
        self._bus.emit(ShowDetailsPanel())
        
        # 2. Загружаем данные узла
        self._load_node_details(node)
    
    def _load_node_details(self, node: NodeIdentifier) -> None:
        """
        Загружает детальную информацию о узле.
        
        Алгоритм:
        1. Вызвать loader.load_details()
        2. При успехе — отправить данные в DetailsPanel
        3. При ошибке — показать ошибку
        
        Args:
            node: Идентификатор узла
        """
        log.info(f"DetailsController: загрузка деталей для {node.node_type.value}#{node.node_id}")
        
        try:
            # Загружаем детальные данные
            details = self._loader.load_details(node.node_type, node.node_id)
            
            if details is None:
                log.warning(f"DetailsController: данные для {node.node_type.value}#{node.node_id} не найдены")
                self._show_error(node, "Данные не найдены")
                return
            
            # Успешно загрузили данные
            log.success(f"DetailsController: данные загружены для {node.node_type.value}#{node.node_id}")
            log.debug(f"DetailsController: тип данных = {type(details).__name__}")
            
            # Отправляем данные в DetailsPanel
            self._send_details_to_panel(node, details)
            
        except Exception as e:
            log.error(f"DetailsController: ошибка загрузки {node.node_type.value}#{node.node_id}: {e}")
            self._show_error(node, str(e))
    
    def _send_details_to_panel(self, node: NodeIdentifier, details: Any) -> None:
        """
        Отправляет данные в DetailsPanel через событие.
        
        Args:
            node: Идентификатор узла
            details: Данные узла (модель Complex, Building, Floor или Room)
        """
        # TODO: В будущем здесь будут View Models для вкладок
        # Сейчас отправляем только базовые данные
        
        self._bus.emit(NodeDetailsLoaded(
            node=node,
            payload=details,
            context={}  # пока пустой контекст
        ))
        
        log.debug(f"DetailsController: NodeDetailsLoaded отправлен для {node.node_type.value}#{node.node_id}")
    
    def _show_error(self, node: NodeIdentifier, error_message: str) -> None:
        """
        Показывает ошибку в DetailsPanel.
        
        Args:
            node: Идентификатор узла
            error_message: Текст ошибки
        """
        # TODO: Создать событие ShowError и обработать в DetailsPanel
        log.error(f"DetailsController: ошибка для {node.node_type.value}#{node.node_id}: {error_message}")
    
    # ===== Очистка =====
    
    def cleanup(self) -> None:
        """Очищает ресурсы перед завершением."""
        self._details_panel = None
        self._current_node = None
        super().cleanup()
        log.debug("DetailsController: ресурсы очищены")