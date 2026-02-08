# База данных системы управления недвижимостью и пожарной безопасностью

## Структура базы данных

База данных организована в шесть тематических схем:

1. `security`   – Управление пользователями, ролями и правами доступа
2. `dictionary` – Централизованные справочники системы
3. `physical`   – Физическая структура объектов недвижимости
4. `business`   – Бизнес-процессы аренды и управления недвижимостью
5. `fire`       – Пожарная безопасность и техническое обслуживание оборудования
6. `audit`      – Аудит изменений и системное журналирование

---

## Схема `security`

### Таблица `users`
| Колонка               | Тип         | Ограничения            | Комментарий                                    |
|-----------------------|-------------|------------------------|------------------------------------------------|
| id                    | bigint      | NOT NULL               | Уникальный идентификатор пользователя системы  |
| username              | text        | NOT NULL UNIQUE        | Логин для входа в систему                      |
| password_hash         | text        | NOT NULL               | Хэш пароля                                     |
| person_id             | bigint      | NOT NULL               | Ссылка на responsible_persons.id               |
| is_active             | boolean     | DEFAULT true           | Активен ли пользователь                        |
| must_change_password  | boolean     | DEFAULT true           | Требуется сменить пароль при первом входе      |
| last_login_at         | timestamptz |                        | Дата и время последнего входа                  |
| failed_login_attempts | integer     | DEFAULT 0              | Количество неудачных попыток входа             |
| locked_until          | timestamptz |                        | Время блокировки                               |
| mfa_enabled           | boolean     | DEFAULT false          | Включена ли двухфакторная аутентификация       |
| mfa_secret            | text        |                        | Секрет для двухфакторной аутентификации        |
| created_at            | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                           |
| updated_at            | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                         |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (person_id) REFERENCES dictionary.responsible_persons(id)

### Таблица `roles`
| Колонка     | Тип         | Ограничения            | Комментарий                             |
|-------------|-------------|------------------------|-----------------------------------------|
| id          | bigint      | NOT NULL               | Уникальный идентификатор роли          |
| code        | text        | NOT NULL UNIQUE        | Код роли (sysadmin, lawyer, technician)|
| name        | text        | NOT NULL               | Название роли                          |
| description | text        |                        | Описание роли                          |
| is_system   | boolean     | DEFAULT false          | Системная роль                         |
| created_at  | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at  | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- UNIQUE (code)

### Таблица `user_roles`
| Колонка             | Тип         | Ограничения            | Комментарий                             |
|---------------------|-------------|------------------------|-----------------------------------------|
| id                  | bigint      | NOT NULL               | Уникальный идентификатор назначения    |
| user_id             | bigint      | NOT NULL               | Идентификатор пользователя             |
| role_id             | bigint      | NOT NULL               | Идентификатор роли                     |
| context_entity_type | text        |                        | Тип сущности контекста                  |
| context_entity_id   | bigint      |                        | ID сущности контекста                   |
| is_primary          | boolean     | DEFAULT false          | Основная ли роль                       |
| granted_by          | bigint      |                        | Кто выдал роль                          |
| granted_at          | timestamptz | NOT NULL DEFAULT now() | Дата выдачи роли                       |
| valid_until         | timestamptz |                        | Дата окончания действия роли           |
| is_active           | boolean     | DEFAULT true           | Активна ли роль                        |
| created_at          | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at          | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- UNIQUE (user_id, role_id, context_entity_type, COALESCE(context_entity_id, 0))
- FOREIGN KEY (user_id) REFERENCES users(id)
- FOREIGN KEY (role_id) REFERENCES roles(id)
- FOREIGN KEY (granted_by) REFERENCES users(id)

### Таблица `data_visibility_rules`
| Колонка            | Тип         | Ограничения            | Комментарий                             |
|--------------------|-------------|------------------------|-----------------------------------------|
| id                 | bigint      | NOT NULL               | Уникальный идентификатор правила       |
| role_id            | bigint      | NOT NULL               | Идентификатор роли                     |
| table_schema       | text        | NOT NULL               | Схема таблицы                          |
| table_name         | text        | NOT NULL               | Имя таблицы                            |
| column_name        | text        |                        | Имя колонки                            |
| visibility_context | text        | NOT NULL               | Контекст видимости                     |
| condition_sql      | text        |                        | SQL-условие                            |
| priority           | integer     | DEFAULT 0              | Приоритет применения                   |
| is_active          | boolean     | DEFAULT true           | Активно ли правило                     |
| created_at         | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at         | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (role_id) REFERENCES roles(id)

