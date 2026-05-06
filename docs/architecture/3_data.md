## Анализ слоя «data»

### Краткое описание слоя

Слой **data** отвечает за **хранение, кэширование, навигацию и валидацию данных** в памяти клиентского приложения. Он предоставляет:

- **Графовое хранилище** (`EntityGraph`) — фасад над индексами хранения (`EntityStore`), связей (`RelationIndex`), валидности (`ValidityIndex`) и состояния загрузки (`LoadStateIndex`).  
- **Репозитории** (`ComplexRepository`, `BuildingRepository`, `FloorRepository`, `RoomRepository`) — высокоуровневый CRUD + навигация по дереву (получение ID детей/родителей).  
- **Справочники** (`ReferenceStore`) — фасад для read-only реестров статусов и типов.

Слой **не содержит бизнес-логики** (фильтрация, преобразования в ViewModel, принятие решений). Только работа с памятью: положить, получить, удалить, проверить валидность, найти детей/родителя.

**Что слой НЕ должен делать:**
- Обращаться к API (загрузка данных — дело `services` или выше).
- Содержать UI-логику.
- Импортировать слои `services`, `projections`, `controllers`, `view models`, `ui`.
- Принимать решения о том, когда обновлять данные (только по команде сверху).

---

### Файловая структура слоя

```
src/data/
├── __init__.py                    # публичный API (EntityGraph, ReferenceStore, репозитории)
├── entity_graph.py                # фасад EntityGraph + EntityGraphStats
├── reference_store.py             # фасад ReferenceStore (справочники)
│
├── graph/                         # ПРИВАТНО: внутренности EntityGraph
│   ├── __init__.py
│   ├── store.py                   # EntityStore — хранение объектов по типам
│   ├── relations.py               # RelationIndex — связи родитель-потомок
│   ├── validity.py                # ValidityIndex — валидность данных (с событиями DataInvalidated)
│   ├── load_state.py              # LoadStateIndex — состояние загрузки детей (NOT_LOADED/LOADING/LOADED)
│   ├── consistency.py             # ConsistencyChecker — проверка консистентности графа
│   ├── schema.py                  # PARENT_ID_FIELD, get_node_type, get_parent_id, обёртки hierarchy
│   ├── locked.py                  # LockedComponent (базовый с RLock)
│   └── decorators.py              # validate_ids (декоратор для валидации ID)
│
├── reference/                     # ПРИВАТНО: реестры справочников
│   ├── __init__.py
│   ├── base.py                    # BaseRegistry[T] (абстрактный)
│   ├── building_status_registry.py
│   ├── room_status_registry.py
│   ├── contract_status_registry.py
│   ├── equipment_status_registry.py
│   ├── payment_status_registry.py
│   ├── placement_status_registry.py
│   └── counterparty_type_registry.py
│
└── repositories/                  # ПУБЛИЧНЫЕ репозитории (высокоуровневый доступ)
    ├── __init__.py                # экспорт ComplexRepository, BuildingRepository, FloorRepository, RoomRepository
    ├── base.py                    # BaseRepository[T] (реализует core.Repository)
    ├── complex.py                 # ComplexRepository
    ├── building.py                # BuildingRepository
    ├── floor.py                   # FloorRepository
    └── room.py                    # RoomRepository
```

---

### Описание внутренних классов (приватные / не для внешнего использования)

| Класс / Модуль | Назначение |
|----------------|-------------|
| `EntityStore` (`graph/store.py`) | Потокобезопасное хранилище объектов по типу (`NodeType` → `dict[id, Any]`). Только put/get/remove/has, без логики связей. |
| `RelationIndex` (`graph/relations.py`) | Индекс связей родитель-потомок (прямой и обратный). `link`, `unlink`, `get_children`, `get_parent`, `remove_node`. Проверяет допустимость связи по правилам `core.rules.hierarchy`. |
| `ValidityIndex` (`graph/validity.py`) | Индекс валидности данных (актуальны / устарели). При инвалидации генерирует `DataInvalidated`. Поддерживает точечную, bulk и рекурсивную (BFS) инвалидацию ветки. |
| `LoadStateIndex` (`graph/load_state.py`) | Отслеживает состояние загрузки детей: `NOT_LOADED`, `LOADING`, `LOADED`. Предотвращает гонки при параллельных запросах. |
| `ConsistencyChecker` (`graph/consistency.py`) | Диагностический инструмент для проверки целостности графа (связи, валидность). (Часть методов отмечена как TODO). |
| `LockedComponent` (`graph/locked.py`) | Базовый класс с `RLock` для потокобезопасных компонентов графа. |
| `BaseRegistry[T]` (`reference/base.py`) | Абстрактный реестр для read-only справочников. Содержит `loader`, словарь `{id: DTO}`, метод `warmup()`, `get()`, `is_ready()`. |
| `BuildingStatusRegistry`, `RoomStatusRegistry`, … (в `reference/`) | Конкретные реестры для каждого справочника. Переопределяют только `_log_result()`. |
| `BaseRepository[T]` (`repositories/base.py`) | Базовый класс репозиториев. Реализует `core.Repository` (get, get_all, add, remove, …). Добавляет `exists`, `is_valid`, `invalidate`. Работает через `EntityGraph`. |
| `_validate_ids` и `validate_ids` декоратор (`graph/decorators.py`) | Внутренний декоратор для валидации ID (положительные целые). |

