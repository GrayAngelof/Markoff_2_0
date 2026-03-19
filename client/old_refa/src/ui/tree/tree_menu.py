# client/src/ui/tree/tree_menu.py
"""
Модуль контекстного меню для дерева.
В новой архитектуре генерирует события через EventBus.
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import QPoint, Slot, Qt  # <-- ИСПРАВЛЕНО: добавили импорт Qt
from PySide6.QtGui import QAction
from typing import Optional, Dict

from src.ui.tree_model.tree_node import TreeNode
from src.core.event_bus import EventBus
from src.core.events import UIEvents

from utils.logger import get_logger
log = get_logger(__name__)


class TreeMenu:
    """
    Контекстное меню для дерева объектов.
    
    В новой архитектуре не содержит логики, только генерирует события:
    - При выборе "Обновить узел" → ui.refresh_requested с mode='current'
    """
    
    # ===== Константы =====
    _MENU_ACTION_REFRESH = "🔄 Обновить {node_type}"
    """Шаблон текста для действия обновления в меню"""
    
    _NODE_TYPE_DISPLAY_NAMES: Dict[str, str] = {
        'complex': 'комплекс',
        'building': 'корпус',
        'floor': 'этаж',
        'room': 'помещение'
    }
    """Отображаемые названия для типов узлов"""
    
    def __init__(self, tree_view, event_bus: EventBus):
        """
        Инициализирует контекстное меню.
        
        Args:
            tree_view: Родительское дерево (TreeView)
            event_bus: Шина событий
        """
        self._tree_view = tree_view
        self._bus = event_bus
        self._current_node: Optional[TreeNode] = None
        self._current_index = None
        
        # Подключаем сигнал контекстного меню
        self._tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # <-- ИСПРАВЛЕНО
        self._tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        log.debug("TreeMenu: инициализирован")
    
    # ===== Приватные методы =====
    
    def _get_node_display_name(self, node: TreeNode) -> str:
        """
        Возвращает отображаемое название для типа узла.
        
        Args:
            node: Узел дерева
            
        Returns:
            Строка с названием типа узла
        """
        return self._NODE_TYPE_DISPLAY_NAMES.get(node.node_type.value, 'объект')
    
    def _create_refresh_action(self, menu: QMenu, node: TreeNode) -> QAction:
        """
        Создаёт действие для обновления узла.
        
        Args:
            menu: Родительское меню
            node: Узел, для которого создаётся действие
            
        Returns:
            Созданное действие QAction
        """
        node_type_display = self._get_node_display_name(node)
        action_text = self._MENU_ACTION_REFRESH.format(node_type=node_type_display)
        
        refresh_action = QAction(action_text, menu)
        refresh_action.triggered.connect(self._on_refresh_current)
        refresh_action.setStatusTip(f"Обновить данные {node_type_display}")
        
        return refresh_action
    
    def _on_refresh_current(self) -> None:
        """
        Обрабатывает выбор пункта "Обновить узел".
        Генерирует событие ui.refresh_requested.
        """
        if not self._current_node:
            log.warning("TreeMenu: нет текущего узла для обновления")
            return
        
        node_type = self._current_node.node_type.value
        node_id = self._current_node.get_id()
        
        log.info(f"TreeMenu: запрос обновления узла {node_type}#{node_id}")
        
        self._bus.emit(UIEvents.REFRESH_REQUESTED, {
            'mode': 'current',
            'node_type': node_type,
            'node_id': node_id
        }, source='tree_menu')
    
    @Slot(QPoint)
    def _show_context_menu(self, position: QPoint) -> None:
        """
        Показывает контекстное меню в указанной позиции.
        
        Args:
            position: Позиция курсора в координатах viewport
        """
        # Получаем индекс узла под курсором
        index = self._tree_view.indexAt(position)
        if not index.isValid():
            log.debug("TreeMenu: клик вне узла")
            return
        
        # Получаем узел по индексу
        node = index.internalPointer()
        if not node or not isinstance(node, TreeNode):
            log.warning("TreeMenu: узел не найден по индексу")
            return
        
        self._current_node = node
        self._current_index = index
        
        # Создаём контекстное меню
        menu = QMenu(self._tree_view)
        
        # Добавляем действие для обновления узла
        refresh_action = self._create_refresh_action(menu, node)
        menu.addAction(refresh_action)
        
        # Показываем меню в глобальных координатах
        global_position = self._tree_view.viewport().mapToGlobal(position)
        menu.exec(global_position)
        
        log.debug(f"TreeMenu: показано меню для {self._get_node_display_name(node)}")
    
    def cleanup(self) -> None:
        """Очищает ресурсы."""
        self._current_node = None
        self._current_index = None
        log.debug("TreeMenu: очищен")