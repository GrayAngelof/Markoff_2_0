## Анализ слоя «core» (ядро)

### Краткое описание слоя

Слой **core** — фундамент всего приложения. Он **не зависит** ни от каких других слоёв (models, data, services, projections, controllers, view models, ui). Его задачи:

- **Типы и структуры данных** — базовые перечисления (`NodeType`), value object (`NodeIdentifier`), протоколы (`HasNodeType`, `IDetailsViewModel`), исключения.
- **Шина событий** — `EventBus` (фасад) с внутренними механизмами слабых ссылок и автоматической очисткой мёртвых подписчиков.
- **События приложения** — конкретные классы-события (наследники `EventData`), сгруппированные по смыслу: UI-события, команды, события данных, события деталей, системные.
- **Правила иерархии** — чисто функции, определяющие связи между типами узлов (кто кому родитель/ребёнок, может ли иметь детей, навигация по иерархии).
- **Порты (интерфейсы)** — `Repository` (protocol) для единообразного доступа к данным (будет реализован в слое `data`).

**Что core НЕ должен делать:**
- Не содержит бизнес-логику управления данными (загрузка, кэширование, валидация DTO).
- Не имеет зависимостей от внешних API, баз данных, UI-фреймворков.
- Не управляет состоянием приложения (кроме подписок на события, которые хранятся в `EventBus`).

---

### Файловая структура слоя

```
src/core/
├── __init__.py                     # пустой (ничего не экспортирует)
├── event_bus.py                    # фасад EventBus (публичный)
├── bus/                            # ПРИВАТНО: внутренности EventBus
│   ├── __init__.py
│   ├── registry.py                 # _SubscriptionRegistry
│   └── weak_callback.py            # _WeakCallback
├── events/                         # определения всех событий
│   ├── __init__.py                 # экспорт событий
│   └── definitions.py              # классы событий (NodeSelected, DataLoaded и др.)
├── ports/                          # ПРИВАТНО: интерфейсы (ports)
│   ├── __init__.py
│   └── repository.py               # Repository (Protocol)
├── rules/                          # бизнес-правила иерархии
│   ├── __init__.py
│   └── hierarchy.py                # функции get_child_type, can_have_children и др.
└── types/                          # типы данных (публичные)
    ├── __init__.py                 # экспорт основных типов
    ├── event_structures.py         # базовый класс EventData
    ├── exceptions.py               # иерархия исключений CoreError, NotFoundError и др.
    ├── protocols.py                # HasNodeType, IDetailsViewModel
    ├── reference_data.py           # ReferenceDataType (enum)
    ├── reference_entity.py         # ReferenceEntityType (enum)
    └── structure.py                # NodeType, NodeIdentifier, ROOT_NODE и псевдонимы
```

---

### Описание внутренних классов и модулей

> **Публичные** элементы (используются вышестоящими слоями) перечислены в следующем разделе «Экспортируемые методы/классы». Здесь указаны только внутренние детали реализации, которые не должны импортироваться напрямую.

| Класс / Модуль | Назначение |
|----------------|-------------|
| `_SubscriptionRegistry` (в `bus/registry.py`) | Внутренний реестр подписок для `EventBus`. Хранит словарь `{тип_события: список _WeakCallback}`. Обеспечивает автоматическую очистку мёртвых подписок при уведомлениях и подсчётах. |
| `_WeakCallback` (в `bus/weak_callback.py`) | Слабая ссылка на callback (функцию или метод). Позволяет `EventBus` не удерживать объекты, на которые подписан обработчик, предотвращая утечки памяти. |
| Модуль `bus/__init__.py` | Запрещает прямой импорт из `bus` (внутренняя реализация). |
| Модуль `ports/__init__.py` | Запрещает прямой импорт из `ports`; публичный доступ только через `from src.core.ports.repository import Repository`. |

Все события (наследники `EventData`) и перечисление `DataLoadedKind` определены в `events/definitions.py`, но экспортируются через `events/__init__.py`.

---

### Список внутренних импортов (только между модулями core)

В `bus/registry.py`:
- `from .weak_callback import _WeakCallback`
- `from ..types.event_structures import EventData`

В `bus/weak_callback.py`:
- импортов из других модулей core нет (только внешний logger).

В `event_bus.py`:
- `from src.core.bus.registry import _SubscriptionRegistry`
- `from src.core.types.event_structures import EventData`

В `events/__init__.py` и `definitions.py`:
- `from src.core.types.event_structures import EventData`
- `from src.core.types.structure import NodeIdentifier, NodeType`
- `from src.core.types.protocols import IDetailsViewModel`

В `rules/hierarchy.py`:
- `from src.core.types.structure import NodeType`

В `types/__init__.py` (экспорт):
- `from .event_structures import EventData`
- `from .exceptions import ...`
- `from .structure import NodeIdentifier, NodeType, ROOT_NODE`
- `from .protocols import HasNodeType, IDetailsViewModel`
- `from .reference_data import ReferenceDataType`
- `from .reference_entity import ReferenceEntityType`

В `types/protocols.py`:
- `from .structure import NodeType`

В `types/structure.py`:
- импортов из других модулей core нет.

---

## Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящие слои (`models`, `data`, `services`, `projections`, `controllers`, `view models`, `ui`) **импортируют из `src.core` только следующие публичные элементы** (через конкретные подмодули, не через `src.core` напрямую):

### 1. Шина событий — `src.core.event_bus`

