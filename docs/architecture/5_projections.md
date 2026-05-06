## Анализ слоя «projections»

### Краткое описание слоя

Слой **projections** отвечает за **преобразование «сырых» данных (DTO, справочники, репозитории) в структуры, удобные для отображения в UI**. Это чистое преобразование без бизнес-логики.

Основные задачи:
- **Дерево** (`TreeProjection`) — строит иерархические узлы `TreeNode` из репозиториев и загруженных DTO. Формирует отображаемые имена (например, «Этаж 3 (12)»). Не занимается загрузкой данных.
- **Узел дерева** (`TreeNode`) — единая структура для всех уровней иерархии. Хранит ссылки на родителя и детей, предоставляет методы навигации (`find_child_by_id`, `row`, `child_at`) и идентификации (`get_identifier`).
- **Детали** (`DetailsProjection`) — преобразует DetailDTO в объект, реализующий протокол `IDetailsViewModel` из `core`. Использует `ReferenceStore` для маппинга ID справочников в человекочитаемые названия. Формирует пары «название поля → значение» для грида.

**Что слой НЕ должен делать:**
- Не выполняет загрузку данных (это `services`).
- Не содержит бизнес-логику (фильтрацию, принятие решений).
- Не обращается к `controllers`, `view models`, `ui`.
- Не управляет состоянием UI (например, выделенными узлами).

---

### Файловая структура слоя

```
src/projections/
├── __init__.py                # Публичное API (TreeProjection, TreeNode, DetailsProjection)
├── tree.py                    # TreeProjection — построение дерева
├── tree_node.py               # TreeNode — узел дерева
└── details_projection.py      # DetailsProjection — преобразование деталей
```

---

### Описание внутренних классов

| Класс | Назначение |
|-------|-------------|
| `TreeNode` | Узел дерева. Содержит `data` (исходный DTO), `_node_type`, `_display_name`, `_has_children`, ссылки на `_parent` и `_children`. Предоставляет свойства `id`, `name`, `has_children`, методы `append_child`, `add_children`, `remove_child`, `find_child_by_id`, `row`, `get_identifier`. |
| `TreeProjection` | Преобразует репозитории и загруженные DTO в иерархию `TreeNode`. Методы: `get_root_nodes()` — корневые узлы (комплексы); `build_children_from_payload(payload, child_type)` — создаёт узлы из списка DTO (корпуса, этажи, помещения). |
| `_DetailsViewModelImpl` (внутренний, не экспортируется) | Реализация протокола `IDetailsViewModel`. Содержит приватные поля `_header_title`, `_header_subtitle`, `_header_status_name`, `_grid_items`. Используется только внутри `DetailsProjection`. |
| `DetailsProjection` | Преобразует DetailDTO (`ComplexDetailDTO`, `BuildingDetailDTO`, `FloorDetailDTO`, `RoomDetailDTO`) в `IDetailsViewModel`. Использует `ReferenceStore` для получения имени статуса. Форматирует даты, площади, типы этажей/помещений. Методы: `build_*_details`. |

---

### Список внутренних импортов

**Из `core`**:
- `from src.core.types import NodeIdentifier, NodeType`
- `from src.core.types.protocols import IDetailsViewModel`

**Из `models`**:
- `from src.models import BuildingDetailDTO, ComplexDetailDTO, FloorDetailDTO, RoomDetailDTO`

**Из `data`**:
- `from src.data import ReferenceStore`
- `from src.data.repositories import BuildingRepository, ComplexRepository, FloorRepository, RoomRepository`

**Из `services`** (только через `data_loader`? нет, в проекциях нет прямого импорта `services`; импортируют только `repositories` из `data`, что разрешено)

**Из `shared`**:
- `from src.shared.time import format_timestamp`

**Внутри `projections`**:
- `from .tree_node import TreeNode` (в `tree.py`)
- `from .details_projection import DetailsProjection` (в `__init__.py`)
- `from .tree import TreeProjection` (в `__init__.py`)

