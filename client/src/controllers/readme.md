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

**Controllers — это мозг приложения, который получает сигналы от UI, принимает решения, использует сервисы для загрузки данных и отправляет результаты обратно через события.** 

## 📚 **СЛОЙ CONTROLLERS**

Спасибо за детальный разбор! Учитывая все замечания, представляю исправленную версию.

---

## 1. **НАЗНАЧЕНИЕ И МЕСТО В АРХИТЕКТУРЕ**

Controllers — это **слой координации потока данных**, расположенный между сервисным слоем (`services`) и пользовательским интерфейсом (`ui`). Контроллеры получают события от UI через EventBus, **координируют вызовы сервисов**, управляют временным состоянием приложения (текущий выбранный узел, список раскрытых узлов) и генерируют новые события для UI.

**Важное уточнение:** Контроллеры **не содержат бизнес-логику** в классическом понимании — они не содержат правил валидации, расчётов или алгоритмов предметной области. Бизнес-правила остаются в `DataLoader` и `ContextService`. Контроллеры только **координируют поток данных** между слоями.

### **Место в иерархии**
```
ui (пользовательский интерфейс)
      ↑ (события)
controllers (координация потока данных) ←──────┐
      ↓ (вызовы)                               │
services (бизнес-правила, оркестрация)         │
      ↓                                        │
data (хранение)                                │
      ↓                                        │
models (структуры)                             │
      ↓                                        │
core (типы, события) ──────────────────────────┘
```

**Ключевое правило:** Контроллеры могут импортировать `core`, `models`, `data`, `services`, но НЕ могут импортировать `ui` и `projections`. Коммуникация с UI происходит только через EventBus с типизированными событиями.

---

## 2. **СТРУКТУРА СЛОЯ**

```
controllers/
├── __init__.py                 # Публичное API (экспорт всех контроллеров)
├── base.py                     # BaseController (абстрактный базовый класс)
├── tree_controller.py          # TreeController (управление деревом)
├── details_controller.py       # DetailsController (панель деталей)
├── refresh_controller.py       # RefreshController (обновление данных)
└── connection_controller.py    # ConnectionController (статус соединения)
```

**Принцип:** Каждый контроллер отвечает за одну логическую область. Нет внутренних подпапок — все контроллеры находятся на верхнем уровне, так как это публичный API слоя.

---

## 3. **КОМПОНЕНТЫ СЛОЯ**

### 3.1. **BaseController — базовый класс**

```python
from controllers.base import BaseController
```

**Ответственность:**
- Единая подписка на типизированные события с сохранением для отписки
- Централизованная обработка ошибок через `_emit_error`
- Метод `cleanup()` для освобождения ресурсов
- Логирование подписок и отписок

**Публичные методы:**

| Метод | Описание |
|-------|----------|
| `cleanup()` | Отписывается от всех событий и освобождает ресурсы |

**Защищённые методы (для наследников):**

| Метод | Описание |
|-------|----------|
| `_subscribe(event_type, callback)` | Подписка на событие с сохранением |
| `_emit_error(node, error, extra_context)` | Централизованная эмиссия ошибок |

**Пример использования:**
```python
class MyController(BaseController):
    def __init__(self, bus: EventBus):
        super().__init__(bus)
        self._subscribe(NodeSelected, self._on_node_selected)
    
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        try:
            # координация
            pass
        except Exception as e:
            self._emit_error(event.data.node, e)
```

---

### 3.2. **TreeController — управление деревом**

```python
from src.controllers import TreeController
```

**Ответственность:**
- Обработка выбора узла (`NodeSelected`)
- Обработка раскрытия/сворачивания узла (`NodeExpanded`, `NodeCollapsed`)
- **Координация** загрузки деталей узла через `DataLoader`
- **Координация** загрузки детей узла при раскрытии
- Сбор контекста (имена родителей) через `ContextService`
- **Единственное место**, где хранится **временное состояние**:
  - `_current_selection` — текущий выбранный узел
  - `_expanded_nodes` — множество раскрытых узлов
