# client/src/ui/details/info_grid.py
"""
Сетка с полями информации для панели деталей.
Предоставляет гибкую систему отображения пар "Лейбл: Значение"
с возможностью динамического показа/скрытия полей.
"""
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtCore import Qt
from typing import Dict, List, Optional, Tuple

from src.utils.logger import get_logger
log = get_logger(__name__)


class InfoGrid(QWidget):
    """
    Сетка для отображения информации в формате "Лейбл: Значение".
    
    Особенности:
    - Динамическое создание всех возможных полей
    - Возможность показа только нужных полей через show_only()
    - Автоматическая очистка значений через clear_all()
    - Поддержка переноса текста и выделения мышью
    - Получение списка видимых полей для тестирования
    """
    
    # ===== Константы =====
    
    # Определения всех возможных полей: (ключ, текст_лейбла)
    _FIELD_DEFINITIONS: List[Tuple[str, str]] = [
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
    """Список всех возможных полей для отображения"""
    
    # Стили для лейблов
    _LABEL_STYLESHEET = "font-weight: bold; color: #666666;"
    """Стиль для текста лейблов"""
    
    _PLACEHOLDER_TEXT = "—"
    """Текст-заполнитель для пустых значений"""
    
    # ===== Константы layout =====
    _VERTICAL_SPACING = 8
    """Вертикальный отступ между строками в пикселях"""
    
    _HORIZONTAL_SPACING = 20
    """Горизонтальный отступ между лейблом и значением в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует сетку информации.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация данных
        self._fields: Dict[str, QLabel] = {}
        self._labels: Dict[str, QLabel] = {}
        
        # Создание UI
        self._init_grid()
        self._create_all_fields()
        
        log.debug("InfoGrid: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_grid(self) -> None:
        """
        Инициализирует сетку QGridLayout с базовыми настройками.
        """
        self._grid = QGridLayout(self)
        self._grid.setVerticalSpacing(self._VERTICAL_SPACING)
        self._grid.setHorizontalSpacing(self._HORIZONTAL_SPACING)
        self._grid.setColumnStretch(1, 1)  # Колонка со значениями растягивается
        
        log.debug("InfoGrid: layout инициализирован")
    
    def _create_all_fields(self) -> None:
        """
        Создаёт все предопределённые поля из _FIELD_DEFINITIONS.
        Для каждого поля создаётся пара (лейбл, значение).
        """
        for row, (key, label_text) in enumerate(self._FIELD_DEFINITIONS):
            self._create_field_row(row, key, label_text)
        
        log.debug(f"InfoGrid: создано {len(self._FIELD_DEFINITIONS)} полей")
    
    def _create_field_row(self, row: int, key: str, label_text: str) -> None:
        """
        Создаёт одну строку с лейблом и полем значения.
        
        Args:
            row: Номер строки в сетке
            key: Ключ поля для идентификации
            label_text: Текст лейбла
        """
        # Создаём лейбл
        label_widget = QLabel(label_text)
        label_widget.setStyleSheet(self._LABEL_STYLESHEET)
        label_widget.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        # Создаём поле значения
        value_widget = QLabel(self._PLACEHOLDER_TEXT)
        value_widget.setWordWrap(True)
        value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Добавляем в сетку
        self._grid.addWidget(label_widget, row, 0)
        self._grid.addWidget(value_widget, row, 1)
        
        # Сохраняем для доступа по ключу
        self._labels[key] = label_widget
        self._fields[key] = value_widget
    
    # ===== Геттеры =====
    
    @property
    def fields(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь всех полей значений.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_значения}
        """
        return self._fields.copy()
    
    @property
    def labels(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь всех лейблов.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_лейбла}
        """
        return self._labels.copy()
    
    @property
    def grid_layout(self) -> QGridLayout:
        """
        Возвращает сетку layout для дополнительной настройки.
        
        Returns:
            QGridLayout: Сетка расположения
        """
        return self._grid
    
    # ===== Публичные методы управления полями =====
    
    def clear_all(self) -> None:
        """
        Очищает все поля, устанавливая текст-заполнитель.
        """
        for field in self._fields.values():
            field.setText(self._PLACEHOLDER_TEXT)
        
        log.debug("InfoGrid: все поля очищены")
    
    def set_field(self, key: str, value: Optional[str]) -> None:
        """
        Устанавливает значение для указанного поля.
        
        Args:
            key: Ключ поля
            value: Новое значение (None или пустая строка заменяются на заполнитель)
        """
        if key not in self._fields:
            log.warning(f"InfoGrid: попытка установить неизвестное поле '{key}'")
            return
        
        # Проверяем значение
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self._fields[key].setText(self._PLACEHOLDER_TEXT)
            log.debug(f"InfoGrid: поле '{key}' очищено")
        else:
            self._fields[key].setText(str(value))
            log.debug(f"InfoGrid: поле '{key}' = '{value[:50]}...'")
    
    def show_only(self, *keys: str) -> None:
        """
        Показывает только указанные поля, скрывая все остальные.
        
        Args:
            *keys: Ключи полей, которые нужно показать
        """
        # Сначала скрываем все поля
        for key in self._fields:
            self._fields[key].setVisible(False)
            self._labels[key].setVisible(False)
        
        # Показываем только нужные
        visible_count = 0
        for key in keys:
            if key in self._fields:
                self._fields[key].setVisible(True)
                self._labels[key].setVisible(True)
                visible_count += 1
            else:
                log.warning(f"InfoGrid: попытка показать неизвестное поле '{key}'")
        
        # Логируем результат
        visible_fields = self.get_visible_fields()
        log.debug(f"InfoGrid: показано {visible_count} полей: {sorted(visible_fields)}")
    
    def show_all(self) -> None:
        """
        Показывает все поля (для отладки или специальных режимов).
        """
        for key in self._fields:
            self._fields[key].setVisible(True)
            self._labels[key].setVisible(True)
        
        log.debug("InfoGrid: показаны все поля")
    
    def hide_all(self) -> None:
        """
        Скрывает все поля.
        """
        for key in self._fields:
            self._fields[key].setVisible(False)
            self._labels[key].setVisible(False)
        
        log.debug("InfoGrid: скрыты все поля")
    
    # ===== Методы для проверки состояния =====
    
    def get_visible_fields(self) -> List[str]:
        """
        Возвращает список ключей видимых в данный момент полей.
        
        Returns:
            List[str]: Список ключей видимых полей
        """
        visible = [
            key for key, widget in self._fields.items()
            if widget.isVisible()
        ]
        return visible
    
    def is_field_visible(self, key: str) -> bool:
        """
        Проверяет, видимо ли указанное поле.
        
        Args:
            key: Ключ поля
            
        Returns:
            bool: True если поле видимо
        """
        if key not in self._fields:
            return False
        return self._fields[key].isVisible()
    
    def get_field_value(self, key: str) -> str:
        """
        Возвращает текущее значение поля.
        
        Args:
            key: Ключ поля
            
        Returns:
            str: Текст поля или пустая строка, если поле не найдено
        """
        if key not in self._fields:
            return ""
        return self._fields[key].text()
    
    # ===== Методы для тестирования =====
    
    def get_all_field_keys(self) -> List[str]:
        """
        Возвращает список всех возможных ключей полей.
        
        Returns:
            List[str]: Список всех ключей
        """
        return [key for key, _ in self._FIELD_DEFINITIONS]
    
    def get_field_count(self) -> int:
        """
        Возвращает общее количество полей.
        
        Returns:
            int: Количество полей
        """
        return len(self._fields)