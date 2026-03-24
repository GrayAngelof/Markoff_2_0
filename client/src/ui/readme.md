# ============================================
# СПЕЦИФИКАЦИЯ: UI (Пользовательский интерфейс)
# ВЕРСИЯ: 2.0
# ============================================

## 1. НАЗНАЧЕНИЕ

UI слой — это **визуальное представление приложения**, которое отображает данные пользователю и преобразует действия пользователя в события. UI не содержит бизнес-логики, не загружает данные, не принимает решений — он только показывает и сообщает.

**Ключевая идея:** UI — это **пассивный слой**. Он подписывается на события от контроллеров и отображает полученные View Models. При действиях пользователя он испускает UI-события через EventBus. UI не вызывает сервисы, не вызывает репозитории, не вызывает проекции. **Все изменения в UI (подмена панелей, обновление содержимого) инициируются контроллерами, а не UI.**

---

## 2. ГДЕ ЛЕЖИТ

```
client/src/ui/
├── __init__.py
├── app_window.py                    # 🆕 ФАСАД — сборка главного окна
│
├── main_window/
│   ├── __init__.py
│   ├── window.py                    # Пустая оболочка QMainWindow
│   ├── menu.py                      # Главное меню (постоянный компонент)
│   ├── toolbar.py                   # Панель инструментов (постоянный компонент)
│   └── status_bar.py                # Строка состояния (постоянный компонент)
│
├── common/
│   ├── __init__.py
│   └── central_widget.py            # Разделитель 30/70 с возможностью подмены панелей
│
├── tree/
│   ├── __init__.py
│   ├── view.py                      # TreeView (QTreeView) — подменяемый компонент
│   ├── base_view.py                 # TreeViewBase (общая инициализация)
│   ├── menu.py                      # Контекстное меню
│   └── selection.py                 # Утилиты выделения
│
├── tree_model/                      # Модель дерева (Qt-специфичная)
│   ├── __init__.py
│   ├── model.py                     # TreeModel (QAbstractItemModel)
│   ├── base_model.py                # TreeModelBase
│   ├── index_mixin.py               # TreeModelIndexMixin
│   └── node.py                      # TreeNode
│
├── details/
│   ├── __init__.py
│   ├── panel.py                     # DetailsPanel — подменяемый компонент
│   ├── base_panel.py                # DetailsPanelBase
│   ├── header.py                    # HeaderWidget (иконка, заголовок, статус, иерархия)
│   ├── placeholder.py               # PlaceholderWidget (заглушка)
│   ├── info_grid.py                 # InfoGrid (сетка полей)
│   ├── tabs.py                      # DetailsTabs (вкладки)
│   ├── contact_list.py              # ContactListWidget (контакты)
│   ├── bank_widget.py               # BankWidget (банковские реквизиты)
│   │
│   └── tabs_content/                # Содержимое вкладок
│       ├── __init__.py
│       ├── physics_tab.py           # Вкладка "Физика" (статистика)
│       ├── legal_tab.py             # Вкладка "Юрики" (контакты)
│       └── fire_tab.py              # Вкладка "Пожарка" (датчики + события)
│
├── reference/                       # 🆕 Окна справочников (открываются по навигации)
│   ├── __init__.py
│   ├── base_window.py               # Базовое окно для всех справочников
│   ├── room_types.py                # Типы помещений
│   ├── room_statuses.py             # Статусы помещений
│   ├── counterparty_types.py        # Типы контрагентов
│   ├── role_catalog.py              # Роли ответственных лиц
│   └── contact_categories.py        # Категории контактов
│
├── dialogs/
│   ├── __init__.py
│   ├── about_dialog.py              # "О программе"
│   ├── error_dialog.py              # Диалог ошибки
│   ├── confirmation_dialog.py       # Диалог подтверждения
│   └── list_dialog.py               # Диалог списка (корпуса, этажи, помещения)
│
├── common_components/
│   ├── __init__.py
│   ├── refresh_menu.py              # Меню обновления (F5, Ctrl+F5, Ctrl+Shift+F5)
│   └── card_widget.py               # Кликабельная карточка (для статистики)
│
└── resources/
    ├── styles/
    │   ├── main.css
    │   └── details.css
    └── icons/
        └── ...
```

---

## 3. ЗА ЧТО ОТВЕЧАЕТ

