## 📁 Идеальная файловая структура Markoff

После анализа всего кода, вот **целевая архитектура**, к которой нужно стремиться. Она устраняет дублирование, четко разделяет ответственность и делает навигацию по проекту интуитивной.

client/
├── src/
│   ├── core/                      # ЯДРО - ничего не знает о внешнем мире
│   │   ├── __init__.py
│   │   ├── event_bus.py           # ✅ Шина событий
│   │   ├── events.py              # ⚠️ РАСШИРИТЬ: все константы событий
│   │   └── types.py               # 🆕 Базовые типы (NodeType и др.)
│   │
│   ├── data/                       # ДАННЫЕ - единый источник правды
│   │   ├── __init__.py
│   │   ├── entity_graph.py         # ✅ ФАСАД графа (на виду!)
│   │   ├── entity_types.py         # ✅ Типы сущностей
│   │   ├── graph/                   # Внутренности графа (скрыты)
│   │   │   ├── __init__.py
│   │   │   ├── store.py             # ✅ EntityStore
│   │   │   ├── relations.py         # ✅ RelationIndex
│   │   │   ├── validity.py          # ✅ ValidityIndex
│   │   │   └── schema.py            # ✅ Схема связей
│   │   └── repositories/            # 🆕 Репозитории (работа с графом)
│   │       ├── __init__.py
│   │       ├── complex_repo.py
│   │       ├── building_repo.py
│   │       └── ...
│   │
│   ├── models/                      # МОДЕЛИ - структуры данных
│   │   ├── __init__.py
│   │   ├── base.py                  # 🆕 Базовый класс
│   │   ├── complex.py               # ✅
│   │   ├── building.py              # ✅
│   │   ├── floor.py                 # ✅
│   │   ├── room.py                   # ✅
│   │   ├── counterparty.py           # ✅
│   │   └── responsible_person.py     # ✅
│   │
│   ├── services/                    # СЕРВИСЫ - оркестрация
│   │   ├── __init__.py
│   │   ├── api_client.py             # ✅ ФАСАД API клиента (на виду!)
│   │   ├── api/                       # Внутренности API (скрыты)
│   │   │   ├── __init__.py
│   │   │   ├── http_client.py         # 🆕 Низкоуровневый HTTP клиент
│   │   │   ├── endpoints.py           # 🆕 Константы эндпоинтов
│   │   │   ├── dto.py                 # 🆕 Объекты передачи данных
│   │   │   └── converters.py          # 🆕 Преобразование DTO → модели
│   │   │
│   │   ├── data_loader.py             # ✅ ФАСАД загрузчика (на виду!)
│   │   ├── loading/                    # Внутренности загрузчика (скрыты)
│   │   │   ├── __init__.py
│   │   │   ├── node_loader.py          # ✅ NodeLoader (ядро)
│   │   │   ├── event_handler.py        # ✅ EventHandler
│   │   │   ├── loader_utils.py         # ✅ LoaderUtils
│   │   │   └── owners.py                # 🆕 Загрузка владельцев
│   │   │
│   │   ├── connection.py               # ✅ ConnectionService
│   │   └── validation/                  # 🆕 Валидация
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       └── rules.py
│   │
│   ├── controllers/                   # КОНТРОЛЛЕРЫ - бизнес-логика
│   │   ├── __init__.py
│   │   ├── base.py                    # ✅ BaseController
│   │   ├── tree_controller.py         # ✅ TreeController
│   │   ├── details_controller.py      # ✅ DetailsController
│   │   ├── refresh_controller.py      # ✅ RefreshController
│   │   └── connection_controller.py   # ✅ ConnectionController
│   │
│   ├── projections/                    # ПРОЕКЦИИ - адаптеры для UI
│   │   ├── __init__.py
│   │   ├── base.py                     # ✅ BaseProjection (убрать Qt)
│   │   └── tree.py                     # ✅ TreeProjection
│   │
│   ├── ui/                              # UI СЛОЙ - только Qt
│   │   ├── __init__.py
│   │   │
│   │   ├── main_window/                  # Главное окно
│   │   │   ├── __init__.py
│   │   │   ├── window.py                  # ✅ MainWindow
│   │   │   ├── components/                
│   │   │   │   ├── __init__.py
│   │   │   │   ├── central_widget.py      # ✅
│   │   │   │   ├── toolbar.py             # ✅
│   │   │   │   └── status_bar.py          # ✅
│   │   │   └── shortcuts.py               # ✅ ShortcutManager
│   │   │
│   │   ├── tree/                          # Дерево объектов
│   │   │   ├── __init__.py
│   │   │   ├── view.py                     # ✅ TreeView
│   │   │   ├── base_view.py                # ✅ TreeViewBase
│   │   │   ├── menu.py                     # ✅ TreeMenu
│   │   │   └── selection.py                # ✅ TreeSelectionUtils
│   │   │
│   │   ├── tree_model/                     # Модель дерева
│   │   │   ├── __init__.py
│   │   │   ├── model.py                     # ✅ TreeModel
│   │   │   ├── base_model.py                # ✅ TreeModelBase
│   │   │   ├── index_mixin.py               # ✅ TreeModelIndexMixin
│   │   │   └── node.py                      # ✅ TreeNode
│   │   │
│   │   ├── details/                         # Панель деталей
│   │   │   ├── __init__.py
│   │   │   ├── panel.py                      # ✅ DetailsPanel
│   │   │   ├── base_panel.py                 # ✅ DetailsPanelBase
│   │   │   ├── header.py                     # ✅ HeaderWidget
│   │   │   ├── placeholder.py                # ✅ PlaceholderWidget
│   │   │   ├── info_grid.py                  # ✅ InfoGrid
│   │   │   ├── tabs.py                       # ✅ DetailsTabs
│   │   │   ├── contact_list.py               # ✅ ContactListWidget
│   │   │   ├── display/                       # Логика отображения
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py                  # ✅ DisplayConfig
│   │   │   │   ├── handlers.py                # ✅ DisplayHandlers
│   │   │   │   └── field_manager.py           # ✅ FieldManager
│   │   │   └── widgets/                        # Доп. виджеты
│   │   │       ├── __init__.py
│   │   │       ├── bank_widget.py
│   │   │       └── ...
│   │   │
│   │   ├── common/                          # Общие UI компоненты
│   │   │   ├── __init__.py
│   │   │   ├── refresh_menu.py               # ✅ RefreshMenu
│   │   │   └── dialogs/
│   │   │       ├── __init__.py
│   │   │       ├── error_dialog.py
│   │   │       └── confirmation_dialog.py
│   │   │
│   │   └── resources/                        # Ресурсы
│   │       ├── styles/
│   │       ├── icons/
│   │       └── translations/
│   │
│   └── utils/                               # УТИЛИТЫ
│       ├── __init__.py
│       ├── logger.py                         # ✅
│       ├── timing.py                         # 🆕
│       ├── compare.py                        # 🆕
│       └── decorators.py                     # 🆕
│
├── tests/                                    # ТЕСТЫ
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── mocks/
│
├── scripts/                                  # Скрипты
│   ├── generate_test_data.py
│   └── check_consistency.py
│
├── logs/                                      # Логи (gitignore)
│
├── main.py                                    # 🚀 Точка входа
├── requirements.txt
├── README.md
└── .gitignore

