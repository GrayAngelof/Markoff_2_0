## Анализ слоя: **core** (фундаментальный слой)

### Краткое описание слоя

**Назначение** – обеспечить базовую инфраструктуру и типовую безопасность для всего приложения. Слой `core` не содержит бизнес-логики, работы с данными или UI. Его компоненты используются всеми вышестоящими слоями (`models`, `data`, `services`, `projections`, `controllers`, `ui`).

**Что делает:**
- Определяет базовые типы (`NodeType`, `NodeIdentifier`, `EventData`, исключения)
- Реализует шину событий (`EventBus`) со слабыми ссылками для слабой связанности
- Задаёт контракты доступа к данным (интерфейс `Repository`)
- Содержит чистые функции для правил иерархии (кто кому родитель, может ли иметь детей)

**Что не должен делать:**
- Импортировать что-либо из `models`, `data`, `services`, `projections`, `controllers`, `ui`
- Содержать логику работы с API, БД, файловой системой
- Включать UI-специфичный код (виджеты, рендеринг)
- Содержать бизнес-правила, зависящие от конкретных сущностей (кроме иерархии типов)

---

### Файловая структура слоя

```
client/src/core/
├── __init__.py                    # Публичное API ядра (фасады и типы)
├── event_bus.py                   # Фасад EventBus (основной класс для работы с событиями)
├── bus/                           # Внутренняя реализация шины (приватный пакет)
│   ├── __init__.py                # Маркер приватности
│   ├── registry.py                # _SubscriptionRegistry (реестр подписок)
│   └── weak_callback.py           # _WeakCallback (слабая ссылка на callback)
├── events/                        # Определения всех событий приложения
│   ├── __init__.py                # Экспорт событий
│   └── definitions.py             # Классы событий (NodeSelected, DataLoaded и т.д.)
├── ports/                         # Интерфейсы (абстракции) для доступа к данным
│   ├── __init__.py                # Маркер приватности
│   └── repository.py              # Repository (Protocol)
├── rules/                         # Бизнес-правила иерархии (чистые функции)
│   ├── __init__.py                # Маркер приватности
│   └── hierarchy.py               # get_child_type, can_have_children, validate_hierarchy и др.
└── types/                         # Базовые типы данных и исключения
    ├── __init__.py                # Публичный экспорт базовых типов
    ├── event_structures.py        # EventData (базовый класс событий)
    ├── exceptions.py              # Иерархия исключений (CoreError, NotFoundError...)
    ├── nodes.py                   # NodeType, NodeIdentifier, псевдонимы
    └── protocols.py               # Протоколы для структурной типизации (HasNodeType)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `_SubscriptionRegistry` | `bus/registry.py` | Хранит подписки на события в виде слабых ссылок, уведомляет подписчиков, автоматически очищает мёртвые обработчики. |
| `_WeakCallback` | `bus/weak_callback.py` | Оборачивает callback (функцию или метод) в слабую ссылку, позволяя сборщику мусора удалять объекты, на которые ссылается обработчик. Различает методы и функции. |
| `EventBus` | `event_bus.py` | **Фасад** – единственный публичный класс слоя для работы с событиями. Предоставляет `subscribe()`, `emit()`, `clear()`, `set_debug()`. |
| `EventData` | `types/event_structures.py` | Базовый класс для всех событий (frozen dataclass с slots). Обеспечивает типовую безопасность и компактное представление. |
| `NodeIdentifier` | `types/nodes.py` | Value object для типобезопасной идентификации узла (тип + числовой ID). Immutable, использует slots. |
| `NodeType` | `types/nodes.py` | Enum типов узлов: `ROOT`, `COMPLEX`, `BUILDING`, `FLOOR`, `ROOM`. |
| `Repository` (Protocol) | `ports/repository.py` | Контракт для репозиториев: `get()`, `get_all()`, `add()`, `remove()`. |
| `CoreError` и наследники | `types/exceptions.py` | Иерархия исключений ядра: `ConfigurationError`, `NotFoundError`, `ValidationError`, `ApiError`, `ConnectionError`, `DuplicateError`, `SerializationError`, `HierarchyError`. |
| `DataLoadedKind` | `events/definitions.py` | Enum типов загруженных данных: `CHILDREN` или `DETAILS`. |

---

### Внутренние импорты (только между модулями core)

Ниже перечислены импорты, игнорируя `utils.logger` (внешний утилитарный модуль, не входит в иерархию слоёв, но логирование допустимо на любом слое).

**Из `core/bus/registry.py`:**
- `from .weak_callback import _WeakCallback`
- `from ..types.event_structures import EventData`

**Из `core/bus/weak_callback.py`:**
- (нет внутренних импортов core)

**Из `core/event_bus.py`:**
- `from .bus.registry import _SubscriptionRegistry`
- `from .types.event_structures import EventData`

**Из `core/events/__init__.py`:**
- `from .definitions import (все события)`

**Из `core/events/definitions.py`:**
- `from src.core.types.event_structures import EventData`
- `from src.core.types.nodes import NodeIdentifier, NodeType`

**Из `core/ports/repository.py`:**
- (нет внутренних импортов core)

**Из `core/rules/hierarchy.py`:**
- `from ..types.nodes import NodeType`

**Из `core/types/__init__.py`:**
- `from .event_structures import EventData`
- `from .exceptions import CoreError, NotFoundError, ValidationError`
- `from .nodes import NodeIdentifier, NodeType, ROOT_NODE`

**Из `core/types/protocols.py`:**
- `from .nodes import NodeType`

**Из `core/__init__.py` (публичный фасад):**
- `from .types import NodeType, NodeIdentifier`
- `from .event_bus import EventBus`
- `from .types.exceptions import CoreError, NotFoundError, ValidationError`
- `from .ports.repository import Repository`
- `from .events import (все события)`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вся публичная поверхность слоя `core` доступна через импорт из `src.core` (согласно `core/__init__.py`):

**Классы:**
- `EventBus` – шина событий (основной механизм коммуникации)
  - `__init__(debug: bool = False)`
  - `subscribe(event_type, callback) -> Callable[[], None]`
  - `emit(event_data, source: Optional[str] = None) -> None`
  - `clear() -> None`
  - `set_debug(enabled: bool) -> None`
  - `debug -> bool` (property)

**Базовые типы:**
- `NodeType` (enum: `ROOT`, `COMPLEX`, `BUILDING`, `FLOOR`, `ROOM`)
- `NodeIdentifier` (dataclass: `node_type`, `node_id`)
- `ROOT_NODE` (константа – виртуальный корневой узел)

**Исключения:**
- `CoreError` – базовое для всех ошибок ядра
- `NotFoundError` – объект не найден
- `ValidationError` – ошибка валидации
- (остальные исключения доступны через полный путь, но редко нужны выше)

**Интерфейсы (ports):**
- `Repository` (Protocol) – для реализации репозиториев в слое `data`

**События (все – dataclasses, наследники `EventData`, с `slots=True`):**

| Категория | События |
|-----------|---------|
| UI события | `NodeSelected[T]`, `NodeExpanded`, `NodeCollapsed`, `CollapseAllRequested`, `CurrentSelectionChanged`, `ExpandedNodesChanged`, `TabChanged` |
| Команды | `RefreshRequested` (mode: 'current'/'visible'/'full'), `ShowDetailsPanel` |
| События данных | `DataLoaded[T]`, `DataError`, `DataInvalidated` |
| События деталей | `ChildrenLoaded[T]`, `NodeDetailsLoaded[T]` |
| Системные | `ConnectionChanged` |

**Функции (из `core.rules.hierarchy` – не экспортируются через `__init__.py`, но доступны через полный путь `from src.core.rules.hierarchy import ...`):**
- `get_child_type(parent_type: NodeType) -> Optional[NodeType]`
- `get_parent_type(child_type: NodeType) -> Optional[NodeType]`
- `can_have_children(node_type: NodeType) -> bool`
- `is_leaf(node_type: NodeType) -> bool`
- `get_all_ancestors(start_type: NodeType) -> List[NodeType]`
- `get_all_descendants(start_type: NodeType) -> List[NodeType]`
- `validate_hierarchy(parent_type: NodeType, child_type: NodeType) -> bool`

---

### Итоговое заключение: принципы работы со слоем `core`

1. **Импорт только сверху вниз** – вышестоящие слои (`models`, `data`, `services`, `projections`, `controllers`, `ui`) могут импортировать из `core` свободно.
2. **Запрещены импорты из `core` в обратную сторону** – код внутри `core` не должен импортировать ничего из `models`, `data` и т.д. Внутренние модули `core` могут импортировать друг друга только по правилам приватности.
3. **Используйте публичное API через `src.core`** – все необходимые типы, исключения, события и `EventBus` доступны оттуда.
4. **Не импортируйте внутренние пакеты `core.bus`, `core.ports`, `core.rules` напрямую** – они помечены как приватные. Исключение: функции правил иерархии (`hierarchy.py`) можно импортировать явно, так как они не скрыты за фасадом (но это допустимо только из слоёв, которым нужна навигация по типам).
5. **Работа с событиями**:
   - Создавайте экземпляры событий (например, `NodeSelected(node=..., payload=...)`) и вызывайте `event_bus.emit()`.
   - Подписывайтесь через `event_bus.subscribe(ТипСобытия, callback)`.
   - Полученная функция отписки позволяет удалить подписку при необходимости.
   - События иммутабельны (`frozen=True`) и используют `slots` для экономии памяти.
6. **Generic-события** – `NodeSelected[T]`, `DataLoaded[T]`, `ChildrenLoaded[T]`, `NodeDetailsLoaded[T]` поддерживают типизированные `payload`. Используйте конкретный тип при подписке: `event_bus.subscribe(DataLoaded[MyDTO], handler)`.
7. **Интерфейс `Repository`** – используйте для типизации репозиториев в слое `data`. Все репозитории должны реализовывать методы `get`, `get_all`, `add`, `remove`.
8. **Исключения** – наследуйте свои ошибки от `CoreError` или его подклассов для единообразной обработки. Никогда не выбрасывайте `Exception` без обёртки.
9. **Иерархия** – для навигации по типам узлов используйте чистые функции из `rules.hierarchy`, они не имеют побочных эффектов и не обращаются к данным. Валидация связей (`validate_hierarchy`) – только по типам, не по ID.
10. **Логирование** – допустимо использовать `utils.logger` на любом слое, включая `core`, но это единственное исключение из правила «только сверху вниз».

Слой `core` является **единственным общим фундаментом** – всё приложение строится на нём, но он не знает ничего о вышележащих слоях. Это обеспечивает тестируемость, переиспользование и чёткое разделение ответственности.