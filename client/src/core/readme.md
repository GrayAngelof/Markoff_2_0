# ============================================
# СПЕЦИФИКАЦИЯ: CORE (ЯДРО ПРИЛОЖЕНИЯ)
# ============================================

## 1. НАЗНАЧЕНИЕ
Core — это фундамент приложения, задающий единые правила игры для всех остальных слоёв. Он обеспечивает слабую связанность, типобезопасность и предсказуемость системы, предоставляя базовые типы, контракты, механизм событий и правила предметной области. Core не решает бизнес-задачи, но создаёт каркас, в котором они могут безопасно и масштабируемо развиваться.

## 2. ГДЕ ЛЕЖИТ
`client/src/core/`

## 3. ЗА ЧТО ОТВЕЧАЕТ
✅ **Отвечает за:**
- **Типовую систему:** `NodeType` (enum), `NodeIdentifier` (value object), `NodeID`, `NodeKey`, `ParentInfo`.
- **Механизм событий:** Базовые классы (`EventData`, `Event`), константы (`UIEvents`, `SystemEvents` и др.) и шину (`EventBus`) с доставкой событий-фактов через weak-ссылки.
- **Иерархию узлов:** Функции для определения родительских/дочерних типов (`get_child_type`), проверки (`can_have_children`, `is_leaf`) и валидации строгой древовидной структуры (`validate_hierarchy`).
- **Сериализацию идентификаторов:** Преобразование между `NodeIdentifier` и внутренними строковыми ключами (`make_node_key`, `parse_node_key`), а также форматирование для отображения.
- **Базовые контракты:** Интерфейс `Repository[T, ID]`, определяющий минимальный CRUD.
- **Исключения:** Иерархия исключений ядра (`CoreError`, `ValidationError`, `NotFoundError` и др.).

❌ **НЕ отвечает за:**
- Бизнес-логику и оркестрацию процессов.
- Хранение, загрузку или кэширование данных.
- UI, форматирование для пользователя и внешние API.
- Любые утилиты общего назначения, не связанные с типами и контрактами ядра.

## 4. КТО ИСПОЛЬЗУЕТ
- **Потребители:** Все слои приложения (`data`, `services`, `controllers`, `ui`), плагины и AI-агенты.
- **Зависимости:** Только стандартная библиотека Python. Core ничего не импортирует из других слоёв проекта.

## 5. КЛЮЧЕВЫЕ ПОНЯТИЯ
- **Событие (Event) = факт:** Отражает то, что уже произошло в системе, а не команду на выполнение действия.
- **EventBus = транспорт:** Только доставляет события от источника к подписчикам, не управляя бизнес-процессами.
- **NodeType = структура дерева:** Описывает исключительно иерархию недвижимости (комплекс → здание → этаж → помещение), а не бизнес-домен.
- **NodeIdentifier = единая точка идентичности:** Гарантирует уникальность объекта, объединяя его тип и ID, что исключает путаницу между сущностями разных типов с одинаковым числовым ID.
- **Иерархия (Hierarchy) = строгое дерево:** Каждый узел имеет ровно одного родителя, исключая графовые связи.

## 6. ОГРАНИЧЕНИЯ
⛔ **НЕЛЬЗЯ:**
- Использовать `EventBus` для оркестрации или создавать события-команды.
- Передавать данные событий в виде простых `dict`, вместо типизированных наследников `EventData`.
- Расширять `NodeType` сущностями, не входящими в иерархическое дерево.
- Использовать иерархию как граф (один родитель — строгое правило).
- Усложнять интерфейс `Repository` под конкретные сценарии или добавлять в него логику.
- Добавлять в Core утилиты общего назначения или зависимости от других слоёв.
- Использовать `NodeKey` (внутренний формат) как часть публичного API.

✅ **МОЖНО:**
- Добавлять новые константы событий (фактов) и новые типы узлов в рамках существующей иерархии.
- Реализовывать интерфейс `Repository` в других слоях, не изменяя сам контракт.
- Расширять правила иерархии новыми функциями-проверками.

