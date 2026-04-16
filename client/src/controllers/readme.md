## 📋 **СПЕЦИФИКАЦИЯ: CONTROLLERS (СЛОЙ БИЗНЕС-ЛОГИКИ)**

# ============================================
# СПЕЦИФИКАЦИЯ: CONTROLLERS (СЛОЙ БИЗНЕС-ЛОГИКИ)
# ============================================

## 1. НАЗНАЧЕНИЕ
Controllers — это слой бизнес-логики приложения. Они получают события от UI (через EventBus), 
принимают решения о том, какие данные загружать, в каком порядке, и какое состояние обновить. 
Контроллеры не знают о существовании UI, не содержат кода отображения и не хранят состояние 
дольше, чем необходимо для обработки текущего действия.

## 2. ГДЕ ЛЕЖИТ
`client/src/controllers/`

## 3. ЗА ЧТО ОТВЕЧАЕТ
✅ **Отвечает за:**
- **Реакцию на события:** Подписка на события из core.events и принятие решений
- **Координацию загрузки:** Определение, какие данные загружать и в каком порядке
- **Управление состоянием:** Текущий выбранный узел, список раскрытых узлов, контекст
- **Сбор контекста:** Получение имён родителей для отображения в UI
- **Инвалидацию данных:** Решение, когда и какие данные нужно перезагрузить
- **Обработку ошибок:** Преобразование ошибок из нижележащих слоёв в события для UI
- **Подготовку данных для UI:** Формирование структур, готовых к отображению

❌ **НЕ отвечает за:**
- HTTP-запросы (это services/api_client)
- Хранение данных (это data/entity_graph)
- Оркестрацию загрузки (это services/data_loader)
- Отображение (это ui)
- Форматирование для отображения (это ui/formatters)
- Долгосрочное хранение состояния (только временное, в памяти)

## 4. КТО ИСПОЛЬЗУЕТ
✅ **Потребители (вызывают):**
- `ui` — через подписку на события от UI и отправку событий обратно
- `main_window` — при инициализации создаёт контроллеры и передаёт зависимости

✅ **Зависимости (вызывает сам):**
- `core` — типы (NodeType, NodeIdentifier), события (DataLoaded, NodeSelected), шина
- `models` — DTO сущностей (Complex, Building, и т.д.)
- `data` — репозитории (ComplexRepository, BuildingRepository, и т.д.)
- `services` — DataLoader, ConnectionService (через интерфейсы)

❌ **НЕ зависит от:**
- `ui` — контроллеры не знают о виджетах
- `projections` — контроллеры не строят деревья

## 5. КЛЮЧЕВЫЕ ПОНЯТИЯ
- **Бизнес-логика** — правила принятия решений: что загружать, когда инвалидировать
- **Состояние контроллера** — временные данные: текущий выбранный узел, раскрытые узлы
- **Контекст узла** — имена родителей для отображения иерархии
- **Ленивая загрузка** — загрузка детей только при раскрытии узла
- **Инвалидация** — решение о том, какие данные устарели и требуют перезагрузки

## 6. ОГРАНИЧЕНИЯ (важно!)
⛔ **НЕЛЬЗЯ:**
- Хранить долгосрочное состояние (данные должны быть в EntityGraph)
- Импортировать `ui` или `projections`
- Вызывать методы UI напрямую (только через события)
- Содержать логику отображения (форматирование, цвета)
- Содержать HTTP-логику (это в services)
- Содержать логику кэширования (это в data)
- Возвращать `None` вместо исключений (использовать NotFoundError)
- Создавать циклические зависимости между контроллерами

✅ **МОЖНО:**
- Добавлять новые контроллеры под новые сценарии
- Подписываться на новые типы событий
- Использовать репозитории для доступа к данным
- Использовать DataLoader для загрузки
- Собирать контекст из репозиториев
- Эмитить события для UI

## 7. ПРИМЕРЫ