### Таблица `session_log`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор сессии        |
| user_id      | bigint      | NOT NULL               | Идентификатор пользователя             |
| session_token| text        | NOT NULL               | Токен сессии                           |
| ip_address   | inet        |                        | IP-адрес входа                         |
| user_agent   | text        |                        | User-Agent браузера                    |
| login_at     | timestamptz | NOT NULL DEFAULT now() | Время входа                            |
| logout_at    | timestamptz |                        | Время выхода                           |
| is_active    | boolean     | DEFAULT true           | Активна ли сессия                      |
| created_at   | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at   | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (user_id) REFERENCES users(id)

---

## Схема `dictionary`

### Таблица `physical_room_types`
| Колонка              | Тип         | Ограничения                         | Комментарий                                     |
|----------------------|-------------|-------------------------------------|-------------------------------------------------|
| id                   | bigint      | NOT NULL                            | Первичный ключ, автоинкремент                  |
| code                 | text        | NOT NULL UNIQUE                     | Машинный код (office, warehouse)               |
| name                 | text        | NOT NULL                            | Человекочитаемое название типа помещения       |
| description          | text        |                                     | Подробное описание типа помещения              |
| fire_safety_category | character   |                                     | Категория пожарной опасности (A, B, C, D, F)   |
| is_rentable          | boolean     | NOT NULL DEFAULT true               | Можно ли сдавать в аренду                      |
| base_rate_weight     | numeric(5,2)| NOT NULL DEFAULT 1.0                | Базовый коэффициент для расчёта ставки         |
| created_at           | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                           |
| updated_at           | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                         |
| display_order        | integer     |                                     | Порядок отображения в интерфейсе               |
| is_active            | boolean     | NOT NULL DEFAULT true               | Активен ли тип для выбора                      |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `placement_usage_types`
| Колонка                  | Тип         | Ограничения                         | Комментарий                                     |
|--------------------------|-------------|-------------------------------------|-------------------------------------------------|
| id                       | bigint      | NOT NULL                            | Первичный ключ, автоинкремент                  |
| code                     | text        | NOT NULL UNIQUE                     | Машинный код (office, warehouse)               |
| name                     | text        | NOT NULL                            | Название типа                                  |
| description              | text        |                                     | Описание типа                                  |
| rate_multiplier          | numeric(5,2)| NOT NULL DEFAULT 1.0                | Множитель к базовой ставке помещения           |
| requires_special_agreement| boolean    | NOT NULL DEFAULT false              | Требует отдельного соглашения                  |
| compatible_physical_types| jsonb       |                                     | Массив кодов physical_room_types для совместимости |
| created_at               | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                           |
| updated_at               | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                         |
| display_order            | integer     |                                     | Порядок отображения в интерфейсе               |
| is_active                | boolean     | NOT NULL DEFAULT true               | Активен ли тип для выбора                      |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `sensor_types`
| Колонка           | Тип         | Ограничения                         | Комментарий                                     |
|-------------------|-------------|-------------------------------------|-------------------------------------------------|
| id                | bigint      | NOT NULL                            | Первичный ключ, автоинкремент                  |
| code              | text        | NOT NULL UNIQUE                     | Машинный код (smoke, heat, manual)             |
| name              | text        | NOT NULL                            | Название датчика                               |
| description       | text        |                                     | Описание датчика                               |
| check_interval_days| integer    |                                     | Рекомендуемый интервал проверки в днях         |
| default_status    | text        | NOT NULL DEFAULT 'active'           | Статус по умолчанию при установке              |
| display_order     | integer     |                                     | Порядок отображения в интерфейсе               |
| created_at        | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                           |
| updated_at        | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                         |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `counterparties`
| Колонка        | Тип         | Ограничения                         | Комментарий                                     |
|----------------|-------------|-------------------------------------|-------------------------------------------------|
| id             | bigint      | NOT NULL                            | Уникальный идентификатор контрагента           |
| type           | text        | NOT NULL DEFAULT 'tenant'           | Тип: landlord, tenant, supplier, contractor, service |
| short_name     | text        | NOT NULL                            | Краткое название                               |
| full_name      | text        |                                     | Полное юридическое название                    |
| tax_id         | text        |                                     | ИНН                                            |
| legal_address  | text        |                                     | Юридический адрес                              |
| actual_address | text        |                                     | Фактический адрес                              |
| bank_details   | jsonb       |                                     | Банковские реквизиты в формате JSON            |
| status_code    | varchar(20) | FK, NOT NULL DEFAULT 'active'       | Ссылка на counterparty_statuses.code           |
| notes          | text        |                                     | Дополнительные заметки                         |
| created_at     | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                           |
| updated_at     | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                         |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (status_code) REFERENCES counterparty_statuses(code)

