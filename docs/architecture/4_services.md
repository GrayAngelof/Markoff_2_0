## Анализ слоя: **services** (сервисный слой)

### Краткое описание слоя

**Назначение** – координировать загрузку данных из API и управление кэшем. Слой `services` выступает оркестратором между HTTP-клиентом, графом данных и бизнес-логикой вышестоящих слоёв. Он отвечает за "как" получить данные (из кэша или сети), но не за "что с ними делать".

**Что делает:**
- Предоставляет фасад `ApiClient` для всех HTTP-запросов к бекенду
- Координирует загрузку данных через `DataLoader` (оркестрация кэша и сети)
- Управляет состоянием соединения через `ConnectionService`
- Собирает контекст для UI (имена родителей) через `ContextService`
- Реализует ленивую загрузку детей дерева с защитой от гонок
- Поддерживает повторные попытки при временных сбоях
- Эмитит события `DataLoaded`/`DataError`/`ConnectionChanged` через `EventBus`

**Что не должен делать:**
- Содержать UI-логику (отображение, форматирование для экрана)
- Содержать бизнес-правила предметной области (это `controllers` и выше)
- Хранить состояние приложения (кэш – в `data`, UI-состояние – в `ui`)
- Напрямую манипулировать DOM или виджетами

---

### Файловая структура слоя

