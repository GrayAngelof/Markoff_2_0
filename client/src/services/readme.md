## Анализ слоя: **services** (слой бизнес-логики и сервисов)

### Краткое описание слоя

**Назначение** – координировать загрузку данных, управлять соединением с сервером и предоставлять бизнес-ориентированные сервисы для вышестоящих слоёв (`projections`, `controllers`, `ui`). Слой `services` **не хранит данные**, но orchestrирует их получение, кэширование и преобразование.

**Что делает:**
- Предоставляет фасад `ApiClient` для всех HTTP-запросов к бэкенду (преобразование JSON → DTO)
- Реализует фасад `DataLoader` – единую точку входа для загрузки данных (дерево, детали, справочники)
- Управляет состоянием соединения через `ConnectionService` (периодическая проверка, генерация `ConnectionChanged`)
- Собирает контекст для UI (`ContextService`): имена родителей, владельцы, ответственные лица
- Реализует ленивую загрузку детей с отслеживанием состояния (`TreeLoader` через `LoadStateIndex`)
- Обрабатывает повторные попытки при ошибках (базовый загрузчик `BaseLoader`)

**Что не должен делать:**
- Содержать UI-специфичный код (форматирование, рендеринг) – это в `projections` или `ui`
- Обращаться напрямую к БД или файловой системе – только через `data` слой
- Содержать сложную бизнес-логику предметной области (расчёты, правила) – это в отдельных сервисах или `models`
- Нарушать иерархию: не импортировать из `projections`, `controllers`, `ui`

**Зависимости:** от `core` (типы, события, `EventBus`), от `models` (все DTO), от `data` (`EntityGraph`, репозитории), от `shared` (валидация, сравнение), от `utils.logger`. Внутри себя сервисы могут зависеть друг от друга (например, `DataLoader` использует загрузчики, `ConnectionService` использует `ApiClient`).

---

### Файловая структура слоя

