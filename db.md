# База данных системы управления недвижимостью и пожарной безопасностью

## Структура базы данных

База данных организована в семь тематических схем, каждая из которых отвечает за определенный аспект системы с учетом требований безопасности и разграничения доступа:

1. **`security`** – управление пользователями, ролями и правами доступа
2. **`dictionary`** – централизованные справочники системы
3. **`physical`** – физическая структура объектов недвижимости
4. **`business`** – бизнес-процессы аренды и управления недвижимостью
5. **`fire`** – пожарная безопасность и техническое обслуживание оборудования
6. **`audit`** – аудит изменений и системное журналирование
7. **`public`** – служебные таблицы для технических нужд

---

## Схема `security`

Централизованное управление доступом пользователей к данным системы.

### Таблица `users`
Пользователи системы.

| Колонка                | Тип                      | Ограничения            | Комментарий                                           |
|------------------------|--------------------------|------------------------|-------------------------------------------------------|
| id                     | bigint                   | NOT NULL               | Уникальный идентификатор пользователя системы         |
| username               | text                     | NOT NULL UNIQUE        | Логин для входа в систему                             |
| password_hash          | text                     | NOT NULL               | Хэш пароля (bcrypt/scrypt)                            |
| person_id              | bigint                   | NOT NULL               | Ссылка на ответственное лицо (responsible_persons.id) |
| is_active              | boolean                  | DEFAULT true           | Активен ли пользователь                               |
| must_change_password   | boolean                  | DEFAULT true           | Требуется ли сменить пароль при следующем входе       |
| last_login_at          | timestamp with time zone |                        | Дата и время последнего входа                         |
| failed_login_attempts  | integer                  | DEFAULT 0              | Количество неудачных попыток входа                    |
| locked_until           | timestamp with time zone |                        | До какого времени заблокирован                        |
| mfa_enabled            | boolean                  | DEFAULT false          | Включена ли двухфакторная аутентификация              |
| mfa_secret             | text                     |                        | Секрет для двухфакторной аутентификации               |
| created_at             | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                          |
| updated_at             | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи             |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (person_id)` REFERENCES `dictionary.responsible_persons(id)`

### Таблица `roles`
Роли системы с разным уровнем доступа.

| Колонка            | Тип                      | Ограничения            | Комментарий                                                 									                                   |
|--------------------|--------------------------|------------------------|-----------------------------------------------------------------------------------------------------------------|
| code               | text                     | NOT NULL               | Код роли: sysadmin, building_admin, lawyer, accountant, fire_safety, technician, security, tenant_admin, viewer |
| name               | text                     | NOT NULL               | Название роли                                                									                                 |
| description        | text                     |                        | Описание роли и прав                                        										                                 |
| is_system          | boolean                  | DEFAULT false          | Системная роль (нельзя удалить/изменить)                  									                                     |
| created_at         | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                              									                                     |

**Ключи и ограничения:**
- `PRIMARY KEY (code)`

### Таблица `user_roles`
Назначение ролей пользователям с контекстом.

| Колонка             | Тип                      | Ограничения            | Комментарий                                                       	           |
|---------------------|--------------------------|------------------------|--------------------------------------------------------------------------------|
| user_id             | bigint                   | NOT NULL               | Идентификатор пользователя                                       	             |
| role_code           | text                     | NOT NULL               | Код роли                                                        	             |
| context_entity_type | text                     |                        | Тип сущности контекста: counterparty, building, complex, global, all_buildings |
| context_entity_id   | bigint                   |                        | Идентификатор сущности контекста                               	               |
| is_primary          | boolean                  | DEFAULT false          | Основная ли роль для этого контекста                                       	   |
| granted_by          | bigint                   |                        | Кто выдал роль (user.id)                                               	       |
| granted_at          | timestamp with time zone | NOT NULL DEFAULT now() | Когда выдана роль                                                  	           |
| valid_until         | timestamp with time zone |                        | До какого времени действует роль                                               |
| is_active           | boolean                  | DEFAULT true           | Активна ли роль в этом контексте                                               |

**Ключи и ограничения:**
- `PRIMARY KEY (user_id, role_code, context_entity_type, COALESCE(context_entity_id, 0))`
- `FOREIGN KEY (user_id)` REFERENCES `users(id)`
- `FOREIGN KEY (role_code)` REFERENCES `roles(code)`
- `FOREIGN KEY (granted_by)` REFERENCES `users(id)`

### Таблица `data_visibility_rules`
Правила видимости данных для различных ролей.

| Колонка             | Тип                      | Ограничения            | Комментарий                                                        |
|---------------------|--------------------------|------------------------|--------------------------------------------------------------------|
| id                  | bigint                   | NOT NULL               | Уникальный идентификатор правила                                   |
| role_code           | text                     | NOT NULL               | Код роли, к которой применяется правило                            |
| table_schema        | text                     | NOT NULL               | Схема таблицы                                                      |
| table_name          | text                     | NOT NULL               | Наименование таблицы                                               |
| column_name         | text                     |                        | Наименование колонки (NULL для всей таблицы)                       |
| visibility_context  | text                     | NOT NULL               | Контекст видимости: own_only, assigned_only, all, none, restricted |
| condition_sql       | text                     |                        | Дополнительное условие в формате SQL                               |
| priority            | integer                  | DEFAULT 0              | Приоритет применения (чем выше, тем раньше применяется)            |
| is_active           | boolean                  | DEFAULT true           | Активно ли правило                                                 |
| created_at          | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                       |
| updated_at          | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи                          |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (role_code)` REFERENCES `roles(code)`

### Таблица `session_log`
Журнал сессий пользователей.

