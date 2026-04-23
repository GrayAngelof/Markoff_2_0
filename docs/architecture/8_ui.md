## Анализ слоя: **ui** (пользовательский интерфейс)

### Краткое описание слоя

**Назначение** – предоставить графический интерфейс пользователя (Qt), отображать данные и преобразовывать действия пользователя в события шины (`EventBus`). Слой `ui` – самый верхний в иерархии, он зависит от всех нижележащих слоёв (`core`, `models`, `data`, `services`, `projections`, `controllers`), но **не должен импортироваться снизу** (хотя нарушение есть – `controllers` импортирует `DetailsPanel`).

**Что делает:**
- Создаёт и компонует виджеты: главное окно, меню, панель инструментов, строку состояния, дерево объектов, панель деталей.
- Предоставляет модели для отображения (`TreeModel`) и виджеты (`TreeView`, `DetailsPanel`).
- Обрабатывает сигналы Qt (клики, раскрытие/сворачивание) и преобразует их в события `EventBus` (`NodeSelected`, `NodeExpanded`, `NodeCollapsed`, `RefreshRequested`).
- Подписывается на события `EventBus` через обработчики (`TreeUiHandler`, `DetailsUiHandler`, `UiCoordinator`) и обновляет UI (вставка детей в дерево, показ панели деталей, сворачивание дерева).
- Не содержит бизнес-логики, не загружает данные, не управляет состоянием приложения (кроме временного UI-состояния, например, раскрытых узлов в модели).

**Что не должен делать:**
- Импортировать что-либо из `controllers` (нарушение зависимости, но в текущем коде нет таких импортов – проблема только в `controllers`).
- Содержать логику доступа к данным или бизнес-правила.
- Управлять кэшем или валидностью данных.
- Знать о существовании `EntityGraph` или репозиториев напрямую.

---

### Файловая структура слоя

