# ============================================
# СПЕЦИФИКАЦИЯ: MODELS (DTO СЛОЙ)
# ============================================

## 1. НАЗНАЧЕНИЕ
Модели — это слой, определяющий структуру данных, которыми оперирует приложение. Они являются единственным источником правды о том, как выглядят сущности предметной области (комплексы, корпуса, контрагенты) на стороне клиента. Модели обеспечивают типобезопасность и изолируют остальной код от изменений в API бекенда.

## 2. ГДЕ ЛЕЖИТ
`client/src/models/`

## 3. ЗА ЧТО ОТВЕЧАЕТ
✅ **Отвечает за:**
- Определение структуры всех сущностей приложения
- Типизацию полей (int, str, Optional, datetime)
- Десериализацию из JSON (метод `from_dict`)
- Иммутабельность данных (защита от случайных изменений)
- Базовую валидацию обязательных полей
- Работу с датами (парсинг ISO строк в datetime)

❌ **НЕ отвечает за:**
- Бизнес-логику (это `services`)
- Форматирование для UI (это `ui/formatters`)
- Загрузку/сохранение данных (это `data`)
- Связи между сущностями (только через ID)
- Сериализацию в JSON (это задача API клиента)

## 4. КТО ИСПОЛЬЗУЕТ
- **Потребители:** Все слои приложения (`data`, `services`, `controllers`, `ui`)
- **Зависимости:** 
  - Core (базовые типы, `NodeType`)
  - Shared (утилиты для парсинга дат)
  - Никаких зависимостей от `data`, `services`, `ui`

## 5. КЛЮЧЕВЫЕ ПОНЯТИЯ
- **DTO (Data Transfer Object)** — объект только для переноса данных
- **Иммутабельность** — невозможность изменить объект после создания
- **from_dict()** — единый метод создания из ответа API
- **BaseDTO** — корневой класс для всех моделей
- **DateTimeMixin** — примесь для работы с датами
- **Связи через ID** — модель хранит только идентификаторы, не объекты

## 6. ОГРАНИЧЕНИЯ (ВАЖНО!)
⛔ **НЕЛЬЗЯ:**
- Добавлять методы с бизнес-логикой
- Хранить связанные объекты (только ID)
- Использовать `from_dict` не по назначению
- Изменять поля после создания
- Создавать циклические зависимости между моделями
- Добавлять зависимости от других слоёв
- Использовать магические строки/числа

✅ **МОЖНО:**
- Добавлять новые модели
- Расширять существующие новыми полями
- Добавлять новые миксины (если нужно)
- Наследоваться от BaseDTO