| Колонка            | Тип                      | Ограничения            | Комментарий                      |
|--------------------|--------------------------|------------------------|----------------------------------|
| id                 | bigint                   | NOT NULL               | Уникальный идентификатор сессии  |
| user_id            | bigint                   | NOT NULL               | Идентификатор пользователя       |
| session_token      | text                     | NOT NULL               | Токен сессии                     |
| ip_address         | inet                     |                        | IP-адрес входа                   |
| user_agent         | text                     |                        | User-Agent браузера              |
| login_at           | timestamp with time zone | NOT NULL DEFAULT now() | Время входа                      |
| logout_at          | timestamp with time zone |                        | Время выхода                     |
| is_active          | boolean                  | DEFAULT true           | Активна ли сессия                |
| created_at         | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи     |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (user_id)` REFERENCES `users(id)`

---

## Схема `dictionary`

Централизованные справочники системы, используемые всеми другими схемами.

### Таблица `physical_room_types`
Типы физических помещений.

| Колонка                | Тип                      | Ограничения            | Комментарий                                           |
|------------------------|--------------------------|------------------------|-------------------------------------------------------|
| id                     | bigint                   | NOT NULL               | Первичный ключ, автоинкремент                         |
| code                   | text                     | NOT NULL               | Машинный код (lowercase. например: office, warehouse) |
| name                   | text                     | NOT NULL               | Человекочитаемое название типа помещения              |
| description            | text                     |                        | Подробное описание типа помещения                     |
| fire_safety_category   | character                |                        | Категория пожарной опасности (A, B, C, D, F)          |
| is_rentable            | boolean                  | NOT NULL DEFAULT true  | Можно ли сдавать данный тип помещения в аренду        |
| base_rate_weight       | numeric                  | NOT NULL DEFAULT 1.0   | Базовый коэффициент для расчета арендной ставки       |
| created_at             | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                          |
| updated_at             | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи             |
| display_order          | integer                  |                        | Порядок отображения в выпадающих списках интерфейса   |
| is_active              | boolean                  | NOT NULL DEFAULT true  | Активен ли данный тип помещения для использования     |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`

### Таблица `placement_usage_type_physical_type`
Связь типов использования и физических типов помещений.

| Колонка           | Тип    | Ограничения | Комментарий                                |
|-------------------|--------|-------------|--------------------------------------------|
| usage_type_id     | bigint | NOT NULL    | Идентификатор типа использования помещения |
| physical_type_id  | bigint | NOT NULL    | Идентификатор физического типа помещения   |

**Ключи и ограничения:**
- `PRIMARY KEY (physical_type_id, usage_type_id)`
- `FOREIGN KEY (physical_type_id)` REFERENCES `physical_room_types(id)`
- `FOREIGN KEY (usage_type_id)` REFERENCES `placement_usage_types(id)`

### Таблица `placement_usage_types`
Типы использования помещений.

| Колонка                     | Тип                      | Ограничения            | Комментарий                                                             |
|-----------------------------|--------------------------|------------------------|-------------------------------------------------------------------------|
| id                          | bigint                   | NOT NULL               | Уникальный идентификатор типа использования                             |
| code                        | text                     | NOT NULL               | Машинный код типа использования                                         |
| name                        | text                     | NOT NULL               | Название типа использования                                             |
| description                 | text                     |                        | Описание типа использования                                             |
| rate_multiplier             | numeric                  | NOT NULL DEFAULT 1.0   | Множитель к базовой ставке помещения для данного типа использования >=0 |
| requires_special_agreement  | boolean                  | NOT NULL DEFAULT false | Требуется ли специальное соглашение для данного типа использования      |
| created_at                  | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                            |
| updated_at                  | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи                               |
| display_order               | integer                  |                        | Порядок отображения в интерфейсе                                        |
| is_active                   | boolean                  | NOT NULL DEFAULT true  | Активен ли данный тип использования                                     |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`

### Таблица `sensor_types`
Типы датчиков пожарной безопасности.

| Колонка             | Тип                      | Ограничения                     | Комментарий                                            |
|---------------------|--------------------------|---------------------------------|--------------------------------------------------------|
| id                  | bigint                   | NOT NULL                        | Уникальный идентификатор типа датчика                  |
| code                | text                     | NOT NULL                        | Машинный код типа датчика                              |
| name                | text                     | NOT NULL                        | Название типа датчика                                  |
| description         | text                     |                                 | Описание типа датчика и его назначения                 |
| check_interval_days | integer                  |                                 | Рекомендуемый интервал поверки/проверки датчика в днях |
| default_status      | text                     | NOT NULL DEFAULT 'active'::text | Статус по умолчанию при установке нового датчика       |
| display_order       | integer                  |                                 | Порядок отображения в интерфейсе                       |
| created_at          | timestamp with time zone | NOT NULL DEFAULT now()          | Дата и время создания записи                           |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`

### Таблица `status_catalog`
Каталог статусов для различных сущностей.

| Колонка       | Тип                      | Ограничения            | Комментарий                                                                         |
|---------------|--------------------------|------------------------|-------------------------------------------------------------------------------------|
| entity        | text                     | NOT NULL               | Имя сущности (room, contract, counterparty, building, sensor, placement, equipment) |
| code          | text                     | NOT NULL               | Машинный код статуса (active, expired, draft, suspended, archived)                  |
| name          | text                     | NOT NULL               | Человекочитаемое название статуса                                                   |
| description   | text                     |                        | Описание статуса и его значения                                                     |
| is_initial    | boolean                  | NOT NULL DEFAULT false | Можно ли установить этот статус при создании новой записи?                          |
| display_order | integer                  |                        | Порядок отображения статуса в интерфейсе                                            |
| created_at    | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                        |

**Ключи и ограничения:**
- `PRIMARY KEY (entity, code)`

### Таблица `counterparties`
Контрагенты системы (арендодатели, арендаторы, поставщики, подрядчики).