```
client/src/ui/
├── __init__.py                    # Публичное API: AppWindow
├── app_window.py                  # Фасад UI слоя (сборка всех компонентов)
├── coordinator.py                 # UiCoordinator (подписка на глобальные события: ShowDetailsPanel, CollapseAllRequested)
├── common/
│   ├── __init__.py
│   └── central_widget.py          # Центральный виджет с разделителем (TreeView слева, QStackedWidget справа)
├── details/                       # Панель детальной информации
│   ├── __init__.py                # Экспорт DetailsPanel
│   ├── panel.py                   # DetailsPanel (главный контейнер правой панели)
│   ├── details_tabs.py            # DetailsTabs (вкладки)
│   ├── header.py                  # HeaderWidget (шапка)
│   ├── info_grid.py               # InfoGrid (сетка полей)
│   ├── placeholder.py             # PlaceholderWidget (заглушка при отсутствии выбора)
│   └── tabs/                      # Вкладки (заглушки)
│       ├── __init__.py
│       ├── documents.py
│       ├── legal.py
│       ├── physics.py
│       └── safety.py
├── handlers/                      # Обработчики событий для обновления UI
│   ├── __init__.py
│   ├── details_handler.py         # DetailsUiHandler (подписка на NodeDetailsLoaded)
│   └── tree_handler.py            # TreeUiHandler (подписка на ChildrenLoaded)
├── main_window/                   # Компоненты главного окна
│   ├── __init__.py
│   ├── window.py                  # MainWindow (пустая оболочка QMainWindow)
│   ├── menu.py                    # MenuBar (главное меню)
│   ├── toolbar.py                 # Toolbar (панель инструментов с кнопкой обновления)
│   └── status_bar.py              # StatusBar (строка состояния с индикатором соединения)
└── tree/                          # Виджет дерева объектов
    ├── __init__.py                # Экспорт TreeView, TreeModel
    ├── model.py                   # TreeModel (QAbstractItemModel для TreeNode)
    └── view.py                    # TreeView (QTreeView, эмитит события)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `AppWindow` | `app_window.py` | **Фасад UI слоя** – создаёт все компоненты, предоставляет геттеры для виджетов, подключает сигналы к `EventBus`. |
| `UiCoordinator` | `coordinator.py` | Подписывается на `ShowDetailsPanel` и `CollapseAllRequested`, управляет отображением панели деталей и сворачиванием дерева. |
| `CentralWidget` | `common/central_widget.py` | Контейнер с горизонтальным разделителем: слева `TreeView`, справа `QStackedWidget` с `PlaceholderWidget` и `DetailsPanel`. |
| `DetailsPanel` | `details/panel.py` | Правая панель: содержит `HeaderWidget`, `PlaceholderWidget`, `InfoGrid`, `DetailsTabs`. |
| `DetailsTabs` | `details/details_tabs.py` | Виджет вкладок (Физика, Юрики, Пожарка, Документы). На данном этапе – только заглушки. |
| `HeaderWidget` | `details/header.py` | Шапка панели деталей (иконка, заголовок, статус, иерархия). Пока пустая. |
| `InfoGrid` | `details/info_grid.py` | Сетка для отображения пар «лейбл – значение». Пока пустая. |
| `PlaceholderWidget` | `details/placeholder.py` | Текстовая заглушка «Выберите объект в дереве слева». |
| `PhysicsTab`, `LegalTab`, `SafetyTab`, `DocumentsTab` | `details/tabs/*.py` | Вкладки-заглушки с центрированным текстом. |
| `TreeUiHandler` | `handlers/tree_handler.py` | Подписывается на `ChildrenLoaded`, обновляет `TreeModel` (вставка детей или замена корневых узлов). |
| `DetailsUiHandler` | `handlers/details_handler.py` | Подписывается на `NodeDetailsLoaded`, эмитит `ShowDetailsPanel` (пока только логирует). |
| `MainWindow` | `main_window/window.py` | Пустая оболочка `QMainWindow` – не знает, какие компоненты будут добавлены. |
| `MenuBar` | `main_window/menu.py` | Главное меню (Файл, Справочники, Помощь). Пока без действий. |
| `Toolbar` | `main_window/toolbar.py` | Панель инструментов: сплит-кнопка обновления (3 режима) и кнопка переключения режима (заглушка). Сигнал `refresh_triggered(str)`. |
| `StatusBar` | `main_window/status_bar.py` | Строка состояния: временные сообщения и индикатор соединения (подписка на `ConnectionChanged`). |
| `TreeModel` | `tree/model.py` | `QAbstractItemModel` для отображения `TreeNode`. Поддерживает вставку/удаление детей, кэширует узлы. |
| `TreeView` | `tree/view.py` | `QTreeView`, эмитит `NodeSelected`, `NodeExpanded`, `NodeCollapsed` через `EventBus`. |

---

### Внутренние импорты (только между модулями проекта)

Игнорируем `utils.logger` и стандартные библиотеки.

**Из `app_window.py`**:
- `from src.core import EventBus`
- `from src.core.events.definitions import RefreshRequested`
- `from src.ui.common.central_widget import CentralWidget`
- `from src.ui.main_window.menu import MenuBar`
- `from src.ui.main_window.status_bar import StatusBar`
- `from src.ui.main_window.toolbar import Toolbar`
- `from src.ui.main_window.window import MainWindow`

**Из `coordinator.py`**:
- `from src.core import EventBus`
- `from src.core.events.definitions import CollapseAllRequested, ShowDetailsPanel`
- `from src.ui.app_window import AppWindow`

**Из `common/central_widget.py`**:
- `from src.ui.details import DetailsPanel`
- `from src.ui.details.placeholder import PlaceholderWidget`
- `from src.ui.tree.view import TreeView`

**Из `details/panel.py`**:
- `from src.core import EventBus`
- `from src.ui.details.details_tabs import DetailsTabs`
- `from src.ui.details.header import HeaderWidget`
- `from src.ui.details.info_grid import InfoGrid`
- `from src.ui.details.placeholder import PlaceholderWidget`

**Из `details/details_tabs.py`**:
- `from src.ui.details.tabs.documents import DocumentsTab`
- `from src.ui.details.tabs.legal import LegalTab`
- `from src.ui.details.tabs.physics import PhysicsTab`
- `from src.ui.details.tabs.safety import SafetyTab`

**Из `handlers/tree_handler.py`**:
- `from src.core import EventBus`
- `from src.core.events.definitions import ChildrenLoaded`
- `from src.core.types import ROOT_NODE`
- `from src.ui.tree.model import TreeModel`
- `from src.ui.tree.view import TreeView`

**Из `handlers/details_handler.py`**:
- `from src.core import EventBus`
- `from src.core.events.definitions import NodeDetailsLoaded, ShowDetailsPanel`
- `from src.ui.details.panel import DetailsPanel`

**Из `main_window/status_bar.py`**:
- `from src.core import EventBus`
- `from src.core.events.definitions import ConnectionChanged`

**Из `main_window/toolbar.py`** – нет внутренних импортов (только Qt).

**Из `tree/model.py`**:
- `from src.core.types import NodeType`
- `from src.projections.tree_node import TreeNode`

**Из `tree/view.py`**:
- `from src.core import EventBus`
- `from src.core.events import NodeCollapsed, NodeExpanded, NodeSelected`
- `from src.projections.tree_node import TreeNode`

---

### Экспортируемые классы / функции для точки входа (main.py)

Через `ui/__init__.py` экспортируется только `AppWindow`. Также `UiCoordinator` не экспортируется через `__init__.py`, но используется в `main.py` (предположительно). Публичными для сборки приложения являются:

- `AppWindow` – фасад, создающий все виджеты и предоставляющий доступ к ним.
- `UiCoordinator` (не в `__init__.py`, но может быть импортирован напрямую) – координатор глобальных UI-действий.
- `TreeUiHandler` и `DetailsUiHandler` – используются в `main.py` для подписки на события и обновления UI.
- `TreeView`, `TreeModel`, `DetailsPanel` – могут быть получены через `AppWindow` и переданы в обработчики.

**Основные публичные методы `AppWindow`** (используются в `main.py` и `UiCoordinator`):

| Метод | Назначение |
|-------|-------------|
| `get_tree_view()` | Возвращает `TreeView` для установки модели и передачи в `TreeUiHandler`. |
| `get_details_panel()` | Возвращает `DetailsPanel` для передачи в `DetailsUiHandler`. |
| `get_window() -> QMainWindow` | Возвращает `QMainWindow` для вызова `show()`. |
| `show_details_panel()` | Переключает правую панель с заглушки на `DetailsPanel`. |

**Методы `UiCoordinator`** (вызываются из `main.py`):

| Метод | Назначение |
|-------|-------------|
| `start()` | Подписывается на `ShowDetailsPanel` и `CollapseAllRequested`. |
| `cleanup()` | Отписывается. |

**Методы `TreeUiHandler` и `DetailsUiHandler`**:

| Класс | Метод | Назначение |
|-------|-------|-------------|
| `TreeUiHandler` | `start()` | Устанавливает модель в `TreeView` и подписывается на `ChildrenLoaded`. |
| `TreeUiHandler` | `cleanup()` | Отписывается. |
| `DetailsUiHandler` | `start()` | Подписывается на `NodeDetailsLoaded`. |
| `DetailsUiHandler` | `cleanup()` | Отписывается. |

---

### Итоговое заключение: принципы работы со слоем `ui`

1. **Импорт только сверху вниз** – слой `ui` может импортировать из `core`, `projections` и (в будущем) из `controllers`? **Нет, импорт из `controllers` недопустим** – контроллеры ниже по иерархии. Однако в текущем коде `ui` не импортирует `controllers`, что корректно. Проблема в обратную сторону: `controllers` импортирует `DetailsPanel` из `ui` (нарушение, отмеченное в анализе `controllers`). Это нужно исправить, передавая `DetailsPanel` через интерфейс или событие.

2. **Фасад `AppWindow`** – единственный композиционный корень для UI. Он создаёт все виджеты и предоставляет доступ к ним через геттеры. Никто не должен создавать виджеты напрямую.

3. **Обработчики событий (`TreeUiHandler`, `DetailsUiHandler`, `UiCoordinator`)** – отделены от виджетов. Они подписываются на `EventBus` и обновляют UI. Это позволяет тестировать логику обновления без реальных виджетов.

4. **Модель дерева (`TreeModel`)** – не знает о `EventBus`, бизнес-логике или загрузке данных. Только отображает `TreeNode`. Кэширует узлы для быстрого доступа.

5. **Виджет дерева (`TreeView`)** – эмитит события `NodeSelected`, `NodeExpanded`, `NodeCollapsed` через `EventBus`. Не вызывает никакие сервисы напрямую.

6. **Панель деталей (`DetailsPanel`)** – пока только структурный каркас. При получении `NodeDetailsLoaded` эмитится `ShowDetailsPanel`, но само обновление полей не реализовано (TODO).

7. **Статус бар** – подписывается на `ConnectionChanged` и обновляет индикатор. Использует сигналы Qt для потокобезопасного обновления UI.

8. **Кнопка обновления** – сплит-кнопка с тремя режимами. Сигнал `refresh_triggered` преобразуется в событие `RefreshRequested` в `AppWindow`.

9. **Жизненный цикл** – в `main.py` должны быть вызваны `start()` у обработчиков и `UiCoordinator`, а при завершении – `cleanup()`. Виджеты не требуют явной очистки, кроме `StatusBar.cleanup()`.

10. **Нарушение зависимости** – `controllers/details_controller.py` импортирует `src.ui.details.panel.DetailsPanel`. Это нарушает правило «только сверху вниз». Рекомендуется заменить на событие `ShowDetailsPanel` (уже существует) и убрать прямую ссылку на UI из контроллера.

Слой `ui` является **чисто презентационным** – он отображает данные и передаёт команды, не содержа бизнес-логики или логики доступа к данным.