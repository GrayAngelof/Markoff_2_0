# client/src/ui/tree/tree_selection.py
"""
Модуль для работы с выделением узлов и контекстом иерархии.
Предоставляет методы для получения информации о выбранных узлах,
восстановления выделения и сбора контекста из родительских элементов.
"""
from PySide6.QtCore import QModelIndex, Slot
from typing import Optional, Dict, Any, Tuple, Union

from src.ui.tree_model import NodeType, TreeNode

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeSelectionMixin:
    """
    Миксин для работы с выделением узлов и контекстом иерархии.
    
    Предоставляет функциональность:
    - Сбор контекста из родительских узлов
    - Получение информации о выбранном узле
    - Выбор узла по типу и идентификатору
    - Безопасное восстановление выделения
    - Восстановление родительского узла как запасной вариант
    
    Требует наличия в родительском классе:
    - model: TreeModel - модель данных
    - tree_view: QTreeView - виджет дерева
    - item_selected: Signal - сигнал выбора элемента (опционально)
    """
    
    # ===== Публичные методы =====
    
    def get_selected_node_info(self) -> Optional[Tuple[str, int, Any]]:
        """
        Получает информацию о текущем выбранном узле.
        
        Returns:
            Кортеж (тип_узла, идентификатор, данные) или None, если ничего не выбрано
        """
        # Проверяем наличие необходимых компонентов
        if not hasattr(self, 'tree_view') or not hasattr(self, 'model'):
            log.error("TreeSelection: отсутствуют tree_view или model")
            return None
        
        # Получаем индексы выбранных элементов
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return None
        
        # Берём первый выбранный индекс
        index = selected_indexes[0]
        node = self.model._get_node(index)
        
        if node is None:
            return None
        
        return (node.node_type.value, node.get_id(), node.data)
    
    def select_node(self, node_type: Union[str, NodeType], node_id: int) -> bool:
        """
        Выбирает узел по типу и идентификатору.
        
        Args:
            node_type: Тип узла (строка или NodeType)
            node_id: Идентификатор узла
            
        Returns:
            True, если узел найден и выбран, иначе False
        """
        # Проверяем наличие необходимых компонентов
        if not hasattr(self, 'model') or not hasattr(self, 'tree_view'):
            log.error("TreeSelection: отсутствуют model или tree_view")
            return False
        
        # Преобразуем тип в NodeType при необходимости
        if isinstance(node_type, str):
            try:
                node_type_enum = NodeType(node_type)
            except ValueError:
                log.error(f"TreeSelection: неверный тип узла '{node_type}'")
                return False
        else:
            node_type_enum = node_type
        
        # Получаем индекс узла
        index = self.model.get_index_by_id(node_type_enum, node_id)
        
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            log.debug(f"Узел {node_type} #{node_id} выбран")
            return True
        
        log.warning(f"Узел {node_type} #{node_id} не найден")
        return False
    
    # ===== Защищённые методы для работы с контекстом =====
    
    def _get_context_for_node(self, node: TreeNode) -> Dict[str, Any]:
        """
        Собирает контекст из родительских узлов.
        
        Проходит по цепочке родителей и собирает информацию:
        - Имя комплекса
        - Имя корпуса
        - Номер этажа
        
        Args:
            node: Узел, для которого собирается контекст
            
        Returns:
            Словарь с контекстом:
            {
                'complex_name': str или None,
                'building_name': str или None,
                'floor_num': int или None
            }
        """
        context = {
            'complex_name': None,
            'building_name': None,
            'floor_num': None
        }
        
        current_node = node
        while current_node is not None:
            # Проверяем тип текущего узла и извлекаем соответствующую информацию
            if current_node.node_type == NodeType.COMPLEX and current_node.data:
                context['complex_name'] = current_node.data.name
                log.debug(f"Найден комплекс: {current_node.data.name}")
                
            elif current_node.node_type == NodeType.BUILDING and current_node.data:
                context['building_name'] = current_node.data.name
                log.debug(f"Найден корпус: {current_node.data.name}")
                
            elif current_node.node_type == NodeType.FLOOR and current_node.data:
                context['floor_num'] = current_node.data.number
                log.debug(f"Найден этаж: {current_node.data.number}")
            
            # Переходим к родителю
            current_node = current_node.parent
        
        return context
    
    # ===== Приватные методы восстановления выделения =====
    
    @Slot(str, int, dict)
    def _restore_selection_safe(self, node_type: str, node_id: int, 
                                context: Optional[Dict] = None) -> None:
        """
        Безопасно восстанавливает выделение узла по его идентификатору.
        
        Пытается найти узел по типу и ID. Если узел найден:
        1. Устанавливает его как текущий
        2. Испускает сигнал item_selected с правильным контекстом
        
        Если узел не найден, пробует восстановить родительский узел.
        
        Args:
            node_type: Тип искомого узла
            node_id: Идентификатор искомого узла
            context: Контекст для восстановления (если None, будет собран заново)
        """
        try:
            # Преобразуем тип в NodeType
            try:
                node_type_enum = NodeType(node_type)
            except ValueError:
                log.error(f"Неверный тип узла при восстановлении: '{node_type}'")
                return
            
            # Получаем индекс узла
            index = self.model.get_index_by_id(node_type_enum, node_id)
            
            if index.isValid():
                node = self.model._get_node(index)
                if node and node.get_id() == node_id:
                    # Устанавливаем выделение
                    self.tree_view.setCurrentIndex(index)
                    
                    # Подготавливаем контекст
                    if context is None:
                        context = self._get_context_for_node(node)
                    
                    # Испускаем сигнал, если он доступен
                    if hasattr(self, 'item_selected'):
                        self.item_selected.emit(node_type, node_id, node.data, context)
                        log.info(f"Восстановлено выделение {node_type} #{node_id}")
                    else:
                        log.debug(f"Узел {node_type} #{node_id} найден, сигнал отсутствует")
                    
                    return
            
            # Узел не найден - пробуем восстановить родителя
            log.warning(f"Узел {node_type} #{node_id} не найден, ищем родителя")
            self._restore_parent_selection(node_type, node_id)
            
        except Exception as error:
            log.error(f"Ошибка при восстановлении выделения: {error}")
            import traceback
            traceback.print_exc()
    
    @Slot(str, int)
    def _restore_parent_selection(self, node_type: str, node_id: int) -> None:
        """
        Восстанавливает родительский узел, если целевой узел не найден.
        
        Используется как запасной вариант при восстановлении выделения.
        Определяет тип родителя и пытается выбрать первый доступный узел этого типа.
        
        Args:
            node_type: Тип искомого узла (для определения родителя)
            node_id: Идентификатор искомого узла (не используется, для совместимости)
        """
        try:
            # Определяем тип родителя на основе типа искомого узла
            parent_type_enum = None
            
            if node_type == NodeType.ROOM.value:
                parent_type_enum = NodeType.FLOOR
                log.debug("Ищем родительский этаж для комнаты")
                
            elif node_type == NodeType.FLOOR.value:
                parent_type_enum = NodeType.BUILDING
                log.debug("Ищем родительский корпус для этажа")
                
            elif node_type == NodeType.BUILDING.value:
                parent_type_enum = NodeType.COMPLEX
                log.debug("Ищем родительский комплекс для корпуса")
                
            else:
                log.warning(f"Для типа {node_type} нет родительского типа")
                return
            
            # Для комплекса выбираем первый в списке
            if parent_type_enum == NodeType.COMPLEX:
                index = self.model.index(0, 0)
                if index.isValid():
                    node = self.model._get_node(index)
                    if node:
                        self.tree_view.setCurrentIndex(index)
                        
                        # Собираем контекст
                        context = self._get_context_for_node(node)
                        
                        # Испускаем сигнал
                        if hasattr(self, 'item_selected'):
                            self.item_selected.emit(
                                NodeType.COMPLEX.value,
                                node.get_id(),
                                node.data,
                                context
                            )
                            log.info(f"Выбран комплекс #{node.get_id()} как запасной вариант")
                        
        except Exception as error:
            log.error(f"Ошибка при восстановлении родителя: {error}")