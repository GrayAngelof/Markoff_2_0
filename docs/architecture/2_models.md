## Анализ слоя: **models** (DTO слой данных)

### Краткое описание слоя

**Назначение** – определить иммутабельные DTO (Data Transfer Objects) для всех сущностей системы. Слой `models` содержит **только данные**, никакой бизнес-логики или UI-специфичного кода. DTO служат строгим контрактом между API бекенда и клиентским приложением.

**Что делает:**
- Определяет древовидные DTO (`*TreeDTO`) – минимальные данные для отображения в дереве
- Определяет детальные DTO (`*DetailDTO`) – полные данные для панели деталей
- Предоставляет фабричные методы `from_dict()` для десериализации из API-ответов
- Обеспечивает иммутабельность (`frozen=True`) для безопасного кэширования и передачи между компонентами
- Реализует сравнение объектов по уникальному ключу (тип + id)

**Что не должен делать:**
- Содержать бизнес-логику (валидацию, вычисления, преобразования)
- Импортировать что-либо из `data`, `services`, `projections`, `controllers`, `ui`
- Содержать ссылки на UI-компоненты или логику отображения
- Мутировать состояние после создания
- Обращаться к API, БД или внешним сервисам

---

### Файловая структура слоя

```
client/src/models/
├── __init__.py                    # Публичное API моделей (экспорт всех DTO)
├── base.py                        # BaseDTO – базовый класс для всех DTO
├── mixins.py                      # DateTimeMixin – работа с датами
├── complex.py                     # ComplexTreeDTO, ComplexDetailDTO
├── building.py                    # BuildingTreeDTO, BuildingDetailDTO
├── floor.py                       # FloorTreeDTO, FloorDetailDTO
└── room.py                        # RoomTreeDTO, RoomDetailDTO
```

---

### Внутренние классы (кратко)

| Класс | Модуль | Назначение |
|-------|--------|------------|
| `BaseDTO` | `base.py` | Абстрактный базовый DTO. Обеспечивает иммутабельность, сравнение по `(NODE_TYPE, id)`, хеширование и строковое представление. |
| `DateTimeMixin` | `mixins.py` | Примесь для работы с датами. Добавляет поля `created_at`, `updated_at` и статический метод `parse_datetime()` для парсинга ISO дат из API. |
| `ComplexTreeDTO` | `complex.py` | Минимальные данные комплекса для отображения в дереве (`id`, `name`, `buildings_count`). |
| `ComplexDetailDTO` | `complex.py` | Полные данные комплекса для панели деталей (включая `description`, `address`, `owner_id`, `status_id`, даты). |
| `BuildingTreeDTO` | `building.py` | Минимальные данные корпуса для дерева (`id`, `name`, `complex_id`, `floors_count`). |
| `BuildingDetailDTO` | `building.py` | Полные данные корпуса для панели деталей (включая `description`, `address`, `owner_id`, `status_id`, даты). |
| `FloorTreeDTO` | `floor.py` | Минимальные данные этажа для дерева (`id`, `number`, `building_id`, `rooms_count`). |
| `FloorDetailDTO` | `floor.py` | Полные данные этажа для панели деталей (включая `description`, `physical_type_id`, `status_id`, `plan_image_url`, даты). |
| `RoomTreeDTO` | `room.py` | Минимальные данные помещения для дерева (`id`, `number`, `floor_id`, `area`). |
| `RoomDetailDTO` | `room.py` | Полные данные помещения для панели деталей (включая `description`, `physical_type_id`, `status_id`, `max_tenants`, даты). |

---

### Внутренние импорты (только между модулями models)

**Из `complex.py`, `building.py`, `floor.py`, `room.py`:**
- `from .base import BaseDTO`
- `from .mixins import DateTimeMixin`

**Из `mixins.py`:**
- (нет внутренних импортов models – только `utils.logger`)

**Из `base.py`:**
- (нет внутренних импортов models)

**Из `__init__.py` (публичный фасад):**
- `from .complex import ComplexTreeDTO, ComplexDetailDTO`
- `from .building import BuildingTreeDTO, BuildingDetailDTO`
- `from .floor import FloorTreeDTO, FloorDetailDTO`
- `from .room import RoomTreeDTO, RoomDetailDTO`

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вся публичная поверхность слоя `models` доступна через импорт из `src.models` (согласно `models/__init__.py`):

**Базовые классы (доступны через полный путь, но редко нужны выше):**
- `BaseDTO` – от него наследуются все DTO (обычно не используется напрямую)
- `DateTimeMixin` – для работы с датами (обычно не используется напрямую)

