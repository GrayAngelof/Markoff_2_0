# client/src/controllers/details_controller.py
"""
DetailsController — управление панелью детальной информации.

На данном этапе:
- Испускает ShowPlaceholder при запуске
- Не загружает данные
"""

from typing import Optional

from src.core import EventBus
from src.core.events import ShowDetailsPanel
from src.controllers.base import BaseController
from src.services.data_loader import DataLoader
from utils.logger import get_logger

log = get_logger(__name__)


class DetailsController(BaseController):
    """
    Контроллер панели деталей.
    
    На данном этапе только показывает заглушку.
    """
    
    def __init__(self, bus: EventBus, loader: Optional[DataLoader] = None):
        """
        Инициализирует контроллер панели деталей.
        
        Args:
            bus: Шина событий
        """
        log.info("Инициализация DetailsController")        
        super().__init__(bus)
        log.system("EventBus инициализирован")

        # loader не используется (YAGNI), но принимаем для совместимости
        self._loader = loader

        # При старте — показываем заглушку
        self._bus.emit(ShowDetailsPanel())
        
        log.success("DetailsController инициализирован")