### Таблица `responsible_persons`
| Колонка            | Тип         | Ограничения                         | Комментарий                                     |
|--------------------|-------------|-------------------------------------|-------------------------------------------------|
| id                 | bigint      | NOT NULL                            | Уникальный идентификатор ответственного лица   |
| counterparty_id    | bigint      |                                     | Идентификатор контрагента                      |
| person_name        | text        | NOT NULL                            | ФИО ответственного лица                        |
| position           | text        |                                     | Должность                                      |
| department         | text        |                                     | Подразделение/отдел                            |
| role_code          | text        | NOT NULL                            | Код роли                                       |
| phone              | text        |                                     | Контактный телефон                             |
| email              | text        |                                     | Электронная почта                              |
| contact_categories | text[]      | DEFAULT '{}'                        | Категории: legal, fire_safety, technical, financial, emergency, general |
| is_public_contact  | boolean     | DEFAULT false                       | Является ли публичным контактом                |
| is_active          | boolean     | NOT NULL DEFAULT true               | Активен ли сотрудник                           |
| hire_date          | date        |                                     | Дата приема на работу                          |
| termination_date   | date        |                                     | Дата увольнения                                |
| notes              | text        |                                     | Дополнительные заметки                         |
| created_at         | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                           |
| updated_at         | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                         |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (counterparty_id) REFERENCES counterparties(id)
- FOREIGN KEY (role_code) REFERENCES role_catalog(code)