- Эмиссия событий состояния (`CurrentSelectionChanged`, `ExpandedNodesChanged`)
- Эмиссия событий для UI (`NodeDetailsLoaded[Building]`, `ChildrenLoaded[Building]`)

**Публичные методы:**

| Метод | Описание |
|-------|----------|
| `get_current_selection()` | Возвращает текущий выбранный узел |
| `get_expanded_nodes()` | Возвращает копию списка раскрытых узлов |
| `is_expanded(node)` | Проверяет, раскрыт ли узел |

**Генерируемые события:**

| Событие (типизированное) | Когда | Данные |
|--------------------------|-------|--------|
| `CurrentSelectionChanged` | Изменился выбранный узел | `selection: NodeIdentifier` |
| `ExpandedNodesChanged` | Изменился список раскрытых узлов | `expanded_nodes: Set[NodeIdentifier]` |
| `NodeDetailsLoaded[T]` | Загружены детали узла | `node: NodeIdentifier`, `payload: T`, `context: dict` |
| `ChildrenLoaded[T]` | Загружены дети узла | `parent: NodeIdentifier`, `children: List[T]` |

**Состояние (единственный источник правды):**
```python
self._current_selection: Optional[NodeIdentifier] = None
self._expanded_nodes: Set[NodeIdentifier] = set()
```

---

### 3.3. **DetailsController — панель деталей**

```python
from src.controllers import DetailsController
```

**Ответственность:**
- Запоминание текущего выбранного узла
- **Координация** загрузки связанных данных (владельцы, контакты) через `DataLoader`
- Реакция на переключение вкладок (`TabChanged`)
- Эмиссия событий с детальными данными

**Важное уточнение:** `DataLoader.load_building_with_owner()` возвращает типизированный `BuildingWithOwnerResult` (dataclass), а не словарь. В контроллере **нельзя использовать `.get()`** — только прямой доступ к атрибутам: `result.building`, `result.owner`, `result.responsible_persons`.

**Публичные методы:**

| Метод | Описание |
|-------|----------|
| `get_current_node()` | Возвращает текущий выбранный узел |

**Генерируемые события:**

| Событие | Когда | Данные |
|---------|-------|--------|
| `BuildingDetailsLoaded` | Загружены детали корпуса с владельцем | `building: Building`, `owner: Optional[Counterparty]`, `responsible_persons: List[ResponsiblePerson]` |

**Ключевая особенность:** Контроллер **не принимает решений** о загрузке — он только вызывает `DataLoader.load_building_with_owner()`, который сам проверяет кэш и решает, что загружать. Бизнес-правила (например, "если у корпуса есть владелец, загрузить его") находятся в DataLoader.

---

### 3.4. **RefreshController — обновление данных**

```python
from src.controllers import RefreshController
```

**Ответственность:**
- Обработка запросов на обновление (`RefreshRequested`)
- Поддержка трёх режимов:
  - `current` — обновить текущий выбранный узел
  - `visible` — обновить все раскрытые узлы
  - `full` — полная перезагрузка всех данных
- **Не хранит состояние** — получает его через события:
  - `CurrentSelectionChanged` — текущий выбранный узел
  - `ExpandedNodesChanged` — список раскрытых узлов

**Реактивность:** Все данные приходят синхронно через события, что делает слой реактивным. При изменении состояния в TreeController, RefreshController автоматически получает актуальные значения.

**Публичные методы:**

| Метод | Описание |
|-------|----------|
| `get_current_selection()` | Возвращает текущий выбранный узел |
| `get_expanded_nodes()` | Возвращает копию списка раскрытых узлов |

**Генерируемые события:**

| Событие | Когда | Данные |
|---------|-------|--------|
| `NodeReloaded` | Узел перезагружен | `node: NodeIdentifier` |
| `VisibleNodesReloaded` | Все раскрытые узлы перезагружены | `count: int` |
| `FullReloadCompleted` | Полная перезагрузка завершена | `count: int` |

**Ключевая особенность:** RefreshController **не хранит состояние** — всё состояние приходит из событий. Это гарантирует, что состояние всегда синхронизировано с TreeController и не может рассинхронизироваться.

---

