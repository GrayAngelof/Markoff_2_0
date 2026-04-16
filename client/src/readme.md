# Корень приложения — описание слоя

## Назначение

Точка входа и композиционный корень приложения. Собирает все слои в правильном порядке, настраивает зависимости (DI), запускает сервисы.

**Строгая зависимость:** от всех слоёв (`core`, `models`, `data`, `services`, `projections`, `controllers`, `ui`). Никаких обратных импортов.

---

## Структура

```
src/
├── __init__.py              # Корневой пакет (пустой)
├── bootstrap.py             # ApplicationBootstrap — композиционный корень
└── main.py                  # Точка входа
```

---

## Компоненты

### 1. `main.py` — точка входа

Запускает приложение, настраивает окружение и логирование.

| Функция | Описание |
|---------|----------|
| `setup_application()` | Создаёт `QApplication`, устанавливает имя и организацию |
| `setup_logging()` | Настраивает уровни логирования (DEBUG при разработке) |
| `main()` | Точка входа — инициализация, запуск цикла, очистка |

**Порядок запуска:**
1. Установка `QT_LOGGING_RULES` (подавление шума Qt)
2. Настройка логирования
3. Создание `QApplication`
4. Создание `ApplicationBootstrap`
5. Получение и отображение окна
6. Запуск `app.exec()`
7. Очистка ресурсов

---

### 2. `ApplicationBootstrap` (`bootstrap.py`) — композиционный корень

Создаёт все компоненты в строгом порядке сверху вниз.

#### Порядок инициализации

| Шаг | Слой | Компоненты |
|-----|------|------------|
| 1 | Core | `EventBus` |
| 2 | Data | `EntityGraph`, репозитории (Complex, Building, Floor, Room, Counterparty, ResponsiblePerson) |
| 3 | Services | `ApiClient`, `DataLoader`, `ContextService`, `ConnectionService` |
| 4 | Projections | `TreeProjection` |
| 5 | Controllers | `TreeController`, `DetailsController`, `RefreshController`, `ConnectionController` |
| 6 | UI | `AppWindow` |
| 7 | Запуск сервисов | `ConnectionService.start()`, `load_root_nodes()` |

#### Методы

| Метод | Описание |
|-------|----------|
| `__init__(app)` | Создаёт все компоненты в правильном порядке |
| `cleanup()` | Останавливает сервисы, очищает контроллеры, шину, граф |
| `get_window()` | Возвращает `QMainWindow` для отображения |
| `get_bus()` | Возвращает `EventBus` (для отладки) |

#### Внутренние методы (шаги инициализации)

| Метод | Что создаёт |
|-------|-------------|
| `_init_core()` | `EventBus` (debug=True) |
| `_init_data()` | `EntityGraph`, 6 репозиториев |
| `_init_services()` | `ApiClient`, `DataLoader`, `ContextService`, `ConnectionService` |
| `_init_projections()` | `TreeProjection` |
| `_init_controllers()` | Tree, Details, Refresh, Connection контроллеры |
| `_init_ui()` | `AppWindow`, связывает контроллеры с UI |
| `_start_services()` | Запускает `ConnectionService`, вызывает `load_root_nodes()` |

#### Связывание контроллеров с UI

```python
# TreeController → AppWindow
self._tree_controller.set_app_window(self._app_window)

# DetailsController → DetailsPanel
details_panel = self._app_window.get_details_panel()
self._details_controller.set_details_panel(details_panel)
```

---

## Зависимости (все импорты)

### `bootstrap.py` импортирует:

| Слой | Компоненты |
|------|------------|
| `controllers` | `ConnectionController`, `DetailsController`, `RefreshController`, `TreeController` |
| `core` | `EventBus` |
| `data` | `EntityGraph`, 6 репозиториев |
| `projections` | `TreeProjection` |
| `services` | `ApiClient`, `ConnectionService`, `ContextService`, `DataLoader` |
| `ui` | `AppWindow` |
| `utils.logger` | `get_logger` |

### `main.py` импортирует:

| Модуль | Компоненты |
|--------|------------|
| `src.bootstrap` | `ApplicationBootstrap` |
| `utils.logger` | `Logger`, `get_logger` |
| `PySide6.QtWidgets` | `QApplication` |

---

## Итог

Корень приложения предоставляет:

| Возможность | Через |
|-------------|-------|
| Точка входа | `main.py` |
| Композиционный корень (DI) | `ApplicationBootstrap` |
| Жизненный цикл приложения | инициализация → запуск → очистка |
| Измерение времени инициализации | `log.measure_time()` |
| Единое место очистки ресурсов | `cleanup()` |

**Принципы:**
- `main.py` — только запуск, вся логика в `bootstrap.py`
- Строгий порядок инициализации сверху вниз (core → models → data → services → projections → controllers → ui)
- Все зависимости передаются явно (DI, нет глобальных переменных)
- Единая точка очистки ресурсов при завершении
- Измерение времени каждого этапа для отладки производительности