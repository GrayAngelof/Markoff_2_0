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

## 📚 **СЛОЙ MODELS: ПОЛНОЕ ОПИСАНИЕ**

---

## 1. **НАЗНАЧЕНИЕ И МЕСТО В АРХИТЕКТУРЕ**

Модели — это **слой определения структуры данных**, которым оперирует приложение. Они являются единственным источником правды о том, как выглядят сущности предметной области (комплексы, корпуса, контрагенты) на стороне клиента. Модели обеспечивают типобезопасность и изолируют остальной код от изменений в API бекенда.

### **Место в иерархии**
```
controllers (координация потока данных)
      ↓
services (бизнес-логика загрузки)
      ↓
data (хранение, навигация, валидность)
      ↓
models (структуры данных) ←───────┐
      ↓                          │
core (типы, события) ────────────┘
```

**Ключевое правило:** Models может импортировать `core` (только базовые типы, например `NodeType`), но НЕ может импортировать `data`, `services`, `controllers` и `ui`.

---

## 2. **СТРУКТУРА СЛОЯ**

```
models/
├── __init__.py                 # Публичное API (витрина)
├── base.py                     # BaseDTO, DateTimeMixin
├── complex.py                  # Модель комплекса
├── building.py                 # Модель корпуса
├── floor.py                    # Модель этажа
├── room.py                     # Модель помещения
├── counterparty.py             # Модель контрагента
└── responsible_person.py       # Модель ответственного лица
```

**Принцип:** Каждый модуль отвечает за одну группу сущностей. Все модели следуют единому паттерну: иммутабельный dataclass с методом `from_dict`.

---

## 3. **КОМПОНЕНТЫ СЛОЯ**

### 3.1. **BaseDTO и DateTimeMixin (base.py)**

```python
from src.models.base import BaseDTO, DateTimeMixin
```

**BaseDTO** — абстрактный базовый класс для всех моделей:
- Определяет интерфейс (`from_dict`)
- Обеспечивает единообразие

**DateTimeMixin** — примесь для работы с датами:
- Парсинг ISO строк в `datetime` объекты
- Единое форматирование

---

### 3.2. **Complex — модель комплекса**

```python
from src.models import Complex

complex = Complex.from_dict(api_data)
```

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `id` | `int` | ✅ | Уникальный идентификатор |
| `name` | `str` | ✅ | Название комплекса |
| `buildings_count` | `int` | ✅ | Количество корпусов (кэшированное значение) |
| `description` | `Optional[str]` | ❌ | Описание комплекса |
| `address` | `Optional[str]` | ❌ | Адрес комплекса |
| `owner_id` | `Optional[int]` | ❌ | ID владельца (контрагента) |
| `created_at` | `Optional[datetime]` | ❌ | Дата создания |
| `updated_at` | `Optional[datetime]` | ❌ | Дата обновления |

**Пример использования:**
```python
# Создание из API
complex = Complex.from_dict({
    "id": 1,
    "name": "Фабрика Веретено",
    "buildings_count": 2,
    "address": "г. Москва, ул. Ткацкая, д. 1",
    "owner_id": 42
})

# Только чтение
print(complex.name)          # "Фабрика Веретено"
print(complex.buildings_count)  # 2
print(complex.owner_id)      # 42

# Нельзя изменить!
# complex.name = "Новое"  # ❌ Ошибка!
```

---

### 3.3. **Building — модель корпуса**

```python
from src.models import Building

building = Building.from_dict(api_data)
```

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `id` | `int` | ✅ | Уникальный идентификатор |
| `name` | `str` | ✅ | Название корпуса |
| `complex_id` | `int` | ✅ | ID родительского комплекса |
| `floors_count` | `int` | ✅ | Количество этажей (кэшированное значение) |
| `description` | `Optional[str]` | ❌ | Описание корпуса |
| `address` | `Optional[str]` | ❌ | Адрес корпуса |
| `status_id` | `Optional[int]` | ❌ | ID статуса (справочник) |
| `owner_id` | `Optional[int]` | ❌ | ID владельца (контрагента) |
| `created_at` | `Optional[datetime]` | ❌ | Дата создания |
| `updated_at` | `Optional[datetime]` | ❌ | Дата обновления |