### **Отвечает за:**
- **Постоянные компоненты:** главное меню, панель инструментов, статус бар
- **Изменяемые компоненты:** предоставление места для дерева и панели деталей (через CentralWidget)
- Отображение иерархического дерева объектов (когда контроллер подменит заглушку)
- Отображение детальной информации о выбранном объекте (когда контроллер подменит заглушку)
- Преобразование действий пользователя в UI-события (NodeSelected, NodeExpanded, TabChanged, MenuReferenceRequested, RefreshRequested)
- Отображение заглушек при отсутствии данных
- Визуальную обратную связь (статусы, цвета, индикаторы)

### **НЕ отвечает за:**
- **Создание и подмену панелей** — это делают контроллеры (TreeController, DetailsController)
- **Загрузку данных** (это DataLoader)
- **Хранение данных** (это EntityGraph)
- **Преобразование данных в View Models** (это проекции)
- **Решение, когда обновлять UI** (это контроллер)
- **Бизнес-логику** ("если у корпуса есть владелец, загрузить его")
- **Обработку ошибок** (контроллер эмитит DataError, UI только показывает)
- **Управление состоянием** (выбранный узел, раскрытые узлы — это контроллер)
- **Навигацию** (открытие окон справочников — это NavigationController)

---

## 4. КТО ИСПОЛЬЗУЕТ И КТО СОЗДАЕТ

### **Создают:**
- **bootstrap** — создает AppWindow (фасад) и передает его в контроллеры
- **AppWindow** — создает постоянные компоненты (MenuBar, Toolbar, StatusBar, CentralWidget с заглушками)

### **Подменяют панели:**
- **TreeController** — после загрузки комплексов создает TreeView и вызывает `app_window.set_left_panel()`
- **DetailsController** — при выборе узла создает DetailsPanel и вызывает `app_window.set_right_panel()`

### **Вызывают (эмитят события):**
- **MenuBar** — эмитит `MenuReferenceRequested`, `MenuHelpAbout`, `MenuFileExit`
- **Toolbar** — эмитит `RefreshRequested`, `ModeChanged`
- **TreeView** — эмитит `NodeSelected`, `NodeExpanded`, `NodeCollapsed`
- **DetailsPanel** — эмитит `TabChanged`

### **Подписываются на события:**
- **StatusBar** — подписывается на `ConnectionChanged`, `DataLoading`, `DataLoaded`, `DataError`
- **Toolbar** — подписывается на `ConnectionChanged`, `NetworkActionsEnabled`, `NetworkActionsDisabled`
- **PhysicsTab, LegalTab, FireTab** — подписываются на соответствующие `*Updated` события

### **НЕ используют:**
- UI не вызывает контроллеры напрямую
- UI не вызывает проекции
- UI не вызывает DataLoader
- UI не вызывает репозитории
- UI не обращается к EntityGraph

---

## 5. КЛЮЧЕВЫЕ ПОНЯТИЯ

| Термин | Значение |
|--------|----------|
| **Постоянные компоненты** | MenuBar, Toolbar, StatusBar — всегда видны, создаются один раз в AppWindow |
| **Изменяемые компоненты** | Левая панель (дерево) и правая панель (детали) — могут подменяться контроллерами |
| **AppWindow** | Фасад UI слоя. Собирает постоянные компоненты, создает CentralWidget с заглушками, предоставляет методы `set_left_panel()` и `set_right_panel()` |
| **CentralWidget** | Разделитель 30/70. Не знает, что слева и справа. Предоставляет методы для подмены панелей |
| **UI-событие** | Событие, инициируемое UI (NodeSelected, NodeExpanded, MenuReferenceRequested) |
| **Событие от контроллера** | Событие, содержащее View Model (StatisticsUpdated, ContactsUpdated) |
| **Заглушка (Placeholder)** | Отображение "—" или "нет данных" при отсутствии информации |
| **Пассивность** | UI не принимает решений, только отображает и сообщает |
| **Реактивность** | UI обновляется автоматически при получении событий |

---

## 6. ОГРАНИЧЕНИЯ (ВАЖНО!)

### **Запрещено:**
1. **Вызывать контроллеры напрямую**
   - ❌ `self._controller.do_something()`
   - ✅ `self._bus.emit(NodeSelected(...))`

2. **Вызывать проекции напрямую**
   - ❌ `self._stats_proj.build(...)`
   - ✅ Только контроллеры вызывают проекции

3. **Вызывать DataLoader напрямую**
   - ❌ `self._loader.load_details(...)`
   - ✅ Только контроллеры вызывают DataLoader

4. **Хранить данные (кроме View Models для отображения)**
   - ❌ `self._buildings: List[Building] = []`
   - ✅ Получаем View Models из событий, сразу отображаем

5. **Содержать бизнес-логику**
   - ❌ `if building.owner_id: self.load_owner()`
   - ✅ Только контроллеры содержат логику

