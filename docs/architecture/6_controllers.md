## Анализ слоя: **controllers** (слой контроллеров)

### Краткое описание слоя

**Назначение** – координировать поток данных между сервисами, проекциями и UI-слоем. Контроллеры являются "мозгом" приложения: они подписываются на события, принимают решения, вызывают сервисы и генерируют новые события. Они **не знают** о конкретных виджетах (Qt), но знают о событиях, которые эти виджеты порождают.

**Что делает:**
- Подписывается на события от UI (через `EventBus`) и реагирует на них
- Хранит состояние приложения (раскрытые узлы, текущий выбор)
- Вызывает сервисы (`DataLoader`, `ContextService`) для загрузки данных
- Преобразует результаты в события для UI (`ChildrenLoaded`, `NodeDetailsLoaded`)
- Обрабатывает ошибки и эмитит `DataError`
- Управляет жизненным циклом подписок (автоматическая отписка через `cleanup()`)

**Что не должен делать:**
- Содержать UI-специфичный код (работа с виджетами, QTimer, QThread)
- Выполнять HTTP-запросы напрямую (только через `services`)
- Хранить DTO или бизнес-данные (только идентификаторы и состояния)
- Форматировать данные для отображения (это `projections`)
- Содержать бизнес-правила предметной области

---

### Файловая структура слоя

