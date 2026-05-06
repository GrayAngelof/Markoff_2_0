## Анализ слоя «controllers»

### Краткое описание слоя

Слой **controllers** — это **управляющий слой** приложения. Он находится между `projections` и `view models/ui`. Его задачи:

- **Подписка на события от UI** (например, `NodeSelected`, `NodeExpanded`, `RefreshRequested`) и координация ответных действий.
- **Управление состоянием приложения** (текущий выбранный узел — в `DetailsController`, список раскрытых узлов — в `TreeController`).
- **Оркестрация загрузки данных** через `DataLoader` (из слоя `services`).
- **Преобразование данных для UI** — использование `TreeProjection` и `DetailsProjection` из слоя `projections`.
- **Эмиссия событий для UI** (`ChildrenLoaded`, `NodeDetailsLoaded`, `ExpandedNodesChanged`, `CurrentSelectionChanged`, `CollapseAllRequested`).

**Что слой НЕ должен делать:**
- Не содержит код отображения (UI).
- Не импортирует `view models` или `ui` напрямую.
- Не выполняет HTTP-запросы самостоятельно (делегирует `DataLoader`).
- Не хранит DTO или данные (только идентификаторы и состояние раскрытия/выбора).

---

### Файловая структура слоя

```
src/controllers/
├── __init__.py                 # Публичное API (TreeController, DetailsController, RefreshController, ConnectionController)
├── base.py                     # BaseController — общая подписка/отписка, обработка ошибок
├── tree_controller.py          # TreeController — раскрытие/сворачивание, загрузка детей, состояние раскрытых узлов
├── details_controller.py       # DetailsController — выбор узла, загрузка деталей, эмиссия NodeDetailsLoaded
├── refresh_controller.py       # RefreshController — обновление данных (current/visible/full)
└── connection_controller.py    # ConnectionController — отслеживание статуса соединения (без UI)
```

---

### Описание внутренних классов

| Класс | Назначение |
|-------|-------------|
| `BaseController` | Абстрактный базовый класс для всех контроллеров. Предоставляет: <br> - метод `_subscribe(event_type, callback)` — подписка с автосохранением unsubscribe-функции; <br> - `cleanup()` — отписка от всех событий; <br> - `_emit_error()` — централизованная эмиссия `DataError`. |
| `TreeController` | Управление деревом. Хранит `_expanded_nodes: Set[NodeIdentifier]`. <br> Подписан на `NodeExpanded`, `NodeCollapsed`, `DataLoaded`, `CollapseAllRequested`. <br> При раскрытии узла вызывает `DataLoader.load_*_tree()`. <br> При получении `DataLoaded` (kind=CHILDREN) строит `TreeNode` через `TreeProjection` и эмиттит `ChildrenLoaded`. <br> Эмиттит `ExpandedNodesChanged` при изменении списка раскрытых узлов. |
| `DetailsController` | Управление панелью деталей. Хранит `_current_selection`. <br> Подписан на `NodeSelected`. Обновляет выбор, эмиттит `CurrentSelectionChanged`. <br> Загружает детали через `DataLoader`, преобразует через `DetailsProjection` и эмиттит `NodeDetailsLoaded`. |
| `RefreshController` | Обработка запросов обновления (F5 и т.д.). Подписан на `RefreshRequested`, а также на `CurrentSelectionChanged` и `ExpandedNodesChanged` для отслеживания состояния. <br> Поддерживает режимы: <br> - `current` — перезагружает текущий выбранный узел (`reload_node`); <br> - `visible` — перезагружает все раскрытые узлы; <br> - `full` — очищает кэш, сворачивает все узлы (`CollapseAllRequested`), загружает комплексы заново. |
| `ConnectionController` | Отслеживает статус соединения через событие `ConnectionChanged`. Хранит `_is_online` и `_initial_status_received`. Не эмитит события, только предоставляет методы `is_online()` и `is_initialized()` для других контроллеров/UI. |

Все контроллеры наследуются от `BaseController` и используют его механизм подписки.

---

### Список внутренних импортов (только внутри controllers и вниз)