| Элемент | Назначение |
|---------|-------------|
| `class EventBus` | Центральный диспетчер событий (подписка/отписка/испускание). |
| `EventBus.__init__(debug: bool = False)` | Создать экземпляр. |
| `EventBus.subscribe(event_type, callback) -> Callable[[], None]` | Подписаться на событие; возвращает функцию отписки. |
| `EventBus.emit(event_data: EventData, source: str \| None = None)` | Опубликовать событие. |
| `EventBus.clear() -> None` | Удалить все подписки. |
| `EventBus.set_debug(enabled: bool) -> None` | Включить/выключить отладочный режим. |
| `EventBus.debug -> property` | Текущий режим отладки. |

### 2. Типы и структуры — `src.core.types`

| Элемент | Назначение |
|---------|-------------|
| `class NodeType(str, Enum)` | Тип узла: `ROOT`, `COMPLEX`, `BUILDING`, `FLOOR`, `ROOM`. |
| `class NodeIdentifier` | Value object: `(node_type: NodeType, node_id: int)`. |
| `ROOT_NODE` | Константа — виртуальный корневой узел `NodeIdentifier(NodeType.ROOT, 0)`. |
| `class EventData` | Базовый класс для всех событий (используется для типизации). |
| `class CoreError` (и наследники) | Базовое исключение; `NotFoundError`, `ValidationError`, `SerializationError` и др. |
| `class HasNodeType(Protocol)` | Объект, у которого есть атрибут класса `NODE_TYPE: NodeType`. |
| `class IDetailsViewModel(Protocol)` | Минимальный контракт для ViewModel деталей (атрибуты: `header_title`, `header_subtitle`, `header_status_name`, `grid_items`). |
| `class ReferenceDataType(str, Enum)` | Типы справочников (`BUILDING_STATUS`, `ROOM_STATUS` и т.д.). |
| `class ReferenceEntityType(str, Enum)` | Типы сущностей (`COUNTERPARTY`, `RESPONSIBLE_PERSON`). |

### 3. События — `src.core.events`

Все классы-события (наследники `EventData`) экспортируются **поимённо** через `src.core.events`. Основные:

| Категория | События (классы) |
|-----------|------------------|
| UI действия | `NodeSelected[T]`, `NodeExpanded`, `NodeCollapsed`, `CollapseAllRequested`, `CurrentSelectionChanged`, `ExpandedNodesChanged`, `TabChanged` |
| Команды | `RefreshRequested` (mode: 'current'/'visible'/'full'), `ShowDetailsPanel` |
| Результаты загрузки | `DataLoaded[T]`, `DataError`, `DataInvalidated` |
| Детали для UI | `ChildrenLoaded[T]`, `NodeDetailsLoaded` |
| Системные | `ConnectionChanged` |

Также экспортируется тип `DataLoadedKind` (enum: `CHILDREN`, `DETAILS`).

### 4. Правила иерархии — `src.core.rules.hierarchy`

| Функция | Назначение |
|---------|-------------|
| `get_child_type(parent_type: NodeType) -> Optional[NodeType]` | Тип ребёнка для родителя (или None, если лист). |
| `get_parent_type(child_type: NodeType) -> Optional[NodeType]` | Тип родителя (или None для корня). |
| `can_have_children(node_type: NodeType) -> bool` | Может ли узел иметь детей. |
| `is_leaf(node_type: NodeType) -> bool` | Является ли узел листом (не может иметь детей). |
| `get_all_ancestors(start_type: NodeType) -> List[NodeType]` | Список всех предков (от ближайшего к дальнему). |
| `get_all_descendants(start_type: NodeType) -> List[NodeType]` | Список всех потомков. |
| `validate_hierarchy(parent_type: NodeType, child_type: NodeType) -> bool` | Проверяет допустимость связи родитель-потомок. |

### 5. Порт репозитория — `src.core.ports.repository`

| Элемент | Назначение |
|---------|-------------|
| `class Repository(Protocol[T, ID])` | Интерфейс для реализации репозиториев в слое `data`. Методы: `get(id)`, `get_all()`, `add(entity)`, `remove(id)`. |

---

## Итоговое заключение

**Принципы работы со слоем core:**

1. **Никаких сквозных импортов из `bus`, `ports` или внутренних модулей** — используйте только публичные точки входа:  
   - `from src.core.event_bus import EventBus`  
   - `from src.core.types import NodeType, NodeIdentifier, ...`  
   - `from src.core.events import NodeSelected, DataLoaded, ...`  
   - `from src.core.rules.hierarchy import get_child_type, ...`  
   - `from src.core.ports.repository import Repository`

2. **События передаются по классу (типобезопасно)** — не используйте строковые идентификаторы.

3. **Подписка на события должна быть симметричной** — возвращаемую функцию отписки желательно сохранять и вызывать при уничтожении подписчика.

4. **Исключения ядра (`CoreError` и наследники)** — перехватывайте их для обработки специфических ошибок нижнего уровня.

5. **Никакой бизнес-логики загрузки данных в core** — слой остаётся абстрактным фундаментом, не зависящим от реализации хранения, сети или UI.

6. **При тестировании** `EventBus` можно использовать как мок или реальный экземпляр (он не создаёт побочных эффектов вне вызовов обработчиков).

Слой core стабилен и меняется редко; изменения в нём требуют осторожности из-за большого количества зависимых вышележащих слоёв.