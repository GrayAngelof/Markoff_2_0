## Анализ слоя «ui»

### Краткое описание слоя

Слой **ui** — это **верхний уровень приложения**, реализованный на **PySide6 (Qt)**. Он отвечает за:

- **Отображение данных** — дерево объектов (`TreeView`), панель деталей (`DetailsPanel`), статусная строка, тулбар, меню.
- **Обработку пользовательских действий** — клики по дереву, раскрытие/сворачивание узлов, нажатие кнопки обновления.
- **Коммуникацию с бизнес-логикой через события** — все действия пользователя преобразуются в события `EventBus` (`NodeSelected`, `NodeExpanded`, `RefreshRequested`), а обновления UI приходят через обработчики (`TreeUiHandler`, `DetailsUiHandler`, `UiCoordinator`).

**Что слой НЕ должен делать:**
- Не содержит бизнес-логику (загрузка данных, инвалидация, маппинг).
- Не вызывает напрямую `DataLoader` или репозитории.
- Не хранит состояние приложения (выбранный узел, раскрытые узлы) — только отображает его через модель.

---

### Файловая структура слоя

```
src/ui/
├── __init__.py                 # Публичное API: AppWindow
├── app_window.py               # AppWindow — фасад, собирающий все виджеты
├── coordinator.py              # UiCoordinator — подписка на события для управления виджетами
├── common/
│   ├── __init__.py
│   └── central_widget.py       # Центральный виджет с разделителем TreeView / StackedWidget
├── details/                    # Панель деталей
│   ├── __init__.py             # Экспорт DetailsPanel
│   ├── panel.py                # DetailsPanel — основной контейнер
│   ├── header.py               # HeaderWidget — шапка (тип, название, статус)
│   ├── info_grid.py            # InfoGrid — таблица "лейбл: значение"
│   ├── details_tabs.py         # DetailsTabs — вкладки (физика, юрики, пожарка, документы)
│   ├── placeholder.py          # PlaceholderWidget — заглушка "выберите объект"
│   └── tabs/                   # Внутренности вкладок (пока заглушки)
│       ├── __init__.py
│       ├── physics.py          # PhysicsTab
│       ├── legal.py            # LegalTab
│       ├── safety.py           # SafetyTab
│       └── documents.py        # DocumentsTab
├── handlers/                   # Обработчики событий (UI слой)
│   ├── __init__.py             # Экспорт DetailsUiHandler, TreeUiHandler
│   ├── details_handler.py      # Подписка на NodeDetailsLoaded → обновление DetailsPanel
│   └── tree_handler.py         # Подписка на ChildrenLoaded → обновление TreeModel
├── main_window/                # Компоненты главного окна
│   ├── __init__.py             # Экспорт MainWindow
│   ├── window.py               # MainWindow — пустая QMainWindow
│   ├── menu.py                 # MenuBar — главное меню (структура, без логики)
│   ├── toolbar.py              # Toolbar — панель инструментов (кнопка обновления)
│   └── status_bar.py           # StatusBar — строка состояния с индикатором соединения
└── tree/                       # Виджет дерева
    ├── __init__.py             # Экспорт TreeModel, TreeView
    ├── model.py                # TreeModel — Qt-модель на основе TreeNode
    └── view.py                 # TreeView — QTreeView, эмитит события в EventBus
```

---

### Описание внутренних классов (приватные / публичные, но внутренние для слоя)

