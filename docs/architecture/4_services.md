## Анализ слоя «services»

### Краткое описание слоя

Слой **services** — это слой **бизнес-логики и координации** в приложении. Он расположен между `data` и `projections/controllers`. Его задачи:

- **HTTP-коммуникация с бэкендом** — `ApiClient` (фасад над `HttpClient`) выполняет запросы, преобразует JSON в DTO (через `converters`) и транслирует сетевые ошибки в иерархию исключений.
- **Загрузка и кэширование данных** — `DataLoader` (фасад) оркестрирует специализированные загрузчики:
  - `TreeLoader` — ленивая загрузка детей для дерева (учитывает состояние загрузки через `LoadStateIndex`).
  - `PhysicalLoader` — загрузка детальных данных (DetailDTO) с проверкой кэша в `EntityGraph`.
  - `DictionaryLoader` — загрузка справочников (статусы, типы) через API.
- **Мониторинг соединения** — `ConnectionService` в отдельном потоке периодически проверяет доступность сервера и генерирует событие `ConnectionChanged`.
- **Формирование контекста для UI** — `ContextService` собирает имена родителей (комплекс, корпус, этаж) для заданного узла, используя репозитории.

**Что слой НЕ должен делать:**
- Не содержит UI-логики (форматирование, ViewModel).
- Не обращается к слоям `projections`, `controllers`, `view models`, `ui`.
- Не хранит долгосрочное состояние (кроме кэша в `data`, который он использует).
- Не реализует сложную бизнес-логику предметной области (это задача выше).

---

### Файловая структура слоя

```
src/services/
├── __init__.py                      # Публичное API (ApiClient, ConnectionService, ContextService, DataLoader)
├── api_client.py                    # ApiClient — фасад HTTP клиента
├── connection.py                    # ConnectionService — мониторинг соединения
├── context_service.py               # ContextService — сбор имён родителей
├── data_loader.py                   # DataLoader — оркестратор загрузки
│
├── api/                             # ПРИВАТНЫЙ пакет: детали HTTP и конвертации
│   ├── __init__.py
│   ├── converters.py                # Функции to_*_list, to_*_detail (JSON → DTO)
│   ├── endpoints.py                 # Endpoints — URL-константы
│   ├── errors.py                    # Иерархия исключений ApiError, ConnectionError, TimeoutError и др.
│   └── http_client.py               # HttpClient — низкоуровневый requests.Session
│
└── loaders/                         # ПРИВАТНЫЙ пакет: загрузчики
    ├── __init__.py
    ├── base.py                      # BaseLoader — повторные попытки и эмиссия DataLoaded/DataError
    ├── dictionary_loader.py         # DictionaryLoader — загрузка справочников
    ├── node_loader.py               # NodeLoader — чистые вызовы API (без кэша, без мутации графа)
    ├── physical_loader.py           # PhysicalLoader — загрузка деталей (с кэшем через EntityGraph)
    └── tree_loader.py               # TreeLoader — ленивая загрузка детей (с состоянием загрузки)
```

---

### Описание внутренних классов (приватные / не для внешнего использования)

| Класс / Модуль | Назначение |
|----------------|-------------|
| `HttpClient` (`api/http_client.py`) | Низкоуровневый HTTP-клиент на `requests.Session`. Выполняет GET-запросы, преобразует статус-коды в исключения (`ConnectionError`, `TimeoutError`, `NotFoundError`, `ClientError`, `ServerError`). |
| `Endpoints` (`api/endpoints.py`) | Статические методы, возвращающие URL-пути для API (например, `complexes()`, `buildings(complex_id)`). Единое место для всех эндпоинтов. |
| Функции конвертеров (`api/converters.py`) | Преобразуют сырые JSON-словари в DTO (например, `to_complex_tree_list`, `to_building_detail`). Не содержат логики, только вызов `from_dict`. |
| Исключения (`api/errors.py`) | Иерархия: `ApiError` → `ConnectionError`, `TimeoutError`, `NotFoundError`, `ClientError`, `ServerError`. Все сохраняют статус-код и тело ответа. |
| `BaseLoader` (`loaders/base.py`) | Абстрактный загрузчик с методом `_with_events`, который оборачивает вызов функции, добавляет повторные попытки и эмитит `DataLoaded` / `DataError` в `EventBus`. |
| `NodeLoader` (`loaders/node_loader.py`) | Чистый загрузчик: вызывает методы `ApiClient` и возвращает DTO. Не взаимодействует с `EntityGraph`. Используется `TreeLoader` и `PhysicalLoader`. |
| `TreeLoader` (`loaders/tree_loader.py`) | Загрузка данных для дерева (TreeDTO). Использует `LoadStateIndex` через `EntityGraph` для отслеживания состояния загрузки детей. Предотвращает повторные запросы и гонки. |
| `PhysicalLoader` (`loaders/physical_loader.py`) | Загрузка детальных данных (DetailDTO). Проверяет кэш через `EntityGraph.get_if_full()` перед запросом. Сохраняет загруженные DTO в граф. |
| `DictionaryLoader` (`loaders/dictionary_loader.py`) | Загрузка справочников (статусы, типы). Не сохраняет их в граф — это делает `ReferenceStore` (в `data`). |