### 3.5. **ConnectionController — статус соединения**

```python
from src.controllers import ConnectionController
```

**Ответственность:**
- Отслеживание статуса соединения через событие `ConnectionChanged`
- **Debounce** — эмитит события только при реальном изменении статуса
- Генерация событий для UI при изменении статуса

**Публичные методы:**

| Метод | Описание |
|-------|----------|
| `is_online()` | Возвращает текущий статус соединения |

**Генерируемые события:**

| Событие | Когда | Данные |
|---------|-------|--------|
| `NetworkActionsEnabled` | Соединение восстановлено (офлайн → онлайн) | — |
| `NetworkActionsDisabled` | Соединение потеряно (онлайн → офлайн) | — |

**Ключевая особенность:** При первом запуске `_is_online = None`, что позволяет UI корректно обработать первый статус без лишних событий. События эмитятся только при реальном изменении статуса, что предотвращает flood.

---

## 4. **ПОТОКИ ДАННЫХ**

### 4.1. **Выбор узла в дереве**

```
[UI] испускает NodeSelected(node=BUILDING#101)
    │
    ▼
[TreeController] _on_node_selected(event: Event[NodeSelected])
    │
    ├─→ сохраняет _current_selection
    ├─→ эмитит CurrentSelectionChanged(selection=node)
    ├─→ вызывает loader.load_details(BUILDING, 101) → возвращает Building
    │        │
    │        ▼
    │   [DataLoader] проверяет кэш → если нет → загружает через API
    │
    ├─→ вызывает context_service.get_context(node)
    │        │
    │        ▼
    │   [ContextService] собирает имена родителей
    │
    └─→ эмитит NodeDetailsLoaded[Building](
            node=node, 
            payload=building, 
            context={'complex_name': 'Северный'}
        )
    │
    ▼
[UI] получает NodeDetailsLoaded[Building] → отображает в панели деталей
    │
    ▼
[DetailsController] _on_node_selected(event: Event[NodeSelected])
    │
    └─→ если BUILDING → вызывает loader.load_building_with_owner(101)
             │
             ▼
        [DataLoader] загружает корпус + владельца + контакты
        возвращает BuildingWithOwnerResult (dataclass)
             │
             ▼
        эмитит BuildingDetailsLoaded(
            building=result.building,
            owner=result.owner,
            responsible_persons=result.responsible_persons
        )
    │
    ▼
[UI] получает BuildingDetailsLoaded → обновляет вкладку контактов
```

### 4.2. **Раскрытие узла в дереве**

```
[UI] испускает NodeExpanded(node=COMPLEX#42)
    │
    ▼
[TreeController] _on_node_expanded(event: Event[NodeExpanded])
    │
    ├─→ добавляет в _expanded_nodes
    ├─→ эмитит ExpandedNodesChanged(expanded_nodes=...)
    ├─→ определяет child_type = BUILDING
    ├─→ вызывает loader.load_children(COMPLEX, 42, BUILDING)
    │        │
    │        ▼
    │   [DataLoader] проверяет кэш → если нет → загружает через API
    │   возвращает List[Building]
    │
    └─→ эмитит ChildrenLoaded[Building](
            parent=COMPLEX#42, 
            children=[Building(...), ...]
        )
    │
    ▼
[UI] получает ChildrenLoaded[Building] → обновляет дерево
```

### 4.3. **Обновление данных (F5)**

```
[UI] испускает RefreshRequested(mode="current")
    │
    ▼
[RefreshController] _on_refresh_requested(event: Event[RefreshRequested])
    │
    ├─→ проверяет self._current_selection (из события CurrentSelectionChanged)
    ├─→ вызывает loader.reload_node(BUILDING, 101)
    │        │
    │        ▼
    │   [DataLoader] инвалидирует в графе → загружает заново
    │
    └─→ эмитит NodeReloaded(node=BUILDING#101)
    │
    ▼
[UI] получает NodeReloaded → может показать уведомление
```

### 4.4. **Изменение статуса соединения**