## 7. ПРИМЕРЫ
```python
# Импорт публичного API
from src.core import (
    NodeType, NodeIdentifier, EventBus, UIEvents,
    make_node_key, can_have_children, Repository
)

# Создание типизированного идентификатора
node_id = NodeIdentifier(NodeType.BUILDING, 101)

# Работа с шиной событий (событие = факт)
class NodeSelected(EventData):
    node_id: int

bus = EventBus()
bus.subscribe(UIEvents.NODE_SELECTED, lambda e: print(f"Выбран узел {e.data.node_id}"))
bus.emit(UIEvents.NODE_SELECTED, NodeSelected(node_id=42))

# Сериализация
key = make_node_key(NodeType.COMPLEX, 7)  # "complex:7"

# Проверка иерархии
if can_have_children(NodeType.FLOOR):
    print("У этажа могут быть помещения")
```

## 8. РИСКИ
🔴 **Критические:**
- Превращение `EventBus` в оркестратор и шину команд, что приведёт к неявным связям.
- Потеря типизации при использовании словарей вместо `EventData`.
- Разрастание `NodeType` до размеров бизнес-домена, что нарушит изоляцию Core.
- Нарушение принципа "событие = факт", ведущее к недетерминированному поведению.

🟡 **Средние:**
- Случайная утечка `NodeKey` во внешний API, что создаст нежелательную зависимость от внутреннего формата.
- Попытка наделить `Repository` дополнительными методами, нарушая его контракт.

🟢 **Контролируемые:**
- Рост числа событий при соблюдении правил безопасности не влияет на стабильность ядра.

# ============================================
# КОНЕЦ СПЕЦИФИКАЦИИ
# ============================================

## 📚 ОПИСАНИЕ ЯДРА
В соответствии с архитектурой, ядро реализовано как минимальный, но самодостаточный слой, обеспечивающий типобезопасность и слабую связанность через **type-based события**. Код организован в следующую структуру каталогов:

```
core/
├── __init__.py                    # Публичное API (минималистичный, 8 элементов)
├── event_bus.py                   # Фасад шины событий (type-based)
├── events.py                      # Классы всех событий (типизированные факты)
├── hierarchy.py                   # Правила иерархии узлов
├── serializers.py                 # Преобразования идентификаторов (public/private)
│
├── types/                         # Базовые типы и исключения
│   ├── __init__.py
│   ├── nodes.py                   # NodeType (str, Enum), NodeIdentifier (+slots)
│   ├── event_structures.py        # EventData, Event (конверт с метаданными)
│   └── exceptions.py              # Иерархия исключений (9 классов)
│
└── interfaces/                    # Базовые контракты
    ├── __init__.py
    └── repository.py              # Repository[T, ID] с явными исключениями
```

---

## 📦 Публичное API (минималистичный подход)

Core экспортирует **только самое необходимое**. Всё остальное импортируется из подмодулей:

```python
# Базовые типы и шина (экспортируются из core)
from src.core import NodeType, NodeIdentifier, EventBus, CoreError, NotFoundError, ValidationError

# События — из core.events
from src.core.events import (
    # UI события (факты)
    NodeSelected, NodeExpanded, NodeCollapsed, TabChanged,
    # Системные события (факты)
    DataLoading, DataLoaded, DataError, ConnectionChanged,
    # Команды
    RefreshRequested,
    # События состояния (для контроллеров)
    CurrentSelectionChanged, ExpandedNodesChanged,
    # События деталей
    NodeDetailsLoaded, ChildrenLoaded, BuildingDetailsLoaded,
    # События обновления
    NodeReloaded, VisibleNodesReloaded, FullReloadCompleted,
    # События соединения
    NetworkActionsEnabled, NetworkActionsDisabled
)

# Правила иерархии — из core.hierarchy
from src.core.hierarchy import get_child_type, can_have_children, validate_hierarchy

# Сериализация — из core.serializers
from src.core.serializers import identifier_to_key, key_to_identifier, try_parse_identifier, format_display

# Дополнительные исключения — из core.types.exceptions
from src.core.types.exceptions import SerializationError, ConnectionError, ApiError
```

---

## 🔹 Базовые типы (из `core.types`)

```python
from src.core import NodeType, NodeIdentifier, NodeID, NodeKey, ParentInfo
```

| Тип | Описание | Пример |
|-----|----------|--------|
| `NodeType` | Enum типов узлов (str, Enum) | `NodeType.COMPLEX`, `NodeType.BUILDING` |
| `NodeID` | Алиас для int | `complex_id: NodeID = 42` |
| `NodeKey` | Строковый ключ "тип:id" | `"complex:42"` |
| `ParentInfo` | Кортеж (тип, id) родителя | `(NodeType.BUILDING, 101)` |
| `NodeIdentifier` | Value Object (+slots, frozen) | `NodeIdentifier(NodeType.COMPLEX, 42)` |