**Пример использования:**
```python
# Создание из API
building = Building.from_dict({
    "id": 101,
    "name": "Корпус А",
    "complex_id": 1,
    "floors_count": 9,
    "owner_id": 42
})

# Навигация через ID
complex_id = building.complex_id  # 1
owner_id = building.owner_id      # 42

# Для получения объекта используем репозиторий
complex_obj = complex_repo.get(building.complex_id)
```

---

### 3.4. **Floor — модель этажа**

```python
from src.models import Floor

floor = Floor.from_dict(api_data)
```

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `id` | `int` | ✅ | Уникальный идентификатор |
| `number` | `int` | ✅ | Номер этажа (может быть отрицательным) |
| `building_id` | `int` | ✅ | ID родительского корпуса |
| `rooms_count` | `int` | ✅ | Количество помещений (кэшированное значение) |
| `description` | `Optional[str]` | ❌ | Описание этажа |
| `physical_type_id` | `Optional[int]` | ❌ | ID типа этажа (справочник) |
| `status_id` | `Optional[int]` | ❌ | ID статуса (справочник) |
| `plan_image_url` | `Optional[str]` | ❌ | URL плана этажа |
| `created_at` | `Optional[datetime]` | ❌ | Дата создания |
| `updated_at` | `Optional[datetime]` | ❌ | Дата обновления |

**Пример использования:**
```python
# Создание из API
floor = Floor.from_dict({
    "id": 1001,
    "number": -1,
    "building_id": 101,
    "rooms_count": 5
})

# Отрицательный номер = подвал
print(floor.number)  # -1

# Навигация через ID
building_id = floor.building_id  # 101
```

---

### 3.5. **Room — модель помещения**

```python
from src.models import Room

room = Room.from_dict(api_data)
```

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `id` | `int` | ✅ | Уникальный идентификатор |
| `number` | `str` | ✅ | Номер помещения ("101", "101А", "Б12") |
| `floor_id` | `int` | ✅ | ID родительского этажа |
| `area` | `Optional[float]` | ❌ | Площадь помещения |
| `status_code` | `Optional[str]` | ❌ | Код статуса ('free', 'occupied', 'reserved', 'maintenance') |
| `description` | `Optional[str]` | ❌ | Описание помещения |
| `physical_type_id` | `Optional[int]` | ❌ | ID типа помещения (справочник) |
| `max_tenants` | `Optional[int]` | ❌ | Максимальное количество арендаторов |
| `created_at` | `Optional[datetime]` | ❌ | Дата создания |
| `updated_at` | `Optional[datetime]` | ❌ | Дата обновления |

**Пример использования:**
```python
# Создание из API
room = Room.from_dict({
    "id": 10001,
    "number": "101А",
    "floor_id": 1001,
    "area": 45.5,
    "status_code": "free"
})

# Номер как строка (не int!)
print(room.number)      # "101А"
print(room.status_code)  # "free"
```

---

### 3.6. **Counterparty — модель контрагента**

```python
from src.models import Counterparty

counterparty = Counterparty.from_dict(api_data)
```

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `id` | `int` | ✅ | Уникальный идентификатор |
| `short_name` | `str` | ✅ | Краткое название |
| `status_code` | `str` | ✅ | Статус ('active', 'suspended') |
| `full_name` | `Optional[str]` | ❌ | Полное юридическое название |
| `type_id` | `Optional[int]` | ❌ | ID типа контрагента (справочник) |
| `tax_id` | `Optional[str]` | ❌ | ИНН |
| `legal_address` | `Optional[str]` | ❌ | Юридический адрес |
| `actual_address` | `Optional[str]` | ❌ | Фактический адрес |
| `bank_details` | `Optional[Dict]` | ❌ | Банковские реквизиты (полуструктурированные) |
| `notes` | `Optional[str]` | ❌ | Примечания |
| `created_at` | `Optional[datetime]` | ❌ | Дата создания |
| `updated_at` | `Optional[datetime]` | ❌ | Дата обновления |

