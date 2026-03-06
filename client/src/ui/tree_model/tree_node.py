# client/src/ui/tree_model/tree_node.py
"""
Модуль с классом TreeNode, представляющим узел дерева.
Содержит данные, тип, связи с родителем и детьми, а также состояние загрузки.
"""
from typing import Optional, List, Any, TYPE_CHECKING

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.ui.tree_model.node_types import NodeType
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeNode:
    """
    Узел дерева, содержащий данные и связи с родительскими/дочерними узлами.
    
    Атрибуты:
        data: Модель данных (Complex, Building, Floor или Room)
        node_type: Тип узла (NodeType)
        parent: Родительский узел (None для корневого узла)
        children: Список дочерних узлов
        loaded: Флаг, указывающий, загружены ли дочерние элементы
        
    Методы:
        - append_child: Добавление дочернего узла
        - remove_child: Удаление конкретного ребёнка
        - remove_all_children: Удаление всех детей
        - child_at: Получение ребёнка по индексу
        - row: Получение индекса узла в родителе
        - child_count: Количество детей
        - get_display_text: Текст для отображения в дереве
        - get_id: Получение идентификатора узла
        - update_data: Обновление данных узла
    """
    
    # ===== Константы для форматирования текста =====
    _DISPLAY_FORMAT_BUILDING = "{name} ({count})"
    """Формат отображения корпуса с количеством этажей"""
    
    _DISPLAY_FORMAT_FLOOR = "{text} ({count})"
    """Формат отображения этажа с количеством помещений"""
    
    _DISPLAY_FORMAT_COMPLEX_WITH_COUNT = "{name} ({count})"
    """Формат отображения комплекса с количеством корпусов"""
    
    _FLOOR_TEXT_BASEMENT = "Подвал {num}"
    """Текст для подвального этажа"""
    
    _FLOOR_TEXT_GROUND = "Цокольный этаж"
    """Текст для цокольного этажа"""
    
    _FLOOR_TEXT_REGULAR = "Этаж {num}"
    """Текст для обычного этажа"""
    
    _UNKNOWN_TEXT = "???"
    """Текст для неизвестного типа узла"""
    
    def __init__(self, data: Any, node_type: NodeType, 
                 parent: Optional['TreeNode'] = None) -> None:
        """
        Инициализирует узел дерева.
        
        Args:
            data: Модель данных (Complex, Building, Floor или Room)
            node_type: Тип узла
            parent: Родительский узел (по умолчанию None)
        """
        self._data = data
        self._node_type = node_type
        self._parent = parent
        self._children: List['TreeNode'] = []
        self._loaded = False
        
        log.debug(f"TreeNode создан: {node_type} id={self.get_id()}")
    
    # ===== Геттеры =====
    
    @property
    def data(self) -> Any:
        """Возвращает данные узла."""
        return self._data
    
    @property
    def node_type(self) -> NodeType:
        """Возвращает тип узла."""
        return self._node_type
    
    @property
    def parent(self) -> Optional['TreeNode']:
        """Возвращает родительский узел."""
        return self._parent
    
    @property
    def children(self) -> List['TreeNode']:
        """Возвращает список дочерних узлов."""
        return self._children.copy()
    
    @property
    def loaded(self) -> bool:
        """
        Возвращает флаг загрузки дочерних элементов.
        
        Returns:
            True, если дочерние элементы загружены
        """
        return self._loaded
    
    @loaded.setter
    def loaded(self, value: bool) -> None:
        """
        Устанавливает флаг загрузки дочерних элементов.
        
        Args:
            value: Новое значение флага
        """
        self._loaded = value
    
    # ===== Публичные методы =====
    
    def append_child(self, child: 'TreeNode') -> None:
        """
        Добавляет дочерний узел.
        
        Args:
            child: Дочерний узел для добавления
        """
        self._children.append(child)
        log.debug(f"Дочерний узел добавлен к {self._node_type} #{self.get_id()}")
    
    def remove_child(self, child: 'TreeNode') -> bool:
        """
        Удаляет конкретного ребёнка.
        
        Args:
            child: Дочерний узел для удаления
            
        Returns:
            True, если узел был удалён, иначе False
        """
        if child in self._children:
            self._children.remove(child)
            log.debug(f"Дочерний узел удалён из {self._node_type} #{self.get_id()}")
            return True
        return False
    
    def remove_all_children(self) -> None:
        """Удаляет всех детей и сбрасывает флаг загрузки."""
        self._children.clear()
        self._loaded = False
        log.debug(f"Все дочерние узлы удалены из {self._node_type} #{self.get_id()}")
    
    def child_at(self, row: int) -> Optional['TreeNode']:
        """
        Возвращает ребёнка по индексу.
        
        Args:
            row: Индекс ребёнка
            
        Returns:
            TreeNode или None, если индекс вне диапазона
        """
        if 0 <= row < len(self._children):
            return self._children[row]
        return None
    
    def row(self) -> int:
        """
        Возвращает индекс этого узла в родителе.
        
        Returns:
            Индекс узла или 0, если узел не найден в списке детей родителя
        """
        if self._parent:
            try:
                return self._parent._children.index(self)
            except ValueError:
                log.warning(f"Узел {self._node_type} #{self.get_id()} не найден в родителе")
                return 0
        return 0
    
    def child_count(self) -> int:
        """
        Возвращает количество дочерних узлов.
        
        Returns:
            Количество детей
        """
        return len(self._children)
    
    def get_display_text(self) -> str:
        """
        Возвращает текст для отображения в дереве.
        
        Для каждого типа узла применяется своё форматирование:
        - Комплекс: название (количество корпусов)
        - Корпус: название (количество этажей)
        - Этаж: тип этажа (количество помещений)
        - Помещение: номер
        
        Returns:
            str: Отформатированный текст для отображения
        """
        if self._node_type == NodeType.COMPLEX and isinstance(self._data, Complex):
            return self._format_complex_text()
        
        elif self._node_type == NodeType.BUILDING and isinstance(self._data, Building):
            return self._format_building_text()
        
        elif self._node_type == NodeType.FLOOR and isinstance(self._data, Floor):
            return self._format_floor_text()
        
        elif self._node_type == NodeType.ROOM and isinstance(self._data, Room):
            return self._data.number
        
        log.warning(f"Неизвестный тип узла для отображения: {self._node_type}")
        return self._UNKNOWN_TEXT
    
    def get_id(self) -> int:
        """
        Возвращает идентификатор узла.
        
        Returns:
            ID узла или -1, если идентификатор отсутствует
        """
        if hasattr(self._data, 'id'):
            return self._data.id
        log.warning(f"Узел {self._node_type} не имеет атрибута id")
        return -1
    
    def update_data(self, new_data: Any) -> None:
        """
        Обновляет данные узла.
        
        Args:
            new_data: Новые данные для узла
        """
        self._data = new_data
        log.debug(f"Данные узла {self._node_type} #{self.get_id()} обновлены")
    
    # ===== Приватные методы форматирования =====
    
    def _format_complex_text(self) -> str:
        """Форматирует текст для комплекса."""
        data = self._data
        if data.buildings_count > 0:
            return self._DISPLAY_FORMAT_COMPLEX_WITH_COUNT.format(
                name=data.name, 
                count=data.buildings_count
            )
        return data.name
    
    def _format_building_text(self) -> str:
        """Форматирует текст для корпуса."""
        data = self._data
        if data.floors_count > 0:
            return self._DISPLAY_FORMAT_BUILDING.format(
                name=data.name, 
                count=data.floors_count
            )
        return data.name
    
    def _format_floor_text(self) -> str:
        """Форматирует текст для этажа."""
        data = self._data
        
        # Определяем текст этажа в зависимости от номера
        if data.number < 0:
            floor_text = self._FLOOR_TEXT_BASEMENT.format(num=abs(data.number))
        elif data.number == 0:
            floor_text = self._FLOOR_TEXT_GROUND
        else:
            floor_text = self._FLOOR_TEXT_REGULAR.format(num=data.number)
        
        # Добавляем количество помещений, если есть
        if data.rooms_count > 0:
            return self._DISPLAY_FORMAT_FLOOR.format(
                text=floor_text, 
                count=data.rooms_count
            )
        return floor_text
    
    # ===== Специальные методы =====
    
    def __repr__(self) -> str:
        """Возвращает строковое представление узла."""
        return f"TreeNode({self._node_type.value}, id={self.get_id()}, loaded={self._loaded})"