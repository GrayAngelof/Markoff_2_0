# client/src/projections/tree_node.py
"""
Узел дерева для отображения.

Единообразная структура для всех уровней иерархии.
Содержит данные, ссылки на родителя и детей, методы навигации.
"""

# ===== ИМПОРТЫ =====
from typing import Any, List, Optional

from src.core.types import NodeIdentifier, NodeType
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class TreeNode:
    """
    Узел дерева.

    Единообразная структура для всех уровней:
    - id: уникальный ID узла
    - type: тип узла ("complex", "building", "floor", "room")
    - name: отображаемое имя
    - has_children: есть ли дети (для стрелочки)

    Также хранит:
    - data: исходные данные (модель)
    - parent: ссылка на родительский узел
    - children: список дочерних узлов
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        data: Any,
        node_type: NodeType,
        display_name: str,
        has_children: bool = False,
        parent: Optional['TreeNode'] = None,
    ) -> None:
        """Инициализирует узел дерева."""
        self._data = data
        self._node_type = node_type
        self._display_name = display_name
        self._has_children = has_children
        self._parent = parent
        self._children: List['TreeNode'] = []

    # ---- ПУБЛИЧНЫЕ СВОЙСТВА (для TreeModel) ----
    @property
    def id(self) -> int:
        """Уникальный ID узла."""
        if self._data and hasattr(self._data, 'id'):
            return self._data.id
        return -1

    @property
    def type(self) -> str:
        """Тип узла."""
        return self._node_type.value

    @property
    def name(self) -> str:
        """Отображаемое имя."""
        return self._display_name

    @property
    def has_children(self) -> bool:
        """Есть ли дети (для стрелочки)."""
        return self._has_children or len(self._children) > 0

    # ---- ВНУТРЕННИЕ СВОЙСТВА (для построения дерева) ----
    @property
    def data(self) -> Any:
        """Исходные данные."""
        return self._data

    @property
    def node_type(self) -> NodeType:
        """Тип узла (для внутреннего использования)."""
        return self._node_type

    @property
    def parent(self) -> Optional['TreeNode']:
        """Родительский узел."""
        return self._parent

    @property
    def children(self) -> List['TreeNode']:
        """Список дочерних узлов (копия)."""
        return self._children.copy()

    # ---- УПРАВЛЕНИЕ ДЕТЬМИ ----
    def append_child(self, child: 'TreeNode') -> None:
        """Добавляет одного дочернего узла."""
        self._children.append(child)
        log.debug(f"Узел {self.type}#{self.id} добавил ребенка {child.type}#{child.id}")

    def add_children(self, children: List['TreeNode']) -> None:
        """Добавляет несколько дочерних узлов."""
        if not children:
            return

        self._children.extend(children)
        log.debug(f"Узел {self.type}#{self.id} добавил {len(children)} детей")

    def remove_child(self, child: 'TreeNode') -> bool:
        """
        Удаляет дочерний узел.

        Returns:
            True если узел был удалён
        """
        if child in self._children:
            self._children.remove(child)
            log.debug(f"Узел {self.type}#{self.id} удалил ребенка {child.type}#{child.id}")
            return True
        return False

    def remove_all_children(self) -> None:
        """Удаляет всех детей."""
        count = len(self._children)
        if count > 0:
            self._children.clear()
            log.debug(f"Узел {self.type}#{self.id} удалил всех {count} детей")

    def child_at(self, row: int) -> Optional['TreeNode']:
        """Возвращает ребёнка по индексу."""
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def child_count(self) -> int:
        """Возвращает количество детей."""
        return len(self._children)

    def row(self) -> int:
        """Возвращает индекс узла в родителе."""
        if self._parent:
            try:
                return self._parent._children.index(self)
            except ValueError:
                log.warning(f"Узел {self.type}#{self.id} не найден в родителе")
                return 0
        return 0

    # ---- ИДЕНТИФИКАЦИЯ ----
    def get_id(self) -> int:
        """Возвращает ID узла."""
        return self.id

    def get_identifier(self) -> NodeIdentifier:
        """Возвращает NodeIdentifier для событий."""
        return NodeIdentifier(self._node_type, self.get_id())

    # ---- ПОИСК ----
    def find_child_by_id(self, node_type: NodeType, node_id: int) -> Optional['TreeNode']:
        """Рекурсивно ищет дочерний узел по типу и ID."""
        if self.node_type == node_type and self.get_id() == node_id:
            return self

        for child in self._children:
            result = child.find_child_by_id(node_type, node_id)
            if result:
                return result

        return None

    # ---- СТРОКОВОЕ ПРЕДСТАВЛЕНИЕ ----
    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"TreeNode({self.type}, id={self.id}, name={self.name}, children={len(self._children)})"

    def __str__(self) -> str:
        """Строковое представление для отображения."""
        return self.name