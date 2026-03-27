# client/src/bootstrap.py
"""
Инициализация всех компонентов приложения.
Собирает вместе Core, Models, Data, Services, Controllers и передает в UI.

Порядок инициализации (строго сверху вниз):
1. Core (EventBus) — ядро, не зависит от других
2. Data (EntityGraph, Repositories) — хранение данных
3. Services (ApiClient, DataLoader, ContextService, ConnectionService) — бизнес-логика
4. Projections (TreeProjection) — преобразование данных для UI
5. Controllers (TreeController, DetailsController, ...) — координация
6. UI (AppWindow) — отображение (создается ПОСЛЕ контроллеров, но настраивается ДО запуска)
7. Запуск фоновых сервисов ПОСЛЕ подписки UI
"""

from typing import Optional

from PySide6.QtWidgets import QApplication, QMainWindow

from src.core import EventBus
from src.core.events import NodeSelected, NodeExpanded, NodeCollapsed

from src.data import EntityGraph
from src.data import (
    ComplexRepository,
    BuildingRepository,
    FloorRepository,
    RoomRepository,
    CounterpartyRepository,
    ResponsiblePersonRepository,
)

from src.services import ApiClient, DataLoader, ConnectionService, ContextService
from src.projections.tree import TreeProjection
from src.controllers import (
    TreeController,
    DetailsController,
    RefreshController,
    ConnectionController,
)

from src.ui.app_window import AppWindow

from utils.logger import get_logger

log = get_logger(__name__)


class ApplicationBootstrap:
    """
    Загрузчик всех компонентов приложения — композиционный корень.
    
    Отвечает за:
    - Создание экземпляров всех слоев в правильном порядке
    - Настройку зависимостей (Dependency Injection)
    - Передачу зависимостей в UI
    - Запуск фоновых сервисов ПОСЛЕ того, как UI подписался на события
    - Очистку ресурсов при завершении
    """
    
    def __init__(self, app: QApplication):
        """
        Инициализирует все компоненты приложения.
        
        Args:
            app: Экземпляр QApplication
        """
        log.info("=" * 60)
        log.info("Запуск инициализации компонентов")
        log.info("=" * 60)

        self._app = app
        
        # Инициализация слоев по порядку с замером времени
        with log.measure_time("инициализация Core"):
            self._init_core()
        
        with log.measure_time("инициализация Data слоя"):
            self._init_data()
        
        with log.measure_time("инициализация Services"):
            self._init_services()
        
        with log.measure_time("инициализация Projections"):
            self._init_projections()
        
        with log.measure_time("инициализация Controllers"):
            self._init_controllers()
        
        with log.measure_time("инициализация UI"):
            self._init_ui()
        
        with log.measure_time("запуск фоновых сервисов"):
            self._start_services()
        
        log.info("=" * 60)
        log.success("Все компоненты инициализированы")
        log.info("=" * 60)
    
    # ===== Инициализация слоев =====
    
    def _init_core(self) -> None:
        """Инициализация ядра."""
        self._bus = EventBus()
        self._bus.set_debug(True)
        
        log.success("EventBus создан")
    
    def _init_data(self) -> None:
        """Инициализация слоя данных."""
        # Граф сущностей
        self._graph = EntityGraph(self._bus)
        
        # Репозитории
        self._complex_repo = ComplexRepository(self._graph)
        self._building_repo = BuildingRepository(self._graph)
        self._floor_repo = FloorRepository(self._graph)
        self._room_repo = RoomRepository(self._graph)
        self._counterparty_repo = CounterpartyRepository(self._graph)
        self._responsible_person_repo = ResponsiblePersonRepository(self._graph)
        
        log.success("EntityGraph и репозитории созданы")
        log.debug(f"Репозитории: Complex, Building, Floor, Room, Counterparty, ResponsiblePerson")
    
    def _init_services(self) -> None:
        """Инициализация сервисного слоя (СОЗДАНИЕ, без запуска)."""
        # API клиент
        self._api = ApiClient()
        log.success("ApiClient создан")
        
        # DataLoader
        self._loader = DataLoader(self._bus, self._api, self._graph)
        log.success("DataLoader создан")
        
        # ContextService
        self._context_service = ContextService(
            self._complex_repo,
            self._building_repo,
            self._floor_repo,
            self._room_repo,
            self._counterparty_repo,
            self._responsible_person_repo
        )
        log.success("ContextService создан")
        
        # ConnectionService (только создаем, НЕ ЗАПУСКАЕМ)
        self._connection_service = ConnectionService(self._bus, self._api)
        log.success("ConnectionService создан")
    
    def _init_projections(self) -> None:
        """Инициализация проекций."""
        # TreeProjection
        self._tree_projection = TreeProjection(
            complex_repo=self._complex_repo,
            building_repo=self._building_repo,
            floor_repo=self._floor_repo,
            room_repo=self._room_repo
        )
        log.success("TreeProjection создан")
    
    def _init_controllers(self) -> None:
        """Инициализация контроллеров."""
        # TreeController
        self._tree_controller = TreeController(
            bus=self._bus,
            loader=self._loader,
            context_service=self._context_service,
            tree_projection=self._tree_projection
        )
        
        # DetailsController (DetailsPanel будет установлен позже)
        self._details_controller = DetailsController(
            bus=self._bus,
            loader=self._loader
        )
        
        # RefreshController
        self._refresh_controller = RefreshController(
            bus=self._bus,
            loader=self._loader
        )
        
        # ConnectionController
        self._connection_controller = ConnectionController(self._bus)
        
        log.info("Контроллеры созданы: Tree, Details, Refresh, Connection")
    
    def _init_ui(self) -> None:
        """Инициализация UI."""
        # 1. Создаем фасад окна (AppWindow сам подписывается на ShowDetailsPanel)
        self._app_window = AppWindow(self._bus)
        log.success("AppWindow создан")
        
        # 2. Передаем AppWindow в TreeController (для доступа к TreeView)
        self._tree_controller.set_app_window(self._app_window)
        
        # 3. Передаем DetailsPanel в DetailsController
        details_panel = self._app_window.get_details_panel()
        self._details_controller.set_details_panel(details_panel)
        
        log.debug("Связи UI → контроллеры установлены")
    
    def _start_services(self) -> None:
        """Запускает фоновые сервисы ПОСЛЕ того, как UI подписался."""
        # 1. Запускаем ConnectionService
        self._connection_service.start()
        log.api("ConnectionService запущен")
        
        # 2. Запускаем загрузку комплексов
        log.info("Инициируем загрузку комплексов...")
        self._tree_controller.load_root_nodes()
        
        log.info("Все фоновые сервисы запущены")
    
    # ===== Публичные методы =====
    
    def get_window(self) -> QMainWindow:
        """Возвращает главное окно для отображения."""
        return self._app_window.get_window()
    
    def get_bus(self) -> EventBus:
        """Возвращает шину событий (для отладки)."""
        return self._bus
    
    def cleanup(self) -> None:
        """Очистка ресурсов перед завершением."""
        with log.measure_time("остановка сервисов и очистка ресурсов"):
            # Останавливаем сервисы
            self._connection_service.stop()
            log.api("ConnectionService остановлен")
            
            # Очищаем контроллеры
            self._tree_controller.cleanup()
            self._details_controller.cleanup()
            self._refresh_controller.cleanup()
            self._connection_controller.cleanup()
            log.success("Контроллеры очищены")
            
            # Очищаем граф
            self._graph.clear()
            log.data("EntityGraph очищен")
        
        log.shutdown("Ресурсы очищены")