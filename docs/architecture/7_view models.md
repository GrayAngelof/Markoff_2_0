## Анализ слоя «view models»

### Краткое описание слоя

Слой **view models** — это **набор иммутабельных контейнеров данных**, которые передаются из бизнес-логики (контроллеров/проекций) непосредственно в UI. Его задачи:

- **Предоставить единый контракт** для отображения данных в UI (панель деталей).
- **Изолировать UI от бизнес-логики** — UI работает только с этими ViewModel, не зависит от DTO или репозиториев.
- **Обеспечить иммутабельность** — все ViewModel являются `@dataclass(frozen=True, slots=True)`, что гарантирует неизменность данных при передаче между потоками и предсказуемость обновлений.

**Что слой НЕ должен делать:**
- Не содержит бизнес-логику (преобразования, вычисления, вызовы API).
- Не зависит от core, data, services, projections, controllers (кроме структурной совместимости с протоколами core). На практике он может импортировать протоколы из core для явной типизации, но в приведённом коде это не требуется.
- Не взаимодействует с UI напрямую (только данные).

---

### Файловая структура слоя

```
src/view_models/
├── __init__.py        # Публичное API (DetailsViewModel, HeaderViewModel, InfoGridItem)
└── details.py         # Определения ViewModel для панели деталей
```

---

### Описание всех классов

Все ViewModel иммутабельны (`frozen=True, slots=True`). Они не имеют методов (кроме property для совместимости с `IDetailsViewModel`).

| Класс | Назначение |
|-------|-------------|
| `HeaderViewModel` | Модель заголовка панели деталей. Поля: `title` (название объекта), `subtitle` (тип объекта, например «КОМПЛЕКС»), `status_name` (название статуса, опционально). |
| `InfoGridItem` | Одна запись в таблице/сетке деталей. Поля: `label` (название поля, например «ID»), `value` (значение, строка). |
| `DetailsViewModel` | Полная ViewModel панели деталей. Содержит `header: HeaderViewModel` и `grid: List[InfoGridItem]`. <br> Реализует протокол `IDetailsViewModel` из `core` через свойства-делегаты: `header_title`, `header_subtitle`, `header_status_name`, `grid_items` (возвращает `List[Tuple[str, str]]`). |

---

### Список внутренних импортов

Слой `view_models` **не имеет внутренних импортов из других модулей приложения**. Он использует только стандартную библиотеку Python:
- `from dataclasses import dataclass, field`
- `from typing import List, Optional, Tuple`

Никаких импортов из `core`, `models`, `data`, `services`, `projections`, `controllers`, `ui`.

---

### Экспортируемые методы / классы для вышестоящих слоёв

Вышестоящий слой (`ui`) **импортирует из `src.view_models`**:

#### 1. `HeaderViewModel`

```python
@dataclass(frozen=True, slots=True)
class HeaderViewModel:
    title: str
    subtitle: str
    status_name: Optional[str] = None
```

#### 2. `InfoGridItem`

```python
@dataclass(frozen=True, slots=True)
class InfoGridItem:
    label: str
    value: str
```

#### 3. `DetailsViewModel`

```python
@dataclass(frozen=True, slots=True)
class DetailsViewModel:
    header: HeaderViewModel
    grid: List[InfoGridItem] = field(default_factory=list)

    # Свойства для совместимости с IDetailsViewModel
    @property
    def header_title(self) -> str: ...
    @property
    def header_subtitle(self) -> str: ...
    @property
    def header_status_name(self) -> Optional[str]: ...
    @property
    def grid_items(self) -> List[Tuple[str, str]]: ...
```

UI использует эти классы для отображения данных. Например:
- Заголовок панели получает `title`, `subtitle`, `status_name` из `DetailsViewModel.header`.
- Сетка (таблица) отображает каждый `InfoGridItem` как строку «label: value».

---

### Итоговое заключение

**Принципы работы со слоем `view_models`:**

1. **Импорт только из `src.view_models`** — используйте `DetailsViewModel`, `HeaderViewModel`, `InfoGridItem`. Не пытайтесь создавать ViewModel вручную в UI (они должны создаваться в слое `controllers` или `projections`).

2. **ViewModel иммутабельны** — после создания их нельзя изменить. Для обновления данных создаётся новый экземпляр, который передаётся через событие (например, `NodeDetailsLoaded`). Это упрощает реактивное обновление UI.

3. **Структурная совместимость с `core.IDetailsViewModel`** — `DetailsViewModel` не наследуется от протокла явно, но предоставляет все необходимые свойства. Это позволяет использовать его в любом месте, где ожидается `IDetailsViewModel`, без жёсткой привязки к протоколу.

4. **Никакой логики форматирования** — строки в `label` и `value` уже должны быть готовы к отображению (локализованы, отформатированы). Форматирование выполняется в слое `projections` или `controllers`.

5. **Тестирование** — ViewModel — это простые структуры данных, их тестирование сводится к проверке корректности заполнения полей. Сложность в том, чтобы убедиться, что они соответствуют ожиданиям UI, но это достигается через контракты.

Слой `view_models` завершает цепочку подготовки данных: от DTO (models) через сервисы (services), проекции (projections), контроллеры (controllers) до чистых, неизменяемых контейнеров для отображения (view models). UI слой может работать с ними напрямую, не имея доступа к бизнес-логике или данным.