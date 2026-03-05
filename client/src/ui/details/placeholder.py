# client/src/ui/details/placeholder.py
"""
Виджет-заглушка для панели детальной информации
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class PlaceholderWidget(QWidget):
    """
    Заглушка, показываемая когда ничего не выбрано
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("🔍 Выберите объект в дереве слева\nдля просмотра детальной информации")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 14px;
                padding: 40px;
                border: 2px dashed #cccccc;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        
        layout.addWidget(self.label)