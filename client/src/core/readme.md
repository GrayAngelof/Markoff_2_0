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
from core import (
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

## Описание реализации и структуры

В соответствии со спецификацией, ядро реализовано как минимальный, но самодостаточный слой, обеспечивающий типобезопасность и слабую связанность. Код организован в следующую структуру каталогов, где каждый модуль отвечает за свою часть фундамента:

```
core/
├── __init__.py                    # Публичное API, экспортирующее основные компоненты
├── event_constants.py             # Константы событий (UIEvents, SystemEvents и т.д.)
├── event_bus.py                   # Фасад шины событий (EventBus) для подписки и эмиссии
├── hierarchy.py                   # Правила иерархии узлов (функции get_child_type, validate_hierarchy и др.)
├── serializers.py                 # Преобразования идентификаторов (make_node_key, parse_node_key и др.)
│
├── types/                         # Базовые типы и исключения
│   ├── __init__.py
│   ├── nodes.py                   # NodeType (enum), NodeIdentifier (value object)
│   ├── protocols.py               # Протоколы для типизации объектов, имеющих NODE_TYPE.
│   ├── event_structures.py        # EventData, Event (конверт события)
│   └── exceptions.py              # Иерархия исключений (CoreError, ValidationError...)
│
├── interfaces/                    # Базовые контракты
│   ├── __init__.py
│   └── repository.py              # Абстрактный базовый класс Repository[T, ID]
│
└── bus/                           # Приватная реализация шины (не для импорта снаружи)
    ├── __init__.py
    ├── weak_callback.py           # Обёртка для слабых ссылок на callback'и
    └── registry.py                # Реестр подписчиков для EventBus
```

Такая структура гарантирует, что Core остаётся независимым, легко тестируемым и понятным. Всё, что не является фундаментом, исключено из этого слоя, что предотвращает его разрастание и сохраняет чёткие границы ответственности.

## 📦 Публичное API (что можно импортировать из core)

### 🔹 Базовые типы (из `core.types`)

```python
from core import NodeType, NodeIdentifier, NodeID, NodeKey, ParentInfo
```

| Тип | Описание | Пример |
|-----|----------|--------|
| `NodeType` | Enum типов узлов | `NodeType.COMPLEX`, `NodeType.BUILDING` |
| `NodeID` | Алиас для int (ID узла) | `complex_id: NodeID = 42` |
| `NodeKey` | Строковый ключ "тип:id" | `"complex:42"` |
| `ParentInfo` | Кортеж (тип, id) родителя | `(NodeType.BUILDING, 101)` |
| `NodeIdentifier` | Value Object идентификатора | `NodeIdentifier(NodeType.COMPLEX, 42)` |

**Пример использования:**
```python
# Создание идентификатора
node_id = NodeIdentifier(NodeType.COMPLEX, 42)

# Доступ к атрибутам
print(node_id.node_type)  # NodeType.COMPLEX
print(node_id.id)         # 42

# Сравнение
another_id = NodeIdentifier(NodeType.COMPLEX, 42)
assert node_id == another_id  # True (сравниваются тип и id)

# ParentInfo для передачи информации о родителе
parent = (NodeType.BUILDING, 101)
```

### 🔹 Структуры событий (из `core.types`)

```python
from core import Event, EventData
```

| Класс | Назначение |
|-------|------------|
| `EventData` | Базовый класс для данных всех событий |
| `Event` | Конверт события с метаданными |

**Пример использования:**
```python
from dataclasses import dataclass

# Всегда наследуйтесь от EventData
@dataclass
class NodeSelected(EventData):
    """Данные события выбора узла"""
    node_id: int
    node_type: NodeType
    source: str = "user"

# Создание конверта события (обычно делает EventBus)
event = Event(
    type=UIEvents.NODE_SELECTED,
    data=NodeSelected(node_id=42),
    source="tree_view",
    timestamp="2024-01-15T10:30:00"
)
```

### 🔹 Исключения (из `core.types`)

```python
from core import CoreError, ValidationError, NotFoundError, DuplicateError
```

| Исключение | Когда возникает |
|------------|-----------------|
| `CoreError` | Базовое для всех ошибок ядра |
| `ValidationError` | Ошибка валидации данных |
| `NotFoundError` | Объект не найден |
| `DuplicateError` | Дубликат объекта |
| `ConfigurationError` | Ошибка конфигурации |
| `HierarchyError` | Ошибка в иерархии |
| `SerializationError` | Ошибка сериализации |

**Пример использования:**
```python
try:
    node = repository.get(42)
    if node is None:
        raise NotFoundError(f"Узел с ID 42 не найден")
except NotFoundError as e:
    logger.error(f"Ошибка: {e}")
```

### 🔹 Константы событий (из `core.event_constants`)

```python
from core import UIEvents, SystemEvents, HotkeyEvents, ProjectionEvents, CustomEvents
```

| Класс | Категория | Пример |
|-------|-----------|--------|
| `UIEvents` | Команды от пользователя | `UIEvents.NODE_SELECTED` |
| `SystemEvents` | Системные факты | `SystemEvents.DATA_LOADED` |
| `HotkeyEvents` | Горячие клавиши | `HotkeyEvents.REFRESH_CURRENT` |
| `ProjectionEvents` | События проекций | `ProjectionEvents.TREE_UPDATED` |
| `CustomEvents` | Пользовательские | `CustomEvents.BUILDING_OWNER_LOADED` |

**Пример использования:**
```python
# Подписка на системное событие
bus.subscribe(SystemEvents.DATA_LOADED, on_data_loaded)

# Испускание события от пользователя
bus.emit(UIEvents.NODE_SELECTED, NodeSelected(node_id=42))
```

### 🔹 Шина событий (из `core.event_bus`)

```python
from core import EventBus
```

| Метод | Описание |
|-------|----------|
| `subscribe(event_type, callback)` | Подписаться на событие, возвращает функцию для отписки |
| `emit(event_type, data=None, source=None)` | Испустить событие |
| `get_stats()` | Получить статистику использования |
| `clear()` | Очистить все подписки |
| `set_debug(enabled)` | Включить/выключить режим отладки |

**Пример использования:**
```python
# Создание шины (обычно синглтон в приложении)
bus = EventBus()

# Подписка на событие
def handle_node_selected(event: Event):
    print(f"Выбран узел: {event.data.node_id}")

unsubscribe = bus.subscribe(UIEvents.NODE_SELECTED, handle_node_selected)

# Испускание события
bus.emit(
    UIEvents.NODE_SELECTED,
    NodeSelected(node_id=42),
    source="navigation"
)

# Отписка, когда обработчик больше не нужен
unsubscribe()

# Получение статистики
stats = bus.get_stats()
print(f"Всего подписок: {stats['total_subscriptions']}")
print(f"Событий испущено: {stats['events_emitted']}")
```

### 🔹 Правила иерархии (из `core.hierarchy`)

```python
from core import (
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
from core import NodeType, validate_hierarchy, can_have_children

# Проверка возможности связи
if can_have_children(NodeType.BUILDING):
    child_type = get_child_type(NodeType.BUILDING)  # FLOOR
    print(f"У здания могут быть {child_type}")

# Валидация при создании связи
try:
    validate_hierarchy(NodeType.FLOOR, NodeType.ROOM)  # OK
    validate_hierarchy(NodeType.ROOM, NodeType.BUILDING)  # HierarchyError
except HierarchyError as e:
    print(f"Недопустимая иерархия: {e}")

# Получение всех предков для типа
ancestors = get_all_ancestors(NodeType.ROOM)
# [NodeType.FLOOR, NodeType.BUILDING, NodeType.COMPLEX]
```

### 🔹 Сериализация (из `core.serializers`)

```python
from core import (
    make_node_key, parse_node_key,
    identifier_to_key, key_to_identifier,
    format_display_id, format_display_from_parts,
    parse_display_id, safe_parse_node_key
)
```

| Функция | Описание | Пример |
|---------|----------|--------|
| `make_node_key(type, id)` | Создать ключ | `"complex:42"` |
| `parse_node_key(key)` | Разобрать ключ | `NodeIdentifier(COMPLEX, 42)` |
| `identifier_to_key(identifier)` | ID → ключ | `"complex:42"` |
| `key_to_identifier(key)` | Ключ → ID | `NodeIdentifier(COMPLEX, 42)` |
| `format_display_id(identifier)` | Для отображения | `"COMPLEX#42"` |
| `format_display_from_parts(type, id)` | Из частей | `"COMPLEX#42"` |
| `parse_display_id(display)` | Разобрать display | `NodeIdentifier(COMPLEX, 42)` |
| `safe_parse_node_key(key)` | Безопасный парсинг | `NodeIdentifier` или None |

**Пример использования:**
```python
from core import NodeIdentifier, NodeType

# Создание идентификатора
node_id = NodeIdentifier(NodeType.BUILDING, 101)

# Преобразование в ключ для хранения в словаре
key = identifier_to_key(node_id)  # "building:101"

# Обратное преобразование
restored_id = key_to_identifier(key)
assert restored_id == node_id

# Форматирование для отображения пользователю
display = format_display_id(node_id)  # "BUILDING#101"

# Безопасный парсинг пользовательского ввода
user_input = "COMPLEX#42"
parsed = parse_display_id(user_input)  # NodeIdentifier(COMPLEX, 42)

# Безопасный парсинг ключа с обработкой ошибок
result = safe_parse_node_key("invalid:format")
if result is None:
    print("Некорректный формат ключа")
```

### 🔹 Интерфейсы (из `core.interfaces`)

```python
from core import Repository
```

| Интерфейс | Описание |
|-----------|----------|
| `Repository[T, ID]` | Базовый контракт для всех репозиториев |

**Методы:**
- `get(id: ID) -> Optional[T]`
- `get_all() -> List[T]`
- `add(entity: T) -> None`
- `remove(id: ID) -> bool`

**Пример использования (реализация в data слое):**
```python
from core import Repository, NodeIdentifier

class BuildingRepository(Repository[Building, NodeIdentifier]):
    def __init__(self, db_session):
        self._session = db_session
    
    def get(self, id: NodeIdentifier) -> Optional[Building]:
        if id.node_type != NodeType.BUILDING:
            raise ValidationError(f"Ожидается BUILDING, получен {id.node_type}")
        return self._session.query(Building).get(id.id)
    
    def get_all(self) -> List[Building]:
        return self._session.query(Building).all()
    
    def add(self, entity: Building) -> None:
        self._session.add(entity)
    
    def remove(self, id: NodeIdentifier) -> bool:
        building = self.get(id)
        if building:
            self._session.delete(building)
            return True
        return False
```


## 🚫 Что НЕЛЬЗЯ импортировать из core

| Компонент | Почему |
|-----------|--------|
| `core.bus` | Приватная реализация, может меняться без предупреждения |
| `core.utils.*` напрямую | Использовать через `core` или явный импорт из подмодулей |
| Внутренние модули types | Только через `core.types` (хотя обычно хватает `from core import ...`) |

---

## 🎯 Главное правило импорта

```python
# ✅ Правильно (импорт через публичное API)
from core import NodeType, EventBus, UIEvents, has_changed, Repository

# ✅ Тоже правильно (явный импорт из подмодуля, если нужно)
from core.hierarchy import get_child_type
from core.serializers import make_node_key

# ❌ Неправильно (приватный модуль, внутренняя реализация)
from core.bus.registry import _SubscriptionRegistry

# ❌ Неправильно (глубокий обход публичного API)
from core.types.nodes import NodeType  # лучше from core import NodeType
```

---

## 📊 Чек-лист: что есть в core

| Категория | Количество | Готово |
|-----------|------------|--------|
| Базовые типы | 4 | ✅ |
| Структуры событий | 2 | ✅ |
| Исключения | 7 | ✅ |
| Константы событий | 5 классов | ✅ |
| Шина событий | 1 класс, 5 методов | ✅ |
| Правила иерархии | 7 функций | ✅ |
| Сериализация | 8 функций | ✅ |
| Интерфейсы | 1 протокол | ✅ |

---

## 💡 Итог

Публичное API Core спроектировано так, чтобы быть:
- **Интуитивным** — имена функций говорят сами за себя
- **Типобезопасным** — везде используются строгие типы вместо `dict`
- **Минимальным** — только то, что нужно всем слоям
- **Стабильным** — обратная совместимость сохраняется

**Любой слой приложения может начать с:**
```python
from core import (
    NodeType,           # Работа с типами
    NodeIdentifier,     # Идентификаторы
    EventBus,           # Шина событий
    UIEvents,           # Константы
    Repository          # Если нужно реализовать хранилище
)
```