```
client/src/controllers/
├── __init__.py                    # Публичное API контроллеров
├── base.py                        # BaseController (подписки, отписки, ошибки)
├── tree_controller.py             # TreeController (дерево, раскрытие узлов)
├── details_controller.py          # DetailsController (выбор узла, детали)
├── refresh_controller.py          # RefreshController (обновление данных: F5)
└── connection_controller.py       # ConnectionController (статус соединения)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `BaseController` | `base.py` | Абстрактный базовый контроллер. Управляет подписками (автоматическая отписка в `cleanup()`). Предоставляет `_subscribe()` и `_emit_error()`. |
| `TreeController` | `tree_controller.py` | Управление деревом. Хранит множество раскрытых узлов. При раскрытии узла вызывает `DataLoader` для загрузки детей. Эмитит `ChildrenLoaded` и `ExpandedNodesChanged`. |
| `DetailsController` | `details_controller.py` | Управление панелью деталей. Хранит текущий выбранный узел (единственный источник правды). При выборе узла загружает детали через `DataLoader` и эмитит `NodeDetailsLoaded`. |
| `RefreshController` | `refresh_controller.py` | Управление обновлением данных. Поддерживает три режима: `current` (текущий узел), `visible` (раскрытые узлы), `full` (полная перезагрузка). |
| `ConnectionController` | `connection_controller.py` | Мониторинг соединения. Следит за событиями `ConnectionChanged`, хранит текущий статус. Эмитит события только при реальном изменении (debounce). |

---

### Внутренние импорты (только между модулями controllers)

**Из `base.py`:**
- `from src.core import EventBus`
- `from src.core.events.definitions import DataError`
- `from src.core.types import EventData, NodeIdentifier`

**Из `tree_controller.py`:**
- `from .base import BaseController`
- `from src.core.events.definitions import (ChildrenLoaded, CollapseAllRequested, DataLoaded, DataLoadedKind, ExpandedNodesChanged, NodeCollapsed, NodeExpanded)`
- `from src.core.types import NodeIdentifier, NodeType, ROOT_NODE`
- `from src.projections.tree import TreeProjection`
- `from src.services import DataLoader`

**Из `details_controller.py`:**
- `from .base import BaseController`
- `from src.core.events.definitions import (CurrentSelectionChanged, NodeDetailsLoaded, NodeSelected)`
- `from src.core.types.nodes import NodeIdentifier, NodeType`
- `from src.services.data_loader import DataLoader`

**Из `refresh_controller.py`:**
- `from .base import BaseController`
- `from src.core.events.definitions import (CollapseAllRequested, CurrentSelectionChanged, ExpandedNodesChanged, RefreshRequested)`
- `from src.core.types import NodeIdentifier`
- `from src.services import DataLoader`

**Из `connection_controller.py`:**
- `from .base import BaseController`
- `from src.core.events.definitions import ConnectionChanged`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вся публичная поверхность слоя `controllers` доступна через импорт из `src.controllers`:

**`BaseController` (абстрактный, не создаётся напрямую):**
- `__init__(bus: EventBus)`
- `cleanup() -> None` – отписывается от всех событий (вызывается при завершении)

**`TreeController`:**
- `__init__(bus: EventBus, loader: DataLoader, tree_projection: TreeProjection)`
- `load_root_nodes() -> None` – загружает комплексы при старте приложения

**`DetailsController`:**
- `__init__(bus: EventBus, loader: DataLoader)`
- (нет публичных методов – работает через события)

**`RefreshController`:**
- `__init__(bus: EventBus, loader: DataLoader)`
- (нет публичных методов – работает через события)

**`ConnectionController`:**
- `__init__(bus: EventBus)`
- `is_online() -> Optional[bool]` – текущий статус соединения
- `is_initialized() -> bool` – получен ли первый статус

---

### Итоговое заключение: принципы работы со слоём `controllers`

1. **Импорт только сверху вниз** – вышестоящий слой (`ui`) может импортировать из `controllers` свободно. Контроллеры могут импортировать:
   - `core` – для `EventBus`, типов, событий
   - `services` – для `DataLoader`
   - `projections` – для `TreeProjection`
   - `data` – для репозиториев (только если необходимо, но предпочтительнее через `services`)

2. **Запрещены обратные импорты** – контроллеры не должны импортировать ничего из `ui`. Вся коммуникация с UI происходит через `EventBus`.

3. **Единый источник правды** – контроллеры хранят состояние приложения:
   - `TreeController._expanded_nodes` – раскрытые узлы
   - `DetailsController._current_selection` – текущий выбранный узел
   - `RefreshController` копирует эти состояния через события
   - `ConnectionController._is_online` – статус соединения

4. **Автоматическое управление подписками** – используйте `self._subscribe(event_type, callback)` вместо прямого `bus.subscribe()`. Это сохраняет функцию отписки и автоматически очищает подписки при вызове `cleanup()`.

5. **Централизованная обработка ошибок** – используйте `self._emit_error(node, exception, extra_context)` для эмиссии `DataError`. Метод автоматически собирает контекст (имя контроллера, тип ошибки).

6. **Контроллеры не знают о виджетах** – они работают с событиями и идентификаторами. Например, `TreeController` не знает о `QTreeView` или `TreeModel` – он только эмитит `ChildrenLoaded`, а UI-слой сам решает, как вставить узлы в модель.

7. **Поток данных (пример – выбор узла):**
   ```
   TreeView (UI) → эмитит NodeSelected
   DetailsController._on_node_selected() → обрабатывает
       → обновляет _current_selection
       → эмитит CurrentSelectionChanged (для RefreshController)
       → вызывает DataLoader.load_*_detail()
   DataLoader → эмитит DataLoaded (kind=DETAILS)
   DetailsController (не обрабатывает DETAILS в текущей версии)
   DetailsUiHandler → подписан на NodeDetailsLoaded
   ```

8. **Поток данных (раскрытие узла):**
   ```
   TreeView (UI) → эмитит NodeExpanded
   TreeController._on_node_expanded()
       → добавляет узел в _expanded_nodes
       → вызывает DataLoader.load_*_tree() (ленивая загрузка)
   DataLoader → загружает детей, сохраняет в граф, эмитит DataLoaded (kind=CHILDREN)
   TreeController._on_data_loaded() → получает DataLoaded
       → создаёт TreeNode через TreeProjection.build_children_from_payload()
       → эмитит ChildrenLoaded
   TreeModel (UI) → подписан на ChildrenLoaded → обновляет модель
   ```

9. **Режимы обновления (RefreshController):**
   - `current` (F5) – обновить только выбранный узел (`reload_node`)
   - `visible` (Ctrl+F5) – обновить все раскрытые узлы
   - `full` (Ctrl+Shift+F5) – очистить кэш → свернуть дерево → загрузить комплексы

10. **ConnectionController – debounce** – хранит предыдущий статус и эмитит события только при реальном изменении. Первый полученный статус сохраняется, но не эмитится как изменение.

11. **Жизненный цикл контроллеров** – создаются в `main.py` (или фабрике) и передаются в `MainWindow`. При завершении приложения вызывается `cleanup()` на всех контроллерах.

12. **Cleanup обязателен** – всегда вызывайте `cleanup()` перед удалением контроллера. Игнорирование приводит к утечкам памяти (слабые ссылки могут не сработать вовремя) и "мёртвым" обработчикам.

13. **Типизация событий** – `_subscribe()` использует wrapper для проверки типа полученного события. Это защита от багов, когда обработчик подписан на один тип, а получает другой.

Слой `controllers` является **координатором между бизнес-логикой и UI**. Он не содержит ни бизнес-правил, ни кода отображения – только "клей", который связывает события, сервисы и проекции в осмысленный поток данных. Контроллеры легко тестируются в изоляции от виджетов, так как все зависимости передаются через конструктор, а коммуникация идёт через `EventBus`.