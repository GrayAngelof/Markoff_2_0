# client/src/ui/details/details_panel.py
"""
Основной класс панели детальной информации.
Объединяет все компоненты для отображения информации о выбранном объекте.
Теперь поддерживает отображение владельцев и контактных лиц.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Slot
from typing import Optional, Tuple, Any, Dict, List

from src.ui.details.base_panel import DetailsPanelBase
from src.ui.details.display_handlers import DisplayHandlers
from src.ui.details.contact_list_widget import ContactListWidget
from src.ui.details.field_manager import FieldManager
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson

from utils.logger import get_logger
log = get_logger(__name__)


class DetailsPanel(DetailsPanelBase):
    """
    Панель детальной информации для отображения данных о выбранном объекте.
    
    Новые возможности:
    - Отображение информации о владельце для корпусов
    - Список контактных лиц с группировкой по категориям
    - Банковские реквизиты контрагентов
    """
    
    def __init__(self, parent=None) -> None:
        """Инициализирует панель детальной информации."""
        super().__init__(parent)
        
        # Добавляем виджет контактов в третью вкладку
        self._contact_widget = ContactListWidget()
        self.tabs.addTab(self._contact_widget, "👥 Контакты")
        
        # Для четвёртой вкладки (если нужны банковские реквизиты)
        self._bank_widget = QWidget()
        bank_layout = QVBoxLayout(self._bank_widget)
        self._bank_label = QLabel()
        self._bank_label.setWordWrap(True)
        self._bank_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bank_layout.addWidget(self._bank_label)
        bank_layout.addStretch()
        self.tabs.addTab(self._bank_widget, "💰 Банк")
        
        self._bus = None  # будет установлен извне
        self._current_owner: Optional[Counterparty] = None
        self._current_persons: List[ResponsiblePerson] = []
        self._current_context: Dict[str, Any] = {}
        
        log.success("DetailsPanel: создана (расширенная версия)")
    
    def set_event_bus(self, bus):
        """Устанавливает шину событий и подписывается."""
        log.debug(f"🔍 DetailsPanel.set_event_bus вызван с bus={bus}")
        self._bus = bus
        log.debug("🔍 DetailsPanel: Подписываемся на ui.node_selected")
        self._bus.subscribe('ui.node_selected', self._on_node_selected_event)
        log.debug("🔍 Подписываемся на ui.node_details_loaded")
        self._bus.subscribe('ui.node_details_loaded', self._on_details_loaded_event)
        log.debug(f"DetailsPanel: подписана на события (подписок: ui.node_selected, ui.node_details_loaded)")
        log.debug(f"DetailsPanel: self._bus = {self._bus}")
    
    def _on_node_selected_event(self, event: dict) -> None:
        """
        Обрабатывает событие выбора узла через EventBus.
        Сразу устанавливает текущий узел и показывает имеющиеся данные.
        """
        data = event['data']
        node_type_obj = data['node_type']
        node_id = data['node_id']
        node_data = data.get('data')
        
        # Преобразуем node_type в строку если это NodeType
        if hasattr(node_type_obj, 'value'):
            node_type_str = node_type_obj.value
        else:
            node_type_str = str(node_type_obj)
        
        # ИСПРАВЛЕНО: СРАЗУ устанавливаем текущий узел ДО вызова show_item_details
        self._current_type = node_type_str
        self._current_id = node_id
        self._current_data = node_data
        
        log.debug(f"🔥 Установлен текущий узел: {node_type_str}#{node_id}")
        
        # Вызываем существующий метод с текущими данными (могут быть неполными)
        self.show_item_details(node_type_str, node_id, node_data, {})
    
    def _on_details_loaded_event(self, event: dict) -> None:
        """
        Обрабатывает событие загрузки деталей узла.
        Обновляет отображение, если это текущий узел.
        """
        data = event['data']
        node_type = data['node_type']
        node_id = data['node_id']
        node_data = data['data']
        context = data.get('context', {})
        
        log.debug(f"🔥 Получены детали для {node_type}#{node_id}")
        
        # ИСПРАВЛЕНО: всегда обновляем, если это текущий узел
        if node_type == self._current_type and node_id == self._current_id:
            log.info(f"🔥 Обновление панели деталями для {node_type}#{node_id}")
            self.show_item_details(node_type, node_id, node_data, context)
        else:
            log.debug(f"🔥 Детали для другого узла: текущий {self._current_type}#{self._current_id}, получен {node_type}#{node_id}")
    
    # ===== Публичные методы =====
    
    @Slot(str, int, object, dict)
    def show_item_details(self, item_type: str, item_id: int, 
                          item_data: Any, context: Dict[str, Any]) -> None:
        """
        Показывает информацию о выбранном объекте с учётом контекста.
        """
        # Сохраняем информацию о выбранном объекте
        self._current_type = item_type
        self._current_id = item_id
        self._current_data = item_data
        self._current_context = context
        
        log.info(f"DetailsPanel: выбран {item_type} #{item_id}")
        log.debug(f"DetailsPanel: контекст: {context}")
        
        # Скрываем заглушку
        self.placeholder.hide()
        
        # Очищаем поля
        self.clear_all_fields()
        self._contact_widget.set_contacts([])
        self._bank_label.setText("")
        
        # Отображаем соответствующий тип с контекстом
        self._display_by_type(item_type, item_data, context)
    
    @Slot(dict)
    def update_owner_info(self, data: Dict) -> None:
        """
        Обновляет информацию о владельце для текущего корпуса.
        
        Args:
            data: Словарь с данными владельца
        """
        if self._current_type != 'building':
            return
        
        owner = data.get('owner')
        persons = data.get('responsible_persons', [])
        context = data.get('context', {})
        
        if not owner:
            return
        
        self._current_owner = owner
        self._current_persons = persons if persons else []
        
        log.info(f"Обновление информации о владельце для корпуса {self._current_id}")
        
        # Добавляем информацию о владельце в сетку
        owner_details = FieldManager.format_counterparty_details(owner)
        
        # Добавляем поля владельца
        self.info_grid.set_field("owner_name", owner_details.get('name', ''))
        self.info_grid.set_field("owner_inn", owner_details.get('inn', ''))
        self.info_grid.set_field("owner_legal", owner_details.get('legal_address', ''))
        self.info_grid.set_field("owner_actual", owner_details.get('actual_address', ''))
        
        # Показываем дополнительные поля
        self.info_grid.show_only(
            "address", "description", "plan",
            "owner_name", "owner_inn", "owner_legal", "owner_actual"
        )
        
        # Обновляем контакты и банк
        self._contact_widget.set_contacts(self._current_persons)
        self._bank_label.setText(owner_details.get('bank_details', ''))
        
        # Переключаемся на вкладку с контактами если нужно
        # self.tabs.setCurrentIndex(2)
    
    def _display_by_type(self, item_type: str, item_data: Any, context: Dict[str, Any]) -> None:
        """Отображает данные в зависимости от типа объекта."""
        if item_type == 'complex' and isinstance(item_data, Complex):
            DisplayHandlers.show_complex(self, item_data)
            
        elif item_type == 'building' and isinstance(item_data, Building):
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            DisplayHandlers.show_building(self, item_data, complex_name)
            
        elif item_type == 'floor' and isinstance(item_data, Floor):
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            DisplayHandlers.show_floor(self, item_data, building_name, complex_name)
            
        elif item_type == 'room' and isinstance(item_data, Room):
            floor_num = context.get('floor_num', 0)
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            DisplayHandlers.show_room(self, item_data, floor_num, building_name, complex_name)
            
        else:
            log.warning(f"DetailsPanel: неизвестный тип объекта '{item_type}'")
            self._reset_panel()
    
    def _reset_panel(self) -> None:
        """Сбрасывает панель в исходное состояние."""
        # Вызываем метод базового класса для очистки (если он есть)
        if hasattr(super(), 'clear'):
            super().clear()  # type: ignore
        
        self._contact_widget.set_contacts([])
        self._bank_label.setText("")
        self._current_owner = None
        self._current_persons = []
        self._current_context = {}
        
        log.debug("DetailsPanel: сброшена")
    
    def clear(self) -> None:
        """Переопределяем метод clear из базового класса."""
        self._reset_panel()