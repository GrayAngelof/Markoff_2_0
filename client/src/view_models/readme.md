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

## 📚 **ОПИСАНИЕ СЛОЯ VIEW MODELS**

В соответствии с архитектурой, View Models — это **слой контракта данных** между бизнес-логикой (контроллерами/проекциями) и пользовательским интерфейсом. Они определяют, какие данные и в каком формате UI получает для отображения, обеспечивая типобезопасность и изоляцию UI от структуры хранения данных.

Код организован в следующую структуру каталогов:

```
view_models/
├── __init__.py                    # Публичное API (экспорт всех View Models)
├── statistics.py                  # Статистика для вкладки "Физика"
├── contacts.py                    # Контакты для вкладки "Юрики"
├── sensors.py                     # Датчики для вкладки "Пожарка"
├── events.py                      # События для вкладки "Пожарка"
└── lists.py                       # Списки (корпусов, этажей, помещений)
```

---

## 📦 **Публичное API (минималистичный подход)**

View Models экспортируют **только структуры данных**. Все View Models — иммутабельные dataclass'ы:

```python
# Импорт View Models
from src.view_models import (
    # Статистика
    ComplexStatisticsVM, BuildingStatisticsVM, FloorStatisticsVM, RoomTypeStat,
    # Контакты
    ContactsVM, ContactGroup, ContactPerson, ContactSummary,
    # Датчики
    SensorsVM, SensorIssue,
    # События
    EventsVM, EventItem,
    # Списки
    BuildingListItem, FloorListItem, RoomListItem
)
```

---

## 🔹 **Общие принципы View Models**

| Принцип | Описание |
|---------|----------|
| **Иммутабельность** | Все View Models — `@dataclass(frozen=True, slots=True)` |
| **Отсутствие None** | Вместо None используются пустые значения или отдельные флаги |
| **Отсутствие логики** | Только поля-данные, никаких методов (кроме `empty()` фабрики) |
| **Доменная гранулярность** | Каждый домен (статистика, контакты, датчики, события) — отдельный View Model |
| **Явность** | Все поля имеют понятные имена и типы |
| **Минимализм** | Только то, что нужно UI сейчас (YAGNI) |

---

## 🔹 **StatisticsViewModel — статистика для вкладки "Физика"**

```python
from src.view_models import ComplexStatisticsVM, BuildingStatisticsVM, FloorStatisticsVM, RoomTypeStat
```

### **ComplexStatisticsVM (статистика комплекса)**

```python
@dataclass(frozen=True, slots=True)
class ComplexStatisticsVM:
    """Статистика для комплекса."""
    
    total_buildings: int = 0          # Всего корпусов
    total_floors: int = 0             # Всего этажей
    total_rooms: int = 0              # Всего помещений
    
    free_rooms: int = 0               # Свободные помещения
    occupied_rooms: int = 0           # Занятые помещения
    reserved_rooms: int = 0           # Зарезервированные помещения
    maintenance_rooms: int = 0        # Помещения на ремонте
    
    total_area: float = 0.0           # Общая площадь
    rentable_area: float = 0.0        # Сдаваемая площадь
    occupancy_rate: float = 0.0       # Процент занятости
    
    room_types: List[RoomTypeStat] = field(default_factory=list)  # Статистика по типам
    
    @classmethod
    def empty(cls) -> 'ComplexStatisticsVM':
        """Возвращает пустую статистику (для fallback)."""
        return cls()
```

### **BuildingStatisticsVM (статистика корпуса)**

```python
@dataclass(frozen=True, slots=True)
class BuildingStatisticsVM:
    """Статистика для корпуса."""
    
    total_floors: int = 0
    total_rooms: int = 0
    
    free_rooms: int = 0
    occupied_rooms: int = 0
    reserved_rooms: int = 0
    maintenance_rooms: int = 0
    
    total_area: float = 0.0
    occupancy_rate: float = 0.0
    
    @classmethod
    def empty(cls) -> 'BuildingStatisticsVM':
        return cls()
```

### **FloorStatisticsVM (статистика этажа)**

```python
@dataclass(frozen=True, slots=True)
class FloorStatisticsVM:
    """Статистика для этажа."""
    
    total_rooms: int = 0
    
    free_rooms: int = 0
    occupied_rooms: int = 0
    reserved_rooms: int = 0
    maintenance_rooms: int = 0
    
    room_types: List[RoomTypeStat] = field(default_factory=list)
    
    @classmethod
    def empty(cls) -> 'FloorStatisticsVM':
        return cls()
```

### **RoomTypeStat (статистика по типу помещения)**