**Пример использования:**
```python
# Создание идентификатора
node_id = NodeIdentifier(NodeType.COMPLEX, 42)

# Доступ к атрибутам
print(node_id.node_type)  # NodeType.COMPLEX
print(node_id.node_id)    # 42

# Форматирование для логов и UI (нет атрибута .display!)
display = f"{node_id.node_type.value}#{node_id.node_id}"  # "complex#42"

# Сравнение (работает благодаря frozen dataclass)
another = NodeIdentifier(NodeType.COMPLEX, 42)
assert node_id == another  # True
```

---

## 🔹 Структуры событий (из `core.types`)

```python
from src.core.types import EventData, Event
```

| Класс | Назначение |
|-------|------------|
| `EventData` | Базовый класс для всех фактов (событий) |
| `Event[T]` | Generic конверт события с метаданными (source, timestamp) |

**Пример использования:**
```python
from dataclasses import dataclass
from typing import Optional, List, Set, TypeVar, Generic
from src.core import NodeIdentifier, NodeType
from src.core.types import EventData

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class NodeSelected(EventData):
    """Пользователь выбрал узел (ФАКТ, а не команда)."""
    node: NodeIdentifier
    payload: Optional[Any] = None

@dataclass(frozen=True, slots=True)
class NodeDetailsLoaded(EventData, Generic[T]):
    """Детальная информация о узле загружена."""
    node: NodeIdentifier
    payload: T
    context: dict

@dataclass(frozen=True, slots=True)
class CurrentSelectionChanged(EventData):
    """Изменился текущий выбранный узел."""
    selection: Optional[NodeIdentifier]

@dataclass(frozen=True, slots=True)
class ExpandedNodesChanged(EventData):
    """Изменился список раскрытых узлов."""
    expanded_nodes: Set[NodeIdentifier]

# Конверт создаётся EventBus автоматически
# event = Event(data=NodeSelected(node=...), source="tree_view", timestamp=...)
```

---

## 🔹 События (из `core.events`)

```python
from src.core.events import (
    # === UI события (факты) ===
    NodeSelected, NodeExpanded, NodeCollapsed, TabChanged,
    
    # === Системные события (факты) ===
    DataLoading, DataLoaded, DataError, ConnectionChanged,
    
    # === Команды ===
    RefreshRequested,
    
    # === События состояния (для контроллеров) ===
    CurrentSelectionChanged, ExpandedNodesChanged,
    
    # === События деталей ===
    NodeDetailsLoaded, ChildrenLoaded, BuildingDetailsLoaded,
    
    # === События обновления ===
    NodeReloaded, VisibleNodesReloaded, FullReloadCompleted,
    
    # === События соединения ===
    NetworkActionsEnabled, NetworkActionsDisabled
)
```

### **Полная таблица событий**

| Событие | Тип | Generic | Назначение |
|---------|-----|---------|------------|
| **UI события (факты)** |
| `NodeSelected` | Факт | `T` | Пользователь выбрал узел |
| `NodeExpanded` | Факт | — | Узел раскрыт |
| `NodeCollapsed` | Факт | — | Узел свёрнут |
| `TabChanged` | Факт | — | Переключена вкладка |
| **Системные события (факты)** |
| `DataLoading` | Факт | — | Началась загрузка данных |
| `DataLoaded` | Факт | `T` | Данные загружены |
| `DataError` | Факт | — | Ошибка загрузки |
| `ConnectionChanged` | Факт | — | Статус соединения изменился |
| **Команды** |
| `RefreshRequested` | Команда | — | Запрос на обновление |
| **События состояния (для контроллеров)** |
| `CurrentSelectionChanged` | Факт | — | Изменился текущий выбранный узел |
| `ExpandedNodesChanged` | Факт | — | Изменился список раскрытых узлов |
| **События деталей** |
| `NodeDetailsLoaded` | Факт | `T` | Детальная информация о узле загружена |
| `ChildrenLoaded` | Факт | `T` | Дети узла загружены |
| `BuildingDetailsLoaded` | Факт | — | Загружены детали корпуса с владельцем |
| **События обновления** |
| `NodeReloaded` | Факт | — | Узел перезагружен |
| `VisibleNodesReloaded` | Факт | — | Все раскрытые узлы перезагружены |
| `FullReloadCompleted` | Факт | — | Полная перезагрузка завершена |
| **События соединения** |
| `NetworkActionsEnabled` | Факт | — | Сетевые действия разрешены (онлайн) |
| `NetworkActionsDisabled` | Факт | — | Сетевые действия запрещены (офлайн) |

