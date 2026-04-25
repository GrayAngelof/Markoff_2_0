# client/src/ui/handlers/tree_handler.py
"""
Обработчик событий дерева (UI слой).

Подписывается на ChildrenLoaded и обновляет TreeModel.
Единственное место в UI, которое знает о структуре дерева (root vs children).
"""

# ===== ИМПОРТЫ =====
from src.core.event_bus import EventBus
from src.core.events.definitions import ChildrenLoaded
from src.core.types import ROOT_NODE
from src.ui.tree.model import TreeModel
from src.ui.tree.view import TreeView
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class TreeUiHandler:
    """
    Обработчик событий дерева.

    Отвечает за:
    - Подписку на ChildrenLoaded
    - Обновление TreeModel (корневые узлы или вставка детей)
    - Никакой бизнес-логики, только UI-координация

    Принцип работы:
    - При event.parent == ROOT_NODE → полная замена корневых узлов
    - Иначе → поиск родителя в модели и вставка детей
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, tree_view: TreeView) -> None:
        """Инициализирует обработчик."""
        log.system("TreeUiHandler инициализация")
        self._bus = bus
        self._tree_view = tree_view
        self._model = TreeModel()
        self._subscriptions = []
        log.system("TreeUiHandler инициализирован")

    def start(self) -> None:
        """Настраивает виджет и подписывается на события."""
        log.info("Запуск TreeUiHandler")

        self._tree_view.setModel(self._model)
        self._tree_view.set_event_bus(self._bus)

        sub = self._bus.subscribe(ChildrenLoaded, self._on_children_loaded)
        self._subscriptions.append(sub)

        log.success("TreeUiHandler запущен")

    def cleanup(self) -> None:
        """Отписывается от событий и очищает ресурсы."""
        log.info("Очистка TreeUiHandler")

        for sub in self._subscriptions:
            sub()
        self._subscriptions.clear()

        log.success("TreeUiHandler очищен")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_children_loaded(self, event: ChildrenLoaded) -> None:
        """
        Обрабатывает событие загрузки детей.

        При event.parent == ROOT_NODE — заменяет корневые узлы.
        Иначе — ищет родителя и вставляет детей.
        """
        if event.parent == ROOT_NODE:
            log.debug(f"Получены корневые узлы: {len(event.children)}")
            self._model.set_root_nodes(event.children)
            return

        parent_node = self._model.get_node_by_id(
            event.parent.node_type,
            event.parent.node_id
        )

        if parent_node is None:
            log.warning(
                f"Родительский узел {event.parent.node_type.value}#{event.parent.node_id} "
                "не найден в модели, пропускаем вставку"
            )
            return

        log.debug(f"Вставка {len(event.children)} детей в узел {parent_node.type}#{parent_node.id}")
        self._model.insert_children(parent_node, event.children)