```
client/src/services/
├── __init__.py                    # Публичное API (фасады)
├── api_client.py                  # ApiClient (фасад HTTP клиента)
├── data_loader.py                 # DataLoader (фасад загрузки данных)
├── connection.py                  # ConnectionService (мониторинг соединения)
├── context_service.py             # ContextService (сбор контекста для UI)
├── api/                           # Приватный пакет API реализации
│   ├── __init__.py                # Маркер приватности (пустой __all__)
│   ├── http_client.py             # HttpClient (низкоуровневый HTTP)
│   ├── endpoints.py               # Endpoints (константы URL)
│   ├── converters.py              # Конвертеры JSON → DTO
│   └── errors.py                  # Иерархия исключений API
└── loaders/                       # Приватный пакет загрузчиков
    ├── __init__.py                # Экспорт загрузчиков (внутренний)
    ├── base.py                    # BaseLoader (повторные попытки + события)
    ├── tree_loader.py             # TreeLoader (ленивая загрузка дерева)
    ├── physical_loader.py         # PhysicalLoader (детальные данные)
    ├── node_loader.py             # NodeLoader (чистый вызов API)
    └── dictionary_loader.py       # DictionaryLoader (справочники, заглушка)
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `ApiClient` | `api_client.py` | **Фасад HTTP клиента**. Все публичные методы возвращают DTO. Логирует запросы, преобразует JSON через converters. |
| `DataLoader` | `data_loader.py` | **Фасад загрузки данных**. Оркестрирует TreeLoader и PhysicalLoader. Единая точка входа для всех загрузок. |
| `ConnectionService` | `connection.py` | Мониторинг соединения. Периодически проверяет доступность сервера в отдельном потоке. Эмитит `ConnectionChanged`. |
| `ContextService` | `context_service.py` | Сбор контекста для UI. Получает имена родителей для отображения иерархии в панели деталей. |
| `HttpClient` | `api/http_client.py` | Низкоуровневый HTTP клиент на `requests`. Преобразует статусы в исключения, поддерживает сессии. |
| `Endpoints` | `api/endpoints.py` | Константы URL-путей. Все эндпоинты API в виде статических методов. |
| `BaseLoader` | `loaders/base.py` | Базовый класс загрузчиков. Оборачивает вызовы в `_with_events` для эмиссии `DataLoaded`/`DataError` и повторных попыток. |
| `TreeLoader` | `loaders/tree_loader.py` | Загрузка данных для дерева. Ленивая загрузка детей с проверкой `LoadStateIndex`. Работает через `EntityGraph`. |
| `PhysicalLoader` | `loaders/physical_loader.py` | Загрузка детальных данных. Проверяет кэш через `get_if_full()` перед запросом к API. |
| `NodeLoader` | `loaders/node_loader.py` | Чистый загрузчик. Только вызывает `ApiClient` и возвращает DTO. Не мутирует граф. |
| `DictionaryLoader` | `loaders/dictionary_loader.py` | Загрузчик справочников (заглушка, TODO). |

**Иерархия исключений API (`api/errors.py`):**
- `ApiError` – базовое
  - `ConnectionError` – сеть недоступна
    - `TimeoutError` – таймаут
  - `NotFoundError` – 404
  - `ClientError` – 4xx (кроме 404)
  - `ServerError` – 5xx

---

### Внутренние импорты (только между модулями services)

**Из `api_client.py` (фасад):**
- `from src.services.api.converters import (to_complex_tree_list, ...)`
- `from src.services.api.endpoints import Endpoints`
- `from src.services.api.errors import (ApiError, ConnectionError, NotFoundError, TimeoutError)`
- `from src.services.api.http_client import HttpClient`

**Из `data_loader.py` (фасад):**
- `from src.services.loaders.physical_loader import PhysicalLoader`
- `from src.services.loaders.tree_loader import TreeLoader`

**Из `connection.py`:**
- `from src.services.api_client import ApiClient`

**Из `context_service.py`:**
- `from src.data import (BuildingRepository, ComplexRepository, FloorRepository, RoomRepository)`

**Из `loaders/base.py`:**
- `from src.core.events.definitions import DataError, DataLoaded, DataLoadedKind`

**Из `loaders/tree_loader.py` и `physical_loader.py`:**
- `from src.services.loaders.base import BaseLoader`
- `from src.services.loaders.node_loader import NodeLoader`

**Из `loaders/node_loader.py`:**
- `from src.services.api_client import ApiClient`

**Из `api/http_client.py`:**
- `from src.services.api.errors import (ApiError, ClientError, ConnectionError, NotFoundError, ServerError, TimeoutError)`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вся публичная поверхность слоя `services` доступна через импорт из `src.services`:

**`ApiClient` – HTTP фасад:**
- `__init__(base_url: Optional[str] = None)`
- `close()` / контекстный менеджер
- **Tree (минимальные данные):**
  - `get_complexes_tree() -> List[ComplexTreeDTO]`
  - `get_buildings_tree(complex_id: NodeID) -> List[BuildingTreeDTO]`
  - `get_floors_tree(building_id: NodeID) -> List[FloorTreeDTO]`
  - `get_rooms_tree(floor_id: NodeID) -> List[RoomTreeDTO]`
- **Detail (полные данные):**
  - `get_complex_detail(complex_id: NodeID) -> Optional[ComplexDetailDTO]`
  - `get_building_detail(building_id: NodeID) -> Optional[BuildingDetailDTO]`
  - `get_floor_detail(floor_id: NodeID) -> Optional[FloorDetailDTO]`
  - `get_room_detail(room_id: NodeID) -> Optional[RoomDetailDTO]`
- **Мониторинг:**
  - `check_connection(timeout: int = 3) -> bool`
  - `get_server_info() -> dict`

**`DataLoader` – фасад загрузки (оркестратор кэша и сети):**
- `__init__(bus: EventBus, api: ApiClient, graph: EntityGraph)`
- **Корневые узлы:**
  - `load_complexes_tree() -> List[ComplexTreeDTO]`
- **Ленивая загрузка детей (с проверкой кэша и состояний):**
  - `load_buildings_tree(complex_id: NodeID) -> List[BuildingTreeDTO]`
  - `load_floors_tree(building_id: NodeID) -> List[FloorTreeDTO]`
  - `load_rooms_tree(floor_id: NodeID) -> List[RoomTreeDTO]`
- **Детальные данные (с проверкой полного кэша):**
  - `load_complex_detail(complex_id: NodeID) -> Optional[ComplexDetailDTO]`
  - `load_building_detail(building_id: NodeID) -> Optional[BuildingDetailDTO]`
  - `load_floor_detail(floor_id: NodeID) -> Optional[FloorDetailDTO]`
  - `load_room_detail(room_id: NodeID) -> Optional[RoomDetailDTO]`
- **Управление кэшем:**
  - `reload_node(node_type: NodeType, node_id: NodeID) -> None`
  - `clear_cache() -> None`

**`ConnectionService` – мониторинг соединения:**
- `__init__(bus: EventBus, api: ApiClient, interval_ms: int = 600000)`
- `start() -> None` – запускает фоновую проверку
- `stop() -> None` – останавливает
- `force_check() -> None` – принудительная проверка

**`ContextService` – сбор контекста для UI:**
- `__init__(complex_repo, building_repo, floor_repo, room_repo)`
- `get_context(node: NodeIdentifier) -> Dict[str, Any]` – возвращает имена родителей
- `get_building_context(building_id: int) -> Dict[str, Any]`

---

### Итоговое заключение: принципы работы со слоём `services`

1. **Импорт только сверху вниз** – вышестоящие слои (`projections`, `controllers`, `ui`) могут импортировать из `services` свободно. Слой `services` может импортировать:
   - `core` – для `EventBus`, `NodeType`, событий
   - `data` – для `EntityGraph` и репозиториев
   - `models` – для всех DTO

2. **Запрещены обратные импорты** – код внутри `services` не должен импортировать ничего из `projections`, `controllers`, `ui`.

3. **Используйте `DataLoader` как единую точку входа для загрузки данных** – он автоматически проверяет кэш, управляет состоянием загрузки и эмитит события:
   ```python
   from src.services import DataLoader
   
   # Загрузит из кэша или API, эмитит DataLoaded/DataError
   complexes = data_loader.load_complexes_tree()
   ```

4. **`ApiClient` используйте только если нужен прямой HTTP-запрос без кэширования** – например, для проверки соединения или получения информации о сервере. Для основных данных всегда используйте `DataLoader`.

5. **Работа с событиями** – все загрузчики через `BaseLoader._with_events()` автоматически эмитят:
   - `DataLoaded` – при успешной загрузке
   - `DataError` – при ошибке после всех попыток

6. **Повторные попытки** – `BaseLoader` по умолчанию делает 1 повторную попытку при ошибке (можно настроить через `retry_count`). Задержка между попытками – 0.5 секунды.

7. **Ленивая загрузка дерева** – `TreeLoader` защищает от гонок через `LoadStateIndex`:
   - Если дети уже загружены – возвращает из кэша
   - Если загрузка уже идёт – возвращает `[]` (не блокирует)
   - Если не загружены – начинает загрузку и блокирует последующие вызовы

8. **Детальные данные** – `PhysicalLoader` использует `graph.get_if_full()` для проверки наличия полного DTO (`IS_DETAIL=True`) в кэше. Если есть – возвращает без запроса к API.

9. **`ContextService` только для UI** – этот сервис собирает строковые представления (имена родителей) для отображения в панели деталей. Не используйте его для бизнес-логики.

10. **`ConnectionService` в отдельном потоке** – сервис запускает фоновый поток для периодической проверки соединения. При изменении статуса эмитит `ConnectionChanged`. Всегда вызывайте `start()` при старте приложения и `stop()` при завершении.

11. **Приватные пакеты** – никогда не импортируйте напрямую из `src.services.api.*` или `src.services.loaders.*`. Всё публичное API доступно через `src.services`:
    ```python
    # ✅ Правильно
    from src.services import ApiClient, DataLoader
    
    # ❌ Неправильно
    from src.services.api.http_client import HttpClient
    from src.services.loaders.tree_loader import TreeLoader
    ```

12. **Иерархия исключений** – все ошибки API преобразуются в иерархию `ApiError`. Вышестоящие слои могут ловить конкретные типы (например, `ConnectionError` для отображения офлайн-режима).

13. **Чистые загрузчики vs мутирующие** – `NodeLoader` только вызывает API и возвращает DTO (чистая функция). `TreeLoader` и `PhysicalLoader` мутируют граф и управляют состоянием. Это разделение упрощает тестирование.

Слой `services` является **оркестратором между сетью, кэшем и бизнес-логикой**. Он скрывает от вышестоящих слоёв сложность работы с асинхронностью, состоянием загрузки и кэшированием. Контроллеры и UI работают только с `DataLoader`, не зная о существовании `EntityGraph` или `HttpClient`.