**Пример использования с Generic:**
```python
from src.core import EventBus, NodeIdentifier, NodeType
from src.core.events import NodeSelected, NodeDetailsLoaded, ChildrenLoaded, BuildingDetailsLoaded

bus = EventBus()

# Подписка на типизированные события
def on_details_loaded(event: Event[NodeDetailsLoaded[Building]]) -> None:
    building = event.data.payload  # тип Building!
    print(f"Загружено здание: {building.name}")

def on_children_loaded(event: Event[ChildrenLoaded[Building]]) -> None:
    buildings = event.data.children  # тип List[Building]!
    print(f"Загружено {len(buildings)} зданий")

def on_building_details(event: Event[BuildingDetailsLoaded]) -> None:
    building = event.data.building
    owner = event.data.owner
    print(f"Здание {building.name}, владелец: {owner.short_name if owner else 'не указан'}")

# Подписка
bus.subscribe(NodeDetailsLoaded[Building], on_details_loaded)
bus.subscribe(ChildrenLoaded[Building], on_children_loaded)
bus.subscribe(BuildingDetailsLoaded, on_building_details)

# Испускание
bus.emit(NodeDetailsLoaded[Building](
    node=NodeIdentifier(NodeType.BUILDING, 101),
    payload=building,
    context={'complex_name': 'Северный'}
))
bus.emit(BuildingDetailsLoaded(
    building=building,
    owner=owner,
    responsible_persons=persons
))
```

---

## 🔹 Исключения (из `core.types.exceptions`)

```python
from src.core import CoreError, NotFoundError, ValidationError
from src.core.types.exceptions import SerializationError, ConnectionError, ApiError
```

| Исключение | Назначение |
|------------|------------|
| `CoreError` | Базовое для всех ошибок ядра |
| `NotFoundError` | Объект не найден (repository.get) |
| `ValidationError` | Ошибка валидации данных |
| `SerializationError` | Ошибка парсинга ключей |
| `ConnectionError` | Ошибка соединения с сервером |
| `ApiError` | Ошибка при обращении к API |
| `ConfigurationError` | Ошибка конфигурации |
| `HierarchyError` | Ошибка в иерархии |
| `DuplicateError` | Дубликат объекта |

**Пример использования:**
```python
from src.core import NotFoundError
from src.core.serializers import key_to_identifier, SerializationError

try:
    identifier = key_to_identifier("invalid:key")
except SerializationError as e:
    print(f"Ошибка парсинга: {e}")

try:
    building = building_repo.get(999)
except NotFoundError as e:
    print(f"Ошибка: {e}")
```

---

## 🔹 Шина событий (из `core.event_bus`)

```python
from src.core import EventBus
```

| Метод | Описание |
|-------|----------|
| `subscribe(event_type, callback)` | Подписка по классу события, возвращает unsubscribe |
| `emit(event_data, source=None)` | Испускание события с типизированными данными |
| `get_stats()` | Статистика использования |
| `clear()` | Очистить все подписки |
| `set_debug(enabled)` | Включить/выключить режим отладки |

**Пример использования:**
```python
from src.core import EventBus, NodeIdentifier, NodeType
from src.core.events import (
    DataLoaded, NodeSelected, NodeDetailsLoaded,
    CurrentSelectionChanged, BuildingDetailsLoaded
)

bus = EventBus(debug=True)

def on_data_loaded(event: Event[DataLoaded]) -> None:
    print(f"Загружено {event.data.count} объектов")

def on_node_selected(event: Event[NodeSelected]) -> None:
    print(f"Выбран {event.data.node.node_type.value}#{event.data.node.node_id}")

def on_selection_changed(event: Event[CurrentSelectionChanged]) -> None:
    if event.data.selection:
        print(f"Выбор изменён: {event.data.selection.node_type.value}#{event.data.selection.node_id}")
    else:
        print("Выбор сброшен")

# Подписка
unsub1 = bus.subscribe(DataLoaded, on_data_loaded)
unsub2 = bus.subscribe(NodeSelected, on_node_selected)
unsub3 = bus.subscribe(CurrentSelectionChanged, on_selection_changed)

# Испускание
bus.emit(DataLoaded(
    node_type="complex", node_id=0, payload=complexes, count=5
))
bus.emit(NodeSelected(
    node=NodeIdentifier(NodeType.BUILDING, 101)
))
bus.emit(CurrentSelectionChanged(
    selection=NodeIdentifier(NodeType.BUILDING, 101)
))

# Отписка
unsub1()
unsub2()
unsub3()
```

