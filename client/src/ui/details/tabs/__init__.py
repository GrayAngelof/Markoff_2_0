# client/src/ui/details/tabs/__init__.py
"""
Пакет вкладок панели детальной информации.
Экспортирует все вкладки для использования в DetailsTabs.
"""

from src.ui.details.tabs.physics import PhysicsTab
from src.ui.details.tabs.legal import LegalTab
from src.ui.details.tabs.safety import SafetyTab
from src.ui.details.tabs.documents import DocumentsTab

__all__ = [
    "PhysicsTab",
    "LegalTab",
    "SafetyTab",
    "DocumentsTab",
]