---

### Список внутренних импортов (только между модулями services и вниз)

**Импорты из `core`**:
- `from src.core.event_bus import EventBus`
- `from src.core.events.definitions import DataLoaded, DataError, DataLoadedKind, ConnectionChanged`
- `from src.core.types import NodeType, NodeIdentifier`
- `from src.core.types.structure import NodeID`

**Импорты из `models`**:
- Все DTO (ComplexTreeDTO, BuildingDetailDTO, …) импортируются в `api_client.py`, `converters.py`, `loaders/*`.

**Импорты из `data`**:
- `from src.data import EntityGraph, EntityGraphStats` (в `data_loader.py`, `physical_loader.py`, `tree_loader.py`)
- `from src.data import ComplexRepository, BuildingRepository, FloorRepository, RoomRepository` (в `context_service.py`)

**Импорты из `shared` и `utils`**:
- `from src.shared.validation import validate_positive_int` (не используется напрямую, но используется в `data`)
- `from utils.logger import get_logger`

**Импорты внутри `services`**:
- В `api_client.py`: `from src.services.api.converters import ...`, `from src.services.api.endpoints import Endpoints`, `from src.services.api.errors import ...`, `from src.services.api.http_client import HttpClient`
- В `data_loader.py`: `from src.services.loaders.tree_loader import TreeLoader`, `from src.services.loaders.physical_loader import PhysicalLoader`, `from src.services.loaders.dictionary_loader import DictionaryLoader`
- В `connection.py`: `from .api_client import ApiClient`
- В `physical_loader.py`: `from .base import BaseLoader`, `from .node_loader import NodeLoader`
- В `tree_loader.py`: аналогично.

**⚠️ Примечание:** слой `services` **не импортирует** `projections`, `controllers`, `view models`, `ui`.

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящие слои (`projections`, `controllers`, `view models`, `ui`) **импортируют из `src.services`**:

#### 1. `ApiClient` — HTTP клиент для бэкенда

| Метод | Назначение |
|-------|-------------|
| `__init__(base_url: Optional[str] = None)` | Создать клиент. |
| `close()` / контекстный менеджер | Закрыть сессию. |
| `get_complexes_tree() -> List[ComplexTreeDTO]` | Загрузить комплексы (Tree). |
| `get_buildings_tree(complex_id) -> List[BuildingTreeDTO]` | Корпуса комплекса. |
| `get_floors_tree(building_id) -> List[FloorTreeDTO]` | Этажи корпуса. |
| `get_rooms_tree(floor_id) -> List[RoomTreeDTO]` | Помещения этажа. |
| `get_complex_detail(complex_id) -> Optional[ComplexDetailDTO]` | Детали комплекса. |
| `get_building_detail(building_id) -> Optional[BuildingDetailDTO]` | Детали корпуса. |
| `get_floor_detail(floor_id) -> Optional[FloorDetailDTO]` | Детали этажа. |
| `get_room_detail(room_id) -> Optional[RoomDetailDTO]` | Детали помещения. |
| `get_building_statuses() -> List[BuildingStatusDTO]` | Справочник статусов зданий. |
| `get_room_statuses() -> List[RoomStatusDTO]` | Справочник статусов помещений. |
| `get_contract_statuses() -> List[ContractStatusDTO]` | Статусы договоров. |
| `get_equipment_statuses() -> List[EquipmentStatusDTO]` | Статусы оборудования. |
| `get_payment_statuses() -> List[PaymentStatusDTO]` | Статусы платежей. |
| `get_placement_statuses() -> List[PlacementStatusDTO]` | Статусы размещения. |
| `get_counterparty_types() -> List[CounterpartyTypeDTO]` | Типы контрагентов. |
| `check_connection(timeout=3) -> bool` | Проверить доступность сервера. |
| `get_server_info() -> dict` | Получить информацию о сервере (версия и т.д.). |

#### 2. `ConnectionService` — мониторинг соединения

