# client/src/ui/details/header_widget.py
"""
Виджет шапки для панели детальной информации.
Содержит иконку объекта, заголовок, статус и строку иерархии.
Обеспечивает единообразное отображение верхней части панели для всех типов объектов.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional, Dict

from src.utils.logger import get_logger
log = get_logger(__name__)


class HeaderWidget(QWidget):
    """
    Шапка панели детальной информации.
    
    Состоит из двух строк:
    - Верхняя строка: иконка, заголовок, статус
    - Нижняя строка: иерархия (в составе...)
    
    Предоставляет методы для установки заголовка, статуса, иерархии
    и изменения внешнего вида статуса в зависимости от его значения.
    """
    
    # ===== Константы =====
    
    # Стили для всего виджета
    _WIDGET_STYLESHEET = """
        QWidget {
            background-color: #f5f5f5;
            border-bottom: 2px solid #d0d0d0;
        }
    """
    """Общий стиль виджета"""
    
    # Стили для иконки
    _ICON_STYLESHEET = "font-size: 24px;"
    """Стиль для иконки объекта"""
    
    # Базовый стиль для статуса
    _STATUS_BASE_STYLE = "padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;"
    """Базовая часть стиля статуса (без цвета)"""
    
    # Стили для разных статусов
    _STATUS_STYLES: Dict[str, str] = {
        'free': _STATUS_BASE_STYLE + "background-color: #c8e6c9; color: #2e7d32;",
        'occupied': _STATUS_BASE_STYLE + "background-color: #ffcdd2; color: #c62828;",
        'reserved': _STATUS_BASE_STYLE + "background-color: #fff9c4; color: #f57f17;",
        'maintenance': _STATUS_BASE_STYLE + "background-color: #ffecb3; color: #ff6f00;",
    }
    """Словарь стилей для каждого статуса"""
    
    _STATUS_DEFAULT_STYLE = _STATUS_BASE_STYLE + "background-color: #e0e0e0;"
    """Стиль по умолчанию для неизвестного статуса"""
    
    # Стиль для иерархии
    _HIERARCHY_STYLESHEET = "color: #666666; font-size: 11px;"
    """Стиль для текста иерархии"""
    
    # ===== Константы размеров =====
    _HEADER_HEIGHT = 80
    """Высота шапки в пикселях"""
    
    _CONTENT_MARGINS = (15, 5, 15, 5)
    """Отступы содержимого (слева, сверху, справа, снизу)"""
    
    _ICON_FONT_SIZE = 24
    """Размер шрифта для иконки в пикселях"""
    
    _TITLE_FONT_SIZE = 16
    """Размер шрифта для заголовка в пикселях"""
    
    _STATUS_FONT_SIZE = 12
    """Размер шрифта для статуса в пикселях"""
    
    _HIERARCHY_FONT_SIZE = 11
    """Размер шрифта для иерархии в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет шапки.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Настройка внешнего вида
        self._setup_appearance()
        
        # Создание UI
        self._init_ui()
        
        log.debug("HeaderWidget: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _setup_appearance(self) -> None:
        """
        Настраивает внешний вид виджета: стили и размер.
        """
        self.setStyleSheet(self._WIDGET_STYLESHEET)
        self.setFixedHeight(self._HEADER_HEIGHT)
    
    def _init_ui(self) -> None:
        """
        Инициализирует пользовательский интерфейс шапки.
        Создаёт layout, верхнюю и нижнюю строки.
        """
        # Основной вертикальный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*self._CONTENT_MARGINS)
        
        # Верхняя строка: иконка + заголовок + статус
        top_row = self._create_top_row()
        layout.addLayout(top_row)
        
        # Нижняя строка: иерархия
        self._hierarchy_label = self._create_hierarchy_label()
        layout.addWidget(self._hierarchy_label)
        
        log.debug("HeaderWidget: UI инициализирован")
    
    def _create_top_row(self) -> QHBoxLayout:
        """
        Создаёт верхнюю строку с иконкой, заголовком и статусом.
        
        Returns:
            QHBoxLayout: Layout верхней строки
        """
        top_row = QHBoxLayout()
        
        # Иконка
        self._icon_label = self._create_icon_label()
        top_row.addWidget(self._icon_label)
        
        # Заголовок (растягивается)
        self._title_label = self._create_title_label()
        top_row.addWidget(self._title_label, 1)
        
        # Статус
        self._status_label = self._create_status_label()
        top_row.addWidget(self._status_label)
        
        return top_row
    
    def _create_icon_label(self) -> QLabel:
        """
        Создаёт метку для иконки объекта.
        
        Returns:
            QLabel: Настроенная метка для иконки
        """
        label = QLabel("🏢")  # Иконка по умолчанию
        label.setStyleSheet(self._ICON_STYLESHEET)
        return label
    
    def _create_title_label(self) -> QLabel:
        """
        Создаёт метку для заголовка.
        
        Returns:
            QLabel: Настроенная метка для заголовка
        """
        label = QLabel("")
        
        # Настройка шрифта
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(self._TITLE_FONT_SIZE)
        label.setFont(title_font)
        
        return label
    
    def _create_status_label(self) -> QLabel:
        """
        Создаёт метку для статуса.
        
        Returns:
            QLabel: Настроенная метка для статуса
        """
        label = QLabel("")
        label.setStyleSheet(self._STATUS_DEFAULT_STYLE)
        return label
    
    def _create_hierarchy_label(self) -> QLabel:
        """
        Создаёт метку для отображения иерархии.
        
        Returns:
            QLabel: Настроенная метка для иерархии
        """
        label = QLabel("")
        label.setStyleSheet(self._HIERARCHY_STYLESHEET)
        label.setWordWrap(True)
        return label
    
    # ===== Геттеры =====
    
    @property
    def icon_label(self) -> QLabel:
        """
        Возвращает виджет иконки.
        
        Returns:
            QLabel: Виджет с иконкой
        """
        return self._icon_label
    
    @property
    def title_label(self) -> QLabel:
        """
        Возвращает виджет заголовка.
        
        Returns:
            QLabel: Виджет с заголовком
        """
        return self._title_label
    
    @property
    def status_label(self) -> QLabel:
        """
        Возвращает виджет статуса.
        
        Returns:
            QLabel: Виджет со статусом
        """
        return self._status_label
    
    @property
    def hierarchy_label(self) -> QLabel:
        """
        Возвращает виджет иерархии.
        
        Returns:
            QLabel: Виджет с текстом иерархии
        """
        return self._hierarchy_label
    
    # ===== Публичные методы =====
    
    def set_title(self, title: str) -> None:
        """
        Устанавливает заголовок.
        
        Args:
            title: Текст заголовка
        """
        self._title_label.setText(title)
        log.debug(f"HeaderWidget: заголовок установлен '{title}'")
    
    def set_icon(self, icon: str) -> None:
        """
        Устанавливает иконку.
        
        Args:
            icon: Символ иконки (эмодзи)
        """
        self._icon_label.setText(icon)
        log.debug(f"HeaderWidget: иконка установлена '{icon}'")
    
    def set_status(self, status: str) -> None:
        """
        Устанавливает текст статуса.
        
        Args:
            status: Текст статуса
        """
        self._status_label.setText(status)
        log.debug(f"HeaderWidget: статус установлен '{status}'")
    
    def set_hierarchy(self, hierarchy: str) -> None:
        """
        Устанавливает текст иерархии.
        
        Args:
            hierarchy: Текст иерархии (например, "в составе корпуса...")
        """
        self._hierarchy_label.setText(hierarchy)
        log.debug(f"HeaderWidget: иерархия установлена '{hierarchy}'")
    
    def set_status_style(self, status_code: Optional[str]) -> None:
        """
        Устанавливает стиль статуса в зависимости от кода.
        
        Args:
            status_code: Код статуса ('free', 'occupied', 'reserved', 'maintenance' или None)
        """
        style = self._STATUS_STYLES.get(status_code, self._STATUS_DEFAULT_STYLE)
        self._status_label.setStyleSheet(style)
        
        status_text = status_code if status_code else "default"
        log.debug(f"HeaderWidget: стиль статуса '{status_text}' применён")
    
    def clear(self) -> None:
        """
        Очищает все поля шапки.
        """
        self._title_label.setText("")
        self._icon_label.setText("🏢")  # Возвращаем иконку по умолчанию
        self._status_label.setText("")
        self._status_label.setStyleSheet(self._STATUS_DEFAULT_STYLE)
        self._hierarchy_label.setText("")
        
        log.debug("HeaderWidget: очищен")
    
    # ===== Методы для кастомизации =====
    
    def set_status_style_custom(self, stylesheet: str) -> None:
        """
        Устанавливает произвольный стиль для статуса.
        
        Args:
            stylesheet: QSS строка со стилями
        """
        self._status_label.setStyleSheet(stylesheet)
        log.debug("HeaderWidget: применён пользовательский стиль статуса")