| Класс | Назначение |
|-------|-------------|
| `AppWindow` (`app_window.py`) | Фасад UI. Создаёт все виджеты (окно, меню, тулбар, статусбар, центральный виджет). Предоставляет геттеры для `TreeView` и `DetailsPanel`. Подключает сигнал `Toolbar.refresh_triggered` к эмиссии `RefreshRequested`. |
| `MainWindow` (`main_window/window.py`) | Пустая `QMainWindow` (только заголовок, размеры). Ничего не знает о содержимом. |
| `MenuBar` (`main_window/menu.py`) | Создаёт меню «Файл», «Справочники», «Помощь». Действия пока не подключены (TODO). |
| `Toolbar` (`main_window/toolbar.py`) | Панель инструментов со сплит-кнопкой «Обновить» (3 режима: current, visible, full) и кнопкой переключения режима (пока без логики). Эмитит сигнал `refresh_triggered(str)`. |
| `StatusBar` (`main_window/status_bar.py`) | Строка состояния. Подписывается на `ConnectionChanged`. Использует внутренние сигналы (`StatusBarSignals`) для потокобезопасного обновления из любого потока. Показывает индикатор (⚪/✅/❌) и временные сообщения. |
| `CentralWidget` (`common/central_widget.py`) | Контейнер с `QSplitter` (30/70). Левая часть — `TreeView`. Правая — `QStackedWidget` с `PlaceholderWidget` (индекс 0) и `DetailsPanel` (индекс 1). Предоставляет метод `show_details_panel()` для переключения. |
| `DetailsPanel` (`details/panel.py`) | Главный виджет правой панели. Содержит `HeaderWidget`, `InfoGrid` и `DetailsTabs`. Получает `DetailsViewModel` через метод `update_content()`. Кэширует ViewModel по `NodeIdentifier`. При первом обновлении удаляет `PlaceholderWidget`. |
| `HeaderWidget` (`details/header.py`) | Шапка: показывает `subtitle: title` и опционально статус. |
| `InfoGrid` (`details/info_grid.py`) | Сетка в две колонки для отображения пар «лейбл → значение». Использует `grid_items` из `DetailsViewModel`. |
| `DetailsTabs` (`details/details_tabs.py`) | `QTabWidget` с четырьмя вкладками (физика, юрики, пожарка, документы). Пока только заглушки. |
| `PlaceholderWidget` (`details/placeholder.py`) | Текстовая заглушка «Выберите объект в дереве слева». |
| `TreeView` (`tree/view.py`) | `QTreeView` с настроенным внешним видом. Эмитит события `NodeSelected`, `NodeExpanded`, `NodeCollapsed` через `EventBus`. |
| `TreeModel` (`tree/model.py`) | Qt-модель, наследник `QAbstractItemModel`. Хранит корневые узлы `TreeNode` и кэш `{ (type, id): TreeNode }`. Предоставляет методы `set_root_nodes()`, `insert_children()`, `remove_children()`, `node_changed()`. |
| `TreeUiHandler` (`handlers/tree_handler.py`) | Обработчик событий для дерева. Подписывается на `ChildrenLoaded`. Если `parent == ROOT_NODE` — заменяет корневые узлы в модели. Иначе ищет родителя в кэше и вставляет детей. |
| `DetailsUiHandler` (`handlers/details_handler.py`) | Обработчик для панели деталей. Подписывается на `NodeDetailsLoaded`. Преобразует протокол `IDetailsViewModel` в конкретную `DetailsViewModel` (с `HeaderViewModel` и `InfoGridItem`) и вызывает `DetailsPanel.update_content()`. Затем эмитит `ShowDetailsPanel`. |
| `UiCoordinator` (`coordinator.py`) | Координатор глобальных UI-действий. Подписывается на `ShowDetailsPanel` (показывает панель деталей) и `CollapseAllRequested` (сворачивает всё дерево). |

---

### Список внутренних импортов (только внутри ui и вниз)

**Импорты из `src.core`**:
- `EventBus`
- События: `NodeSelected`, `NodeExpanded`, `NodeCollapsed`, `ChildrenLoaded`, `NodeDetailsLoaded`, `ShowDetailsPanel`, `CollapseAllRequested`, `RefreshRequested`, `ConnectionChanged`
- Типы: `ROOT_NODE`, `NodeType`, `NodeIdentifier`

**Импорты из `src.projections`**:
- `TreeNode` (для модели дерева)

