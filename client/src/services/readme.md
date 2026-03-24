## 📚 **СПЕЦИФИКАЦИЯ: SERVICES (СЛОЙ СЕРВИСОВ)**

# ============================================
# СПЕЦИФИКАЦИЯ: SERVICES (СЛОЙ СЕРВИСОВ)
# ============================================

## 1. НАЗНАЧЕНИЕ
Сервисный слой — это тонкий слой оркестрации, который координирует загрузку данных 
из API, их сохранение в Data слой и мониторинг состояния соединения. Сервисы 
не хранят состояние, не содержат бизнес-логики и не знают о существовании UI.

## 2. ГДЕ ЛЕЖИТ
`client/src/services/`

## 3. ЗА ЧТО ОТВЕЧАЕТ

✅ **ApiClient:**
- Выполнение HTTP запросов к бэкенду (GET, POST, PUT, DELETE)
- Преобразование JSON ответов в DTO модели (Complex, Building и т.д.)
- Единая обработка ошибок (404, 500, таймауты, соединение)
- Логирование всех запросов через `log.api()`
- Проверка доступности сервера (`check_connection`)

✅ **DataLoader (фасад):**
- Координация процесса загрузки данных
- Проверка наличия данных в Data слое перед запросом к API
- Ленивая загрузка связанных данных (владельцы, контакты)
- Инвалидация и перезагрузка устаревших данных
- Предоставление единого интерфейса для контроллеров

✅ **NodeLoader (внутренний):**
- Реализация логики загрузки для каждого типа сущностей
- Преобразование API ответов в модели
- Сохранение моделей в EntityGraph
- Загрузка владельцев и ответственных лиц по требованию

✅ **ConnectionService:**
- Периодическая проверка доступности сервера
- Генерация событий при изменении статуса соединения
- Возможность принудительной проверки

## 4. КТО ИСПОЛЬЗУЕТ

✅ **Потребители (вызывают):**
- `controllers` — для загрузки данных по запросу пользователя
- `projections` — для получения данных при построении структур

✅ **Зависимости (вызывает сам):**
- `core` — типы (NodeType), события (SystemEvents), утилиты (has_changed)
- `models` — DTO сущности (Complex, Building, Counterparty и т.д.)
- `data` — EntityGraph, репозитории

## 5. КЛЮЧЕВЫЕ ПОНЯТИЯ

- **ApiClient** — единственный компонент, знающий о HTTP. Инкапсулирует все запросы.
- **DataLoader** — фасад, скрывающий сложность загрузки (проверка кэша, ленивая загрузка)
- **NodeLoader** — ядро загрузки. Знает, какие API методы вызывать для каждого типа.
- **Ленивая загрузка** — данные загружаются только когда реально нужны (при раскрытии узла)
- **Проверка кэша** — перед каждым API запросом проверяется наличие данных в EntityGraph
- **Попадание (hit)** — данные найдены в кэше, API запрос не выполняется
- **Промах (miss)** — данных нет в кэше, выполняется API запрос

## 6. ОГРАНИЧЕНИЯ (ВАЖНО!)

⛔ **НЕЛЬЗЯ:**
- Хранить данные в сервисах (все данные только в EntityGraph)
- Подписываться на UI события в сервисах (это работа контроллеров)
- Импортировать `controllers` или `ui` из сервисов
- Использовать `print()` вместо логгера
- Создавать методы форматирования для UI
- Дублировать методы ApiClient в DataLoader
- Использовать магические строки (только константы из core)
- Мутировать объекты (модели иммутабельны)

✅ **МОЖНО:**
- Создавать временные кэши для загрузки (например, owner_id → owner)
- Использовать `log.api()`, `log.cache()`, `log.data()`, `log.success()`
- Генерировать системные события (DATA_LOADING, DATA_LOADED, DATA_ERROR)
- Вызывать методы EntityGraph и репозиториев
- Добавлять новые методы загрузки под новые типы сущностей

## 7. ПРИМЕРЫ (концептуально)

