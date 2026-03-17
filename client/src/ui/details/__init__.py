# client/src/ui/details/__init__.py
"""
Пакет компонентов панели детальной информации.
Обновлён для поддержки контактов и банковских реквизитов.
"""
from src.ui.details.details_panel import DetailsPanel
from src.ui.details.contact_list_widget import ContactListWidget
from src.ui.details.header_widget import HeaderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.placeholder import PlaceholderWidget
from src.ui.details.tabs import DetailsTabs
from src.ui.details.field_manager import FieldManager
from src.ui.details.display_handlers import DisplayHandlers

__all__ = [
    "DetailsPanel",
    "ContactListWidget",
    "HeaderWidget",
    "InfoGrid",
    "PlaceholderWidget",
    "DetailsTabs",
    "FieldManager",
    "DisplayHandlers",
]