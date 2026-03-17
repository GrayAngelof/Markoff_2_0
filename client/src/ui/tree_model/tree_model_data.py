# client/src/ui/tree_model/tree_model_data.py
"""
Миксин для управления данными модели дерева.
Предоставляет методы для добавления, обновления и удаления узлов.
"""
from PySide6.QtCore import QModelIndex, Qt
from typing import List, Any, Dict, Protocol, runtime_checkable, cast

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


@runtime_checkable
class TreeModelDataProtocol(Protocol):
    """
    Протокол, определяющий методы, которые должны быть в классе,
    использующем TreeModelDataMixin.
    """
    _root_node: TreeNode
    _node_index: Dict[str, TreeNode]
    
    def beginResetModel(self) -> None: ...
    def endResetModel(self) -> None: ...
    def beginInsertRows(self, parent: QModelIndex, first: int, last: int) -> None: ...
    def endInsertRows(self) -> None: ...
    def beginRemoveRows(self, parent: QModelIndex, first: int, last: int) -> None: ...
    def endRemoveRows(self) -> None: ...
    def dataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: List[int]) -> None: ...
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex: ...
    def _get_node(self, index: QModelIndex) -> TreeNode: ...
    def _add_to_index(self, node: TreeNode) -> None: ...
    def _remove_from_index(self, node: TreeNode) -> None: ...
    def _clear_index(self) -> None: ...


class TreeModelDataMixin:
    """
    Миксин для управления данными модели дерева.
    
    Предоставляет методы:
    - set_complexes: установка корневых узлов (комплексов)
    - add_children: добавление дочерних узлов (первоначальная загрузка)
    - update_children: обновление дочерних узлов с сохранением существующих
    - reset: полный сброс модели
    
    Требует наличия в классе методов, определённых в TreeModelDataProtocol.
    """
    
    # ===== Аннотации для атрибутов, которые будут в конечном классе =====
    _root_node: TreeNode
    _node_index: Dict[str, TreeNode]
    
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
        
        # Проверяем, что класс реализует необходимый протокол
        if not isinstance(self, TreeModelDataProtocol):
            log.warning(f"{self.__class__.__name__} должен реализовывать TreeModelDataProtocol")
        
        log.debug("TreeModelDataMixin: инициализирован")
    
    # ===== Вспомогательные методы для доступа к атрибутам =====
    
    def _get_root_node(self) -> TreeNode:
        """Возвращает корневой узел."""
        return cast(TreeNode, self._root_node)
    
    def _get_node_index(self) -> Dict[str, TreeNode]:
        """Возвращает индекс узлов."""
        return cast(Dict[str, TreeNode], self._node_index)
    
    # ===== Публичные методы =====
    
    def set_complexes(self, complexes: List[Any]) -> None:
        """
        Устанавливает список комплексов (корневые узлы).
        
        Вызывается при инициализации и полной перезагрузке.
        
        Args:
            complexes: Список объектов Complex
        """
        # Проверяем наличие необходимых атрибутов
        if not hasattr(self, '_root_node'):
            log.error("TreeModelDataMixin: отсутствует атрибут _root_node")
            return
        
        root_node = self._get_root_node()
        
        self.beginResetModel()  # type: ignore
        
        # Очищаем всё
        root_node.remove_all_children()
        if hasattr(self, '_clear_index'):
            self._clear_index()  # type: ignore
        
        # Создаём узлы для комплексов
        for complex_data in complexes:
            node = TreeNode(complex_data, NodeType.COMPLEX, root_node)
            root_node.append_child(node)
            if hasattr(self, '_add_to_index'):
                self._add_to_index(node)  # type: ignore
        
        self.endResetModel()  # type: ignore
        
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
        # Проверяем наличие необходимых методов
        if not hasattr(self, '_get_node') or not hasattr(self, '_root_node'):
            log.error("TreeModelDataMixin: отсутствуют необходимые методы/атрибуты")
            return
        
        root_node = self._get_root_node()
        parent_node = self._get_node(parent_index)  # type: ignore
        if parent_node is None or parent_node == root_node:
            log.error("Попытка добавить детей к несуществующему родителю")
            return
        
        # Начинаем вставку
        first_row = parent_node.child_count()
        last_row = first_row + len(children_data) - 1
        
        self.beginInsertRows(parent_index, first_row, last_row)  # type: ignore
        
        # Создаём и добавляем дочерние узлы
        for data in children_data:
            child_node = TreeNode(data, child_type, parent_node)
            parent_node.append_child(child_node)
            if hasattr(self, '_add_to_index'):
                self._add_to_index(child_node)  # type: ignore
        
        # Помечаем, что дети загружены
        parent_node.loaded = True
        
        self.endInsertRows()  # type: ignore
        
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
        # Проверяем наличие необходимых методов
        if not hasattr(self, '_get_node') or not hasattr(self, '_root_node') or \
           not hasattr(self, 'index') or not hasattr(self, 'dataChanged'):
            log.error("TreeModelDataMixin: отсутствуют необходимые методы/атрибуты")
            return
        
        root_node = self._get_root_node()
        parent_node = self._get_node(parent_index)  # type: ignore
        if parent_node is None or parent_node == root_node:
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
                child_index = self.index(row, 0, parent_index)  # type: ignore
                self.dataChanged.emit(  # type: ignore
                    child_index, child_index, 
                    [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ForegroundRole]
                )
                
                # Удаляем из словаря новых, чтобы не создавать дубликат
                del new_data_dict[child_id]
            else:
                # Элемент удалён - убираем его
                self.beginRemoveRows(parent_index, row, row)  # type: ignore
                parent_node.children.pop(row)
                if hasattr(self, '_remove_from_index'):
                    self._remove_from_index(child_node)  # type: ignore
                self.endRemoveRows()  # type: ignore
                
                # Перестраиваем словарь existing_children после удаления
                existing_children = {
                    child.get_id(): (i, child) 
                    for i, child in enumerate(parent_node.children)
                }
        
        # Добавляем новые элементы
        if new_data_dict:
            first_row = parent_node.child_count()
            last_row = first_row + len(new_data_dict) - 1
            self.beginInsertRows(parent_index, first_row, last_row)  # type: ignore
            
            for data in new_data_dict.values():
                child_node = TreeNode(data, child_type, parent_node)
                parent_node.append_child(child_node)
                if hasattr(self, '_add_to_index'):
                    self._add_to_index(child_node)  # type: ignore
            
            self.endInsertRows()  # type: ignore
        
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
        # Проверяем наличие необходимых атрибутов
        if not hasattr(self, '_root_node'):
            log.error("TreeModelDataMixin: отсутствует атрибут _root_node")
            return
        
        root_node = self._get_root_node()
        
        self.beginResetModel()  # type: ignore
        root_node.remove_all_children()
        if hasattr(self, '_clear_index'):
            self._clear_index()  # type: ignore
        self.endResetModel()  # type: ignore
        
        log.debug(self._LOG_RESET)