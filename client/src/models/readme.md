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

## Описание реализации и структуры

В соответствии со спецификацией, слой моделей реализован как набор иммутабельных DTO, обеспечивающих типобезопасность и единообразие работы с данными от API бекенда. Код организован в следующую структуру каталогов, где каждый модуль отвечает за свою группу сущностей:
models/
├── init.py # Публичное API (витрина)
├── base.py # BaseDTO, DateTimeMixin
├── complex.py # Модель комплекса
├── building.py # Модель корпуса
├── floor.py # Модель этажа
├── room.py # Модель помещения
├── counterparty.py # Модель контрагента
└── responsible_person.py # Модель ответственного лица

Публичное API (что можно импортировать из models)
python
from src.models import (
    # Основные модели
    Complex,
    Building,
    Floor,
    Room,
    Counterparty,
    ResponsiblePerson
)
🔹 Complex
python
complex.id               # int
complex.name             # str
complex.buildings_count  # int (сколько корпусов)
complex.description      # Optional[str]
complex.address          # Optional[str]
complex.owner_id         # Optional[int]
complex.created_at       # Optional[datetime]
complex.updated_at       # Optional[datetime]
🔹 Building
python
building.id              # int
building.name            # str
building.complex_id      # int
building.floors_count    # int (сколько этажей)
building.description     # Optional[str]
building.address         # Optional[str]
building.status_id       # Optional[int]
building.owner_id        # Optional[int]
building.created_at      # Optional[datetime]
building.updated_at      # Optional[datetime]
🔹 Floor
python
floor.id                 # int
floor.number             # int (может быть отрицательным)
floor.building_id        # int
floor.rooms_count        # int (сколько помещений)
floor.description        # Optional[str]
floor.physical_type_id   # Optional[int]
floor.status_id          # Optional[int]
floor.plan_image_url     # Optional[str]
floor.created_at         # Optional[datetime]
floor.updated_at         # Optional[datetime]
🔹 Room
python
room.id                  # int
room.number              # str ("101", "101А")
room.floor_id            # int
room.area                # Optional[float]
room.status_code         # Optional[str] ('free', 'occupied')
room.description         # Optional[str]
room.physical_type_id    # Optional[int]
room.max_tenants         # Optional[int]
room.created_at          # Optional[datetime]
room.updated_at          # Optional[datetime]
🔹 Counterparty
python
counterparty.id              # int
counterparty.short_name      # str
counterparty.status_code     # str ('active', 'suspended')
counterparty.full_name       # Optional[str]
counterparty.type_id         # Optional[int]
counterparty.tax_id          # Optional[str] (ИНН)
counterparty.legal_address   # Optional[str]
counterparty.actual_address  # Optional[str]
counterparty.bank_details    # Optional[Dict]
counterparty.notes           # Optional[str]
counterparty.created_at      # Optional[datetime]
counterparty.updated_at      # Optional[datetime]
🔹 ResponsiblePerson
python
person.id                    # int
person.counterparty_id       # int
person.person_name           # str
person.is_public_contact     # bool
person.is_active             # bool
person.position              # Optional[str]
person.role_code             # Optional[str]
person.phone                 # Optional[str]
person.email                 # Optional[str]
person.contact_categories    # Optional[str]
person.notes                 # Optional[str]
person.created_at            # Optional[datetime]
person.updated_at            # Optional[datetime]
🎯 Правила использования
✅ Правильно
python
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
❌ Неправильно
python
# Попытка изменить
complex.name = "Новое"  # ❌ Ошибка!

# Хранение связанных объектов
class Building:
    complex: Complex  # ❌ Нельзя!
    owner: Counterparty  # ❌ Нельзя!

# Логика в модели
class Room:
    def is_available(self):  # ❌ Нельзя!
        return self.status_code == 'free'

# Форматирование в модели
class Building:
    def display_name(self):  # ❌ Нельзя!
        return f"{self.name} (ID: {self.id})"

Чек-лист: что есть в models
Модель	Обязательные поля	Опциональные поля	Готово
Complex	id, name, buildings_count	5 полей	✅
Building	id, name, complex_id, floors_count	6 полей	✅
Floor	id, number, building_id, rooms_count	6 полей	✅
Room	id, number, floor_id	6 полей	✅
Counterparty	id, short_name, status_code	8 полей	✅
ResponsiblePerson	id, counterparty_id, person_name, is_public_contact, is_active	7 полей	✅
💡 Итог
Модели — это контракт между бекендом и клиентом:
Только данные, никакой логики
Только чтение, никаких изменений
Только ID, никаких объектов
Только коды, никакого текста