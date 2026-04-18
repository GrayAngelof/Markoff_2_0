## Анализ слоя: **models** (слой DTO-моделей данных)

### Краткое описание слоя

**Назначение** – предоставить иммутабельные DTO (Data Transfer Objects) для всех сущностей предметной области: комплексы, корпуса, этажи, помещения, контрагенты, ответственные лица. Слой `models` является **единственным источником истины** о структуре данных, получаемых от API и передаваемых внутри приложения.

**Что делает:**
- Определяет строго типизированные, иммутабельные (`frozen=True`) dataclass-модели
- Содержит методы `from_dict()` для десериализации ответов API в модели
- Обеспечивает парсинг datetime полей через миксин `DateTimeMixin`
- Предоставляет единый базовый класс `BaseDTO` с общим полем `id`

**Что не должен делать:**
- Содержать бизнес-логику, валидацию, правила иерархии (это в `core.rules` или `services`)
- Взаимодействовать с API, БД, кэшем, файловой системой (это в `data`)
- Содержать UI-специфичный код (форматирование, отображение)
- Импортировать что-либо из `data`, `services`, `projections`, `controllers`, `ui`
- Мутировать состояние (все модели иммутабельны)

**Зависимости:** только от `core` (типы `NodeType` не импортируются явно, но используются атрибуты `NODE_TYPE` для соответствия) и `utils.logger` (допустим на любом слое). Никаких зависимостей от вышестоящих слоёв.

---

### Файловая структура слоя

```
client/src/models/
├── __init__.py                    # Публичный экспорт всех моделей
├── base.py                        # BaseDTO (базовый класс с id)
├── mixins.py                      # DateTimeMixin (парсинг дат)
├── complex.py                     # Complex (комплекс)
├── building.py                    # Building (корпус)
├── floor.py                       # Floor (этаж)
├── room.py                        # Room (помещение)
├── counterparty.py                # Counterparty (контрагент)
└── responsible_person.py          # ResponsiblePerson (ответственное лицо)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `BaseDTO` | `base.py` | Базовый класс для всех DTO. Содержит обязательное поле `id` (int) и метод `__repr__`. |
| `DateTimeMixin` | `mixins.py` | Миксин, добавляющий поля `created_at`, `updated_at` (Optional[datetime]) и статический метод `parse_datetime()` для парсинга ISO-строк из API. |
| `Complex` | `complex.py` | Модель комплекса. Поля: `name`, `buildings_count`, `description`, `address`, `owner_id`. Имеет `NODE_TYPE = "complex"`. |
| `Building` | `building.py` | Модель корпуса. Поля: `name`, `complex_id`, `floors_count`, `description`, `address`, `status_id`, `owner_id`. `NODE_TYPE = "building"`. |
| `Floor` | `floor.py` | Модель этажа. Поля: `number`, `building_id`, `rooms_count`, `description`, `physical_type_id`, `status_id`, `plan_image_url`. `NODE_TYPE = "floor"`. |
| `Room` | `room.py` | Модель помещения. Поля: `number`, `floor_id`, `area`, `status_code`, `description`, `physical_type_id`, `max_tenants`. `NODE_TYPE = "room"`. |
| `Counterparty` | `counterparty.py` | Модель контрагента. Поля: `short_name`, `full_name`, `type_id`, `tax_id`, `legal_address`, `actual_address`, `bank_details`, `status_code`, `notes`. `NODE_TYPE = "counterparty"`. |
| `ResponsiblePerson` | `responsible_person.py` | Модель ответственного лица. Поля: `counterparty_id`, `person_name`, `position`, `role_code`, `phone`, `email`, `contact_categories`, `is_public_contact`, `is_active`, `notes`. `NODE_TYPE = "responsible_person"`. |

---

### Внутренние импорты (только между модулями models)

- `base.py` → импортирует только стандартный `dataclasses`
- `mixins.py` → импортирует `datetime`, `Optional`, `get_logger` из `utils.logger`
- `complex.py` → `from .base import BaseDTO`, `from .mixins import DateTimeMixin`
- `building.py` → аналогично
- `floor.py` → аналогично
- `room.py` → аналогично
- `counterparty.py` → аналогично
- `responsible_person.py` → аналогично
- `__init__.py` → импортирует все конкретные модели для публичного экспорта

**Никакие модели не импортируют друг друга** (например, `Complex` не импортирует `Building`). Это обеспечивает слабую связанность внутри слоя.

**Импорты из core отсутствуют** – хотя модели используют концепцию `NODE_TYPE`, они не импортируют `NodeType` из `core.types`. Это сделано намеренно: `NODE_TYPE` – строковая константа для удобства, а строгая типизация с `NodeType` происходит в вышестоящих слоях (`services`, `projections`).

---

### Экспортируемые методы / классы для вышестоящих слоёв

Все модели экспортируются через `src.models` (согласно `models/__init__.py`):

**Классы:**
- `Complex`
- `Building`
- `Floor`
- `Room`
- `Counterparty`
- `ResponsiblePerson`

**Методы (публичное API каждого класса):**
- `from_dict(data: dict) -> Self` – альтернативный конструктор для десериализации из ответа API.  
  *Выбрасывает `ValueError` при отсутствии обязательных полей.*
- Все поля доступны для чтения (иммутабельные атрибуты).
- Наследуют `__repr__` от `BaseDTO`.

**Не экспортируются напрямую:** `BaseDTO`, `DateTimeMixin` (они внутренние, хотя вышестоящие слои могут их импортировать при необходимости, но это не рекомендуется – лучше работать с конкретными моделями).

---

### Итоговое заключение: принципы работы со слоем `models`

1. **Зависимость только от `core` и утилит** – слой `models` не знает о `data`, `services` и выше. Импорты из `core` отсутствуют (хотя концептуально модели соответствуют типам из `core.types.nodes`, привязка через строковые `NODE_TYPE`).

2. **Иммутабельность обязательна** – все модели `frozen=True`. Это позволяет безопасно использовать их в кэшах, словарях, событиях и передавать между потоками.

3. **Создание моделей** – предпочтительный способ: `Complex.from_dict(api_response)`. В тестах или при ручном конструировании можно использовать конструктор `Complex(id=1, name="...", ...)`.

4. **Что нельзя делать в этом слое**:
   - Добавлять методы, изменяющие состояние (сеттеры, мутирующие методы)
   - Добавлять бизнес-проверки (например, `can_have_children` – это в `core.rules.hierarchy`)
   - Добавлять методы для работы с БД или API

5. **Расширение моделей** – при добавлении новой сущности:
   - Создать новый файл с классом, наследующим `BaseDTO` и `DateTimeMixin` (если нужны даты)
   - Определить `NODE_TYPE` строковой константой (соответствует значению `NodeType` из `core`)
   - Реализовать `from_dict()` с проверкой обязательных полей
   - Добавить класс в `__init__.py` и `__all__`

6. **Обработка дат** – использовать `DateTimeMixin.parse_datetime()` для преобразования ISO-строк. Ошибки парсинга логируются как warning, возвращается `None`.

7. **Связь с `core`** – для навигации по иерархии типов используйте функции из `core.rules.hierarchy`, передавая `model.NODE_TYPE` (преобразовав в `NodeType` при необходимости). Преобразование строки в `NodeType` выполняется в слое `projections` или `services`, а не в `models`.

Слой `models` является **чистым хранилищем данных** – его единственная ответственность: представить ответы API в типобезопасной, иммутабельной форме для использования всем приложением выше.