### ApiClient:
```python
# В контроллере
from src.services import ApiClient

api = ApiClient()
complexes = api.get_complexes()  # List[Complex]
building = api.get_building_detail(101)  # Optional[Building]
owner = api.get_counterparty(42)  # Optional[Counterparty]
```

### DataLoader:
```python
# В контроллере
from src.services import DataLoader

loader = DataLoader(event_bus, api_client, graph)

# Проверяет кэш, если нет — загружает
complexes = loader.load_complexes()

# Ленивая загрузка детей (с проверкой кэша)
buildings = loader.load_children(NodeType.COMPLEX, 42, NodeType.BUILDING)

# Загрузка деталей (с проверкой полноты)
details = loader.load_details(NodeType.BUILDING, 101)

# Получение связанных данных
owner = loader.get_owner_for_building(building)

# Перезагрузка
loader.reload_node(NodeType.BUILDING, 101)
loader.reload_branch(NodeType.COMPLEX, 42)
```

### ConnectionService:
```python
# В main.py
from src.services import ConnectionService

service = ConnectionService(event_bus, api_client)
service.start()  # начинает периодическую проверку

# При изменении статуса генерируется SystemEvents.CONNECTION_CHANGED
```

## 8. РИСКИ

🔴 **Критические:**
- **Дублирование кэша** — если сервис начнет хранить свои данные. Решение: строго использовать EntityGraph.
- **Нарушение иерархии** — если сервис импортирует controllers или ui. Решение: code-review.
- **Утечка памяти** — если хранить ссылки на объекты дольше нужного. Решение: только временные кэши.

🟡 **Средние:**
- **Снижение hit rate** — если кэш часто инвалидируется. Решение: анализ статистики.
- **Медленные запросы** — если ApiClient не использует сессию. Решение: requests.Session().

🟢 **Контролируемые:**
- **Сложность отладки** — много уровней вызовов. Решение: подробное логирование через категории.

## 9. ЧТО ВХОДИТ В СОСТАВ

| Компонент | Тип | Ответственность |
|-----------|-----|-----------------|
| `ApiClient` | Публичный | HTTP запросы, преобразование в модели |
| `DataLoader` | Публичный (фасад) | Оркестрация загрузки, проверка кэша |
| `NodeLoader` | Приватный | Ядро загрузки (внутри loading/) |
| `LoaderUtils` | Приватный | Утилиты (проверка деталей) |
| `ConnectionService` | Публичный | Мониторинг соединения |

## 10. ЧТО НЕ ВХОДИТ В СОСТАВ

| Компонент | Почему |
|-----------|--------|
| Обработчики UI событий | Это ответственность контроллеров |
| Форматтеры для отображения | Это ответственность UI |
| Бизнес-логика | Это ответственность контроллеров |
| Хранение данных | Это ответственность Data слоя |

============================================
КОНЕЦ СПЕЦИФИКАЦИИ
============================================
```


## 📚 **СЛОЙ SERVICES: ПОЛНОЕ ОПИСАНИЕ**

---

## 1. **НАЗНАЧЕНИЕ И МЕСТО В АРХИТЕКТУРЕ**

Сервисный слой — это **тонкая прослойка оркестрации**, расположенная между слоем данных (`data`) и слоем контроллеров (`controllers`). Он содержит **бизнес-логику загрузки данных** (например, "если у корпуса есть владелец, загрузить его и его ответственных лиц"), но не хранит состояние и не знает о существовании UI.

### **Место в иерархии**
```
controllers (координация потока данных)
      ↓
services (бизнес-логика загрузки, оркестрация) ←────┐
      ↓                                             │
data (хранение, навигация, валидность)              │
      ↓                                             │
models (структуры данных)                           │
      ↓                                             │