**Tree DTO (для слоёв `data`, `services`, `projections`):**
- `ComplexTreeDTO` – комплексы в дереве
- `BuildingTreeDTO` – корпуса в дереве
- `FloorTreeDTO` – этажи в дереве
- `RoomTreeDTO` – помещения в дереве

**Detail DTO (для слоёв `data`, `services`, `projections`):**
- `ComplexDetailDTO` – детальная информация о комплексе
- `BuildingDetailDTO` – детальная информация о корпусе
- `FloorDetailDTO` – детальная информация об этаже
- `RoomDetailDTO` – детальная информация о помещении

**Каждый DTO предоставляет:**
- Конструктор через `__init__(id=..., name=..., ...)` – все поля обязательны, кроме опциональных
- Фабричный метод `from_dict(cls, data: dict) -> DTO` – строгая десериализация
- Метод `key(self) -> Tuple[str, int]` – уникальный ключ `(NODE_TYPE, id)`
- Иммутабельность (нельзя изменить после создания)
- Автоматическое сравнение и хеширование по `key()`
- Строковое представление для отладки: `ComplexTreeDTO[TREE](key=('complex', 42))`

---

### Итоговое заключение: принципы работы со слоем `models`

1. **Импорт только сверху вниз** – вышестоящие слои (`data`, `services`, `projections`, `controllers`, `ui`) могут импортировать из `models` свободно. Слой `models` может импортировать только:
   - `core` – для типов (`NodeType`, `NodeIdentifier` – **но в текущей реализации не импортирует, т.к. NODE_TYPE задан строкой**)
   - Внутренние модули (`base`, `mixins`)
   - Внешние утилиты (`utils.logger` – только в `mixins.py`)

   **Важное замечание:** В текущей реализации `NODE_TYPE` объявлен как `ClassVar[str] = "complex"`, а не `ClassVar[NodeType] = NodeType.COMPLEX`. Это допустимо (избегает циклической зависимости), но требует согласованности строковых значений с `core.types.nodes.NodeType`.

2. **Запрещены импорты из `models` в обратную сторону** – код внутри `models` не должен импортировать ничего из `data`, `services`, `projections`, `controllers`, `ui`.

3. **Используйте публичное API через `src.models`** – все DTO доступны оттуда:
   ```python
   from src.models import ComplexTreeDTO, BuildingDetailDTO
   ```

4. **Создавайте DTO только через `from_dict()`** – фабричный метод обеспечивает строгую десериализацию и обработку опциональных полей:
   ```python
   complex_tree = ComplexTreeDTO.from_dict(api_response)
   ```

5. **Не создавайте DTO вручную через конструктор** – конструктор предназначен для внутреннего использования фабрикой. Исключение – тесты или фабрики данных.

6. **Строгий контракт десериализации**:
   - Обязательные поля (`id`, `name`, `number`, `complex_id` и т.д.) берутся через `data["field"]` – при отсутствии выбрасывается `KeyError`
   - Опциональные поля через `data.get()` с защитой от неправильных типов
   - Числовые поля с защитой от `None` и некорректных значений

7. **Иммутабельность гарантирует безопасность**:
   - DTO можно безопасно кэшировать в `EntityGraph`
   - DTO можно передавать между компонентами без риска случайной модификации
   - DTO можно использовать как ключи в словарях и элементах множеств

8. **Сравнение и хеширование** – два DTO считаются равными, если у них одинаковые `(NODE_TYPE, id)`. Это позволяет:
   - `ComplexTreeDTO(id=1) == ComplexDetailDTO(id=1)` – `True` (разные типы DTO, но одна сущность)
   - `ComplexTreeDTO(id=1) != BuildingTreeDTO(id=1)` – `True` (разные типы сущностей)

9. **Разделение Tree и Detail DTO** – важный архитектурный паттерн:
   - `TreeDTO` – минимальные поля для производительности (дерево может содержать тысячи узлов)
   - `DetailDTO` – полные данные для детального просмотра (загружаются по требованию)

10. **Обработка дат** – используйте `DateTimeMixin.parse_datetime()` для парсинга ISO дат из API. Метод нормализует `'Z'` в `'+00:00'` для совместимости с `datetime.fromisoformat()`.

11. **Логирование** – допустимо использовать `utils.logger` только в `mixins.py` для логирования ошибок парсинга дат. В остальных DTO логирование не требуется.

Слой `models` является **единственным источником истины** для структуры данных в приложении. Любое изменение API бекенда должно отражаться только в этом слое. Вышестоящие слои работают только с DTO из этого слоя, не зная о внутреннем формате API-ответов.