---

## 🔹 Правила иерархии (из `core.hierarchy`)

```python
from src.core.hierarchy import (
    get_child_type, get_parent_type,
    can_have_children, is_leaf,
    get_all_ancestors, get_all_descendants,
    validate_hierarchy
)
```

| Функция | Описание | Пример |
|---------|----------|--------|
| `get_child_type(parent_type)` | Тип детей | `get_child_type(NodeType.COMPLEX) → BUILDING` |
| `get_parent_type(child_type)` | Тип родителя | `get_parent_type(NodeType.ROOM) → FLOOR` |
| `can_have_children(node_type)` | Может ли иметь детей | `can_have_children(NodeType.ROOM) → False` |
| `is_leaf(node_type)` | Является ли листом | `is_leaf(NodeType.ROOM) → True` |
| `get_all_ancestors(node_type)` | Все предки | `[FLOOR, BUILDING, COMPLEX]` |
| `get_all_descendants(node_type)` | Все потомки | `[BUILDING, FLOOR, ROOM]` |
| `validate_hierarchy(parent, child)` | Проверка связи | `validate_hierarchy(COMPLEX, BUILDING) → True` |

**Пример использования:**
```python
from src.core import NodeType
from src.core.hierarchy import get_child_type, can_have_children

if can_have_children(NodeType.BUILDING):
    child_type = get_child_type(NodeType.BUILDING)  # FLOOR
    print(f"У здания могут быть {child_type.value}")
```

---

## 🔹 Сериализация (из `core.serializers`)

```python
from src.core.serializers import (
    identifier_to_key,          # NodeIdentifier → "type:id"
    key_to_identifier,          # "type:id" → NodeIdentifier (исключение)
    try_parse_identifier,       # "type:id" → NodeIdentifier | None
    format_display,             # NodeIdentifier → "TYPE#id"
    format_display_from_parts,  # (type, id) → "TYPE#id"
    parse_display,              # "TYPE#id" → NodeIdentifier (исключение)
    try_parse_display           # "TYPE#id" → NodeIdentifier | None
)
```

| Функция | Возврат | Ошибка | Назначение |
|---------|---------|--------|------------|
| `identifier_to_key()` | `str` | нет | Ключ для внутренних индексов |
| `key_to_identifier()` | `NodeIdentifier` | `SerializationError` | Строгий парсинг |
| `try_parse_identifier()` | `Optional[NodeIdentifier]` | нет | Безопасный парсинг |
| `format_display()` | `str` | нет | Для UI и логов |
| `parse_display()` | `NodeIdentifier` | `SerializationError` | Строгий парсинг display |
| `try_parse_display()` | `Optional[NodeIdentifier]` | нет | Безопасный парсинг display |

**Пример использования:**
```python
from src.core import NodeIdentifier, NodeType
from src.core.serializers import identifier_to_key, key_to_identifier, try_parse_identifier, format_display

# Создание идентификатора
node = NodeIdentifier(NodeType.BUILDING, 101)

# Преобразование в ключ
key = identifier_to_key(node)  # "building:101"

# Обратное преобразование (строгое)
restored = key_to_identifier(key)  # NodeIdentifier(BUILDING, 101)

# Безопасное преобразование
maybe = try_parse_identifier("invalid:key")  # None

# Форматирование для отображения (без атрибута .display!)
display = format_display(node)  # "BUILDING#101"
# Или вручную:
manual_display = f"{node.node_type.value.upper()}#{node.node_id}"  # "BUILDING#101"
```

---

## 🔹 Интерфейсы (из `core.interfaces`)

```python
from src.core import Repository
```

| Интерфейс | Описание |
|-----------|----------|
| `Repository[T, ID]` | Базовый контракт для репозиториев |

**Методы:**
- `get(id: ID) -> T` — возвращает сущность или выбрасывает `NotFoundError`
- `get_all() -> List[T]` — все сущности (может быть пустым)
- `add(entity: T) -> None` — добавляет или обновляет
- `remove(id: ID) -> None` — удаляет или выбрасывает `NotFoundError`
- `exists(id: ID) -> bool` — проверяет существование (без исключений)