core (типы, события, исключения) ───────────────────┘
```

**Ключевое правило:** Services может импортировать `core`, `models`, `data`, но НЕ может импортировать `controllers` и `ui`.

---

## 2. **СТРУКТУРА СЛОЯ**

```
services/
├── __init__.py                 # Публичное API
├── api_client.py               # ФАСАД HTTP клиента
├── data_loader.py              # ФАСАД загрузки данных
├── connection.py               # Сервис мониторинга соединения
├── context_service.py          # 🆕 Сервис контекста (имена родителей)
├── types.py                    # 🆕 Типизированные результаты (BuildingWithOwnerResult)
│
├── api/                        # ПРИВАТНО — детали HTTP
│   ├── __init__.py
│   ├── http_client.py          # Низкоуровневый HTTP (requests.Session)
│   ├── endpoints.py            # Константы эндпоинтов
│   ├── converters.py           # JSON → модели
│   └── errors.py               # Иерархия исключений
│
└── loading/                    # ПРИВАТНО — детали загрузки
    ├── __init__.py
    ├── node_loader.py          # Тупой исполнитель (физическая иерархия)
    ├── dictionary_loader.py    # Загрузчик справочников
    └── utils.py                # Вспомогательные функции
```

**Принцип:** Фасады на верхнем уровне, детали реализации — в приватных подпапках. Никто не импортирует из `api/` или `loading/` напрямую.

---

## 3. **КОМПОНЕНТЫ СЛОЯ**

### 3.1. **ApiClient (фасад HTTP)**

```python
from src.services import ApiClient

api = ApiClient(base_url="http://localhost:8000")
```

**Ответственность:**
- Выполнение HTTP запросов к бэкенду
- Преобразование JSON в модели (Complex, Building, Floor, Room, Counterparty, ResponsiblePerson)
- Единая обработка ошибок (404, 500, таймауты, соединение)
- Логирование всех запросов через `log.api()`
- Проверка доступности сервера (`check_connection`)

**Публичные методы:**

| Метод | Возврат | Описание |
|-------|---------|----------|
| `get_complexes()` | `List[Complex]` | Все комплексы |
| `get_buildings(complex_id)` | `List[Building]` | Корпуса комплекса |
| `get_floors(building_id)` | `List[Floor]` | Этажи корпуса |
| `get_rooms(floor_id)` | `List[Room]` | Помещения этажа |
| `get_complex_detail(complex_id)` | `Optional[Complex]` | Детали комплекса |
| `get_building_detail(building_id)` | `Optional[Building]` | Детали корпуса |
| `get_floor_detail(floor_id)` | `Optional[Floor]` | Детали этажа |
| `get_room_detail(room_id)` | `Optional[Room]` | Детали помещения |
| `get_counterparty(counterparty_id)` | `Optional[Counterparty]` | Контрагент |
| `get_responsible_persons(counterparty_id)` | `List[ResponsiblePerson]` | Ответственные лица |
| `check_connection()` | `bool` | Доступен ли сервер |
| `get_server_info()` | `dict` | Информация о сервере |

**Исключения (сохраняют traceback):**

| Исключение | Когда возникает |
|------------|-----------------|
| `ConnectionError` | Сервер недоступен |
| `TimeoutError` | Таймаут запроса |
| `NotFoundError` | 404 Not Found |
| `ClientError` | 4xx ошибки (кроме 404) |
| `ServerError` | 5xx ошибки |
| `ApiError` | Другие ошибки API |

---

### 3.2. **DataLoader (фасад загрузки)**

```python
from src.services import DataLoader

