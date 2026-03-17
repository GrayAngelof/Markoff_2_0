# client/src/ui/details/base_panel.py
"""
Базовый класс для панели детальной информации.
Содержит общую инициализацию, базовые компоненты и методы
для управления отображением информации о выбранном объекте.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional, Dict, List, Any

from src.ui.details.header_widget import HeaderWidget
from src.ui.details.placeholder import PlaceholderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.tabs import DetailsTabs
from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class DetailsPanelBase(QWidget):
    """
    Базовый класс для панели детальной информации.
    
    Предоставляет:
    - Шапку с иерархией (HeaderWidget)
    - Заглушку (PlaceholderWidget) для режима "ничего не выбрано"
    - Сетку информации (InfoGrid) для отображения данных
    - Вкладки (DetailsTabs) для дополнительной информации
    - Методы для управления видимостью компонентов
    - Прокси-методы для доступа к дочерним компонентам
    
    Наследники должны реализовать:
    - show_item_details() - отображение информации о конкретном объекте
    """
    
    # ===== Константы =====
    
    _CONTENT_MARGINS = (10, 10, 10, 10)
    """Отступы для контента (слева, сверху, справа, снизу)"""
    
    _LAYOUT_SPACING = 10
    """Расстояние между элементами в layout"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует базовую панель детальной информации.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация состояния
        self._init_state()
        
        # Инициализация UI
        self._init_ui()
        
        # Явно делаем панель видимой
        self.setVisible(True)
        
        log.debug("DetailsPanelBase: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_state(self) -> None:
        """Инициализирует состояние панели."""
        self._current_type: Optional[str] = None
        self._current_id: Optional[int] = None
        self._current_data: Optional[Any] = None
        
        log.debug("DetailsPanelBase: состояние инициализировано")
    
    def _init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        # Основной вертикальный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаём и добавляем шапку
        self._create_header()
        layout.addWidget(self._header)
        
        # Создаём и добавляем контейнер с контентом
        self._create_content_container()
        layout.addWidget(self._content_container, 1)  # Растягивается с коэффициентом 1
        
        log.debug("DetailsPanelBase: UI инициализирован")
    
    def _create_header(self) -> None:
        """Создаёт и настраивает шапку панели."""
        self._header = HeaderWidget(self)
        self._header.setVisible(True)
        log.debug("DetailsPanelBase: шапка создана")
    
    def _create_content_container(self) -> None:
        """Создаёт контейнер с заглушкой, сеткой и вкладками."""
        # Контейнер для контента (растягивается)
        self._content_container = QWidget(self)
        self._content_container.setVisible(True)
        
        # Layout для контейнера
        container_layout = QVBoxLayout(self._content_container)
        container_layout.setContentsMargins(*self._CONTENT_MARGINS)
        container_layout.setSpacing(self._LAYOUT_SPACING)
        
        # Заглушка (видима по умолчанию)
        self._placeholder = PlaceholderWidget(self._content_container)
        self._placeholder.setVisible(True)
        container_layout.addWidget(self._placeholder)
        
        # Сетка информации (скрыта по умолчанию)
        self._info_grid = InfoGrid(self._content_container)
        self._info_grid.setVisible(False)
        container_layout.addWidget(self._info_grid)
        
        # Вкладки (всегда видимы)
        self._tabs = DetailsTabs(self._content_container)
        self._tabs.setVisible(True)
        container_layout.addWidget(self._tabs)
        
        # Добавляем растяжку в конце, чтобы контент не прижимался к верху
        container_layout.addStretch()
        
        log.debug("DetailsPanelBase: контейнер контента создан")
    
    # ===== Геттеры =====
    
    @property
    def header(self) -> HeaderWidget:
        """
        Возвращает виджет шапки.
        
        Returns:
            HeaderWidget: Виджет шапки
        """
        return self._header
    
    @property
    def title_label(self) -> QLabel:
        """Прокси для заголовка из шапки."""
        return self._header.title_label
    
    @property
    def hierarchy_label(self) -> QLabel:
        """Прокси для метки иерархии из шапки."""
        return self._header.hierarchy_label
    
    @property
    def status_label(self) -> QLabel:
        """Прокси для метки статуса из шапки."""
        return self._header.status_label
    
    @property
    def icon_label(self) -> QLabel:
        """Прокси для метки иконки из шапки."""
        return self._header.icon_label
    
    @property
    def placeholder(self) -> PlaceholderWidget:
        """
        Возвращает виджет-заглушку.
        
        Returns:
            PlaceholderWidget: Виджет заглушки
        """
        return self._placeholder
    
    @property
    def info_grid(self) -> InfoGrid:
        """
        Возвращает сетку информации.
        
        Returns:
            InfoGrid: Сетка с полями
        """
        return self._info_grid
    
    @property
    def fields(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь полей из сетки информации.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_значения}
        """
        return self._info_grid.fields
    
    @property
    def tabs(self) -> DetailsTabs:
        """
        Возвращает виджет вкладок.
        
        Returns:
            DetailsTabs: Виджет вкладок
        """
        return self._tabs
    
    @property
    def content_container(self) -> QWidget:
        """
        Возвращает контейнер с контентом.
        
        Returns:
            QWidget: Контейнер контента
        """
        return self._content_container
    
    # ===== Методы управления видимостью =====
    
    def show_info_grid(self) -> None:
        """
        Показывает сетку информации и скрывает заглушку.
        Также убеждается, что вся цепочка родительских виджетов видима.
        """
        log.debug("DetailsPanelBase: показываем info_grid")
        
        # Убеждаемся, что вся цепочка видима
        self.setVisible(True)
        self._content_container.setVisible(True)
        self._info_grid.setVisible(True)
        
        # Скрываем заглушку
        self._placeholder.setVisible(False)
        
        log.debug("DetailsPanelBase: info_grid показана, заглушка скрыта")
    
    def hide_info_grid(self) -> None:
        """
        Скрывает сетку информации и показывает заглушку.
        """
        self._placeholder.setVisible(True)
        self._info_grid.setVisible(False)
        log.debug("DetailsPanelBase: info_grid скрыта, заглушка показана")
    
    # ===== Методы управления полями =====
    
    def clear_all_fields(self) -> None:
        """Очищает все поля в сетке информации."""
        self._info_grid.clear_all()
        log.debug("DetailsPanelBase: все поля очищены")
    
    def set_field(self, key: str, value: Optional[str]) -> None:
        """
        Устанавливает значение для указанного поля.
        
        Args:
            key: Ключ поля
            value: Значение для установки
        """
        self._info_grid.set_field(key, value)
    
    def set_status_style(self, status: Optional[str]) -> None:
        """
        Устанавливает стиль статуса в шапке.
        
        Args:
            status: Код статуса
        """
        self._header.set_status_style(status)
    
    def show_fields(self, *keys: str) -> None:
        """
        Показывает только указанные поля.
        
        Args:
            *keys: Ключи полей для отображения
        """
        self._info_grid.show_only(*keys)
    
    # ===== Методы для работы с вкладками =====
    
    def set_current_tab(self, index: int) -> None:
        """
        Устанавливает текущую вкладку по индексу.
        
        Args:
            index: Индекс вкладки
        """
        self._tabs.setCurrentIndex(index)
        log.debug(f"DetailsPanelBase: установлена вкладка {index}")
    
    def get_current_tab(self) -> int:
        """
        Возвращает индекс текущей вкладки.
        
        Returns:
            int: Индекс текущей вкладки
        """
        return self._tabs.currentIndex()
    
    # ===== Методы для работы с состоянием =====
    
    @property
    def current_type(self) -> Optional[str]:
        """Возвращает тип текущего выбранного объекта."""
        return self._current_type
    
    @current_type.setter
    def current_type(self, value: Optional[str]) -> None:
        """Устанавливает тип текущего выбранного объекта."""
        self._current_type = value
    
    @property
    def current_id(self) -> Optional[int]:
        """Возвращает ID текущего выбранного объекта."""
        return self._current_id
    
    @current_id.setter
    def current_id(self, value: Optional[int]) -> None:
        """Устанавливает ID текущего выбранного объекта."""
        self._current_id = value
    
    @property
    def current_data(self) -> Optional[Any]:
        """Возвращает данные текущего выбранного объекта."""
        return self._current_data
    
    @current_data.setter
    def current_data(self, value: Optional[Any]) -> None:
        """Устанавливает данные текущего выбранного объекта."""
        self._current_data = value
    
    def is_object_selected(self) -> bool:
        """
        Проверяет, выбран ли какой-либо объект.
        
        Returns:
            bool: True если объект выбран
        """
        return self._current_type is not None and self._current_id is not None
    
    def clear_selection(self) -> None:
        """Очищает информацию о выбранном объекте."""
        self._current_type = None
        self._current_id = None
        self._current_data = None
        log.debug("DetailsPanelBase: выделение сброшено")