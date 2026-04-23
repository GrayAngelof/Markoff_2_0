## Анализ слоя: **data** (слой доступа к данным и кэширования)

### Краткое описание слоя

**Назначение** – управлять хранением, кэшированием, валидностью и связями между сущностями в памяти приложения. Слой `data` предоставляет единый фасад `EntityGraph` для работы с графом объектов и репозитории для типобезопасного доступа к данным. Этот слой **не знает**, откуда приходят данные (API, БД, файлы) – он только хранит и организует их.

**Что делает:**
- Хранит DTO объекты в потокобезопасном индексе (`EntityStore`)
- Поддерживает иерархические связи "родитель-потомок" (`RelationIndex`)
- Отслеживает валидность данных для оптимизации запросов (`ValidityIndex`)
- Управляет состоянием загрузки детей (`LoadStateIndex`) для предотвращения гонок
- Предоставляет репозитории с CRUD-операциями для каждого типа сущностей
- Обеспечивает полную потокобезопасность через RLock

**Что не должен делать:**
- Содержать бизнес-логику (фильтрацию, сортировку, вычисления)
- Выполнять сетевые запросы или обращаться к API
- Импортировать что-либо из `services`, `projections`, `controllers`, `ui`
- Содержать UI-специфичный код
- Знать о том, откуда пришли данные (кэш или свежая загрузка)

---

### Файловая структура слоя