### Базовый контроллер
```python
from src.core import EventBus, NodeIdentifier, NodeType
from src.core.events import NodeSelected, DataLoaded
from src.data import BuildingRepository, ComplexRepository
from src.services import DataLoader
from src.controllers.base import BaseController

class TreeController(BaseController):
    def __init__(self, bus: EventBus, loader: DataLoader,
                 complex_repo: ComplexRepository,
                 building_repo: BuildingRepository):
        super().__init__(bus)
        self._loader = loader
        self._complex_repo = complex_repo
        self._building_repo = building_repo
        self._current_selection: Optional[NodeIdentifier] = None
        
        # Подписка на события
        self._subscribe(NodeSelected, self._on_node_selected)
        self._subscribe(NodeExpanded, self._on_node_expanded)
    
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        """Пользователь выбрал узел."""
        node = event.data.node
        self._current_selection = node
        
        # Загружаем детали (с проверкой кэша)
        details = self._loader.load_details(node.node_type, node.node_id)
        
        # Собираем контекст (имена родителей)
        context = self._get_context(node)
        
        # Отправляем в UI через событие
        self._bus.emit(NodeDetailsLoaded(
            node=node,
            payload=details,
            context=context
        ))
    
    def _get_context(self, node: NodeIdentifier) -> dict:
        """Собирает имена родителей для отображения иерархии."""
        context = {}
        
        # Получаем всех предков из графа
        ancestors = self._graph.get_ancestors(node.node_type, node.node_id)
        
        for anc in ancestors:
            if anc.node_type == NodeType.COMPLEX:
                complex_obj = self._complex_repo.get(anc.node_id)
                context['complex_name'] = complex_obj.name
            elif anc.node_type == NodeType.BUILDING:
                building_obj = self._building_repo.get(anc.node_id)
                context['building_name'] = building_obj.name
        
        return context
```

### Контроллер с инвалидацией
```python
class RefreshController(BaseController):
    def __init__(self, bus: EventBus, loader: DataLoader,
                 complex_repo: ComplexRepository):
        super().__init__(bus)
        self._loader = loader
        self._complex_repo = complex_repo
        
        self._subscribe(RefreshRequested, self._on_refresh_requested)
    
    def _on_refresh_requested(self, event: Event[RefreshRequested]) -> None:
        """Обрабатывает запрос на обновление."""
        mode = event.data.mode
        
        if mode == "current" and self._current_selection:
            # Инвалидируем и перезагружаем
            self._loader.reload_node(
                self._current_selection.node_type,
                self._current_selection.node_id
            )
        elif mode == "full":
            # Полная перезагрузка
            self._loader.clear_cache()
            complexes = self._loader.load_complexes()
            self._bus.emit(DataReloaded(payload=complexes))
```

## 8. РИСКИ
🔴 **Критические:**
- **Хранение состояния вне графа** — приводит к рассинхронизации данных
- **Прямые вызовы UI** — нарушение слоёв, невозможность тестировать
- **Сложная логика в контроллерах** — должен быть тонкий слой

🟡 **Средние:**
- **Слишком много подписок** — утечки памяти (но BaseController решает)
- **Дублирование логики между контроллерами** — выносить в общие методы
- **Игнорирование ошибок** — обязательно логировать и эмитить DataError

🟢 **Контролируемые:**
- **Рост числа контроллеров** — по одному на сценарий, это нормально
- **Сложность отладки** — подробное логирование через log.debug()

============================================
КОНЕЦ СПЕЦИФИКАЦИИ
============================================

# Controllers — описание слоя

## Назначение

Оркестрация UI-событий и бизнес-логики. Единственное место, где хранится состояние приложения (текущий выбор, раскрытые узлы). Подписывается на события `core`, вызывает `services` и `projections`, обновляет `ui`.

**Строгая зависимость:** от `core` (события), `services` (DataLoader, ContextService), `projections` (TreeProjection), `ui` (TreeModel, TreeView, DetailsPanel, AppWindow). Никаких обратных импортов.

---

## Структура

```
controllers/
├── __init__.py              # Публичное API
├── base.py                  # BaseController — подписка/отписка, обработка ошибок
├── tree_controller.py       # TreeController — дерево, состояние, загрузка детей
├── details_controller.py    # DetailsController — панель деталей
├── refresh_controller.py    # RefreshController — обновление данных (3 режима)
└── connection_controller.py # ConnectionController — статус соединения
```

---

## Публичное API

### Импорт

```python
from src.controllers import (
    BaseController,
    TreeController,
    DetailsController,
    RefreshController,
    ConnectionController,
)
```

---

## Компоненты

### 1. BaseController (`base.py`) — базовый класс

Предоставляет общую функциональность для всех контроллеров.

| Метод | Описание |
|-------|----------|
| `_subscribe(event_type, callback)` | Подписывается на событие, сохраняет для автоматической отписки |
| `_emit_error(node, error, extra_context)` | Централизованная эмиссия `DataError` |
| `cleanup()` | Отписывается от всех событий |

**Особенности:**
- Автоматически оборачивает callback для проверки типа события
- Все подписки сохраняются в `_subscriptions` для очистки
- Добавляет контекст контроллера в ошибки

---

### 2. TreeController (`tree_controller.py`) — управление деревом

**Единственное место хранения состояния:**
- `_current_selection: Optional[NodeIdentifier]`
- `_expanded_nodes: Set[NodeIdentifier]`

