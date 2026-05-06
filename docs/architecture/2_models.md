## Анализ слоя «models»

### Краткое описание слоя

Слой **models** — это набор **иммутабельных DTO** (Data Transfer Objects), которые описывают структуру данных, получаемых от API бэкенда. Основное назначение:

- **Типизированное представление** ответов API (иерархия объектов, справочники, сущности).
- **Разделение на подкатегории**: физическая структура (`structure`), справочники (`reference`), бизнес-сущности (`entity`).
- **Единый контракт** для слоёв `data`, `services`, `projections`, `controllers`, `view models` и `ui` — везде используются одни и те же DTO.
- **Парсинг примитивов** (даты из ISO, преобразование типов) в методах `from_dict`.

**Что слой НЕ должен делать:**
- Не содержит бизнес-логику (расчёты, валидацию, преобразования, зависящие от контекста).
- Не имеет зависимостей от внешних API (кроме типов `core`).
- Не управляет состоянием приложения (кэши, хранение и т.д.).
- Не содержит логику UI (форматирование, локализация).

---

### Файловая структура слоя

```
src/models/
├── __init__.py                 # экспорт всех DTO (structure, reference, entity)
├── base.py                     # BaseDTO (базовый DTO с ключом и идентификатором)
├── mixins.py                   # DateTimeMixin (парсинг дат)
│
├── structure/                  # физическая иерархия объектов
│   ├── __init__.py             # экспорт DTO структуры
│   ├── complex.py              # ComplexTreeDTO, ComplexDetailDTO
│   ├── building.py             # BuildingTreeDTO, BuildingDetailDTO
│   ├── floor.py                # FloorTreeDTO, FloorDetailDTO
│   └── room.py                 # RoomTreeDTO, RoomDetailDTO
│
├── reference/                  # справочники (reference data)
│   ├── __init__.py             # экспорт справочников
│   ├── base.py                 # ReferenceBaseDTO (базовый для справочников)
│   ├── building_status.py      # BuildingStatusDTO
│   ├── room_status.py          # RoomStatusDTO
│   ├── contract_status.py      # ContractStatusDTO
│   ├── equipment_status.py     # EquipmentStatusDTO
│   ├── payment_status.py       # PaymentStatusDTO
│   ├── placement_status.py     # PlacementStatusDTO
│   └── counterparty_type.py    # CounterpartyTypeDTO
│
└── entity/                     # бизнес-сущности (reference entity)
    ├── __init__.py             # экспорт сущностей
    ├── base.py                 # EntityBaseDTO (базовый для сущностей)
    ├── counterparty.py         # CounterpartyDTO
    └── responsible_person.py   # ResponsiblePersonDTO
```

---

### Описание всех внутренних классов

> Все DTO являются `@dataclass(frozen=True, kw_only=True)`, иммутабельны.  
> Для каждого DTO определены `NODE_TYPE` (для structure) или `REFERENCE_TYPE` (для reference) / `ENTITY_TYPE` (для entity).  
> Метод `from_dict` преобразует словарь ответа API в DTO.

#### Базовые классы (приватные, не экспортируются напрямую)

| Класс | Назначение |
|-------|-------------|
| `BaseDTO` | Базовый для всех DTO. Содержит `id`, `NODE_TYPE`, `IS_DETAIL`. Предоставляет `key()` (тип, id) и `to_identifier()` (преобразование в `NodeIdentifier`). |
| `DateTimeMixin` | Миксин с полями `created_at`, `updated_at` и методом `parse_datetime()` для парсинга ISO-строк (с поддержкой `Z`). |
| `ReferenceBaseDTO` | Наследует `DateTimeMixin`. Добавляет поля `code`, `name`, `description`, `display_order` и `REFERENCE_TYPE`. Используется для всех справочников. |
| `EntityBaseDTO` | Наследует `DateTimeMixin`. Добавляет поле `id` и `ENTITY_TYPE`. Используется для бизнес-сущностей (контрагенты, ответственные лица). |