```
client/src/data/
├── __init__.py                    # Публичное API (EntityGraph, репозитории)
├── entity_graph.py                # Фасад графа (координатор всех компонентов)
├── graph/                         # Внутренние компоненты графа (приватный пакет)
│   ├── __init__.py                # Маркер приватности
│   ├── consistency.py             # ConsistencyChecker (валидация целостности)
│   ├── load_state.py              # LoadStateIndex (состояние загрузки детей)
│   ├── locked.py                  # LockedComponent (базовый класс с RLock)
│   ├── relations.py               # RelationIndex (индекс связей)
│   ├── schema.py                  # Схема графа (маппинг типов и полей)
│   ├── store.py                   # EntityStore (хранилище объектов)
│   └── validity.py                # ValidityIndex (индекс валидности)
├── repositories/                  # Репозитории для доступа к данным
│   ├── __init__.py                # Публичный экспорт репозиториев
│   ├── base.py                    # BaseRepository (базовая реализация)
│   ├── complex.py                 # ComplexRepository
│   ├── building.py                # BuildingRepository
│   ├── floor.py                   # FloorRepository
│   └── room.py                    # RoomRepository
└── utils/                         # Утилиты data слоя
    └── decorators.py              # validate_ids (декоратор валидации ID)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `EntityGraph` | `entity_graph.py` | **Фасад** – главный координатор. Объединяет store, relations, validity, load_state. Предоставляет единое API для всех операций с графом. |
| `EntityStore` | `graph/store.py` | Потокобезопасное хранилище объектов. Только `put`, `get`, `remove`, `has`. Не знает о связях. |
| `RelationIndex` | `graph/relations.py` | Индекс связей "родитель-потомок". Прямые и обратные индексы для O(1) навигации. Потокобезопасен. |
| `ValidityIndex` | `graph/validity.py` | Индекс валидности данных. Отслеживает, какие сущности актуальны. Генерирует `DataInvalidated` события. Поддерживает веточную инвалидацию. |
| `LoadStateIndex` | `graph/load_state.py` | Состояние загрузки детей (`NOT_LOADED`, `LOADING`, `LOADED`). Предотвращает гонки при параллельных запросах. |
| `ConsistencyChecker` | `graph/consistency.py` | Проверка целостности графа (TODO: частично реализован). |
| `LockedComponent` | `graph/locked.py` | Базовый класс с RLock для потокобезопасных компонентов. |
| `BaseRepository` | `repositories/base.py` | Базовый репозиторий, реализующий `core.Repository`. Обеспечивает CRUD + навигацию. |
| `ComplexRepository` | `repositories/complex.py` | Репозиторий для комплексов. Добавляет `get_building_ids()`, `get_tree()`, `get_detail()`. |
| `BuildingRepository` | `repositories/building.py` | Репозиторий для корпусов. Добавляет `get_floor_ids()`, `get_by_complex()`. |
| `FloorRepository` | `repositories/floor.py` | Репозиторий для этажей. Добавляет `get_room_ids()`, `get_by_building()`. |
| `RoomRepository` | `repositories/room.py` | Репозиторий для помещений. Добавляет `get_by_floor()`. |

---

### Внутренние импорты (только между модулями data)

**Из `entity_graph.py`:**
- `from src.data.graph.consistency import ConsistencyChecker`
- `from src.data.graph.load_state import LoadState, LoadStateIndex`
- `from src.data.graph.relations import RelationIndex, RelationStats`
- `from src.data.graph.schema import get_node_type, get_parent_id`
- `from src.data.graph.store import EntityStore, StoreStats`
- `from src.data.graph.validity import ValidityIndex, ValidityStats`
- `from src.shared.comparison import has_changed`
- `from src.shared.validation import validate_positive_int`

**Из `graph/relations.py`:**
- `from src.data.graph.schema import get_child_type, get_parent_type`
- `from src.shared.validation import validate_positive_int`

**Из `graph/validity.py`:**
- `from src.core import EventBus`
- `from src.core.events.definitions import DataInvalidated`
- `from src.core.rules.hierarchy import get_child_type`
- `from src.shared.validation import validate_positive_int`

**Из `graph/schema.py`:**
- `from src.core.rules.hierarchy import get_child_type, get_parent_type`
- `from src.core.types.protocols import HasNodeType`

**Из `repositories/base.py`:**
- `from src.core import NodeType, NotFoundError`
- `from src.core.ports.repository import Repository as CoreRepository`
- `from src.data.entity_graph import EntityGraph`

**Из `repositories/complex.py` (и аналогичных):**
- `from src.core import NodeType`
- `from src.models import ComplexTreeDTO, ComplexDetailDTO`
- `from src.data.repositories.base import BaseRepository`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вся публичная поверхность слоя `data` доступна через импорт из `src.data`:

**Фасад графа:**
- `EntityGraph(event_bus: EventBus)` – основной координатор
  - **CRUD:** `add_or_update(entity) -> bool`, `add_or_update_bulk(entities) -> Dict`, `get(node_type, id)`, `get_all(node_type)`, `remove(node_type, id, cascade=False)`
  - **Навигация:** `get_children(parent_type, parent_id) -> List[int]`, `get_parent(child_type, child_id) -> Optional[NodeIdentifier]`, `get_ancestors(node_type, node_id) -> List[NodeIdentifier]`
  - **Валидность:** `is_valid()`, `validate()`, `invalidate()`, `invalidate_branch()`, `validate_bulk()`, `invalidate_bulk()`
  - **Состояние загрузки:** `is_children_loaded()`, `mark_children_loading() -> bool`, `mark_children_loaded()`, `mark_children_load_failed()`
  - **Статистика:** `get_stats() -> EntityGraphStats`, `print_stats()`, `check_consistency()`
  - **Специальные:** `get_if_full()`, `get_cached_children()`, `clear()`

**Репозитории (все наследуют `BaseRepository`):**
- `BaseRepository[T]` – абстрактный базовый репозиторий
  - `get(id: int) -> T` (кидает `NotFoundError`)
  - `get_all() -> List[T]`
  - `get_ids() -> List[int]`
  - `exists(id: int) -> bool`
  - `add(entity: T) -> None`
  - `remove(id: int) -> bool`
  - `is_valid(id: int) -> bool`
  - `invalidate(id: int) -> bool`

- `ComplexRepository(graph: EntityGraph)`
  - Все методы `BaseRepository[ComplexDTO]`
  - `get_building_ids(complex_id: int) -> List[int]` – навигация
  - `get_tree(complex_id: int) -> Optional[ComplexTreeDTO]`
  - `get_detail(complex_id: int) -> Optional[ComplexDetailDTO]`
  - `has_detail(complex_id: int) -> bool`

- `BuildingRepository(graph: EntityGraph)`
  - `get_floor_ids(building_id: int) -> List[int]`
  - `get_by_complex(complex_id: int) -> List[int]`
  - `get_tree()`, `get_detail()`, `has_detail()`

- `FloorRepository(graph: EntityGraph)`
  - `get_room_ids(floor_id: int) -> List[int]`
  - `get_by_building(building_id: int) -> List[int]`
  - `get_tree()`, `get_detail()`, `has_detail()`

- `RoomRepository(graph: EntityGraph)`
  - `get_by_floor(floor_id: int) -> List[int]`
  - `get_tree()`, `get_detail()`, `has_detail()`

**Типы:**
- `EntityGraphStats` – TypedDict со статистикой (store, relations, validity, load_state)

---

### Итоговое заключение: принципы работы со слоем `data`

1. **Импорт только сверху вниз** – вышестоящие слои (`services`, `projections`, `controllers`, `ui`) могут импортировать из `data` свободно. Слой `data` может импортировать:
   - `core` – для типов, событий, правил иерархии
   - `models` – для DTO (сущности, которые хранит)
   - `shared` – для утилит (`has_changed`, `validate_positive_int`)

2. **Запрещены обратные импорты** – код внутри `data` не должен импортировать ничего из `services`, `projections`, `controllers`, `ui`.

3. **Используйте репозитории для доступа к данным** – они предоставляют типобезопасное API и скрывают внутреннее устройство графа:
   ```python
   from src.data import EntityGraph, ComplexRepository
   
   graph = EntityGraph(event_bus)
   repo = ComplexRepository(graph)
   complex = repo.get(42)  # вернёт ComplexDTO или NotFoundError
   ```

4. **EntityGraph – низкоуровневый фасад** – используйте его только когда репозиторий не покрывает нужную операцию (например, пакетная валидация или статистика).

5. **Работа с валидностью** – это ключевая оптимизация:
   - Данные считаются валидными, если они загружены из API и не устарели
   - `invalidate_branch()` инвалидирует всю ветку (комплекс → корпуса → этажи → комнаты)
   - При инвалидации генерируется `DataInvalidated` событие через `EventBus`
   - Проверяйте `is_valid()` перед использованием данных, особенно в UI

6. **Состояние загрузки детей** – защита от гонок:
   - `mark_children_loading()` возвращает `False`, если загрузка уже идёт или завершена
   - Используйте это в сервисах перед выполнением API-запроса
   - Всегда вызывайте `mark_children_loaded()` или `mark_children_load_failed()` после завершения

7. **Навигация через ID, а не объекты** – методы типа `get_building_ids()` возвращают ID, а не DTO. Это позволяет:
   - Лениво загружать детей только при необходимости
   - Избегать циклических зависимостей
   - Упрощать проверку наличия данных

8. **Каскадное удаление** – `remove(cascade=True)` удаляет всех потомков рекурсивно. Используйте осторожно, только когда нужно полностью очистить ветку.

9. **Потокобезопасность** – все операции в `EntityGraph` блокируются через `RLock`. Можно безопасно вызывать методы из разных потоков (например, при загрузке данных в фоне).

10. **Bulk-операции** – для производительности используйте `add_or_update_bulk()` и `validate_bulk()`/`invalidate_bulk()` при работе с большими списками.

11. **Статистика и диагностика** – `print_stats()` и `check_consistency()` помогают отлаживать состояние кэша и выявлять проблемы с целостностью.

12. **Приватные пакеты** – никогда не импортируйте напрямую из `src.data.graph.*` или `src.data.utils.*`. Всё публичное API доступно через `src.data`.

Слой `data` является **единственным местом хранения данных в памяти приложения**. Все вышестоящие слои получают данные только через репозитории или `EntityGraph`. Это обеспечивает консистентность, кэширование и потокобезопасность без дублирования логики хранения.