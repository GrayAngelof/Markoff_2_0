# client/src/ui/details/info_grid.py
"""
Сетка с полями информации для панели деталей
"""
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtCore import Qt


class InfoGrid(QWidget):
    """
    Сетка с парами "Лейбл: Значение"
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.grid = QGridLayout(self)
        self.grid.setVerticalSpacing(8)
        self.grid.setHorizontalSpacing(20)
        self.grid.setColumnStretch(1, 1)
        
        self.fields = {}
        self._create_fields()
    
    def _create_fields(self):
        """Создание всех возможных полей"""
        field_names = [
            ("address", "Адрес:"),
            ("owner", "Владелец:"),
            ("tenant", "Арендатор:"),
            ("description", "Описание:"),
            ("plan", "Планировка:"),
            ("type", "Тип:"),
            ("contract", "Договор:"),
            ("valid_until", "Действует до:"),
            ("rent", "Арендная плата:"),
        ]
        
        for i, (key, label) in enumerate(field_names):
            # Лейбл
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #666666;")
            label_widget.setAlignment(Qt.AlignRight | Qt.AlignTop)
            
            # Значение
            value_widget = QLabel("—")
            value_widget.setWordWrap(True)
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            self.grid.addWidget(label_widget, i, 0)
            self.grid.addWidget(value_widget, i, 1)
            
            self.fields[key] = value_widget
    
    def clear_all(self):
        """Очистить все поля"""
        for field in self.fields.values():
            field.setText("—")
    
    def set_field(self, key: str, value):
        """Установить значение поля с проверкой"""
        if key not in self.fields:
            return
        
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self.fields[key].setText("—")
        else:
            self.fields[key].setText(str(value))
    
    def show_only(self, *keys):
        """Показать только указанные поля"""
        # Сначала скрываем все
        for field in self.fields.values():
            field.parent().hide()
        
        # Показываем нужные
        for key in keys:
            if key in self.fields:
                self.fields[key].parent().show()