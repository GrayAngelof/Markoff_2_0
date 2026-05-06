## Анализ слоя «ui» (интерфейс пользователя)

### Краткое описание слоя

Слой **ui** — самый верхний слой приложения. Он отвечает за **отображение данных и взаимодействие с пользователем** с использованием фреймворка **PySide6 (Qt)**. Слой ui:

- **Отображает дерево объектов** (`TreeView` + `TreeModel`) и панель деталей (`DetailsPanel`).
- **Генерирует пользовательские события** (клик, раскрытие/сворачивание узла) и отправляет их в `EventBus`.
- **Подписывается на события через обработчики** (`TreeUiHandler`, `DetailsUiHandler`) и обновляет виджеты.
- **Управляет главным окном** (`MainWindow` — пустая оболочка, без логики), строкой состояния (`StatusBar`), панелью инструментов (`Toolbar`) и меню (`MenuBar`).
- **Содержит только UI-логику** (обновление виджетов, преобразование событий в вызовы методов). Никакой бизнес-логики, загрузки данных, работы с API.

**Что слой ui НЕ должен делать:**
- Не выполняет HTTP-запросы или загрузку данных (это `services`).
- Не хранит состояние приложения (выбранный узел, раскрытые узлы) — оно хранится в контроллерах.
- Не содержит код, зависящий от фреймворка, кроме Qt (не должно быть прямых вызовов `requests`, `sqlite` и т.д.).
- Не импортирует `models`, `data`, `services`, `projections`, `controllers`, `view_models` (кроме `view_models` для данных, `core` для событий и `projections` для `TreeNode`).

---

### Файловая структура слоя

```
src/ui/
├── common/                     # Общие компоненты
│   ├── __init__.py
│   └── central_widget.py       # CentralWidget (разделитель дерево/детали)
├── details/                    # Панель детальной информации
│   ├── __init__.py
│   ├── panel.py                # DetailsPanel (главный контейнер)
│   ├── header.py               # HeaderWidget (шапка)
│   ├── info_grid.py            # InfoGrid (сетка "лейбл: значение")
│   ├── placeholder.py          # PlaceholderWidget (заглушка)
│   ├── details_tabs.py         # DetailsTabs (виджет вкладок)
│   └── tabs/                   # Вкладки (пока заглушки)
│       ├── __init__.py
│       ├── documents.py        # DocumentsTab
│       ├── legal.py            # LegalTab
│       ├── physics.py          # PhysicsTab
│       └── safety.py           # SafetyTab
├── handlers/                   # Обработчики событий (UI слой)
│   ├── __init__.py
│   ├── details_handler.py      # DetailsUiHandler
│   └── tree_handler.py         # TreeUiHandler
├── main_window/                # Главное окно и его части
│   ├── __init__.py
│   ├── window.py               # MainWindow (пустая оболочка)
│   ├── menu.py                 # MenuBar
│   ├── toolbar.py              # Toolbar
│   └── status_bar.py           # StatusBar
└── tree/                       # Дерево объектов
    ├── __init__.py
    ├── model.py                # TreeModel (QAbstractItemModel)
    └── view.py                 # TreeView (QTreeView с эмиссией событий)
```

---

### Описание всех классов (внутренних и публичных)

#### Публичные классы (экспортируются через `__init__.py`)

| Класс | Назначение |
|-------|-------------|
| `MainWindow` (`main_window.window`) | Пустое главное окно QMainWindow. Только заголовок, размеры. Не знает о содержимом. |
| `CentralWidget` (`common.central_widget`) | Виджет с горизонтальным разделителем: слева `TreeView`, справа `QStackedWidget` (заглушка / `DetailsPanel`). Предоставляет доступ к `TreeView` и `DetailsPanel`. |
| `DetailsPanel` (`details.panel`) | Панель деталей. Содержит `HeaderWidget`, `InfoGrid`, `DetailsTabs`. Получает `DetailsViewModel` и обновляет себя. Кэширует ViewModel для быстрого переключения. |
| `TreeModel` (`tree.model`) | Модель данных для `QTreeView`. Наследует `QAbstractItemModel`. Хранит корневые узлы (`TreeNode`), кэш узлов. Предоставляет методы `set_root_nodes`, `insert_children`, `remove_children`, `get_node_by_id`. |
| `TreeView` (`tree.view`) | Виджет дерева. Эмитит события `NodeSelected`, `NodeExpanded`, `NodeCollapsed` через `EventBus`. Подключает сигналы Qt к методам-слотам. |
| `TreeUiHandler` (`handlers.tree_handler`) | Обработчик событий дерева. Подписывается на `ChildrenLoaded`, обновляет `TreeModel`. При `parent == ROOT_NODE` — полная замена корневых узлов, иначе вставка детей. |
| `DetailsUiHandler` (`handlers.details_handler`) | Обработчик панели деталей. Подписывается на `NodeDetailsLoaded`, преобразует `IDetailsViewModel` в `DetailsViewModel` и вызывает `panel.update_content()`, затем эмитит `ShowDetailsPanel`. |
| `StatusBar` (`main_window.status_bar`) | Строка состояния. Подписывается на `ConnectionChanged`, отображает состояние соединения. Потокобезопасен через сигналы Qt. |
| `Toolbar` (`main_window.toolbar`) | Панель инструментов. Содержит сплит-кнопку обновления (3 режима: current/visible/full) и кнопку переключения режима (Read Only/Edit Mode — пока без функционала). Эмитит сигнал `refresh_triggered`. |
| `MenuBar` (`main_window.menu`) | Главное меню (Файл, Справочники, Помощь). Только визуальная структура; действия будут добавлены позже. |