---

### Список импортов (внутренние зависимости слоя data)

**Импорты из `core`**:
- `from src.core.event_bus import EventBus`
- `from src.core.events.definitions import DataInvalidated`
- `from src.core.rules.hierarchy import get_child_type, get_parent_type`
- `from src.core.types import NodeType, NodeIdentifier, NotFoundError`
- `from src.core.types.protocols import HasNodeType`
- `from src.core.ports.repository import Repository`

**Импорты из `models`**:
- `from src.models import BuildingStatusDTO, RoomStatusDTO, …` (все DTO)
- В репозиториях: `from src.models import ComplexTreeDTO, ComplexDetailDTO, …`

**Импорты из `shared` и `utils`**:
- `from src.shared.validation import validate_positive_int`
- `from src.shared.comparison import has_changed`
- `from utils.logger import get_logger`

**Внутри data**:
- `from .graph.store import EntityStore`
- `from .graph.relations import RelationIndex`
- `from .graph.validity import ValidityIndex`
- `from .graph.load_state import LoadStateIndex`
- `from .graph.consistency import ConsistencyChecker`
- `from .graph.schema import get_node_type, get_parent_id`
- `from .reference.building_status_registry import BuildingStatusRegistry` (и аналоги)
- `from .repositories.base import BaseRepository`
- `from .entity_graph import EntityGraph` (в репозиториях)

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящие слои (`services`, `projections`, `controllers`, `view models`, `ui`) **импортируют из `src.data`**:

#### 1. `EntityGraph` (фасад графа) — из `src.data`

| Метод | Назначение |
|-------|-------------|
| `__init__(event_bus: EventBus)` | Создать граф, связанный с шиной событий. |
| `add_or_update(entity: Any) -> bool` | Добавить/обновить DTO, вернуть `True` если были изменения. |
| `add_or_update_bulk(entities: List[Any]) -> Dict` | Массовое добавление/обновление со статистикой. |
| `get(node_type, entity_id) -> Optional[Any]` | Получить DTO. |
| `get_all(node_type) -> List[Any]` | Все DTO типа. |
| `get_all_ids(node_type) -> List[int]` | Все ID типа. |
| `has_entity(node_type, entity_id) -> bool` | Проверить существование. |
| `remove(node_type, entity_id, cascade=False) -> bool` | Удалить; если `cascade=True` → удалить всех потомков. |
| `get_children(parent_type, parent_id) -> List[int]` | Вернуть ID детей. |
| `get_parent(child_type, child_id) -> Optional[NodeIdentifier]` | Вернуть родителя. |
| `get_ancestors(node_type, node_id) -> List[NodeIdentifier]` | Все предки (от ближайшего к дальнему). |
| `is_valid(node_type, entity_id) -> bool` | Данные актуальны? |
| `validate(node_type, entity_id)` | Пометить как валидные. |
| `validate_bulk(node_type, ids) -> int` | Пометить множество валидными. |
| `invalidate(node_type, entity_id) -> bool` | Пометить невалидными. |
| `invalidate_bulk(node_type, ids) -> int` | Массовая инвалидация. |
| `invalidate_branch(node_type, entity_id) -> int` | Инвалидировать всю ветку (включая потомков). |
| `is_children_loaded(node_type, node_id) -> bool` | Загружены ли дети? |
| `mark_children_loading(...) -> bool` | Начать загрузку детей (вернёт `False` если уже загружается/загружено). |
| `mark_children_loaded(...)` | Отметить, что дети загружены. |
| `mark_children_load_failed(...)` | Сбросить состояние при ошибке. |
| `reset_children_state(...)` | Принудительно сбросить. |
| `get_timestamp(node_type, entity_id) -> Optional[datetime]` | Время последнего обновления. |
| `get_stats() -> EntityGraphStats` | Статистика (store, relations, validity, load_state). |
| `print_stats()` | Вывод статистики в лог. |
| `check_consistency() -> Dict` | Проверить целостность графа. |
| `clear()` | Полностью очистить граф. |

