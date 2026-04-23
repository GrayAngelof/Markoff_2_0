# client/src/controllers/details_controller.py
"""
DetailsController — управление панелью детальной информации.

Ответственность:
- Отслеживание текущего выбранного узла (единственный источник правды)
- Эмиссия события CurrentSelectionChanged для RefreshController
- Загрузка данных через DataLoader
- Отправка данных в DetailsPanel через событие NodeDetailsLoaded

НЕ отвечает за:
- Показ панели деталей (это ответственность DetailsUiHandler)
- Раскрытие/сворачивание узлов (это TreeController)
- Прямую работу с UI (DetailsPanel)

Поток данных:
1. Пользователь выбирает узел в дереве
2. TreeView эмитит NodeSelected
3. DetailsController получает NodeSelected
4. Обновляет _current_selection и эмитит CurrentSelectionChanged (если изменился)
5. Загружает данные через DataLoader
6. Отправляет данные через NodeDetailsLoaded в DetailsUiHandler
7. DetailsUiHandler сам решает, когда показать панель
"""

# ===== ИМПОРТЫ =====
from typing import Any, Optional

from src.core import EventBus
from src.core.events.definitions import (
    CurrentSelectionChanged,
    NodeDetailsLoaded,
    NodeSelected,
)
from src.core.types.nodes import NodeIdentifier, NodeType
from .base import BaseController
from src.services.data_loader import DataLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsController(BaseController):
    """
    Контроллер панели деталей.

    Отвечает за:
    - Отслеживание текущего выбранного узла (единственный источник правды)
    - Эмиссию CurrentSelectionChanged для RefreshController
    - Загрузку данных через DataLoader
    - Отправку данных в DetailsPanel через события

    НЕ отвечает за:
    - Показ панели деталей (это DetailsUiHandler)
    - Раскрытие/сворачивание узлов (это TreeController)
    - Прямую работу с UI (DetailsPanel)
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, loader: DataLoader) -> None:
        """Инициализирует контроллер панели деталей."""
        log.system("DetailsController инициализация")
        super().__init__(bus)

        self._loader = loader
        self._current_selection: Optional[NodeIdentifier] = None

        self._subscribe(NodeSelected, self._on_node_selected)

        log.system("DetailsController инициализирован")

    def cleanup(self) -> None:
        """Очищает ресурсы перед завершением."""
        self._current_selection = None
        super().cleanup()
        log.debug("DetailsController: ресурсы очищены")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_node_selected(self, event: NodeSelected) -> None:
        """
        Обрабатывает выбор узла в дереве.

        - Обновляет текущий выбранный узел
        - Эмитит CurrentSelectionChanged (для RefreshController)
        - Инициирует загрузку деталей
        """
        node = event.node
        log.info(f"Выбран узел {node.node_type.value}#{node.node_id}")

        # Обновление состояния и эмиссия изменения выбора
        old_selection = self._current_selection
        self._current_selection = node

        if old_selection != node:
            self._emit_current_selection_changed()

        # Загружаем детали узла (панель покажет DetailsUiHandler)
        self._load_node_details(node)

    # ---- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ЭМИССИИ СОСТОЯНИЯ ----
    def _emit_current_selection_changed(self) -> None:
        """Эмитит событие об изменении текущего выбранного узла."""
        self._bus.emit(CurrentSelectionChanged(selection=self._current_selection))
        log.debug(f"Эмиттирован CurrentSelectionChanged: {self._current_selection}")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ЗАГРУЗКИ ДАННЫХ ----
    def _load_node_details(self, node: NodeIdentifier) -> None:
        """
        Загружает детальную информацию об узле.

        Диспетчеризация по типу узла:
        - COMPLEX → load_complex_detail()
        - BUILDING → load_building_detail()
        - FLOOR → load_floor_detail()
        - ROOM → load_room_detail()
        """
        log.debug(f"Загрузка деталей для {node.node_type.value}#{node.node_id}")

        try:
            details = self._load_by_type(node)

            if details is None:
                log.warning(f"Данные для {node.node_type.value}#{node.node_id} не найдены")
                self._show_error(node, "Данные не найдены")
                return

            log.success(f"Данные загружены для {node.node_type.value}#{node.node_id}")
            self._send_details_to_panel(node, details)

        except Exception as e:
            log.error(f"Ошибка загрузки {node.node_type.value}#{node.node_id}: {e}")
            self._show_error(node, str(e))

    def _load_by_type(self, node: NodeIdentifier) -> Optional[Any]:
        """
        Загружает детали в зависимости от типа узла.

        Returns:
            Соответствующий DetailDTO:
            - ComplexDetailDTO
            - BuildingDetailDTO
            - FloorDetailDTO
            - RoomDetailDTO
        """
        node_type = node.node_type
        node_id = node.node_id

        if node_type == NodeType.COMPLEX:
            return self._loader.load_complex_detail(node_id)
        elif node_type == NodeType.BUILDING:
            return self._loader.load_building_detail(node_id)
        elif node_type == NodeType.FLOOR:
            return self._loader.load_floor_detail(node_id)
        elif node_type == NodeType.ROOM:
            return self._loader.load_room_detail(node_id)
        else:
            log.warning(f"Неизвестный тип узла для загрузки деталей: {node_type}")
            return None

    def _send_details_to_panel(self, node: NodeIdentifier, details: Any) -> None:
        """Отправляет данные в DetailsPanel через событие NodeDetailsLoaded."""
        self._bus.emit(NodeDetailsLoaded(
            node=node,
            payload=details,
            context={},  # TODO: заполнить имена родителей через ContextService
        ))
        log.debug(f"NodeDetailsLoaded отправлен для {node.node_type.value}#{node.node_id}")

    def _show_error(self, node: NodeIdentifier, error_message: str) -> None:
        """Показывает ошибку в DetailsPanel."""
        # TODO: Создать событие ShowError и обработать в DetailsPanel
        log.error(f"Ошибка для {node.node_type.value}#{node.node_id}: {error_message}")