#### Внутренние (приватные) классы (не экспортируются)

| Класс | Назначение |
|-------|-------------|
| `HeaderWidget` (`details.header`) | Шапка панели деталей. Отображает заголовок, подзаголовок, статус. |
| `InfoGrid` (`details.info_grid`) | Сетка для пар «лейбл: значение». Динамически создаёт строки на основе `vm.grid_items`. |
| `PlaceholderWidget` (`details.placeholder`) | Заглушка, показываемая, когда нет выбранного узла («Выберите объект в дереве слева»). |
| `DetailsTabs` (`details.details_tabs`) | Виджет вкладок (Физика, Юрики, Пожарка, Документы). Пока только заглушки, без содержимого. |
| `PhysicsTab`, `LegalTab`, `SafetyTab`, `DocumentsTab` (`details.tabs.*`) | Отдельные вкладки-заглушки. |
| `StatusBarSignals` (`main_window.status_bar`) | Вспомогательный QObject для межпотоковых сигналов (connection_status_changed). |
| `_DetailsViewModelImpl` (не используется в ui, но определён в projections) | Здесь не используется — ui использует `DetailsViewModel` из `view_models`. |

---

### Список внутренних импортов (только внутри ui и вниз)

**Импорты из `core`**:
- `from src.core.event_bus import EventBus`
- `from src.core.events import NodeSelected, NodeExpanded, NodeCollapsed, ChildrenLoaded, NodeDetailsLoaded, ShowDetailsPanel, ConnectionChanged`
- `from src.core.types import NodeIdentifier, NodeType, ROOT_NODE`

**Импорты из `projections`**:
- `from src.projections.tree_node import TreeNode`

**Импорты из `view_models`**:
- `from src.view_models.details import DetailsViewModel, HeaderViewModel, InfoGridItem`

**Импорты из `utils`**:
- `from utils.logger import get_logger`

**Импорты из PySide6** (основные модули):
- `PySide6.QtCore`, `PySide6.QtWidgets`, `PySide6.QtGui`

**Внутри ui** (между модулями):
- `from src.ui.common import CentralWidget`
- `from src.ui.details import DetailsPanel`
- `from src.ui.details.placeholder import PlaceholderWidget`
- `from src.ui.details.details_tabs import DetailsTabs`
- `from src.ui.details.header import HeaderWidget`
- `from src.ui.details.info_grid import InfoGrid`
- `from src.ui.details.tabs.* import ...`
- `from src.ui.handlers import DetailsUiHandler, TreeUiHandler`
- `from src.ui.main_window import MainWindow`
- `from src.ui.tree import TreeModel, TreeView`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящий слой для `ui` — это **главный модуль приложения** (например, `app.py` или `main.py`), который создаёт экземпляры всех объектов: `EventBus`, `EntityGraph`, `DataLoader`, `ReferenceStore`, репозитории, проекции, контроллеры, затем компоненты ui и связывает их через события. Из `src.ui` импортируются:

#### 1. `MainWindow` (из `src.ui.main_window`)

```python
class MainWindow(QMainWindow):
    """Пустая оболочка главного окна."""
    # Нет публичных методов, кроме стандартных Qt
```

#### 2. `CentralWidget` (из `src.ui.common`)

| Метод | Назначение |
|-------|-------------|
| `__init__()` | Создаёт виджет с разделителем. |
| `show_details_panel()` | Переключает правую панель с заглушки на DetailsPanel. |
| `get_tree_view() -> TreeView` | Возвращает виджет дерева. |
| `get_details_panel() -> DetailsPanel` | Возвращает панель деталей. |
| `central_widget -> QWidget` | QWidget для установки в MainWindow. |

#### 3. `DetailsPanel` (из `src.ui.details`)

| Метод | Назначение |
|-------|-------------|
| `set_event_bus(bus: EventBus)` | Устанавливает шину (используется для эмиссии ShowDetailsPanel). |
| `update_content(vm: DetailsViewModel, node: NodeIdentifier)` | Обновляет панель. |
| `get_cached_view_model(node) -> Optional[DetailsViewModel]` | Возвращает кэшированную ViewModel. |
| `clear_cache()` | Очищает кэш. |
| `header`, `info_grid`, `tabs` | Свойства для доступа к дочерним виджетам (необязательно). |

