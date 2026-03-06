# client/src/ui/details/details_panel.py
"""
Основной класс панели детальной информации.
Объединяет все компоненты для отображения информации о выбранном объекте:
- Шапка с иерархией
- Сетка с полями информации
- Вкладки для дополнительных данных
"""
from PySide6.QtCore import Slot
from typing import Optional, Tuple, Any, Dict, List

from src.ui.details.base_panel import DetailsPanelBase
from src.ui.details.display_handlers import DisplayHandlers
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room

from src.utils.logger import get_logger
log = get_logger(__name__)


class DetailsPanel(DetailsPanelBase):
    """
    Панель детальной информации для отображения данных о выбранном объекте.
    
    Особенности:
    - Автоматически подстраивается под тип объекта
    - Использует контекст иерархии для построения правильной цепочки
    - Скрывает заглушку и показывает информацию при выборе объекта
    - Очищается при отсутствии выбора
    
    Поддерживаемые типы объектов:
    - complex (комплекс)
    - building (корпус)
    - floor (этаж)
    - room (помещение)
    """
    
    # ===== Константы =====
    
    _UNKNOWN_COMPLEX = "Неизвестный комплекс"
    """Текст для неизвестного комплекса в контексте"""
    
    _UNKNOWN_BUILDING = "Неизвестный корпус"
    """Текст для неизвестного корпуса в контексте"""
    
    _DEFAULT_FLOOR_NUM = 0
    """Номер этажа по умолчанию"""
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует панель детальной информации.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        log.success("DetailsPanel: создана")
    
    # ===== Приватные методы =====
    
    def _log_hierarchy(self, item_type: str, hierarchy_text: str) -> None:
        """
        Логирует информацию об иерархии для отладки.
        
        Args:
            item_type: Тип объекта
            hierarchy_text: Текст иерархии
        """
        log.debug(f"DetailsPanel: [{item_type}] иерархия: {hierarchy_text}")
    
    def _log_visible_fields(self) -> None:
        """Логирует список видимых полей для отладки."""
        visible = self.info_grid.get_visible_fields()
        log.debug(f"DetailsPanel: видимые поля: {sorted(visible)}")
    
    def _validate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет и дополняет контекст значениями по умолчанию.
        
        Args:
            context: Исходный контекст
            
        Returns:
            Dict[str, Any]: Проверенный контекст с заполненными пропусками
        """
        validated = context.copy() if context else {}
        
        # Устанавливаем значения по умолчанию для отсутствующих ключей
        if 'complex_name' not in validated or validated['complex_name'] is None:
            validated['complex_name'] = self._UNKNOWN_COMPLEX
            
        if 'building_name' not in validated or validated['building_name'] is None:
            validated['building_name'] = self._UNKNOWN_BUILDING
            
        if 'floor_num' not in validated or validated['floor_num'] is None:
            validated['floor_num'] = self._DEFAULT_FLOOR_NUM
        
        return validated
    
    # ===== Публичные методы =====
    
    @Slot(str, int, object, dict)
    def show_item_details(self, item_type: str, item_id: int, 
                          item_data: Any, context: Dict[str, Any]) -> None:
        """
        Показывает информацию о выбранном объекте с учётом контекста.
        
        Args:
            item_type: Тип элемента ('complex', 'building', 'floor', 'room')
            item_id: Идентификатор элемента
            item_data: Объект модели (Complex, Building, Floor или Room)
            context: Словарь с именами родительских узлов
        """
        # Сохраняем информацию о выбранном объекте
        self._current_type = item_type
        self._current_id = item_id
        self._current_data = item_data
        
        # Логируем полученные данные
        log.info(f"DetailsPanel: выбран {item_type} #{item_id}")
        log.debug(f"DetailsPanel: контекст: {context}")
        
        # Проверяем и дополняем контекст
        validated_context = self._validate_context(context)
        
        # Скрываем заглушку
        self.placeholder.hide()
        
        # Очищаем поля
        self.clear_all_fields()
        
        # Отображаем соответствующий тип с контекстом
        self._display_by_type(item_type, item_data, validated_context)
        
        # Логируем результат для отладки
        self._log_visible_fields()
    
    def _display_by_type(self, item_type: str, item_data: Any, context: Dict[str, Any]) -> None:
        """
        Отображает данные в зависимости от типа объекта.
        
        Args:
            item_type: Тип объекта
            item_data: Данные объекта
            context: Контекст иерархии
        """
        if item_type == 'complex' and isinstance(item_data, Complex):
            DisplayHandlers.show_complex(self, item_data)
            
        elif item_type == 'building' and isinstance(item_data, Building):
            complex_name = context.get('complex_name', self._UNKNOWN_COMPLEX)
            DisplayHandlers.show_building(self, item_data, complex_name)
            
        elif item_type == 'floor' and isinstance(item_data, Floor):
            building_name = context.get('building_name', self._UNKNOWN_BUILDING)
            complex_name = context.get('complex_name', self._UNKNOWN_COMPLEX)
            DisplayHandlers.show_floor(self, item_data, building_name, complex_name)
            
        elif item_type == 'room' and isinstance(item_data, Room):
            floor_num = context.get('floor_num', self._DEFAULT_FLOOR_NUM)
            building_name = context.get('building_name', self._UNKNOWN_BUILDING)
            complex_name = context.get('complex_name', self._UNKNOWN_COMPLEX)
            DisplayHandlers.show_room(self, item_data, floor_num, building_name, complex_name)
            
        else:
            log.warning(f"DetailsPanel: неизвестный тип объекта '{item_type}'")
            self.clear()
    
    def clear(self) -> None:
        """Очищает панель и показывает заглушку."""
        self._current_type = None
        self._current_id = None
        self._current_data = None
        
        # Скрываем сетку, показываем заглушку
        self.hide_info_grid()
        
        # Очищаем заголовки
        self.title_label.setText("")
        self.hierarchy_label.setText("")
        self.status_label.setText("")
        self.icon_label.setText(DisplayHandlers.ICON_COMPLEX)
        
        log.debug("DetailsPanel: очищена")
    
    def get_current_selection(self) -> Tuple[Optional[str], Optional[int], Optional[Any]]:
        """
        Возвращает информацию о текущем выбранном объекте.
        
        Returns:
            Tuple[Optional[str], Optional[int], Optional[Any]]:
            (тип, идентификатор, данные) или (None, None, None)
        """
        return self._current_type, self._current_id, self._current_data
    
    def is_object_selected(self) -> bool:
        """
        Проверяет, выбран ли какой-либо объект.
        
        Returns:
            bool: True если объект выбран
        """
        return self._current_type is not None and self._current_id is not None
    
    def get_current_type(self) -> Optional[str]:
        """
        Возвращает тип текущего выбранного объекта.
        
        Returns:
            Optional[str]: Тип объекта или None
        """
        return self._current_type
    
    def get_current_id(self) -> Optional[int]:
        """
        Возвращает ID текущего выбранного объекта.
        
        Returns:
            Optional[int]: ID объекта или None
        """
        return self._current_id
    
    def get_current_data(self) -> Optional[Any]:
        """
        Возвращает данные текущего выбранного объекта.
        
        Returns:
            Optional[Any]: Объект модели или None
        """
        return self._current_data