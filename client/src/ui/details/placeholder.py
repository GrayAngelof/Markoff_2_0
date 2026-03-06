# client/src/ui/details/placeholder.py
"""
Виджет-заглушка для панели детальной информации.
Отображается, когда в дереве не выбран ни один объект,
предлагая пользователю сделать выбор.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional

from src.utils.logger import get_logger
log = get_logger(__name__)


class PlaceholderWidget(QWidget):
    """
    Виджет-заглушка, отображаемый при отсутствии выбранного объекта.
    
    Содержит информационное сообщение с иконкой и стилизованной рамкой.
    Занимает всю доступную область правой панели.
    """
    
    # ===== Константы =====
    
    # Текст заглушки (можно менять для разных языков)
    _DEFAULT_TEXT = "🔍 Выберите объект в дереве слева\nдля просмотра детальной информации"
    """Текст по умолчанию для заглушки"""
    
    # Стили для текста
    _LABEL_STYLESHEET = """
        QLabel {
            color: #999999;
            font-size: 14px;
            padding: 40px;
            border: 2px dashed #cccccc;
            border-radius: 10px;
            margin: 20px;
        }
    """
    """Стили для текстовой метки"""
    
    # ===== Константы размеров =====
    _PADDING = 40
    """Внутренний отступ в пикселях"""
    
    _MARGIN = 20
    """Внешний отступ в пикселях"""
    
    _BORDER_WIDTH = 2
    """Толщина пунктирной рамки в пикселях"""
    
    _BORDER_RADIUS = 10
    """Радиус скругления рамки в пикселях"""
    
    _FONT_SIZE = 14
    """Размер шрифта в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет-заглушку.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация UI
        self._init_ui()
        
        log.debug("PlaceholderWidget: инициализирован")
    
    # ===== Приватные методы =====
    
    def _init_ui(self) -> None:
        """
        Инициализирует пользовательский интерфейс заглушки.
        Создаёт layout и текстовую метку с сообщением.
        """
        # Создаём layout с центрированием
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Создаём текстовую метку
        self._message_label = self._create_message_label()
        
        # Добавляем метку в layout
        layout.addWidget(self._message_label)
        
        log.debug("PlaceholderWidget: UI инициализирован")
    
    def _create_message_label(self) -> QLabel:
        """
        Создаёт и настраивает текстовую метку с сообщением.
        
        Returns:
            QLabel: Настроенная текстовая метка
        """
        label = QLabel(self._DEFAULT_TEXT)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)  # Разрешаем перенос строк
        label.setStyleSheet(self._LABEL_STYLESHEET)
        
        return label
    
    # ===== Геттеры и сеттеры =====
    
    @property
    def message_label(self) -> QLabel:
        """
        Возвращает виджет текстовой метки.
        
        Returns:
            QLabel: Виджет с текстом сообщения
        """
        return self._message_label
    
    @property
    def current_text(self) -> str:
        """
        Возвращает текущий текст заглушки.
        
        Returns:
            str: Текст сообщения
        """
        return self._message_label.text()
    
    def set_message(self, text: str) -> None:
        """
        Устанавливает новый текст для заглушки.
        
        Args:
            text: Новый текст сообщения
        """
        self._message_label.setText(text)
        log.debug(f"PlaceholderWidget: текст изменён на '{text}'")
    
    def reset_to_default(self) -> None:
        """
        Сбрасывает текст заглушки к значению по умолчанию.
        """
        self._message_label.setText(self._DEFAULT_TEXT)
        log.debug("PlaceholderWidget: текст сброшен к значению по умолчанию")
    
    # ===== Публичные методы =====
    
    def show_message(self, message: str) -> None:
        """
        Показывает пользовательское сообщение в заглушке.
        
        Args:
            message: Текст сообщения для отображения
        """
        self.set_message(message)
        self.show()
        log.info(f"PlaceholderWidget: показано сообщение '{message}'")
    
    def show_default(self) -> None:
        """
        Показывает стандартное сообщение-заглушку.
        """
        self.reset_to_default()
        self.show()
        log.debug("PlaceholderWidget: показано сообщение по умолчанию")
    
    # ===== Методы для кастомизации внешнего вида =====
    
    def set_style_property(self, property_name: str, value: str) -> None:
        """
        Устанавливает свойство стиля для метки.
        
        Args:
            property_name: Имя свойства (например, "color", "font-size")
            value: Значение свойства
        """
        current_style = self._message_label.styleSheet()
        # Простая замена - для сложных случаев лучше использовать QSS парсер
        new_style = f"{property_name}: {value};"
        
        # Добавляем новое свойство в существующий стиль
        if current_style:
            # Удаляем старое значение если есть
            lines = current_style.split(';')
            filtered_lines = [line for line in lines if property_name not in line]
            new_style = ';'.join(filtered_lines) + ';' + new_style
        else:
            new_style = self._LABEL_STYLESHEET + ';' + new_style
        
        self._message_label.setStyleSheet(new_style)
        log.debug(f"PlaceholderWidget: стиль обновлён - {property_name}: {value}")