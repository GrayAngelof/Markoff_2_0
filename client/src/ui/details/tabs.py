# client/src/ui/details/tabs.py
"""
Модуль для создания и управления вкладками панели детальной информации.
Предоставляет виджет с тремя предопределёнными вкладками:
- Физика (статистика по физическим объектам)
- Юрики (информация о юридических лицах)
- Пожарка (данные пожарной безопасности)
"""
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional, List, Tuple

from src.utils.logger import get_logger
log = get_logger(__name__)


class DetailsTabs(QTabWidget):
    """
    Виджет вкладок для панели детальной информации.
    
    Содержит три предопределённые вкладки:
    - 📊 Физика - для отображения физических характеристик
    - ⚖️ Юрики - для информации о юридических лицах и арендаторах
    - 🔥 Пожарка - для данных пожарной безопасности и датчиков
    
    Каждая вкладка в текущей версии содержит заглушку с пояснительным текстом.
    В будущем будет заменена на реальные виджеты с данными.
    """
    
    # ===== Константы =====
    
    # Определения вкладок: (индекс, название, текст заглушки, иконка)
    _TABS_DEFINITIONS: List[Tuple[str, str, str]] = [
        ("📊 Физика", "Физика", "📊 Статистика по физике будет здесь"),
        ("⚖️ Юрики", "Юрики", "⚖️ Информация о юридических лицах будет здесь"),
        ("🔥 Пожарка", "Пожарка", "🔥 Данные пожарной безопасности будут здесь"),
    ]
    """Список кортежей (текст_вкладки, внутреннее_имя, текст_заглушки)"""
    
    # Стили для виджета вкладок
    _TAB_WIDGET_STYLESHEET = """
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
    """
    
    # Стили для текста-заглушки
    _PLACEHOLDER_STYLESHEET = """
        QLabel {
            color: #808080;
            padding: 40px;
            font-size: 12px;
        }
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет вкладок.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Настройка внешнего вида
        self._setup_appearance()
        
        # Создание вкладок
        self._create_all_tabs()
        
        log.debug("DetailsTabs: инициализирован")
    
    # ===== Приватные методы =====
    
    def _setup_appearance(self) -> None:
        """
        Настраивает внешний вид виджета вкладок.
        Применяет стили из констант.
        """
        self.setStyleSheet(self._TAB_WIDGET_STYLESHEET)
        log.debug("DetailsTabs: стили применены")
    
    def _create_all_tabs(self) -> None:
        """
        Создаёт все предопределённые вкладки.
        Для каждой вкладки из _TABS_DEFINITIONS создаёт виджет-заглушку.
        """
        for tab_text, internal_name, placeholder_text in self._TABS_DEFINITIONS:
            tab_widget = self._create_placeholder_tab(placeholder_text, internal_name)
            self.addTab(tab_widget, tab_text)
            
        log.info(f"DetailsTabs: создано {len(self._TABS_DEFINITIONS)} вкладок")
    
    def _create_placeholder_tab(self, text: str, internal_name: str) -> QWidget:
        """
        Создаёт виджет-заглушку для вкладки.
        
        Args:
            text: Текст для отображения в заглушке
            internal_name: Внутреннее имя вкладки (для логирования)
            
        Returns:
            QWidget: Виджет с заглушкой
        """
        # Создаём контейнер для вкладки
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Создаём текст-заглушку
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(self._PLACEHOLDER_STYLESHEET)
        
        # Добавляем в layout
        layout.addWidget(label)
        
        log.debug(f"DetailsTabs: создана вкладка-заглушка '{internal_name}'")
        
        return widget
    
    # ===== Публичные методы =====
    
    def set_tab_enabled(self, index: int, enabled: bool = True) -> None:
        """
        Включает или отключает вкладку по индексу.
        
        Args:
            index: Индекс вкладки (0, 1, 2)
            enabled: True - включить, False - отключить
        """
        self.setTabEnabled(index, enabled)
        status = "включена" if enabled else "отключена"
        log.debug(f"DetailsTabs: вкладка {index} {status}")
    
    def get_tab_count(self) -> int:
        """
        Возвращает количество вкладок.
        
        Returns:
            int: Количество вкладок
        """
        return self.count()
    
    def get_current_tab_index(self) -> int:
        """
        Возвращает индекс текущей выбранной вкладки.
        
        Returns:
            int: Индекс текущей вкладки
        """
        return self.currentIndex()
    
    def get_current_tab_text(self) -> str:
        """
        Возвращает текст текущей выбранной вкладки.
        
        Returns:
            str: Текст текущей вкладки или пустая строка
        """
        index = self.currentIndex()
        if 0 <= index < self.count():
            return self.tabText(index)
        return ""
    
    # ===== Методы для будущего расширения =====
    
    def set_tab_widget(self, index: int, widget: QWidget) -> None:
        """
        Заменяет виджет в указанной вкладке на новый.
        
        Args:
            index: Индекс вкладки
            widget: Новый виджет для вкладки
        """
        # Сохраняем текущий текст вкладки
        tab_text = self.tabText(index)
        
        # Удаляем старый виджет и добавляем новый
        self.removeTab(index)
        self.insertTab(index, widget, tab_text)
        
        log.info(f"DetailsTabs: виджет вкладки {index} заменён")
    
    def update_tab_text(self, index: int, new_text: str) -> None:
        """
        Обновляет текст указанной вкладки.
        
        Args:
            index: Индекс вкладки
            new_text: Новый текст для вкладки
        """
        if 0 <= index < self.count():
            self.setTabText(index, new_text)
            log.debug(f"DetailsTabs: текст вкладки {index} изменён на '{new_text}'")