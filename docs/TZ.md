## 📜 **ПРАВИЛА СОЗДАНИЯ ТЗ (КРАТКАЯ ВЕРСИЯ)**

---

## 🎯 **1. РАЗДЕЛЕНИЕ**

| Документ | Что | Формат |
|----------|-----|--------|
| **Спецификация** | ЧТО делать (границы, контракты) | Текст + таблицы + концептуальный код |
| **ТЗ** | КАК делать (структура, псевдокод) | Структура + 10-20 строк псевдокода на файл |

---

## 📋 **2. ШАБЛОН ТЗ**

```markdown
## 📋 ТЗ: [НАЗВАНИЕ]

### 📁 **Структура**
```
слой/
├── __init__.py              # публичное API
├── фасад.py                  # ФАСАД (главная точка входа)
└── внутреннее/               # приватно
    ├── __init__.py
    └── компонент.py
```

### 📄 **Файл: фасад.py**
```python
# Зависимости: core, models, data (только нижележащие)

class Фасад:
    def __init__(self, deps):
        self._internal = Internal(deps)
    
    def public_method(self, params) -> Return:
        """Проверка кэша → вызов internal → событие → возврат"""
        pass
```

### 📊 **Сводка**
| Компонент | Тип | Назначение |
|-----------|-----|------------|
| Фасад | Публичный | Оркестрация |
| Internal | Приватный | Детали реализации |
```

---

## 🏛️ **3. ПРАВИЛА ИМПОРТОВ (снизу вверх)**

| Слой | Импортирует | НЕ импортирует |
|------|-------------|----------------|
| Core | typing, dataclasses | всё остальное |
| Models | core | data, services, ui |
| Data | core, models | services, ui |
| Services | core, models, data | controllers, ui |
| Controllers | core, models, data, services | ui (только события) |
| UI | всё | — |

---

## 🔍 **4. ЧТО ДОЛЖНО БЫТЬ В ТЗ**

- ✅ Структура файлов (фасад наверху, внутренности внизу)
- ✅ Псевдокод (10-20 строк на файл)
- ✅ Сводка компонентов
- ✅ Схема потока (для сложных случаев)

## ❌ ЧЕГО НЕ ДОЛЖНО БЫТЬ

- ❌ Детальной реализации (циклы, условия, 50+ строк)
- ❌ Импортов вышележащих слоев
- ❌ Магических строк (только константы из core)

---

## 📝 **5. ПРИМЕР (Services)**

```markdown
## 📋 ТЗ: SERVICES

### 📁 **Структура**
```
services/
├── __init__.py
├── api_client.py              # ФАСАД
├── data_loader.py              # ФАСАД
├── api/                        # приватно
│   ├── http_client.py
│   └── endpoints.py
└── loading/                    # приватно
    ├── node_loader.py
    └── owner_loader.py
```

### 📄 **api_client.py**
```python
class ApiClient:
    def __init__(self, base_url=None):
        self._session = HttpSession(base_url)
    
    def get_complexes(self) -> List[Complex]:
        data = self._session.get(ENDPOINTS.COMPLEXES)
        return [Complex.from_dict(item) for item in data]
```

### 📄 **data_loader.py**
```python
class DataLoader:
    def __init__(self, bus, api, graph):
        self._loader = NodeLoader(api, graph)
        self._graph = graph
    
    def load_complexes(self) -> List[Complex]:
        # Проверка кэша → если есть → возврат
        # Если нет → self._loader.load_complexes()
```

### 📊 **Сводка**
| Компонент | Тип | Назначение |
|-----------|-----|------------|
| ApiClient | Публичный | HTTP + преобразование в модели |
| DataLoader | Публичный | Оркестрация, проверка кэша |
| NodeLoader | Приватный | Ядро загрузки |
```

---

## ✅ **6. ЧЕК-ЛИСТ**

- [ ] Есть утвержденная спецификация?
- [ ] Структура: фасад наверху, внутренности внизу?
- [ ] Импорты только снизу вверх?
- [ ] Псевдокод краткий (10-20 строк)?
- [ ] Есть сводка компонентов?

---