loader = DataLoader(bus, api, graph)
```

**Ответственность:**
- Координация процесса загрузки данных
- Проверка наличия данных в `EntityGraph` перед запросом к API
- Ленивая загрузка связанных данных
- **Бизнес-логика загрузки** (например, `load_building_with_owner()`)
- Инвалидация и перезагрузка устаревших данных
- Эмиссия событий (`DataLoading`, `DataLoaded`, `DataError`)
- Предоставление единого интерфейса для контроллеров

**Публичные методы:**

| Метод | Возврат | Описание |
|-------|---------|----------|
| `load_complexes()` | `List[Complex]` | Все комплексы (с проверкой кэша) |
| `load_children(parent_type, parent_id, child_type)` | `List[Any]` | Ленивая загрузка детей |
| `load_details(node_type, node_id)` | `Optional[Any]` | Детальная информация |
| `load_counterparty(counterparty_id)` | `Optional[Counterparty]` | Контрагент |
| `load_responsible_persons(counterparty_id)` | `List[ResponsiblePerson]` | Ответственные лица |
| **🆕** `load_building_with_owner(building_id)` | `Optional[BuildingWithOwnerResult]` | Корпус + владелец + контакты |
| `get_ancestors(node_type, node_id)` | `List[NodeIdentifier]` | Все предки узла |
| `reload_node(node_type, node_id)` | `None` | Перезагрузить узел |
| `reload_branch(node_type, node_id)` | `None` | Перезагрузить ветку |
| `clear_cache()` | `None` | Очистить кэш |
| `get_stats()` | `dict` | Статистика |
| `print_stats()` | `None` | Вывод статистики |

**Логика работы каждого метода:**

```python
def load_complexes(self) -> List[Complex]:
    # 1. Спросить граф: есть ли данные в кэше?
    cached = self._graph.get_all(NodeType.COMPLEX)
    if cached:
        log.cache(f"Complexes in cache: {len(cached)}")
        return cached  # попадание — возвращаем из кэша
    
    # 2. Промах — загружаем через API
    return self._with_events(
        NodeType.COMPLEX.value, 0,
        self._node_loader.load_complexes
    )
```

```python
def load_children(self, parent_type, parent_id, child_type):
    # 1. Спросить граф: есть ли ВСЕ дети в кэше?
    cached = self._graph.get_cached_children(parent_type, parent_id, child_type)
    if cached:
        log.cache(f"Children in cache: {len(cached)}")
        return cached
    
    # 2. Промах — загружаем через API
    return self._with_events(
        parent_type.value, parent_id,
        self._node_loader.load_children,
        parent_type, parent_id, child_type
    )
```

```python
def load_details(self, node_type, node_id):
    # 1. Спросить граф: есть ли данные И полные?
    cached = self._graph.get_if_full(node_type, node_id)
    if cached:
        log.cache(f"Full details in cache")
        return cached
    
    # 2. Промах — загружаем через API
    return self._with_events(
        node_type.value, node_id,
        self._node_loader.load_details,
        node_type, node_id
    )
```

```python
# 🆕 Бизнес-логика загрузки корпуса с владельцем
def load_building_with_owner(self, building_id: NodeID) -> Optional[BuildingWithOwnerResult]:
    """Загружает корпус, его владельца и ответственных лиц."""
    building = self.load_details(NodeType.BUILDING, building_id)
    if building is None:
        return None
    
    result = BuildingWithOwnerResult(building=building)
    
    if building.owner_id:
        owner = self.load_counterparty(building.owner_id)
        if owner:
            result = BuildingWithOwnerResult(
                building=building,
                owner=owner,
                responsible_persons=self.load_responsible_persons(owner.id)
            )
    
    return result
```

**Внутренний механизм `_with_events`:**

```python
def _with_events(self, node_type, node_id, fn, *args, **kwargs):
    # 1. Эмитим событие начала загрузки
    self._bus.emit(DataLoading(node_type=node_type, node_id=node_id))
    
    try:
        # 2. Выполняем загрузку
        result = fn(*args, **kwargs)
        
        # 3. Эмитим событие успеха
        count = len(result) if isinstance(result, list) else (1 if result else 0)
        self._bus.emit(DataLoaded(
            node_type=node_type,
            node_id=node_id,
            payload=result,
            count=count
        ))
        
        return result
        
    except Exception as e:
        # 4. Эмитим событие ошибки
        self._bus.emit(DataError(
            node_type=node_type,
            node_id=node_id,
            error=str(e)
        ))
        raise
```

---

### 3.3. **ContextService — 🆕 сервис контекста**

```python
from src.services import ContextService

