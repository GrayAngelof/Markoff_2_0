# client/src/bootstrap.py
"""
Инициализация всех компонентов приложения.

Собирает вместе Core, Models, Data, Services, Controllers и передаёт в UI.

Порядок инициализации (строго сверху вниз):
1. Core (EventBus) — ядро, не зависит от других
2. Data (EntityGraph, Repositories) — хранение данных
3. Services (ApiClient, DataLoader, ContextService, ConnectionService) — бизнес-логика
4. Projections (TreeProjection) — преобразование данных для UI
5. Controllers (TreeController, DetailsController, ...) — координация
6. UI (AppWindow) — отображение (создаётся ПОСЛЕ контроллеров, но настраивается ДО запуска)
7. Запуск фоновых сервисов ПОСЛЕ подписки UI
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from PySide6.QtWidgets import QApplication, QMainWindow

from src.controllers import (
    ConnectionController,
    DetailsController,
    RefreshController,
    TreeController,
)
from src.core import EventBus
from src.data import (
    BuildingRepository,
    ComplexRepository,
    CounterpartyRepository,
    EntityGraph,
    FloorRepository,
    ResponsiblePersonRepository,
    RoomRepository,
)
from src.projections.tree import TreeProjection
from src.services import ApiClient, ConnectionService, ContextService, DataLoader
from src.ui.app_window import AppWindow
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

        log.info("=" * 60)
        log.success("Все компоненты инициализированы")
        log.info("=" * 60)

    def cleanup(self) -> None:
        """Очистка ресурсов перед завершением."""
        with log.measure_time("остановка сервисов и очистка ресурсов"):
            self._connection_service.stop()
            log.api("ConnectionService остановлен")

            self._tree_controller.cleanup()
            self._details_controller.cleanup()
            self._refresh_controller.cleanup()
            self._connection_controller.cleanup()
            log.success("Контроллеры очищены")

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
        """Инициализация ядра."""
        self._bus = EventBus()
        self._bus.set_debug(True)
        log.success("EventBus создан")

    def _init_data(self) -> None:
        """Инициализация слоя данных."""
        self._graph = EntityGraph(self._bus)

        self._complex_repo = ComplexRepository(self._graph)
        self._building_repo = BuildingRepository(self._graph)
        self._floor_repo = FloorRepository(self._graph)
        self._room_repo = RoomRepository(self._graph)
        self._counterparty_repo = CounterpartyRepository(self._graph)
        self._responsible_person_repo = ResponsiblePersonRepository(self._graph)

        log.success("EntityGraph и репозитории созданы")

    def _init_services(self) -> None:
        """Инициализация сервисного слоя (создание, без запуска)."""
        self._api = ApiClient()
        log.success("ApiClient создан")

        self._loader = DataLoader(self._bus, self._api, self._graph)
        log.success("DataLoader создан")

        self._context_service = ContextService(
            self._complex_repo,
            self._building_repo,
            self._floor_repo,
            self._room_repo,
            self._counterparty_repo,
            self._responsible_person_repo,
        )
        log.success("ContextService создан")

        self._connection_service = ConnectionService(self._bus, self._api)
        log.success("ConnectionService создан")

    def _init_projections(self) -> None:
        """Инициализация проекций."""
        self._tree_projection = TreeProjection(
            complex_repo=self._complex_repo,
            building_repo=self._building_repo,
            floor_repo=self._floor_repo,
            room_repo=self._room_repo,
        )
        log.success("TreeProjection создан")

    def _init_controllers(self) -> None:
        """Инициализация контроллеров."""
        self._tree_controller = TreeController(
            bus=self._bus,
            loader=self._loader,
            context_service=self._context_service,
            tree_projection=self._tree_projection,
        )

        self._details_controller = DetailsController(
            bus=self._bus,
            loader=self._loader,
        )

        self._refresh_controller = RefreshController(
            bus=self._bus,
            loader=self._loader,
        )

        self._connection_controller = ConnectionController(self._bus)

        log.info("Контроллеры созданы: Tree, Details, Refresh, Connection")

    def _init_ui(self) -> None:
        """Инициализация UI."""
        self._app_window = AppWindow(self._bus)
        log.success("AppWindow создан")

        self._tree_controller.set_app_window(self._app_window)

        details_panel = self._app_window.get_details_panel()
        self._details_controller.set_details_panel(details_panel)

        log.debug("Связи UI → контроллеры установлены")

    def _start_services(self) -> None:
        """Запускает фоновые сервисы ПОСЛЕ того, как UI подписался."""
        self._connection_service.start()
        log.api("ConnectionService запущен")

        log.info("Инициируем загрузку комплексов...")
        self._tree_controller.load_root_nodes()

        log.info("Все фоновые сервисы запущены")