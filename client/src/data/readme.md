## Анализ слоя: **data** (доступ к данным и граф сущностей)

### Краткое описание слоя

**Назначение** – управление хранением, связями, валидностью и состоянием загрузки сущностей в памяти. Слой `data` предоставляет **единый фасад `EntityGraph`** для всех операций с данными, а также **репозитории** для типобезопасного доступа к сущностям. Слой не содержит бизнес-логики (она в `services`) и не зависит от UI.

**Что делает:**
- Хранит сущности (`EntityStore`), поддерживает индексы связей родитель-потомок (`RelationIndex`)
- Отслеживает валидность данных (`ValidityIndex`) – какие сущности актуальны, а какие требуют перезагрузки
- Управляет состоянием загрузки детей (`LoadStateIndex`) – предотвращает повторные загрузки и гонки
- Обеспечивает потокобезопасность всех операций (через `RLock`)
- Предоставляет репозитории для каждого типа сущности (`ComplexRepository`, `BuildingRepository` и т.д.), реализующие контракт `core.Repository`
- Координирует все внутренние компоненты через фасад `EntityGraph`

**Что не должен делать:**
- Импортировать что-либо из `services`, `projections`, `controllers`, `ui`
- Содержать бизнес-правила предметной области (фильтрацию, поиск, валидацию)
- Обращаться напрямую к API или БД (это задача адаптеров, слой `data` – кэш в памяти)
- Содержать UI-специфичный код

---

### Файловая структура слоя