---

## 📊 Легенда изменений

| Символ | Значение |
|--------|----------|
| ✅ | Уже есть в хорошем состоянии |
| ⚠️ | Нужно расширить/улучшить |
| 🆕 | Нужно создать |
| ❌ | Удалить |
| 🔄 | Переименовать/переместить |

---

## 🎯 Ключевые изменения

### 1. **Убрать дублирование типов**
- `core/types.py` — единый источник для `NodeType`
- Удалить `ui/tree_model/node_types.py`

### 2. **Очистить контроллеры от UI**
- Удалить `ui/main_window/controllers/` — их логика должна быть в основных контроллерах или UI-компонентах
- Контроллеры не должны знать о `QObject`, `QTimer` и т.д.

### 3. **Выделить API в отдельную папку**
- `services/api/` — всё, что связано с HTTP
- Отделить константы эндпоинтов от клиента

### 4. **Создать слой репозиториев**
- `data/repository/` — специализированные запросы к графу
- Инкапсулирует логику типа "найти всех владельцев корпуса"

### 5. **Выделить валидацию**
- `services/validation/` — проверка данных перед сохранением
- Отделить от моделей (SRP)

### 6. **Убрать Qt из проекций**
- `projections/base.py` — не должен наследовать `QObject`
- Таймер должен инжектиться извне

### 7. **Унифицировать названия**
- `tree_view.py` → `tree/view.py`
- `details_panel.py` → `details/panel.py`
- `api_client.py` → `api/client.py`

### 8. **Создать общие утилиты**
- `utils/compare.py` — для сравнения объектов
- `utils/timing.py` — для профилирования
- `utils/decorators.py` — для повторных попыток, кэширования

---

## 🔄 Поток зависимостей (чистая архитектура)

```
Внешний слой (UI, инфраструктура) → Слой приложения (контроллеры) → Слой данных (сущности)

UI (Qt) → Контроллеры (логика) → Сервисы (оркестрация) → Репозитории (доступ) → Граф (данные)
   ↓            ↓                     ↓                        ↓
Проекции ← События ←────────────── EventBus ←───────────────────┘
```

**Правила:**
- UI знает только о проекциях, контроллерах и событиях
- Контроллеры знают только о сервисах, графе и событиях
- Сервисы знают только о репозиториях, API и графе
- Репозитории знают только о графе
- Граф знает только о себе и моделях
- Все общаются через события (EventBus) или интерфейсы

---

## 📈 Метрики идеальной структуры

| Показатель | Цель |
|------------|------|
| Циклических зависимостей | 0 |
| Модулей, знающих о Qt | только `ui/` |
| Модулей, знающих о HTTP | только `services/api/` |
| Мест с определением NodeType | 1 (`core/types.py`) |
| Мест с определением событий | 1 (`core/events.py`) |
| Мест с хранением данных | 1 (`data/entity_graph.py`) |

---

## 🚀 План миграции

1. **Создать новую структуру** параллельно со старой
2. **Перемещать модули по одному**, обновляя импорты
3. **Запускать тесты после каждого перемещения**
4. **Удалять старые файлы** только когда все зависимости обновлены
5. **Фиксить найденные проблемы** по ходу дела

Такая структура сделает код **предсказуемым, тестируемым и поддерживаемым** на годы вперед!