```python
@dataclass(frozen=True, slots=True)
class RoomTypeStat:
    """Статистика по типу помещения."""
    
    type_name: str          # "Офисное", "Складское", "Торговое"
    count: int              # Количество
    area: float             # Общая площадь
```

---

## 🔹 **ContactsViewModel — контакты для вкладки "Юрики"**

```python
from src.view_models import ContactsVM, ContactGroup, ContactPerson, ContactSummary
```

### **ContactsVM (основной контейнер)**

```python
@dataclass(frozen=True, slots=True)
class ContactsVM:
    """Контакты для отображения."""
    
    total_organizations: int = 0       # Всего организаций
    tenants_count: int = 0             # Арендаторов
    owners_count: int = 0              # Собственников
    debtors_count: int = 0             # Должников
    
    groups: List[ContactGroup] = field(default_factory=list)   # Группы контактов
    summary: Optional[ContactSummary] = None                   # Сводка
    
    @classmethod
    def empty(cls) -> 'ContactsVM':
        return cls()
```

### **ContactGroup (группа контактов)**

```python
@dataclass(frozen=True, slots=True)
class ContactGroup:
    """Группа контактов по категории."""
    
    category: str                     # "Юридические вопросы", "Финансовые вопросы"
    contacts: List[ContactPerson] = field(default_factory=list)
```

### **ContactPerson (контактное лицо)**

```python
@dataclass(frozen=True, slots=True)
class ContactPerson:
    """Контактное лицо."""
    
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: bool = False
```

### **ContactSummary (сводка)**

```python
@dataclass(frozen=True, slots=True)
class ContactSummary:
    """Сводка для UI."""
    
    total_area: float = 0.0
    rented_area: float = 0.0
    occupancy_rate: float = 0.0
    total_debt: float = 0.0
```

---

## 🔹 **SensorsViewModel — датчики для вкладки "Пожарка"**

```python
from src.view_models import SensorsVM, SensorIssue
```

### **SensorsVM (датчики)**

```python
@dataclass(frozen=True, slots=True)
class SensorsVM:
    """Датчики для отображения."""
    
    total: int = 0                    # Всего датчиков
    active: int = 0                   # Активные
    inactive: int = 0                 # Неактивные
    maintenance: int = 0              # На обслуживании
    
    issues: List[SensorIssue] = field(default_factory=list)   # Проблемные датчики
    
    # ID для кликабельности
    active_ids: List[int] = field(default_factory=list)
    inactive_ids: List[int] = field(default_factory=list)
    maintenance_ids: List[int] = field(default_factory=list)
    
    @classmethod
    def empty(cls) -> 'SensorsVM':
        return cls()
```

### **SensorIssue (проблемный датчик)**

```python
@dataclass(frozen=True, slots=True)
class SensorIssue:
    """Проблемный датчик."""
    
    sensor_id: int
    location: str                     # "пом. 203"
    issue: str                        # "не отвечает", "низкий заряд"
    last_check: datetime
```

---

## 🔹 **EventsViewModel — события для вкладки "Пожарка"**

```python
from src.view_models import EventsVM, EventItem
```

### **EventsVM (события)**

```python
@dataclass(frozen=True, slots=True)
class EventsVM:
    """События для отображения."""
    
    total: int = 0                    # Всего событий
    recent_events: List[EventItem] = field(default_factory=list)   # Последние 3-5 событий
    all_events_link: bool = True      # Показывать ссылку "все события"
    
    @classmethod
    def empty(cls) -> 'EventsVM':
        return cls()
```

### **EventItem (отдельное событие)**

```python
@dataclass(frozen=True, slots=True)
class EventItem:
    """Отдельное событие."""
    
    timestamp: datetime
    type: str                         # "Сработка", "ТО", "Тест"
    location: str                     # "Корпус А, 3 этаж"
    description: str
    is_critical: bool = False
```

---

## 🔹 **ListsViewModel — списки для диалогов**

```python
from src.view_models import BuildingListItem, FloorListItem, RoomListItem
```

### **BuildingListItem (элемент списка корпусов)**

```python
@dataclass(frozen=True, slots=True)
class BuildingListItem:
    """Элемент списка корпусов."""
    
    id: int
    name: str
    floors_count: int
```

### **FloorListItem (элемент списка этажей)**

```python
@dataclass(frozen=True, slots=True)
class FloorListItem:
    """Элемент списка этажей."""
    
    id: int
    number: int
    rooms_count: int
```

### **RoomListItem (элемент списка помещений)**