```
client/src/data/
├── __init__.py                    # Публичное API: EntityGraph, репозитории
├── entity_graph.py                # Фасад графа (координирует store, relations, validity, load_state)
├── graph/                         # Внутренние компоненты графа (приватные)
│   ├── __init__.py                # Маркер приватности
│   ├── consistency.py             # ConsistencyChecker (проверка целостности индексов)
│   ├── load_state.py              # LoadState, LoadStateIndex (состояние загрузки детей)
│   ├── locked.py                  # LockedComponent (базовый класс с RLock)
│   ├── relations.py               # RelationIndex (связи родитель-потомок)
│   ├── schema.py                  # Схема: parent_id field, get_node_type, get_parent_id
│   ├── store.py                   # EntityStore (хранение сущностей)
│   └── validity.py                # ValidityIndex (валидность данных)
├── repositories/                  # Репозитории (публичные)
│   ├── __init__.py                # Экспорт всех репозиториев
│   ├── base.py                    # BaseRepository (реализация core.Repository)
│   ├── complex.py                 # ComplexRepository
│   ├── building.py                # BuildingRepository
│   ├── floor.py                   # FloorRepository
│   ├── room.py                    # RoomRepository
│   ├── counterparty.py            # CounterpartyRepository
│   └── responsible_person.py      # ResponsiblePersonRepository
└── utils/                         # Внутренние утилиты (не экспортируются)
    └── decorators.py              # validate_ids (декоратор валидации ID)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `EntityGraph` | `entity_graph.py` | **Фасад** – координация store, relations, validity, load_state. Предоставляет единое API для всех операций с данными. |
| `EntityStore` | `graph/store.py` | Хранилище сущностей: `put`, `get`, `remove`, `get_all`. Не знает о связях или валидности. |
| `RelationIndex` | `graph/relations.py` | Индекс связей родитель-потомок (прямые и обратные). O(1) навигация. Потокобезопасен. |
| `ValidityIndex` | `graph/validity.py` | Отслеживает, какие сущности актуальны. Поддерживает точечную и веточную инвалидацию, генерирует `DataInvalidated`. |
| `LoadStateIndex` | `graph/load_state.py` | Состояние загрузки детей: `NOT_LOADED`, `LOADING`, `LOADED`. Предотвращает повторные загрузки. |
| `ConsistencyChecker` | `graph/consistency.py` | Проверяет целостность индексов (для диагностики). |
| `LockedComponent` | `graph/locked.py` | Базовый класс с `RLock` для синхронизации. |
| `BaseRepository[T]` | `repositories/base.py` | Абстрактный репозиторий, реализующий `core.Repository`. Хранит ссылку на `EntityGraph`. |
| `ComplexRepository`, `BuildingRepository`, … | `repositories/*.py` | Конкретные репозитории, добавляющие методы навигации (`get_building_ids`, `get_floor_ids` и т.п.). |

---

### Внутренние импорты (только между модулями проекта)

Игнорируем `utils.logger`, `src.shared.*`, стандартные библиотеки.

**Из `entity_graph.py`**:
- `from src.core import EventBus`
- `from src.core.rules.hierarchy import get_child_type, get_parent_type`
- `from src.core.types import NodeIdentifier, NodeType`
- `from src.core.types.nodes import NodeID`
- `from .graph.consistency import ConsistencyChecker`
- `from .graph.decorators import validate_ids` (не используется в коде – декоратор, но импорт есть)
- `from .graph.load_state import LoadState, LoadStateIndex`
- `from .graph.relations import RelationIndex, RelationStats`
- `from .graph.schema import get_node_type, get_parent_id`
- `from .graph.store import EntityStore, StoreStats`
- `from .graph.validity import ValidityIndex, ValidityStats`

**Из `graph/relations.py`**:
- `from src.core.types import NodeType`
- `from src.shared.validation import validate_positive_int`
- `from .schema import get_child_type, get_parent_type`

**Из `graph/validity.py`**:
- `from src.core import EventBus`
- `from src.core.events.definitions import DataInvalidated`
- `from src.core.rules.hierarchy import get_child_type`
- `from src.core.types import NodeType`
- `from src.shared.validation import validate_positive_int`

**Из `graph/schema.py`**:
- `from src.core.rules.hierarchy import get_child_type, get_parent_type`
- `from src.core.types import NodeType`
- `from src.core.types.protocols import HasNodeType`

**Из `repositories/base.py`**:
- `from src.core import NodeType, NotFoundError`
- `from src.core.ports.repository import Repository as CoreRepository`
- `from src.data.entity_graph import EntityGraph`

**Из `repositories/*.py`**:
- `from src.core import NodeType`
- `from src.models import Complex, Building, Floor, Room, Counterparty, ResponsiblePerson`
- `from .base import BaseRepository`

**Из `graph/load_state.py`**:
- `from src.core.types import NodeType`

**Из `graph/store.py`**:
- `from src.core.types import NodeType`
- `from src.shared.validation import validate_positive_int`

**Из `utils/decorators.py`**:
- `from src.shared.validation import validate_positive_int`

---

### Экспортируемые методы / классы для вышестоящих слоёв (`services`, `projections`, `controllers`)

Через `data/__init__.py` экспортируются:

**Фасад графа:**
- `EntityGraph` – основной класс для работы с данными (CRUD, навигация, валидация, состояние загрузки)
- `EntityGraphStats` – TypedDict со статистикой

**Репозитории (все наследуют `BaseRepository` и реализуют `core.Repository`):**
- `BaseRepository` (для создания собственных репозиториев)
- `ComplexRepository`
- `BuildingRepository`
- `FloorRepository`
- `RoomRepository`
- `CounterpartyRepository`
- `ResponsiblePersonRepository`

**Основные методы `EntityGraph` (публичное API):**

| Категория | Метод | Назначение |
|-----------|-------|-------------|
| Жизненный цикл | `clear()` | Полная очистка графа. |
| CRUD | `add_or_update(entity)` | Добавить или обновить сущность. |
| | `add_or_update_bulk(entities)` | Пакетная вставка/обновление. |
| | `get(node_type, id)` | Получить сущность или None. |
| | `get_all(node_type)` | Все сущности типа. |
| | `get_all_ids(node_type)` | Все ID типа. |
| | `has_entity(node_type, id)` | Проверка существования. |
| | `remove(node_type, id, cascade=False)` | Удаление (опционально каскадное). |
| Навигация | `get_children(parent_type, parent_id)` | ID детей. |
| | `get_parent(child_type, child_id)` | Родитель как `NodeIdentifier`. |
| | `get_ancestors(node_type, node_id)` | Список предков. |
| Валидность | `is_valid(node_type, id)` | Проверка валидности. |
| | `validate(node_type, id)` | Пометить как валидный. |
| | `validate_bulk(node_type, ids)` | Массовая валидация. |
| | `invalidate(node_type, id)` | Инвалидировать один узел. |
| | `invalidate_bulk(node_type, ids)` | Массовая инвалидация. |
| | `invalidate_branch(node_type, id)` | Инвалидировать всю ветку. |
| Состояние загрузки | `is_children_loaded(node_type, id)` | Загружены ли дети? |
| | `mark_children_loading(node_type, id)` | Начать загрузку. |
| | `mark_children_loaded(node_type, id)` | Завершить загрузку. |
| | `mark_children_load_failed(node_type, id)` | Ошибка загрузки. |
| | `reset_children_state(node_type, id)` | Сбросить состояние. |
| Временные метки | `get_timestamp(node_type, id)` | Время последнего обновления. |
| Диагностика | `get_stats()` | Статистика (store, relations, validity, load_state). |
| | `print_stats()` | Вывод статистики в лог. |
| | `check_consistency()` | Проверка целостности. |
| Для загрузчика | `get_if_full(node_type, id)` | Получить, только если есть полные данные. |
| | `get_cached_children(parent_type, parent_id, child_type)` | Получить детей только если все в кэше. |

**Методы репозиториев (помимо CRUD от `BaseRepository`):**

| Репозиторий | Метод навигации |
|-------------|----------------|
| `ComplexRepository` | `get_building_ids(complex_id)` |
| `BuildingRepository` | `get_floor_ids(building_id)`, `get_by_complex(complex_id)` |
| `FloorRepository` | `get_room_ids(floor_id)`, `get_by_building(building_id)` |
| `RoomRepository` | `get_by_floor(floor_id)` |
| `CounterpartyRepository` | `get_person_ids(counterparty_id)` |
| `ResponsiblePersonRepository` | `get_by_counterparty(counterparty_id)` |

---

### Итоговое заключение: принципы работы со слоем `data`

1. **Импорт только сверху вниз** – слой `data` может импортировать из `core` и `models`, но **не должен** импортировать из `services`, `projections`, `controllers`, `ui`. Проверка показывает корректность зависимостей.

2. **Используйте `EntityGraph` как единый фасад** – все операции с данными (CRUD, навигация, валидация, состояние загрузки) проходят через него. Никогда не обращайтесь напрямую к внутренним компонентам (`EntityStore`, `RelationIndex` и т.д.) – они приватные.

3. **Для типобезопасного доступа используйте репозитории** – каждый репозиторий работает с конкретной моделью (`Complex`, `Building` и т.д.) и предоставляет методы навигации, возвращающие ID (ленивая загрузка). Репозитории реализуют контракт `core.Repository`.

4. **Валидность данных** – после успешной загрузки из внешнего источника вызывайте `validate()` или `validate_bulk()`. При изменении данных (обновление, удаление) вызывайте `invalidate()` или `invalidate_branch()`. Это позволит слою `services` знать, когда нужно перезагружать данные.

5. **Состояние загрузки детей** – перед загрузкой детей вызовите `mark_children_loading()`, после успеха – `mark_children_loaded()`. Это предотвращает дублирующиеся запросы. Если загрузка упала – `mark_children_load_failed()`.

6. **Потокобезопасность** – все методы `EntityGraph` и внутренних компонентов используют `RLock`, поэтому можно вызывать из любых потоков.

7. **Пакетные операции** – для массовой вставки/обновления используйте `add_or_update_bulk()` – это эффективнее, чем по одному вызову.

8. **Удаление** – если нужно удалить узел со всеми потомками, используйте `remove(node_type, id, cascade=True)`. Это корректно обновит индексы связей и валидность.

9. **Диагностика** – в режиме отладки можно вызывать `print_stats()` и `check_consistency()` для проверки целостности графа.

Слой `data` является **кэширующим графом в памяти** – он не знает, откуда приходят данные (API, БД, файлы). Его задача – обеспечить быстрый доступ к уже загруженным сущностям и отслеживать их актуальность.