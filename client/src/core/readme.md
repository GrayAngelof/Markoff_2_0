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


# Core — описание слоя

## Назначение

Минимальный самодостаточный слой, обеспечивающий типобезопасность и слабую связанность через type-based события.

**Строгая зависимость:** другие слои импортируют только из `core`. Обратные импорты запрещены.

---

## Структура

```
core/
├── __init__.py              # Публичное API
├── event_bus.py             # Шина событий (фасад)
├── events/
│   ├── __init__.py          # Экспорт событий
│   └── definitions.py       # Классы событий
├── bus/                     # ПРИВАТНО — реализация шины
├── ports/                   # Интерфейсы (Protocol)
│   └── repository.py        # Repository[T, ID]
├── rules/
│   └── hierarchy.py         # Правила иерархии узлов
└── types/
    ├── nodes.py             # NodeType, NodeIdentifier
    ├── event_structures.py  # EventData, Event
    ├── exceptions.py        # Иерархия исключений
    └── protocols.py         # Структурные типы
```

---

## Публичное API

### Импорт

```python
# Базовое
from src.core import NodeType, NodeIdentifier, EventBus

# Исключения
from src.core import CoreError, NotFoundError, ValidationError

# События
from src.core.events import (
    NodeSelected, NodeExpanded, NodeCollapsed, TabChanged,
    RefreshRequested, ShowDetailsPanel,
    DataLoaded, DataError, DataInvalidated,
    ChildrenLoaded, NodeDetailsLoaded, ConnectionChanged
)

# Правила иерархии
from src.core.rules.hierarchy import (
    get_child_type, get_parent_type, can_have_children,
    is_leaf, get_all_ancestors, get_all_descendants, validate_hierarchy
)

# Интерфейсы
from src.core.ports.repository import Repository
```

---

## Компоненты

### 1. Типы (`types/`)

| Тип | Назначение |
|-----|------------|
| `NodeType` | Enum типов узлов: `COMPLEX`, `BUILDING`, `FLOOR`, `ROOM`, `COUNTERPARTY`, `RESPONSIBLE_PERSON` |
| `NodeIdentifier` | Value object: `(node_type, node_id)`, frozen, slots |
| `EventData` | Базовый класс для всех событий |
| `Event[T]` | Конверт с метаданными: `source`, `timestamp` |

**Пример:**
```python
node = NodeIdentifier(NodeType.BUILDING, 101)
```

---

### 2. Исключения (`types/exceptions.py`)

| Исключение | Назначение |
|------------|------------|
| `CoreError` | Базовое для всех ошибок ядра |
| `NotFoundError` | Объект не найден |
| `ValidationError` | Ошибка валидации |
| `SerializationError` | Ошибка парсинга |
| `ConnectionError` | Ошибка сети |
| `ApiError` | Ошибка API |
| `ConfigurationError` | Ошибка конфигурации |
| `HierarchyError` | Ошибка иерархии |
| `DuplicateError` | Дубликат |

---

### 3. События (`events/definitions.py`)

#### UI события (факты)
- `NodeSelected[T]` — выбран узел
- `NodeExpanded` — раскрыт узел
- `NodeCollapsed` — свёрнут узел
- `TabChanged` — переключена вкладка

#### Команды
- `RefreshRequested` — запрос на обновление (mode: current/visible/full)
- `ShowDetailsPanel` — показать панель деталей

#### События данных
- `DataLoaded[T]` — данные загружены
- `DataError` — ошибка загрузки
- `DataInvalidated` — данные устарели

#### События деталей
- `ChildrenLoaded[T]` — загружены дочерние элементы
- `NodeDetailsLoaded[T]` — загружена детальная информация

#### Системные
- `ConnectionChanged` — изменился статус соединения

---

### 4. Шина событий (`EventBus`)

| Метод | Описание |
|-------|----------|
| `subscribe(event_type, callback)` | Подписка, возвращает `unsubscribe()` |
| `emit(event_data, source=None)` | Испускание события |
| `clear()` | Очистка всех подписок |
| `set_debug(enabled)` | Режим отладки |

**Особенности:**
- Подписка по типу события (класс)
- Слабые ссылки — автоматическая очистка мёртвых обработчиков
- Типобезопасные обработчики

```python
bus = EventBus()

def handler(event: NodeSelected) -> None:
    print(event.data.node.node_id)

unsub = bus.subscribe(NodeSelected, handler)
bus.emit(NodeSelected(node=identifier))
unsub()
```

---

### 5. Правила иерархии (`rules/hierarchy.py`)

| Функция | Возврат |
|---------|---------|
| `get_child_type(parent_type)` | тип детей или `None` |
| `get_parent_type(child_type)` | тип родителя или `None` |
| `can_have_children(node_type)` | `bool` |
| `is_leaf(node_type)` | `bool` |
| `get_all_ancestors(node_type)` | `List[NodeType]` |
| `get_all_descendants(node_type)` | `List[NodeType]` |
| `validate_hierarchy(parent, child)` | `bool` |

**Пример:**
```python
get_child_type(NodeType.COMPLEX)        # BUILDING
get_parent_type(NodeType.ROOM)          # FLOOR
can_have_children(NodeType.ROOM)        # False
get_all_ancestors(NodeType.ROOM)        # [FLOOR, BUILDING, COMPLEX]
```

---

### 6. Интерфейсы репозиториев (`ports/repository.py`)

```python
class Repository(Protocol[T, ID]):
    def get(self, id: ID) -> T: ...
    def get_all(self) -> List[T]: ...
    def add(self, entity: T) -> None: ...
    def remove(self, id: ID) -> bool: ...
```

**Контракт:**
- `get()` выбрасывает `NotFoundError` при отсутствии
- `remove()` возвращает `bool` (удалено/не найдено)

---

## Приватные модули (не импортировать)

| Модуль | Причина |
|--------|---------|
| `core.bus` | Внутренняя реализация `EventBus` |
| `core.types.protocols` | Внутренняя типизация |

---

## Зависимости от других слоёв

**Core не имеет зависимостей на другие слои приложения.**  
Единственное исключение — `utils.logger`, допустимый как инфраструктурная утилита на всех слоях.

---

## Итог

Слой предоставляет вышележащим слоям:
- **Типобезопасную** коммуникацию через `EventBus`
- **Value objects** для идентификации узлов
- **Правила иерархии** без обращения к данным
- **Базовые интерфейсы** для репозиториев
- **Иерархию исключений** для единообразной обработки ошибок