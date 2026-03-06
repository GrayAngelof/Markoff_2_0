# client/src/ui/main_window/controllers/data_controller.py
"""
Контроллер обработки данных.
Отвечает за обработку сигналов загрузки данных и обновление интерфейса.
"""
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class DataController(QObject):
    """
    Контроллер обработки данных.
    
    Обрабатывает сигналы:
    - data_loading: начало загрузки данных
    - data_loaded: завершение загрузки
    - data_error: ошибка загрузки
    """
    
    def __init__(self, tree_view, status_bar, counter_action) -> None:
        """
        Инициализирует контроллер данных.
        
        Args:
            tree_view: Виджет дерева (TreeView)
            status_bar: Строка статуса (StatusBar)
            counter_action: Действие счётчика объектов (QAction)
        """
        super().__init__()
        
        self._tree_view = tree_view
        self._status_bar = status_bar
        self._counter_action = counter_action
        
        log.debug("DataController: инициализирован")
    
    # ===== Приватные методы =====
    
    def _update_counter(self) -> None:
        """Обновляет счётчик объектов в панели инструментов."""
        if hasattr(self._tree_view, 'cache'):
            stats = self._tree_view.cache.get_stats()
            self._counter_action.setText(f"📊 В кэше: {stats['size']} объектов")
            log.debug(f"DataController: счётчик обновлён: {stats['size']}")
    
    # ===== Публичные слоты =====
    
    @Slot(str, int)
    def on_data_loading(self, node_type: str, node_id: int) -> None:
        """
        Обрабатывает начало загрузки данных.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self._status_bar.show_temporary_message(
            f"📡 Загрузка {node_type} #{node_id}..."
        )
        log.debug(f"DataController: начало загрузки {node_type} #{node_id}")
    
    @Slot(str, int)
    def on_data_loaded(self, node_type: str, node_id: int) -> None:
        """
        Обрабатывает завершение загрузки данных.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self._status_bar.show_temporary_message(
            f"✅ Загружен {node_type} #{node_id}"
        )
        self._update_counter()
        log.debug(f"DataController: загрузка завершена {node_type} #{node_id}")
    
    @Slot(str, int, str)
    def on_data_error(self, node_type: str, node_id: int, error: str) -> None:
        """
        Обрабатывает ошибку загрузки данных.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        self._status_bar.show_temporary_message(
            f"❌ Ошибка загрузки {node_type} #{node_id}"
        )
        
        QMessageBox.warning(
            self._tree_view,
            "Ошибка загрузки",
            f"Не удалось загрузить {node_type} #{node_id}:\n{error}"
        )
        
        log.error(f"Ошибка загрузки {node_type} #{node_id}: {error}")