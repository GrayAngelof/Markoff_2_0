# client/src/controllers/details_controller.py
"""
DetailsController — управление панелью детальной информации.

Ответственность:
- Отслеживание текущего выбранного узла (единственный источник правды)
- Эмиссия события CurrentSelectionChanged для RefreshController
- Загрузка данных через DataLoader
- Преобразование DTO в ViewModel через DetailsProjection
- Отправка ViewModel в UI через событие NodeDetailsLoaded

НЕ отвечает за:
- Показ панели деталей (это DetailsUiHandler)
- Раскрытие/сворачивание узлов (это TreeController)
- Прямую работу с UI (DetailsPanel)

Поток данных:
1. Пользователь выбирает узел в дереве
2. TreeView эмитит NodeSelected
3. DetailsController получает NodeSelected
4. Обновляет _current_selection и эмитит CurrentSelectionChanged (если изменился)
5. Загружает данные через DataLoader
6. Преобразует DTO → DetailsViewModel через DetailsProjection
7. Отправляет ViewModel через NodeDetailsLoaded в DetailsUiHandler
"""

# ===== ИМПОРТЫ =====
from typing import Any, Callable, Dict, Optional

from src.core import EventBus
from src.core.events.definitions import (
    CurrentSelectionChanged,
    NodeDetailsLoaded,
    NodeSelected,
)
from src.core.types.nodes import NodeIdentifier, NodeType
from src.projections.details_projection import DetailsProjection
from src.services.data_loader import DataLoader
from src.view_models.details import DetailsViewModel
from utils.logger import get_logger

from .base import BaseController


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsController(BaseController):
    """
    Контроллер панели деталей.

    Отвечает за:
    - Отслеживание текущего выбранного узла
    - Эмиссию CurrentSelectionChanged для RefreshController
    - Загрузку данных через DataLoader
    - Преобразование DTO → ViewModel через DetailsProjection
    - Отправку ViewModel в UI
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        bus: EventBus,
        loader: DataLoader,
        projection: DetailsProjection,
    ) -> None:
        """Инициализирует контроллер панели деталей."""
        log.system("DetailsController инициализация")
        super().__init__(bus)

        self._loader = loader
        self._projection = projection
        self._current_selection: Optional[NodeIdentifier] = None

        # Регистрация загрузчиков DTO по типу узла
        self._dto_loaders: Dict[NodeType, Callable[[int], Optional[Any]]] = {
            NodeType.COMPLEX: self._loader.load_complex_detail,
            NodeType.BUILDING: self._loader.load_building_detail,
            NodeType.FLOOR: self._loader.load_floor_detail,
            NodeType.ROOM: self._loader.load_room_detail,
        }

        # Регистрация билдеров ViewModel по типу узла
        self._vm_builders: Dict[NodeType, Callable[[Any], DetailsViewModel]] = {
            NodeType.COMPLEX: self._projection.build_complex_details,
            NodeType.BUILDING: self._projection.build_building_details,
            NodeType.FLOOR: self._projection.build_floor_details,
            NodeType.ROOM: self._projection.build_room_details,
        }

        self._subscribe(NodeSelected, self._on_node_selected)

        log.system("DetailsController инициализирован")

    def cleanup(self) -> None:
        """Очищает ресурсы перед завершением."""
        self._current_selection = None
        self._dto_loaders.clear()
        self._vm_builders.clear()
        super().cleanup()
        log.debug("DetailsController: ресурсы очищены")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_node_selected(self, event: NodeSelected) -> None:
        """
        Обрабатывает выбор узла в дереве.

        - Обновляет текущий выбранный узел
        - Эмитит CurrentSelectionChanged (для RefreshController)
        - Загружает детали и преобразует в ViewModel
        """
        node = event.node
        log.info(f"Выбран узел {node.node_type.value}#{node.node_id}")

        old_selection = self._current_selection
        self._current_selection = node

        if old_selection != node:
            self._emit_current_selection_changed()

        self._load_and_emit_view_model(node)

    # ---- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ----
    def _emit_current_selection_changed(self) -> None:
        """Эмитит событие об изменении текущего выбранного узла."""
        self._bus.emit(CurrentSelectionChanged(selection=self._current_selection))
        log.debug(f"Эмиттирован CurrentSelectionChanged: {self._current_selection}")

    def _load_and_emit_view_model(self, node: NodeIdentifier) -> None:
        """
        Загружает детали, преобразует в ViewModel и отправляет в UI.
        """
        log.debug(f"Загрузка деталей для {node.node_type.value}#{node.node_id}")

        try:
            dto = self._load_dto_by_type(node)

            if dto is None:
                log.warning(f"Данные для {node.node_type.value}#{node.node_id} не найдены")
                return

            vm = self._build_view_model(node, dto)
            self._emit_view_model(node, vm)

        except Exception as e:
            log.error(f"Ошибка загрузки {node.node_type.value}#{node.node_id}: {e}")

    def _load_dto_by_type(self, node: NodeIdentifier) -> Optional[Any]:
        """Загружает DTO через зарегистрированный загрузчик."""
        loader = self._dto_loaders.get(node.node_type)
        if loader is None:
            log.warning(f"Нет загрузчика для типа узла: {node.node_type}")
            return None
        return loader(node.node_id)

    def _build_view_model(self, node: NodeIdentifier, dto: Any) -> DetailsViewModel:
        """Преобразует DTO в DetailsViewModel через зарегистрированный билдер."""
        builder = self._vm_builders.get(node.node_type)
        if builder is None:
            raise ValueError(f"Нет билдера для типа узла: {node.node_type}")
        return builder(dto)

    def _emit_view_model(self, node: NodeIdentifier, vm: DetailsViewModel) -> None:
        """Отправляет ViewModel в UI через событие NodeDetailsLoaded."""
        self._bus.emit(NodeDetailsLoaded(
            node=node,
            view_model=vm,
        ))
        log.debug(f"NodeDetailsLoaded отправлен для {node.node_type.value}#{node.node_id}")