```
[ConnectionService] проверяет сервер каждые 30 сек
    │
    ├─→ статус изменился: онлайн → офлайн
    │
    └─→ эмитит ConnectionChanged(is_online=False)
    │
    ▼
[ConnectionController] _on_connection_changed(event: Event[ConnectionChanged])
    │
    ├─→ проверяет, что статус действительно изменился
    │   (self._is_online != new_status) — debounce
    │
    └─→ эмитит NetworkActionsDisabled()
    │
    ▼
[UI] получает NetworkActionsDisabled → блокирует кнопки, показывает индикатор
```

---

## 5. **ВЗАИМОДЕЙСТВИЕ СО СЛОЯМИ**

### 5.1. **Связь с ядром (core)**

Controllers **используют** типы и события из core:
```python
from src.core import EventBus, NodeIdentifier, NodeType
from src.core.events import NodeSelected, DataLoaded, RefreshRequested
from src.core.types.exceptions import NotFoundError
```

Controllers **не изменяют** core.

### 5.2. **Связь с моделями (models)**

Controllers **используют** модели как типы данных:
```python
from src.models import Building, Counterparty, ResponsiblePerson
```

Controllers **не создают** модели напрямую — это делает DataLoader.

### 5.3. **Связь со слоем данных (data)**

Controllers **используют** репозитории через DataLoader:
```python
# В TreeController
details = self._loader.load_details(node_type, node_id)
children = self._loader.load_children(parent_type, parent_id, child_type)
```

Controllers **не обращаются** к EntityGraph напрямую — только через DataLoader.

### 5.4. **Связь со слоем сервисов (services)**

Controllers **вызывают** DataLoader и ContextService:
```python
self._loader.load_details(...)
self._loader.load_building_with_owner(...)  # возвращает BuildingWithOwnerResult
self._context_service.get_context(...)       # возвращает dict
```

Controllers **не вызывают** ApiClient напрямую — только через DataLoader.

### 5.5. **Связь с UI**

Controllers **общаются** с UI только через типизированные события:
```python
# Эмитим события для UI
self._bus.emit(NodeDetailsLoaded[Building](
    node=node, 
    payload=building, 
    context=context
))
self._bus.emit(BuildingDetailsLoaded(
    building=result.building,
    owner=result.owner,
    responsible_persons=result.responsible_persons
))
```

Controllers **не знают** о существовании UI-виджетов.

---

## 6. **КЛЮЧЕВЫЕ ПРИНЦИПЫ РАБОТЫ**

### 6.1. **Тонкие контроллеры (координация, а не логика)**
Контроллеры не содержат бизнес-логики — только координацию:
- Получают событие
- Вызывают сервисы
- Эмитят новые события

**Бизнес-правила остаются в DataLoader и ContextService.**

### 6.2. **Единый источник временного состояния**
Только `TreeController` хранит **временное состояние** приложения:
- `_current_selection`
- `_expanded_nodes`

Другие контроллеры получают состояние через события.

### 6.3. **Отсутствие состояния в RefreshController**
`RefreshController` не хранит состояние — получает его из событий:
```python
self._subscribe(CurrentSelectionChanged, self._on_selection_changed)
self._subscribe(ExpandedNodesChanged, self._on_expanded_changed)
```

Это делает слой реактивным — при изменении состояния в TreeController, RefreshController автоматически получает актуальные значения.

### 6.4. **Debounce в ConnectionController**
Эмитит события только при реальном изменении статуса:
```python
if self._is_online == new_status:
    return  # статус не изменился — не эмитим
```

### 6.5. **Единая обработка ошибок**
Все ошибки проходят через `BaseController._emit_error()`:
```python
try:
    result = self._loader.load_details(...)
except Exception as e:
    self._emit_error(node, e)
    return
```

### 6.6. **Правильная отписка (cleanup)**
Все подписки сохраняются и очищаются в `cleanup()`:
```python
def cleanup(self) -> None:
    for unsubscribe in self._subscriptions:
        unsubscribe()
    self._subscriptions.clear()
```

**Пример использования в MainWindow:**
```python
def closeEvent(self, event):
    # Очищаем все контроллеры
    self._tree_controller.cleanup()
    self._details_controller.cleanup()
    self._refresh_controller.cleanup()
    self._connection_controller.cleanup()
    event.accept()
```

