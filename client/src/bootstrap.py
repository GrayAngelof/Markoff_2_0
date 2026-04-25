# client/src/bootstrap.py
"""
Инициализация всех компонентов приложения.

Собирает вместе Core, Models, Data, Services, Controllers и передаёт в UI.

Порядок инициализации (строго сверху вниз):
1. Core (EventBus) — ядро, не зависит от других
2. Data (EntityGraph, Repositories, ReferenceStore) — хранение данных и справочники
3. Services (ApiClient, DataLoader, ConnectionService) — бизнес-логика
4. Projections (TreeProjection, DetailsProjection) — преобразование данных для UI
5. Controllers (TreeController, DetailsController, ...) — координация
6. UI (AppWindow) — отображение (создаётся ПОСЛЕ контроллеров, но настраивается ДО запуска)
7. Запуск фоновых сервисов ПОСЛЕ подписки UI
8. Загрузка справочников в ReferenceStore
"""

# ===== ИМПОРТЫ =====
from PySide6.QtWidgets import QApplication, QMainWindow

from src.controllers import (
    ConnectionController,
    DetailsController,
    RefreshController,
    TreeController,
)
from src.core.event_bus import EventBus
from src.data import (
    BuildingRepository,
    ComplexRepository,
    EntityGraph,
    FloorRepository,
    ReferenceStore,
    RoomRepository,
)
from src.projections.details_projection import DetailsProjection
from src.projections.tree import TreeProjection
from src.services import ApiClient, ConnectionService, DataLoader
from src.ui.app_window import AppWindow
from src.ui.coordinator import UiCoordinator
from src.ui.handlers.details_handler import DetailsUiHandler
from src.ui.handlers.tree_handler import TreeUiHandler
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class ApplicationBootstrap:
    """
    Загрузчик всех компонентов приложения — композиционный корень.

    Отвечает за:
    - Создание экземпляров всех слоёв в правильном порядке
    - Настройку зависимостей (Dependency Injection)
    - Передачу зависимостей в UI
    - Запуск фоновых сервисов ПОСЛЕ того, как UI подписался на события
    - Очистку ресурсов при завершении
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, app: QApplication) -> None:
        """Инициализирует все компоненты приложения."""
        log.info("=" * 60)
        log.info("Запуск инициализации компонентов")
        log.info("=" * 60)

        self._app = app

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

        with log.measure_time("загрузка справочников"):
            self._load_reference_data()

        log.info("=" * 60)
        log.success("Все компоненты инициализированы")
        log.info("=" * 60)

    def cleanup(self) -> None:
        """Очищает ресурсы перед завершением приложения."""
        with log.measure_time("остановка сервисов и очистка ресурсов"):
            self._connection_service.stop()
            log.api("ConnectionService остановлен")

            # Очистка UI обработчиков
            self._tree_ui_handler.cleanup()
            self._details_ui_handler.cleanup()
            self._ui_coordinator.cleanup()

            # Очистка контроллеров
            self._tree_controller.cleanup()
            self._details_controller.cleanup()
            self._refresh_controller.cleanup()
            self._connection_controller.cleanup()
            log.data("Контроллеры очищены")

            # Очистка ядра
            self._bus.clear()
            log.data("Шина очищена")

            # Очистка данных
            self._graph.clear()
            log.data("EntityGraph очищен")

        log.shutdown("Ресурсы очищены")

    # ---- ПУБЛИЧНОЕ API ----
    def get_window(self) -> QMainWindow:
        """Возвращает главное окно для отображения."""
        return self._app_window.get_window()

    def get_bus(self) -> EventBus:
        """Возвращает шину событий (для отладки)."""
        return self._bus

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _init_core(self) -> None:
        """Инициализирует ядро (EventBus)."""
        self._bus = EventBus()
        self._bus.set_debug(True)
        log.success("EventBus создан")

    def _init_data(self) -> None:
        """Инициализирует слой данных (EntityGraph, репозитории)."""
        self._graph = EntityGraph(self._bus)

        self._complex_repo = ComplexRepository(self._graph)
        self._building_repo = BuildingRepository(self._graph)
        self._floor_repo = FloorRepository(self._graph)
        self._room_repo = RoomRepository(self._graph)

        log.success("EntityGraph и репозитории созданы")

    def _init_services(self) -> None:
        """Инициализирует сервисный слой (создание, без запуска)."""
        self._api = ApiClient()
        log.success("ApiClient создан")

        # Композиционный корень связывает слои: передаём loader'ы из ApiClient
        self._reference_store = ReferenceStore(
            building_loader=self._api.get_building_statuses,
            room_loader=self._api.get_room_statuses,
        )
        log.success("ReferenceStore создан")

        self._loader = DataLoader(self._bus, self._api, self._graph)
        log.success("DataLoader создан")

        self._connection_service = ConnectionService(self._bus, self._api)
        log.success("ConnectionService создан")

    def _init_projections(self) -> None:
        """Инициализирует проекции (преобразование данных для UI)."""
        self._tree_projection = TreeProjection(
            complex_repo=self._complex_repo,
            building_repo=self._building_repo,
            floor_repo=self._floor_repo,
            room_repo=self._room_repo,
        )
        log.success("TreeProjection создан")

        self._details_projection = DetailsProjection(self._reference_store)
        log.success("DetailsProjection создан")

    def _init_controllers(self) -> None:
        """Инициализирует контроллеры (координация)."""
        self._tree_controller = TreeController(
            bus=self._bus,
            loader=self._loader,
            tree_projection=self._tree_projection,
        )

        self._details_controller = DetailsController(
            bus=self._bus,
            loader=self._loader,
            projection=self._details_projection,
        )

        self._refresh_controller = RefreshController(
            bus=self._bus,
            loader=self._loader,
        )

        self._connection_controller = ConnectionController(self._bus)

        log.info("Контроллеры созданы: Tree, Details, Refresh, Connection")

    def _init_ui(self) -> None:
        """Инициализирует UI и обработчики событий."""
        self._app_window = AppWindow(self._bus)
        log.success("AppWindow создан")

        # Получаем виджеты
        tree_view = self._app_window.get_tree_view()
        details_panel = self._app_window.get_details_panel()

        # Создаём UI обработчики
        self._tree_ui_handler = TreeUiHandler(self._bus, tree_view)
        self._details_ui_handler = DetailsUiHandler(self._bus, details_panel)
        self._ui_coordinator = UiCoordinator(self._bus, self._app_window)

        # Запускаем их (подписка на события)
        self._tree_ui_handler.start()
        self._details_ui_handler.start()
        self._ui_coordinator.start()

        log.debug("UI обработчики инициализированы и запущены")

    def _start_services(self) -> None:
        """Запускает фоновые сервисы ПОСЛЕ того, как UI подписался на события."""
        self._connection_service.start()
        log.api("ConnectionService запущен")

        log.info("Инициируем загрузку комплексов...")
        self._tree_controller.load_root_nodes()

        log.info("Все фоновые сервисы запущены")

    def _load_reference_data(self) -> None:
        """Загружает справочные данные в ReferenceStore."""
        log.info("-" * 40)
        log.info("Загрузка справочных данных")
        log.info("-" * 40)

        self._reference_store.warmup()

        log.info("-" * 40)
        log.info("Загрузка справочных данных завершена")
        log.info("-" * 40)