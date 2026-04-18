## Анализ слоя: **controllers** (слой контроллеров — управление потоками данных и состоянием)

### Краткое описание слоя

**Назначение** – координировать взаимодействие между UI, сервисами и шиной событий. Контроллеры подписываются на события из `core`, инициируют загрузку данных через `DataLoader`, обновляют проекции и управляют состоянием приложения (текущий выбор, раскрытые узлы). Слой `controllers` является **мостом между UI и бизнес-логикой**.

**Что делает:**
- Подписывается на события (например, `NodeSelected`, `NodeExpanded`, `RefreshRequested`)
- Эмитит новые события (например, `ShowDetailsPanel`, `CurrentSelectionChanged`, `ExpandedNodesChanged`)
- Управляет жизненным циклом UI-компонентов (создание `TreeView`, подмена панелей через `AppWindow`)
- Хранит состояние приложения: текущий выбранный узел, список раскрытых узлов
- Инициирует загрузку данных через `DataLoader` и обрабатывает результат (`DataLoaded`)
- Строит дерево через `TreeProjection` и обновляет `TreeModel`
- Обрабатывает ошибки централизованно через `_emit_error`

**Что не должен делать:**
- Содержать бизнес-логику предметной области (расчёты, валидацию) – это в `services`
- Содержать прямые манипуляции с DOM/Qt-виджетами (кроме вызовов методов `TreeView`/`TreeModel`/`AppWindow`)
- Импортировать что-либо из `projections` (разрешено), но не должен сам строить узлы – делегирует `TreeProjection`
- Обращаться к API или графу напрямую – только через `DataLoader` и репозитории (через проекции)

**Зависимости:** от `core` (события, `EventBus`, типы), от `services` (`DataLoader`), от `projections` (`TreeProjection`), от `ui` (`AppWindow`, `TreeModel`, `TreeView`, `DetailsPanel`). Также от `utils.logger`. Это **единственный слой, который может импортировать из `ui`** (и то только для управления виджетами, не для бизнес-логики).

---

### Файловая структура слоя

