# client/src/ui/tree/view.py
"""
Виджет дерева. Отображает TreeModel и эмитит события через EventBus.
"""
import traceback

from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import QModelIndex, Slot
from typing import Optional

from src.core import EventBus
from src.core.events import NodeSelected, NodeExpanded, NodeCollapsed
from src.ui.tree.node import TreeNode

from utils.logger import get_logger

log = get_logger(__name__)


class TreeView(QTreeView):
    """
    Виджет дерева.
    
    Отвечает за:
    - Отображение дерева через TreeModel
    - Эмиссию событий при действиях пользователя
    - Не содержит бизнес-логики
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._bus: Optional[EventBus] = None
        
        # Настройки внешнего вида
        self.setHeaderHidden(True)
        self.setIndentation(20)
        self.setExpandsOnDoubleClick(True)
        self.setAnimated(False)
        self.setAlternatingRowColors(False)
        self.setAutoFillBackground(False)
        self.setMouseTracking(False)

        self._update_count = 0
       
        # Подключаем сигналы Qt
        self.expanded.connect(self._on_expanded)
        self.collapsed.connect(self._on_collapsed)
        
        log.debug("TreeView создан")
    
    def set_event_bus(self, bus: EventBus) -> None:
        """Устанавливает шину событий."""
        self._bus = bus
        log.debug("EventBus установлен")
    
    def set_model(self, model) -> None:
        """Устанавливает модель и подключает сигнал выбора."""
        super().setModel(model)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        # DEBUG - детальная информация о модели
        root_count = model.rowCount()
        log.debug(f"Модель установлена, корневых узлов: {root_count}")
        
        # Проверяем, что данные есть
        if root_count > 0:
            index = model.index(0, 0)
            if index.isValid():
                data = model.data(index)
                log.debug(f"Первый корневой узел: '{data}'")

    @Slot(QModelIndex)
    def _on_expanded(self, index: QModelIndex) -> None:
        """Узел раскрыт — эмитим событие."""
        node = index.internalPointer()
        if self._bus and isinstance(node, TreeNode):
            # API - действия пользователя в UI, связанные с навигацией
            log.api(f"Узел раскрыт: {node.type}#{node.id}")
            self._bus.emit(NodeExpanded(node=node.get_identifier()))
    
    @Slot(QModelIndex)
    def _on_collapsed(self, index: QModelIndex) -> None:
        """Узел свернут — эмитим событие."""
        node = index.internalPointer()
        if self._bus and isinstance(node, TreeNode):
            log.api(f"Узел свернут: {node.type}#{node.id}")
            self._bus.emit(NodeCollapsed(node=node.get_identifier()))
    
    def _on_selection_changed(self, selected, deselected) -> None:
        """Выбор изменен — эмитим событие."""
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            node = index.internalPointer()
            if self._bus and isinstance(node, TreeNode):
                log.api(f"Узел выбран: {node.type}#{node.id}")
                self._bus.emit(NodeSelected(node=node.get_identifier()))

    def _log_update(self):
        """Вспомогательный метод для логирования обновлений."""
        self._update_count += 1
        log.debug(f"Обновление #{self._update_count}")
        # traceback.print_stack()  # раскомментировать для поиска источника