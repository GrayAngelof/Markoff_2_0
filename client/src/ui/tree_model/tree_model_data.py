# client/src/ui/tree_model/tree_model_data.py
"""
Миксин для управления данными модели дерева.
Предоставляет методы для добавления, обновления и удаления узлов.
"""
from PySide6.QtCore import QModelIndex, Qt
from typing import List, Any, Dict

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModelDataMixin:
    """
    Миксин для управления данными модели дерева.
    
    Предоставляет методы:
    - set_complexes: установка корневых узлов (комплексов)
    - add_children: добавление дочерних узлов (первоначальная загрузка)
    - update_children: обновление дочерних узлов с сохранением существующих
    - reset: полный сброс модели
    
    Требует наличия в классе:
    - _root_node: TreeNode - корневой узел
    - _node_index: Dict - индекс узлов
    - _add_to_index: метод для добавления узла в индекс
    - _remove_from_index: метод для удаления узла из индекса
    - beginInsertRows/endInsertRows: методы Qt
    - beginRemoveRows/endRemoveRows: методы Qt
    - beginResetModel/endResetModel: методы Qt
    - dataChanged: сигнал Qt
    """
    
    # ===== Константы =====
    _LOG_COMPLEXES_LOADED = "Загружено {count} комплексов"
    """Шаблон сообщения о загрузке комплексов"""
    
    _LOG_CHILDREN_ADDED = "Добавлено {count} {type} к {parent_type} #{parent_id}"
    """Шаблон сообщения о добавлении детей"""
    
    _LOG_CHILDREN_UPDATED = "Обновлены дети {parent_type} #{parent_id}"
    """Шаблон сообщения об обновлении детей"""
    
    _LOG_RESET = "Модель сброшена"
    """Сообщение о сбросе модели"""
    
    def __init__(self, *args, **kwargs):
        """
        Инициализирует миксин управления данными.
        """
        super().__init__(*args, **kwargs)
        log.debug("TreeModelDataMixin: инициализирован")
    
    # ===== Публичные методы =====
    
    def set_complexes(self, complexes: List[Any]) -> None:
        """
        Устанавливает список комплексов (корневые узлы).
        
        Вызывается при инициализации и полной перезагрузке.
        
        Args:
            complexes: Список объектов Complex
        """
        self.beginResetModel()
        
        # Очищаем всё
        self._root_node.remove_all_children()
        self._clear_index()
        
        # Создаём узлы для комплексов
        for complex_data in complexes:
            node = TreeNode(complex_data, NodeType.COMPLEX, self._root_node)
            self._root_node.append_child(node)
            self._add_to_index(node)
        
        self.endResetModel()
        
        log.success(self._LOG_COMPLEXES_LOADED.format(count=len(complexes)))
    
    def add_children(self, parent_index: QModelIndex, 
                     children_data: List[Any], child_type: NodeType) -> None:
        """
        Добавляет новые дочерние узлы к родительскому (первоначальная загрузка).
        
        Args:
            parent_index: Индекс родительского узла
            children_data: Список данных для дочерних узлов
            child_type: Тип дочерних узлов
        """
        parent_node = self._get_node(parent_index)
        if parent_node is None or parent_node == self._root_node:
            log.error("Попытка добавить детей к несуществующему родителю")
            return
        
        # Начинаем вставку
        first_row = parent_node.child_count()
        last_row = first_row + len(children_data) - 1
        
        self.beginInsertRows(parent_index, first_row, last_row)
        
        # Создаём и добавляем дочерние узлы
        for data in children_data:
            child_node = TreeNode(data, child_type, parent_node)
            parent_node.append_child(child_node)
            self._add_to_index(child_node)
        
        # Помечаем, что дети загружены
        parent_node.loaded = True
        
        self.endInsertRows()
        
        log.data(self._LOG_CHILDREN_ADDED.format(
            count=len(children_data),
            type=child_type.value,
            parent_type=parent_node.node_type.value,
            parent_id=parent_node.get_id()
        ))
    
    def update_children(self, parent_index: QModelIndex, 
                        children_data: List[Any], child_type: NodeType) -> None:
        """
        Обновляет дочерние узлы, сохраняя существующие где возможно.
        
        Args:
            parent_index: Индекс родительского узла
            children_data: Новые данные для дочерних узлов
            child_type: Тип дочерних узлов
        """
        parent_node = self._get_node(parent_index)
        if parent_node is None or parent_node == self._root_node:
            log.error("Попытка обновить детей несуществующего родителя")
            return
        
        # Создаём словарь существующих детей по ID
        existing_children = {
            child.get_id(): (i, child) 
            for i, child in enumerate(parent_node.children)
        }
        
        # Создаём словарь новых данных по ID
        new_data_dict = {data.id: data for data in children_data}
        
        # Обновляем существующие узлы и удаляем те, которых больше нет
        for child_id, (row, child_node) in list(existing_children.items()):
            if child_id in new_data_dict:
                # Обновляем существующий узел новыми данными
                child_node.update_data(new_data_dict[child_id])
                
                # Сигнализируем об изменении данных
                child_index = self.index(row, 0, parent_index)
                self.dataChanged.emit(
                    child_index, child_index, 
                    [Qt.DisplayRole, Qt.ForegroundRole]
                )
                
                # Удаляем из словаря новых, чтобы не создавать дубликат
                del new_data_dict[child_id]
            else:
                # Элемент удалён - убираем его
                self.beginRemoveRows(parent_index, row, row)
                parent_node.children.pop(row)
                self._remove_from_index(child_node)
                self.endRemoveRows()
                
                # Перестраиваем словарь existing_children после удаления
                existing_children = {
                    child.get_id(): (i, child) 
                    for i, child in enumerate(parent_node.children)
                }
        
        # Добавляем новые элементы
        if new_data_dict:
            first_row = parent_node.child_count()
            last_row = first_row + len(new_data_dict) - 1
            self.beginInsertRows(parent_index, first_row, last_row)
            
            for data in new_data_dict.values():
                child_node = TreeNode(data, child_type, parent_node)
                parent_node.append_child(child_node)
                self._add_to_index(child_node)
            
            self.endInsertRows()
        
        # Помечаем, что дети загружены
        parent_node.loaded = True
        
        log.data(self._LOG_CHILDREN_UPDATED.format(
            parent_type=parent_node.node_type.value,
            parent_id=parent_node.get_id()
        ))
    
    def reset(self) -> None:
        """
        Выполняет полный сброс модели.
        Очищает все узлы и индекс.
        """
        self.beginResetModel()
        self._root_node.remove_all_children()
        self._clear_index()
        self.endResetModel()
        
        log.debug(self._LOG_RESET)