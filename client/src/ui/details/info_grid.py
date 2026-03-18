# client/src/ui/details/info_grid.py
"""
Сетка с полями информации для панели деталей.
Добавлена поддержка многострочных полей и групп.
"""
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from typing import Dict, List, Optional, Tuple, Any

from utils.logger import get_logger

log = get_logger(__name__)


class InfoGrid(QWidget):
    """
    Сетка для отображения информации в формате "Лейбл: Значение".
    
    Предоставляет:
    - Динамическое создание полей
    - Многострочные значения с переносом
    - Группы полей с разделителями
    - Доступ к полям через словарь
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует сетку информации."""
        super().__init__(parent)
        
        self._grid = QGridLayout(self)
        self._grid.setVerticalSpacing(8)
        self._grid.setHorizontalSpacing(20)
        self._grid.setColumnStretch(1, 1)
        
        # Словари для хранения виджетов
        self._label_widgets: Dict[str, QLabel] = {}  # лейблы
        self._value_widgets: Dict[str, QLabel] = {}  # значения
        self._current_row = 0
        
        log.debug("InfoGrid: инициализирована")
    
    # ===== Свойства для доступа =====
    
    @property
    def fields(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь всех полей значений.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_значения}
        """
        return self._value_widgets.copy()
    
    @property
    def labels(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь всех лейблов.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_лейбла}
        """
        return self._label_widgets.copy()
    
    # ===== Управление полями =====
    
    def add_field(self, key: str, label_text: str, value: Optional[str] = None) -> None:
        """
        Добавляет новое поле в сетку.
        
        Args:
            key: Ключ поля
            label_text: Текст лейбла
            value: Начальное значение (опционально)
        """
        if key in self._value_widgets:
            log.warning(f"Поле '{key}' уже существует, обновляем значение")
            self.set_field(key, value)
            return
        
        # Создаём лейбл
        label_widget = QLabel(label_text)
        label_widget.setStyleSheet("font-weight: bold; color: #666666;")
        # ИСПРАВЛЕНО: используем правильные константы Qt
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        # Создаём поле значения
        value_widget = QLabel(value or "—")
        value_widget.setWordWrap(True)
        # ИСПРАВЛЕНО: используем правильные константы Qt
        value_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Добавляем в сетку
        self._grid.addWidget(label_widget, self._current_row, 0)
        self._grid.addWidget(value_widget, self._current_row, 1)
        
        # Сохраняем
        self._label_widgets[key] = label_widget
        self._value_widgets[key] = value_widget
        
        self._current_row += 1
        
        log.debug(f"Добавлено поле '{key}'")
    
    def add_separator(self) -> None:
        """Добавляет разделитель между группами полей."""
        separator = QFrame()
        # ИСПРАВЛЕНО: используем правильные константы QFrame
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #cccccc;")
        
        self._grid.addWidget(separator, self._current_row, 0, 1, 2)
        self._current_row += 1
    
    def set_field(self, key: str, value: Optional[str]) -> None:
        """
        Устанавливает значение для указанного поля.
        """
        if key not in self._value_widgets:
            # Если поля нет, создаём его автоматически
            label_text = key.replace('_', ' ').title() + ":"
            self.add_field(key, label_text, value)
            return
        
        # ДОБАВИТЬ ЛОГ
        log.debug(f"set_field: key={key}, value={value}")
        
        if value is None or value.strip() == "":
            self._value_widgets[key].setText("—")
        else:
            self._value_widgets[key].setText(str(value))
        
        log.debug(f"Поле '{key}' = '{value}'")
    
    def get_field(self, key: str) -> Optional[str]:
        """
        Возвращает текущее значение поля.
        
        Args:
            key: Ключ поля
            
        Returns:
            Optional[str]: Текст поля или None, если поле не найдено
        """
        if key not in self._value_widgets:
            return None
        return self._value_widgets[key].text()
    
    def show_only(self, *keys: str) -> None:
        """
        Показывает только указанные поля, скрывая все остальные.
        
        Args:
            *keys: Ключи полей, которые нужно показать
        """
        # Сначала скрываем все поля
        for key in self._value_widgets:
            self._value_widgets[key].setVisible(False)
            self._label_widgets[key].setVisible(False)
        
        # Показываем только нужные
        visible_count = 0
        for key in keys:
            if key in self._value_widgets:
                self._value_widgets[key].setVisible(True)
                self._label_widgets[key].setVisible(True)
                visible_count += 1
            else:
                log.warning(f"InfoGrid: попытка показать неизвестное поле '{key}'")
        
        log.debug(f"InfoGrid: показано {visible_count} полей")
    
    def show_all(self) -> None:
        """Показывает все поля."""
        for key in self._value_widgets:
            self._value_widgets[key].setVisible(True)
            self._label_widgets[key].setVisible(True)
        log.debug("InfoGrid: показаны все поля")
    
    def hide_all(self) -> None:
        """Скрывает все поля."""
        for key in self._value_widgets:
            self._value_widgets[key].setVisible(False)
            self._label_widgets[key].setVisible(False)
        log.debug("InfoGrid: скрыты все поля")
    
    def get_visible_fields(self) -> List[str]:
        """
        Возвращает список ключей видимых в данный момент полей.
        
        Returns:
            List[str]: Список ключей видимых полей
        """
        return [
            key for key, widget in self._value_widgets.items()
            if widget.isVisible()
        ]
    
    def is_field_visible(self, key: str) -> bool:
        """
        Проверяет, видимо ли указанное поле.
        
        Args:
            key: Ключ поля
            
        Returns:
            bool: True если поле видимо
        """
        if key not in self._value_widgets:
            return False
        return self._value_widgets[key].isVisible()
    
    def clear_all(self) -> None:
        """Очищает все поля, устанавливая текст-заполнитель."""
        for field in self._value_widgets.values():
            field.setText("—")
        log.debug("InfoGrid: все поля очищены")
    
    def get_all_field_keys(self) -> List[str]:
        """
        Возвращает список всех существующих ключей полей.
        
        Returns:
            List[str]: Список всех ключей
        """
        return list(self._value_widgets.keys())
    
    def get_field_count(self) -> int:
        """
        Возвращает общее количество полей.
        
        Returns:
            int: Количество полей
        """
        return len(self._value_widgets)