# client/src/ui/details/details_tabs.py
"""
Виджет вкладок для панели детальной информации.
На данном этапе — только структурный каркас с пустыми вкладками.
"""

from PySide6.QtWidgets import QTabWidget, QWidget
from typing import Optional

from src.ui.details.tabs.physics import PhysicsTab
from src.ui.details.tabs.legal import LegalTab
from src.ui.details.tabs.safety import SafetyTab
from src.ui.details.tabs.documents import DocumentsTab

from utils.logger import get_logger

log = get_logger(__name__)


class DetailsTabs(QTabWidget):
    """
    Виджет вкладок для панели детальной информации.
    
    На данном этапе:
    - Создает пустые вкладки
    - Не содержит логики загрузки данных
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет вкладок.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        log.debug("DetailsTabs: создание структурного каркаса")
        
        self._setup_tabs()
        
        log.debug("DetailsTabs: структурный каркас создан")
    
    def _setup_tabs(self) -> None:
        """Создает структурный каркас вкладок."""
        # Вкладка физики
        self._physics_tab = PhysicsTab()
        self.addTab(self._physics_tab, "📊 Физика")
        
        # Вкладка юриков
        self._legal_tab = LegalTab()
        self.addTab(self._legal_tab, "⚖️ Юрики")
        
        # Вкладка пожарной безопасности
        self._safety_tab = SafetyTab()
        self.addTab(self._safety_tab, "🔥 Пожарка")
        
        # Вкладка документов
        self._documents_tab = DocumentsTab()
        self.addTab(self._documents_tab, "📄 Документы")
        
        log.debug(f"DetailsTabs: создано {self.count()} вкладок")
    
    # ===== Геттеры (для будущего использования) =====
    
    @property
    def physics_tab(self) -> PhysicsTab:
        """Возвращает вкладку физики."""
        return self._physics_tab
    
    @property
    def legal_tab(self) -> LegalTab:
        """Возвращает вкладку юриков."""
        return self._legal_tab
    
    @property
    def safety_tab(self) -> SafetyTab:
        """Возвращает вкладку пожарной безопасности."""
        return self._safety_tab
    
    @property
    def documents_tab(self) -> DocumentsTab:
        """Возвращает вкладку документов."""
        return self._documents_tab