### Таблица `role_catalog`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор роли          |
| code         | text        | NOT NULL UNIQUE        | Код роли                                |
| name         | text        | NOT NULL               | Название роли                          |
| description  | text        |                        | Описание роли                          |
| category     | text        | NOT NULL               | Категория: safety, technical, legal, financial, management, contact, other |
| display_order| integer     |                        | Порядок отображения                    |
| is_active    | boolean     | DEFAULT true           | Активна ли роль                        |
| created_at   | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at   | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `contact_categories`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор категории     |
| code         | text        | NOT NULL UNIQUE        | Код категории                           |
| name         | text        | NOT NULL               | Название категории                      |
| description  | text        |                        | Описание категории                      |
| allowed_roles| text[]      |                        | Массив ролей, которые могут видеть эти контакты |
| created_at   | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at   | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `counterparty_statuses`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор статуса       |
| code         | varchar(20) | NOT NULL UNIQUE        | Код статуса: active, suspended, archived |
| name         | varchar(100)| NOT NULL               | Название статуса                        |
| description  | text        |                        | Описание                                |
| is_initial   | boolean     | DEFAULT false          | Можно ли установить при создании        |
| display_order| integer     | DEFAULT 0              | Порядок отображения                    |
| created_at   | timestamptz | DEFAULT now()          | Дата создания записи                   |
| updated_at   | timestamptz | DEFAULT now()          | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `room_statuses`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор статуса       |
| code         | varchar(20) | NOT NULL UNIQUE        | Код статуса: available, occupied, renovation |
| name         | varchar(100)| NOT NULL               | Название статуса                        |
| description  | text        |                        | Описание                                |
| is_initial   | boolean     | DEFAULT false          | Можно ли установить при создании        |
| allows_rent  | boolean     | DEFAULT false          | Можно ли сдавать в этом статусе         |
| display_order| integer     | DEFAULT 0              | Порядок отображения                    |
| created_at   | timestamptz | DEFAULT now()          | Дата создания записи                   |
| updated_at   | timestamptz | DEFAULT now()          | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `contract_statuses`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор статуса       |
| code         | varchar(20) | NOT NULL UNIQUE        | Код статуса: draft, active, expired, terminated |
| name         | varchar(100)| NOT NULL               | Название статуса                        |
| description  | text        |                        | Описание                                |
| is_initial   | boolean     | DEFAULT false          | Можно ли установить при создании        |
| is_terminal  | boolean     | DEFAULT false          | Конечный ли статус                      |
| display_order| integer     | DEFAULT 0              | Порядок отображения                    |
| created_at   | timestamptz | DEFAULT now()          | Дата создания записи                   |
| updated_at   | timestamptz | DEFAULT now()          | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `placement_statuses`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор статуса       |
| code         | varchar(20) | NOT NULL UNIQUE        | Код статуса: planned, active, completed, cancelled |
| name         | varchar(100)| NOT NULL               | Название статуса                        |
| description  | text        |                        | Описание                                |
| is_initial   | boolean     | DEFAULT false          | Можно ли установить при создании        |
| display_order| integer     | DEFAULT 0              | Порядок отображения                    |
| created_at   | timestamptz | DEFAULT now()          | Дата создания записи                   |
| updated_at   | timestamptz | DEFAULT now()          | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `payment_statuses`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор статуса       |
| code         | varchar(20) | NOT NULL UNIQUE        | Код статуса: pending, processed, failed, refunded |
| name         | varchar(100)| NOT NULL               | Название статуса                        |
| description  | text        |                        | Описание                                |
| is_initial   | boolean     | DEFAULT false          | Можно ли установить при создании        |
| is_success   | boolean     | DEFAULT false          | Успешный ли платеж                     |
| display_order| integer     | DEFAULT 0              | Порядок отображения                    |
| created_at   | timestamptz | DEFAULT now()          | Дата создания записи                   |
| updated_at   | timestamptz | DEFAULT now()          | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `equipment_statuses`
| Колонка      | Тип         | Ограничения            | Комментарий                             |
|--------------|-------------|------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL               | Уникальный идентификатор статуса       |
| code         | varchar(20) | NOT NULL UNIQUE        | Код статуса: active, inactive, maintenance, decommissioned |
| name         | varchar(100)| NOT NULL               | Название статуса                        |
| description  | text        |                        | Описание                                |
| is_initial   | boolean     | DEFAULT false          | Можно ли установить при создании        |
| is_operational| boolean    | DEFAULT true           | Работоспособен ли в этом статусе        |
| display_order| integer     | DEFAULT 0              | Порядок отображения                    |
| created_at   | timestamptz | DEFAULT now()          | Дата создания записи                   |
| updated_at   | timestamptz | DEFAULT now()          | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `building_statuses`
| Колонка         | Тип         | Ограничения            | Комментарий                             |
|-----------------|-------------|------------------------|-----------------------------------------|
| id              | bigint      | NOT NULL               | Уникальный идентификатор статуса       |
| code            | varchar(20) | NOT NULL UNIQUE        | Код статуса: operational, renovation, closed, demolished |
| name            | varchar(100)| NOT NULL               | Название статуса                        |
| description     | text        |                        | Описание                                |
| is_initial      | boolean     | DEFAULT false          | Можно ли установить при создании        |
| allows_occupancy| boolean     | DEFAULT true           | Можно ли занимать здание                |
| display_order   | integer     | DEFAULT 0              | Порядок отображения                    |
| created_at      | timestamptz | DEFAULT now()          | Дата создания записи                   |
| updated_at      | timestamptz | DEFAULT now()          | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

---

## Схема `physical`

### Таблица `complexes`
| Колонка    | Тип         | Ограничения            | Комментарий                             |
|------------|-------------|------------------------|-----------------------------------------|
| id         | bigint      | NOT NULL               | Уникальный идентификатор комплекса     |
| name       | text        | NOT NULL UNIQUE        | Наименование комплекса                 |
| description| text        |                        | Описание комплекса                     |
| address    | text        |                        | Адрес комплекса                        |
| owner_id   | bigint      |                        | Идентификатор контрагента-владельца    |
| created_at | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (owner_id) REFERENCES dictionary.counterparties(id)

