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
from src.data.entity_graph import EntityGraph  # <-- ДОБАВЛЕНО для типизации

from utils.logger import get_logger


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
        _graph: Ссылка на граф сущностей (для проверки наличия детей)
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
        self._graph: Optional[EntityGraph] = None  # <-- ДОБАВЛЕНО
        
        log.debug(f"TreeNode создан: {node_type} id={self.get_id()}")
    
    def set_graph(self, graph: EntityGraph) -> None:
        """Устанавливает ссылку на граф сущностей."""
        self._graph = graph
        log.debug(f"Граф установлен для узла {self._node_type} #{self.get_id()}")
    
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
        """
        # Определяем тип как строку
        if isinstance(self._node_type, NodeType):
            type_str = self._node_type.value
            log.debug(f"get_display_text для enum: {type_str}")
        else:
            type_str = str(self._node_type)
            log.debug(f"get_display_text для строки: {type_str}")
        
        # Форматируем в зависимости от типа
        if type_str == 'complex':
            return self._format_complex_text()
        elif type_str == 'building':
            return self._format_building_text()
        elif type_str == 'floor':
            return self._format_floor_text()
        elif type_str == 'room':
            return self._format_room_text()
        
        log.warning(f"Неизвестный тип узла: {type_str}")
        return str(self._data) if self._data else self._UNKNOWN_TEXT
    
    def _format_room_text(self) -> str:
        """Форматирует текст для помещения."""
        data = self._data
        if data is None:
            return self._UNKNOWN_TEXT
        return data.number

    def get_id(self) -> int:
        """
        Возвращает идентификатор узла.
        
        Returns:
            ID узла или -1, если идентификатор отсутствует
        """
        # Для корневого узла data может быть None
        if self._data is None:
            return -1
        
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
        if data is None:
            return self._UNKNOWN_TEXT
        
        # Пробуем получить buildings_count разными способами
        buildings_count = getattr(data, 'buildings_count', 0)
        
        # Проверяем, есть ли уже загруженные корпуса в графе
        # (для показа стрелочки даже если счётчик временно 0)
        if self._graph:
            from src.data.entity_types import COMPLEX
            children = self._graph.get_children(COMPLEX, self.get_id())
            if children:
                return f"{data.name} ({len(children)})"
        
        # Если есть счётчик в данных - используем его
        if buildings_count and buildings_count > 0:
            return self._DISPLAY_FORMAT_COMPLEX_WITH_COUNT.format(
                name=data.name, 
                count=buildings_count
            )
        
        # По умолчанию - просто название
        return data.name
    
    def _format_building_text(self) -> str:
        """Форматирует текст для корпуса."""
        data = self._data
        if data is None:
            return self._UNKNOWN_TEXT
        
        floors_count = getattr(data, 'floors_count', 0)
        if floors_count > 0:
            return self._DISPLAY_FORMAT_BUILDING.format(
                name=data.name, 
                count=floors_count
            )
        return data.name
    
    def _format_floor_text(self) -> str:
        """Форматирует текст для этажа."""
        data = self._data
        if data is None:
            return self._UNKNOWN_TEXT
        
        # Определяем текст этажа в зависимости от номера
        if data.number < 0:
            floor_text = self._FLOOR_TEXT_BASEMENT.format(num=abs(data.number))
        elif data.number == 0:
            floor_text = self._FLOOR_TEXT_GROUND
        else:
            floor_text = self._FLOOR_TEXT_REGULAR.format(num=data.number)
        
        # Добавляем количество помещений, если есть
        rooms_count = getattr(data, 'rooms_count', 0)
        if rooms_count > 0:
            return self._DISPLAY_FORMAT_FLOOR.format(
                text=floor_text, 
                count=rooms_count
            )
        return floor_text
    
    # ===== Специальные методы =====
    
    def __repr__(self) -> str:
        """Возвращает строковое представление узла."""
        return f"TreeNode({self._node_type.value}, id={self.get_id()}, loaded={self._loaded})"