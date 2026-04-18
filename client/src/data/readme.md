## Анализ слоя: **data** (слой работы с данными и графом сущностей)

### Краткое описание слоя

**Назначение** – управлять хранением, кэшированием, навигацией и валидностью сущностей в памяти клиента. Слой `data` предоставляет **единый фасад `EntityGraph`** для доступа к данным и набор **репозиториев**, реализующих контракт `core.Repository`.

**Что делает:**
- Хранит DTO-модели (`models`) в потокобезопасном кэше (`EntityStore`)
- Поддерживает индексы связей "родитель-потомок" для O(1)-навигации (`RelationIndex`)
- Отслеживает валидность данных (актуальность) и генерирует события `DataInvalidated` (`ValidityIndex`)
- Управляет состоянием загрузки дочерних элементов (`LoadStateIndex`) для предотвращения повторных запросов
- Предоставляет CRUD-операции, пакетное обновление, каскадное удаление
- Реализует репозитории (навигационные методы: `get_building_ids()`, `get_floor_ids()` и т.д.)

**Что не должен делать:**
- Содержать бизнес-логику (фильтрацию, сортировку, агрегацию, расчёты) – это в `services`
- Взаимодействовать с API, БД, файловой системой напрямую – только через вышестоящие сервисы
- Импортировать что-либо из `services`, `projections`, `controllers`, `ui`
- Содержать UI-специфичный код (форматирование, представление)

**Зависимости:** от `core` (типы, события, правила иерархии, `EventBus`, `Repository` protocol), от `models` (все DTO), от `shared` (валидация, сравнение), от `utils.logger`.

---

### Файловая структура слоя