**Пример использования:**
```python
# Создание из API
counterparty = Counterparty.from_dict({
    "id": 42,
    "short_name": "ООО Ромашка",
    "full_name": "Общество с ограниченной ответственностью 'Ромашка'",
    "tax_id": "1234567890",
    "status_code": "active",
    "bank_details": {
        "bank_name": "Сбербанк",
        "account": "40702810123456789012",
        "bik": "044525225"
    }
})

print(counterparty.short_name)  # "ООО Ромашка"
print(counterparty.tax_id)      # "1234567890"
```

---

### 3.7. **ResponsiblePerson — модель ответственного лица**

```python
from src.models import ResponsiblePerson

person = ResponsiblePerson.from_dict(api_data)
```

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `id` | `int` | ✅ | Уникальный идентификатор |
| `counterparty_id` | `int` | ✅ | ID контрагента |
| `person_name` | `str` | ✅ | ФИО |
| `is_public_contact` | `bool` | ✅ | Публичный ли контакт |
| `is_active` | `bool` | ✅ | Активен ли |
| `position` | `Optional[str]` | ❌ | Должность |
| `role_code` | `Optional[str]` | ❌ | Код роли (из справочника) |
| `phone` | `Optional[str]` | ❌ | Телефон |
| `email` | `Optional[str]` | ❌ | Email |
| `contact_categories` | `Optional[str]` | ❌ | Категории контактов (через запятую) |
| `notes` | `Optional[str]` | ❌ | Примечания |
| `created_at` | `Optional[datetime]` | ❌ | Дата создания |
| `updated_at` | `Optional[datetime]` | ❌ | Дата обновления |

**Пример использования:**
```python
# Создание из API
person = ResponsiblePerson.from_dict({
    "id": 100,
    "counterparty_id": 42,
    "person_name": "Иванов Иван Иванович",
    "position": "Генеральный директор",
    "phone": "+7 (495) 123-45-67",
    "email": "i.ivanov@romashka.ru",
    "is_public_contact": True,
    "is_active": True
})

print(person.person_name)  # "Иванов Иван Иванович"
print(person.phone)        # "+7 (495) 123-45-67"
```

---

## 4. **ПРАВИЛА ИСПОЛЬЗОВАНИЯ**

### ✅ **Правильно**

```python
# Создание из API
complex = Complex.from_dict(api_data)

# Только чтение данных
name = complex.name
building_count = complex.buildings_count

# Доступ к связанным данным через ID
owner_id = building.owner_id
if owner_id:
    owner = counterparty_repo.get(owner_id)

# Использование в UI через форматтеры
from ui.formatters import building_formatter
label.setText(building_formatter.format_title(building))

# Использование в сервисах
def load_building_with_owner(self, building_id):
    building = self.load_details(NodeType.BUILDING, building_id)
    if building and building.owner_id:
        owner = self.load_counterparty(building.owner_id)
```

### ❌ **Неправильно**

```python
# Попытка изменить (модели иммутабельны!)
complex.name = "Новое"  # ❌ Ошибка!

# Хранение связанных объектов в модели
@dataclass
class Building:
    complex: Complex      # ❌ Нельзя!
    owner: Counterparty   # ❌ Нельзя!

# Бизнес-логика в модели
class Room:
    def is_available(self):     # ❌ Нельзя!
        return self.status_code == 'free'

# Форматирование в модели
class Building:
    def display_name(self):      # ❌ Нельзя!
        return f"{self.name} (ID: {self.id})"

# Прямое создание без from_dict
complex = Complex(id=1, name="Тест")  # ❌ Не использовать!
```

---

## 5. **КЛЮЧЕВЫЕ ПРИНЦИПЫ**

### 5.1. **Иммутабельность**
```python
@dataclass(frozen=True, slots=True)
class Complex:
    id: int
    name: str
```

**Почему:** Нельзя случайно изменить данные в кэше или передать по ссылке и испортить оригинал.

### 5.2. **Только данные, никакой логики**
- ❌ Нет методов `is_available()`, `can_edit()`, `get_owner()`
- ✅ Вся логика в сервисах (`DataLoader`, `ContextService`)