### Таблица `buildings`
| Колонка         | Тип         | Ограничения                         | Комментарий                             |
|-----------------|-------------|-------------------------------------|-----------------------------------------|
| id              | bigint      | NOT NULL                            | Уникальный идентификатор здания        |
| complex_id      | bigint      | NOT NULL                            | Идентификатор комплекса                |
| name            | text        | NOT NULL                            | Наименование здания                    |
| description     | text        |                                     | Описание здания                        |
| address         | text        |                                     | Адрес здания                           |
| floors_count    | integer     | NOT NULL CHECK (floors_count > 0)   | Общее количество этажей                |
| physical_type_id| bigint      | NOT NULL                            | Ссылка на physical_room_types.id       |
| status_code     | varchar(20) | FK, NOT NULL                        | Ссылка на building_statuses.code       |
| created_at      | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                   |
| updated_at      | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- UNIQUE (complex_id, name)
- FOREIGN KEY (complex_id) REFERENCES complexes(id)
- FOREIGN KEY (physical_type_id) REFERENCES dictionary.physical_room_types(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.building_statuses(code)

### Таблица `floors`
| Колонка         | Тип         | Ограничения                         | Комментарий                             |
|-----------------|-------------|-------------------------------------|-----------------------------------------|
| id              | bigint      | NOT NULL                            | Уникальный идентификатор этажа         |
| building_id     | bigint      | NOT NULL                            | Идентификатор здания                   |
| number          | integer     | NOT NULL                            | Номер этажа (0 - цоколь, -1 - подвал)  |
| description     | text        |                                     | Описание этажа                         |
| physical_type_id| bigint      | NOT NULL                            | Ссылка на physical_room_types.id       |
| status_code     | varchar(20) | FK, NOT NULL                        | Ссылка на room_statuses.code           |
| plan_image_url  | text        |                                     | Ссылка на план этажа                   |
| created_at      | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                   |
| updated_at      | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- UNIQUE (building_id, number)
- FOREIGN KEY (building_id) REFERENCES buildings(id)
- FOREIGN KEY (physical_type_id) REFERENCES dictionary.physical_room_types(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.room_statuses(code)

### Таблица `rooms`
| Колонка         | Тип         | Ограничения                         | Комментарий                             |
|-----------------|-------------|-------------------------------------|-----------------------------------------|
| id              | bigint      | NOT NULL                            | Уникальный идентификатор помещения     |
| floor_id        | bigint      | NOT NULL                            | Идентификатор этажа                    |
| number          | text        | NOT NULL                            | Номер помещения (101А, 201Б)           |
| description     | text        |                                     | Описание помещения                     |
| area            | numeric(10,2)|                                     | Площадь помещения в кв.м.              |
| physical_type_id| bigint      | NOT NULL                            | Ссылка на physical_room_types.id       |
| status_code     | varchar(20) | FK, NOT NULL                        | Ссылка на room_statuses.code           |
| max_tenants     | integer     |                                     | Максимальное количество арендаторов    |
| created_at      | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                   |
| updated_at      | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- UNIQUE (floor_id, number)
- FOREIGN KEY (floor_id) REFERENCES floors(id)
- FOREIGN KEY (physical_type_id) REFERENCES dictionary.physical_room_types(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.room_statuses(code)

### Таблица `zones`
| Колонка            | Тип         | Ограничения            | Комментарий                             |
|--------------------|-------------|------------------------|-----------------------------------------|
| id                 | bigint      | NOT NULL               | Уникальный идентификатор зоны          |
| room_id            | bigint      | NOT NULL               | Идентификатор помещения                |
| name               | text        | NOT NULL               | Название зоны                          |
| description        | text        |                        | Описание зоны                          |
| polygon_coordinates| jsonb       |                        | Координаты полигона зоны в JSON        |
| created_at         | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at         | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- UNIQUE (room_id, name)
- FOREIGN KEY (room_id) REFERENCES rooms(id)

---

## Схема `business`

### Таблица `contracts`
| Колонка        | Тип         | Ограничения                         | Комментарий                             |
|----------------|-------------|-------------------------------------|-----------------------------------------|
| id             | bigint      | NOT NULL                            | Уникальный идентификатор договора      |
| counterparty_id| bigint      | NOT NULL                            | Идентификатор контрагента-арендатора   |
| contract_number| text        | NOT NULL UNIQUE                     | Уникальный номер договора              |
| description    | text        |                                     | Описание договора                      |
| start_date     | date        | NOT NULL                            | Дата начала действия                   |
| end_date       | date        | NOT NULL                            | Дата окончания                         |
| status_code    | varchar(20) | FK, NOT NULL                        | Ссылка на contract_statuses.code       |
| monthly_payment| decimal(15,2)|                                     | Ежемесячный платеж                     |
| payment_day    | integer     | CHECK (payment_day >= 1 AND payment_day <= 31) | День месяца оплаты     |
| created_at     | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                   |
| updated_at     | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (counterparty_id) REFERENCES dictionary.counterparties(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.contract_statuses(code)
- CHECK (end_date > start_date)

### Таблица `placements`
| Колонка      | Тип         | Ограничения                         | Комментарий                             |
|--------------|-------------|-------------------------------------|-----------------------------------------|
| id           | bigint      | NOT NULL                            | Уникальный идентификатор размещения    |
| contract_id  | bigint      | NOT NULL                            | Идентификатор договора аренды          |
| room_id      | bigint      | NOT NULL                            | Идентификатор помещения                |
| usage_type_id| bigint      | NOT NULL                            | Ссылка на placement_usage_types.id     |
| start_date   | date        | NOT NULL                            | Дата начала аренды помещения           |
| end_date     | date        |                                     | Дата окончания (NULL - бессрочно)      |
| status_code  | varchar(20) | FK, NOT NULL                        | Ссылка на placement_statuses.code      |
| area_used    | numeric(10,2)| NOT NULL CHECK (area_used > 0)     | Фактически используемая площадь        |
| actual_rate  | decimal(15,2)|                                     | Ставка аренды для этого помещения      |
| created_at   | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                   |
| updated_at   | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- UNIQUE (room_id)
- FOREIGN KEY (contract_id) REFERENCES contracts(id)
- FOREIGN KEY (room_id) REFERENCES physical.rooms(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.placement_statuses(code)
- FOREIGN KEY (usage_type_id) REFERENCES dictionary.placement_usage_types(id)
- CHECK (end_date IS NULL OR end_date > start_date)

### Таблица `payments`
| Колонка     | Тип         | Ограничения                         | Комментарий                             |
|-------------|-------------|-------------------------------------|-----------------------------------------|
| id          | bigint      | NOT NULL                            | Уникальный идентификатор платежа       |
| contract_id | bigint      | NOT NULL                            | Идентификатор договора                 |
| placement_id| bigint      |                                     | Идентификатор размещения               |
| payment_date| date        | NOT NULL                            | Дата фактической оплаты                |
| amount      | decimal(15,2)| NOT NULL CHECK (amount > 0)        | Сумма платежа                          |
| period_start| date        | NOT NULL                            | Начало оплачиваемого периода           |
| period_end  | date        | NOT NULL                            | Конец оплачиваемого периода            |
| payment_type| text        |                                     | Тип платежа: card, cashless, cash      |
| status_code | varchar(20) | FK, NOT NULL DEFAULT 'pending'      | Ссылка на payment_statuses.code        |
| created_at  | timestamptz | NOT NULL DEFAULT now()              | Дата создания записи                   |
| updated_at  | timestamptz | NOT NULL DEFAULT now()              | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (contract_id) REFERENCES contracts(id)
- FOREIGN KEY (placement_id) REFERENCES placements(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.payment_statuses(code)
- CHECK (period_end > period_start)

### Таблица `entity_responsibilities`
| Колонка            | Тип         | Ограничения            | Комментарий                             |
|--------------------|-------------|------------------------|-----------------------------------------|
| id                 | bigint      | NOT NULL               | Уникальный идентификатор связи         |
| entity_type        | text        | NOT NULL               | Тип сущности                           |
| entity_id          | bigint      | NOT NULL               | ID сущности                            |
| person_id          | bigint      | NOT NULL               | Идентификатор ответственного лица      |
| responsibility_type| text        | NOT NULL               | Тип ответственности                    |
| start_date         | date        | NOT NULL               | Дата начала ответственности            |
| end_date          | date        |                        | Дата окончания ответственности         |
| is_primary        | boolean     | DEFAULT false          | Является ли основным ответственным     |
| notes             | text        |                        | Дополнительные примечания              |
| created_at        | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at        | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (person_id) REFERENCES dictionary.responsible_persons(id)
- UNIQUE (entity_type, entity_id, person_id, responsibility_type)

---

## Схема `fire`

### Таблица `buses`
| Колонка     | Тип         | Ограничения                           | Комментарий                             |
|-------------|-------------|---------------------------------------|-----------------------------------------|
| id          | bigint      | NOT NULL                              | Уникальный идентификатор шины          |
| name        | text        | NOT NULL UNIQUE                       | Наименование шины                      |
| description | text        |                                       | Описание шины                          |
| building_id | bigint      | NOT NULL                              | Ссылка на здание                       |
| status_code | varchar(20) | FK, NOT NULL                          | Ссылка на equipment_statuses.code      |
| last_check  | timestamptz |                                       | Время последней проверки               |
| created_at  | timestamptz | NOT NULL DEFAULT now()                | Дата создания записи                   |
| updated_at  | timestamptz | NOT NULL DEFAULT now()                | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (building_id) REFERENCES physical.buildings(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.equipment_statuses(code)

### Таблица `sensors`
| Колонка          | Тип         | Ограничения                           | Комментарий                             |
|------------------|-------------|---------------------------------------|-----------------------------------------|
| id               | bigint      | NOT NULL                              | Уникальный идентификатор датчика       |
| device_id        | text        | NOT NULL UNIQUE                       | Уникальный серийный номер устройства   |
| bus_id           | bigint      | FK, NOT NULL                          | Ссылка на шину                         |
| room_id          | bigint      |                                       | Ссылка на помещение                    |
| zone_id          | bigint      |                                       | Ссылка на зону                         |
| description      | text        |                                       | Описание датчика                       |
| type_id          | bigint      | FK, NOT NULL                          | Ссылка на sensor_types.id              |
| model            | text        |                                       | Модель датчика                         |
| installation_date| date        | NOT NULL                              | Дата установки                         |
| last_maintenance | date        |                                       | Дата последнего обслуживания           |
| status_code      | varchar(20) | FK, NOT NULL                          | Ссылка на equipment_statuses.code      |
| created_at       | timestamptz | NOT NULL DEFAULT now()                | Дата создания записи                   |
| updated_at       | timestamptz | NOT NULL DEFAULT now()                | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (bus_id) REFERENCES buses(id)
- FOREIGN KEY (type_id) REFERENCES dictionary.sensor_types(id)
- FOREIGN KEY (status_code) REFERENCES dictionary.equipment_statuses(code)

### Таблица `sensor_events`
| Колонка     | Тип         | Ограничения                           | Комментарий                             |
|-------------|-------------|---------------------------------------|-----------------------------------------|
| id          | bigint      | NOT NULL                              | Уникальный идентификатор события       |
| sensor_id   | bigint      | FK, NOT NULL                          | Ссылка на датчик                       |
| description | text        |                                       | Описание события                       |
| event_type  | text        | NOT NULL CHECK (event_type IN ('triggered', 'normal', 'battery_low', 'disconnected', 'test')) | Тип события |
| old_status  | varchar(20) |                                       | Предыдущий статус                      |
| new_status  | varchar(20) | NOT NULL                              | Новый статус                           |
| value       | numeric(10,2)|                                      | Измеренное значение                    |
| resolved_at | timestamptz |                                       | Время разрешения события               |
| resolved_by | bigint      |                                       | Кто разрешил                           |
| created_at  | timestamptz | NOT NULL DEFAULT now()                | Дата создания записи                   |
| updated_at  | timestamptz | NOT NULL DEFAULT now()                | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- FOREIGN KEY (sensor_id) REFERENCES sensors(id)

### Таблица `emergency_scenarios`
| Колонка   | Тип         | Ограничения                           | Комментарий                             |
|-----------|-------------|---------------------------------------|-----------------------------------------|
| id        | bigint      | NOT NULL                              | Уникальный идентификатор сценария      |
| name      | text        | NOT NULL                              | Название сценария                      |
| description| text       |                                       | Описание сценария                      |
| conditions| jsonb       | NOT NULL                              | Условия срабатывания в JSON            |
| actions   | jsonb       | NOT NULL                              | Действия при срабатывании в JSON       |
| priority  | integer     | CHECK (priority >= 1 AND priority <= 10) | Приоритет (1 - наивысший)         |
| is_active | boolean     | DEFAULT true                          | Активен ли сценарий                    |
| created_at| timestamptz | NOT NULL DEFAULT now()                | Дата создания записи                   |
| updated_at| timestamptz | NOT NULL DEFAULT now()                | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

---

## Схема `audit`

### Таблица `change_log`
| Колонка       | Тип         | Ограничения            | Комментарий                             |
|---------------|-------------|------------------------|-----------------------------------------|
| id            | bigint      | NOT NULL               | Уникальный идентификатор               |
| table_schema  | varchar(50) | NOT NULL               | Схема таблицы                          |
| table_name    | varchar(100)| NOT NULL               | Имя таблицы                            |
| record_id     | bigint      | NOT NULL               | ID записи                              |
| operation     | varchar(10) | NOT NULL               | Тип: INSERT, UPDATE, DELETE            |
| old_data      | jsonb       |                        | Данные до изменения                    |
| new_data      | jsonb       |                        | Данные после изменения                 |
| is_deleted    | boolean     | DEFAULT false          | Флаг удаления записи                   |
| changed_by    | varchar(100)|                        | Кто изменил                            |
| changed_at    | timestamptz | NOT NULL DEFAULT now() | Когда изменил                          |
| ip_address    | inet        |                        | IP-адрес                               |
| transaction_id| uuid        |                        | ID транзакции для группировки         |
| created_at    | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at    | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- INDEX idx_change_log_table (table_schema, table_name, changed_at)
- INDEX idx_change_log_operation (operation, is_deleted)
- INDEX idx_change_log_transaction (transaction_id)

### Таблица `deleted_records_archive`
| Колонка               | Тип         | Ограничения            | Комментарий                             |
|-----------------------|-------------|------------------------|-----------------------------------------|
| id                    | bigint      | NOT NULL               | Уникальный ID архива                   |
| original_table_schema | varchar(50) | NOT NULL               | Исходная схема                         |
| original_table_name   | varchar(100)| NOT NULL               | Исходная таблица                       |
| original_record_id    | bigint      | NOT NULL               | Исходный ID записи                     |
| record_data           | jsonb       | NOT NULL               | Полная копия записи                    |
| deleted_by            | varchar(100)|                        | Кто удалил                             |
| deleted_at            | timestamptz | NOT NULL DEFAULT now() | Когда удалил                           |
| deletion_reason       | text        |                        | Причина удаления                       |
| can_be_restored       | boolean     | DEFAULT true           | Можно ли восстановить                  |
| restored_at           | timestamptz |                        | Когда восстановили                     |
| restored_by           | varchar(100)|                        | Кто восстановил                        |
| created_at            | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at            | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)
- INDEX idx_deleted_archive_lookup (original_table_schema, original_table_name, original_record_id)
- INDEX idx_deleted_archive_date (deleted_at)
- INDEX idx_deleted_archive_restorable (can_be_restored) WHERE can_be_restored = true

### Таблица `system_log`
| Колонка   | Тип         | Ограничения            | Комментарий                             |
|-----------|-------------|------------------------|-----------------------------------------|
| id        | bigint      | NOT NULL               | Уникальный идентификатор               |
| log_level | text        | NOT NULL               | Уровень: DEBUG, INFO, WARN, ERROR, FATAL |
| module    | text        |                        | Модуль системы                         |
| message   | text        | NOT NULL               | Текст сообщения                        |
| details   | jsonb       |                        | Дополнительные данные в JSON           |
| user_id   | text        |                        | Идентификатор пользователя             |
| ip_address| inet        |                        | IP-адрес источника                     |
| created_at| timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at| timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

### Таблица `user_action_log`
| Колонка     | Тип         | Ограничения            | Комментарий                             |
|-------------|-------------|------------------------|-----------------------------------------|
| id          | bigint      | NOT NULL               | Уникальный идентификатор               |
| user_id     | bigint      |                        | ID пользователя                         |
| action      | varchar(100)| NOT NULL               | Действие (login, search, export)       |
| entity_type | varchar(50) |                        | Тип сущности                           |
| entity_id   | bigint      |                        | ID сущности                            |
| details     | jsonb       |                        | Детали действия в JSON                 |
| ip_address  | inet        |                        | IP-адрес пользователя                  |
| user_agent  | text        |                        | Информация о клиентском приложении     |
| performed_at| timestamptz |                        | Время выполнения действия              |
| created_at  | timestamptz | NOT NULL DEFAULT now() | Дата создания записи                   |
| updated_at  | timestamptz | NOT NULL DEFAULT now() | Дата обновления записи                 |

**Ключи и ограничения:**
- PRIMARY KEY (id)

---

## Основные связи между таблицами:

1. `security.users` ← `dictionary.responsible_persons` ← `dictionary.counterparties`
2. `security.roles` ← `security.user_roles` → `security.users`
3. `dictionary.counterparties` → `dictionary.counterparty_statuses`
4. `physical.complexes` → `physical.buildings` → `physical.floors` → `physical.rooms` → `physical.zones`
5. `physical.rooms` → `dictionary.room_statuses`
6. `physical.buildings` → `dictionary.building_statuses`
7. `business.contracts` → `dictionary.contract_statuses`
8. `business.placements` → `dictionary.placement_statuses`
9. `business.payments` → `dictionary.payment_statuses`
10. `fire.sensors` → `dictionary.equipment_statuses`
11. Все таблицы → `audit.change_log` → `audit.deleted_records_archive`
```
