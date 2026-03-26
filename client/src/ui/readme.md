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

## 📚 **ОПИСАНИЕ СЛОЯ UI**

В соответствии с архитектурой, UI слой — это **чистое, пассивное, реактивное представление приложения**. Он не содержит бизнес-логики, не загружает данные, не принимает решений. UI только отображает View Models, подписывается на события от контроллеров и эмитит UI-события при действиях пользователя.

Код организован в следующую структуру каталогов:

```
ui/
├── __init__.py                    # Публичное API (экспорт AppWindow)
├── app_window.py                  # Фасад UI слоя (сборка окна)
│
├── main_window/                   # Постоянные компоненты окна
│   ├── __init__.py
│   ├── window.py                  # Пустая оболочка QMainWindow
│   ├── menu.py                    # Главное меню (Файл, Справочники, Помощь)
│   ├── toolbar.py                 # Панель инструментов (Обновить, Режим работы)
│   └── status_bar.py              # Строка состояния (индикатор соединения)
│
├── common/                        # Общие компоненты
│   ├── __init__.py
│   └── central_widget.py          # Разделитель 30/70 с подменой панелей
│
├── tree/                          # Дерево объектов
│   ├── __init__.py
│   ├── node.py                    # TreeNode (структура узла)
│   ├── model.py                   # TreeModel (QAbstractItemModel)
│   └── view.py                    # TreeView (QTreeView, эмиссия событий)
│
└── details/                       # Панель деталей (в разработке)
    ├── __init__.py
    ├── panel.py                   # DetailsPanel (главная панель)
    ├── header.py                  # HeaderWidget (иконка, заголовок, статус)
    ├── placeholder.py             # PlaceholderWidget (заглушка)
    ├── info_grid.py               # InfoGrid (сетка полей)
    ├── tabs.py                    # DetailsTabs (вкладки)
    └── display/                   # Логика отображения (в разработке)
```

---

## 📦 **Публичное API (минималистичный подход)**

UI экспортирует **только фасад**. Всё остальное — внутренняя реализация:

```python
# Основной фасад (экспортируется из ui)
from src.ui import AppWindow

# Внутренние компоненты не экспортируются и не предназначены для внешнего использования
# from src.ui.tree.view import TreeView  # ❌ НЕПРАВИЛЬНО
# from src.ui.main_window.menu import MenuBar  # ❌ НЕПРАВИЛЬНО
```

---

## 🔹 **AppWindow — фасад UI слоя**

```python
from src.ui import AppWindow

app_window = AppWindow(bus)
```

| Метод | Возврат | Описание |
|-------|---------|----------|
| `__init__(bus)` | — | Создает окно, постоянные компоненты и CentralWidget |
| `get_window()` | `QMainWindow` | Возвращает QMainWindow для отображения |
| `set_right_panel(widget)` | — | Заменяет правую панель (вызывается контроллерами) |
| `get_tree_view()` | `TreeView` | Возвращает TreeView для установки модели |

**Ответственность:**
- Создание пустого MainWindow
- Создание постоянных компонентов (MenuBar, Toolbar, StatusBar)
- Создание CentralWidget с TreeView (сразу) и заглушкой справа
- Компоновка всех компонентов в окне
- Предоставление методов для подмены панелей (прокси к CentralWidget)

**НЕ отвечает за:**
- Создание DetailsPanel
- Решение, когда подменять панели

---

## 🔹 **Постоянные компоненты (main_window/)**

### **MainWindow — пустая оболочка**

```python
# ui/main_window/window.py

class MainWindow(QMainWindow):
    """
    Пустая оболочка главного окна.
    Отвечает только за настройку заголовка и размеров.
    Не знает, какие компоненты будут добавлены.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markoff 2.0")
        self.setMinimumSize(1024, 768)
        self.resize(1024, 768)
```

### **MenuBar — главное меню**

```python
# ui/main_window/menu.py

class MenuBar(QMenuBar):
    """
    Главное меню приложения.
    Создает пункты меню и эмитит события через EventBus.
    
    Структура:
    - Файл → Выход (Ctrl+Q)
    - Справочники → Типы помещений, Статусы помещений, ...
    - Помощь → О программе
    """
```

