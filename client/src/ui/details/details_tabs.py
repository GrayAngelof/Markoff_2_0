# client/src/ui/details/details_tabs.py
"""
Виджет вкладок для панели детальной информации.

На данном этапе — только структурный каркас с пустыми вкладками.
"""

# ===== ИМПОРТЫ =====
from typing import Final, Optional

from PySide6.QtWidgets import QTabWidget, QWidget

from src.ui.details.tabs.documents import DocumentsTab
from src.ui.details.tabs.legal import LegalTab
from src.ui.details.tabs.physics import PhysicsTab
from src.ui.details.tabs.safety import SafetyTab
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsTabs(QTabWidget):
    """
    Виджет вкладок для панели детальной информации.

    На данном этапе — только структурный каркас с пустыми вкладками.
    """

    # Локальные константы — названия вкладок
    _TAB_PHYSICS: Final[str] = "Физика"
    _TAB_LEGAL: Final[str] = "Юрики"
    _TAB_SAFETY: Final[str] = "Пожарка"
    _TAB_DOCUMENTS: Final[str] = "Документы"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует виджет вкладок."""
        log.info("Инициализация DetailsTabs")
        super().__init__(parent)

        log.debug("DetailsTabs: создание структурного каркаса")

        self._setup_tabs()

        log.debug("DetailsTabs: структурный каркас создан")
        log.system("DetailsTabs инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    @property
    def physics_tab(self) -> PhysicsTab:
        """Возвращает вкладку физики."""
        return self._physics_tab

    @property
    def legal_tab(self) -> LegalTab:
        """Возвращает вкладку юридических лиц."""
        return self._legal_tab

    @property
    def safety_tab(self) -> SafetyTab:
        """Возвращает вкладку пожарной безопасности."""
        return self._safety_tab

    @property
    def documents_tab(self) -> DocumentsTab:
        """Возвращает вкладку документов."""
        return self._documents_tab

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_tabs(self) -> None:
        """Создаёт структурный каркас вкладок."""
        self._physics_tab = PhysicsTab()
        self.addTab(self._physics_tab, self._TAB_PHYSICS)
        log.success("PhysicsTab создан")

        self._legal_tab = LegalTab()
        self.addTab(self._legal_tab, self._TAB_LEGAL)
        log.success("LegalTab создан")

        self._safety_tab = SafetyTab()
        self.addTab(self._safety_tab, self._TAB_SAFETY)
        log.success("SafetyTab создан")

        self._documents_tab = DocumentsTab()
        self.addTab(self._documents_tab, self._TAB_DOCUMENTS)
        log.success("DocumentsTab создан")

        log.success(f"DetailsTabs: создано {self.count()} вкладок")