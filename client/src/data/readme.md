## 📚 **СПЕЦИФИКАЦИЯ: DATA (СЛОЙ ДАННЫХ)**

```python
# ============================================
# СПЕЦИФИКАЦИЯ: DATA (СЛОЙ ДАННЫХ)
# ============================================

## 1. НАЗНАЧЕНИЕ
Data слой — это единый источник правды о состоянии данных в приложении. Он отвечает за хранение, индексацию, кэширование и доступ к сущностям, полученным от API, обеспечивая быстрый доступ по ID и связям, а также отслеживая актуальность загруженных данных. Слой данных не знает, откуда пришли данные — он только хранит их и предоставляет интерфейс для доступа.

## 2. ГДЕ ЛЕЖИТ
`client/src/data/`

## 3. ЗА ЧТО ОТВЕЧАЕТ
✅ **Отвечает за:**
- **Хранение сущностей:** Централизованное хранение всех загруженных объектов в памяти
- **Кэширование данных:** Все загруженные сущности хранятся и переиспользуются без повторных запросов
- **Индексацию связей:** Быстрый доступ к связям "родитель-потомок" (O(1))
- **Валидность данных:** Отслеживание, какие данные актуальны, а какие требуют перезагрузки
- **Инвалидацию кэша:** Точечное или веточное удаление устаревших данных
- **CRUD операции:** Базовые операции для каждого типа сущностей
- **Навигацию по графу:** Получение детей, родителей, предков
- **Потокобезопасность:** Корректная работа в многопоточной среде
- **Статистику использования:** Отслеживание попаданий/промахов, размера хранилища, эффективности кэша

❌ **НЕ отвечает за:**
- Загрузку данных из API (это `services/api_client`)
- Бизнес-логику (это `services` и `controllers`)
- Форматирование для UI (это `ui/formatters`)
- Валидацию бизнес-правил (это `services`)
- Кэширование на диске (только in-memory)
- HTTP-кэширование (это `api_client`)
- Логику обновления данных (только хранение и инвалидация)

## 4. КТО ИСПОЛЬЗУЕТ
✅ **Потребители (вызывают):**
- `services` — через репозитории для получения/сохранения данных
- `controllers` — через сервисы (косвенно)
- `projections` — для построения структур отображения

✅ **Зависимости (вызывает сам):**
- `core` — типы узлов (NodeType), правила иерархии, исключения
- `models` — DTO сущностей (Complex, Building и т.д.)
- `shared` — утилиты сравнения (has_changed), валидации, таймеры
- `utils.logger` — логирование операций

## 5. КЛЮЧЕВЫЕ ПОНЯТИЯ
- **EntityGraph** — фасад, объединяющий хранилище, индексы связей и валидность. Главная точка доступа к данным.
- **EntityStore** — простое хранилище объектов по типам и ID. Только put/get/remove.
- **RelationIndex** — индексы связей между сущностями (кто чей ребенок, кто родитель).
- **ValidityIndex** — отслеживание актуальности данных (какие сущности валидны, какие устарели).
- **Кэш (Cache)** — механизм переиспользования ранее загруженных данных для повышения производительности.
- **Репозиторий** — интерфейс доступа к сущностям конкретного типа. Предоставляет CRUD + навигацию.
- **Ленивая загрузка** — получение только ID детей без самих объектов (для дерева).
- **Инвалидация** — пометка данных как устаревших для последующей перезагрузки.
- **Валидность** — состояние данных, при котором они считаются актуальными и могут использоваться.
- **Попадание (hit)** — случай, когда запрошенные данные есть в кэше.
- **Промах (miss)** — случай, когда запрошенных данных нет в кэше.
- **Потокобезопасность** — гарантия корректной работы при одновременном доступе из нескольких потоков.

## 6. ОГРАНИЧЕНИЯ (важно!)
⛔ **НЕЛЬЗЯ:**
- Хранить бизнес-логику в репозиториях
- Создавать циклические зависимости между репозиториями
- Использовать репозитории для сложных запросов с агрегацией (это в сервисы)
- Хранить состояние вне графа (никаких отдельных кэшей в других слоях)
- Нарушать потокобезопасность (все операции под RLock)
- Добавлять логику форматирования или отображения
- Импортировать внутренности графа напрямую (store, relations, validity)
- Возвращать сырые данные из репозиториев — только DTO модели
- Держать ссылки на объекты дольше, чем нужно (чтобы не мешать GC)
- Игнорировать валидность данных — всегда проверять перед использованием
- Допускать утечки памяти — своевременно инвалидировать устаревшее

✅ **МОЖНО:**
- Добавлять новые репозитории под новые типы сущностей
- Расширять методы навигации (get_children, get_parent, get_ancestors)
- Добавлять индексы для новых типов связей
- Оптимизировать производительность доступа
- Мониторить эффективность кэша через статистику
- Добавлять новые методы валидности (по времени, по событиям)
- Инвалидировать только устаревшие данные (ветками или точечно)
- Использовать статистику для анализа эффективности

## 7. ПРИМЕРЫ

### Получение данных с проверкой кэша:
```python
from data import ComplexRepository
from shared.validation import validate_positive_int