```
client/src/services/
├── __init__.py                    # Публичный экспорт: ApiClient, DataLoader, ConnectionService, ContextService
├── api_client.py                  # ApiClient – фасад HTTP клиента (публичный)
├── connection.py                  # ConnectionService – мониторинг соединения
├── context_service.py             # ContextService – сбор контекста для UI
├── data_loader.py                 # DataLoader – фасад загрузки данных
├── types.py                       # Общие типы (BuildingWithOwnerResult и др.)
├── api/                           # Приватный пакет API слоя
│   ├── __init__.py                # Маркер приватности
│   ├── http_client.py             # HttpClient – низкоуровневый HTTP клиент (requests)
│   ├── endpoints.py               # Endpoints – константы URL
│   ├── converters.py              # Преобразование JSON → DTO (to_complex_list и т.д.)
│   └── errors.py                  # Иерархия исключений (ApiError, ConnectionError, ...)
├── loaders/                       # Приватный пакет загрузчиков (оркестрация)
│   ├── __init__.py                # Экспорт BaseLoader, TreeLoader, PhysicalLoader, BusinessLoader, SafetyLoader
│   ├── base.py                    # BaseLoader – обёртка с повторными попытками и эмиссией событий
│   ├── tree_loader.py             # TreeLoader – загрузка дерева (ленивая загрузка детей)
│   ├── physical_loader.py         # PhysicalLoader – загрузка детальной физики
│   ├── business_loader.py         # BusinessLoader – заглушка для бизнес-данных
│   └── safety_loader.py           # SafetyLoader – заглушка для данных пожарной безопасности
└── loading/                       # Приватный пакет "тупых" загрузчиков (без логики)
    ├── __init__.py                # Маркер приватности
    ├── node_loader.py             # NodeLoader – чистая загрузка физической иерархии (не мутирует граф)
    └── dictionary_loader.py       # DictionaryLoader – загрузка справочников (контрагенты, ответственные лица)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `ApiClient` | `api_client.py` | **Фасад HTTP клиента**. Выполняет запросы к API, преобразует JSON в DTO через converters. Логирует все вызовы. |
| `HttpClient` | `api/http_client.py` | Низкоуровневый HTTP клиент на основе `requests.Session`. Обрабатывает статус-коды, преобразует ошибки в иерархию `ApiError`. |
| `Endpoints` | `api/endpoints.py` | Контейнер URL-путей (статичные методы). |
| `BaseLoader` | `loaders/base.py` | Базовый класс для всех загрузчиков. Предоставляет метод `_with_events` для единообразной эмиссии `DataLoaded`/`DataError` и повторных попыток. |
| `TreeLoader` | `loaders/tree_loader.py` | Загрузчик дерева. Отвечает за ленивую загрузку детей, использует `LoadStateIndex` из `data` для предотвращения дублирующихся запросов. |
| `PhysicalLoader` | `loaders/physical_loader.py` | Загрузчик детальной информации о физических объектах. Проверяет кэш через `get_if_full()`. |
| `BusinessLoader` | `loaders/business_loader.py` | Заглушка для будущей загрузки бизнес-данных (контрагенты, ответственные лица). |
| `SafetyLoader` | `loaders/safety_loader.py` | Заглушка для данных пожарной безопасности. |
| `NodeLoader` | `loading/node_loader.py` | **Чистый загрузчик** физической иерархии. Не мутирует граф, только вызывает API и возвращает DTO. Конфигурируется через DI (словари child_loaders/detail_loaders). |
| `DictionaryLoader` | `loading/dictionary_loader.py` | Загрузчик справочных данных (контрагенты, ответственные лица). Сохраняет в граф, возвращает DTO. |
| `ConnectionService` | `connection.py` | Сервис мониторинга соединения. В отдельном потоке периодически проверяет доступность сервера, эмитит `ConnectionChanged`. |
| `ContextService` | `context_service.py` | Сервис сбора контекста для UI. Получает имена родителей, владельцев, ответственных лиц через репозитории `data`. |
| `DataLoader` | `data_loader.py` | **Фасад загрузки данных**. Делегирует `TreeLoader`, `PhysicalLoader`, `BusinessLoader`, `SafetyLoader`. Единая точка входа для всех загрузок. |
| `BuildingWithOwnerResult` | `types.py` | Dataclass для результата загрузки корпуса с владельцем и ответственными лицами. |

---

### Внутренние импорты (только между модулями services, core, models, data, shared, utils)

**Из `core`:**  
- `EventBus`, `NodeType`, `NodeIdentifier`, `ConnectionChanged`, `DataLoaded`, `DataError`, `DataLoadedKind`
- `get_child_type`, `get_parent_type` (через `core.rules.hierarchy`)

**Из `models`:**  
- `Complex`, `Building`, `Floor`, `Room`, `Counterparty`, `ResponsiblePerson`

**Из `data`:**  
- `EntityGraph` (импортируется через `src.data`)
- Репозитории: `ComplexRepository`, `BuildingRepository`, `FloorRepository`, `RoomRepository`, `CounterpartyRepository`, `ResponsiblePersonRepository`

**Из `shared`:**  
- `validate_positive_int`, `has_changed` (через `shared.validation`, `shared.comparison`)

**Из `utils.logger`** – везде.

**Внутри `services`:**  
- `ApiClient` → `HttpClient`, `Endpoints`, converters, errors
- `DataLoader` → `TreeLoader`, `PhysicalLoader`, `BusinessLoader`, `SafetyLoader`
- `TreeLoader` → `NodeLoader` (из `loading`), `EntityGraph`, `ApiClient`
- `PhysicalLoader` → `NodeLoader`, `EntityGraph`, `ApiClient`
- `ContextService` → репозитории из `data`
- `ConnectionService` → `ApiClient`, `EventBus`

**Никаких импортов из `projections`, `controllers`, `ui`.**

---

### Экспортируемые методы / классы для вышестоящих слоёв

Публичное API слоя `services` доступно через `from src.services import ...` (согласно `services/__init__.py`):

**Классы:**
- `ApiClient`
- `DataLoader`
- `ConnectionService`
- `ContextService`

**Методы `ApiClient` (все возвращают DTO или список DTO):**
- `get_complexes() -> List[Complex]`
- `get_buildings(complex_id) -> List[Building]`
- `get_floors(building_id) -> List[Floor]`
- `get_rooms(floor_id) -> List[Room]`
- `get_complex_detail(complex_id) -> Optional[Complex]`
- `get_building_detail(building_id) -> Optional[Building]`
- `get_floor_detail(floor_id) -> Optional[Floor]`
- `get_room_detail(room_id) -> Optional[Room]`
- `get_counterparty(counterparty_id) -> Optional[Counterparty]`
- `get_responsible_persons(counterparty_id) -> List[ResponsiblePerson]`
- `check_connection(timeout) -> bool`
- `get_server_info() -> dict`

**Методы `DataLoader`:**
- `load_complexes() -> List[Complex]`
- `load_children(parent_type, parent_id, child_type) -> List[Any]`
- `reload_node(node_type, node_id) -> None`
- `clear_cache() -> None`
- `load_details(node_type, node_id) -> Optional[Any]`
- `load_counterparty(counterparty_id) -> Optional[Any]` (заглушка)
- `load_responsible_persons(counterparty_id) -> List[Any]` (заглушка)
- `load_sensors_by_room(room_id) -> List[Any]` (заглушка)
- `load_events_by_building(building_id) -> List[Any]` (заглушка)

**Методы `ConnectionService`:**
- `start() -> None` – запускает периодическую проверку соединения
- `stop() -> None` – останавливает
- `force_check() -> None` – принудительная проверка

**Методы `ContextService`:**
- `get_context(node: NodeIdentifier) -> Dict[str, Any]` – возвращает имена родителей
- `get_building_context(building_id: int) -> Dict[str, Any]` – контекст корпуса (владелец, ответственные)
- `get_owner_context(counterparty_id: int) -> Dict[str, Any]` – контекст владельца

**Типы (опционально):**
- `BuildingWithOwnerResult` – dataclass для группировки корпуса, владельца и ответственных лиц.

---

### Итоговое заключение: принципы работы со слоем `services`

1. **Зависимость только от `core`, `models`, `data`** – слой `services` не знает о `projections`, `controllers`, `ui`. Это строгое правило: сервисы вызывают методы `data` (репозитории, `EntityGraph`) и используют события `core`, но не содержат кода отображения или обработки запросов.

2. **Используйте фасады для упрощения** – вышестоящие слои должны работать через `ApiClient`, `DataLoader`, `ConnectionService`, `ContextService`, а не через внутренние загрузчики (`TreeLoader`, `PhysicalLoader` и т.д.). Это обеспечивает стабильный контракт.

3. **Ленивая загрузка данных** – для дерева используйте `DataLoader.load_children()`. Он сам проверяет `is_children_loaded()` и управляет состоянием `LOADING`/`LOADED`. Не вызывайте `load_children` повторно для уже загруженного узла.

4. **Работа с кэшем** – `DataLoader.load_details()` сначала проверяет наличие полных данных через `EntityGraph.get_if_full()`. При ручном обновлении вызывайте `reload_node()` – он инвалидирует данные и сбрасывает состояние детей.

5. **Мониторинг соединения** – `ConnectionService` запускается один раз при старте приложения. Он автоматически эмитит `ConnectionChanged` в `EventBus`. Подписывайтесь на это событие в UI для отображения статуса.

6. **Обработка ошибок** – все методы `ApiClient` преобразуют HTTP ошибки в исключения из `services.api.errors` (`ConnectionError`, `TimeoutError`, `NotFoundError`, `ClientError`, `ServerError`). Вышестоящие слои должны их обрабатывать. `DataLoader` через `BaseLoader` делает повторные попытки (по умолчанию 1) и эмитит `DataError` при окончательном провале.

7. **Контекст для UI** – не пытайтесь собирать имена родителей вручную через репозитории. Используйте `ContextService.get_context()`, который уже знает иерархию и возвращает готовый словарь.

8. **Расширение** – при добавлении нового типа загрузки:
   - Добавьте методы в `ApiClient` (если нужно)
   - Реализуйте новый загрузчик (наследуя `BaseLoader`) или добавьте логику в существующий
   - Добавьте метод-фасад в `DataLoader`
   - **Не** раскрывайте внутренние загрузчики напрямую

Слой `services` является **оркестратором** – он связывает `data` (кэш, граф) и `core` (события) с внешними источниками (API). Вся бизнес-логика, которая требует координации нескольких репозиториев или внешних вызовов, должна находиться здесь, но без привязки к UI.