```
client/src/controllers/
├── __init__.py                    # Экспорт BaseController, TreeController, DetailsController, RefreshController, ConnectionController
├── base.py                        # BaseController — базовая подписка/отписка, обработка ошибок
├── tree_controller.py             # TreeController — управление деревом, состояние выбора/раскрытия
├── details_controller.py          # DetailsController — управление панелью деталей
├── refresh_controller.py          # RefreshController — обновление данных (current/visible/full)
└── connection_controller.py       # ConnectionController — отслеживание статуса соединения
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `BaseController` | `base.py` | Абстрактный базовый класс. Предоставляет методы `_subscribe` (автоотписка), `_emit_error` (централизованная эмиссия `DataError`), `cleanup` (отписка от всех событий). Хранит список функций отписки и обёрток. |
| `TreeController` | `tree_controller.py` | **Главный контроллер дерева.** Подписывается на `NodeSelected`, `NodeExpanded`, `NodeCollapsed`, `DataLoaded`, `CollapseAllRequested`. Хранит `_current_selection` и `_expanded_nodes`. Инициирует загрузку корневых узлов (`load_root_nodes`), загрузку детей при раскрытии, обрабатывает загруженные данные (`_on_data_loaded` – единственное место создания и вставки узлов). Управляет созданием `TreeView` и подменой панели через `AppWindow`. |
| `DetailsController` | `details_controller.py` | Управляет панелью деталей. Подписывается на `NodeSelected`. При выборе узла эмитит `ShowDetailsPanel`, загружает детали через `DataLoader.load_details`, отправляет результат через `NodeDetailsLoaded`. |
| `RefreshController` | `refresh_controller.py` | Обрабатывает запросы обновления (`RefreshRequested`). Поддерживает три режима: `current` (текущий узел), `visible` (все раскрытые узлы), `full` (очистка кэша + сворачивание дерева + перезагрузка комплексов). Подписывается на `CurrentSelectionChanged` и `ExpandedNodesChanged` для синхронизации состояния. |
| `ConnectionController` | `connection_controller.py` | Отслеживает статус соединения через событие `ConnectionChanged`. Логирует изменения статуса и предоставляет методы `is_online()` и `is_initialized()`. Не эмитит события, только хранит состояние. |

---

### Внутренние импорты (только между модулями controllers, core, services, projections, ui, utils)

**Из `core`:**  
- `EventBus`, `EventData`, `NodeIdentifier`, `NodeType`
- События: `NodeSelected`, `NodeExpanded`, `NodeCollapsed`, `DataLoaded`, `DataLoadedKind`, `ChildrenLoaded`, `NodeDetailsLoaded`, `ShowDetailsPanel`, `RefreshRequested`, `CollapseAllRequested`, `CurrentSelectionChanged`, `ExpandedNodesChanged`, `ConnectionChanged`, `DataError`

**Из `services`:**  
- `DataLoader`

**Из `projections`:**  
- `TreeProjection`, `TreeNode`

**Из `ui`:**  
- `AppWindow`, `TreeModel`, `TreeView`, `DetailsPanel`

**Из `utils.logger`** – везде.

**Между контроллерами:**  
- `TreeController` не импортирует другие контроллеры (только через события)
- `RefreshController` использует `DataLoader` и события, но не другие контроллеры
- `DetailsController` использует `DataLoader`, но не другие контроллеры

**Никаких импортов из `data` или `models` напрямую** (всё через `services` и `projections`).

---

### Экспортируемые методы / классы для вышестоящих слоёв (главным образом для `ui`)

Публичное API слоя `controllers` доступно через `from src.controllers import ...` (согласно `controllers/__init__.py`):

**Классы:**
- `BaseController` (обычно не используется напрямую, но может быть расширен)
- `TreeController`
- `DetailsController`
- `RefreshController`
- `ConnectionController`

**Методы `TreeController`:**
- `set_app_window(app_window: AppWindow) -> None` – передаёт ссылку на фасад главного окна для подмены панелей.
- `load_root_nodes() -> None` – загружает комплексы при старте и создаёт `TreeView`.

**Методы `DetailsController`:**
- `set_details_panel(panel: DetailsPanel) -> None` – устанавливает панель для отображения деталей.

**Методы `RefreshController`:** (публичных методов нет, только подписки на события)

**Методы `ConnectionController`:**
- `is_online() -> Optional[bool]` – возвращает текущий статус соединения (None – ещё не определён).
- `is_initialized() -> bool` – True, если первый статус уже получен.

**Методы `BaseController` (наследуются):**
- `cleanup() -> None` – отписывается от всех событий. Должен вызываться при завершении работы контроллера.

---

### Итоговое заключение: принципы работы со слоем `controllers`

1. **Зависимость от `ui` разрешена, но только для управления виджетами** – контроллеры могут импортировать `AppWindow`, `TreeModel`, `TreeView`, `DetailsPanel`, чтобы создавать/обновлять UI. Однако **никакой бизнес-логики в этих вызовах быть не должно** (только вызовы методов типа `setModel`, `set_event_bus`, `collapse_all`).

2. **Все контроллеры должны наследовать `BaseController`** – это гарантирует автоматическую отписку от событий при `cleanup()` и единообразную обработку ошибок через `_emit_error`.

3. **Состояние хранится только в контроллерах** – `TreeController` является единственным источником правды для `_current_selection` и `_expanded_nodes`. Он эмитит события `CurrentSelectionChanged` и `ExpandedNodesChanged`, на которые подписываются другие контроллеры (например, `RefreshController`). Это предотвращает дублирование состояния.

4. **Загрузка данных инициируется контроллерами, но не выполняется ими** – контроллеры вызывают методы `DataLoader` (например, `load_children`, `load_details`), а результат приходит через событие `DataLoaded`. Обработка `DataLoaded` (создание узлов, вставка в модель) происходит в `TreeController._on_data_loaded` – **единственном месте**, где создаются `TreeNode`.

5. **Никогда не обращайтесь к репозиториям или графу напрямую из контроллера** – только через `DataLoader` и `TreeProjection`. Исключение: `TreeProjection` сам использует репозитории, но это деталь реализации проекции.

6. **Контроллеры не должны содержать логику форматирования** – для этого есть `projections`. Например, `TreeController` не форматирует имя этажа, а вызывает `TreeProjection.build_children_from_payload`.

7. **Жизненный цикл** – при создании приложения создаются все контроллеры, им передаётся `EventBus` и `DataLoader`. Затем вызывается `TreeController.load_root_nodes()`. При завершении приложения вызывается `cleanup()` у каждого контроллера (обычно в деструкторе `MainWindow`).

8. **Обработка ошибок** – используйте `self._emit_error(node, exception)` для отправки `DataError` в шину. UI может подписаться на `DataError` и показать сообщение.

9. **Расширение** – при добавлении нового функционала:
   - Создайте новый контроллер, наследующий `BaseController`
   - Подпишитесь на нужные события в конструкторе
   - Добавьте публичные методы для взаимодействия с UI (если нужно)
   - Экспортируйте в `controllers/__init__.py`
   - Создайте экземпляр контроллера в `main.py` или `App` и передайте ему зависимости

Слой `controllers` является **единственным местом, где UI знает о данных и наоборот**. Он обеспечивает слабую связанность через события и централизованное управление состоянием, позволяя легко тестировать логику без реального UI.