# Валидация входных данных
complex_id = validate_positive_int(user_input, "complex_id")

# Проверяем кэш
complex = complex_repo.get(complex_id)
if not complex:
    # Промах — нет в кэше, грузим через сервис
    complex = loader.load_complex(complex_id)
    complex_repo.add(complex)  # сохраняем в кэш
else:
    # Попадание — данные уже в кэше
    logger.debug(f"Комплекс {complex_id} получен из кэша")
```

### Навигация по связям с ленивой загрузкой:
```python
# Получаем только ID детей из кэша (быстро)
building_ids = complex_repo.get_building_ids(complex_id)

# Сами здания загружаются лениво — только когда нужны
for building_id in building_ids[:10]:
    building = building_repo.get(building_id)
    if not building:
        building = loader.load_building(building_id)
        building_repo.add(building)
```

### Проверка валидности и инвалидация:
```python
# Проверяем, актуальны ли данные
if not graph.is_valid(NodeType.BUILDING, building_id):
    # Данные устарели — перезагружаем
    building = loader.reload_building(building_id)
    # После перезагрузки валидность восстанавливается

# Принудительная инвалидация ветки (например, после обновления на сервере)
graph.invalidate_branch(NodeType.COMPLEX, 42)
# Все данные комплекса и его детей помечены как устаревшие
```

### Сохранение новых данных в кэш:
```python
# После загрузки из API
new_building = Building.from_dict(api_response)
building_repo.add(new_building)  # автоматически обновляет индексы и валидность
```

### Мониторинг эффективности кэша:
```python
stats = graph.get_stats()
logger.info(f"📊 Статистика кэша:")
logger.info(f"  • Всего сущностей: {stats['total_entities']}")
logger.info(f"  • По типам: {stats['by_type']}")
logger.info(f"  • Попаданий: {stats['hits']}")
logger.info(f"  • Промахов: {stats['misses']}")
logger.info(f"  • Hit rate: {stats['hit_rate']}")
logger.info(f"  • Инвалидаций: {stats['invalidations']}")
```

### Работа с валидностью при массовых операциях:
```python
# Получаем только валидные данные
valid_buildings = [
    building_repo.get(id) 
    for id in building_ids 
    if graph.is_valid(NodeType.BUILDING, id)
]

# Для невалидных — планируем перезагрузку
invalid_ids = [
    id for id in building_ids 
    if not graph.is_valid(NodeType.BUILDING, id)
]
if invalid_ids:
    loader.reload_buildings(invalid_ids)