context_service = ContextService(complex_repo, building_repo, floor_repo, counterparty_repo, loader)
```

**Ответственность:**
- Сбор имён родителей для отображения иерархии в UI
- Загрузка владельцев для комплексов и корпусов
- Формирование готового словаря для контроллеров

**Публичные методы:**

| Метод | Возврат | Описание |
|-------|---------|----------|
| `get_context(node)` | `Dict[str, Optional[str]]` | Имена родителей для узла |
| `get_building_context(building_id)` | `Dict[str, Optional[str]]` | Контекст для корпуса |

**Пример использования:**
```python
# В TreeController
context = self._context_service.get_context(node)
# context = {
#     'complex_name': 'Северный',
#     'building_name': 'Корпус А',
#     'floor_num': '5',
#     'owner_name': 'ООО Ромашка',
#     'complex_owner': 'ООО Строй'
# }
```

---

### 3.4. **🆕 Типизированные результаты (types.py)**

```python
# services/types.py
from dataclasses import dataclass, field
from typing import List, Optional
from models import Building, Counterparty, ResponsiblePerson

@dataclass(frozen=True, slots=True)
class BuildingWithOwnerResult:
    """Типизированный результат загрузки корпуса с владельцем."""
    building: Building
    owner: Optional[Counterparty] = None
    responsible_persons: List[ResponsiblePerson] = field(default_factory=list)
```

**Почему dataclass, а не dict:**
- Type-safe — IDE подсказывает поля
- Нет магических строк `result['building']`
- Легко расширять

---

### 3.5. **ConnectionService (мониторинг соединения)**

```python
from src.services import ConnectionService

service = ConnectionService(bus, api, interval_ms=300000)
service.start()  # запускает периодическую проверку
```

**Ответственность:**
- Периодическая проверка доступности сервера
- Генерация события `ConnectionChanged` при изменении статуса
- Возможность принудительной проверки
- Один поток на весь сервис (нет утечек)

**Публичные методы:**

| Метод | Описание |
|-------|----------|
| `start()` | Запускает периодическую проверку (один поток) |
| `stop()` | Останавливает проверку |
| `force_check()` | Принудительная проверка сейчас |

**Генерируемые события:**

```python
# При изменении статуса
self._bus.emit(ConnectionChanged(is_online=True))   # или False
```

---

### 3.6. **Приватные компоненты (внутренности)**

#### **NodeLoader — тупой исполнитель**

```python
# services/loading/node_loader.py

class NodeLoader:
    def __init__(self, api, graph, child_loaders, detail_loaders):
        # child_loaders: Dict[NodeType, Callable] — как загружать детей
        # detail_loaders: Dict[NodeType, Callable] — как загружать детали
```

**Принцип работы:** NodeLoader не знает о типах узлов. Вся конфигурация передаётся из DataLoader. Если появляется новый тип — не нужно менять NodeLoader, только добавить лоадер в словарь.

**Методы:**
- `load_complexes()` — загружает комплексы
- `load_buildings(complex_id)` — загружает корпуса
- `load_floors(building_id)` — загружает этажи
- `load_rooms(floor_id)` — загружает помещения
- `load_children(parent_type, parent_id, child_type)` — универсальная загрузка детей
- `load_details(node_type, node_id)` — универсальная загрузка деталей

#### **DictionaryLoader — загрузчик справочников**

```python
# services/loading/dictionary_loader.py

class DictionaryLoader:
    def load_counterparty(self, counterparty_id) -> Optional[Counterparty]
    def load_responsible_persons(self, counterparty_id) -> List[ResponsiblePerson]
```

#### **LoaderUtils — утилиты**

```python
# services/loading/utils.py

class LoaderUtils:
    def has_details(self, entity, node_type) -> bool      # проверка полноты
    def invalidate_detail_cache(self, node_type, node_id)  # инвалидация кэша
    def clear_cache(self)                                  # очистка кэша
    def get_stats(self) -> dict                            # статистика
```

---

## 4. **ПОТОКИ ДАННЫХ**

### 4.1. **Загрузка корпуса с владельцем (новый сценарий)**

```
[DetailsController] вызывает loader.load_building_with_owner(101)
    │
    ▼
