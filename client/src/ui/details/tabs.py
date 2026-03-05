# client/src/ui/details/tabs.py
"""
Вкладки для панели детальной информации
"""
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class DetailsTabs(QTabWidget):
    """
    Вкладки: Физика, Юрики, Пожарка
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                padding: 5px;
                margin-top: 5px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        self._create_tabs()
    
    def _create_tabs(self):
        """Создание всех вкладок"""
        # Вкладка Физика
        physics_tab = QWidget()
        physics_layout = QVBoxLayout(physics_tab)
        physics_label = QLabel("📊 Статистика по физике будет здесь")
        physics_label.setAlignment(Qt.AlignCenter)
        physics_label.setStyleSheet("color: #808080; padding: 40px;")
        physics_layout.addWidget(physics_label)
        self.addTab(physics_tab, "📊 Физика")
        
        # Вкладка Юрики
        legal_tab = QWidget()
        legal_layout = QVBoxLayout(legal_tab)
        legal_label = QLabel("⚖️ Информация о юридических лицах будет здесь")
        legal_label.setAlignment(Qt.AlignCenter)
        legal_label.setStyleSheet("color: #808080; padding: 40px;")
        legal_layout.addWidget(legal_label)
        self.addTab(legal_tab, "⚖️ Юрики")
        
        # Вкладка Пожарка
        fire_tab = QWidget()
        fire_layout = QVBoxLayout(fire_tab)
        fire_label = QLabel("🔥 Данные пожарной безопасности будут здесь")
        fire_label.setAlignment(Qt.AlignCenter)
        fire_label.setStyleSheet("color: #808080; padding: 40px;")
        fire_layout.addWidget(fire_label)
        self.addTab(fire_tab, "🔥 Пожарка")