---

## 7. **ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ**

### 7.1. **Инициализация в MainWindow**

```python
from src.core import EventBus
from src.data import EntityGraph, ComplexRepository, BuildingRepository, FloorRepository, CounterpartyRepository
from src.services import ApiClient, DataLoader, ContextService
from src.controllers import TreeController, DetailsController, RefreshController, ConnectionController

# Создаём зависимости
bus = EventBus()
graph = EntityGraph(bus)
api = ApiClient()
loader = DataLoader(bus, api, graph)

# Репозитории (через фасад graph)
complex_repo = ComplexRepository(graph)
building_repo = BuildingRepository(graph)
floor_repo = FloorRepository(graph)
counterparty_repo = CounterpartyRepository(graph)

# Сервисы
context_service = ContextService(
    complex_repo, building_repo, floor_repo, counterparty_repo, loader
)

# Создаём контроллеры
tree_controller = TreeController(bus, loader, context_service)
details_controller = DetailsController(bus, loader)
refresh_controller = RefreshController(bus, loader)
connection_controller = ConnectionController(bus)

# Запускаем
connection_controller.start()  # если есть метод start
```

### 7.2. **Реакция на выбор узла в UI**

```python
# UI испускает событие
bus.emit(NodeSelected(node=NodeIdentifier(NodeType.BUILDING, 101)))

# TreeController обрабатывает и эмитит NodeDetailsLoaded[Building]
# UI получает NodeDetailsLoaded[Building] и обновляет панель
```

### 7.3. **Реакция на F5**

```python
# UI испускает событие
bus.emit(RefreshRequested(mode="current"))

# RefreshController обрабатывает и вызывает loader.reload_node()
# После обновления эмитит NodeReloaded
# UI может показать уведомление
```

---

## 8. **ССЫЛКИ НА СОБЫТИЯ (core/events.py)**

| Событие | Файл | Строка |
|---------|------|--------|
| `NodeSelected` | core/events.py | UI события |
| `NodeExpanded` | core/events.py | UI события |
| `NodeCollapsed` | core/events.py | UI события |
| `TabChanged` | core/events.py | UI события |
| `RefreshRequested` | core/events.py | Команды |
| `CurrentSelectionChanged` | core/events.py | События состояния |
| `ExpandedNodesChanged` | core/events.py | События состояния |
| `NodeDetailsLoaded` | core/events.py | События деталей |
| `ChildrenLoaded` | core/events.py | События деталей |
| `BuildingDetailsLoaded` | core/events.py | События деталей |
| `NodeReloaded` | core/events.py | События обновления |
| `VisibleNodesReloaded` | core/events.py | События обновления |
| `FullReloadCompleted` | core/events.py | События обновления |
| `ConnectionChanged` | core/events.py | Системные события |
| `NetworkActionsEnabled` | core/events.py | События соединения |
| `NetworkActionsDisabled` | core/events.py | События соединения |
| `DataError` | core/events.py | Системные события |

---

## 9. **ИТОГ: ЧТО ДАЁТ СЛОЙ CONTROLLERS**

| Аспект | Результат |
|--------|-----------|
| **Координация потока данных** | Централизована в контроллерах, не размазана по UI |
| **Бизнес-логика** | Остаётся в DataLoader и ContextService |
| **Слабая связанность** | Контроллеры не знают о UI, только о событиях |
| **Тестируемость** | Контроллеры можно тестировать без Qt |
| **Переиспользование** | Один контроллер может использоваться разными UI |
| **Предсказуемость** | Чёткие входы (события) и выходы (события) |
| **Временное состояние** | Только в TreeController, синхронизация через события |
| **Реактивность** | RefreshController автоматически синхронизирован |
| **Обработка ошибок** | Единая, централизованная |
| **Отсутствие утечек** | cleanup() освобождает все подписки |

---

**Controllers — это слой координации потока данных, который получает сигналы от UI, вызывает сервисы с бизнес-логикой, управляет временным состоянием и отправляет результаты обратно через типизированные события.** 