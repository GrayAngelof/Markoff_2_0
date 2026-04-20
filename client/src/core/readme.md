## Анализ слоя: **core** (фундаментальный слой)

### Краткое описание слоя

**Назначение** – обеспечить базовую инфраструктуру и типовую безопасность для всего приложения. Слой `core` не содержит бизнес-логики, работы с данными или UI. Его компоненты используются всеми вышестоящими слоями (`models`, `data`, `services`, `projections`, `controllers`, `ui`).

**Что делает:**
- Определяет базовые типы (`NodeType`, `NodeIdentifier`, `EventData`, иерархию исключений)
- Реализует шину событий (`EventBus`) со слабыми ссылками для слабой связанности
- Задаёт контракты доступа к данным (интерфейс `Repository` в виде `Protocol`)
- Содержит чистые функции для правил иерархии (кто кому родитель, может ли иметь детей, предки/потомки)

**Что не должен делать:**
- Импортировать что-либо из `models`, `data`, `services`, `projections`, `controllers`, `ui`
- Содержать логику работы с API, БД, файловой системой
- Включать UI-специфичный код (виджеты, рендеринг)
- Содержать бизнес-правила, зависящие от конкретных сущностей (кроме иерархии типов узлов)

---

### Файловая структура слоя

```
client/src/core/
├── __init__.py                    # Публичное API ядра (фасады, типы, события)
├── event_bus.py                   # Фасад EventBus (основной класс для работы с событиями)
├── bus/                           # Внутренняя реализация шины (приватный пакет)
│   ├── __init__.py                # Маркер приватности
│   ├── registry.py                # _SubscriptionRegistry (реестр подписок)
│   └── weak_callback.py           # _WeakCallback (слабая ссылка на callback)
├── events/                        # Определения всех событий приложения
│   ├── __init__.py                # Экспорт событий
│   └── definitions.py             # Классы событий (NodeSelected, DataLoaded и др.)
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
| `_WeakCallback` | `bus/weak_callback.py` | Оборачивает callback (функцию или метод) в слабую ссылку, позволяя сборщику мусора удалять объекты, на которые ссылается обработчик. |
| `EventBus` | `event_bus.py` | **Фасад** – единственный публичный класс слоя для работы с событиями. Предоставляет `subscribe()`, `emit()`, `clear()`, `set_debug()`. |
| `EventData` | `types/event_structures.py` | Абстрактный базовый класс для всех событий (frozen dataclass). Обеспечивает типовую безопасность. |
| `NodeIdentifier` | `types/nodes.py` | Value object для типобезопасной идентификации узла (тип + числовой ID). |
| `Repository` (Protocol) | `ports/repository.py` | Контракт для репозиториев: `get()`, `get_all()`, `add()`, `remove()`. |
| `CoreError` и наследники | `types/exceptions.py` | Иерархия исключений ядра: `ConfigurationError`, `NotFoundError`, `ValidationError`, `ApiError`, `ConnectionError`, `DuplicateError`, `SerializationError`, `HierarchyError`. |

---

### Внутренние импорты (только между модулями core)

Игнорируем `utils.logger` (внешний утилитарный модуль, не входит в иерархию слоёв, логирование допустимо на любом слое).

**Из `core/bus/registry.py`**:
- `from .weak_callback import _WeakCallback`
- `from ..types.event_structures import EventData`

**Из `core/event_bus.py`**:
- `from .bus.registry import _SubscriptionRegistry`
- `from .types.event_structures import EventData`

**Из `core/events/definitions.py`**:
- `from src.core.types.event_structures import EventData`
- `from src.core.types.nodes import NodeIdentifier, NodeType`

**Из `core/rules/hierarchy.py`**:
- `from ..types.nodes import NodeType`

**Из `core/__init__.py` (публичный фасад)**:
- `from .types import NodeType, NodeIdentifier`
- `from .event_bus import EventBus`
- `from .types.exceptions import CoreError, NotFoundError, ValidationError`
- `from .ports.repository import Repository`
- `from .events import (NodeSelected, NodeExpanded, NodeCollapsed, TabChanged, RefreshRequested, ShowDetailsPanel, DataLoaded, DataError, DataInvalidated, ChildrenLoaded, NodeDetailsLoaded, ConnectionChanged)`

**Из `core/types/__init__.py`**:
- `from .nodes import NodeType, NodeIdentifier, ROOT_NODE`
- `from .event_structures import EventData`
- `from .exceptions import CoreError, NotFoundError, ValidationError`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вся публичная поверхность слоя `core` доступна через импорт из `src.core` (согласно `core/__init__.py`), а также через прямые импорты из подмодулей (например, `src.core.rules.hierarchy`).

**Классы и фасады:**
- `EventBus` – шина событий (основной механизм коммуникации)

**Базовые типы:**
- `NodeType` (enum)
- `NodeIdentifier` (dataclass)
- `ROOT_NODE` – виртуальный корневой узел

**Исключения:**
- `CoreError`
- `NotFoundError`
- `ValidationError`

**Интерфейсы (ports):**
- `Repository` (Protocol) – для реализации репозиториев в слое `data`

**События (все – dataclasses, наследники `EventData`):**
- UI: `NodeSelected`, `NodeExpanded`, `NodeCollapsed`, `CollapseAllRequested`, `CurrentSelectionChanged`, `ExpandedNodesChanged`, `TabChanged`
- Команды: `RefreshRequested`, `ShowDetailsPanel`
- Данные: `DataLoaded`, `DataError`, `DataInvalidated`
- Детали: `ChildrenLoaded`, `NodeDetailsLoaded`
- Системные: `ConnectionChanged`

**Функции правил иерархии (доступны через `from src.core.rules.hierarchy import ...`):**
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
2. **Запрещены импорты из `core` в обратную сторону** – код внутри `core` не должен импортировать ничего из `models`, `data` и т.д.
3. **Используйте публичное API через `src.core`** – все необходимые типы, исключения, события и `EventBus` доступны оттуда.
4. **Не импортируйте внутренние пакеты `core.bus`, `core.ports` напрямую** – они помечены как приватные. Исключение: функции правил иерархии (`rules.hierarchy`) и `types.protocols` при необходимости можно импортировать явно.
5. **Работа с событиями**:
   - Создавайте экземпляры событий (например, `NodeSelected(node=...)`) и вызывайте `event_bus.emit()`.
   - Подписывайтесь через `event_bus.subscribe(ТипСобытия, callback)`.
6. **Интерфейс `Repository`** – используйте для типизации репозиториев в слое `data`.
7. **Исключения** – наследуйте свои ошибки от `CoreError` или его подклассов для единообразной обработки.
8. **Иерархия** – для навигации по типам узлов используйте чистые функции из `rules.hierarchy`, они не имеют побочных эффектов.

Слой `core` является **единственным общим фундаментом** – всё приложение строится на нём, но он не знает ничего о вышележащих слоях.