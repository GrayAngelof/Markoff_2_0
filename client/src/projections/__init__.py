# client/src/projections/__init__.py
"""
Проекции — слой преобразования данных для UI.

Проекции преобразуют "сырые" DTO из data слоя в структуры,
удобные для отображения в UI:
- TreeProjection — строит иерархическое дерево TreeNode из репозиториев
- TreeNode — узел дерева с методами навигации (родитель, дети, поиск)
- DetailsProjection — собирает DetailsViewModel из DTO и справочников

ЕДИНСТВЕННЫЙ способ импорта проекций:
    from src.projections import TreeProjection, TreeNode, DetailsProjection

ПРИМЕЧАНИЕ:
    Проекции не содержат бизнес-логики, только преобразование данных.
    Не предназначены для прямого вызова из UI — используйте контроллеры.
"""

# ===== ИМПОРТЫ =====
from .details_projection import DetailsProjection
from .tree import TreeProjection
from .tree_node import TreeNode


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Преобразование дерева (репозитории → TreeNode)
    "TreeProjection",
    
    # Узел дерева (навигация, хранение данных)
    "TreeNode",
    
    # Преобразование деталей (DTO + справочники → DetailsViewModel)
    "DetailsProjection",
]