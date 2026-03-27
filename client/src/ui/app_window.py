# client/src/ui/app_window.py
"""
Фасад UI слоя.
Собирает главное окно из постоянных компонентов.

Принципы работы:
1. AppWindow создает ВСЕ UI компоненты (не принимает их извне)
2. Компоненты создаются в порядке: оболочка → постоянные → центральная область
3. Геттеры (get_tree_view, get_details_panel) позволяют контроллерам:
   - Установить модели данных (TreeModel)
   - Подписать компоненты на события (DetailsPanel.set_event_bus)
   - Настроить поведение после создания
4. Подписки на события (ShowDetailsPanel) обрабатываются здесь же,
   делегируя управление видимостью CentralWidget
"""

from PySide6.QtWidgets import QMainWindow

from src.core.event_bus import EventBus
from src.core.events import ShowDetailsPanel
from src.core.types.event_structures import Event

from src.ui.main_window.window import MainWindow
from src.ui.main_window.menu import MenuBar
from src.ui.main_window.toolbar import Toolbar
from src.ui.main_window.status_bar import StatusBar
from src.ui.common.central_widget import CentralWidget

from utils.logger import get_logger

log = get_logger(__name__)


class AppWindow:
    """
    Фасад UI слоя — единственный композиционный корень.
    
    Отвечает за:
    - Создание пустого MainWindow
    - Создание постоянных компонентов (MenuBar, Toolbar, StatusBar)
    - Создание CentralWidget (который внутри создает TreeView и DetailsPanel)
    - Компоновку всех компонентов в окне
    - Подписку на глобальные UI-события (ShowDetailsPanel)
    - Предоставление геттеров для контроллеров (TreeView, DetailsPanel)
    
    НЕ отвечает за:
    - Создание моделей данных (TreeModel)
    - Бизнес-логику (передается контроллерам)
    - Решение, когда показывать DetailsPanel (только делегирует CentralWidget)
    """
    
    def __init__(self, bus: EventBus) -> None:
        log.info("Инициализация AppWindow")
        
        self._bus = bus
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")
        
        # 1. Создаем пустую оболочку окна
        self._window = MainWindow()
        log.success("MainWindow создан")
        
        # 2. Создаем постоянные компоненты
        self._menu = MenuBar()
        log.success("MenuBar создан")
        
        self._toolbar = Toolbar()
        log.success("Toolbar создан")
        
        self._status_bar = StatusBar(bus)
        log.success("StatusBar создан")
        
        # 3. Создаем центральную область
        self._central = CentralWidget()
        log.success("CentralWidget создан")
        
        # 4. 🎯 ПЕРЕДАЕМ ШИНУ В TREEVIEW
        tree_view = self._central.get_tree_view()
        tree_view.set_event_bus(bus)
        log.success("TreeView настроен (EventBus передан)")
        
        # 5. Настраиваем DetailsPanel
        self._details_panel = self._central.get_details_panel()
        self._details_panel.set_event_bus(bus)
        log.success("DetailsPanel настроен (EventBus передан)")
        
        # 6. Подписываемся на событие показа панели деталей
        self._bus.subscribe(ShowDetailsPanel, self._on_show_details_panel)
        log.link("AppWindow подписан на ShowDetailsPanel")
        
        # 7. Компонуем все в главном окне
        self._window.setMenuBar(self._menu)
        self._window.addToolBar(self._toolbar)
        self._window.setStatusBar(self._status_bar)
        self._window.setCentralWidget(self._central.central_widget)
        
        log.system("AppWindow инициализирован")
    
    # ===== Геттеры для контроллеров =====
    # 
    # Зачем нужны геттеры?
    # 
    # AppWindow создает UI компоненты, но не знает, как их настраивать.
    # Контроллеры (TreeController, DetailsController) отвечают за:
    #   - Создание моделей (TreeModel)
    #   - Подписку на сигналы
    #   - Бизнес-логику
    # 
    # Геттеры позволяют:
    #   1. Сохранить инкапсуляцию — AppWindow не раскрывает внутреннюю структуру
    #   2. Соблюсти иерархию — контроллеры настраивают UI после создания
    #   3. Обеспечить тестируемость — можно подменить компоненты
    # 
    # Без геттеров пришлось бы:
    #   - Передавать компоненты в AppWindow извне (нарушение инкапсуляции)
    #   - Или создавать модели внутри AppWindow (нарушение иерархии)
    
    def get_tree_view(self):
        """
        Возвращает TreeView для установки модели.
        
        Используется:
        - TreeController для установки TreeModel
        
        Returns:
            TreeView: Виджет дерева (создан внутри CentralWidget)
        """
        return self._central.get_tree_view()
    
    def get_details_panel(self):
        """
        Возвращает DetailsPanel для дополнительной настройки.
        
        Используется:
        - DetailsController для доступа к панели (если нужно)
        
        Returns:
            DetailsPanel: Панель детальной информации (создана внутри CentralWidget)
        """
        return self._central.get_details_panel()
    
    def get_window(self) -> QMainWindow:
        """
        Возвращает QMainWindow для отображения.
        
        Используется:
        - bootstrap/main.py для показа окна
        
        Returns:
            QMainWindow: Главное окно приложения
        """
        return self._window
    
    # ===== Обработчики событий =====
    
    def _on_show_details_panel(self, event: Event[ShowDetailsPanel]) -> None:
        """
        Обрабатывает событие показа панели деталей.
        
        Контроллер (DetailsController) эмитит это событие при выборе узла.
        AppWindow делегирует переключение видимости CentralWidget.
        
        Args:
            event: Событие ShowDetailsPanel (данные не требуются)
        """
        log.debug("AppWindow: получено ShowDetailsPanel, переключаем панель")
        self._central.show_details_panel()