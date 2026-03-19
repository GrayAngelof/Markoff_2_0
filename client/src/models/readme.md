## 🎯 **Ты абсолютно прав! Это справка, а не документация кода!**

Прости, я увлекся и начал описывать реализацию, а нужно было **чисто инструкцию по использованию**. Исправляюсь!

---

## 📚 **СПРАВКА ПО МОДЕЛЯМ (MODELS) — версия 1.0**

### 🎯 **Назначение моделей**

Модели — это **единственный источник правды** о том, как выглядят данные, которые приходят с бекенда. Если ты работаешь с комплексом, корпусом или контрагентом — ты работаешь через эти классы.

**Главное правило:** Модели только хранят данные. Вся логика — в других местах.

---

## 📦 **Где лежат модели**

```
src/models/
```

Все модели импортируются напрямую из пакета:

```python
from src.models import Complex, Building, Counterparty
```

Не нужно лезть в отдельные файлы — достаточно этого импорта.

---

## 🏗️ **Список моделей**

| Модель | Что описывает | Когда использовать |
|--------|---------------|-------------------|
| `Complex` | Комплекс зданий | Работа с комплексами |
| `Building` | Корпус | Работа с корпусами |
| `Floor` | Этаж | Работа с этажами |
| `Room` | Помещение | Работа с помещениями |
| `Counterparty` | Контрагент (юр. лицо) | Работа с владельцами, арендаторами |
| `ResponsiblePerson` | Ответственное лицо | Контактные лица контрагентов |

---

## 🎯 **Как создать модель из API**

У каждой модели есть метод `from_dict()`. **Только так** нужно создавать модели из ответов бекенда:

```python
# Получили данные от API
api_response = {
    "id": 1,
    "name": "Фабрика Веретено",
    "buildings_count": 2,
    "description": "Историческое здание",
    "created_at": "2024-01-15T14:30:45Z"
}

# Создаём модель
complex = Complex.from_dict(api_response)
```

**Важно:** 
- Все обязательные поля должны быть в словаре
- Если поля нет — метод упадет с ошибкой (так и задумано)
- Даты автоматически превращаются в `datetime`

---

## 📋 **Что есть в каждой модели**

### **Complex**
```python
complex.id               # int
complex.name             # str
complex.buildings_count  # int (сколько корпусов, для дерева)
complex.description      # Optional[str]
complex.address          # Optional[str]
complex.owner_id         # Optional[int]
complex.created_at       # Optional[datetime]
complex.updated_at       # Optional[datetime]
```

### **Building**
```python
building.id              # int
building.name            # str
building.complex_id      # int (чей это корпус)
building.floors_count    # int (сколько этажей, для дерева)
building.description     # Optional[str]
building.address         # Optional[str]
building.status_id       # Optional[int]
building.owner_id        # Optional[int] (кто владелец)
building.created_at      # Optional[datetime]
building.updated_at      # Optional[datetime]
```

### **Floor**
```python
floor.id                 # int
floor.number             # int (может быть отрицательным: -1, -2)
floor.building_id        # int (чей это этаж)
floor.rooms_count        # int (сколько помещений, для дерева)
floor.description        # Optional[str]
floor.physical_type_id   # Optional[int]
floor.status_id          # Optional[int]
floor.plan_image_url     # Optional[str]
floor.created_at         # Optional[datetime]
floor.updated_at         # Optional[datetime]
```

### **Room**
```python
room.id                  # int
room.number              # str ("101", "101А", "Б12")
room.floor_id            # int (чей это этаж)
room.area                # Optional[float] (площадь)
room.status_code         # Optional[str] ('free', 'occupied', ...)
room.description         # Optional[str]
room.physical_type_id    # Optional[int]
room.max_tenants         # Optional[int]
room.created_at          # Optional[datetime]
room.updated_at          # Optional[datetime]
```