6. **Принимать решения о загрузке данных**
   - ❌ "данных нет, надо загрузить"
   - ✅ UI показывает заглушку, контроллер решает, загружать или нет

7. **Знать о существовании репозиториев**
   - ❌ Импорт `data.repositories`
   - ✅ Только `view_models`, `core`, `utils.logger`

8. **Создавать или подменять панели самостоятельно**
   - ❌ UI решает, когда создать TreeView
   - ✅ Контроллеры вызывают `app_window.set_left_panel()` и `app_window.set_right_panel()`

---

## 7. АРХИТЕКТУРНЫЕ КОМПОНЕНТЫ

### **7.1. AppWindow (фасад)**

| Метод | Назначение |
|-------|------------|
| `__init__(bus)` | Создает постоянные компоненты и CentralWidget с заглушками |
| `get_window()` | Возвращает QMainWindow для отображения |
| `set_left_panel(widget)` | Подменяет левую панель (вызывается контроллерами) |
| `set_right_panel(widget)` | Подменяет правую панель (вызывается контроллерами) |

**AppWindow НЕ ЗНАЕТ:**
- Кто и когда вызывает set_left_panel
- Что будет в левой панели (дерево или что-то другое)
- Как устроены TreeView и DetailsPanel

### **7.2. CentralWidget (разделитель)**

| Метод | Назначение |
|-------|------------|
| `__init__()` | Создает QSplitter с заглушками |
| `set_left(widget)` | Заменяет левую панель |
| `set_right(widget)` | Заменяет правую панель |
| `central_widget` (property) | Возвращает QWidget для установки в MainWindow |

### **7.3. Постоянные компоненты**

| Компонент | Создает | Эмитит события |
|-----------|---------|----------------|
| **MenuBar** | Пункты меню | `MenuReferenceRequested`, `MenuHelpAbout`, `MenuFileExit` |
| **Toolbar** | Кнопки | `RefreshRequested`, `ModeChanged` |
| **StatusBar** | Индикатор | — (подписывается на события) |

### **7.4. Изменяемые компоненты**

| Компонент | Создается | Подменяется |
|-----------|-----------|-------------|
| **TreeView** | TreeController после загрузки комплексов | `app_window.set_left_panel()` |
| **DetailsPanel** | DetailsController при выборе узла | `app_window.set_right_panel()` |

---

## 8. ПОДПИСКИ UI НА СОБЫТИЯ

| Компонент | Подписывается на события | Что делает |
|-----------|-------------------------|------------|
| **StatusBar** | `ConnectionChanged`, `DataLoading`, `DataLoaded`, `DataError` | Показывает статус и сообщения |
| **Toolbar** | `ConnectionChanged`, `NetworkActionsEnabled`, `NetworkActionsDisabled` | Обновляет индикаторы, блокирует кнопки |
| **PhysicsTab** | `StatisticsUpdated` | Отображает статистику |
| **LegalTab** | `ContactsUpdated` | Отображает контакты |
| **FireTab** | `SensorsUpdated`, `EventsUpdated` | Отображает датчики и события |
| **ListDialog** | `ListUpdated` | Отображает список |

---

## 9. СОБЫТИЯ, КОТОРЫЕ UI ЭМИТИТ

| Событие | Источник | Когда | Данные |
|---------|----------|-------|--------|
| `NodeSelected` | TreeView | Клик на узле | `node: NodeIdentifier` |
| `NodeExpanded` | TreeView | Раскрытие узла | `node: NodeIdentifier` |
| `NodeCollapsed` | TreeView | Сворачивание узла | `node: NodeIdentifier` |
| `TabChanged` | DetailsPanel | Переключение вкладки | `tab_index: int` |
| `RefreshRequested` | Toolbar / Menu | Нажатие F5 | `mode: str` ("current", "visible", "full") |
| `ModeChanged` | Toolbar | Переключение режима | `mode: str` ("read_only", "edit") |
| `MenuReferenceRequested` | MenuBar | Выбор справочника | `reference: str` |
| `MenuHelpAbout` | MenuBar | Выбор "О программе" | — |
| `MenuFileExit` | MenuBar | Выбор "Выход" | — |
| `ListRequested` | Карточка статистики | Клик на карточку | `filter_type: str`, `parent_id: int` |
| `EventsListRequested` | FireTab | Клик "все события" | `node: NodeIdentifier` |

---

## 10. ПРИНЦИПЫ РАБОТЫ