**Эмитит события:**
- `MenuReferenceRequested(reference)` — при выборе справочника
- `MenuHelpAbout` — при выборе "О программе"
- `MenuFileExit` — при выборе "Выход"

### **Toolbar — панель инструментов**

```python
# ui/main_window/toolbar.py

class Toolbar(QToolBar):
    """
    Панель инструментов приложения.
    Содержит кнопки быстрого доступа.
    """
```

**Эмитит события:**
- `RefreshRequested(mode="current")` — при нажатии на обновление
- `ModeChanged(mode)` — при переключении режима (Read Only / Редактирование)

### **StatusBar — строка состояния**

```python
# ui/main_window/status_bar.py

class StatusBar(QStatusBar):
    """
    Строка состояния приложения.
    Отображает статус соединения и временные сообщения.
    """
```

**Подписывается на события:**
- `ConnectionChanged` — обновляет индикатор соединения
- `DataLoading` — показывает "Загрузка..."
- `DataLoaded` — показывает "Готово"
- `DataError` — показывает ошибку

---

## 🔹 **CentralWidget — разделитель с подменой панелей**

```python
# ui/common/central_widget.py

class CentralWidget:
    """
    Центральный виджет с разделителем 30/70.
    
    Создает QSplitter с TreeView (слева) и заглушкой (справа).
    Предоставляет методы для подмены панелей.
    
    Методы:
    - set_left(widget) — заменить левую панель
    - set_right(widget) — заменить правую панель
    - get_tree_view() — получить TreeView
    - central_widget — получить QWidget для установки в MainWindow
    """
```

**Важно:** Левая панель создается сразу как TreeView, без подмены. Правая панель — заглушка, которая будет заменена позже.

---

## 🔹 **TreeView — виджет дерева**

```python
# ui/tree/view.py

class TreeView(QTreeView):
    """
    Виджет дерева.
    
    Отвечает за:
    - Отображение дерева через TreeModel
    - Эмиссию событий при действиях пользователя
    - Не содержит бизнес-логики
    """
```

**Методы:**
| Метод | Описание |
|-------|----------|
| `set_event_bus(bus)` | Устанавливает шину событий |
| `set_model(model)` | Устанавливает модель и подключает сигнал выбора |

**Эмитит события:**
- `NodeSelected(node)` — при клике на узел
- `NodeExpanded(node)` — при раскрытии узла
- `NodeCollapsed(node)` — при сворачивании узла

---

## 🔹 **TreeModel — модель дерева для Qt**

```python
# ui/tree/model.py

class TreeModel(QAbstractItemModel):
    """
    Модель дерева для QTreeView.
    
    Предоставляет данные из TreeNode для отображения.
    Не знает о загрузке данных и EventBus.
    
    Кастомные роли:
    - ItemIdRole: ID узла
    - ItemTypeRole: тип узла (complex, building, floor, room)
    - ItemDataRole: исходные данные (модель)
    """
```

**Публичные методы:**
| Метод | Описание |
|-------|----------|
| `set_root_nodes(nodes)` | Полная замена корневых узлов |
| `insert_children(parent_node, children)` | Вставка дочерних узлов |
| `remove_children(parent_node, row, count)` | Удаление дочерних узлов |
| `node_changed(node)` | Уведомление об изменении узла |
| `get_node_by_id(node_type, node_id)` | Получение узла из кэша |

**Кэш узлов:**
```python
self._node_cache: Dict[Tuple[NodeType, int], TreeNode] = {}
```
Обеспечивает O(1) доступ к узлам по типу и ID.

---

## 🔹 **TreeNode — структура узла дерева**

```python
# ui/tree/node.py

class TreeNode:
    """
    Узел дерева.
    
    Единообразная структура для всех уровней:
    - id: уникальный ID узла
    - type: тип узла ("complex", "building", "floor", "room")
    - name: отображаемое имя
    - has_children: есть ли дети (для стрелочки)
    
    Также хранит:
    - data: исходные данные (модель)
    - parent: ссылка на родительский узел
    - children: список дочерних узлов
    """
```