| Колонка            | Тип                      | Ограничения                           | Комментарий                                                                                                                                     |
|--------------------|--------------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| id                 | bigint                   | NOT NULL                              | Уникальный идентификатор контрагента                                                                                                            |
| type               | text                     | NOT NULL DEFAULT 'tenant'::text       | Тип контрагента: landlord - арендодатель, tenant - арендатор, supplier - поставщик, contractor - подрядчик, service - обслуживающая организация |
| short_name         | text                     | NOT NULL                              | Краткое название (для поиска и отображения в интерфейсе)                                                                                        |
| full_name          | text                     |                                       | Полное юридическое название                                                                                                                     |
| tax_id             | text                     |                                       | ИНН или другой налоговый идентификатор                                                                                                          |
| legal_address      | text                     |                                       | Юридический адрес                                                                                                                               |
| actual_address     | text                     |                                       | Фактический адрес                                                                                                                               |
| bank_details       | jsonb                    |                                       | Банковские реквизиты в формате JSON                                                                                                             |
| status_entity      | text                     | NOT NULL DEFAULT 'counterparty'::text | Тип сущности для статуса                                                                                                                        |
| status_code        | text                     | NOT NULL DEFAULT 'active'::text       | Статус контрагента                                                                                                                              |
| notes              | text                     |                                       | Дополнительные заметки                                                                                                                          |
| created_at         | timestamp with time zone | NOT NULL DEFAULT now()                | Дата и время создания записи                                                                                                                    |
| updated_at         | timestamp with time zone | NOT NULL DEFAULT now()                | Дата и время последнего обновления записи                                                                                                       |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `status_catalog(code, entity)`

### Таблица `responsible_persons`
Ответственные лица (сотрудники, контактные лица контрагентов).

| Колонка             | Тип                      | Ограничения                         | Комментарий                                                                 |
|---------------------|--------------------------|-------------------------------------|-----------------------------------------------------------------------------|
| id                  | bigint                   | NOT NULL                            | Уникальный идентификатор ответственного лица                               |
| counterparty_id     | bigint                   |                                     | Идентификатор контрагента (если лицо связано с организацией)               |
| person_name         | text                     | NOT NULL                            | ФИО ответственного лица                                                    |
| position            | text                     |                                     | Должность                                                                   |
| department          | text                     |                                     | Подразделение/отдел                                                        |
| role_code           | text                     | NOT NULL                            | Код роли (ссылка на role_catalog.code)                                     |
| phone               | text                     |                                     | Контактный телефон                                                         |
| email               | text                     |                                     | Контактный email                                                           |
| contact_categories  | text[]                   | DEFAULT '{}'                        | Категории контакта: legal, fire_safety, technical, financial, emergency, general |
| is_public_contact   | boolean                  | DEFAULT false          | Является ли публичным контактом (виден всем)                                |
| is_active           | boolean                  | NOT NULL DEFAULT true  | Активен ли сотрудник                                                       |
| hire_date           | date                     |                        | Дата приема на работу/начала сотрудничества                                |
| termination_date    | date                     |                        | Дата увольнения/окончания сотрудничества                                   |
| notes               | text                     |                        | Дополнительные заметки                                                     |
| created_at          | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                |
| updated_at          | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи                                  |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (counterparty_id)` REFERENCES `counterparties(id)`
- `FOREIGN KEY (role_code)` REFERENCES `role_catalog(code)`

### Таблица `role_catalog`
Справочник ролей и должностей.

| Колонка            | Тип                      | Ограничения            | Комментарий                                                                 |
|--------------------|--------------------------|------------------------|-----------------------------------------------------------------------------|
| code               | text                     | NOT NULL               | Код роли: fire_safety_officer, building_manager, technician, lawyer, accountant, contact_person, admin, director |
| name               | text                     | NOT NULL               | Название роли                                                              |
| description        | text                     |                        | Описание роли и обязанностей                                               |
| category           | text                     | NOT NULL               | Категория: safety, technical, legal, financial, management, contact, other |
| display_order      | integer                  |                        | Порядок отображения                                                        |
| is_active          | boolean                  | DEFAULT true           | Активна ли роль                                                            |
| created_at         | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                |

**Ключи и ограничения:**
- `PRIMARY KEY (code)`

### Таблица `contact_categories`
Категории контактов для разграничения видимости.

| Колонка            | Тип                      | Ограничения            | Комментарий                                                                 |
|--------------------|--------------------------|------------------------|-----------------------------------------------------------------------------|
| code               | text                     | NOT NULL               | Код категории: legal, fire_safety, technical, financial, emergency, general |
| name               | text                     | NOT NULL               | Название категории                                                         |
| description        | text                     |                        | Описание категории                                                          |
| allowed_roles      | text[]                   |                        | Массив ролей, которые могут видеть эти контакты                            |
| created_at         | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                |

**Ключи и ограничения:**
- `PRIMARY KEY (code)`

---

## Схема `physical`

Физическая структура объектов недвижимости в иерархии: комплексы → здания → этажи → помещения.

### Таблица `complexes`
Комплексы зданий.

| Колонка      | Тип                      | Ограничения            | Комментарий                                                                 |
|--------------|--------------------------|------------------------|-----------------------------------------------------------------------------|
| id           | bigint                   | NOT NULL               | Уникальный идентификатор комплекса                                          |
| name         | text                     | NOT NULL               | Наименование комплекса                                                      |
| description  | text                     |                        | Описание комплекса                                                          |
| address      | text                     |                        | Адрес комплекса                                                             |
| owner_id     | bigint                   |                        | Идентификатор контрагента-владельца (арендодателя)                          |
| created_at   | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                |
| updated_at   | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (owner_id)` REFERENCES `dictionary.counterparties(id)`

### Таблица `buildings`
Здания в составе комплексов.

