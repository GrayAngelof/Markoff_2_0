# client/src/ui/main_window/controllers/refresh_controller.py
"""
Контроллер обновления данных.
Управляет тремя уровнями обновления:
- Текущий узел (F5)
- Все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, Slot

from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class RefreshController(QObject):
    """
    Контроллер обновления данных.
    
    Обрабатывает запросы на обновление разных уровней:
    - refresh_current: обновление текущего узла
    - refresh_visible: обновление всех раскрытых узлов
    - full_reset: полная перезагрузка с подтверждением
    """
    
    # ===== Константы =====
    _RESET_CONFIRMATION_TITLE = "Подтверждение"
    """Заголовок окна подтверждения"""
    
    _RESET_CONFIRMATION_TEXT = (
        "Вы уверены, что хотите выполнить полную перезагрузку?\n"
        "Все данные будут загружены заново."
    )
    """Текст подтверждения полной перезагрузки"""
    
    def __init__(self, tree_view, status_bar) -> None:
        """
        Инициализирует контроллер обновления.
        
        Args:
            tree_view: Виджет дерева (TreeView)
            status_bar: Строка статуса (StatusBar)
        """
        super().__init__()
        
        self._tree_view = tree_view
        self._status_bar = status_bar
        
        log.debug("RefreshController: инициализирован")
    
    # ===== Приватные методы =====
    
    def _confirm_full_reset(self) -> bool:
        """
        Запрашивает подтверждение полной перезагрузки.
        
        Returns:
            bool: True если пользователь подтвердил
        """
        # ИСПРАВЛЕНО: используем правильные константы QMessageBox
        reply = QMessageBox.question(
            self._tree_view,
            self._RESET_CONFIRMATION_TITLE,
            self._RESET_CONFIRMATION_TEXT,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        confirmed = reply == QMessageBox.StandardButton.Yes
        log.debug(f"RefreshController: подтверждение перезагрузки: {confirmed}")
        
        return confirmed
    
    # ===== Публичные слоты =====
    
    @Slot()
    def refresh_current(self) -> None:
        """Обновляет текущий выбранный узел."""
        selected = self._tree_view.get_selected_node_info()
        
        if selected:
            node_type, node_id, _ = selected
            self._status_bar.show_temporary_message(
                f"🔄 Обновление {node_type} #{node_id}..."
            )
            self._tree_view.refresh_current()
            log.info(f"Обновление текущего узла: {node_type} #{node_id}")
        else:
            self._status_bar.show_temporary_message(
                "⚠️ Нет выбранного узла для обновления"
            )
            log.debug("RefreshController: нет выбранного узла")
    
    @Slot()
    def refresh_visible(self) -> None:
        """Обновляет все раскрытые узлы."""
        self._status_bar.show_temporary_message(
            "🔄 Обновление всех раскрытых узлов..."
        )
        self._tree_view.refresh_visible()
        log.info("Обновление всех раскрытых узлов")
    
    @Slot()
    def full_reset(self) -> None:
        """Выполняет полную перезагрузку после подтверждения."""
        if self._confirm_full_reset():
            self._status_bar.show_temporary_message("🔄 Полная перезагрузка...")
            self._tree_view.full_reset()
            self._status_bar.show_temporary_message("✅ Полная перезагрузка выполнена")
            log.info("Полная перезагрузка выполнена")