#### 2. Репозитории (высокоуровневый доступ) — из `src.data`

Все репозитории реализуют `core.Repository` и добавляют навигационные методы.

**`ComplexRepository`**  
- `get_building_ids(complex_id) -> List[int]` — ID корпусов комплекса.  
- `get_tree(complex_id) -> Optional[ComplexTreeDTO]`  
- `get_detail(complex_id) -> Optional[ComplexDetailDTO]`  
- `has_detail(complex_id) -> bool`

**`BuildingRepository`**  
- `get_floor_ids(building_id) -> List[int]`  
- `get_by_complex(complex_id) -> List[int]` (ID корпусов)  
- аналоги `get_tree`, `get_detail`, `has_detail`

**`FloorRepository`**  
- `get_room_ids(floor_id) -> List[int]`  
- `get_by_building(building_id) -> List[int]`  
- `get_tree`, `get_detail`, `has_detail`

**`RoomRepository`**  
- `get_by_floor(floor_id) -> List[int]`  
- `get_tree`, `get_detail`, `has_detail`

Общие методы `BaseRepository` (доступны во всех репозиториях):  
`get(id) -> T` (или `NotFoundError`), `get_all() -> List[T]`, `get_ids() -> List[int]`, `exists(id) -> bool`, `add(entity)`, `remove(id) -> bool`, `is_valid(id) -> bool`, `invalidate(id) -> bool`.

#### 3. `ReferenceStore` (справочники) — из `src.data`

| Метод / свойство | Назначение |
|------------------|-------------|
| `warmup()` | Загрузить все справочники (вызывается один раз при старте). |
| `is_ready() -> bool` | Все ли загружены? |
| `.building_statuses` → `BuildingStatusRegistry` | Доступ к статусам зданий. |
| `.room_statuses` → `RoomStatusRegistry` | Статусы помещений. |
| `.contract_statuses` → `ContractStatusRegistry` | Статусы договоров. |
| `.equipment_statuses` → `EquipmentStatusRegistry` | Статусы оборудования. |
| `.payment_statuses` → `PaymentStatusRegistry` | Статусы платежей. |
| `.placement_statuses` → `PlacementStatusRegistry` | Статусы размещения. |
| `.counterparty_types` → `CounterpartyTypeRegistry` | Типы контрагентов. |

Каждый реестр имеет методы:  
- `get(id: Optional[int]) -> Optional[T]`  
- `is_ready() -> bool`  

**Примечание:** Реестры не предоставляют доступ к `name` напрямую — маппинг ID → человекочитаемое значение делается в слое `projections`.

#### 4. Типы статистики

`EntityGraphStats` (TypedDict) — для диагностики.

---

### Итоговое заключение

**Принципы работы со слоем `data`:**

1. **Импорт только из `src.data`** — используйте `EntityGraph`, репозитории, `ReferenceStore`. Никогда не импортируйте из `data.graph`, `data.reference` напрямую.

2. **Все операции с данными идут через фасады**:
   - `EntityGraph` — низкоуровневый контроль над хранилищем, связями, валидностью.
   - Репозитории — удобный CRUD + навигация для физической иерархии.
   - `ReferenceStore` — только для чтения справочников.

3. **Потокобезопасность** — все публичные методы `EntityGraph` и реестров используют `RLock`. Не нужно дополнительной синхронизации из вызывающего кода.

4. **Инвалидация данных** — при изменении данных на сервере следует вызывать `invalidate` или `invalidate_branch`, чтобы пометить устаревшие сущности. При следующем обращении вышестоящий слой (`services`) перезагрузит их.

5. **Состояние загрузки детей** — используется для предотвращения повторных запросов к API. Перед загрузкой детей узла проверяйте `is_children_loaded` и вызывайте `mark_children_loading` (если вернула `True` — начинайте загрузку).

6. **Репозитории не содержат бизнес-фильтрации** (например, «только корпуса с владельцем X») — это задача слоя `services`.

7. **Справочники загружаются один раз** через `ReferenceStore.warmup()` на старте приложения. После этого `is_ready()` должно быть `True` перед использованием.

8. **Тестирование** — можно создавать `EntityGraph` с мок-данными, не поднимая API. Все зависимости через `EventBus` (можно передать заглушку).

Слой `data` является **единственным источником кэшированных данных** в приложении. Любые изменения состояния данных (добавление, удаление, инвалидация) должны проходить через этот слой.