```
client/src/data/
├── __init__.py                    # (возможно) публичный экспорт фасада и репозиториев
├── entity_graph.py                # Фасад EntityGraph (главный координатор)
├── graph/                         # Внутренние компоненты графа (приватные)
│   ├── __init__.py                # маркер приватности
│   ├── store.py                   # EntityStore – хранилище объектов по типам/ID
│   ├── relations.py               # RelationIndex – индексы связей родитель-потомок
│   ├── validity.py                # ValidityIndex – отслеживание валидности, генерация DataInvalidated
│   ├── load_state.py              # LoadStateIndex – состояния загрузки (NOT_LOADED/LOADING/LOADED)
│   ├── consistency.py             # ConsistencyChecker – проверка целостности индексов
│   ├── schema.py                  # Схема графа: PARENT_ID_FIELD, get_node_type, get_parent_id
│   ├── locked.py                  # LockedComponent – базовый класс с RLock
│   └── decorators.py              # validate_ids – декоратор валидации ID
├── repositories/                  # Репозитории (публичное API для доступа к данным)
│   ├── __init__.py                # экспорт всех репозиториев
│   ├── base.py                    # BaseRepository (реализация core.Repository)
│   ├── complex.py                 # ComplexRepository
│   ├── building.py                # BuildingRepository
│   ├── floor.py                   # FloorRepository
│   ├── room.py                    # RoomRepository
│   ├── counterparty.py            # CounterpartyRepository
│   └── responsible_person.py      # ResponsiblePersonRepository
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `EntityGraph` | `entity_graph.py` | **Фасад** – координатор всех внутренних компонентов. Предоставляет единое API для CRUD, навигации, валидации, состояния загрузки. Потокобезопасен. |
| `EntityStore` | `graph/store.py` | Хранилище сущностей в памяти: `{тип: {id: объект}}` + временные метки. Только put/get/remove, без логики связей. |
| `RelationIndex` | `graph/relations.py` | Индексы связей: прямые (родитель → дети) и обратные (ребёнок → родитель). O(1)-доступ, потокобезопасен. |
| `ValidityIndex` | `graph/validity.py` | Отслеживает, какие сущности актуальны. При инвалидации генерирует `DataInvalidated` через `EventBus`. Поддерживает точечную, bulk и веточную инвалидацию. |
| `LoadStateIndex` | `graph/load_state.py` | Состояния загрузки детей: `NOT_LOADED`, `LOADING`, `LOADED`. Предотвращает гонки при параллельных запросах. |
| `ConsistencyChecker` | `graph/consistency.py` | Диагностический инструмент: проверяет целостность индексов (в коде частично заглушен). |
| `LockedComponent` | `graph/locked.py` | Базовый класс с `RLock` для потокобезопасных компонентов. |
| `BaseRepository` | `repositories/base.py` | Абстрактный репозиторий, реализующий `core.Repository`. Содержит CRUD и методы `exists()`, `is_valid()`, `invalidate()`. |
| `ComplexRepository`, `BuildingRepository`, … | `repositories/*.py` | Конкретные репозитории. Добавляют навигационные методы: `get_building_ids()`, `get_floor_ids()`, `get_room_ids()`, `get_by_complex()`, `get_by_building()`, `get_by_floor()`, `get_person_ids()`, `get_by_counterparty()`. |

---

### Внутренние импорты (только между модулями data, core, models, shared, utils)

**Из `core` (везде):**
- `NodeType`, `NodeIdentifier`, `EventBus`, `DataInvalidated`, `NotFoundError`
- `get_child_type`, `get_parent_type` (из `core.rules.hierarchy`)
- `Repository` (protocol из `core.ports.repository`)

**Из `models` (в репозиториях и `schema.py`):**
- `Complex`, `Building`, `Floor`, `Room`, `Counterparty`, `ResponsiblePerson`

**Из `shared` (утилиты):**
- `validate_positive_int` (из `shared.validation`)
- `has_changed` (из `shared.comparison`)

**Из `utils.logger`** – везде.

**Между внутренними модулями `graph`:**
- `store.py` → импортирует только `NodeType`, `validate_positive_int`
- `relations.py` → импортирует `NodeType`, `get_child_type`, `get_parent_type` (из `graph.schema`), `validate_positive_int`
- `validity.py` → импортирует `EventBus`, `DataInvalidated`, `get_child_type`, `NodeType`, `validate_positive_int`
- `load_state.py` → импортирует `NodeType`
- `schema.py` → импортирует `get_child_type`, `get_parent_type` (из `core.rules.hierarchy`), `NodeType`, `HasNodeType` (protocol)
- `entity_graph.py` → импортирует все внутренние компоненты (`store`, `relations`, `validity`, `load_state`, `consistency`, `schema`, `decorators`)

**Импортов из `services`, `projections`, `controllers`, `ui` нет.**

---

### Экспортируемые методы / классы для вышестоящих слоёв

Публичное API слоя `data` доступно через:
- `from src.data.entity_graph import EntityGraph`
- `from src.data.repositories import ComplexRepository, BuildingRepository, ...`, `BaseRepository`

**Фасад `EntityGraph` (основной):**

CRUD:
- `add_or_update(entity) -> bool`
- `add_or_update_bulk(entities) -> dict`
- `get(node_type, entity_id) -> Optional[Any]`
- `get_all(node_type) -> List[Any]`
- `get_all_ids(node_type) -> List[int]`
- `has_entity(node_type, entity_id) -> bool`
- `remove(node_type, entity_id, cascade=False) -> bool`

Навигация:
- `get_children(parent_type, parent_id) -> List[int]`
- `get_parent(child_type, child_id) -> Optional[NodeIdentifier]`
- `get_ancestors(node_type, node_id) -> List[NodeIdentifier]`

Валидность:
- `is_valid(node_type, entity_id) -> bool`
- `validate(node_type, entity_id)`
- `validate_bulk(node_type, ids) -> int`
- `invalidate(node_type, entity_id) -> bool`
- `invalidate_bulk(node_type, ids) -> int`
- `invalidate_branch(node_type, entity_id) -> int`

Состояние загрузки:
- `is_children_loaded(node_type, node_id) -> bool`
- `mark_children_loading(node_type, node_id) -> bool`
- `mark_children_loaded(node_type, node_id)`
- `mark_children_load_failed(node_type, node_id)`
- `reset_children_state(node_type, node_id)`

Вспомогательные:
- `get_timestamp(node_type, entity_id) -> Optional[datetime]`
- `get_stats() -> EntityGraphStats`
- `print_stats()`
- `check_consistency() -> dict`
- `clear()`

**Репозитории (каждый для своего типа):**

Наследуют от `BaseRepository`, реализуют:
- `get(id) -> T` (кидает `NotFoundError`)
- `get_all() -> List[T]`
- `get_ids() -> List[int]`
- `exists(id) -> bool`
- `add(entity)`
- `remove(id) -> bool`
- `is_valid(id) -> bool`
- `invalidate(id) -> bool`

Специфические навигационные методы (возвращают **ID**, а не объекты):
- `ComplexRepository.get_building_ids(complex_id) -> List[int]`
- `BuildingRepository.get_floor_ids(building_id) -> List[int]` и `get_by_complex(complex_id)`
- `FloorRepository.get_room_ids(floor_id)` и `get_by_building(building_id)`
- `RoomRepository.get_by_floor(floor_id)`
- `CounterpartyRepository.get_person_ids(counterparty_id)`
- `ResponsiblePersonRepository.get_by_counterparty(counterparty_id)`

---

### Итоговое заключение: принципы работы со слоем `data`

1. **Зависимость только от `core` и `models`** – слой `data` не знает о `services`, `projections`, `controllers`, `ui`. Это строгое правило: репозитории и граф не вызывают бизнес-логику.

2. **Используйте фасад `EntityGraph` для низкоуровневых операций** – он координирует все внутренние индексы. В сервисах предпочтительнее работать через репозитории, но прямой доступ к графу допустим при необходимости.

3. **Репозитории – основной интерфейс для вышестоящих слоёв** – они реализуют контракт `core.Repository` и добавляют навигацию по графу (методы, возвращающие ID). Никогда не добавляйте в репозитории бизнес-фильтрацию (например, `get_active_complexes`). Это должно быть в `services`.

4. **Все операции потокобезопасны** – внутренние компоненты используют `RLock`. Можно вызывать из любых потоков.

5. **Работа с валидностью** – после успешной загрузки данных из API вызывайте `graph.validate(type, id)`. При изменении данных на сервере вызывайте `graph.invalidate(type, id)` или `invalidate_branch`. Слой `data` сам сгенерирует событие `DataInvalidated` в шину.

6. **Состояние загрузки детей** – перед асинхронной загрузкой детей проверьте `is_children_loaded()`, затем `mark_children_loading()` (если вернёт `True` – начинайте загрузку). После успеха – `mark_children_loaded()`, при ошибке – `mark_children_load_failed()`. Это предотвращает дублирующиеся запросы.

7. **Никогда не мутируйте объекты напрямую** – все DTO иммутабельны. Обновление происходит через `add_or_update` (сравнивает `has_changed` и обновляет только при реальных изменениях).

8. **Пакетные операции** – для массовой загрузки используйте `add_or_update_bulk` – он эффективнее и выдаёт подробную статистику.

9. **Диагностика** – периодически вызывайте `check_consistency()` в тестах или при подозрении на рассинхрон. `print_stats()` полезен для отладки кэша.

Слой `data` является **единственным источником кэшированных данных в памяти** и обеспечивает слабую связанность между API-загрузчиками (сервисами) и UI-проекциями. Он не содержит бизнес-правил, только техническое управление данными.