#### 4. `TreeView` (из `src.ui.tree`)

| Метод | Назначение |
|-------|-------------|
| `set_event_bus(bus: EventBus)` | Устанавливает шину для эмиссии событий. |
| `set_model(model: QAbstractItemModel)` | Устанавливает модель. |
| `collapse_all()` | Сворачивает все узлы. |

#### 5. `TreeModel` (из `src.ui.tree`)

| Метод | Назначение |
|-------|-------------|
| `set_root_nodes(nodes: List[TreeNode])` | Полная замена корневых узлов. |
| `insert_children(parent_node: TreeNode, children: List[TreeNode])` | Вставляет детей. |
| `remove_children(parent_node, row, count)` | Удаляет детей. |
| `node_changed(node: TreeNode)` | Уведомляет об изменении данных узла. |
| `get_node_by_id(node_type, node_id) -> Optional[TreeNode]` | Поиск узла в кэше. |

#### 6. `TreeUiHandler` (из `src.ui.handlers`)

| Метод | Назначение |
|-------|-------------|
| `__init__(bus, tree_view)` | Инициализирует обработчик. |
| `start()` | Подписывается на `ChildrenLoaded`, настраивает модель и виджет. |
| `cleanup()` | Отписывается. |

#### 7. `DetailsUiHandler` (из `src.ui.handlers`)

| Метод | Назначение |
|-------|-------------|
| `__init__(bus, panel)` | Инициализирует обработчик. |
| `start()` | Подписывается на `NodeDetailsLoaded`. |
| `cleanup()` | Отписывается. |

#### 8. `Toolbar` (из `src.ui.main_window`)

| Сигнал | Назначение |
|--------|-------------|
| `refresh_triggered = Signal(str)` | Передаёт режим обновления: `'current'`, `'visible'`, `'full'`. |

| Метод | Назначение |
|-------|-------------|
| `__init__()` | Создаёт панель инструментов. |

#### 9. `StatusBar` (из `src.ui.main_window`)

| Метод | Назначение |
|-------|-------------|
| `__init__(bus: EventBus)` | Инициализирует строку состояния, подписывается на `ConnectionChanged`. |
| `showTemporaryMessage(message: str, timeout_ms: int = 3000)` | Показывает временное сообщение. |
| `cleanup()` | Останавливает таймер, отписывается. |

#### 10. `MenuBar` (из `src.ui.main_window`)

| Метод | Назначение |
|-------|-------------|
| `__init__()` | Создаёт меню. Пока без действий. |

---

### Итоговое заключение

**Принципы работы со слоем `ui`:**

1. **Импорт только из `src.ui`** — используйте перечисленные публичные классы. Не импортируйте внутренние модули (`details.tabs`, `handlers`, `main_window` напрямую, если только вам не нужны специфические типы).

2. **Сборка приложения** — в главном модуле (`main.py`) создаётся экземпляр `MainWindow`, `CentralWidget`, настройка `EventBus`, `EntityGraph`, `ReferenceStore`, репозиториев, проекций, контроллеров, загрузчиков. Затем:
   - Получить `TreeView` и `DetailsPanel` из `CentralWidget`.
   - Создать обработчики `TreeUiHandler` и `DetailsUiHandler`, вызвать их `start()`.
   - Подключить сигнал `Toolbar.refresh_triggered` к функции, которая эмиттит `RefreshRequested`.
   - Передать `EventBus` в `StatusBar` и `DetailsPanel`.
   - Запустить `ConnectionService`.
   - Вызвать `TreeController.load_root_nodes()`.

3. **Все виджеты Qt должны создаваться и использоваться в главном потоке.** Обработчики событий могут быть вызваны из любого потока (например, `ConnectionChanged` приходит из потока `ConnectionService`), но в `StatusBar` используется сигнал для безопасного обновления UI.

4. **`TreeModel` кэширует узлы** — для поиска родителя при вставке детей используется `get_node_by_id`. Это эффективно и избавляет от рекурсивного обхода.

5. **`DetailsPanel` кэширует ViewModel** — при быстром переключении между узлами данные берутся из кэша, не требуя повторной загрузки.

6. **Никакой бизнес-логики в слое ui** — всё, что не касается отображения и пользовательского ввода, выносится в контроллеры/сервисы.

7. **Тестирование** — слой ui сложно тестировать автоматически из-за Qt. Рекомендуется:
   - Выделять бизнес-логику и преобразования в отдельные классы (уже сделано).
   - Использовать ручное тестирование или инструменты для тестирования Qt (pytest-qt).
   - Для `TreeModel` можно написать unit-тесты, создавая `TreeNode` и проверяя методы модели.

Слой `ui` завершает архитектуру приложения. Все зависимости направлены сверху вниз: ui → handlers → event_bus (core) → проекции (для TreeNode) → view_models. Нижние слои (core, models, data, services, projections, controllers, view_models) ничего не знают о Qt и ui.