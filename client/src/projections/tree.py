# client/src/projections/tree.py
"""
Проекция дерева — преобразует данные в иерархическую структуру TreeNode.

Отвечает только за:
- get_root_nodes() — корневые узлы (комплексы)
- build_children_from_payload() — создание TreeNode из загруженных данных

НЕ отвечает за:
- Загрузку данных (это DataLoader)
- Поиск детей в репозиториях (это делает DataLoader)
"""

# ===== ИМПОРТЫ =====
from typing import Any, List, Optional

from src.core.types import NodeType
from src.data.repositories import (
    BuildingRepository,
    ComplexRepository,
    FloorRepository,
    RoomRepository,
)
from src.ui.tree.node import TreeNode
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class TreeProjection:
    """
    Проекция дерева. Строит иерархическую структуру TreeNode.

    Преобразует данные из репозиториев в узлы дерева для отображения.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        complex_repo: ComplexRepository,
        building_repo: BuildingRepository,
        floor_repo: FloorRepository,
        room_repo: RoomRepository,
    ) -> None:
        """Инициализирует проекцию дерева."""
        log.info("Инициализация TreeProjection")
        self._complex_repo = complex_repo
        self._building_repo = building_repo
        self._floor_repo = floor_repo
        self._room_repo = room_repo
        log.system("TreeProjection инициализирована")

    # ---- ПУБЛИЧНОЕ API ----
    def get_root_nodes(self) -> List[TreeNode]:
        """Возвращает корневые узлы (комплексы) для первоначального отображения."""
        log.info("Загрузка корневых узлов")

        complexes = self._complex_repo.get_all()
        log.debug(f"get_root_nodes: Найдено комплексов: {len(complexes)}")

        root_nodes = []
        for complex_data in complexes:
            display_name = self._get_display_name(
                node_type=NodeType.COMPLEX,
                data=complex_data,
                base_attr='name',
                has_children=complex_data.buildings_count > 0,
                count_attr='buildings_count',
            )

            node = TreeNode(
                data=complex_data,
                node_type=NodeType.COMPLEX,
                display_name=display_name,
                has_children=complex_data.buildings_count > 0,
            )
            root_nodes.append(node)

        log.info(f"Построено корневых узлов: {len(root_nodes)}")
        return root_nodes

    def build_children_from_payload(
        self,
        payload: List[Any],
        child_type: NodeType,
        parent_node: TreeNode,
    ) -> List[TreeNode]:
        """
        Создаёт TreeNode из загруженных данных детей.

        Единственное место, где создаются узлы дерева.
        """
        log.debug(f"build_children_from_payload: Создание {len(payload)} узлов типа {child_type.value}")

        nodes = []
        for child_data in payload:
            has_children = False
            if child_type == NodeType.BUILDING:
                has_children = getattr(child_data, 'floors_count', 0) > 0
            elif child_type == NodeType.FLOOR:
                has_children = getattr(child_data, 'rooms_count', 0) > 0

            display_name = self._get_display_name(
                node_type=child_type,
                data=child_data,
                base_attr='name' if child_type == NodeType.BUILDING else 'number',
                has_children=has_children,
                count_attr='floors_count' if child_type == NodeType.BUILDING else 'rooms_count',
            )

            node = TreeNode(
                data=child_data,
                node_type=child_type,
                display_name=display_name,
                has_children=has_children,
                parent=parent_node,
            )
            nodes.append(node)

        nodes.sort(key=lambda node: node.name.lower())
        log.debug(f"build_children_from_payload: Создано {len(nodes)} узлов, отсортировано")
        return nodes

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _get_display_name(
        self,
        node_type: NodeType,
        data: Any,
        base_attr: str,
        has_children: bool,
        count_attr: Optional[str] = None,
    ) -> str:
        """Формирует отображаемое имя узла."""
        base_name = getattr(data, base_attr, str(data))

        if node_type == NodeType.FLOOR:
            base_name = self._format_floor_number(base_name)

        if has_children and count_attr:
            count = getattr(data, count_attr, 0)
            return f"{base_name} ({count})"

        return str(base_name)

    @staticmethod
    def _format_floor_number(number: Any) -> str:
        """Форматирует номер этажа в читаемый текст."""
        try:
            num = int(number)
            if num < 0:
                return f"Подвал {abs(num)}"
            if num == 0:
                return "Цокольный этаж"
            return f"Этаж {num}"
        except (ValueError, TypeError):
            return str(number)