| Колонка          | Тип                      | Ограничения                         | Комментарий                                                                 |
|------------------|--------------------------|-------------------------------------|-----------------------------------------------------------------------------|
| id               | bigint                   | NOT NULL                            | Уникальный идентификатор здания                                            |
| complex_id       | bigint                   | NOT NULL                            | Идентификатор комплекса, к которому относится здание                       |
| name             | text                     | NOT NULL                            | Наименование здания                                                         |
| description      | text                     |                                     | Описание здания                                                             |
| address          | text                     |                                     | Адрес здания                                                                |
| floors_count     | integer                  | NOT NULL                            | Общее количество этажей (должно быть > 0)                                   |
| physical_type_id | bigint                   | NOT NULL                            | Идентификатор физического типа здания                                      |
| status_entity    | text                     | NOT NULL DEFAULT 'building'::text   | Тип сущности для статуса                                                   |
| status_code      | text                     | NOT NULL                            | Код статуса здания                                                          |
| created_at       | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время создания записи                                                |
| updated_at       | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (complex_id, name)` - Уникальное наименование здания в рамках комплекса
- `FOREIGN KEY (complex_id)` REFERENCES `complexes(id)`
- `FOREIGN KEY (physical_type_id)` REFERENCES `dictionary.physical_room_types(id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `dictionary.status_catalog(code, entity)`

### Таблица `floors`
Этажи зданий.

| Колонка          | Тип                      | Ограничения                         | Комментарий                                                                 |
|------------------|--------------------------|-------------------------------------|-----------------------------------------------------------------------------|
| id               | bigint                   | NOT NULL                            | Уникальный идентификатор этажа                                             |
| building_id      | bigint                   | NOT NULL                            | Идентификатор здания, к которому относится этаж                            |
| number           | integer                  | NOT NULL                            | Номер этажа (0 - цоколь, отрицательные - подвал, положительные - надземные этажи) |
| description      | text                     |                                     | Описание этажа                                                              |
| physical_type_id | bigint                   | NOT NULL                            | Идентификатор физического типа этажа                                       |
| status_entity    | text                     | NOT NULL DEFAULT 'room'::text       | Тип сущности для статуса                                                   |
| status_code      | text                     | NOT NULL                            | Код статуса этажа                                                           |
| plan_image_url   | text                     |                                     | Ссылка на план этажа (схему расположения помещений)                        |
| created_at       | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время создания записи                                                |
| updated_at       | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (building_id, number)` - Уникальный номер этажа в рамках здания
- `FOREIGN KEY (building_id)` REFERENCES `buildings(id)`
- `FOREIGN KEY (physical_type_id)` REFERENCES `dictionary.physical_room_types(id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `dictionary.status_catalog(code, entity)`

### Таблица `rooms`
Помещения на этажах.

| Колонка          | Тип                      | Ограничения                         | Комментарий                                                                 |
|------------------|--------------------------|-------------------------------------|-----------------------------------------------------------------------------|
| id               | bigint                   | NOT NULL                            | Уникальный идентификатор помещения                                          |
| floor_id         | bigint                   | NOT NULL                            | Идентификатор этажа, на котором расположено помещение                      |
| number           | text                     | NOT NULL                            | Номер помещения (строковый, может содержать буквы: "101А", "201Б")          |
| description      | text                     |                                     | Описание помещения                                                          |
| area             | numeric                  |                                     | Площадь помещения в квадратных метрах                                       |
| physical_type_id | bigint                   | NOT NULL                            | Идентификатор физического типа помещения                                   |
| status_entity    | text                     | NOT NULL DEFAULT 'room'::text       | Тип сущности для статуса                                                   |
| status_code      | text                     | NOT NULL                            | Код статуса помещения                                                       |
| max_tenants      | integer                  |                                     | Максимальное рекомендуемое количество арендаторов для помещения            |
| created_at       | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время создания записи                                                |
| updated_at       | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (floor_id, number)` - Уникальный номер помещения в рамках этажа
- `FOREIGN KEY (floor_id)` REFERENCES `floors(id)`
- `FOREIGN KEY (physical_type_id)` REFERENCES `dictionary.physical_room_types(id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `dictionary.status_catalog(code, entity)`

### Таблица `zones`
Зоны в помещениях (для детализации планировки).

| Колонка            | Тип                      | Ограничения            | Комментарий                                                                 |
|--------------------|--------------------------|------------------------|-----------------------------------------------------------------------------|
| id                 | bigint                   | NOT NULL               | Уникальный идентификатор зоны                                              |
| room_id            | bigint                   | NOT NULL               | Идентификатор помещения, к которому относится зона                         |
| name               | text                     | NOT NULL               | Наименование зоны                                                          |
| description        | text                     |                        | Описание зоны                                                               |
| polygon_coordinates| jsonb                    |                        | Координаты полигона зоны в формате JSON (для отображения на плане)         |
| created_at         | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                |
| updated_at         | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (room_id, name)` - Уникальное наименование зоны в рамках помещения
- `FOREIGN KEY (room_id)` REFERENCES `rooms(id)`

---

## Схема `business`

Бизнес-процессы аренды и управления недвижимостью.

### Таблица `contracts`
Договоры аренды.

| Колонка          | Тип                      | Ограничения                      | Комментарий                                                                 |
|------------------|--------------------------|----------------------------------|-----------------------------------------------------------------------------|
| id               | bigint                   | NOT NULL                         | Уникальный идентификатор договора                                           |
| counterparty_id  | bigint                   | NOT NULL                         | Идентификатор контрагента-арендатора                                        |
| contract_number  | text                     | NOT NULL                         | Уникальный номер договора в формате Д-ГГГГ-№ (например, Д-2025-001)          |
| description      | text                     |                                  | Дополнительное описание договора                                            |
| start_date       | date                     | NOT NULL                         | Дата начала действия договора                                               |
| end_date         | date                     | NOT NULL                         | Дата окончания действия договора                                            |
| status_entity    | text                     | NOT NULL DEFAULT 'contract'::text| Тип сущности для статуса                                                   |
| status_code      | text                     | NOT NULL                         | Код статуса договора                                                        |
| monthly_payment  | numeric                  |                                  | Ежемесячный платеж по договору                                              |
| payment_day      | integer                  |                                  | День месяца, в который осуществляется оплата (1-31)                         |
| created_at       | timestamp with time zone | NOT NULL DEFAULT now()           | Дата и время создания записи                                                |
| updated_at       | timestamp with time zone | NOT NULL DEFAULT now()           | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (counterparty_id)` REFERENCES `dictionary.counterparties(id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `dictionary.status_catalog(code, entity)`

### Таблица `placements`
Размещения арендаторов в помещениях.

| Колонка         | Тип                      | Ограничения                         | Комментарий                                                                 |
|-----------------|--------------------------|-------------------------------------|-----------------------------------------------------------------------------|
| id              | bigint                   | NOT NULL                            | Уникальный идентификатор размещения                                         |
| contract_id     | bigint                   | NOT NULL                            | Идентификатор договора аренды                                               |
| room_id         | bigint                   | NOT NULL                            | Идентификатор помещения, в котором происходит размещение                    |
| usage_type_id   | bigint                   | NOT NULL                            | Идентификатор типа использования помещения                                  |
| start_date      | date                     | NOT NULL                            | Дата начала размещения                                                      |
| end_date        | date                     | NOT NULL                            | Дата окончания размещения                                                   |
| status_entity   | text                     | NOT NULL DEFAULT 'placement'::text  | Тип сущности для статуса                                                   |
| status_code     | text                     | NOT NULL                            | Код статуса размещения                                                      |
| area_used       | numeric                  | NOT NULL                            | Фактическая площадь, занимаемая арендатором в данном помещении              |
| actual_rate     | numeric                  |                                     | Фактическая ставка аренды за кв.м. для данного размещения                   |
| created_at      | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время создания записи                                                |
| updated_at      | timestamp with time zone | NOT NULL DEFAULT now()              | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (contract_id)` - Один договор может иметь только одно активное размещение
- `UNIQUE (room_id)` - Одно помещение может быть занято только одним арендатором
- `UNIQUE (start_date)` - Не может быть двух размещений с одинаковой датой начала
- `FOREIGN KEY (contract_id)` REFERENCES `contracts(id)`
- `FOREIGN KEY (room_id)` REFERENCES `physical.rooms(id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `dictionary.status_catalog(code, entity)`
- `FOREIGN KEY (usage_type_id)` REFERENCES `dictionary.placement_usage_types(id)`

### Таблица `payments`
Платежи по договорам.

| Колонка      | Тип                      | Ограничения                      | Комментарий                                                                 |
|--------------|--------------------------|----------------------------------|-----------------------------------------------------------------------------|
| id           | bigint                   | NOT NULL                         | Уникальный идентификатор платежа                                            |
| contract_id  | bigint                   | NOT NULL                         | Идентификатор договора, к которому относится платеж                        |
| placement_id | bigint                   |                                  | Идентификатор размещения, к которому относится платеж (если применимо)      |
| payment_date | date                     | NOT NULL                         | Дата осуществления платежа                                                  |
| amount       | numeric                  | NOT NULL                         | Сумма платежа                                                               |
| period_start | date                     | NOT NULL                         | Начало периода, за который производится оплата                              |
| period_end   | date                     | NOT NULL                         | Конец периода, за который производится оплата                               |
| payment_type | text                     |                                  | Тип платежа: advance (аванс), monthly (ежемесячный), penalty (штраф) и т.д. |
| status       | text                     | NOT NULL DEFAULT 'pending'::text | Статус платежа: pending (ожидает), processed (обработан), failed (неудачный)|
| created_at   | timestamp with time zone | NOT NULL DEFAULT now()           | Дата и время создания записи                                                |
| updated_at   | timestamp with time zone | NOT NULL DEFAULT now()           | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (contract_id)` REFERENCES `contracts(id)`
- `FOREIGN KEY (placement_id)` REFERENCES `placements(id)`

### Таблица `entity_responsibilities`
Назначение ответственных лиц к сущностям системы.

| Колонка             | Тип                      | Ограничения            | Комментарий                                                                 |
|---------------------|--------------------------|------------------------|-----------------------------------------------------------------------------|
| id                  | bigint                   | NOT NULL               | Уникальный идентификатор связи                                             |
| entity_type         | text                     | NOT NULL               | Тип сущности: building, room, equipment, contract, counterparty, complex   |
| entity_id           | bigint                   | NOT NULL               | Идентификатор сущности                                                     |
| person_id           | bigint                   | NOT NULL               | Идентификатор ответственного лица                                          |
| responsibility_type | text                     | NOT NULL               | Тип ответственности: technical, safety, legal, financial, administrative, operational |
| start_date          | date                     | NOT NULL               | Дата начала ответственности                                                |
| end_date            | date                     |                        | Дата окончания ответственности                                             |
| is_primary          | boolean                  | DEFAULT false          | Является ли основным ответственным                                         |
| notes               | text                     |                        | Дополнительные примечания                                                  |
| created_at          | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                |
| updated_at          | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (person_id)` REFERENCES `dictionary.responsible_persons(id)`
- `UNIQUE (entity_type, entity_id, person_id, responsibility_type)` - Уникальное назначение

---

## Схема `fire`

Пожарная безопасность и техническое обслуживание оборудования.

### Таблица `equipment_types`
Типы оборудования пожарной безопасности.

| Колонка        | Тип                        | Ограничения                           | Комментарий                                                                 |
|----------------|----------------------------|---------------------------------------|-----------------------------------------------------------------------------|
| id             | integer                    | NOT NULL                              | Уникальный идентификатор типа оборудования                                 |
| category       | character varying          | NOT NULL                              | Категория: CONTROLLER, SENSOR, INDICATOR, PLAN, OTHER                       |
| code           | character varying          | NOT NULL                              | Машинный код типа: control_panel, smoke_sensor, exit_sign, evacuation_plan  |
| name           | character varying          | NOT NULL                              | Название типа оборудования                                                  |
| description    | text                       |                                       | Описание типа оборудования и его назначения                                 |
| display_order  | integer                    | DEFAULT 0                             | Порядок отображения в интерфейсе                                           |
| created_at     | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP             | Дата и время создания записи                                                |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (code)`

### Таблица `buses`
Шины пожарной системы.

| Колонка                 | Тип                        | Ограничения                                    | Комментарий                                                                 |
|-------------------------|----------------------------|------------------------------------------------|-----------------------------------------------------------------------------|
| id                      | integer                    | NOT NULL                                      | Уникальный идентификатор шины                                              |
| name                    | character varying          | NOT NULL                                      | Наименование шины                                                          |
| description             | text                       |                                                | Описание шины и ее назначения                                              |
| controller_equipment_id | integer                    | NOT NULL                                      | Идентификатор контроллера, управляющего шиной                              |
| total_wire_pairs        | integer                    | NOT NULL                                      | Общее количество пар проводов в шине                                       |
| bus_type                | character varying          | DEFAULT 'radial'::character varying            | Тип шины: radial - радиальная, ring - кольцевая, combined - комбинированная |
| voltage                 | numeric                    |                                                | Рабочее напряжение шины                                                    |
| status_entity           | character varying          | NOT NULL DEFAULT 'bus'::character varying      | Тип сущности для статуса                                                   |
| status_code             | character varying          | NOT NULL DEFAULT 'active'::character varying   | Код статуса шины                                                           |
| created_at              | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP                      | Дата и время создания записи                                               |
| updated_at              | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP                      | Дата и время последнего обновления записи                                  |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (controller_equipment_id)` REFERENCES `equipment(id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `dictionary.status_catalog(code, entity)`

### Таблица `equipment`
Оборудование пожарной безопасности.

| Колонка           | Тип                        | Ограничения                                    | Комментарий                                                                 |
|-------------------|----------------------------|------------------------------------------------|-----------------------------------------------------------------------------|
| id                | integer                    | NOT NULL                                      | Уникальный идентификатор оборудования                                       |
| equipment_type_id | integer                    | NOT NULL                                      | Идентификатор типа оборудования                                             |
| serial_number     | character varying          |                                                | Серийный номер оборудования (уникальный)                                    |
| model             | character varying          |                                                | Модель оборудования                                                         |
| manufacturer      | character varying          |                                                | Производитель оборудования                                                  |
| parent_id         | integer                    |                                                | Ссылка на родительское оборудование (для иерархии)                          |
| controller_id     | integer                    |                                                | Контроллер, который управляет этим оборудованием                            |
| room_id           | integer                    |                                                | Идентификатор помещения, где установлено оборудование                       |
| zone_id           | integer                    |                                                | Идентификатор зоны в помещении, где установлено оборудование                |
| bus_id            | integer                    |                                                | Шина, к которой подключено оборудование                       |
| wire_pair_number  | integer                    |                                                | Номер пары проводов в шине (1..N)                                           |
| status_entity     | character varying          | NOT NULL DEFAULT 'equipment'::character varying| Тип сущности для статуса                                                   |
| status_code       | character varying          | NOT NULL DEFAULT 'active'::character varying   | Код статуса оборудования                                                    |
| installation_date | date                       |                                                | Дата установки оборудования                                                 |
| last_check_date   | date                       |                                                | Дата последней проверки оборудования                                        |
| next_check_date   | date                       |                                                | Дата следующей плановой проверки оборудования                               |
| parameters        | jsonb                      | DEFAULT '{}'::jsonb                            | Технические параметры в формате JSON (мощность, напряжение, протокол и т.д.)|
| created_at        | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP                      | Дата и время создания записи                                                |
| updated_at        | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP                      | Дата и время последнего обновления записи                                   |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (serial_number)`
- `FOREIGN KEY (bus_id)` REFERENCES `buses(id)`
- `FOREIGN KEY (controller_id)` REFERENCES `equipment(id)`
- `FOREIGN KEY (equipment_type_id)` REFERENCES `equipment_types(id)`
- `FOREIGN KEY (parent_id)` REFERENCES `equipment(id)`
- `FOREIGN KEY (room_id)` REFERENCES `physical.rooms(id)`
- `FOREIGN KEY (status_code, status_entity)` REFERENCES `dictionary.status_catalog(code, entity)`
- `FOREIGN KEY (zone_id)` REFERENCES `physical.zones(id)`

### Таблица `equipment_connections`
Связи между оборудованием.

| Колонка              | Тип                        | Ограничения                                    | Комментарий                                                                 |
|----------------------|----------------------------|------------------------------------------------|-----------------------------------------------------------------------------|
| id                   | integer                    | NOT NULL                                      | Уникальный идентификатор связи                                              |
| source_equipment_id  | integer                    | NOT NULL                                      | Идентификатор исходного оборудования                                        |
| target_equipment_id  | integer                    | NOT NULL                                      | Идентификатор целевого оборудования                                         |
| connection_type      | character varying          | NOT NULL DEFAULT 'control'::character varying  | Тип связи: control - управление, power - питание, control_power - управление+питание, signal - сигнализация, backup - резервирование |
| direction            | character varying          | NOT NULL DEFAULT 'bidirectional'::character varying | Направление: unidirectional - однонаправленная, bidirectional - двунаправленная |
| parameters           | jsonb                      | DEFAULT '{}'::jsonb                            | Дополнительные параметры соединения в формате JSON                         |
| created_at           | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP                      | Дата и время создания записи                                                |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `UNIQUE (source_equipment_id, target_equipment_id, connection_type)` - Уникальная комбинация связи
- `FOREIGN KEY (source_equipment_id)` REFERENCES `equipment(id)`
- `FOREIGN KEY (target_equipment_id)` REFERENCES `equipment(id)`

### Таблица `equipment_events`
События оборудования.

| Колонка       | Тип                        | Ограничения                                    | Комментарий                                                                 |
|---------------|----------------------------|------------------------------------------------|-----------------------------------------------------------------------------|
| id            | integer                    | NOT NULL                                      | Уникальный идентификатор события                                            |
| equipment_id  | integer                    | NOT NULL                                      | Идентификатор оборудования, с которым связано событие                      |
| event_type    | character varying          | NOT NULL                                      | Тип события: alarm - тревога, fault - неисправность, test - тест, manual_check - ручная проверка, status_change - изменение статуса |
| severity      | character varying          | DEFAULT 'info'::character varying              | Важность: info - информация, warning - предупреждение, error - ошибка, critical - критическая |
| old_status    | character varying          |                                                | Предыдущий статус оборудования                                              |
| new_status    | character varying          |                                                | Новый статус оборудования                                                   |
| value         | numeric                    |                                                | Значение, связанное с событием (например, температура, давление)           |
| unit          | character varying          |                                                | Единица измерения значения                                                  |
| description   | text                       |                                                | Подробное описание события                                                  |
| triggered_at  | timestamp without time zone| NOT NULL DEFAULT CURRENT_TIMESTAMP             | Время возникновения события                                                 |
| resolved_at   | timestamp without time zone|                                                | Время разрешения события                                                    |
| resolved_by   | character varying          |                                                | Пользователь или система, разрешившая событие                              |
| created_at    | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP                      | Дата и время создания записи                                                |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (equipment_id)` REFERENCES `equipment(id)`

### Таблица `equipment_location_history`
История перемещения оборудования.

| Колонка       | Тип                        | Ограничения                           | Комментарий                                                                 |
|---------------|----------------------------|---------------------------------------|-----------------------------------------------------------------------------|
| id            | integer                    | NOT NULL                              | Уникальный идентификатор записи истории                                     |
| equipment_id  | integer                    | NOT NULL                              | Идентификатор перемещаемого оборудования                                   |
| from_room_id  | integer                    |                                       | Идентификатор исходного помещения                                           |
| from_zone_id  | integer                    |                                       | Идентификатор исходной зоны в помещении                                    |
| to_room_id    | integer                    |                                       | Идентификатор целевого помещения                                           |
| to_zone_id    | integer                    |                                       | Идентификатор целевой зоны в помещении                                     |
| moved_at      | timestamp without time zone| NOT NULL DEFAULT CURRENT_TIMESTAMP    | Дата и время перемещения                                                   |
| moved_by      | character varying          |                                       | Пользователь, выполнивший перемещение                                      |
| reason        | text                       |                                       | Причина перемещения оборудования                                           |
| created_at    | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP             | Дата и время создания записи                                               |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (equipment_id)` REFERENCES `equipment(id)`
- `FOREIGN KEY (from_room_id)` REFERENCES `physical.rooms(id)`
- `FOREIGN KEY (from_zone_id)` REFERENCES `physical.zones(id)`
- `FOREIGN KEY (to_room_id)` REFERENCES `physical.rooms(id)`
- `FOREIGN KEY (to_zone_id)` REFERENCES `physical.zones(id)`

### Таблица `maintenance_schedule`
График технического обслуживания.

| Колонка               | Тип                        | Ограничения                           | Комментарий                                                                 |
|-----------------------|----------------------------|---------------------------------------|-----------------------------------------------------------------------------|
| id                    | integer                    | NOT NULL                              | Уникальный идентификатор графика обслуживания                              |
| equipment_id          | integer                    | NOT NULL                              | Идентификатор оборудования для обслуживания                                |
| maintenance_type      | character varying          | NOT NULL                              | Тип работ: inspection - проверка, replacement - замена, calibration - калибровка, cleaning - чистка |
| description           | text                       |                                       | Описание работ по обслуживанию                                             |
| interval_days         | integer                    | NOT NULL                              | Периодичность проведения работ в днях                                      |
| last_maintenance_date | date                       |                                       | Дата последнего обслуживания                                               |
| next_maintenance_date | date                       |                                       | Дата следующего планового обслуживания                                     |
| assigned_to           | character varying          |                                       | Ответственный за выполнение работ                                          |
| is_active             | boolean                    | DEFAULT true                          | Активен ли график обслуживания                                             |
| created_at            | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP             | Дата и время создания записи                                                |
| updated_at            | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP             | Дата и время последнего обновления записи                                  |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (equipment_id)` REFERENCES `equipment(id)`

### Таблица `maintenance_log`
Журнал технического обслуживания.

| Колонка           | Тип                        | Ограничения                                   | Комментарий                                                                 |
|-------------------|----------------------------|-----------------------------------------------|-----------------------------------------------------------------------------|
| id                | integer                    | NOT NULL                                      | Уникальный идентификатор записи обслуживания                                |
| equipment_id      | integer                    | NOT NULL                                      | Идентификатор обслуживаемого оборудования                                   |
| schedule_id       | integer                    |                                               | Идентификатор графика обслуживания (если было запланировано)                |
| maintenance_date  | date                       | NOT NULL DEFAULT CURRENT_DATE                 | Дата проведения обслуживания                                                |
| maintenance_type  | character varying          | NOT NULL                                      | Тип работ: inspection - проверка, replacement - замена, calibration - калибровка, cleaning - чистка |
| performed_by      | character varying          | NOT NULL                                      | Кто выполнил обслуживание                                                   |
| result            | character varying          | NOT NULL DEFAULT 'completed'::character varying | Результат: completed - выполнено, failed - не выполнено, postponed - отложено |
| cost              | numeric                    |                                               | Стоимость выполненных работ                                                 |
| work_description  | text                       |                                               | Описание выполненных работ                                                  |
| notes             | text                       |                                               | Дополнительные заметки                                                      |
| problems_found    | text                       |                                               | Обнаруженные проблемы                                                       |
| checklist_url     | text                       |                                               | Ссылка на чек-лист или отчет                                                |
| created_at        | timestamp without time zone| DEFAULT CURRENT_TIMESTAMP                     | Дата и время создания записи                                                |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`
- `FOREIGN KEY (equipment_id)` REFERENCES `equipment(id)`
- `FOREIGN KEY (schedule_id)` REFERENCES `maintenance_schedule(id)`

### Вспомогательные таблицы схемы `fire` (представления)

**`active_events`** - Активные события пожарной безопасности  
**`equipment_hierarchy`** - Иерархия оборудования  
**`overdue_maintenance`** - Просроченное обслуживание

---

## Схема `audit`

Аудит изменений и системное журналирование.

### Таблица `change_log`
Журнал изменений данных в системе.

| Колонка      | Тип                      | Ограничения            | Комментарий                                                                 |
|--------------|--------------------------|------------------------|-----------------------------------------------------------------------------|
| id           | bigint                   | NOT NULL               | Уникальный идентификатор записи в журнале                                   |
| table_name   | text                     | NOT NULL               | Наименование таблицы, в которой произошли изменения                         |
| record_id    | bigint                   | NOT NULL               | Идентификатор изменяемой записи в целевой таблице                           |
| operation    | text                     | NOT NULL               | Тип операции: INSERT, UPDATE, DELETE                                        |
| old_values   | jsonb                    |                        | Значения полей до изменения (в формате JSON)                                |
| new_values   | jsonb                    |                        | Значения полей после изменения (в формате JSON)                             |
| changed_by   | text                     |                        | Пользователь или система, внесшая изменения                                 |
| changed_at   | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время изменения                                                      |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`

### Таблица `system_log`
Системный журнал событий.

| Колонка      | Тип                      | Ограничения            | Комментарий                                                                 |
|--------------|--------------------------|------------------------|-----------------------------------------------------------------------------|
| id           | bigint                   | NOT NULL               | Уникальный идентификатор записи в системном журнале                         |
| log_level    | text                     | NOT NULL               | Уровень логирования: DEBUG, INFO, WARN, ERROR, FATAL                        |
| module       | text                     |                        | Модуль или компонент системы, сгенерировавший событие                       |
| message      | text                     | NOT NULL               | Текст сообщения или события                                                 |
| details      | jsonb                    |                        | Дополнительные данные события в формате JSON                                |
| user_id      | text                     |                        | Идентификатор пользователя, связанного с событием                           |
| ip_address   | inet                     |                        | IP-адрес источника события                                                  |
| created_at   | timestamp with time zone | NOT NULL DEFAULT now() | Дата и время создания записи                                                |

**Ключи и ограничения:**
- `PRIMARY KEY (id)`

---

## Схема `public`

Служебные таблицы для технических нужд.

### Таблица `export_all_data`
Таблица для экспорта данных (служебная).

| Колонка       | Тип  | Ограничения | Комментарий                                                                 |
|---------------|------|-------------|-----------------------------------------------------------------------------|
| source_table  | text |             | Наименование исходной таблицы, из которой экспортированы данные            |
| data          | jsonb|             | Экспортированные данные в формате JSON                                     |

---

## Примеры разграничения доступа:

### 1. **Маркофф (системный администратор)**
- Роль: `sysadmin`
- Контекст: `global`
- Видимость: все данные во всех схемах
- Правила: `visibility_context = 'all'` для всех таблиц

### 2. **Юрист "ООО Хозяин"**
- Роль: `lawyer`
- Контекст: `counterparty = 1` (ООО Хозяин)
- Видимость: 
  - Договоры своих контрагентов
  - Контрагенты типа `tenant`
  - Контакты с категориями `legal`, `general`
  - Помещения и здания
- Не видит: пожарное оборудование, технические контакты

### 3. **Вася (техник "ООО ПОЖАРНИК")**
- Роль: `technician`
- Контекст: `counterparty = 3` (ООО ПОЖАРНИК)
- Видимость:
  - Все пожарное оборудование
  - Свои записи обслуживания
  - Помещения (только номер и расположение)
  - Контакты с категориями `fire_safety`, `technical`, `emergency`
- Не видит: договоры, финансовую информацию, юридические контакты

### 4. **Сотрудник "ООО РОМАШКА"**
- Роль: `tenant_admin`
- Контекст: `counterparty = 2` (ООО РОМАШКА)
- Видимость:
  - Свои договоры
  - Занятые помещения
  - Свои контактные лица
  - Технические контакты для связи по пожарке
- Не видит: оборудование других арендаторов, финансовые отчеты

---

## Реализация безопасности:

### 1. **Row Level Security (RLS)**
```sql
-- Включение RLS на критических таблицах
ALTER TABLE business.contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE dictionary.counterparties ENABLE ROW LEVEL SECURITY;
ALTER TABLE fire.equipment ENABLE ROW LEVEL SECURITY;

-- Создание политик видимости на основе ролей
CREATE POLICY contracts_visibility ON business.contracts
FOR SELECT USING (
  security.check_user_access(
    current_user, 
    'contracts', 
    counterparty_id
  )
);