```

## 8. РИСКИ

🔴 **Критические:**
- **Потеря потокобезопасности** — может привести к повреждению данных. Решение: RLock на всех операциях.
- **Утечки памяти** — при неправильном управлении кэшем. Решение: механизмы инвалидации и возможность очистки.
- **Нарушение инкапсуляции** — прямой доступ к графу из сервисов. Решение: строгий доступ только через репозитории.
- **Неактуальные данные в кэше** — если вовремя не инвалидировать. Решение: ValidityIndex и события об изменениях.

🟡 **Средние:**
- **Разрастание репозиториев** — добавление методов с бизнес-логикой. Решение: код-ревью и следование SRP.
- **Неэффективные запросы** — при отсутствии нужных индексов. Решение: анализ паттернов доступа.
- **Дублирование данных** — если появятся дополнительные кэши вне графа. Решение: единый источник правды.
- **Снижение hit rate** — если кэш часто сбрасывается. Решение: анализ причин инвалидации.
- **Рост времени инвалидации** — при каскадном удалении больших веток. Решение: оптимизация индексов.

🟢 **Контролируемые:**
- **Рост объема данных в памяти** — мониторинг через stats, при необходимости LRU.
- **Добавление новых типов** — требует расширения всех индексов и репозиториев.
- **Сложность отладки** — много внутренних компонентов. Решение: подробное логирование.
- **Холодный старт** — первые запросы всегда промахи. Решение: предзагрузка видимого.

============================================
КОНЕЦ СПЕЦИФИКАЦИИ
============================================
```

## 📚 **Документация Data слоя — итоговая версия**

---

## 🎯 **Назначение Data слоя**

Data слой — это **единый источник правды** для всех данных в приложении. Он отвечает за хранение, кэширование, индексацию связей и отслеживание валидности всех загруженных сущностей.

**Главная идея:** Все данные загружаются один раз, сохраняются в граф, и далее используются из кэша. При изменении данных на сервере происходит инвалидация, и данные перезагружаются.


СТРУКТУРА
text
client/src/data/
├── __init__.py                 # Публичное API
│   └── EntityGraph, EntityGraphStats
│
├── entity_graph.py             # ФАСАД (главный класс)
│
├── utils/
│   ├── __init__.py
│   └── comparison.py           # has_changed(), is_equal()
│
├── graph/                      # ВНУТРЕННОСТИ (НЕ ИСПОЛЬЗОВАТЬ!)
│   ├── schema.py               # Правила связей (PARENT_ID_FIELD)
│   ├── store.py                # Хранилище объектов
│   ├── relations.py            # Индексы связей родитель-потомок
│   └── validity.py             # Отслеживание валидности
│
└── repositories/               # РЕПОЗИТОРИИ (следующий шаг)
    ├── __init__.py
    ├── base.py
    ├── complex.py
    ├── building.py
    ├── floor.py
    ├── room.py
    ├── counterparty.py
    └── responsible_person.py


---

## 🏗️ **Что внутри Data слоя**

### **Ядро — EntityGraph (фасад)**

```python
from data import EntityGraph

graph = EntityGraph()
```

`EntityGraph` — это **главный вход** в Data слой. Он объединяет три внутренних компонента:

| Компонент | Назначение | Публичный доступ |
|-----------|------------|------------------|
| `EntityStore` | Хранение объектов по типу и ID | ❌ только через EntityGraph |
| `RelationIndex` | Индексы связей родитель-потомок | ❌ только через EntityGraph |
| `ValidityIndex` | Отслеживание валидности данных | ❌ только через EntityGraph |

**Важно:** Никто не должен импортировать внутренности графа напрямую!

---

## 📦 **Публичное API Data слоя**

### **1. EntityGraph — фасад графа**

```python
from data import EntityGraph

graph = EntityGraph()
```

#### **Основные операции**

| Метод | Описание | Возврат |
|-------|----------|---------|
| `add_or_update(entity)` | Сохранить или обновить сущность | `bool` (изменилось ли) |
| `get(node_type, id)` | Получить сущность из кэша | `Optional[Any]` |
| `get_all(node_type)` | Все сущности типа | `List[Any]` |
| `get_all_ids(node_type)` | Все ID сущностей типа | `List[int]` |
| `has_entity(node_type, id)` | Проверить наличие | `bool` |
| `remove(node_type, id, cascade)` | Удалить сущность | `bool` |

#### **Навигация по графу**

| Метод | Описание | Возврат |
|-------|----------|---------|
| `get_children(parent_type, parent_id)` | ID всех детей | `List[int]` |
| `get_parent(child_type, child_id)` | Родитель | `Optional[NodeIdentifier]` |
| `get_ancestors(node_type, node_id)` | Все предки | `List[NodeIdentifier]` |