#### DTO физической структуры (`structure`)

Все DTO структуры наследуют `BaseDTO`. Для каждого типа узла (`NodeType`) существует два DTO:
- **TreeDTO** — минимальные данные для отображения в дереве (содержит счётчики дочерних элементов).
- **DetailDTO** — полные данные для панели деталей (дополнительные поля, даты создания/обновления).

| Класс | Соответствует узлу | Назначение |
|-------|-------------------|-------------|
| `ComplexTreeDTO` | `COMPLEX` | Имя, количество корпусов. |
| `ComplexDetailDTO` | `COMPLEX` | Имя, описание, адрес, владелец, статус, даты. |
| `BuildingTreeDTO` | `BUILDING` | Имя, `complex_id`, количество этажей. |
| `BuildingDetailDTO` | `BUILDING` | Имя, описание, адрес, владелец, статус, даты. |
| `FloorTreeDTO` | `FLOOR` | Номер этажа, `building_id`, количество помещений. |
| `FloorDetailDTO` | `FLOOR` | Номер, описание, тип, статус, URL плана, даты. |
| `RoomTreeDTO` | `ROOM` | Номер, `floor_id`, площадь. |
| `RoomDetailDTO` | `ROOM` | Номер, площадь, описание, тип, статус, максимальное число арендаторов, даты. |

#### DTO справочников (`reference`)

Наследуют `ReferenceBaseDTO`. Каждый соответствует перечислению `ReferenceDataType`.

| Класс | REFERENCE_TYPE | Дополнительные поля |
|-------|----------------|----------------------|
| `BuildingStatusDTO` | `BUILDING_STATUS` | `is_initial`, `allows_occupancy` |
| `RoomStatusDTO` | `ROOM_STATUS` | `is_initial`, `allows_rent` |
| `ContractStatusDTO` | `CONTRACT_STATUS` | `is_initial`, `is_terminal` |
| `EquipmentStatusDTO` | `EQUIPMENT_STATUS` | `is_initial`, `is_operational` |
| `PaymentStatusDTO` | `PAYMENT_STATUS` | `is_initial`, `is_success` |
| `PlacementStatusDTO` | `PLACEMENT_STATUS` | `is_initial` |
| `CounterpartyTypeDTO` | `COUNTERPARTY_TYPE` | `is_active` |

#### DTO бизнес-сущностей (`entity`)

Наследуют `EntityBaseDTO`. Соответствуют `ReferenceEntityType`.

| Класс | ENTITY_TYPE | Назначение |
|-------|-------------|-------------|
| `CounterpartyDTO` | `COUNTERPARTY` | Контрагент: краткое/полное имя, ИНН, адреса, банковские реквизиты, статус, тип. |
| `ResponsiblePersonDTO` | `RESPONSIBLE_PERSON` | Ответственное лицо: ФИО, должность, отдел, контакты, даты найма/увольнения, активность. |

---

### Список внутренних импортов

Все DTO импортируют друг друга только в пределах слоя `models` и используют типы из `src.core` (разрешённая зависимость сверху вниз). Основные импорты:

**Из `src.core.types`**:
- `NodeType`, `NodeIdentifier` — используются в `BaseDTO` и `to_identifier()`.
- `ReferenceDataType` — в базовом классе справочников.
- `ReferenceEntityType` — в базовом классе сущностей.

**Внутри `models`**:
- `from .base import BaseDTO` — в DTO структуры.
- `from .mixins import DateTimeMixin` — в `base.py`, `ReferenceBaseDTO`, `EntityBaseDTO`.
- `from ..base import BaseDTO` — для иерархических импортов (например, в `structure/complex.py`).
- `from ..mixins import DateTimeMixin` — аналогично.

**Примеры**:
```python
# models/structure/complex.py
from ..base import BaseDTO
from ..mixins import DateTimeMixin
from src.core.types.structure import NodeType
```