### **Counterparty**
```python
counterparty.id              # int
counterparty.short_name      # str (для отображения)
counterparty.full_name       # Optional[str] (полное юр. название)
counterparty.type_id         # Optional[int]
counterparty.tax_id          # Optional[str] (ИНН)
counterparty.legal_address   # Optional[str]
counterparty.actual_address  # Optional[str]
counterparty.bank_details    # Optional[Dict] (JSON с реквизитами)
counterparty.status_code     # str ('active', 'suspended', ...)
counterparty.notes           # Optional[str]
counterparty.created_at      # Optional[datetime]
counterparty.updated_at      # Optional[datetime]
```

### **ResponsiblePerson**
```python
person.id                    # int
person.counterparty_id       # int (чей это контакт)
person.person_name           # str (ФИО)
person.position              # Optional[str] (должность)
person.role_code             # Optional[str]
person.phone                 # Optional[str]
person.email                 # Optional[str]
person.contact_categories    # Optional[str] ("legal,financial")
person.is_public_contact     # bool (публичный ли)
person.is_active             # bool (активен ли)
person.notes                 # Optional[str]
person.created_at            # Optional[datetime]
person.updated_at            # Optional[datetime]
```

---

## 💡 **Важные особенности**

### 1. **Модели неизменяемы (immutable)**
```python
complex.name = "Новое название"  # ❌ ОШИБКА! Нельзя изменить
```
Если нужно изменить данные — создавай новую модель из обновленного словаря.

### 2. **Все связи — через ID**
```python
building.complex_id  # есть
building.owner_id    # есть
# Но самого объекта владельца в модели НЕТ
```
Владельца нужно получать отдельно через `CounterpartyRepository`.

### 3. **Статусы — это коды**
```python
room.status_code = 'occupied'      # код
# Не текст! "ЗАНЯТО" — это работа форматтера
```

### 4. **Даты — это datetime**
```python
complex.created_at.year        # можно
complex.created_at.strftime()  # можно
# Это уже объект datetime, не строка!
```

---

## 🎯 **Где использовать модели**

### ✅ **В API клиенте**
```python
data = api_client.get_complexes()
complexes = [Complex.from_dict(item) for item in data]
return complexes
```

### ✅ **В репозиториях**
```python
def get_by_id(self, id: int) -> Optional[Building]:
    return self._graph.get(NodeType.BUILDING, id)
```

### ✅ **В контроллерах**
```python
def _on_building_selected(self, building: Building):
    self._loader.load_building_details(building.id)
```

### ❌ **НЕ в UI напрямую**
Модели не должны знать про отображение. Для UI есть отдельные форматтеры:
```python
# НЕ ДЕЛАЙ ТАК:
label.setText(building.name)  # можно, но лучше через форматтер

# ДЕЛАЙ ТАК:
from ui.formatters import building_formatter
label.setText(building_formatter.format_building_title(building))
```

---

## 📋 **Частые вопросы**

**Вопрос:** А где методы типа `get_owner_display`?  
**Ответ:** Их нет. Это UI-логика, она в `ui/formatters/`.

**Вопрос:** А как получить владельца корпуса?  
**Ответ:** 
```python
owner_id = building.owner_id
if owner_id:
    owner = counterparty_repo.get(owner_id)
```

**Вопрос:** А что, если в API нет поля?  
**Ответ:** Метод `from_dict` упадет с ошибкой. Это правильно — мы должны знать, если API изменился.

**Вопрос:** А можно создать модель без API, руками?  
**Ответ:** Да:
```python
building = Building(
    id=1,
    name="Тестовый корпус",
    complex_id=42,
    floors_count=5
)
```

---

## 🚫 **Чего НЕТ в моделях (и не ищи)**

- ❌ Нет методов `display_name()`
- ❌ Нет `get_status_display()`
- ❌ Нет вложенных объектов (owner, responsible_persons)
- ❌ Нет бизнес-логики
- ❌ Нет валидации кроме обязательных полей

---

## ✅ **Резюме**

1. **Модели = данные с бекенда**
2. **Создаём только через `from_dict`**
3. **Не изменяем после создания**
4. **Связи только через ID**
5. **Статусы — коды, не текст**
6. **Даты — `datetime`, не строки**
7. **Вся логика — в других местах**

**Это всё, что нужно знать про модели, чтобы правильно их использовать.** 🚀