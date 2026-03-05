# client/src/ui/details/header_widget.py
"""
Виджет шапки для панели детальной информации
Содержит иконку, заголовок, статус и строку иерархии
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class HeaderWidget(QWidget):
    """
    Шапка панели с иерархией
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 2px solid #d0d0d0;
            }
        """)
        self.setFixedHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Верхняя строка: иконка + заголовок + статус
        top_row = QHBoxLayout()
        
        self.icon_label = QLabel("🏢")
        self.icon_label.setStyleSheet("font-size: 24px;")
        top_row.addWidget(self.icon_label)
        
        self.title_label = QLabel("")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)
        top_row.addWidget(self.title_label, 1)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 4px 12px;
                border-radius: 12px;
                background-color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        top_row.addWidget(self.status_label)
        
        layout.addLayout(top_row)
        
        # Нижняя строка: иерархия
        self.hierarchy_label = QLabel("")
        self.hierarchy_label.setStyleSheet("color: #666666; font-size: 11px;")
        self.hierarchy_label.setWordWrap(True)
        layout.addWidget(self.hierarchy_label)
    
    def set_status_style(self, status: str):
        """Установка стиля статуса"""
        base_style = "padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;"
        
        styles = {
            'free': base_style + "background-color: #c8e6c9; color: #2e7d32;",
            'occupied': base_style + "background-color: #ffcdd2; color: #c62828;",
            'reserved': base_style + "background-color: #fff9c4; color: #f57f17;",
            'maintenance': base_style + "background-color: #ffecb3; color: #ff6f00;",
        }
        self.status_label.setStyleSheet(styles.get(status, base_style + "background-color: #e0e0e0;"))