**Пример использования:**
```python
from src.core import Repository, NotFoundError

class BuildingRepository(Repository[Building, int]):
    def get(self, id: int) -> Building:
        building = self._graph.get(NodeType.BUILDING, id)
        if building is None:
            raise NotFoundError(f"Building #{id} not found")
        return building
    
    def remove(self, id: int) -> None:
        if not self._graph.remove(NodeType.BUILDING, id):
            raise NotFoundError(f"Building #{id} not found")
```

---

## 🚫 Что НЕЛЬЗЯ импортировать из core

| Компонент | Почему |
|-----------|--------|
| `core.bus` | Приватная реализация, может меняться |
| `core.types.exceptions` напрямую | Использовать через `from src.core.types.exceptions import ...` или через `core` для базовых |
| Приватные функции `_make_node_key`, `_parse_node_key` | Внутренние, не для внешнего использования |
| `NodeIdentifier.display` | **Атрибут не существует!** Используйте `format_display()` или явное форматирование |

---

## 🎯 Главное правило импорта

```python
# ✅ Правильно — через публичное API
from src.core import NodeType, NodeIdentifier, EventBus
from src.core.events import (
    NodeSelected, DataLoaded, RefreshRequested,
    CurrentSelectionChanged, NodeDetailsLoaded, BuildingDetailsLoaded
)
from src.core.hierarchy import get_child_type
from src.core.serializers import identifier_to_key, key_to_identifier, format_display

# ✅ Тоже правильно — явные импорты из подмодулей
from src.core.types.exceptions import SerializationError, ConnectionError

# ❌ Неправильно — приватные модули
from src.core.bus.registry import _SubscriptionRegistry

# ❌ Неправильно — внутренние функции
from src.core.serializers import _make_node_key

# ❌ Неправильно — несуществующий атрибут
node.display  # AttributeError! Используйте format_display(node) или f"{node.node_type.value}#{node.node_id}"
```

---

## 📊 Чек-лист: что есть в core

| Категория | Количество | Статус |
|-----------|------------|--------|
| Базовые типы | 5 (`NodeType`, `NodeIdentifier`, `NodeID`, `NodeKey`, `ParentInfo`) | ✅ |
| Структуры событий | 2 (`EventData`, `Event`) | ✅ |
| **Классы событий** | **22** (было 9, добавлено 13) | ✅ |
| Исключения | 9 (`CoreError`, `NotFoundError`, `SerializationError`, ...) | ✅ |
| Шина событий | 1 класс, 6 методов | ✅ |
| Правила иерархии | 7 функций | ✅ |
| Сериализация | 7 публичных функций | ✅ |
| Интерфейсы | 1 (`Repository`) | ✅ |

### **Добавленные события (13):**
1. `CurrentSelectionChanged` — изменение выбранного узла
2. `ExpandedNodesChanged` — изменение списка раскрытых узлов
3. `NodeDetailsLoaded[T]` — детали узла загружены
4. `ChildrenLoaded[T]` — дети узла загружены
5. `BuildingDetailsLoaded` — детали корпуса с владельцем загружены
6. `NodeReloaded` — узел перезагружен
7. `VisibleNodesReloaded` — раскрытые узлы перезагружены
8. `FullReloadCompleted` — полная перезагрузка завершена
9. `NetworkActionsEnabled` — сетевые действия разрешены
10. `NetworkActionsDisabled` — сетевые действия запрещены
11. `NodeExpanded` (уже был, но активно используется)
12. `NodeCollapsed` (уже был, но активно используется)
13. `TabChanged` (уже был, но активно используется)

---

## 💡 Итог

Публичное API Core спроектировано так, чтобы быть:

- **Типобезопасным** — никаких строк, только классы и enum; Generic для передачи данных разного типа
- **Интуитивным** — `bus.subscribe(NodeDetailsLoaded[Building], handler)` — IDE подскажет
- **Минималистичным** — экспортируется только 8 базовых элементов
- **Стабильным** — приватные функции скрыты, обратная совместимость обеспечена
- **Полным** — 22 события покрывают все потребности контроллеров и UI

**Любой слой приложения может начать с:**
```python
from src.core import NodeType, NodeIdentifier, EventBus
from src.core.events import (
    NodeSelected, DataLoaded, RefreshRequested,
    CurrentSelectionChanged, NodeDetailsLoaded, BuildingDetailsLoaded
)
from src.core.hierarchy import get_child_type
from src.core.serializers import identifier_to_key, format_display
from src.core.types.exceptions import NotFoundError
```