| Метод | Назначение |
|-------|-------------|
| `__init__(bus, api, interval_ms=600000)` | Создать сервис (интервал по умолчанию 10 минут). |
| `start()` | Запустить периодическую проверку в фоновом потоке. |
| `stop()` | Остановить проверку. |
| `force_check()` | Принудительно проверить соединение сейчас. |

Генерирует событие `ConnectionChanged(is_online: bool)` при изменении статуса.

#### 3. `ContextService` — сбор контекста для UI

| Метод | Назначение |
|-------|-------------|
| `__init__(complex_repo, building_repo, floor_repo, room_repo)` | Инициализировать с репозиториями из `data`. |
| `get_context(node: NodeIdentifier) -> Dict[str, Any]` | Вернуть словарь с ключами `complex_name`, `building_name`, `floor_num` (если применимо). |
| `get_building_context(building_id: int) -> Dict[str, Any]` | Вернуть контекст для корпуса (включая имя комплекса). |

Используется контроллерами для передачи в ViewModel.

#### 4. `DataLoader` — оркестратор загрузки данных

| Метод | Назначение |
|-------|-------------|
| `__init__(bus, api, graph)` | Создать фасад. |
| `load_complexes_tree() -> List[ComplexTreeDTO]` | Загрузить комплексы (с кэшированием). |
| `load_buildings_tree(complex_id) -> List[BuildingTreeDTO]` | Ленивая загрузка корпусов (с учётом состояния загрузки). |
| `load_floors_tree(building_id) -> List[FloorTreeDTO]` | Ленивая загрузка этажей. |
| `load_rooms_tree(floor_id) -> List[RoomTreeDTO]` | Ленивая загрузка помещений. |
| `load_complex_detail(complex_id) -> Optional[ComplexDetailDTO]` | Загрузить детали (с проверкой кэша). |
| `load_building_detail(building_id) -> Optional[BuildingDetailDTO]` | Аналогично для корпуса. |
| `load_floor_detail(floor_id) -> Optional[FloorDetailDTO]` | Для этажа. |
| `load_room_detail(room_id) -> Optional[RoomDetailDTO]` | Для помещения. |
| `reload_node(node_type, node_id)` | Инвалидировать узел и сбросить состояние загрузки его детей. |
| `clear_cache()` | Полностью очистить кэш графа. |

При успешной загрузке `DataLoader` эмитит события `DataLoaded` (с `kind=CHILDREN` или `DETAILS`), при ошибке — `DataError`.

---

### Итоговое заключение

**Принципы работы со слоем `services`:**

1. **Импорт только из `src.services`** — публичные классы: `ApiClient`, `ConnectionService`, `ContextService`, `DataLoader`. Не импортируйте напрямую из `services.api` или `services.loaders`.

2. **Все HTTP-запросы идут через `ApiClient`** — он возвращает уже готовые DTO (из `models`), а не сырые словари. Ошибки сети преобразуются в иерархию исключений (`ConnectionError`, `TimeoutError`, `NotFoundError`, `ClientError`, `ServerError`).

3. **`DataLoader` — основной инструмент для загрузки данных**:
   - Для дерева используйте методы `load_*_tree`. Они обеспечивают ленивую загрузку, кэширование и предотвращение повторных запросов.
   - Для деталей (панель информации) — `load_*_detail`. Они сначала проверяют `EntityGraph`, и только при отсутствии полных данных идут в API.
   - При ручном обновлении (F5) используйте `reload_node` или `clear_cache`.

4. **`ConnectionService`** запускается один раз при старте приложения. Он сам генерирует события `ConnectionChanged` — подписывайтесь на них в контроллерах для показа офлайн-уведомлений.

5. **`ContextService`** нужен только для формирования имён родителей (например, «Корпус А / Комплекс Солнечный»). Не используйте его для бизнес-логики или загрузки данных.

6. **Исключения** — методы `ApiClient` могут бросать исключения из `services.api.errors`. `DataLoader` ловит их, эмитит `DataError` и пробрасывает дальше. Вышестоящие слои могут ловить `ApiError` для обработки общих сетевых проблем.

7. **Никакой UI-логики** — слой `services` не должен ничего знать о `QWidget`, `QML`, React или любом другом фреймворке. Всё, что он возвращает — это DTO и простые словари (для контекста).

8. **Тестирование** — все зависимости передаются через конструктор. Можно легко подменить `ApiClient` на мок, а `EntityGraph` на тестовую реализацию. `EventBus` также можно замокать для проверки эмитируемых событий.

Слой `services` является **мостиком между «сырыми» HTTP-данными и прикладной логикой**. Он не хранит состояние (кроме чтения кэша через `data`) и не принимает решений о том, что показывать на экране.