## 7. ПРИМЕРЫ (только концептуально)
```python
# Как это будет использоваться (не реализация!)
from src.models import Complex, Building

# Создание из API ответа
complex = Complex.from_dict(api_response)

# Только чтение данных
name = complex.name
created = complex.created_at

# Нельзя изменить!
# complex.name = "Новое"  # ❌ Ошибка!

# Связи только через ID
building = Building.from_dict(data)
owner_id = building.owner_id  # ✅ правильно
# owner = building.owner      # ❌ нельзя!
8. РИСКИ
🔴 Критические:

Нарушение иммутабельности → случайные изменения данных в кэше

Добавление логики в модели → разрастание ответственности

Хранение связанных объектов → дублирование данных, проблемы консистентности

🟡 Средние:

Неполная типизация (использование Any) → потеря преимуществ IDE

Игнорирование Optional для необязательных полей → ошибки при отсутствии данных

🟢 Контролируемые:

Рост числа моделей при сохранении чистоты не влияет на стабильность

============================================
КОНЕЦ СПЕЦИФИКАЦИИ
============================================

# Models — описание слоя

## Назначение

DTO (Data Transfer Objects) — иммутабельные контейнеры данных, соответствующие структуре API бэкенда.

**Строгая зависимость:** только от `core` (типы, исключения) и `utils.logger`. Никакой бизнес-логики, UI-логики или методов работы с данными.

---

## Структура

```
models/
├── __init__.py              # Экспорт всех моделей
├── base.py                  # BaseDTO — базовый класс
├── mixins.py                # DateTimeMixin — работа с датами
├── complex.py               # Complex
├── building.py              # Building
├── floor.py                 # Floor
├── room.py                  # Room
├── counterparty.py          # Counterparty
└── responsible_person.py    # ResponsiblePerson
```

---

## Публичное API

### Импорт

```python
from src.models import Complex, Building, Floor, Room, Counterparty, ResponsiblePerson
```

---

## Компоненты

### 1. BaseDTO (`base.py`)

Базовый класс для всех моделей.

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `id` | `int` | Уникальный идентификатор (обязательный) |

**Особенности:**
- `frozen=True` — иммутабельность для кэширования
- `kw_only=True` — явные именованные аргументы
- Валидация `id > 0` в `__post_init__`

---

### 2. DateTimeMixin (`mixins.py`)

Миксин для работы с датами.

| Атрибут | Тип |
|---------|-----|
| `created_at` | `Optional[datetime]` |
| `updated_at` | `Optional[datetime]` |

| Метод | Описание |
|-------|----------|
| `parse_datetime(value)` | Парсит ISO-строку, нормализует `Z` → `+00:00`, логирует ошибки |

---

### 3. Модели данных

Все модели наследуют `BaseDTO` и `DateTimeMixin`.

#### Общее для всех моделей

| Элемент | Описание |
|---------|----------|
| `NODE_TYPE` | Атрибут класса — строковый идентификатор типа узла |
| `from_dict(cls, data)` | Фабричный метод, создаёт модель из API-ответа |

---

#### Complex (`complex.py`)

| Поле | Тип | Обязательное |
|------|-----|--------------|
| `name` | `str` | ✅ |
| `buildings_count` | `int` | ❌ (0) |
| `description` | `Optional[str]` | ❌ |
| `address` | `Optional[str]` | ❌ |
| `owner_id` | `Optional[int]` | ❌ |

---

#### Building (`building.py`)

| Поле | Тип | Обязательное |
|------|-----|--------------|
| `name` | `str` | ✅ |
| `complex_id` | `int` | ✅ |
| `floors_count` | `int` | ❌ (0) |
| `description` | `Optional[str]` | ❌ |
| `address` | `Optional[str]` | ❌ |
| `status_id` | `Optional[int]` | ❌ |
| `owner_id` | `Optional[int]` | ❌ |

---

#### Floor (`floor.py`)

| Поле | Тип | Обязательное |
|------|-----|--------------|
| `number` | `int` | ✅ |
| `building_id` | `int` | ✅ |
| `rooms_count` | `int` | ❌ (0) |
| `description` | `Optional[str]` | ❌ |
| `physical_type_id` | `Optional[int]` | ❌ |
| `status_id` | `Optional[int]` | ❌ |
| `plan_image_url` | `Optional[str]` | ❌ |

---

#### Room (`room.py`)

| Поле | Тип | Обязательное |
|------|-----|--------------|
| `number` | `str` | ✅ |
| `floor_id` | `int` | ✅ |
| `area` | `Optional[float]` | ❌ |
| `status_code` | `Optional[str]` | ❌ |
| `description` | `Optional[str]` | ❌ |
| `physical_type_id` | `Optional[int]` | ❌ |
| `max_tenants` | `Optional[int]` | ❌ |

---

#### Counterparty (`counterparty.py`)

| Поле | Тип | Обязательное |
|------|-----|--------------|
| `short_name` | `str` | ✅ |
| `full_name` | `Optional[str]` | ❌ |
| `type_id` | `Optional[int]` | ❌ |
| `tax_id` | `Optional[str]` | ❌ |
| `legal_address` | `Optional[str]` | ❌ |
| `actual_address` | `Optional[str]` | ❌ |
| `bank_details` | `Optional[Dict]` | ❌ |
| `status_code` | `str` | ❌ ('active') |
| `notes` | `Optional[str]` | ❌ |

---

#### ResponsiblePerson (`responsible_person.py`)

| Поле | Тип | Обязательное |
|------|-----|--------------|
| `counterparty_id` | `int` | ✅ |
| `person_name` | `str` | ✅ |
| `position` | `Optional[str]` | ❌ |
| `role_code` | `Optional[str]` | ❌ |
| `phone` | `Optional[str]` | ❌ |
| `email` | `Optional[str]` | ❌ |
| `contact_categories` | `Optional[str]` | ❌ |
| `is_public_contact` | `bool` | ❌ (False) |
| `is_active` | `bool` | ❌ (True) |
| `notes` | `Optional[str]` | ❌ |

**Особенность:** `contact_categories` нормализует список API в строку через запятую.

---

## Использование

### Создание из API

```python
from src.models import Complex

api_response = {"id": 1, "name": "Северный", "address": "ул. Ленина, 1"}
complex = Complex.from_dict(api_response)

print(complex.name)      # "Северный"
print(complex.id)        # 1
```

### Иммутабельность

```python
complex.name = "Южный"   # ❌ FrozenInstanceError
```

### Сравнение

```python
c1 = Complex(id=1, name="Северный")
c2 = Complex(id=1, name="Южный")
assert c1 == c2          # True — сравнивается id и все поля
```

---

## Валидация

| Что валидируется | Где | Ошибка |
|------------------|-----|--------|
| `id > 0` | `BaseDTO.__post_init__` | `ValueError` |
| Обязательные поля в `from_dict` | Каждая модель | `ValueError` |

---

## Зависимости

| Зависимость | Назначение |
|-------------|------------|
| `core.types` | `NodeType` (не используется напрямую, но модели имеют `NODE_TYPE`) |
| `utils.logger` | Логирование ошибок парсинга дат |

**Нет зависимостей на:** `data`, `services`, `projections`, `controllers`, `ui`

---

## Итог

Слой предоставляет вышележащим слоям:
- **Иммутабельные DTO** для всех типов узлов
- **Единый интерфейс** создания из API через `from_dict`
- **Безопасное преобразование дат** с логированием ошибок
- **Валидацию** обязательных полей на этапе создания