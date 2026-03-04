# client/src/ui/details_panel.py
"""
Правая панель с детальной информацией о выбранном объекте
В текущей версии - заглушка, но реагирует на выбор элемента
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Slot

class DetailsPanel(QWidget):
    """
    Панель детальной информации
    
    В текущей версии:
    - Показывает информацию о выбранном объекте
    - В будущем будет содержать вкладки с разными данными
    """
    
    def __init__(self):
        """Инициализация панели информации"""
        super().__init__()
        
        # Создаём layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаём заголовок
        title = QLabel("Информация об объекте")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #c0c0c0;
            }
        """)
        layout.addWidget(title)
        
        # Создаём контейнер для контента
        self.content = QVBoxLayout()
        
        # Метка для отображения выбранного объекта
        self.selection_label = QLabel("Выберите объект в дереве слева\nдля просмотра детальной информации")
        self.selection_label.setAlignment(Qt.AlignCenter)
        self.selection_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px dashed #c0c0c0;
                margin: 10px;
                padding: 20px;
                color: #808080;
            }
        """)
        
        layout.addWidget(self.selection_label)
        
        # Метка для будущей информации
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignTop)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                margin: 10px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.info_label)
        
        # Добавляем растяжение в конце
        layout.addStretch()
        
        # Текущий выбранный объект
        self.current_type = None
        self.current_id = None
        
        print("✅ DetailsPanel: создана")
    
    @Slot(str, int)
    def show_item_details(self, item_type: str, item_id: int):
        """
        Показывает информацию о выбранном объекте
        
        Args:
            item_type: тип элемента ('complex', 'building', 'floor', 'room')
            item_id: идентификатор элемента
        """
        # Сохраняем текущий объект
        self.current_type = item_type
        self.current_id = item_id
        
        # Показываем, что объект выбран
        self.selection_label.setText(f"Выбран объект: {item_type} #{item_id}")
        
        # Здесь позже будем загружать детальную информацию с сервера
        self.info_label.setText(
            f"Тип: {item_type}\n"
            f"ID: {item_id}\n\n"
            f"Детальная информация будет загружена\n"
            f"в следующих версиях приложения"
        )
        
        print(f"📋 Показана информация для {item_type} #{item_id}")
    
    def clear(self):
        """
        Очистить панель (сбросить к начальному состоянию)
        """
        self.current_type = None
        self.current_id = None
        
        self.selection_label.setText("Выберите объект в дереве слева\nдля просмотра детальной информации")
        self.info_label.setText("")
        
        print("🧹 DetailsPanel: очищена")
    
    def get_current_selection(self):
        """
        Получить текущий выбранный объект
        
        Returns:
            tuple: (item_type, item_id) или (None, None)
        """
        return self.current_type, self.current_id