**Импорты из `src.view_models`**:
- `DetailsViewModel`, `HeaderViewModel`, `InfoGridItem` (в `details_handler.py` и `details/panel.py`)

**Импорты из `utils`**:
- `get_logger`

**Импорты из PySide6**:
- `QtCore`, `QtGui`, `QtWidgets` (многочисленные)

**Импорты внутри `ui`**:
- `from .common.central_widget import CentralWidget`
- `from .details.panel import DetailsPanel`
- `from .handlers.details_handler import DetailsUiHandler`
- и т.д. — обычные относительные импорты.

**⚠️ Примечание:** Слой `ui` **не импортирует** `controllers`, `services`, `data`, `models` (кроме `view_models` и `projections.TreeNode`, что разрешено, так как проекции и view_models — это слои, подготовленные для UI). Он общается с контроллерами только через события `EventBus`.

---

### Экспортируемые методы / классы для вышестоящих слоёв (точки входа)

Выше слоя `ui` находится только `main.py` или точка входа приложения. Публичное API:

#### 1. `src.ui.AppWindow`

```python
class AppWindow:
    def __init__(self, bus: EventBus) -> None
    def get_tree_view(self) -> TreeView
    def get_details_panel(self) -> DetailsPanel
    def get_window(self) -> QMainWindow
    def show_details_panel(self) -> None
```

#### 2. `src.ui.UiCoordinator`

```python
class UiCoordinator:
    def __init__(self, bus: EventBus, app_window: AppWindow) -> None
    def start(self) -> None
    def cleanup(self) -> None
```

#### 3. `src.ui.handlers.TreeUiHandler`

```python
class TreeUiHandler:
    def __init__(self, bus: EventBus, tree_view: TreeView) -> None
    def start(self) -> None
    def cleanup(self) -> None
```

#### 4. `src.ui.handlers.DetailsUiHandler`

```python
class DetailsUiHandler:
    def __init__(self, bus: EventBus, panel: DetailsPanel) -> None
    def start(self) -> None
    def cleanup(self) -> None
```

---

### Итоговое заключение

**Принципы работы со слоем `ui`:**

1. **Импорт только из `src.ui`** — для создания приложения достаточно импортировать `AppWindow`. Обработчики и координатор создаются и запускаются снаружи (в `main.py` или `Application`).

2. **UI не хранит состояние приложения** — всё состояние (выбранный узел, раскрытые узлы, данные) лежит в контроллерах и передаётся через события. Исключение: кэш `DetailsPanel._view_model_cache` для быстрого переключения между узлами — это оптимизация отображения, не бизнес-состояние.

3. **Взаимодействие UI → бизнес-логика** — только через события:
   - `TreeView` эмитит `NodeSelected`, `NodeExpanded`, `NodeCollapsed`
   - `Toolbar` эмитит `RefreshRequested` (через `AppWindow`)

4. **Бизнес-логика → UI** — через обработчики (`TreeUiHandler`, `DetailsUiHandler`, `UiCoordinator`), которые подписаны на события `ChildrenLoaded`, `NodeDetailsLoaded`, `ShowDetailsPanel`, `CollapseAllRequested` и обновляют виджеты.

5. **Модель дерева (`TreeModel`) не знает о `EventBus`** — только получает данные из `TreeNode`. Это позволяет тестировать модель независимо.

6. **Потокобезопасность** — `StatusBar` использует сигналы для обновления из потока `ConnectionService`. Остальные виджеты обновляются только в главном потоке (через события, которые обрабатываются синхронно).

7. **Тестирование** — можно создавать `AppWindow` без `EventBus` (передав заглушку) и проверять компоновку. Обработчики легко мокать.

Слой `ui` является **чисто презентационным** и **не содержит ничего**, что нельзя было бы заменить на другой UI-фреймворк (например, на веб-интерфейс). Он полностью зависит от контрактов `EventBus`, `TreeNode` и `DetailsViewModel`.