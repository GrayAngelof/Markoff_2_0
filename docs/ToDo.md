## Список технических долгов (TODO)

Ниже приведены все отмеченные в коде `# TODO` задачи, требующие реализации, а также явно незавершённые методы.

---

### 1. `data/graph/consistency.py`

**Класс:** `ConsistencyChecker`  
**Метод:** `_check_relation_targets`  
**Описание:** Реализовать проверку, что все связи ведут на существующие объекты.

---

### 2. `data/graph/consistency.py`

**Класс:** `ConsistencyChecker`  
**Метод:** `_check_parent_back_references`  
**Описание:** Реализовать проверку, что у каждого ребенка есть обратная связь.

---

### 3. `data/graph/consistency.py`

**Класс:** `ConsistencyChecker`  
**Метод:** `_check_index_consistency`  
**Описание:** Реализовать проверку соответствия прямых и обратных индексов.

---

### 4. `services/loaders/business_loader.py`

**Класс:** `BusinessLoader`  
**Метод:** `load_counterparty`  
**Описание:** Реализовать загрузку контрагента через API (сейчас заглушка).

---

### 5. `services/loaders/business_loader.py`

**Класс:** `BusinessLoader`  
**Метод:** `load_responsible_persons`  
**Описание:** Реализовать загрузку ответственных лиц контрагента через API (сейчас заглушка).

---

### 6. `services/loaders/safety_loader.py`

**Класс:** `SafetyLoader`  
**Метод:** `load_sensors_by_room`  
**Описание:** Реализовать загрузку датчиков по ID помещения через API (сейчас заглушка).

---

### 7. `services/loaders/safety_loader.py`

**Класс:** `SafetyLoader`  
**Метод:** `load_events_by_building`  
**Описание:** Реализовать загрузку событий пожарной безопасности по ID здания через API (сейчас заглушка).

---

### 8. `controllers/details_controller.py`

**Класс:** `DetailsController`  
**Метод:** `_show_error`  
**Описание:** Создать событие `ShowError` и обработать его в `DetailsPanel` для отображения сообщений об ошибках пользователю.

---

### 9. `ui/main_window/menu.py`

**Класс:** `MenuBar`  
**Метод:** `_create_file_menu`  
**Описание:** Добавить действие при выходе (подключить закрытие приложения к пункту меню "Выход").

---

### 10. `ui/main_window/menu.py`

**Класс:** `MenuBar`  
**Метод:** `_create_reference_menu`  
**Описание:** Добавить действия для справочников (открытие соответствующих окон/диалогов при выборе пунктов меню).

---

### 11. `ui/main_window/menu.py`

**Класс:** `MenuBar`  
**Метод:** `_create_help_menu`  
**Описание:** Добавить действие "О программе" (показать диалог с информацией о приложении).

---

### 12. `ui/main_window/toolbar.py`

**Класс:** `Toolbar`  
**Метод:** `_create_mode_button`  
**Описание:** Добавить действие для кнопки переключения режима (Read Only / Edit Mode) – подключить логику изменения режима работы приложения.

---

> **Примечание:** В слое `ui/details/tabs/` все вкладки (`PhysicsTab`, `LegalTab`, `SafetyTab`, `DocumentsTab`) в текущей реализации являются заглушками, однако явных комментариев `TODO` в них нет. Их наполнение данными из `view_models` – это отдельная задача, не отмеченная как `TODO` в коде.