[DataLoader] load_building_with_owner()
    │
    ├─→ вызывает load_details(BUILDING, 101)
    │        │
    │        ▼
    │   [EntityGraph] проверяет кэш (get_if_full)
    │        │
    │        ├─→ есть и полные → возвращает
    │        └─→ нет → загружает через API
    │
    ├─→ если building.owner_id:
    │        │
    │        ├─→ вызывает load_counterparty(owner_id)
    │        │        │
    │        │        ▼
    │        │   [EntityGraph] проверяет кэш
    │        │
    │        └─→ если owner:
    │                 │
    │                 └─→ вызывает load_responsible_persons(owner.id)
    │                          │
    │                          ▼
    │                     [EntityGraph] проверяет кэш
    │
    └─→ возвращает BuildingWithOwnerResult(building, owner, persons)
    │
    ▼
[DetailsController] эмитит BuildingDetailsLoaded(building, owner, persons)
    │
    ▼
[UI] обновляет вкладку контактов
```

### 4.2. **Загрузка комплексов (первый запуск)**

```
[Controller] вызывает loader.load_complexes()
    │
    ▼
[DataLoader] спрашивает graph.get_all(COMPLEX)
    │
    ▼
[EntityGraph] проверяет хранилище
    │
    ├─► [нет данных] → возвращает []
    │
    ▼
[DataLoader] эмитит DataLoading
    │
    ▼
[DataLoader] вызывает node_loader.load_complexes()
    │
    ▼
[NodeLoader] вызывает api.get_complexes()
    │
    ▼
[ApiClient] вызывает http.get("/physical/")
    │
    ▼
[HttpClient] выполняет GET, получает JSON
    │
    ▼
[ApiClient] преобразует JSON в Complex (converters)
    │
    ▼
[NodeLoader] сохраняет каждый комплекс: graph.add_or_update()
    │
    ▼
[EntityGraph] сохраняет в store, обновляет связи
    │
    ▼
[DataLoader] эмитит DataLoaded с payload=complexes
    │
    ▼
[Controller] получает результат
```

### 4.3. **Повторная загрузка (кэш)**

```
[Controller] вызывает loader.load_complexes()
    │
    ▼
[DataLoader] спрашивает graph.get_all(COMPLEX)
    │
    ▼
[EntityGraph] проверяет хранилище
    │
    ├─► [данные есть] → возвращает список
    │
    ▼
[DataLoader] log.cache("Complexes in cache: 5")
    │
    ▼
