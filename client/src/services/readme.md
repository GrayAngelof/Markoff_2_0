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


# Services — описание слоя

## Назначение

Координация загрузки данных и HTTP-коммуникации. Оркестрирует вызовы API, преобразование ответов, сохранение в граф и эмиссию событий.

**Строгая зависимость:** только от `core` (события, типы), `models` (DTO), `data` (EntityGraph, репозитории). Никакой UI-логики.

---

## Структура

```
services/
├── __init__.py                    # Публичное API
├── api_client.py                  # ApiClient — фасад HTTP
├── data_loader.py                 # DataLoader — фасад загрузки
├── connection.py                  # ConnectionService — мониторинг соединения
├── context_service.py             # ContextService — сбор контекста для UI
├── types.py                       # Общие типы (BuildingWithOwnerResult)
├── api/                           # ПРИВАТНО — HTTP слой
│   ├── http_client.py             # HttpClient — низкоуровневые запросы
│   ├── endpoints.py               # Endpoints — константы URL
│   ├── converters.py              # JSON → модели
│   └── errors.py                  # Иерархия исключений
└── loading/                       # ПРИВАТНО — загрузчики
    ├── node_loader.py             # NodeLoader — физическая иерархия
    ├── dictionary_loader.py       # DictionaryLoader — справочники
    └── utils.py                   # LoaderUtils — проверка полноты
```

---

## Публичное API

### Импорт

```python
from src.services import ApiClient, DataLoader, ConnectionService, ContextService
```

---

## Компоненты

### 1. ApiClient (`api_client.py`) — фасад HTTP

Единая точка доступа к API. Возвращает модели, а не сырые JSON.

| Метод | Описание |
|-------|----------|
| `get_complexes()` | `List[Complex]` |
| `get_buildings(complex_id)` | `List[Building]` |
| `get_floors(building_id)` | `List[Floor]` |
| `get_rooms(floor_id)` | `List[Room]` |
| `get_complex_detail(id)` | `Optional[Complex]` |
| `get_building_detail(id)` | `Optional[Building]` |
| `get_floor_detail(id)` | `Optional[Floor]` |
| `get_room_detail(id)` | `Optional[Room]` |
| `get_counterparty(id)` | `Optional[Counterparty]` |
| `get_responsible_persons(id)` | `List[ResponsiblePerson]` |
| `check_connection(timeout)` | `bool` |
| `get_server_info()` | `dict` |

**Особенности:**
- `NotFoundError` → возвращает `None` или `[]` (не пробрасывает)
- Остальные ошибки пробрасываются с сохранением traceback

---

### 2. DataLoader (`data_loader.py`) — фасад загрузки

Оркестратор загрузки. Проверяет кэш (через `EntityGraph`), эмитит события.

| Метод | Описание |
|-------|----------|
| `load_complexes()` | `List[Complex]` — все комплексы |
| `load_children(parent_type, parent_id, child_type)` | `List[Any]` — ленивая загрузка детей |
| `load_details(node_type, node_id)` | `Optional[Any]` — детальная информация |
| `load_counterparty(id)` | `Optional[Counterparty]` |
| `load_responsible_persons(id)` | `List[ResponsiblePerson]` |
| `load_building_with_owner(id)` | `Optional[BuildingWithOwnerResult]` — корпус + владелец + контакты |
| `reload_node(node_type, node_id)` | `None` — инвалидирует и загружает заново |
| `reload_branch(node_type, node_id)` | `None` — перезагружает всю ветку |
| `clear_cache()` | `None` |
| `get_stats()` | `dict` |

**Эмитит события:**
- `DataLoaded` — при успехе
- `DataError` — при ошибке

---

### 3. ConnectionService (`connection.py`) — мониторинг соединения

Периодически проверяет доступность сервера в отдельном потоке.

| Метод | Описание |
|-------|----------|
| `start()` | Запускает фоновую проверку |
| `stop()` | Останавливает проверку |
| `force_check()` | Принудительная проверка |

**Эмитит:** `ConnectionChanged(is_online=bool)` при изменении статуса

---

### 4. ContextService (`context_service.py`) — сбор контекста

Собирает имена родителей и связанные данные для UI.

| Метод | Описание |
|-------|----------|
| `get_context(node)` | `dict` — имена родителей (complex_name, building_name, floor_num) |
| `get_building_context(building_id)` | `dict` — + owner, responsible_persons |
| `get_owner_context(counterparty_id)` | `dict` — owner + responsible_persons |

---

### 5. Типы (`types.py`)

```python
@dataclass(frozen=True, slots=True)
class BuildingWithOwnerResult:
    building: Building
    owner: Optional[Counterparty] = None
    responsible_persons: List[ResponsiblePerson] = field(default_factory=list)
```

---

## Приватные компоненты

### HTTP слой (`api/`)

| Компонент | Назначение |
|-----------|------------|
| `HttpClient` | Низкоуровневые запросы, обработка статусов, преобразование в исключения |
| `Endpoints` | Константы URL (статические методы) |
| `to_*_list()`, `to_*()` | JSON → модели |
| `ApiError`, `ConnectionError`, `TimeoutError`, `NotFoundError`, `ClientError`, `ServerError` | Иерархия исключений |

### Загрузчики (`loading/`)

| Компонент | Назначение |
|-----------|------------|
| `NodeLoader` | Загрузка физической иерархии (комплексы → корпуса → этажи → помещения) |
| `DictionaryLoader` | Загрузка справочников (контрагенты, ответственные лица) |
| `LoaderUtils` | Проверка полноты данных (есть ли детальные поля), кэширование результатов |

**LoaderUtils.has_details(entity, node_type):**
- `Complex`: есть `description` или `address`
- `Building`: есть `description` или `address`
- `Floor`: есть `description`
- `Room`: есть `area` или `status_code`

---

## Иерархия исключений API

```
ApiError
├── ConnectionError      # сеть недоступна
│   └── TimeoutError     # таймаут
├── NotFoundError        # 404
├── ClientError          # 4xx (кроме 404)
└── ServerError          # 5xx
```

---

## Зависимости

| Компонент | Зависит от |
|-----------|------------|
| `ApiClient` | `api.http_client`, `api.converters`, `api.endpoints`, `api.errors` |
| `DataLoader` | `core.EventBus`, `data.EntityGraph`, `api_client`, `loading.*` |
| `ConnectionService` | `core.EventBus`, `api_client` |
| `ContextService` | `data.*Repository` (через фабрики) |

---

## Итог

Слой предоставляет вышележащим слоям:

| Возможность | Через |
|-------------|-------|
| HTTP-запросы к API | `ApiClient` |
| Ленивая загрузка с кэшированием | `DataLoader` |
| Мониторинг соединения | `ConnectionService` |
| Контекст для UI (имена родителей, владельцы) | `ContextService` |
| Единообразные события загрузки | `DataLoaded` / `DataError` |

**Принципы:**
- `ApiClient` и `DataLoader` — единственные публичные фасады
- Внутренности `api/` и `loading/` не экспортируются
- `DataLoader` проверяет кэш, но не решает, что загружать — только исполняет
- Все ошибки API преобразуются в иерархию исключений