### 5.3. **Связи только через ID**
- ❌ Нет `building.complex` (объект)
- ✅ Только `building.complex_id` (int)

### 5.4. **Только коды, никакого текста**
- ❌ `status: "Свободно"` (локализация в UI)
- ✅ `status_code: "free"`

### 5.5. **Единый метод создания `from_dict`**
```python
@classmethod
def from_dict(cls, data: dict) -> 'Complex':
    return cls(
        id=data['id'],
        name=data['name'],
        buildings_count=data.get('buildings_count', 0),
        # ...
    )
```

**Почему:** Единое место для преобразования API → модель. Защита от изменения API бекенда.

---

## 6. **ЧЕК-ЛИСТ: ЧТО ЕСТЬ В MODELS**

| Модель | Обязательные поля | Опциональные поля | Статус |
|--------|-------------------|-------------------|--------|
| `Complex` | `id`, `name`, `buildings_count` | 5 полей | ✅ |
| `Building` | `id`, `name`, `complex_id`, `floors_count` | 6 полей | ✅ |
| `Floor` | `id`, `number`, `building_id`, `rooms_count` | 6 полей | ✅ |
| `Room` | `id`, `number`, `floor_id` | 6 полей | ✅ |
| `Counterparty` | `id`, `short_name`, `status_code` | 8 полей | ✅ |
| `ResponsiblePerson` | `id`, `counterparty_id`, `person_name`, `is_public_contact`, `is_active` | 7 полей | ✅ |

---

## 7. **ВЗАИМОДЕЙСТВИЕ С ДРУГИМИ СЛОЯМИ**

### 7.1. **Связь с ядром (core)**

Models **использует** типы из core:
```python
from src.core.types import NodeType

# Определение типа для EntityGraph
def get_node_type(entity: Any) -> Optional[NodeType]:
    if isinstance(entity, Complex):
        return NodeType.COMPLEX
    # ...
```

### 7.2. **Связь со слоем данных (data)**

Data слой **хранит** модели:
```python
# EntityGraph хранит модели
graph.add_or_update(complex_obj)  # complex_obj: Complex

# Репозитории возвращают модели
building: Building = building_repo.get(101)
```

### 7.3. **Связь со слоем сервисов (services)**

Services **создаёт и передаёт** модели:
```python
# ApiClient возвращает модели
complexes: List[Complex] = api.get_complexes()

# DataLoader загружает модели
building: Building = loader.load_details(NodeType.BUILDING, 101)

# ContextService работает с моделями
complex_obj: Complex = complex_repo.get(complex_id)
```

### 7.4. **Связь с контроллерами (controllers)**

Controllers **получают и передают** модели:
```python
# TreeController получает модели
details = self._loader.load_details(node_type, node_id)  # Complex, Building, etc.

# Отправляет в UI через события
self._bus.emit(NodeDetailsLoaded(
    node=node,
    payload=details,  # модель
    context=context
))
```

---

## 8. **ИТОГ: ЧТО ДАЁТ СЛОЙ MODELS**

| Аспект | Результат |
|--------|-----------|
| **Типобезопасность** | Все поля типизированы, IDE подсказывает |
| **Иммутабельность** | Нельзя изменить данные случайно |
| **Чистота DTO** | Только данные, никакой логики |
| **Изоляция** | Нет зависимостей от других слоёв |
| **Расширяемость** | Добавить поле — 1 строка в dataclass |
| **Консистентность** | Все модели следуют единому паттерну |
| **Связи** | Только через ID, нет циклических зависимостей |
| **Парсинг дат** | Автоматическое преобразование в datetime |

---

**Модели — это контракт между бекендом и клиентом:**
- **Только данные, никакой логики** — SRP соблюдён
- **Только чтение, никаких изменений** — иммутабельность
- **Только ID, никаких объектов** — нет циклических ссылок
- **Только коды, никакого текста** — локализация в UI

💡 **Итог:** Модели — это фундамент типобезопасности и единообразия работы с данными во всём приложении. Все остальные слои строятся на этом фундаменте, зная, что модели стабильны и предсказуемы. 