#### **Управление валидностью**

| Метод | Описание | Возврат |
|-------|----------|---------|
| `is_valid(node_type, id)` | Проверить актуальность | `bool` |
| `invalidate(node_type, id)` | Пометить как невалидный | `bool` |
| `invalidate_branch(node_type, id)` | Инвалидировать ветку | `int` (количество) |
| `validate(node_type, id)` | Пометить как валидный | `None` |

#### **Bulk-операции**

| Метод | Описание | Возврат |
|-------|----------|---------|
| `validate_bulk(node_type, ids)` | Пометить множество как валидные | `int` |
| `invalidate_bulk(node_type, ids)` | Пометить множество как невалидные | `int` |

#### **Управление**

| Метод | Описание |
|-------|----------|
| `clear()` | Полная очистка графа |
| `get_stats()` | Статистика использования |
| `print_stats()` | Вывод статистики в консоль |
| `check_consistency()` | Проверка консистентности индексов |

#### **Временные метки**

| Метод | Описание |
|-------|----------|
| `get_timestamp(node_type, id)` | Время последнего обновления |

---

### **2. Репозитории — удобный доступ к сущностям**

```python
from data.repositories import (
    ComplexRepository,
    BuildingRepository,
    FloorRepository,
    RoomRepository,
    CounterpartyRepository,
    ResponsiblePersonRepository,
)

complex_repo = ComplexRepository(graph)
```

#### **Базовый интерфейс (BaseRepository)**

| Метод | Описание | Возврат |
|-------|----------|---------|
| `get(id)` | Получить сущность | `Optional[T]` |
| `get_all()` | Все сущности типа | `List[T]` |
| `add(entity)` | Сохранить сущность | `None` |
| `remove(id)` | Удалить сущность | `bool` |
| `exists(id)` | Проверить наличие | `bool` |
| `is_valid(id)` | Проверить валидность | `bool` |
| `invalidate(id)` | Пометить как невалидный | `bool` |

#### **Специализированные методы**

**ComplexRepository**
```python
repo.get_building_ids(complex_id)      # ID всех корпусов
repo.get_by_owner(owner_id)            # комплексы по владельцу
repo.find_by_name(name_part)           # поиск по названию
```

**BuildingRepository**
```python
repo.get_floor_ids(building_id)        # ID всех этажей
repo.get_by_complex(complex_id)        # все корпуса комплекса
repo.get_by_owner(owner_id)            # корпуса по владельцу
```

**FloorRepository**
```python
repo.get_room_ids(floor_id)            # ID всех помещений
repo.get_by_building(building_id)      # все этажи корпуса
repo.get_sorted_by_number(building_id) # этажи по порядку
```

**RoomRepository**
```python
repo.get_by_floor(floor_id)            # все помещения этажа
repo.get_by_status(status_code)        # помещения по статусу
repo.find_by_number(number_part)       # поиск по номеру
```

**CounterpartyRepository**
```python
repo.get_person_ids(counterparty_id)   # ID ответственных лиц
repo.get_by_tax_id(tax_id)             # поиск по ИНН
repo.get_active()                      # только активные
```

**ResponsiblePersonRepository**
```python
repo.get_by_counterparty(counterparty_id)      # все контакты контрагента
repo.get_active_by_counterparty(counterparty_id) # только активные
repo.get_by_category(category)                 # по категории
```

---

## 🔄 **Типичный сценарий использования**

### **Сценарий 1: Загрузка данных из API**

```python
from data import EntityGraph
from data.repositories import ComplexRepository

graph = EntityGraph()
complex_repo = ComplexRepository(graph)

# Загрузка из API
complexes = api.get_complexes()

# Сохранение в кэш
for complex_obj in complexes:
    graph.add_or_update(complex_obj)  # или complex_repo.add(complex_obj)

# Проверка — теперь данные в кэше
cached = complex_repo.get(42)
assert cached is not None
```

### **Сценарий 2: Раскрытие узла в дереве**

