## 📚 СПРАВКА ПО ЯДРУ (CORE) — версия 1.0

### 🎯 **Назначение ядра**

Ядро (`core`) — это **фундамент всего приложения**. Оно содержит только то, без чего приложение не может существовать:
- Базовые типы данных
- Контракты (интерфейсы)
- Правила предметной области
- Шину событий
- Утилиты общего назначения

**Важно:** Core не зависит от других слоёв (models, data, services, ui) и не должен их импортировать!

---

## 📁 **Структура ядра**

```
core/
├── __init__.py                    # Публичное API (витрина)
├── event_constants.py              # Константы всех событий
├── event_bus.py                    # Фасад шины событий
├── hierarchy.py                    # Правила иерархии объектов
├── serializers.py                   # Преобразования идентификаторов
│
├── types/                          # Базовые типы
│   ├── __init__.py
│   ├── nodes.py                    # Типы узлов
│   ├── event_structures.py         # Структуры событий
│   └── exceptions.py               # Базовые исключения
│
├── interfaces/                      # Базовые контракты
│   ├── __init__.py
│   └── repository.py                # Интерфейс репозитория
│
├── bus/                             # Реализация шины (приватно)
│   ├── __init__.py
│   ├── weak_callback.py
│   └── registry.py
│
└── utils/                           # Утилиты
    ├── __init__.py
    ├── comparison.py
    ├── time.py
    └── validation.py
```

---

## 📦 **Публичное API (что можно импортировать из core)**

### 🔹 **Базовые типы** (из `core.types`)

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

### 🔹 **Структуры событий** (из `core.types`)

```python
from core import Event, EventData
```

| Класс | Назначение |
|-------|------------|
| `EventData` | Базовый класс для данных всех событий |
| `Event` | Конверт события с метаданными |

### 🔹 **Исключения** (из `core.types`)

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

### 🔹 **Константы событий** (из `core.event_constants`)

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

### 🔹 **Шина событий** (из `core.event_bus`)

```python
from core import EventBus
```

| Метод | Описание |
|-------|----------|
| `subscribe(event_type, callback)` | Подписаться на событие |
| `emit(event_type, data=None, source=None)` | Испустить событие |
| `get_stats()` | Получить статистику |
| `clear()` | Очистить все подписки |
| `set_debug(enabled)` | Включить/выключить режим отладки |

### 🔹 **Правила иерархии** (из `core.hierarchy`)

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

### 🔹 **Сериализация** (из `core.serializers`)

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
| `safe_parse_node_key(key)` | Безопасный парсинг | `NodeIdentifier` или исключение |

### 🔹 **Интерфейсы** (из `core.interfaces`)

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

### 🔹 **Утилиты** (из `core.utils`)

```python
from core import (
    has_changed, is_equal,
    current_timestamp, current_timestamp_ms,
    format_timestamp, format_timestamp_short,
    Timer,
    is_valid_node_type, is_valid_node_id, is_valid_identifier,
    validate_non_empty, validate_positive_int
)
```

| Утилита | Описание |
|---------|----------|
| `has_changed(old, new)` | Проверка изменений |
| `is_equal(old, new)` | Проверка равенства |
| `current_timestamp()` | Текущее время в ISO |
| `current_timestamp_ms()` | Текущее время в мс |
| `format_timestamp(dt)` | Формат "дд.мм.гггг чч:мм:сс" |
| `format_timestamp_short(dt)` | Формат "дд.мм.гггг чч:мм" |
| `Timer(operation_name)` | Контекстный менеджер для замера времени |
| `is_valid_node_type(str)` | Проверка типа узла |
| `is_valid_node_id(val)` | Проверка ID |
| `is_valid_identifier(obj)` | Проверка NodeIdentifier |
| `validate_non_empty(str, name)` | Валидация непустой строки |
| `validate_positive_int(val, name)` | Валидация положительного числа |

---

## 📋 **Примеры использования**

### Пример 1: Работа с типами
```python
from core import NodeType, NodeIdentifier, make_node_key

# Создание идентификатора
node_id = NodeIdentifier(NodeType.COMPLEX, 42)

# Преобразование в ключ
key = make_node_key(NodeType.BUILDING, 101)  # "building:101"

# Проверка типа
if node_id.node_type == NodeType.COMPLEX:
    print("Это комплекс!")
```

### Пример 2: Шина событий
```python
from core import EventBus, UIEvents

bus = EventBus()

def on_node_selected(event):
    print(f"Выбран узел: {event['data']}")

# Подписка
unsubscribe = bus.subscribe(UIEvents.NODE_SELECTED, on_node_selected)

# Испускание
bus.emit(UIEvents.NODE_SELECTED, {'node_id': 42}, source='my_module')

# Отписка
unsubscribe()
```

### Пример 3: Правила иерархии
```python
from core import NodeType, get_child_type, can_have_children

if can_have_children(NodeType.FLOOR):
    child_type = get_child_type(NodeType.FLOOR)  # ROOM
    print(f"У этажа могут быть {child_type}")
```

### Пример 4: Валидация
```python
from core import validate_positive_int, ValidationError

try:
    building_id = validate_positive_int(user_input, "ID здания")
except ValidationError as e:
    print(f"Ошибка: {e}")
```

### Пример 5: Таймер для замера производительности
```python
from core import Timer

with Timer("Загрузка данных"):
    # какой-то долгий код
    data = api.get_complexes()
# В логе: "⏱ Загрузка данных: 123.45 мс"
```

---

## 🚫 **Что НЕЛЬЗЯ импортировать из core**

| Компонент | Почему |
|-----------|--------|
| `core.bus` | Приватная реализация, может меняться |
| `core.utils.*` напрямую | Использовать через `core` или явный импорт |
| Внутренние модули types | Только через `core.types` |

---

## 🎯 **Главное правило**

```python
# ✅ Правильно
from core import NodeType, EventBus, UIEvents, has_changed

# ✅ Тоже правильно (явный импорт из подмодуля)
from core.hierarchy import get_child_type
from core.serializers import make_node_key

# ❌ Неправильно (приватный модуль)
from core.bus.registry import _SubscriptionRegistry
```

---

## 📊 **Чек-лист: что есть в core**

| Категория | Количество | Готово |
|-----------|------------|--------|
| Базовые типы | 4 | ✅ |
| Структуры событий | 2 | ✅ |
| Исключения | 6 | ✅ |
| Константы событий | 5 классов | ✅ |
| Шина событий | 1 класс | ✅ |
| Правила иерархии | 7 функций | ✅ |
| Сериализация | 8 функций | ✅ |
| Интерфейсы | 1 протокол | ✅ |
| Утилиты | 11 функций | ✅ |

---

## 📝 **Итог**

Ядро предоставляет **всё необходимое** для построения остальных слоёв приложения, оставаясь при этом:
- **Минимальным** — только то, без чего нельзя
- **Стабильным** — редко меняется
- **Независимым** — не тянет другие слои
- **Типизированным** — полная поддержка IDE
- **Документированным** — каждый элемент описан

**Можно смело использовать при написании models, data, services, controllers и ui!**