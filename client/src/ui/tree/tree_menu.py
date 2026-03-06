# client/src/ui/tree/tree_menu.py
"""
Модуль для контекстного меню дерева.
Предоставляет функциональность контекстного меню для узлов дерева
с возможностью обновления выбранного узла.
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import QPoint, Slot, Qt, QModelIndex
from PySide6.QtGui import QAction
from typing import Dict, Optional

from src.ui.tree_model import NodeType, TreeNode

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeMenuMixin:
    """
    Миксин для контекстного меню дерева.
    
    Предоставляет контекстное меню с действиями для узлов дерева:
    - Обновление выбранного узла
    - (в будущем можно добавить другие действия)
    
    Требует наличия в родительском классе:
    - tree_view: QTreeView - виджет дерева
    - model: TreeModel - модель данных
    - _refresh_node: метод для обновления узла
    """
    
    # ===== Константы =====
    _MENU_ACTION_REFRESH = "🔄 Обновить {node_type}"
    """Шаблон текста для действия обновления в меню"""
    
    _NODE_TYPE_DISPLAY_NAMES: Dict[NodeType, str] = {
        NodeType.COMPLEX: "комплекс",
        NodeType.BUILDING: "корпус",
        NodeType.FLOOR: "этаж",
        NodeType.ROOM: "помещение"
    }
    """Отображаемые названия для типов узлов"""
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_node_display_name(self, node: TreeNode) -> str:
        """
        Возвращает отображаемое название для типа узла.
        
        Args:
            node: Узел дерева
            
        Returns:
            Строка с названием типа узла (например, "комплекс")
        """
        return self._NODE_TYPE_DISPLAY_NAMES.get(node.node_type, "объект")
    
    def _create_refresh_action(self, menu: QMenu, node: TreeNode, index: QModelIndex) -> QAction:
        """
        Создаёт действие для обновления узла в контекстном меню.
        
        Args:
            menu: Родительское меню
            node: Узел, для которого создаётся действие
            index: Индекс узла в модели
            
        Returns:
            Созданное действие QAction
        """
        # Получаем отображаемое название типа узла
        node_type_display = self._get_node_display_name(node)
        
        # Создаём действие с соответствующим текстом
        action_text = self._MENU_ACTION_REFRESH.format(node_type=node_type_display)
        refresh_action = QAction(action_text, menu)
        
        # Подключаем сигнал с правильным контекстом
        # Используем лямбду с захватом индекса для избежания проблем с замыканием
        refresh_action.triggered.connect(
            lambda checked=False, idx=index: self._refresh_node(idx, use_cache=False)
        )
        
        # Добавляем всплывающую подсказку
        refresh_action.setStatusTip(f"Обновить данные {node_type_display}")
        
        return refresh_action
    
    # ===== Публичные методы =====
    
    @Slot(QPoint)
    def _show_context_menu(self, position: QPoint) -> None:
        """
        Показывает контекстное меню для узла в указанной позиции.
        
        Args:
            position: Позиция курсора в координатах viewport
        """
        # Получаем индекс узла под курсором
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            log.debug("Контекстное меню: клик вне узла")
            return
        
        # Получаем узел по индексу
        node = self.model._get_node(index)
        if not node:
            log.warning("Контекстное меню: узел не найден по индексу")
            return
        
        # Создаём контекстное меню
        menu = QMenu(self.tree_view)
        
        # Добавляем действие для обновления узла
        refresh_action = self._create_refresh_action(menu, node, index)
        menu.addAction(refresh_action)
        
        # TODO: В будущем можно добавить другие действия:
        # - Копировать название
        # - Показать в проводнике
        # - Свойства
        # - и т.д.
        
        # Показываем меню в глобальных координатах
        global_position = self.tree_view.viewport().mapToGlobal(position)
        menu.exec(global_position)
        
        log.debug(f"Контекстное меню показано для {self._get_node_display_name(node)}")