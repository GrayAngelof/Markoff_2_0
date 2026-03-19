# client/src/ui/main_window/main_window.py
"""
Главное окно приложения - композиционный корень.
"""
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import Slot

from src.core.event_bus import EventBus
from src.core.events import UIEvents, SystemEvents, HotkeyEvents
from src.data.entity_graph import EntityGraph
from src.services.api_client import ApiClient
from src.services.data_load import DataLoader
from src.services.connection_service import ConnectionService
from src.controllers.tree_controller import TreeController
from src.controllers.details_controller import DetailsController
from src.controllers.refresh_controller import RefreshController
from src.controllers.connection_controller import ConnectionController
from src.projections.tree_projection import TreeProjection

from src.ui.tree_model.tree_model import TreeModel
from src.ui.tree.tree_view import TreeView
from src.ui.details.details_panel import DetailsPanel
from src.ui.main_window.components import CentralWidget, Toolbar, StatusBar
from src.ui.main_window.shortcuts import ShortcutManager

from utils.logger import get_logger


log = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    """
    
    def __init__(self) -> None:
        """Инициализирует главное окно."""
        super().__init__()
        
        self._init_architecture()
        self._setup_ui()
        self._connect_ui_signals()
        self._setup_debug_subscriptions()
        
        # Запускаем полную загрузку
        self._bus.emit(UIEvents.REFRESH_REQUESTED, {'mode': 'full'})
        
        log.success("MainWindow полностью инициализировано")
    
    def _init_architecture(self) -> None:
        """Инициализирует архитектурные компоненты."""
        log.info("Инициализация архитектурных компонентов...")
        
        # 1. Ядро
        self._bus = EventBus()
        self._bus.set_debug(True)
        
        # 2. Данные
        self._graph = EntityGraph()
        
        # 3. Сервисы
        self._api = ApiClient()
        self._loader = DataLoader(self._bus, self._api, self._graph)
        self._connection = ConnectionService(self._bus, self._api)
        
        # 4. Контроллеры
        self._tree_controller = TreeController(self._bus, self._loader, self._graph)
        self._details_controller = DetailsController(self._bus, self._loader)
        self._refresh_controller = RefreshController(self._bus)
        self._connection_controller = ConnectionController(self._bus)
        
        # 5. Проекции
        self._tree_projection = TreeProjection(self._bus, self._graph)
        
        log.debug("Архитектурные компоненты инициализированы")
    
    def _setup_ui(self) -> None:
        """Создаёт и настраивает UI компоненты."""
        log.info("Инициализация UI компонентов...")
        
        # Модель и представление дерева
        self._tree_model = TreeModel(self._tree_projection)
        self._tree_view = TreeView(self)
        self._tree_view.set_event_bus(self._bus)  # передаём шину в TreeView
        self._tree_view.setModel(self._tree_model)
        
        # Панель деталей
        self._details_panel = DetailsPanel(self)
        log.debug(f"🔍 Устанавливаем шину событий для DetailsPanel: {self._bus}")
        self._details_panel.set_event_bus(self._bus)
        
        # Центральный виджет с разделителем
        self._central = CentralWidget(self)
        self._central.add_widgets(self._tree_view, self._details_panel)
        
        # Панель инструментов
        self._toolbar = Toolbar(self)
        self._setup_toolbar_connections()
        
        # Статус бар
        self._status_bar = StatusBar(self)
        
        # Горячие клавиши
        self._shortcuts = ShortcutManager(self)
        self._setup_shortcut_connections()
        
        # Настройки окна
        self.setWindowTitle("Markoff - Управление недвижимостью")
        self.setMinimumSize(1200, 800)
        
        log.debug("UI компоненты созданы")
    
    def _setup_toolbar_connections(self) -> None:
        """Настраивает соединения панели инструментов."""
        self._toolbar.signals.refresh_current.connect(
            lambda: self._bus.emit(HotkeyEvents.REFRESH_CURRENT, {}, source='toolbar')
        )
        self._toolbar.signals.refresh_visible.connect(
            lambda: self._bus.emit(HotkeyEvents.REFRESH_VISIBLE, {}, source='toolbar')
        )
        self._toolbar.signals.full_reset.connect(
            lambda: self._bus.emit(HotkeyEvents.FULL_RESET, {}, source='toolbar')
        )
    
    def _setup_shortcut_connections(self) -> None:
        """Настраивает соединения горячих клавиш."""
        self._shortcuts.signals.refresh_current.connect(
            lambda: self._bus.emit(HotkeyEvents.REFRESH_CURRENT, {}, source='shortcut')
        )
        self._shortcuts.signals.refresh_visible.connect(
            lambda: self._bus.emit(HotkeyEvents.REFRESH_VISIBLE, {}, source='shortcut')
        )
        self._shortcuts.signals.full_reset.connect(
            lambda: self._bus.emit(HotkeyEvents.FULL_RESET, {}, source='shortcut')
        )
    
    def _connect_ui_signals(self) -> None:
        """Подключает сигналы между UI компонентами."""
        # ИСПРАВЛЕНО: теперь панель деталей подписывается на события через шину
        # self._tree_view.item_selected больше не используется
        
        # Обновление владельца корпуса -> панель деталей
        self._bus.subscribe('ui.building_owner_loaded', self._on_building_owner_loaded)
        
        # Статус соединения
        self._bus.subscribe(SystemEvents.CONNECTION_CHANGED, self._on_connection_changed)
        
        # Ошибки
        self._bus.subscribe('ui.show_error', self._on_show_error)
        self._bus.subscribe('ui.show_confirmation', self._on_show_confirmation)
        
        log.debug("Сигналы UI подключены")
    
    def _setup_debug_subscriptions(self) -> None:
        """Настраивает подписки для отладки."""
        self._bus.subscribe(SystemEvents.DATA_LOADED, self._on_data_loaded)
        self._bus.subscribe(SystemEvents.DATA_ERROR, self._on_data_error)
    
    # ===== Обработчики событий =====
    
    @Slot(dict)
    def _on_building_owner_loaded(self, event: dict) -> None:
        """Обрабатывает загрузку данных о владельце корпуса."""
        data = event['data']
        self._details_panel.update_owner_info(data)
    
    @Slot(dict)
    def _on_connection_changed(self, event: dict) -> None:
        """Обновляет индикаторы соединения в UI."""
        is_online = event['data']['is_online']
        
        if is_online:
            self._status_bar.set_connection_online()
            self._toolbar.set_status_online()
            self._status_bar.show_temporary_message("✅ Соединение с сервером восстановлено")
        else:
            self._status_bar.set_connection_offline()
            self._toolbar.set_status_offline()
            self._status_bar.show_temporary_message("❌ Сервер недоступен")
    
    @Slot(dict)
    def _on_show_error(self, event: dict) -> None:
        """Показывает диалог с ошибкой."""
        data = event['data']
        QMessageBox.warning(
            self,
            data.get('title', 'Ошибка'),
            data.get('message', 'Произошла неизвестная ошибка')
        )
    
    @Slot(dict)
    def _on_show_confirmation(self, event: dict) -> None:
        """Показывает диалог подтверждения."""
        data = event['data']
        reply = QMessageBox.question(
            self,
            data.get('title', 'Подтверждение'),
            data.get('message', 'Вы уверены?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes and data.get('callback_event'):
            self._bus.emit(
                data['callback_event'],
                data.get('callback_data', {}),
                source='main_window'
            )
    
    @Slot(dict)
    def _on_data_loaded(self, event: dict) -> None:
        """Логирует загрузку данных."""
        data = event['data']
        node_type = data.get('node_type')
        count = data.get('count', 1)
        self._status_bar.show_temporary_message(f"✅ Загружено: {node_type} ({count})")
    
    @Slot(dict)
    def _on_data_error(self, event: dict) -> None:
        """Логирует ошибки загрузки."""
        data = event['data']
        node_type = data.get('node_type')
        error = data.get('error', 'Неизвестная ошибка')
        log.error(f"Ошибка загрузки {node_type}: {error}")
        self._status_bar.show_temporary_message(f"❌ Ошибка: {error[:50]}...")
    
    def closeEvent(self, event) -> None:
        """Обрабатывает закрытие окна."""
        log.info("Завершение работы приложения...")
        
        # Останавливаем сервисы
        self._connection.stop()
        
        # Очищаем контроллеры
        self._tree_controller.cleanup()
        self._details_controller.cleanup()
        self._refresh_controller.cleanup()
        self._connection_controller.cleanup()
        
        # Очищаем проекции
        self._tree_projection.cleanup()
        
        # Очищаем данные
        self._loader.cleanup()
        self._graph.clear()
        
        log.success("Приложение завершено")
        event.accept()