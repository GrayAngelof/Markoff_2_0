# client/src/ui/details/__init__.py
"""
Публичное API для панели детальной информации.
Экспортирует только фасад — DetailsPanel.
"""

from src.ui.details.panel import DetailsPanel

__all__ = ["DetailsPanel"]