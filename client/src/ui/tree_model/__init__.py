# client/src/ui/tree_model/__init__.py
"""
Пакет модели дерева для отображения иерархии объектов.
Предоставляет компоненты для создания и управления древовидными данными.

Основные компоненты:
- NodeType: Перечисление типов узлов
- TreeNode: Класс узла дерева
- TreeModel: Полноценная модель для QTreeView

Пример использования:
    model = TreeModel()
    model.set_cache(cache)
    model.set_complexes(complexes)
    tree_view.setModel(model)
"""
from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.ui.tree_model.tree_model import TreeModel

__all__ = [
    "NodeType",
    "TreeNode", 
    "TreeModel"
]