**Импорты из `core`**:
- `from src.core.event_bus import EventBus`
- `from src.core.events.definitions import` (все события, на которые подписываются или которые эмитят: `NodeSelected`, `NodeExpanded`, `NodeCollapsed`, `DataLoaded`, `ChildrenLoaded`, `NodeDetailsLoaded`, `RefreshRequested`, `CurrentSelectionChanged`, `ExpandedNodesChanged`, `CollapseAllRequested`, `ConnectionChanged`, `DataError`)
- `from src.core.types import EventData, NodeIdentifier, NodeType, ROOT_NODE`
- `from src.core.types.protocols import IDetailsViewModel`

**Импорты из `services`**:
- `from src.services import DataLoader` (и в `refresh_controller.py` также `DataLoader`)

**Импорты из `projections`**:
- `from src.projections.details_projection import DetailsProjection`
- `from src.projections.tree import TreeProjection`

**Импорты из `utils`**: `get_logger`

**Импорты внутри `controllers`**:
- `from .base import BaseController`

**⚠️ Примечание:** Контроллеры **не импортируют** `view models` и `ui`. Они общаются с вышестоящими слоями только через события `EventBus`.

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящие слои (`view models`, `ui`) **импортируют из `src.controllers`**:

#### 1. `TreeController`

| Метод | Назначение |
|-------|-------------|
| `__init__(bus, loader, tree_projection)` | Создать контроллер дерева. |
| `load_root_nodes()` | Загрузить корневые узлы (комплексы) при старте. Вызывается один раз после инициализации. |
| `cleanup()` | Отписаться от событий и очистить состояние. |

Контроллер **не имеет публичных геттеров** для состояния раскрытых узлов — состояние передаётся через события `ExpandedNodesChanged`.

#### 2. `DetailsController`

| Метод | Назначение |
|-------|-------------|
| `__init__(bus, loader, projection)` | Создать контроллер деталей. |
| `cleanup()` | Очистить состояние и отписаться. |

Состояние выбора не доступно напрямую — только через `CurrentSelectionChanged`.

#### 3. `RefreshController`

| Метод | Назначение |
|-------|-------------|
| `__init__(bus, loader)` | Создать контроллер обновления. |
| `cleanup()` | Отписаться. |

Контроллер не имеет публичных методов — всё через события.

#### 4. `ConnectionController`

| Метод | Назначение |
|-------|-------------|
| `__init__(bus)` | Создать контроллер соединения. |
| `is_online() -> Optional[bool]` | Вернуть текущий статус (`True`/`False`/`None` — неизвестно). |
| `is_initialized() -> bool` | `True`, если первый статус уже получен. |
| `cleanup()` | Отписаться. |

---

### Итоговое заключение

**Принципы работы со слоем `controllers`:**

1. **Импорт только из `src.controllers`** — используйте `TreeController`, `DetailsController`, `RefreshController`, `ConnectionController`. Никогда не импортируйте `base.py` напрямую.

2. **Контроллеры — единственный источник истины для состояния UI** (выбранный узел, раскрытые узлы). UI не должен хранить своё состояние, а должен получать его через события и передавать действия через события.

3. **Все контроллеры должны быть очищены** при завершении работы приложения (вызов `cleanup()`), чтобы предотвратить утечки памяти (слабые ссылки в `EventBus` не удаляют подписки мгновенно).

4. **Использование `BaseController._subscribe`** — обязательно для всех подписок, чтобы `cleanup()` мог автоматически отписаться.

5. **Контроллеры не блокируют UI** — загрузка данных через `DataLoader` асинхронна (внутри используются callback и события). Не нужно создавать дополнительные потоки.

6. **Ошибки обрабатываются централизованно** — метод `_emit_error()` генерирует `DataError`, который может быть перехвачен UI для показа уведомлений.

7. **Связь между контроллерами** — через события `EventBus`. Например, `RefreshController` подписывается на `CurrentSelectionChanged` и `ExpandedNodesChanged`, которые эмитят `TreeController` и `DetailsController`.

8. **Тестирование** — контроллеры легко тестировать, передавая мок-объекты `EventBus`, `DataLoader` и `Projection`. Проверять эмитированные события и вызовы методов загрузчика.

Слой `controllers` является **мостом между UI-событиями и бизнес-логикой/данными**. Он не знает о виджетах, но управляет их состоянием через события. Это позволяет менять UI-фреймворк (Qt, Tkinter, веб) без изменения контроллеров.