```python
# models/reference/base.py
from ..mixins import DateTimeMixin
from src.core.types.reference_data import ReferenceDataType
```

```python
# models/entity/base.py
from ..mixins import DateTimeMixin
from src.core.types.reference_entity import ReferenceEntityType
```

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящие слои (`data`, `services`, `projections`, `controllers`, `view models`, `ui`) **импортируют DTO исключительно из `src.models`** (через главный `__init__.py` или напрямую из подмодулей). Полный список экспортируемых DTO:

#### 1. Физическая структура (`src.models.structure` или `src.models`)

| Класс | Назначение |
|-------|-------------|
| `ComplexTreeDTO` | Дерево: комплекс (минимально) |
| `ComplexDetailDTO` | Детали: комплекс (полная информация) |
| `BuildingTreeDTO` | Дерево: корпус |
| `BuildingDetailDTO` | Детали: корпус |
| `FloorTreeDTO` | Дерево: этаж |
| `FloorDetailDTO` | Детали: этаж |
| `RoomTreeDTO` | Дерево: помещение |
| `RoomDetailDTO` | Детали: помещение |

#### 2. Справочники (`src.models.reference` или `src.models`)

| Класс | Назначение |
|-------|-------------|
| `BuildingStatusDTO` | Статус здания |
| `RoomStatusDTO` | Статус помещения |
| `ContractStatusDTO` | Статус договора |
| `EquipmentStatusDTO` | Статус оборудования |
| `PaymentStatusDTO` | Статус платежа |
| `PlacementStatusDTO` | Статус размещения |
| `CounterpartyTypeDTO` | Тип контрагента |

#### 3. Бизнес-сущности (`src.models.entity` или `src.models`)

| Класс | Назначение |
|-------|-------------|
| `CounterpartyDTO` | Контрагент |
| `ResponsiblePersonDTO` | Ответственное лицо |

#### 4. Базовые классы (редко используются выше, но доступны)

| Класс / Функция | Назначение |
|-----------------|-------------|
| `BaseDTO` | Базовый DTO (содержит `key()`, `to_identifier()`) — может быть полезен для обобщённых функций. |
| `DateTimeMixin.parse_datetime()` | Статический метод парсинга ISO-дат. |

**Примечание:** Вышестоящие слои **не должны** создавать DTO вручную (кроме как через `from_dict`). DTO иммутабельны, все изменения требуют создания нового экземпляра.

---

### Итоговое заключение

**Принципы работы со слоем `models`:**

1. **Импорт только из `src.models`** — используйте либо полный путь `from src.models import ComplexTreeDTO`, либо из подмодулей `from src.models.structure import ComplexTreeDTO`. Избегайте импорта внутренних `base.py`, `mixins.py` напрямую.

2. **DTO — неизменяемые (frozen)** — после создания их нельзя изменить. Это гарантирует потокобезопасность и предсказуемость.

3. **Создание DTO** — через фабричный метод `from_dict(data: dict)`. Этот метод выполняет минимальное преобразование (парсинг дат). Не добавляйте в него бизнес-логику.

4. **Использование идентификаторов** — метод `to_identifier()` возвращает `NodeIdentifier` из `core`, что удобно для событий (например, `NodeSelected`).

5. **Различение Tree/Detail** — поле `IS_DETAIL` позволяет слоям выше понять, какие данные доступны (полные или сокращённые). `NODE_TYPE` даёт возможность полиморфной работы.

6. **Запрещено**:
   - Менять поля DTO (они frozen).
   - Добавлять методы, обращающиеся к API, репозиториям, сервисам.
   - Использовать DTO для хранения состояния UI (для этого есть `view models`).

Слой `models` является **единственным источником правды** о структуре данных, получаемых с бэкенда. Любое изменение API должно начинаться с корректировки DTO в этом слое.