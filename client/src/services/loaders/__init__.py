# client/src/services/loaders/__init__.py
"""
Пакет загрузчиков данных.

Содержит специализированные загрузчики:
- TreeLoader — загрузка данных для дерева (ленивая загрузка детей)
- PhysicalLoader — загрузка детальной физики объектов
- BusinessLoader — загрузка бизнес-данных (заглушка)
- SafetyLoader — загрузка данных пожарной безопасности (заглушка)

ПРИМЕЧАНИЕ:
    Пакет является приватным — не импортировать напрямую извне.
    Используйте DataLoader (фасад) как единую точку входа.
"""

# ===== ИМПОРТЫ =====
from .base import BaseLoader
from .physical_loader import PhysicalLoader
from .tree_loader import TreeLoader
from .node_loader import NodeLoader
from .dictionary_loader import DictionaryLoader

# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "BaseLoader",
    "PhysicalLoader",
    "TreeLoader",
    "NodeLoader",
    "DictionaryLoader"
]