**Внешние утилиты**: `utils.logger`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящие слои (`controllers`, `view models`, `ui`) **импортируют из `src.projections`**:

#### 1. `TreeNode` — узел дерева

| Свойство / Метод | Назначение |
|------------------|-------------|
| `id: int` | Числовой ID узла. |
| `type: str` | Тип узла (complex/building/floor/room). |
| `name: str` | Отображаемое имя (например, «Комплекс Солнечный (3)»). |
| `has_children: bool` | Есть ли дети (для отображения стрелочки). |
| `append_child(child)` / `add_children(children)` | Добавить детей. |
| `remove_child(child)` / `remove_all_children()` | Удалить детей. |
| `child_at(row) -> Optional[TreeNode]` | Доступ по индексу. |
| `child_count() -> int` | Количество детей. |
| `row() -> int` | Индекс в родителе. |
| `find_child_by_id(node_type, node_id) -> Optional[TreeNode]` | Рекурсивный поиск. |
| `get_identifier() -> NodeIdentifier` | Для событий. |

#### 2. `TreeProjection` — построитель дерева

| Метод | Назначение |
|-------|-------------|
| `get_root_nodes() -> List[TreeNode]` | Возвращает список корневых узлов (комплексы) для начального отображения. |
| `build_children_from_payload(payload: List[Any], child_type: NodeType) -> List[TreeNode]` | Создаёт узлы для детей из загруженных DTO (корпуса, этажи, помещения). Не устанавливает родителя. |

#### 3. `DetailsProjection` — преобразование деталей

| Метод | Назначение |
|-------|-------------|
| `build_complex_details(dto: ComplexDetailDTO) -> IDetailsViewModel` | Собрать ViewModel для комплекса. |
| `build_building_details(dto: BuildingDetailDTO) -> IDetailsViewModel` | Для корпуса. |
| `build_floor_details(dto: FloorDetailDTO) -> IDetailsViewModel` | Для этажа. |
| `build_room_details(dto: RoomDetailDTO) -> IDetailsViewModel` | Для помещения. |

Возвращаемый объект гарантированно реализует протокол `IDetailsViewModel` из `core` (свойства `header_title`, `header_subtitle`, `header_status_name`, `grid_items`).

---

### Итоговое заключение

**Принципы работы со слоем `projections`:**

1. **Импорт только из `src.projections`** — используйте `TreeProjection`, `TreeNode`, `DetailsProjection`. Не обращайтесь к внутренним модулям напрямую.

2. **Projections не загружают данные** — перед вызовом `TreeProjection.get_root_nodes()` данные уже должны быть в репозиториях (загружены через `DataLoader`). `build_children_from_payload` вызывается после успешной загрузки детей (обычно по событию `DataLoaded`).

3. **`TreeNode` — мутабельный** (может добавлять/удалять детей), но его поля `id`, `type`, `name` неизменны после создания. Изменение `has_children` косвенно через детей. В UI-слое можно хранить `TreeNode` как модель для виджета дерева.

4. **`DetailsProjection` использует `ReferenceStore`** — перед вызовом `build_*_details` убедитесь, что `ReferenceStore` прогрет (`warmup()` выполнен). В противном случае `status_name` будет `None`.

5. **Никакой бизнес-логики в проекциях** — если нужно отфильтровать список корпусов по владельцу или отсортировать специальным образом, делайте это в `controllers` или `services`, а не здесь.

6. **Тестирование** — проекции легко тестировать, подавая на вход мок-репозитории и DTO. Особое внимание уделите форматированию номеров этажей (отрицательные, ноль) и обработке `None`.

7. **Связь с вышестоящими слоями** — `controllers` будут вызывать `TreeProjection` для построения дерева после загрузки данных, и `DetailsProjection` для подготовки данных панели деталей. `View models` могут использовать `TreeNode` напрямую для отображения, но лучше делегировать контроллеру.

Слой `projections` завершает цепочку подготовки данных перед передачей в `controllers/view models`. Он превращает DTO и справочники в интерфейсы, понятные UI, но остаётся **независимым от конкретного UI-фреймворка**.