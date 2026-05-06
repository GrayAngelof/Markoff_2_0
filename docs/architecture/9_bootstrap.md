## Анализ слоя «интеграция» (bootstrap / композиционный корень)

### Краткое описание слоя

Слой **интеграции** не является функциональным слоем в иерархии `core → models → … → ui`. Это **композиционный корень** приложения, отвечающий за:

- **Создание всех компонентов** в правильном порядке (сверху вниз, с учётом зависимостей).
- **Настройку зависимостей** (Dependency Injection) — явная передача экземпляров в конструкторы.
- **Запуск фоновых сервисов** (`ConnectionService`, `TreeController.load_root_nodes()`) **после** того, как UI подписался на события.
- **Загрузку справочников** (`ReferenceStore.warmup()`) после инициализации всех слоёв.
- **Очистку ресурсов** при завершении приложения (остановка сервисов, отписка обработчиков, очистка графа и шины).
- **Точку входа** (`main.py`) — настройка окружения, логирования, создание `QApplication`, вызов bootstrap и главного цикла.

**Что этот слой НЕ должен делать:**
- Не содержит бизнес-логику, работу с данными, UI-логику.
- Не дублирует инициализацию компонентов (каждый компонент инициализируется ровно один раз).
- Не управляет зависимостями через глобальные переменные или синглтоны (всё передаётся явно).

---

### Файловая структура слоя

```
client/src/
├── __init__.py                  # корневой пакет (пустой)
├── bootstrap.py                 # ApplicationBootstrap — композиционный корень
└── main.py                      # точка входа: настройка логирования, QApplication, вызов bootstrap
```

---

### Описание классов и функций

| Класс / Функция | Назначение |
|----------------|-------------|
| `ApplicationBootstrap` | Главный загрузчик. В `__init__` последовательно вызывает `_init_core()`, `_init_data()`, `_init_services()`, `_init_projections()`, `_init_controllers()`, `_init_ui()`, `_start_services()`, `_load_reference_data()`. Хранит ссылки на все созданные компоненты. Предоставляет `cleanup()` для освобождения ресурсов, `get_window()` для получения главного окна, `get_bus()` для отладки. |
| `setup_application()` | Создаёт и настраивает `QApplication` (имя, организация). |
| `setup_logging()` | Настраивает уровни логирования через `Logger` (DEBUG при разработке, категории `performance`, `db`, `api`). |
| `main()` | Точка входа: настройка окружения (переменная `QT_LOGGING_RULES`), вызов `setup_logging()`, создание `QApplication`, создание `ApplicationBootstrap`, получение окна, запуск главного цикла, вызов `bootstrap.cleanup()` при завершении. |

---

### Список внутренних импортов

**Из `src`**:
- `from src.controllers import ConnectionController, DetailsController, RefreshController, TreeController`
- `from src.core.event_bus import EventBus`
- `from src.data import BuildingRepository, ComplexRepository, EntityGraph, FloorRepository, ReferenceStore, RoomRepository`
- `from src.projections.details_projection import DetailsProjection`
- `from src.projections.tree import TreeProjection`
- `from src.services import ApiClient, ConnectionService, DataLoader`
- `from src.services.loaders.dictionary_loader import DictionaryLoader`
- `from src.ui.app_window import AppWindow`
- `from src.ui.coordinator import UiCoordinator`
- `from src.ui.handlers.details_handler import DetailsUiHandler`
- `from src.ui.handlers.tree_handler import TreeUiHandler`

**Из `utils`**:
- `from utils.logger import get_logger, Logger`

**Из PySide6**:
- `from PySide6.QtWidgets import QApplication, QMainWindow`

**Стандартные**:
- `os`, `sys`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящего слоя нет (это корень приложения). Однако `ApplicationBootstrap` предоставляет публичный API для `main.py`:

| Метод | Назначение |
|-------|-------------|
| `__init__(app: QApplication)` | Инициализирует все компоненты. |
| `cleanup() -> None` | Останавливает сервисы, отписывает обработчики, очищает граф и шину. |
| `get_window() -> QMainWindow` | Возвращает главное окно (для вызова `show()`). |
| `get_bus() -> EventBus` | Возвращает шину событий (для отладки). |

Функция `main()` — точка входа, не импортируется другими модулями.

---

### Итоговое заключение

**Принципы работы со слоем интеграции (bootstrap):**

1. **Единственный композиционный корень** — все зависимости создаются и передаются явно. Нет глобальных переменных или «магических» импортов.

2. **Порядок инициализации строго сверху вниз**:
   - Core (`EventBus`)
   - Data (`EntityGraph`, репозитории, `ReferenceStore`)
   - Services (`ApiClient`, `DataLoader`, `ConnectionService`)
   - Projections (`TreeProjection`, `DetailsProjection`)
   - Controllers (Tree, Details, Refresh, Connection)
   - UI (окно, обработчики, координатор)
   - Запуск фоновых сервисов (после подписки UI)
   - Загрузка справочников

3. **Фоновые сервисы запускаются после настройки UI** — это гарантирует, что `StatusBar` и другие обработчики уже подписаны на события `ConnectionChanged` до первой проверки.

4. **Очистка ресурсов в `cleanup()`** — обратный порядок: сначала остановка сервисов, затем отписка обработчиков, очистка контроллеров, шины, графа.

5. **Логирование** — каждый этап инициализации обёрнут в `with log.measure_time(...)`. Уровни логирования настраиваются через `Logger.set_category_level`.

6. **Тестирование** — `ApplicationBootstrap` не предназначен для модульного тестирования (он запускает реальное приложение). Для интеграционных тестов можно создать аналогичный загрузчик с мок-зависимостями.

Слой интеграции — это **клей**, который соединяет все слои, соблюдая строгую направленность зависимостей (только сверху вниз). Он не содержит бизнес-логики и не должен меняться при добавлении новых типов данных или UI-компонентов (меняются только вызовы конструкторов).