**Методы:**
| Метод | Описание |
|-------|----------|
| `append_child(child)` | Добавляет одного ребенка |
| `add_children(children)` | Добавляет несколько детей |
| `child_at(row)` | Возвращает ребенка по индексу |
| `child_count()` | Количество детей |
| `row()` | Индекс в родителе |
| `get_identifier()` | Возвращает NodeIdentifier для событий |
| `find_child_by_id(node_type, node_id)` | Рекурсивный поиск узла |

---

## 🔹 **Принципы работы UI слоя**

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

### **3. Нет состояния**
```python
# UI не хранит данные между обновлениями
class PhysicsTab:
    def __init__(self):
        # ❌ Нет self._statistics
        # ✅ Данные приходят в событиях, сразу отображаются
        pass
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

---

## 🔹 **Поток данных**

```
[Пользователь] кликает на узел
    ↓
[TreeView] эмитит NodeSelected
    ↓
[EventBus] доставляет событие
    ↓
[TreeController] подписан → сохраняет состояние
[DetailsController] подписан → вызывает проекции → эмитит StatisticsUpdated
    ↓
[EventBus] доставляет StatisticsUpdated
    ↓
[PhysicsTab] получает → обновляет отображение
```

**UI НЕ знает:**
- Кто обрабатывает NodeSelected
- Как вычисляется StatisticsViewModel
- Откуда берутся данные

**UI ЗНАЕТ:**
- На какие события подписываться
- Как отображать View Models
- Какие события эмитить

---

## 🚫 **Что НЕЛЬЗЯ делать в UI слое**

| Действие | Почему |
|----------|--------|
| **Вызывать контроллеры напрямую** | Нарушает слоистую архитектуру |
| **Вызывать проекции напрямую** | Проекции — ответственность контроллеров |
| **Вызывать DataLoader напрямую** | Загрузка данных — ответственность контроллеров |
| **Хранить данные (кроме View Models)** | Данные должны быть в EntityGraph |
| **Содержать бизнес-логику** | Бизнес-логика в DataLoader и контроллерах |
| **Принимать решения о загрузке данных** | UI показывает заглушку, контроллер решает |
| **Знать о репозиториях** | Только core, view_models, utils.logger |
| **Создавать или подменять панели самостоятельно** | Контроллеры вызывают set_left_panel/set_right_panel |

---

## 📊 **Чек-лист: что есть в UI слое**

| Компонент | Статус |
|-----------|--------|
| **AppWindow** — фасад | ✅ |
| **MainWindow** — пустая оболочка | ✅ |
| **MenuBar** — главное меню | ✅ |
| **Toolbar** — панель инструментов | ✅ |
| **StatusBar** — строка состояния | ✅ |
| **CentralWidget** — разделитель | ✅ |
| **TreeView** — виджет дерева | ✅ |
| **TreeModel** — модель дерева | ✅ |
| **TreeNode** — структура узла | ✅ |
| Кэш узлов в TreeModel | ✅ |
| Подмена панелей через AppWindow | ✅ |
| Эмиссия UI-событий | ✅ |
| Подписка на события контроллеров | ✅ |
| **DetailsPanel** | ⏸️ В разработке |
| **Вкладки** | ⏸️ В разработке |

---

## 💡 **Итог**

UI слой спроектирован так, чтобы быть:

- **Пассивным** — не принимает решений, только отображает и сообщает
- **Реактивным** — обновляется автоматически при получении событий
- **Типобезопасным** — работает с типизированными View Models
- **Тестируемым** — можно тестировать с мок-событиями
- **Слабо связанным** — не знает о бизнес-логике и данных
- **Расширяемым** — легко добавить новые компоненты

**Любой контроллер может управлять UI через события:**
```python
# Контроллер эмитит событие с View Model
self._bus.emit(StatisticsUpdated(stats))

# UI получает и отображает
self._bus.subscribe(StatisticsUpdated, self._on_statistics)

def _on_statistics(self, event):
    stats = event.data
    self.total_label.setText(str(stats.total_buildings))
    self.free_label.setText(str(stats.free_rooms))
    # ...
```