```python
# В TreeController при раскрытии комплекса
def on_node_expanded(self, node_type, node_id):
    if node_type == NodeType.COMPLEX:
        # Проверяем кэш
        building_ids = complex_repo.get_building_ids(node_id)
        
        if not building_ids:
            # Нет в кэше — грузим
            buildings = loader.load_buildings(node_id)
            for building in buildings:
                building_repo.add(building)
        else:
            # Есть в кэше — используем
            log.cache(f"Найдено {len(building_ids)} корпусов в кэше")
```

### **Сценарий 3: Обновление данных (F5)**

```python
# В RefreshController
def refresh_current(self, node_type, node_id):
    # Инвалидируем всю ветку
    count = graph.invalidate_branch(node_type, node_id)
    log.info(f"Инвалидировано {count} сущностей")
    
    # Перезагружаем
    if node_type == NodeType.COMPLEX:
        complexes = loader.load_complexes()
        for complex_obj in complexes:
            complex_repo.add(complex_obj)
    else:
        details = loader.load_details(node_type, node_id)
        if details:
            graph.add_or_update(details)
```

### **Сценарий 4: Получение контекста для UI**

```python
# В TreeController для отображения иерархии
def get_selected_node_context(self, node_type, node_id):
    context = {}
    
    # Получаем всех предков
    ancestors = graph.get_ancestors(node_type, node_id)
    
    for anc in ancestors:
        if anc.node_type == NodeType.COMPLEX:
            complex_obj = complex_repo.get(anc.node_id)
            context['complex_name'] = complex_obj.name
        elif anc.node_type == NodeType.BUILDING:
            building_obj = building_repo.get(anc.node_id)
            context['building_name'] = building_obj.name
    
    return context
```

---

## 📊 **Статистика и отладка**

```python
# Получить полную статистику
stats = graph.get_stats()

print(f"Всего сущностей: {stats['total_entities']}")
print(f"Валидных: {stats['valid_count']}")
print(f"Комплексов: {stats['store']['by_type']['complex']}")
print(f"Связей родителей: {stats['relations']['parent_entries']}")

# Вывести красиво в консоль
graph.print_stats()

# Проверить консистентность (на случай багов)
result = graph.check_consistency()
if not result['consistent']:
    for issue in result['issues']:
        log.error(issue)
```

---

## 🎯 **Ключевые принципы работы**

### **1. Кэширование**
- Данные сохраняются в граф при первом запросе
- Повторные запросы возвращают данные из кэша (попадание)
- Эффективность: O(1) доступ, hit rate можно мониторить

### **2. Валидность**
- Новые данные помечаются как валидные
- При обновлении на сервере — инвалидация
- Проверка `is_valid()` перед использованием

### **3. Инвалидация**
- Точечная: `invalidate(type, id)`
- Веточная: `invalidate_branch(type, id)` — удаляет весь подграф
- Полная: `clear()`

### **4. Навигация**
- `get_children()` — быстрый доступ к ID детей
- `get_parent()` — быстрый доступ к родителю
- `get_ancestors()` — полный путь вверх по иерархии

### **5. Потокобезопасность**
- Все операции под RLock
- Можно вызывать из любых потоков

---

## ✅ **Чек-лист: что готово**

| Компонент | Статус |
|-----------|--------|
| `EntityGraph` — фасад | ✅ |
| `EntityStore` — хранение | ✅ |
| `RelationIndex` — связи | ✅ |
| `ValidityIndex` — валидность | ✅ |
| `ComplexRepository` | ✅ |
| `BuildingRepository` | ✅ |
| `FloorRepository` | ✅ |
| `RoomRepository` | ✅ |
| `CounterpartyRepository` | ✅ |
| `ResponsiblePersonRepository` | ✅ |
| `has_changed` утилита | ✅ |
| `get_stats` с TypedDict | ✅ |
| `check_consistency` | ✅ |
| Все `__init__.py` | ✅ |
| Полная типизация | ✅ |
| Потокобезопасность | ✅ |
| Логирование | ✅ |

---

## 🚀 **Готов к использованию в сервисах!**