```python
@dataclass(frozen=True, slots=True)
class RoomListItem:
    """Элемент списка помещений."""
    
    id: int
    number: str
    area: Optional[float] = None
    status_code: Optional[str] = None
```

---

## 🔹 **Фабричные методы `empty()`**

Каждый View Model имеет фабричный метод `empty()`, который возвращает экземпляр с нулевыми/пустыми значениями:

```python
# В проекции при ошибке
try:
    stats = self._calculate_complex_stats(complex_id)
except Exception as e:
    log.error(f"Ошибка расчета статистики: {e}")
    return ComplexStatisticsVM.empty()  # не None!
```

**Это гарантирует, что UI никогда не получает None.**

---

## 🔹 **Ключевые архитектурные решения**

| Решение | Обоснование |
|---------|-------------|
| **Иммутабельность (`frozen=True`)** | Нельзя случайно изменить данные после создания |
| **Экономия памяти (`slots=True`)** | Нет `__dict__` у каждого экземпляра |
| **Отсутствие None** | UI не проверяет на None, просто отображает нули |
| **Отсутствие логики** | Форматирование и бизнес-логика — в других слоях |
| **Доменная гранулярность** | Каждый домен обновляется независимо |
| **Фабрика `empty()`** | Единый способ создания пустых View Models |
| **ID для кликабельности** | UI знает, что запросить при клике на карточку |

---

## 🔹 **Поток данных**

```
[DataLoader] → загружает данные → сохраняет в EntityGraph
                                    ↓
[DetailsController] → получает NodeSelected
                                    ↓
[DetailsController] → вызывает StatisticsProjection.build_for_complex()
                                    ↓
[StatisticsProjection] → читает из репозиториев
                                    ↓
[StatisticsProjection] → возвращает ComplexStatisticsVM
                                    ↓
[DetailsController] → эмитит StatisticsUpdated(ComplexStatisticsVM)
                                    ↓
[UI] → получает StatisticsUpdated → отображает
```

---

## 🚫 **Что НЕЛЬЗЯ делать с View Models**

| Действие | Почему |
|----------|--------|
| **Добавлять бизнес-логику** | Только данные, методы только для фабрики `empty()` |
| **Возвращать None вместо View Model** | Всегда возвращаем View Model с нулями |
| **Хранить ссылки на модели данных** | Только примитивы и другие View Models |
| **Создавать циклические ссылки** | ComplexStatisticsVM не ссылается на BuildingStatisticsVM |
| **Добавлять поля "на всякий случай"** | Только то, что нужно UI сейчас |
| **Менять View Models без обновления UI** | View Model — это контракт |

---

## 📊 **Чек-лист: что есть в View Models**

| Компонент | Статус |
|-----------|--------|
| **Statistics** | ✅ Спроектирован |
| `ComplexStatisticsVM` | ✅ |
| `BuildingStatisticsVM` | ✅ |
| `FloorStatisticsVM` | ✅ |
| `RoomTypeStat` | ✅ |
| **Contacts** | ✅ Спроектирован |
| `ContactsVM` | ✅ |
| `ContactGroup` | ✅ |
| `ContactPerson` | ✅ |
| `ContactSummary` | ✅ |
| **Sensors** | ✅ Спроектирован |
| `SensorsVM` | ✅ |
| `SensorIssue` | ✅ |
| **Events** | ✅ Спроектирован |
| `EventsVM` | ✅ |
| `EventItem` | ✅ |
| **Lists** | ✅ Спроектирован |
| `BuildingListItem` | ✅ |
| `FloorListItem` | ✅ |
| `RoomListItem` | ✅ |

---

## 💡 **Итог**

Слой View Models спроектирован так, чтобы быть:

- **Типобезопасным** — все поля типизированы, IDE подсказывает
- **Иммутабельным** — `frozen=True` гарантирует неизменность
- **Минималистичным** — только то, что нужно UI
- **Предсказуемым** — всегда возвращаем View Model, даже при ошибке
- **Расширяемым** — легко добавить новые поля

**Любой контроллер может создавать View Models:**
```python
from src.view_models import ComplexStatisticsVM

stats = ComplexStatisticsVM(
    total_buildings=4,
    total_floors=14,
    total_rooms=245,
    free_rooms=89,
    occupied_rooms=132,
    total_area=12450.0,
    occupancy_rate=72.0,
    room_types=[
        RoomTypeStat("Офисные", 150, 8000.0),
        RoomTypeStat("Складские", 50, 3000.0)
    ]
)

self._bus.emit(StatisticsUpdated(stats))
```

**UI получает готовые данные для отображения.** 🚀