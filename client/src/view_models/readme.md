# ============================================
# СПЕЦИФИКАЦИЯ: View Models
# ============================================

## 1. НАЗНАЧЕНИЕ

Модуль View Models определяет **контракт данных между бизнес-логикой (контроллерами/проекциями) и пользовательским интерфейсом**. Это набор иммутабельных структур (dataclass), которые описывают, какие данные и в каком формате UI получает для отображения. Решает проблему неявных контрактов, когда UI "догадывается" о структуре данных из словарей или неявных полей моделей.

**Ключевая идея:** View Model — это не модель данных (Complex, Building), а **представление информации для конкретного экрана/вкладки**. Одна модель данных может порождать несколько View Models для разных контекстов отображения.

---

## 2. ГДЕ ЛЕЖИТ

```
client/src/view_models/
---

## 3. ЗА ЧТО ОТВЕЧАЕТ

### **Отвечает за:**
- Определение формата данных для каждой вкладки/экрана
- Обеспечение типобезопасности при передаче данных от контроллеров к UI
- Создание четкого контракта между слоями (что UI может ожидать)
- Группировку связанных данных в осмысленные структуры

### **НЕ отвечает за:**
- Логику получения данных (это проекции/контроллеры)
- Логику отображения (это UI)
- Хранение данных (это EntityGraph)
- Валидацию данных (это сервисы)
- Бизнес-правила (это DataLoader)

---

## 4. КТО ИСПОЛЬЗУЕТ

### **Создают (источники):**
- **Проекции** — преобразуют данные из репозиториев в View Models
- **Контроллеры** — вызывают проекции и передают View Models в события

### **Потребляют (назначение):**
- **UI (DetailsPanel, вкладки)** — подписываются на события с View Models и отображают их
- **UI (диалоги списков)** — получают View Models для отображения списков

### **НЕ используют:**
- Слой data (EntityGraph, репозитории) — они работают с моделями, не с View Models
- Слой services (DataLoader) — он работает с моделями
- Core — не знает о View Models

---

## 5. КЛЮЧЕВЫЕ ПОНЯТИЯ

| Термин | Значение |
|--------|----------|
| **View Model** | Иммутабельная структура данных, подготовленная специально для отображения в UI |
| **Статистика (Statistics)** | Агрегированные числовые показатели: количество объектов, площади, проценты занятости |
| **Группа контактов (ContactGroup)** | Контакты, сгруппированные по категории (юридические, финансовые, технические вопросы) |
| **Сводка (Summary)** | Краткая агрегированная информация (общая площадь, занятость, задолженность) |
| **Доменная гранулярность** | Каждый тип данных (статистика, контакты, датчики, события) обновляется независимо |
| **Заглушка (Placeholder)** | Отсутствие данных → UI показывает "—" или "нет данных", но структура View Model всегда присутствует |

---

## 6. ОГРАНИЧЕНИЯ (ВАЖНО!)

### **Запрещено:**
1. **Добавлять бизнес-логику в View Models**
   - ❌ Нет методов `is_available()`, `calculate_occupancy()`
   - ✅ Только поля-данные

2. **Хранить ссылки на модели данных**
   - ❌ Нет `building: Building`
   - ✅ Только примитивы и другие View Models

3. **Использовать View Models в data слое**
   - ❌ Репозитории не возвращают View Models
   - ✅ Репозитории возвращают модели (Complex, Building)

4. **Создавать циклические ссылки между View Models**
   - ❌ ComplexStatisticsVM не ссылается на BuildingStatisticsVM

5. **Добавлять поля "на всякий случай" (YAGNI)**
   - ❌ "может пригодится в будущем"
   - ✅ Только то, что реально нужно UI сейчас

6. **Менять View Models без обновления UI**
   - View Model — это контракт. Изменение = изменение UI

7. **Возвращать None вместо View Model**
   - ✅ Всегда возвращаем View Model с нулевыми/пустыми значениями
   - ✅ UI сам решает, показывать "0" или "—"

---

## 7. ПРИМЕРЫ (что входит в каждую View Model)

### **StatisticsViewModel (для вкладки "Физика")**

| Компонент | Поля |
|-----------|------|
| **ComplexStatisticsVM** | total_buildings, total_floors, total_rooms, free_rooms, occupied_rooms, reserved_rooms, maintenance_rooms, total_area, rentable_area, occupancy_rate, room_types (List[RoomTypeStat]) |
| **BuildingStatisticsVM** | total_floors, total_rooms, free_rooms, occupied_rooms, reserved_rooms, maintenance_rooms, total_area, occupancy_rate |
| **FloorStatisticsVM** | total_rooms, free_rooms, occupied_rooms, reserved_rooms, maintenance_rooms, room_types |
| **RoomTypeStat** | type_name (str), count (int), area (float) |

### **ContactsViewModel (для вкладки "Юрики")**

| Компонент | Поля |
|-----------|------|
| **ContactsVM** | total_organizations, tenants_count, owners_count, debtors_count, groups (List[ContactGroup]), summary (ContactSummary) |
| **ContactGroup** | category (str), contacts (List[ContactPerson]) |
| **ContactPerson** | name, position, phone, email, is_primary |
| **ContactSummary** | total_area, rented_area, occupancy_rate, total_debt |

### **SensorsViewModel (для вкладки "Пожарка")**

| Компонент | Поля |
|-----------|------|
| **SensorsVM** | total, active, inactive, maintenance, issues (List[SensorIssue]) |
| **SensorIssue** | sensor_id, location, issue, last_check |

### **EventsViewModel (для вкладки "Пожарка")**

| Компонент | Поля |
|-----------|------|
| **EventsVM** | total, recent_events (List[EventItem]) |
| **EventItem** | timestamp, type, location, description, is_critical |

### **ListViewModel (для списков)**

| Компонент | Поля |
|-----------|------|
| **BuildingListItem** | id, name, floors_count |
| **FloorListItem** | id, number, rooms_count |
| **RoomListItem** | id, number, area, status_code |

---

## 8. РИСКИ

| Риск | Вероятность | Смягчение |
|------|-------------|-----------|
| **Разрастание View Models** | Средняя | Строго следовать YAGNI — добавлять только то, что нужно UI сейчас |
| **Дублирование полей между View Models** | Средняя | Использовать композицию (один View Model внутри другого) |
| **Несоответствие View Model и UI** | Высокая | View Model — контракт. Изменение требует синхронного обновления UI |
| **Соблазн добавить логику** | Средняя | Code review, проверка на соответствие SRP |
| **Использование View Models в data слое** | Низкая | Архитектурный контроль, запрет импортов |
| **Избыточная детализация** | Средняя | Начинать с простых структур, усложнять по мере необходимости |

---

## 9. ПРИНЦИПЫ ПРОЕКТИРОВАНИЯ

1. **Иммутабельность** — `@dataclass(frozen=True, slots=True)`
2. **Единая гранулярность** — каждый домен (статистика, контакты, датчики, события) — отдельный View Model
3. **Отсутствие None** — всегда возвращаем View Model с нулевыми/пустыми значениями
4. **Явность** — все поля имеют понятные имена и типы
5. **Минимализм** — только то, что нужно UI сейчас
6. **Самодокументируемость** — имена полей говорят сами за себя

---

# ============================================
# КОНЕЦ СПЕЦИФИКАЦИИ
# ============================================

# View Models — описание слоя

## Назначение

Контракты данных между бизнес-логикой и UI. Иммутабельные структуры, подготовленные для отображения. Содержат только данные, никакой логики.

**Строгая зависимость:** ни от каких слоёв (только стандартная библиотека). Может использоваться любым слоем выше.

---

## Структура

```
view_models/
├── __init__.py              # Публичное API
├── statistics.py            # Статистика (физика)
├── contacts.py              # Контакты (юрики)
├── sensors.py               # Датчики (пожарка)
├── events.py                # События (пожарка)
└── lists.py                 # Компактные списки
```

---

## Публичное API

### Импорт

```python
from src.view_models import (
    # Statistics
    ComplexStatisticsVM,
    BuildingStatisticsVM,
    FloorStatisticsVM,
    RoomTypeStat,
    # Contacts
    ContactsVM,
    ContactGroup,
    ContactPerson,
    ContactSummary,
    # Sensors
    SensorsVM,
    SensorIssue,
    # Events
    EventsVM,
    EventItem,
    # Lists
    BuildingListItem,
    FloorListItem,
    RoomListItem,
)
```

---

## Компоненты

### 1. Статистика (`statistics.py`)

#### RoomTypeStat
Статистика по типу помещения.

| Поле | Тип | Описание |
|------|-----|----------|
| `type_name` | `str` | "Офисное", "Складское", "Торговое" |
| `count` | `int` | Количество помещений |
| `area` | `float` | Общая площадь |

#### ComplexStatisticsVM
Статистика для комплекса.

| Поле | Тип | Описание |
|------|-----|----------|
| `total_buildings` | `int` | Всего корпусов |
| `total_floors` | `int` | Всего этажей |
| `total_rooms` | `int` | Всего помещений |
| `free_rooms` | `int` | Свободных |
| `occupied_rooms` | `int` | Занятых |
| `reserved_rooms` | `int` | Зарезервированных |
| `maintenance_rooms` | `int` | На ремонте |
| `total_area` | `float` | Общая площадь |
| `rentable_area` | `float` | Сдаваемая площадь |
| `occupancy_rate` | `float` | Процент занятости (0-100) |
| `room_types` | `List[RoomTypeStat]` | Детализация по типам |

#### BuildingStatisticsVM
Статистика для корпуса.

| Поле | Тип |
|------|-----|
| `total_floors` | `int` |
| `total_rooms` | `int` |
| `free_rooms` | `int` |
| `occupied_rooms` | `int` |
| `reserved_rooms` | `int` |
| `maintenance_rooms` | `int` |
| `total_area` | `float` |
| `occupancy_rate` | `float` |

#### FloorStatisticsVM
Статистика для этажа.

| Поле | Тип |
|------|-----|
| `total_rooms` | `int` |
| `free_rooms` | `int` |
| `occupied_rooms` | `int` |
| `reserved_rooms` | `int` |
| `maintenance_rooms` | `int` |
| `room_types` | `List[RoomTypeStat]` |

---

### 2. Контакты (`contacts.py`)

#### ContactPerson
Контактное лицо.

| Поле | Тип |
|------|-----|
| `name` | `str` |
| `position` | `Optional[str]` |
| `phone` | `Optional[str]` |
| `email` | `Optional[str]` |
| `is_primary` | `bool` |

#### ContactGroup
Группа контактов по категории.

| Поле | Тип |
|------|-----|
| `category` | `str` |
| `contacts` | `List[ContactPerson]` |

#### ContactSummary
Сводка по контрагентам.

| Поле | Тип | Описание |
|------|-----|----------|
| `total_area` | `float` | Общая площадь |
| `rented_area` | `float` | Сданная площадь |
| `occupancy_rate` | `float` | Процент занятости |
| `total_debt` | `float` | Общая задолженность |

#### ContactsVM
Контакты для отображения.

| Поле | Тип | Описание |
|------|-----|----------|
| `total_organizations` | `int` | Всего организаций |
| `tenants_count` | `int` | Арендаторов |
| `owners_count` | `int` | Собственников |
| `debtors_count` | `int` | Должников |
| `groups` | `List[ContactGroup]` | Группы контактов |
| `summary` | `ContactSummary` | Сводка |

---

### 3. Датчики (`sensors.py`)

#### SensorIssue
Проблемный датчик.

| Поле | Тип | Описание |
|------|-----|----------|
| `sensor_id` | `int` | ID датчика |
| `location` | `str` | "пом. 203" |
| `issue` | `str` | "не отвечает", "низкий заряд" |
| `last_check` | `Optional[datetime]` | Последняя проверка |

#### SensorsVM
Датчики для отображения.

| Поле | Тип | Описание |
|------|-----|----------|
| `total` | `int` | Всего датчиков |
| `active` | `int` | Активных |
| `inactive` | `int` | Неактивных |
| `maintenance` | `int` | На обслуживании |
| `issues` | `List[SensorIssue]` | Проблемные |
| `active_ids` | `List[int]` | ID активных (для кликов) |
| `inactive_ids` | `List[int]` | ID неактивных |
| `maintenance_ids` | `List[int]` | ID на обслуживании |

---

### 4. События (`events.py`)

#### EventItem
Отдельное событие.

| Поле | Тип | Описание |
|------|-----|----------|
| `timestamp` | `datetime` | Время события |
| `type` | `str` | "Сработка", "ТО", "Ошибка" |
| `location` | `str` | "Корпус А, 3 этаж" |
| `description` | `str` | Описание |
| `is_critical` | `bool` | Критическое? |

#### EventsVM
События для отображения.

| Поле | Тип | Описание |
|------|-----|----------|
| `total` | `int` | Всего событий |
| `recent_events` | `List[EventItem]` | Недавние события |
| `all_events_link` | `bool` | Показывать ссылку "все события" |

---

### 5. Списки (`lists.py`)

Компактные представления сущностей для списков.

#### BuildingListItem

| Поле | Тип |
|------|-----|
| `id` | `int` |
| `name` | `str` |
| `floors_count` | `int` |

#### FloorListItem

| Поле | Тип |
|------|-----|
| `id` | `int` |
| `number` | `int` |
| `rooms_count` | `int` |

#### RoomListItem

| Поле | Тип |
|------|-----|
| `id` | `int` |
| `number` | `str` |
| `area` | `Optional[float]` |
| `status_code` | `Optional[str]` |

---

## Общие паттерны

### Метод `empty()`

Все основные VM имеют фабричный метод `empty()` для fallback-значений.

```python
empty_stats = ComplexStatisticsVM.empty()
```

### Иммутабельность

Все VM используют:
- `@dataclass(frozen=True, slots=True)` — неизменяемость + экономия памяти

---

## Зависимости

| Компонент | Зависит от |
|-----------|------------|
| Все VM | только стандартная библиотека |

**Нет зависимостей на:** `core`, `models`, `data`, `services`, `projections`, `controllers`, `ui`

---

## Итог

Слой предоставляет вышележащим слоям (контроллерам, UI):

| Категория | View Models |
|-----------|-------------|
| Статистика | `ComplexStatisticsVM`, `BuildingStatisticsVM`, `FloorStatisticsVM`, `RoomTypeStat` |
| Контакты | `ContactsVM`, `ContactGroup`, `ContactPerson`, `ContactSummary` |
| Датчики | `SensorsVM`, `SensorIssue` |
| События | `EventsVM`, `EventItem` |
| Списки | `BuildingListItem`, `FloorListItem`, `RoomListItem` |

**Принципы:**
- Только данные, никакой логики
- Иммутабельность (frozen)
- Компактные структуры, готовые для отображения
- Fallback через `empty()`