| Метод | Описание |
|-------|----------|
| `set_app_window(app_window)` | Устанавливает ссылку на фасад окна |
| `load_root_nodes()` | Загружает комплексы при старте |
| `get_current_selection()` | Возвращает текущий выбранный узел |
| `get_expanded_nodes()` | Возвращает копию списка раскрытых узлов |
| `is_expanded(node)` | Проверяет, раскрыт ли узел |

**Обработчики событий:**

| Событие | Действие |
|---------|----------|
| `NodeSelected` | Сохраняет выбор, загружает детали, эмитит `NodeDetailsLoaded` |
| `NodeExpanded` | Сохраняет в `_expanded_nodes`, вызывает `DataLoader.load_children()` |
| `NodeCollapsed` | Удаляет из `_expanded_nodes` |
| `DataLoaded` | Создаёт узлы через `TreeProjection` и вставляет в `TreeModel` (только для детей) |

**Важно:** Вставка узлов происходит ТОЛЬКО в `_on_data_loaded`. Раскрытие только инициирует загрузку.

---

### 3. DetailsController (`details_controller.py`) — панель деталей

| Метод | Описание |
|-------|----------|
| `set_details_panel(panel)` | Устанавливает ссылку на DetailsPanel |

**Обработчики событий:**

| Событие | Действие |
|---------|----------|
| `NodeSelected` | Эмитит `ShowDetailsPanel`, вызывает `DataLoader.load_details()`, эмитит `NodeDetailsLoaded` |

---

### 4. RefreshController (`refresh_controller.py`) — обновление данных

Поддерживает 3 режима обновления.

| Метод | Описание |
|-------|----------|
| `set_current_selection(selection)` | Устанавливает текущий выбор (из TreeController) |
| `set_expanded_nodes(nodes)` | Устанавливает список раскрытых узлов |
| `get_current_selection()` | Возвращает текущий выбор |
| `get_expanded_nodes()` | Возвращает копию раскрытых узлов |

**Обработчики событий:**

| Событие | Действие |
|---------|----------|
| `RefreshRequested` | В зависимости от `mode` вызывает `reload_node()`, `reload_branch()` или `clear_cache()` + `load_complexes()` |

**Режимы обновления:**
- `"current"` — обновить текущий выбранный узел
- `"visible"` — обновить все раскрытые узлы
- `"full"` — полная перезагрузка всех данных

---

### 5. ConnectionController (`connection_controller.py`) — статус соединения

| Метод | Описание |
|-------|----------|
| `is_online()` | Возвращает текущий статус (None = неизвестен) |
| `is_initialized()` | True, если первый статус уже получен |

**Обработчики событий:**

| Событие | Действие |
|---------|----------|
| `ConnectionChanged` | Сохраняет статус, логирует только при изменении (debounce) |

---

## Состояние приложения (где хранится)

| Данные | Где хранится |
|--------|--------------|
| Текущий выбранный узел | `TreeController._current_selection` |
| Список раскрытых узлов | `TreeController._expanded_nodes` |
| Статус соединения | `ConnectionController._is_online` |

**Принцип:** состояние не дублируется в событиях. События — только факты.

---

## Потоки данных

### Выбор узла
```
TreeView → NodeSelected → TreeController (сохраняет выбор)
                        → DetailsController → ShowDetailsPanel
                        → DataLoader.load_details()
                        → NodeDetailsLoaded → DetailsPanel
```

### Раскрытие узла
```
TreeView → NodeExpanded → TreeController → DataLoader.load_children()
                                        → DataLoaded → TreeController
                                        → TreeProjection.build_children_from_payload()
                                        → TreeModel.insert_children()
                                        → ChildrenLoaded
```

### Обновление
```
UI → RefreshRequested → RefreshController → DataLoader.reload_*()
                                          → DataLoaded → обновление UI
```

---

## Зависимости

| Контроллер | Зависит от |
|------------|------------|
| `BaseController` | `core.EventBus` |
| `TreeController` | `BaseController`, `DataLoader`, `ContextService`, `TreeProjection`, `AppWindow`, `TreeModel`, `TreeView` |
| `DetailsController` | `BaseController`, `DataLoader`, `DetailsPanel` |
| `RefreshController` | `BaseController`, `DataLoader` |
| `ConnectionController` | `BaseController` |

---

## Итог

Слой предоставляет вышележащим слоям (UI):

| Возможность | Через |
|-------------|-------|
| Управление деревом | `TreeController` |
| Управление панелью деталей | `DetailsController` |
| Обновление данных | `RefreshController` |
| Статус соединения | `ConnectionController` |
| Базовые механизмы (подписка, ошибки) | `BaseController` |

**Принципы:**
- Контроллеры — единственное место с состоянием приложения
- Не содержат UI-кода (работают через `ui.*` фасады)
- Не содержат бизнес-логики (делегируют в `services`)
- Подписки автоматически очищаются через `cleanup()`