[Controller] получает данные из кэша (без API!)
```

### 4.4. **Ленивая загрузка детей (раскрытие узла)**

```
[Controller] получает NodeExpanded(node=COMPLEX#42)
    │
    ▼
[Controller] вызывает loader.load_children(COMPLEX, 42, BUILDING)
    │
    ▼
[DataLoader] спрашивает graph.get_cached_children(...)
    │
    ▼
[EntityGraph] проверяет наличие ВСЕХ детей в кэше
    │
    ├─► [есть все] → возвращает список
    ├─► [нет хотя бы одного] → возвращает []
    │
    ▼
[DataLoader] (если кэш неполный) эмитит DataLoading
    │
    ▼
[DataLoader] вызывает node_loader.load_children(...)
    │
    ▼
[NodeLoader] вызывает api.get_buildings(42)
    │
    ▼
[ApiClient] выполняет HTTP запрос
    │
    ▼
[NodeLoader] сохраняет каждый корпус: graph.add_or_update()
    │
    ▼
[DataLoader] эмитит DataLoaded
    │
    ▼
[Controller] получает список корпусов
```

---

## 5. **ВЗАИМОДЕЙСТВИЕ СО СЛОЯМИ**

### 5.1. **Связь со слоем данных (data)**

Services **вызывает** Data слой:
```python
# DataLoader вызывает методы EntityGraph
cached = self._graph.get_all(NodeType.COMPLEX)
self._graph.get_cached_children(parent_type, parent_id, child_type)
self._graph.get_if_full(node_type, node_id)
self._graph.add_or_update(entity)
self._graph.invalidate(node_type, node_id)
```

Services **не знает** о внутренностях Data слоя:
- ❌ Не импортирует `data.graph.store`
- ❌ Не обращается к `RelationIndex` напрямую
- ✅ Только через фасад `EntityGraph`

### 5.2. **Связь со слоем моделей (models)**

Services **создаёт и передаёт** модели:
```python
# ApiClient возвращает модели
def get_complexes(self) -> List[Complex]:
    data = self._http.get(...)
    return to_complex_list(data)  # List[Complex]

# DataLoader сохраняет модели в граф
self._graph.add_or_update(complex_obj)
```

### 5.3. **Связь с ядром (core)**

Services **использует** типы и события из core:
```python
from src.core import NodeType, NodeID, EventBus
from src.core.events import DataLoading, DataLoaded, DataError, ConnectionChanged

# Эмитит события
self._bus.emit(DataLoading(node_type=node_type, node_id=node_id))

# Использует типы
def load_children(self, parent_type: NodeType, parent_id: NodeID, child_type: NodeType)
```

### 5.4. **Связь с контроллерами (controllers)**

Services **вызывается** контроллерами:
```python
# В TreeController
complexes = self._loader.load_complexes()
buildings = self._loader.load_children(NodeType.COMPLEX, complex_id, NodeType.BUILDING)
details = self._loader.load_details(NodeType.BUILDING, building_id)

# В DetailsController
result = self._loader.load_building_with_owner(building_id)

# В ContextService (вызывается TreeController)
context = self._context_service.get_context(node)
```

Services **не знает** о контроллерах:
- ❌ Не импортирует `controllers`
- ❌ Не вызывает методы контроллеров

---

## 6. **СОБЫТИЯ, ГЕНЕРИРУЕМЫЕ SERVICES**

| Событие | Когда | Данные |
|---------|-------|--------|
| `DataLoading` | Перед началом загрузки | `node_type`, `node_id` |
| `DataLoaded` | После успешной загрузки | `node_type`, `node_id`, `payload`, `count` |
| `DataError` | При ошибке загрузки | `node_type`, `node_id`, `error` |
| `ConnectionChanged` | При изменении статуса соединения | `is_online` |

**На эти события подписываются:**
- `controllers` — для обновления состояния
- `projections` — для перестроения дерева
- `ui` — для обновления индикаторов

---

## 7. **КЛЮЧЕВЫЕ ПРИНЦИПЫ РАБОТЫ**

### 7.1. **Тупой оркестратор (DataLoader)**
DataLoader не принимает решений:
- Не решает, есть ли данные в кэше — спрашивает у `EntityGraph`
- Не решает, полные ли данные — спрашивает у `EntityGraph`
- Не решает, нужно ли загружать — спрашивает у `EntityGraph`

### 7.2. **Бизнес-логика в DataLoader**
DataLoader содержит бизнес-логику загрузки:
- `load_building_with_owner()` — если есть owner_id, загрузить владельца и его контакты
- Контроллеры не знают об этой логике

### 7.3. **Тупой исполнитель (NodeLoader)**
NodeLoader не знает о типах:
- Не содержит `if node_type == NodeType.COMPLEX`
- Вся конфигурация передаётся через DI
- Новый тип = новый лоадер в словаре

### 7.4. **Единая обёртка для событий**
Все методы загрузки используют `_with_events`:
- Гарантирует эмиссию `DataLoading` и `DataLoaded`
- Централизованная обработка ошибок
- Единообразие логирования

### 7.5. **Проверка кэша перед каждым запросом**
Каждый публичный метод DataLoader:
1. Сначала спрашивает `EntityGraph`
2. Если данных нет — только тогда идёт в API
3. Результат сохраняется в `EntityGraph` сразу после загрузки

### 7.6. **Сохранение traceback при ошибках**
Все исключения пробрасываются с `from e`:
```python
except Exception as e:
    raise ApiError(f"Failed: {e}") from e
```
При отладке видна полная цепочка вызовов.

---

## 8. **ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ**

### 8.1. **Инициализация в MainWindow**

```python
from src.core import EventBus
from src.data import EntityGraph, ComplexRepository, BuildingRepository, FloorRepository, CounterpartyRepository
from src.services import ApiClient, DataLoader, ConnectionService, ContextService

# Создаём компоненты
bus = EventBus()
graph = EntityGraph(bus)
api = ApiClient()
loader = DataLoader(bus, api, graph)

# Репозитории
complex_repo = ComplexRepository(graph)
building_repo = BuildingRepository(graph)
floor_repo = FloorRepository(graph)
counterparty_repo = CounterpartyRepository(graph)

# Контекст сервис
context_service = ContextService(
    complex_repo, building_repo, floor_repo, counterparty_repo, loader
)

# Мониторинг соединения
connection = ConnectionService(bus, api)
connection.start()

# Передаём в контроллеры
tree_controller = TreeController(bus, loader, context_service)
details_controller = DetailsController(bus, loader)
refresh_controller = RefreshController(bus, loader)
connection_controller = ConnectionController(bus)
```

### 8.2. **Загрузка корпуса с владельцем в DetailsController**

```python
class DetailsController(BaseController):
    def _load_building_details(self, building_id: int) -> None:
        try:
            # DataLoader сам решает, что загружать
            result = self._loader.load_building_with_owner(building_id)
            
            if result:
                self._bus.emit(BuildingDetailsLoaded(
                    building=result.building,
                    owner=result.owner,
                    responsible_persons=result.responsible_persons
                ))
        except Exception as e:
            self._emit_error(NodeIdentifier(NodeType.BUILDING, building_id), e)
```

### 8.3. **Сбор контекста в TreeController**

```python
class TreeController(BaseController):
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        node = event.data.node
        details = self._loader.load_details(node.node_type, node.node_id)
        context = self._context_service.get_context(node)
        
        self._bus.emit(NodeDetailsLoaded(
            node=node,
            payload=details,
            context=context
        ))
```

### 8.4. **Реакция на раскрытие узла**

```python
def _on_node_expanded(self, event):
    node = event.data.node
    
    if node.node_type == NodeType.COMPLEX:
        # Загружаем корпуса (ленивая загрузка)
        buildings = self._loader.load_children(
            NodeType.COMPLEX,
            node.node_id,
            NodeType.BUILDING
        )
        self._bus.emit(ChildrenLoaded(parent=node, children=buildings))
```

---

## 9. **ИТОГ: ЧТО ДАЁТ СЛОЙ SERVICES**

| Аспект | Результат |
|--------|-----------|
| **Разделение ответственности** | Контроллеры не знают о HTTP, Data слой не знает о загрузке |
| **Бизнес-логика загрузки** | DataLoader содержит правила (загрузка владельца с контактами) |
| **Кэширование** | Все данные проходят через `EntityGraph`, нет дублирования |
| **Ленивая загрузка** | Дети загружаются только при раскрытии узла |
| **События** | `DataLoading`, `DataLoaded`, `DataError` для всех операций |
| **Обработка ошибок** | Единая иерархия, сохранение traceback |
| **Тестируемость** | Каждый компонент можно тестировать изолированно |
| **Расширяемость** | Новый тип = новый лоадер в словаре |
| **Контекст для UI** | `ContextService` собирает имена родителей в одном месте |

---

## 🆕 **СПИСОК ИЗМЕНЕНИЙ В СЛОЕ SERVICES**

| Файл | Изменение | Назначение |
|------|-----------|------------|
| `data_loader.py` | 🆕 `load_building_with_owner()` | Бизнес-логика загрузки корпуса с владельцем |
| `data_loader.py` | 🆕 `get_ancestors()` | Получение всех предков узла |
| `context_service.py` | 🆕 новый файл | Сбор имён родителей для UI |
| `types.py` | 🆕 новый файл | Типизированные результаты (`BuildingWithOwnerResult`) |

---

**Services — это мост между хранением (data) и координацией (controllers), который обеспечивает предсказуемую, кэшируемую, событийно-управляемую загрузку данных с бизнес-логикой загрузки связанных сущностей.** 🚀