### **1. Пассивность**
```python
# ❌ Неправильно: UI решает, что делать
def on_button_click(self):
    self._loader.load_complexes()

# ✅ Правильно: UI сообщает о действии
def on_button_click(self):
    self._bus.emit(RefreshRequested(mode="full"))
```

### **2. Реактивность**
```python
# UI подписывается на события и обновляется
def __init__(self):
    self._bus.subscribe(StatisticsUpdated, self._on_statistics)

def _on_statistics(self, event):
    vm = event.data
    self.label.setText(str(vm.total_buildings))
```

### **3. Контроллеры управляют подменой панелей**
```python
# В TreeController после загрузки комплексов:
self._app_window.set_left_panel(tree_view)

# В DetailsController при выборе узла:
self._app_window.set_right_panel(details_panel)
```

### **4. Заглушки вместо None**
```python
# View Model всегда есть, даже если данных нет
def _on_statistics(self, event):
    vm = event.data
    if vm.total_buildings == 0:
        self.label.setText("—")  # заглушка
    else:
        self.label.setText(str(vm.total_buildings))
```

### **5. Нет состояния**
```python
# UI не хранит данные между обновлениями
class PhysicsTab:
    def __init__(self):
        # ❌ Нет self._statistics
        # ✅ Данные приходят в событиях, сразу отображаются
        pass
```

---

## 11. РИСКИ

| Риск | Вероятность | Смягчение |
|------|-------------|-----------|
| **UI начинает хранить состояние** | Средняя | Code review, проверка на отсутствие полей-данных |
| **UI вызывает сервисы напрямую** | Средняя | Архитектурный контроль, запрет импортов |
| **Контроллер не получает ссылку на AppWindow** | Низкая | bootstrap передает AppWindow в контроллеры через `set_app_window()` |
| **Слишком много подписок → утечки памяти** | Средняя | BaseController решает проблему, UI должен отписываться |
| **UI "запоминает" предыдущие данные** | Средняя | При каждом обновлении полностью перерисовывать вкладку |

---

## 12. ВЗАИМОДЕЙСТВИЕ С ДРУГИМИ СЛОЯМИ

### **Схема инициализации:**
```
bootstrap
    ↓
AppWindow(bus) — создает постоянные компоненты + CentralWidget с заглушками
    ↓
bootstrap передает AppWindow в контроллеры (set_app_window)
    ↓
DataLoader загружает комплексы
    ↓
TreeController получает DataLoaded
    ↓
TreeController создает TreeView → вызывает app_window.set_left_panel()
    ↓
Пользователь выбирает узел
    ↓
DetailsController получает NodeSelected
    ↓
DetailsController создает DetailsPanel → вызывает app_window.set_right_panel()
```

### **Схема навигации (справочники):**
```
Пользователь кликает "Справочники → Типы помещений"
    ↓
MenuBar эмитит MenuReferenceRequested(reference="room_types")
    ↓
NavigationController (подписан) получает событие
    ↓
NavigationController создает RoomTypesWindow и показывает его
```

### **Схема данных:**
```
Пользователь кликает на узел
    ↓
TreeView эмитит NodeSelected
    ↓
EventBus доставляет событие
    ↓
TreeController → сохраняет состояние
DetailsController → вызывает проекции → эмитит StatisticsUpdated
    ↓
PhysicsTab получает StatisticsUpdated → обновляет отображение
```

**UI НЕ знает:**
- Кто обрабатывает NodeSelected
- Как вычисляется StatisticsViewModel
- Откуда берутся данные
- Кто и когда подменяет панели

**UI ЗНАЕТ:**
- На какие события подписываться
- Как отображать View Models
- Какие события эмитить
- Что у него есть методы set_left_panel/set_right_panel (которые вызывают контроллеры)

---

## 13. ИТОГ

UI слой — это **чистый, пассивный, реактивный интерфейс**, который:

- ✅ Не содержит бизнес-логики
- ✅ Не загружает данные
- ✅ Не хранит состояние (кроме временного отображения)
- ✅ Не принимает решений о подмене панелей
- ✅ Только отображает View Models
- ✅ Только эмитит UI-события
- ✅ Подписывается на события от контроллеров
- ✅ Показывает заглушки при отсутствии данных
- ✅ Предоставляет методы для подмены панелей (которые вызывают контроллеры)

**Это позволяет:**
- UI не зависеть от того, как устроены данные
- Контроллерам управлять жизненным циклом панелей
- Легко тестировать UI изолированно (с мок-событиями)
- Менять логику получения данных без изменения UI
- Сохранять предсказуемость и отлаживаемость

---

# ============================================
# КОНЕЦ СПЕЦИФИКАЦИИ
# ============================================