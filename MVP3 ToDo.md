ты сеньор фуллстек разработчик, который обучает "зеленого" джуна программированию на python.
У нас есть уже готовый и корректно работающий прототип клиентского приложения.
Файловая структура клиента:
client/src/
├── __init__.py
│   # Маркер пакета Python, может быть пустым.
│
├── main.py
│   # ТОЧКА ВХОДА: инициализация логгера, настройка окружения Qt,
│   # создание и запуск главного окна.
│
├── core/
│   # Ядро приложения: независимые сервисы и инфраструктура.
│   ├── __init__.py
│   ├── api_client.py
│   │   # КЛИЕНТ API: все HTTP-запросы к бекенду (get_complexes, get_buildings и т.д.).
│   │   # Содержит логику формирования URL, обработки ошибок.
│   └── cache.py
│       # СИСТЕМА КЭШИРОВАНИЯ: in-memory хранилище загруженных данных
│       # с поддержкой инвалидации по узлам и веткам.
│
├── models/
│   # МОДЕЛИ ДАННЫХ: дата-классы, соответствующие ответам API.
│   ├── __init__.py
│   ├── complex.py
│   ├── building.py
│   ├── floor.py
│   └── room.py
│
├── utils/
│   # УТИЛИТЫ: вспомогательные модули.
│   ├── __init__.py
│   └── logger.py
│       # ПРОФЕССИОНАЛЬНЫЙ ЛОГГЕР: поддержка уровней, категорий (api, cache, data),
│       # цветного вывода и форматирования.
│
└── ui/
    # ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС: все виджеты и окна.
    ├── __init__.py
    │   # Экспортирует главные классы для удобного импорта (MainWindow, TreeView, DetailsPanel).
    │
    ├── main_window/
    │   # ГЛАВНОЕ ОКНО приложения, разбитое на компоненты.
    │   ├── __init__.py
    │   ├── main_window.py
    │   │   # СБОРКА: создает экземпляры компонентов, контроллеров и связывает их сигналами.
    │   ├── shortcuts.py
    │   │   # ГОРЯЧИЕ КЛАВИШИ: определяет сочетания (F5, Ctrl+F5 и т.д.).
    │   ├── components/
    │   │   # ВИЗУАЛЬНЫЕ КОМПОНЕНТЫ окна.
    │   │   ├── __init__.py
    │   │   ├── central_widget.py   # Центральный виджет с QSplitter.
    │   │   ├── toolbar.py          # Панель инструментов с кнопкой "Обновить".
    │   │   └── status_bar.py       # Строка статуса с индикатором соединения.
    │   └── controllers/
    │       # КОНТРОЛЛЕРЫ: логика, не привязанная к конкретному view.
    │       ├── __init__.py
    │       ├── refresh_controller.py    # Обработка нажатий F5, Ctrl+F5.
    │       ├── data_controller.py       # Реакция на сигналы загрузки данных.
    │       └── connection_controller.py # Периодическая проверка соединения с сервером.
    │
    ├── tree/
    # ПАКЕТ КОМПОНЕНТОВ ДЕРЕВА (левая панель).
    │   ├── __init__.py
    │   ├── tree_view.py
    │   │   # ОСНОВНОЙ КЛАСС: собирает все миксины для работы дерева.
    │   ├── base_tree.py
    │   │   # БАЗОВЫЙ КЛАСС: инициализация UI, заголовок, индикатор загрузки.
    │   │   # МИКСИН: логика загрузки данных (комплексов, детей, деталей).
    │   ├── tree_updater.py
    │   │   # МИКСИН: логика обновления данных (refresh_current, refresh_visible, full_reset).
    │   ├── tree_selection.py
    │   │   # МИКСИН: работа с выделением узлов и контекстом иерархии.
    │   └── tree_menu.py
    │       # МИКСИН: контекстное меню для узлов.
	│	
	│
    ├── tree_model/
    # МОДЕЛЬ ДАННЫХ ДЕРЕВА (QAbstractItemModel) и TreeNode.
    │   ├── __init__.py
    │   ├── node_types.py
    │   │   # Модуль с определением типов узлов дерева.
    │   ├──tree_model_base.py
    │   │   # Базовый абстрактный класс для модели дерева.
    │   ├──tree_model_data.py
    │   │   # Миксин для управления данными модели дерева.
    │   ├──tree_model_index.py
    │   │   # Миксин для работы с индексацией узлов дерева.
    │   ├──tree_model.py
	│   │   # Конкретная реализация модели дерева.
    │   ├──tree_node.py
	│   │   # Модуль с классом TreeNode, представляющим узел дерева.
    │
    ├── details/
    # ПАКЕТ КОМПОНЕНТОВ ПАНЕЛИ ДЕТАЛЕЙ (правая панель).
    │   ├── __init__.py
    │   ├── details_panel.py
    │   │   # ОСНОВНОЙ КЛАСС: собирает все компоненты панели.
    │   ├── base_panel.py
    │   │   # БАЗОВЫЙ КЛАСС: создает layout, шапку, заглушку, сетку и вкладки.
    │   ├── header_widget.py
    │   │   # ШАПКА: иконка, заголовок, статус, строка иерархии.
    │   ├── info_grid.py
    │   │   # СЕТКА ПОЛЕЙ: динамическое отображение пар "Лейбл: Значение".
    │   ├── placeholder.py
    │   │   # ЗАГЛУШКА: отображается, когда ничего не выбрано.
    │   ├── tabs.py
    │   │   # ВКЛАДКИ: Физика, Юрики, Пожарка (пока заглушки).
    │   ├── field_manager.py
    │   │   # МЕНЕДЖЕР ПОЛЕЙ: форматирование данных для отображения.
    │   └── display_handlers.py
    │       # ОБРАБОТЧИКИ ОТОБРАЖЕНИЯ: логика заполнения панели для каждого типа объекта.
    │
    └── refresh_menu.py
        # ВСПЛЫВАЮЩЕЕ МЕНЮ для кнопки "Обновить" на тулбаре.
		
Теперь все файлы по списку:

# client/src/core/__init__.py
"""
Ядро клиентского приложения.
Предоставляет основные сервисы для работы с данными:
- API клиент для взаимодействия с бекендом
- Система кэширования данных
"""
from src.core.api_client import ApiClient
from src.core.cache import DataCache

__all__ = [
    "ApiClient",
    "DataCache"
]

# client/src/core/api_client.py
"""
Клиент для работы с backend API.
Выполняет HTTP запросы к FastAPI бекенду и преобразует ответы в модели данных.
Поддерживает все уровни иерархии:
- Комплексы
- Корпуса
- Этажи
- Помещения
- Детальная информация для каждого типа
"""
import os
import re
import contextlib
import io
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ApiClient:
    """
    Клиент для взаимодействия с backend API.
    
    Получает URL backend из переменной окружения API_URL
    или использует localhost по умолчанию (для разработки).
    
    Принципы:
    1. Все методы возвращают готовые модели данных
    2. Ошибки API пробрасываются как исключения с понятными сообщениями
    3. Единый point-of-truth для всех API вызовов
    4. Детальное логирование для отладки
    """
    
    # ===== Константы =====
    
    # Базовые эндпоинты API
    ENDPOINT_COMPLEXES = "/physical/"
    """Эндпоинт для получения списка комплексов"""
    
    ENDPOINT_BUILDINGS = "/physical/complexes/{}/buildings"
    """Эндпоинт для получения корпусов комплекса"""
    
    ENDPOINT_FLOORS = "/physical/buildings/{}/floors"
    """Эндпоинт для получения этажей корпуса"""
    
    ENDPOINT_ROOMS = "/physical/floors/{}/rooms"
    """Эндпоинт для получения помещений этажа"""
    
    ENDPOINT_HEALTH = "/health"
    """Эндпоинт для проверки здоровья сервера"""
    
    ENDPOINT_ROOT = "/"
    """Корневой эндпоинт"""
    
    # Детальные эндпоинты
    ENDPOINT_COMPLEX_DETAIL = "/physical/complexes/{}"
    """Эндпоинт для получения деталей комплекса"""
    
    ENDPOINT_BUILDING_DETAIL = "/physical/buildings/{}"
    """Эндпоинт для получения деталей корпуса"""
    
    ENDPOINT_FLOOR_DETAIL = "/physical/floors/{}"
    """Эндпоинт для получения деталей этажа"""
    
    ENDPOINT_ROOM_DETAIL = "/physical/rooms/{}"
    """Эндпоинт для получения деталей помещения"""
    
    # Настройки по умолчанию
    DEFAULT_TIMEOUT = 10
    """Таймаут запроса по умолчанию в секундах"""
    
    DEFAULT_USER_AGENT = "Markoff-Client/0.2.0"
    """User-Agent по умолчанию"""
    
    def __init__(self) -> None:
        """Инициализирует клиент API."""
        # Получаем URL из окружения (устанавливается в docker-compose)
        self._base_url = os.getenv("API_URL", "http://localhost:8000")
        # Убираем trailing slash если есть
        self._base_url = self._base_url.rstrip('/')
        
        # Создаём сессию для переиспользования соединений
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
            'User-Agent': self.DEFAULT_USER_AGENT,
            'Content-Type': 'application/json'
        })
        
        log.success(f"API Client инициализирован с базовым URL: {self._base_url}")
    
    # ===== Приватные методы =====
    
    def _build_url(self, path: str) -> str:
        """
        Формирует полный URL из относительного пути.
        
        Args:
            path: Относительный путь или полный URL
            
        Returns:
            str: Полный URL для запроса
        """
        if path.startswith('http'):
            return path
        return urljoin(self._base_url + '/', path.lstrip('/'))
    
    def _log_response_summary(self, data: Any) -> None:
        """
        Логирует краткую информацию о полученном ответе.
        
        Args:
            data: Распарсенные данные ответа
        """
        if isinstance(data, list):
            log.api(f"Ответ получен: {len(data)} записей")
        elif isinstance(data, dict):
            log.api(f"Ответ получен: словарь с {len(data)} ключами")
        else:
            log.api(f"Ответ получен: {type(data).__name__}")
    
    def _handle_http_error(self, e: requests.exceptions.HTTPError, url: str) -> None:
        """
        Обрабатывает HTTP ошибки и формирует понятное сообщение.
        
        Args:
            e: HTTP ошибка
            url: URL запроса
            
        Raises:
            Exception: С понятным описанием ошибки
        """
        status_code = e.response.status_code if hasattr(e, 'response') else 0
        log.error(f"HTTP ошибка {status_code} при запросе к {url}")
        
        if status_code == 404:
            raise Exception("Запрошенный ресурс не найден (404)")
        elif status_code == 422:
            # Ошибка валидации - пробуем получить детали
            try:
                details = e.response.json()
                raise Exception(f"Ошибка валидации: {details}")
            except:
                raise Exception("Ошибка валидации данных (422)")
        elif status_code == 500:
            raise Exception("Внутренняя ошибка сервера (500)")
        else:
            raise Exception(f"Ошибка сервера: HTTP {status_code}")
    
    def _make_request(self, method: str, path: str, **kwargs) -> Any:
        """
        Внутренний метод для выполнения HTTP запросов.
        
        Args:
            method: HTTP метод (GET, POST, etc.)
            path: Путь относительно base_url
            **kwargs: Дополнительные параметры для requests
            
        Returns:
            JSON ответ от сервера
            
        Raises:
            Exception: С описанием ошибки
        """
        # Формируем полный URL
        url = self._build_url(path)
        
        # Устанавливаем таймаут по умолчанию, если не указан
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.DEFAULT_TIMEOUT
        
        try:
            log.api(f"{method} {url}")
            
            # Делаем запрос
            response = self._session.request(method, url, **kwargs)
            
            # Логируем статус
            log.api(f"Статус: {response.status_code}")
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Проверяем, есть ли содержимое
            if response.status_code == 204 or not response.content:
                log.api("Ответ: пустой (204 No Content)")
                return None
            
            # Парсим JSON
            data = response.json()
            
            # Логируем количество записей
            self._log_response_summary(data)
            
            return data
            
        except requests.exceptions.ConnectionError as error:
            log.error(f"Ошибка подключения к {url}: {error}")
            raise Exception(
                f"Не удалось подключиться к серверу по адресу {self._base_url}. "
                "Проверьте, запущен ли backend."
            )
            
        except requests.exceptions.Timeout:
            log.error(f"Таймаут при запросе к {url}")
            raise Exception("Сервер не отвечает. Превышено время ожидания.")
            
        except requests.exceptions.HTTPError as error:
            self._handle_http_error(error, url)
                
        except requests.exceptions.RequestException as error:
            log.error(f"Ошибка запроса: {error}")
            raise Exception(f"Ошибка при выполнении запроса: {error}")
            
        except ValueError as error:
            log.error(f"Ошибка парсинга JSON: {error}")
            raise Exception("Сервер вернул некорректный JSON")
            
        except Exception as error:
            log.error(f"Неизвестная ошибка: {error}")
            raise Exception(f"Непредвиденная ошибка: {error}")
    
    # ===== Методы для комплексов =====
    
    def get_complexes(self) -> List[Complex]:
        """
        Получает список всех комплексов.
        
        Returns:
            List[Complex]: Список комплексов с полными данными
            
        Raises:
            Exception: При ошибке запроса
        """
        try:
            data = self._make_request('GET', self.ENDPOINT_COMPLEXES)
            
            if not data:
                log.warning("Сервер вернул пустой список комплексов")
                return []
            
            complexes = [Complex.from_dict(item) for item in data]
            
            log.data(f"Загружено комплексов: {len(complexes)}")
            for c in complexes:
                log.debug(f"  - {c.name} (корпусов: {c.buildings_count})")
                if c.address:
                    log.debug(f"    адрес: {c.address[:50]}...")
            
            return complexes
            
        except Exception as error:
            log.error(f"Ошибка загрузки комплексов: {error}")
            raise
    
    def get_complex_detail(self, complex_id: int) -> Optional[Complex]:
        """
        Получает детальную информацию о комплексе.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            Optional[Complex]: Объект комплекса с полными данными или None
        """
        try:
            endpoint = self.ENDPOINT_COMPLEX_DETAIL.format(complex_id)
            log.info(f"Загрузка деталей комплекса #{complex_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                log.warning(f"Сервер вернул пустые данные для комплекса {complex_id}")
                return None
            
            complex_obj = Complex.from_dict(data)
            
            log.success(f"Детали комплекса #{complex_id} загружены")
            if complex_obj.address:
                log.debug(f"  адрес: {complex_obj.address[:50]}...")
            if complex_obj.description:
                log.debug(f"  описание: {complex_obj.description[:50]}...")
            
            return complex_obj
            
        except Exception as error:
            log.error(f"Ошибка загрузки деталей комплекса #{complex_id}: {error}")
            return None
    
    # ===== Методы для корпусов =====
    
    def get_buildings(self, complex_id: int) -> List[Building]:
        """
        Получает список корпусов для конкретного комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            List[Building]: Список корпусов с полными данными
        """
        try:
            endpoint = self.ENDPOINT_BUILDINGS.format(complex_id)
            log.info(f"Загрузка корпусов для комплекса #{complex_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                log.info(f"Нет корпусов для комплекса {complex_id}")
                return []
            
            buildings = [Building.from_dict(item) for item in data]
            
            log.data(f"Загружено корпусов: {len(buildings)}")
            for b in buildings:
                log.debug(f"  - {b.name} (этажей: {b.floors_count})")
                if b.address:
                    log.debug(f"    адрес: {b.address[:50]}...")
            
            return buildings
            
        except Exception as error:
            log.error(f"Ошибка загрузки корпусов для комплекса {complex_id}: {error}")
            raise
    
    def get_building_detail(self, building_id: int) -> Optional[Building]:
        """
        Получает детальную информацию о корпусе.
        
        Args:
            building_id: ID корпуса
            
        Returns:
            Optional[Building]: Объект корпуса с полными данными или None
        """
        try:
            endpoint = self.ENDPOINT_BUILDING_DETAIL.format(building_id)
            log.info(f"Загрузка деталей корпуса #{building_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                log.warning(f"Сервер вернул пустые данные для корпуса {building_id}")
                return None
            
            building = Building.from_dict(data)
            log.success(f"Детали корпуса #{building_id} загружены")
            
            return building
            
        except Exception as error:
            log.error(f"Ошибка загрузки деталей корпуса #{building_id}: {error}")
            return None
    
    # ===== Методы для этажей =====
    
    def get_floors(self, building_id: int) -> List[Floor]:
        """
        Получает список этажей для конкретного корпуса.
        
        Args:
            building_id: ID корпуса
            
        Returns:
            List[Floor]: Список этажей с полными данными
        """
        try:
            endpoint = self.ENDPOINT_FLOORS.format(building_id)
            log.info(f"Загрузка этажей для корпуса #{building_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                log.info(f"Нет этажей для корпуса {building_id}")
                return []
            
            floors = [Floor.from_dict(item) for item in data]
            
            # Сортировка по номеру этажа
            floors.sort(key=lambda x: x.number)
            
            log.data(f"Загружено этажей: {len(floors)}")
            for f in floors:
                log.debug(f"  - Этаж {f.number} (помещений: {f.rooms_count})")
                if f.description:
                    log.debug(f"    описание: {f.description[:50]}...")
            
            return floors
            
        except Exception as error:
            log.error(f"Ошибка загрузки этажей для корпуса {building_id}: {error}")
            raise
    
    def get_floor_detail(self, floor_id: int) -> Optional[Floor]:
        """
        Получает детальную информацию об этаже.
        
        Args:
            floor_id: ID этажа
            
        Returns:
            Optional[Floor]: Объект этажа с полными данными или None
        """
        try:
            endpoint = self.ENDPOINT_FLOOR_DETAIL.format(floor_id)
            log.info(f"Загрузка деталей этажа #{floor_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                log.warning(f"Сервер вернул пустые данные для этажа {floor_id}")
                return None
            
            floor = Floor.from_dict(data)
            log.success(f"Детали этажа #{floor_id} загружены")
            
            return floor
            
        except Exception as error:
            log.error(f"Ошибка загрузки деталей этажа #{floor_id}: {error}")
            return None
    
    # ===== Методы для помещений =====
    
    def get_rooms(self, floor_id: int) -> List[Room]:
        """
        Получает список помещений для конкретного этажа.
        
        Args:
            floor_id: ID этажа
            
        Returns:
            List[Room]: Список помещений с полными данными
        """
        try:
            endpoint = self.ENDPOINT_ROOMS.format(floor_id)
            log.info(f"Загрузка помещений для этажа #{floor_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                log.info(f"Нет помещений для этажа {floor_id}")
                return []
            
            rooms = [Room.from_dict(item) for item in data]
            
            # Сортировка по номеру помещения
            rooms.sort(key=lambda x: self._natural_sort_key(x.number))
            
            log.data(f"Загружено помещений: {len(rooms)}")
            for r in rooms[:5]:
                status = f" [{r.status_code}]" if r.status_code else ""
                log.debug(f"  - {r.number}{status}")
                if r.description:
                    log.debug(f"    описание: {r.description[:50]}...")
            if len(rooms) > 5:
                log.debug(f"  - ... и ещё {len(rooms) - 5}")
            
            return rooms
            
        except Exception as error:
            log.error(f"Ошибка загрузки помещений для этажа {floor_id}: {error}")
            raise
    
    def get_room_detail(self, room_id: int) -> Optional[Room]:
        """
        Получает детальную информацию о помещении.
        
        Args:
            room_id: ID помещения
            
        Returns:
            Optional[Room]: Объект помещения с полными данными или None
        """
        try:
            endpoint = self.ENDPOINT_ROOM_DETAIL.format(room_id)
            log.info(f"Загрузка деталей помещения #{room_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                log.warning(f"Сервер вернул пустые данные для помещения {room_id}")
                return None
            
            room = Room.from_dict(data)
            log.success(f"Детали помещения #{room_id} загружены")
            
            return room
            
        except Exception as error:
            log.error(f"Ошибка загрузки деталей помещения #{room_id}: {error}")
            return None
    
    # ===== Вспомогательные методы =====
    
    def _natural_sort_key(self, text: str) -> List[Union[int, str]]:
        """
        Создаёт ключ для естественной сортировки строк с числами.
        
        Например: "101", "101А", "102", "Б12" будут отсортированы правильно.
        
        Args:
            text: Строка для сортировки
            
        Returns:
            List[Union[int, str]]: Ключ для сравнения
        """
        return [int(c) if c.isdigit() else c.lower() 
                for c in re.split('([0-9]+)', text)]
    
    def check_connection(self, silent: bool = False) -> bool:
        """
        Проверяет соединение с сервером.
        
        Args:
            silent: Если True - не выводить логи в консоль
            
        Returns:
            bool: True если сервер доступен
        """
        try:
            if silent:
                # Временно отключаем вывод логов
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    self._make_request('GET', self.ENDPOINT_HEALTH, timeout=3)
            else:
                self._make_request('GET', self.ENDPOINT_HEALTH, timeout=3)
            
            log.debug("Соединение с сервером установлено")
            return True
            
        except Exception as error:
            log.debug(f"Сервер недоступен: {error}")
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Получает информацию о сервере.
        
        Returns:
            Dict[str, Any]: Информация о версии и статусе
        """
        try:
            data = self._make_request('GET', self.ENDPOINT_ROOT)
            return data
        except Exception as error:
            log.error(f"Не удалось получить информацию о сервере: {error}")
            return {}
    
    # ===== Методы для отладки =====
    
    def print_endpoints(self) -> None:
        """Выводит все доступные эндпоинты для отладки."""
        log.info("\n=== Доступные эндпоинты ===")
        log.info(f"Комплексы:   {self._base_url}{self.ENDPOINT_COMPLEXES}")
        log.info(f"Корпуса:     {self._base_url}{self.ENDPOINT_BUILDINGS.format('<complex_id>')}")
        log.info(f"Этажи:       {self._base_url}{self.ENDPOINT_FLOORS.format('<building_id>')}")
        log.info(f"Помещения:   {self._base_url}{self.ENDPOINT_ROOMS.format('<floor_id>')}")
        log.info(f"Health:      {self._base_url}{self.ENDPOINT_HEALTH}")
        log.info(f"Root:        {self._base_url}{self.ENDPOINT_ROOT}")
        log.info("=" * 30)

# client/src/core/cache.py
"""
Система кэширования данных на клиенте.
Хранит загруженные данные в памяти и предоставляет методы для доступа к ним.
Поддерживает инвалидацию отдельных узлов и целых веток дерева.
"""
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
import threading

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class DataCache:
    """
    Кэш для хранения загруженных данных.
    
    Принцип работы:
    1. Данные хранятся в словаре _data с ключами специального формата
    2. Ключ формируется по шаблону: "тип:идентификатор:суффикс"
    3. Поддерживается инвалидация (удаление) отдельных записей и целых веток
    
    Форматы ключей:
    - "complex:{id}" - данные конкретного комплекса
    - "complex:{id}:buildings" - список корпусов комплекса
    - "building:{id}:floors" - список этажей корпуса
    - "floor:{id}:rooms" - список помещений этажа
    
    Также хранит метаданные о времени загрузки и раскрытых узлах.
    """
    
    # ===== Константы типов узлов =====
    TYPE_COMPLEX = "complex"
    """Тип узла: комплекс"""
    
    TYPE_BUILDING = "building"
    """Тип узла: корпус"""
    
    TYPE_FLOOR = "floor"
    """Тип узла: этаж"""
    
    TYPE_ROOM = "room"
    """Тип узла: помещение"""
    
    # ===== Суффиксы для списков дочерних элементов =====
    SUFFIX_BUILDINGS = "buildings"
    """Суффикс для списка корпусов"""
    
    SUFFIX_FLOORS = "floors"
    """Суффикс для списка этажей"""
    
    SUFFIX_ROOMS = "rooms"
    """Суффикс для списка помещений"""
    
    def __init__(self) -> None:
        """Инициализирует пустой кэш."""
        # Основное хранилище данных
        self._data: Dict[str, Any] = {}
        
        # Метаданные: время загрузки каждого ключа
        self._timestamps: Dict[str, datetime] = {}
        
        # Множество раскрытых узлов (для быстрого доступа при обновлении видимых)
        self._expanded_nodes: Set[str] = set()
        
        # Блокировка для потокобезопасности
        self._lock = threading.RLock()
        
        # Счётчики для статистики
        self._hits: int = 0
        """Количество успешных обращений к кэшу"""
        
        self._misses: int = 0
        """Количество промахов"""
        
        self._invalidations: int = 0
        """Количество инвалидаций"""
        
        log.success("Cache: инициализирован")
    
    # ===== Приватные методы работы с ключами =====
    
    def _make_key(self, type_: str, id_: int, suffix: Optional[str] = None) -> str:
        """
        Создаёт ключ для доступа к данным в кэше.
        
        Args:
            type_: Тип узла (complex, building, floor, room)
            id_: Идентификатор узла
            suffix: Необязательный суффикс (например, "buildings")
            
        Returns:
            str: Ключ в формате "type:id:suffix" или "type:id"
        """
        if suffix:
            return f"{type_}:{id_}:{suffix}"
        return f"{type_}:{id_}"
    
    def _parse_key(self, key: str) -> Tuple[str, int, Optional[str]]:
        """
        Разбирает ключ на составляющие.
        
        Args:
            key: Ключ в формате "type:id:suffix" или "type:id"
            
        Returns:
            Tuple[str, int, Optional[str]]: (type, id, suffix)
        """
        parts = key.split(':')
        if len(parts) == 2:
            return parts[0], int(parts[1]), None
        else:
            return parts[0], int(parts[1]), parts[2]
    
    # ===== Основные методы доступа к данным =====
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получает данные из кэша по ключу.
        
        Args:
            key: Ключ данных
            
        Returns:
            Any: Данные или None, если ключ не найден
        """
        with self._lock:
            data = self._data.get(key)
            if data is not None:
                self._hits += 1
                log.cache(f"HIT: {key}")
            else:
                self._misses += 1
                log.cache(f"MISS: {key}")
            return data
    
    def set(self, key: str, value: Any) -> None:
        """
        Сохраняет данные в кэш.
        
        Args:
            key: Ключ данных
            value: Данные для сохранения
        """
        with self._lock:
            self._data[key] = value
            self._timestamps[key] = datetime.now()
            log.cache(f"SET: {key}")
    
    def has(self, key: str) -> bool:
        """
        Проверяет наличие данных в кэше.
        
        Args:
            key: Ключ данных
            
        Returns:
            bool: True если данные есть
        """
        with self._lock:
            return key in self._data
    
    def remove(self, key: str) -> bool:
        """
        Удаляет конкретную запись из кэша.
        
        Args:
            key: Ключ данных
            
        Returns:
            bool: True если запись была удалена
        """
        with self._lock:
            if key in self._data:
                del self._data[key]
                if key in self._timestamps:
                    del self._timestamps[key]
                self._invalidations += 1
                log.cache(f"REMOVE: {key}")
                return True
            return False
    
    # ===== Методы для работы с иерархическими данными =====
    
    def get_complex(self, complex_id: int) -> Optional[Any]:
        """
        Получает данные комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            Optional[Any]: Данные комплекса или None
        """
        return self.get(self._make_key(self.TYPE_COMPLEX, complex_id))
    
    def set_complex(self, complex_id: int, data: Any) -> None:
        """
        Сохраняет данные комплекса.
        
        Args:
            complex_id: ID комплекса
            data: Данные для сохранения
        """
        self.set(self._make_key(self.TYPE_COMPLEX, complex_id), data)
    
    def get_buildings(self, complex_id: int) -> Optional[Any]:
        """
        Получает список корпусов комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            Optional[Any]: Список корпусов или None
        """
        return self.get(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS))
    
    def set_buildings(self, complex_id: int, buildings: Any) -> None:
        """
        Сохраняет список корпусов комплекса.
        
        Args:
            complex_id: ID комплекса
            buildings: Список корпусов для сохранения
        """
        self.set(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS), buildings)
    
    def get_floors(self, building_id: int) -> Optional[Any]:
        """
        Получает список этажей корпуса.
        
        Args:
            building_id: ID корпуса
            
        Returns:
            Optional[Any]: Список этажей или None
        """
        return self.get(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS))
    
    def set_floors(self, building_id: int, floors: Any) -> None:
        """
        Сохраняет список этажей корпуса.
        
        Args:
            building_id: ID корпуса
            floors: Список этажей для сохранения
        """
        self.set(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS), floors)
    
    def get_rooms(self, floor_id: int) -> Optional[Any]:
        """
        Получает список помещений этажа.
        
        Args:
            floor_id: ID этажа
            
        Returns:
            Optional[Any]: Список помещений или None
        """
        return self.get(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS))
    
    def set_rooms(self, floor_id: int, rooms: Any) -> None:
        """
        Сохраняет список помещений этажа.
        
        Args:
            floor_id: ID этажа
            rooms: Список помещений для сохранения
        """
        self.set(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS), rooms)
    
    # ===== Методы инвалидации =====
    
    def invalidate_node(self, node_type: str, node_id: int) -> None:
        """
        Инвалидирует (удаляет) данные конкретного узла.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self.remove(key)
            log.info(f"Инвалидирован узел {node_type}:{node_id}")
    
    def invalidate_branch(self, node_type: str, node_id: int) -> None:
        """
        Инвалидирует ветку целиком - узел и всех его потомков.
        
        Для каждого типа узла удаляет:
        - complex: сам комплекс + его корпуса + этажи корпусов + помещения этажей
        - building: сам корпус + его этажи + помещения этажей
        - floor: сам этаж + его помещения
        - room: только само помещение (нет детей)
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            keys_to_remove = self._collect_branch_keys(node_type, node_id)
            
            # Удаляем все найденные ключи
            unique_keys = set(keys_to_remove)
            for key in unique_keys:
                self.remove(key)
            
            log.info(f"Инвалидирована ветка {node_type}:{node_id} (удалено {len(unique_keys)} записей)")
    
    def _collect_branch_keys(self, node_type: str, node_id: int) -> List[str]:
        """
        Собирает все ключи, относящиеся к ветке узла.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            List[str]: Список ключей для удаления
        """
        keys_to_remove = []
        
        if node_type == self.TYPE_COMPLEX:
            keys_to_remove.extend(self._collect_complex_branch(node_id))
        elif node_type == self.TYPE_BUILDING:
            keys_to_remove.extend(self._collect_building_branch(node_id))
        elif node_type == self.TYPE_FLOOR:
            keys_to_remove.extend(self._collect_floor_branch(node_id))
        elif node_type == self.TYPE_ROOM:
            keys_to_remove.append(self._make_key(node_type, node_id))
        
        return keys_to_remove
    
    def _collect_complex_branch(self, complex_id: int) -> List[str]:
        """
        Собирает ключи для ветки комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            List[str]: Список ключей
        """
        keys = []
        
        # Удаляем комплекс
        keys.append(self._make_key(self.TYPE_COMPLEX, complex_id))
        keys.append(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS))
        
        # Ищем все корпуса этого комплекса в кэше
        prefix = f"{self.TYPE_BUILDING}:"
        for key in list(self._data.keys()):
            if key.startswith(prefix):
                try:
                    _, b_id, suffix = self._parse_key(key)
                    if suffix is None or suffix == self.SUFFIX_FLOORS:
                        keys.append(key)
                        # Для каждого корпуса удаляем его этажи
                        floors_key = self._make_key(self.TYPE_BUILDING, b_id, self.SUFFIX_FLOORS)
                        if floors_key in self._data:
                            keys.append(floors_key)
                except (ValueError, IndexError):
                    continue
        
        return keys
    
    def _collect_building_branch(self, building_id: int) -> List[str]:
        """
        Собирает ключи для ветки корпуса.
        
        Args:
            building_id: ID корпуса
            
        Returns:
            List[str]: Список ключей
        """
        keys = []
        
        # Удаляем корпус
        keys.append(self._make_key(self.TYPE_BUILDING, building_id))
        keys.append(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS))
        
        # Ищем все этажи этого корпуса в кэше
        prefix = f"{self.TYPE_FLOOR}:"
        for key in list(self._data.keys()):
            if key.startswith(prefix):
                try:
                    _, f_id, suffix = self._parse_key(key)
                    if suffix is None or suffix == self.SUFFIX_ROOMS:
                        keys.append(key)
                        # Для каждого этажа удаляем его помещения
                        rooms_key = self._make_key(self.TYPE_FLOOR, f_id, self.SUFFIX_ROOMS)
                        if rooms_key in self._data:
                            keys.append(rooms_key)
                except (ValueError, IndexError):
                    continue
        
        return keys
    
    def _collect_floor_branch(self, floor_id: int) -> List[str]:
        """
        Собирает ключи для ветки этажа.
        
        Args:
            floor_id: ID этажа
            
        Returns:
            List[str]: Список ключей
        """
        keys = []
        
        # Удаляем этаж
        keys.append(self._make_key(self.TYPE_FLOOR, floor_id))
        keys.append(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS))
        
        # Удаляем сами помещения (они не имеют детей)
        prefix = f"{self.TYPE_ROOM}:"
        for key in list(self._data.keys()):
            if key.startswith(prefix):
                try:
                    _, r_id, suffix = self._parse_key(key)
                    if suffix is None:  # само помещение
                        keys.append(key)
                except (ValueError, IndexError):
                    continue
        
        return keys
    
    def invalidate_visible(self, expanded_nodes: List[Tuple[str, int]]) -> None:
        """
        Инвалидирует все раскрытые узлы (для обновления видимых).
        
        Args:
            expanded_nodes: Список кортежей (тип_узла, id_узла) раскрытых узлов
        """
        with self._lock:
            count = 0
            for node_type, node_id in expanded_nodes:
                self.invalidate_branch(node_type, node_id)
                count += 1
            
            log.info(f"Инвалидировано {count} раскрытых узлов")
    
    def clear(self) -> None:
        """Полностью очищает кэш."""
        with self._lock:
            self._data.clear()
            self._timestamps.clear()
            self._expanded_nodes.clear()
            self._hits = 0
            self._misses = 0
            self._invalidations += 1
            log.info("Cache: полная очистка")
    
    # ===== Методы для работы с раскрытыми узлами =====
    
    def mark_expanded(self, node_type: str, node_id: int) -> None:
        """
        Отмечает узел как раскрытый.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self._expanded_nodes.add(key)
            log.debug(f"Узел отмечен как раскрытый: {key}")
    
    def mark_collapsed(self, node_type: str, node_id: int) -> None:
        """
        Отмечает узел как свёрнутый.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self._expanded_nodes.discard(key)
            log.debug(f"Узел отмечен как свёрнутый: {key}")
    
    def get_expanded_nodes(self) -> List[Tuple[str, int]]:
        """
        Получает список всех раскрытых узлов.
        
        Returns:
            List[Tuple[str, int]]: Список кортежей (тип_узла, id_узла)
        """
        with self._lock:
            result = []
            for key in self._expanded_nodes:
                try:
                    type_, id_, _ = self._parse_key(key)
                    result.append((type_, id_))
                except (ValueError, IndexError):
                    continue
            return result
    
    def is_expanded(self, node_type: str, node_id: int) -> bool:
        """
        Проверяет, раскрыт ли узел.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            bool: True если узел раскрыт
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            return key in self._expanded_nodes
    
    # ===== Методы для точечной инвалидации =====
    
    def remove_children_cache(self, node_type: str, node_id: int) -> None:
        """
        Удаляет только кэш дочерних элементов, сохраняя сам узел.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = None
            if node_type == self.TYPE_COMPLEX:
                key = self._make_key(node_type, node_id, self.SUFFIX_BUILDINGS)
            elif node_type == self.TYPE_BUILDING:
                key = self._make_key(node_type, node_id, self.SUFFIX_FLOORS)
            elif node_type == self.TYPE_FLOOR:
                key = self._make_key(node_type, node_id, self.SUFFIX_ROOMS)
            
            if key and key in self._data:
                del self._data[key]
                if key in self._timestamps:
                    del self._timestamps[key]
                log.cache(f"Удалены дети {node_type}:{node_id}")
    
    # ===== Методы для статистики и отладки =====
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получает статистику использования кэша.
        
        Returns:
            Dict[str, Any]: Словарь со статистикой
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._data),
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f"{hit_rate:.1f}%",
                'invalidations': self._invalidations,
                'expanded_nodes': len(self._expanded_nodes),
                'keys': list(self._data.keys())
            }
    
    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()
        log.info("\n=== Cache Statistics ===")
        log.info(f"📦 Записей в кэше: {stats['size']}")
        log.info(f"🎯 Попаданий: {stats['hits']}")
        log.info(f"❌ Промахов: {stats['misses']}")
        log.info(f"📊 Hit rate: {stats['hit_rate']}")
        log.info(f"🔄 Инвалидаций: {stats['invalidations']}")
        log.info(f"🔍 Раскрытых узлов: {stats['expanded_nodes']}")
        log.info("=" * 30)
		
# client/src/models/__init__.py
"""
Модели данных для клиента
Экспортирует все модели для удобного импорта
"""
from .complex import Complex
from .building import Building
from .floor import Floor
from .room import Room

__all__ = [
    "Complex",
    "Building", 
    "Floor",
    "Room"
]

# client/src/models/building.py
"""
Модель данных для корпуса (building) на стороне клиента
Соответствует ответу от API /physical/complexes/{complex_id}/buildings
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Building:
    """
    Модель корпуса для отображения в дереве
    
    Поля соответствуют BuildingTreeResponse из бекенда:
    - id: уникальный идентификатор корпуса
    - name: название корпуса (например, "Корпус А")
    - complex_id: ID родительского комплекса
    - floors_count: количество этажей в корпусе
    
    Дополнительные поля для детального просмотра:
    - description: описание корпуса
    - address: адрес корпуса
    - status_id: ID статуса
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    name: str
    complex_id: int
    floors_count: int
    
    # Дополнительные поля
    description: Optional[str] = None
    address: Optional[str] = None
    status_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Building':
        """
        Создаёт объект Building из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 3, "name": "Корпус А", "complex_id": 1, "floors_count": 4}
            
        Returns:
            Building: объект корпуса
        """
        return cls(
            id=data['id'],
            name=data['name'],
            complex_id=data['complex_id'],
            floors_count=data['floors_count'],
            description=data.get('description'),
            address=data.get('address'),
            status_id=data.get('status_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        return self.name
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Building(id={self.id}, name='{self.name}', complex_id={self.complex_id}, floors={self.floors_count})"
		
# client/src/models/complex.py
"""
Модель данных для комплекса на стороне клиента
Обновлена с учётом поля buildings_count от API
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Complex:
    """
    Модель комплекса для отображения в дереве
    
    Поля соответствуют ComplexTreeResponse из бекенда:
    - id: уникальный идентификатор
    - name: название комплекса (то, что показываем в дереве)
    - buildings_count: количество корпусов (для отображения в скобках)
    
    Дополнительные поля для детального просмотра:
    - description: описание комплекса
    - address: адрес комплекса
    - owner_id: ID владельца
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    name: str
    buildings_count: int
    
    # Дополнительные поля (могут отсутствовать)
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Complex':
        """
        Создаёт объект Complex из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 1, "name": "Фабрика Веретено", "buildings_count": 2}
            
        Returns:
            Complex: объект комплекса
        """
        return cls(
            id=data['id'],
            name=data['name'],
            buildings_count=data.get('buildings_count', 0),
            description=data.get('description'),
            address=data.get('address'),
            owner_id=data.get('owner_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        return self.name
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Complex(id={self.id}, name='{self.name}', buildings={self.buildings_count})"
    
    def display_name(self) -> str:
        """
        Имя для отображения в дереве с количеством корпусов
        Используется в tree_model.py
        """
        if self.buildings_count > 0:
            return f"{self.name} ({self.buildings_count})"
        return self.name
		
# client/src/models/floor.py
"""
Модель данных для этажа (floor) на стороне клиента
Соответствует ответу от API /physical/buildings/{building_id}/floors
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Floor:
    """
    Модель этажа для отображения в дереве
    
    Поля соответствуют FloorTreeResponse из бекенда:
    - id: уникальный идентификатор этажа
    - number: номер этажа (целое число, может быть отрицательным)
    - building_id: ID родительского корпуса
    - rooms_count: количество помещений на этаже
    
    Дополнительные поля для детального просмотра:
    - description: описание этажа
    - physical_type_id: ID типа этажа
    - status_id: ID статуса
    - plan_image_url: URL плана этажа
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    number: int
    building_id: int
    rooms_count: int
    
    # Дополнительные поля
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    plan_image_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Floor':
        """
        Создаёт объект Floor из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 1, "number": 1, "building_id": 3, "rooms_count": 0}
            
        Returns:
            Floor: объект этажа
        """
        return cls(
            id=data['id'],
            number=data['number'],
            building_id=data['building_id'],
            rooms_count=data['rooms_count'],
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            status_id=data.get('status_id'),
            plan_image_url=data.get('plan_image_url'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        if self.number < 0:
            return f"Подвал {abs(self.number)}"
        elif self.number == 0:
            return "Цокольный этаж"
        else:
            return f"Этаж {self.number}"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Floor(id={self.id}, number={self.number}, building_id={self.building_id}, rooms={self.rooms_count})"
		
# client/src/models/room.py
"""
Модель данных для помещения (room) на стороне клиента
Соответствует ответу от API /physical/floors/{floor_id}/rooms
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Room:
    """
    Модель помещения для отображения в дереве
    
    Поля соответствуют RoomTreeResponse из бекенда:
    - id: уникальный идентификатор помещения
    - number: номер помещения (строка, может содержать буквы)
    - floor_id: ID родительского этажа
    - area: площадь помещения (опционально)
    - status_code: статус помещения (опционально)
    
    Дополнительные поля для детального просмотра:
    - description: описание помещения
    - physical_type_id: ID типа помещения
    - max_tenants: максимальное количество арендаторов
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    number: str
    floor_id: int
    area: Optional[float] = None
    status_code: Optional[str] = None
    
    # Дополнительные поля
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    max_tenants: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        """
        Создаёт объект Room из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 101, "number": "101", "floor_id": 1, 
                    "area": 45.5, "status_code": "free"}
            
        Returns:
            Room: объект помещения
        """
        return cls(
            id=data['id'],
            number=data['number'],
            floor_id=data['floor_id'],
            area=data.get('area'),
            status_code=data.get('status_code'),
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            max_tenants=data.get('max_tenants'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        return self.number
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Room(id={self.id}, number='{self.number}', floor_id={self.floor_id}, status={self.status_code})"
    
    def get_status_display(self) -> str:
        """
        Возвращает человекочитаемый статус помещения
        """
        status_map = {
            'free': 'Свободно',
            'occupied': 'Занято',
            'reserved': 'Зарезервировано',
            'maintenance': 'На обслуживании',
        }
        return status_map.get(self.status_code, self.status_code or 'Неизвестно')
		
# client/src/ui/details/__init__.py
"""
Пакет компонентов панели детальной информации
"""
from src.ui.details.details_panel import DetailsPanel

__all__ = ["DetailsPanel"]

# client/src/ui/details/base_panel.py
"""
Базовый класс для панели детальной информации.
Содержит общую инициализацию, базовые компоненты и методы
для управления отображением информации о выбранном объекте.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional, Dict, List, Any

from src.ui.details.header_widget import HeaderWidget
from src.ui.details.placeholder import PlaceholderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.tabs import DetailsTabs
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class DetailsPanelBase(QWidget):
    """
    Базовый класс для панели детальной информации.
    
    Предоставляет:
    - Шапку с иерархией (HeaderWidget)
    - Заглушку (PlaceholderWidget) для режима "ничего не выбрано"
    - Сетку информации (InfoGrid) для отображения данных
    - Вкладки (DetailsTabs) для дополнительной информации
    - Методы для управления видимостью компонентов
    - Прокси-методы для доступа к дочерним компонентам
    
    Наследники должны реализовать:
    - show_item_details() - отображение информации о конкретном объекте
    """
    
    # ===== Константы =====
    
    _CONTENT_MARGINS = (10, 10, 10, 10)
    """Отступы для контента (слева, сверху, справа, снизу)"""
    
    _LAYOUT_SPACING = 10
    """Расстояние между элементами в layout"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует базовую панель детальной информации.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация состояния
        self._init_state()
        
        # Инициализация UI
        self._init_ui()
        
        # Явно делаем панель видимой
        self.setVisible(True)
        
        log.debug("DetailsPanelBase: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_state(self) -> None:
        """Инициализирует состояние панели."""
        self._current_type: Optional[str] = None
        self._current_id: Optional[int] = None
        self._current_data: Optional[Any] = None
        
        log.debug("DetailsPanelBase: состояние инициализировано")
    
    def _init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        # Основной вертикальный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаём и добавляем шапку
        self._create_header()
        layout.addWidget(self._header)
        
        # Создаём и добавляем контейнер с контентом
        self._create_content_container()
        layout.addWidget(self._content_container, 1)  # Растягивается с коэффициентом 1
        
        log.debug("DetailsPanelBase: UI инициализирован")
    
    def _create_header(self) -> None:
        """Создаёт и настраивает шапку панели."""
        self._header = HeaderWidget(self)
        self._header.setVisible(True)
        log.debug("DetailsPanelBase: шапка создана")
    
    def _create_content_container(self) -> None:
        """Создаёт контейнер с заглушкой, сеткой и вкладками."""
        # Контейнер для контента (растягивается)
        self._content_container = QWidget(self)
        self._content_container.setVisible(True)
        
        # Layout для контейнера
        container_layout = QVBoxLayout(self._content_container)
        container_layout.setContentsMargins(*self._CONTENT_MARGINS)
        container_layout.setSpacing(self._LAYOUT_SPACING)
        
        # Заглушка (видима по умолчанию)
        self._placeholder = PlaceholderWidget(self._content_container)
        self._placeholder.setVisible(True)
        container_layout.addWidget(self._placeholder)
        
        # Сетка информации (скрыта по умолчанию)
        self._info_grid = InfoGrid(self._content_container)
        self._info_grid.setVisible(False)
        container_layout.addWidget(self._info_grid)
        
        # Вкладки (всегда видимы)
        self._tabs = DetailsTabs(self._content_container)
        self._tabs.setVisible(True)
        container_layout.addWidget(self._tabs)
        
        # Добавляем растяжку в конце, чтобы контент не прижимался к верху
        container_layout.addStretch()
        
        log.debug("DetailsPanelBase: контейнер контента создан")
    
    # ===== Геттеры =====
    
    @property
    def header(self) -> HeaderWidget:
        """
        Возвращает виджет шапки.
        
        Returns:
            HeaderWidget: Виджет шапки
        """
        return self._header
    
    @property
    def title_label(self) -> QLabel:
        """Прокси для заголовка из шапки."""
        return self._header.title_label
    
    @property
    def hierarchy_label(self) -> QLabel:
        """Прокси для метки иерархии из шапки."""
        return self._header.hierarchy_label
    
    @property
    def status_label(self) -> QLabel:
        """Прокси для метки статуса из шапки."""
        return self._header.status_label
    
    @property
    def icon_label(self) -> QLabel:
        """Прокси для метки иконки из шапки."""
        return self._header.icon_label
    
    @property
    def placeholder(self) -> PlaceholderWidget:
        """
        Возвращает виджет-заглушку.
        
        Returns:
            PlaceholderWidget: Виджет заглушки
        """
        return self._placeholder
    
    @property
    def info_grid(self) -> InfoGrid:
        """
        Возвращает сетку информации.
        
        Returns:
            InfoGrid: Сетка с полями
        """
        return self._info_grid
    
    @property
    def fields(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь полей из сетки информации.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_значения}
        """
        return self._info_grid.fields
    
    @property
    def tabs(self) -> DetailsTabs:
        """
        Возвращает виджет вкладок.
        
        Returns:
            DetailsTabs: Виджет вкладок
        """
        return self._tabs
    
    @property
    def content_container(self) -> QWidget:
        """
        Возвращает контейнер с контентом.
        
        Returns:
            QWidget: Контейнер контента
        """
        return self._content_container
    
    # ===== Методы управления видимостью =====
    
    def show_info_grid(self) -> None:
        """
        Показывает сетку информации и скрывает заглушку.
        Также убеждается, что вся цепочка родительских виджетов видима.
        """
        log.debug("DetailsPanelBase: показываем info_grid")
        
        # Убеждаемся, что вся цепочка видима
        self.setVisible(True)
        self._content_container.setVisible(True)
        self._info_grid.setVisible(True)
        
        # Скрываем заглушку
        self._placeholder.setVisible(False)
        
        log.debug("DetailsPanelBase: info_grid показана, заглушка скрыта")
    
    def hide_info_grid(self) -> None:
        """
        Скрывает сетку информации и показывает заглушку.
        """
        self._placeholder.setVisible(True)
        self._info_grid.setVisible(False)
        log.debug("DetailsPanelBase: info_grid скрыта, заглушка показана")
    
    # ===== Методы управления полями =====
    
    def clear_all_fields(self) -> None:
        """Очищает все поля в сетке информации."""
        self._info_grid.clear_all()
        log.debug("DetailsPanelBase: все поля очищены")
    
    def set_field(self, key: str, value: Optional[str]) -> None:
        """
        Устанавливает значение для указанного поля.
        
        Args:
            key: Ключ поля
            value: Значение для установки
        """
        self._info_grid.set_field(key, value)
    
    def set_status_style(self, status: Optional[str]) -> None:
        """
        Устанавливает стиль статуса в шапке.
        
        Args:
            status: Код статуса
        """
        self._header.set_status_style(status)
    
    def show_fields(self, *keys: str) -> None:
        """
        Показывает только указанные поля.
        
        Args:
            *keys: Ключи полей для отображения
        """
        self._info_grid.show_only(*keys)
    
    # ===== Методы для работы с вкладками =====
    
    def set_current_tab(self, index: int) -> None:
        """
        Устанавливает текущую вкладку по индексу.
        
        Args:
            index: Индекс вкладки
        """
        self._tabs.setCurrentIndex(index)
        log.debug(f"DetailsPanelBase: установлена вкладка {index}")
    
    def get_current_tab(self) -> int:
        """
        Возвращает индекс текущей вкладки.
        
        Returns:
            int: Индекс текущей вкладки
        """
        return self._tabs.currentIndex()
    
    # ===== Методы для работы с состоянием =====
    
    @property
    def current_type(self) -> Optional[str]:
        """Возвращает тип текущего выбранного объекта."""
        return self._current_type
    
    @current_type.setter
    def current_type(self, value: Optional[str]) -> None:
        """Устанавливает тип текущего выбранного объекта."""
        self._current_type = value
    
    @property
    def current_id(self) -> Optional[int]:
        """Возвращает ID текущего выбранного объекта."""
        return self._current_id
    
    @current_id.setter
    def current_id(self, value: Optional[int]) -> None:
        """Устанавливает ID текущего выбранного объекта."""
        self._current_id = value
    
    @property
    def current_data(self) -> Optional[Any]:
        """Возвращает данные текущего выбранного объекта."""
        return self._current_data
    
    @current_data.setter
    def current_data(self, value: Optional[Any]) -> None:
        """Устанавливает данные текущего выбранного объекта."""
        self._current_data = value
    
    def is_object_selected(self) -> bool:
        """
        Проверяет, выбран ли какой-либо объект.
        
        Returns:
            bool: True если объект выбран
        """
        return self._current_type is not None and self._current_id is not None
    
    def clear_selection(self) -> None:
        """Очищает информацию о выбранном объекте."""
        self._current_type = None
        self._current_id = None
        self._current_data = None
        log.debug("DetailsPanelBase: выделение сброшено")
		
# client/src/ui/details/details_panel.py
"""
Основной класс панели детальной информации.
Объединяет все компоненты для отображения информации о выбранном объекте:
- Шапка с иерархией
- Сетка с полями информации
- Вкладки для дополнительных данных
"""
from PySide6.QtCore import Slot
from typing import Optional, Tuple, Any, Dict, List

from src.ui.details.base_panel import DetailsPanelBase
from src.ui.details.display_handlers import DisplayHandlers
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room

from src.utils.logger import get_logger
log = get_logger(__name__)


class DetailsPanel(DetailsPanelBase):
    """
    Панель детальной информации для отображения данных о выбранном объекте.
    
    Особенности:
    - Автоматически подстраивается под тип объекта
    - Использует контекст иерархии для построения правильной цепочки
    - Скрывает заглушку и показывает информацию при выборе объекта
    - Очищается при отсутствии выбора
    
    Поддерживаемые типы объектов:
    - complex (комплекс)
    - building (корпус)
    - floor (этаж)
    - room (помещение)
    """
    
    # ===== Константы =====
    
    _UNKNOWN_COMPLEX = "Неизвестный комплекс"
    """Текст для неизвестного комплекса в контексте"""
    
    _UNKNOWN_BUILDING = "Неизвестный корпус"
    """Текст для неизвестного корпуса в контексте"""
    
    _DEFAULT_FLOOR_NUM = 0
    """Номер этажа по умолчанию"""
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует панель детальной информации.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        log.success("DetailsPanel: создана")
    
    # ===== Приватные методы =====
    
    def _log_hierarchy(self, item_type: str, hierarchy_text: str) -> None:
        """
        Логирует информацию об иерархии для отладки.
        
        Args:
            item_type: Тип объекта
            hierarchy_text: Текст иерархии
        """
        log.debug(f"DetailsPanel: [{item_type}] иерархия: {hierarchy_text}")
    
    def _log_visible_fields(self) -> None:
        """Логирует список видимых полей для отладки."""
        visible = self.info_grid.get_visible_fields()
        log.debug(f"DetailsPanel: видимые поля: {sorted(visible)}")
    
    def _validate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет и дополняет контекст значениями по умолчанию.
        
        Args:
            context: Исходный контекст
            
        Returns:
            Dict[str, Any]: Проверенный контекст с заполненными пропусками
        """
        validated = context.copy() if context else {}
        
        # Устанавливаем значения по умолчанию для отсутствующих ключей
        if 'complex_name' not in validated or validated['complex_name'] is None:
            validated['complex_name'] = self._UNKNOWN_COMPLEX
            
        if 'building_name' not in validated or validated['building_name'] is None:
            validated['building_name'] = self._UNKNOWN_BUILDING
            
        if 'floor_num' not in validated or validated['floor_num'] is None:
            validated['floor_num'] = self._DEFAULT_FLOOR_NUM
        
        return validated
    
    # ===== Публичные методы =====
    
    @Slot(str, int, object, dict)
    def show_item_details(self, item_type: str, item_id: int, 
                          item_data: Any, context: Dict[str, Any]) -> None:
        """
        Показывает информацию о выбранном объекте с учётом контекста.
        
        Args:
            item_type: Тип элемента ('complex', 'building', 'floor', 'room')
            item_id: Идентификатор элемента
            item_data: Объект модели (Complex, Building, Floor или Room)
            context: Словарь с именами родительских узлов
        """
        # Сохраняем информацию о выбранном объекте
        self._current_type = item_type
        self._current_id = item_id
        self._current_data = item_data
        
        # Логируем полученные данные
        log.info(f"DetailsPanel: выбран {item_type} #{item_id}")
        log.debug(f"DetailsPanel: контекст: {context}")
        
        # Проверяем и дополняем контекст
        validated_context = self._validate_context(context)
        
        # Скрываем заглушку
        self.placeholder.hide()
        
        # Очищаем поля
        self.clear_all_fields()
        
        # Отображаем соответствующий тип с контекстом
        self._display_by_type(item_type, item_data, validated_context)
        
        # Логируем результат для отладки
        self._log_visible_fields()
    
    def _display_by_type(self, item_type: str, item_data: Any, context: Dict[str, Any]) -> None:
        """
        Отображает данные в зависимости от типа объекта.
        
        Args:
            item_type: Тип объекта
            item_data: Данные объекта
            context: Контекст иерархии
        """
        if item_type == 'complex' and isinstance(item_data, Complex):
            DisplayHandlers.show_complex(self, item_data)
            
        elif item_type == 'building' and isinstance(item_data, Building):
            complex_name = context.get('complex_name', self._UNKNOWN_COMPLEX)
            DisplayHandlers.show_building(self, item_data, complex_name)
            
        elif item_type == 'floor' and isinstance(item_data, Floor):
            building_name = context.get('building_name', self._UNKNOWN_BUILDING)
            complex_name = context.get('complex_name', self._UNKNOWN_COMPLEX)
            DisplayHandlers.show_floor(self, item_data, building_name, complex_name)
            
        elif item_type == 'room' and isinstance(item_data, Room):
            floor_num = context.get('floor_num', self._DEFAULT_FLOOR_NUM)
            building_name = context.get('building_name', self._UNKNOWN_BUILDING)
            complex_name = context.get('complex_name', self._UNKNOWN_COMPLEX)
            DisplayHandlers.show_room(self, item_data, floor_num, building_name, complex_name)
            
        else:
            log.warning(f"DetailsPanel: неизвестный тип объекта '{item_type}'")
            self.clear()
    
    def clear(self) -> None:
        """Очищает панель и показывает заглушку."""
        self._current_type = None
        self._current_id = None
        self._current_data = None
        
        # Скрываем сетку, показываем заглушку
        self.hide_info_grid()
        
        # Очищаем заголовки
        self.title_label.setText("")
        self.hierarchy_label.setText("")
        self.status_label.setText("")
        self.icon_label.setText(DisplayHandlers.ICON_COMPLEX)
        
        log.debug("DetailsPanel: очищена")
    
    def get_current_selection(self) -> Tuple[Optional[str], Optional[int], Optional[Any]]:
        """
        Возвращает информацию о текущем выбранном объекте.
        
        Returns:
            Tuple[Optional[str], Optional[int], Optional[Any]]:
            (тип, идентификатор, данные) или (None, None, None)
        """
        return self._current_type, self._current_id, self._current_data
    
    def is_object_selected(self) -> bool:
        """
        Проверяет, выбран ли какой-либо объект.
        
        Returns:
            bool: True если объект выбран
        """
        return self._current_type is not None and self._current_id is not None
    
    def get_current_type(self) -> Optional[str]:
        """
        Возвращает тип текущего выбранного объекта.
        
        Returns:
            Optional[str]: Тип объекта или None
        """
        return self._current_type
    
    def get_current_id(self) -> Optional[int]:
        """
        Возвращает ID текущего выбранного объекта.
        
        Returns:
            Optional[int]: ID объекта или None
        """
        return self._current_id
    
    def get_current_data(self) -> Optional[Any]:
        """
        Возвращает данные текущего выбранного объекта.
        
        Returns:
            Optional[Any]: Объект модели или None
        """
        return self._current_data
		
# client/src/ui/details/display_handlers.py
"""
Обработчики отображения для разных типов объектов.
Предоставляют методы для заполнения панели детальной информации
данными из моделей Complex, Building, Floor, Room.
"""
from typing import TYPE_CHECKING

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.ui.details.field_manager import FieldManager

from src.utils.logger import get_logger
log = get_logger(__name__)


# Для избежания циклических импортов при проверке типов
if TYPE_CHECKING:
    from src.ui.details.base_panel import DetailsPanelBase


class DisplayHandlers:
    """
    Набор статических методов для отображения разных типов объектов.
    
    Каждый метод отвечает за заполнение панели данными соответствующего типа:
    - show_complex: отображение комплекса
    - show_building: отображение корпуса
    - show_floor: отображение этажа
    - show_room: отображение помещения
    
    Методы учитывают контекст иерархии и статус объекта.
    """
    
    # ===== Константы =====
    
    # Тексты для статусов по умолчанию
    _DEFAULT_STATUS = "Активен"
    """Текст статуса по умолчанию для комплексов, корпусов и этажей"""
    
    # Иконки для разных типов объектов
    ICON_COMPLEX = "🏢"
    ICON_BUILDING = "🏭"
    ICON_FLOOR = "🏗️"
    ICON_ROOM = "🚪"
    
    # Тексты для ссылок на планировки
    _PLAN_COMPLEX = "[ ссылка на общий план ]"
    _PLAN_BUILDING = "[ ссылка на планы корпуса ]"
    _PLAN_FLOOR = "[ ссылка на план этажа ]"
    
    # Текст для типа этажа по умолчанию
    _DEFAULT_FLOOR_TYPE = "Этаж с офисами"
    
    # Текст для отсутствующего описания
    _DESCRIPTION_MISSING = "Описание отсутствует"
    
    # ===== Приватные вспомогательные методы =====
    
    @staticmethod
    def _log_hierarchy(panel: 'DetailsPanelBase', item_type: str, hierarchy_text: str) -> None:
        """
        Логирует информацию об иерархии для отладки.
        
        Args:
            panel: Панель деталей
            item_type: Тип объекта
            hierarchy_text: Текст иерархии
        """
        if hasattr(panel, '_log_hierarchy'):
            panel._log_hierarchy(item_type, hierarchy_text)
    
    @staticmethod
    def _format_floor_number(number: int) -> str:
        """
        Форматирует номер этажа с учётом подвала и цоколя.
        
        Args:
            number: Номер этажа
            
        Returns:
            str: Отформатированное название этажа
        """
        if number < 0:
            return f"Подвал {abs(number)}"
        elif number == 0:
            return "Цокольный этаж"
        else:
            return f"Этаж {number}"
    
    @staticmethod
    def _format_room_hierarchy(floor_num: int, building_name: str, complex_name: str) -> str:
        """
        Форматирует строку иерархии для помещения.
        
        Args:
            floor_num: Номер этажа
            building_name: Название корпуса
            complex_name: Название комплекса
            
        Returns:
            str: Отформатированная строка иерархии
        """
        if floor_num < 0:
            floor_text = f"подвал {abs(floor_num)}"
        elif floor_num == 0:
            floor_text = "цокольный этаж"
        else:
            floor_text = f"этаж {floor_num}"
        
        return f"(этаж {floor_num}, корпус {building_name}, комплекс: {complex_name})"
    
    # ===== Публичные методы отображения =====
    
    @staticmethod
    def show_complex(panel: 'DetailsPanelBase', data: Complex) -> None:
        """
        Отображает информацию о комплексе.
        
        Args:
            panel: Панель деталей
            data: Данные комплекса
        """
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(f"КОМПЛЕКС: {data.name}")
        panel.hierarchy_label.setText("")
        panel.icon_label.setText(DisplayHandlers.ICON_COMPLEX)
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "complex", "корневой уровень")
        
        # Устанавливаем статус
        panel.status_label.setText(DisplayHandlers._DEFAULT_STATUS)
        panel.set_status_style(None)
        
        # Устанавливаем поля
        panel.set_field("address", data.address)
        panel.set_field("owner", FieldManager.format_owner(data.owner_id))
        panel.set_field("description", data.description)
        panel.set_field("plan", DisplayHandlers._PLAN_COMPLEX)
        
        # Очищаем лишние поля
        panel.set_field("tenant", None)
        panel.set_field("type", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        
        # Показываем сетку и нужные поля
        panel.show_info_grid()
        panel.show_fields("address", "owner", "description", "plan")
        
        log.info(f"Отображён комплекс '{data.name}' (ID: {data.id})")
    
    @staticmethod
    def show_building(panel: 'DetailsPanelBase', data: Building, complex_name: str) -> None:
        """
        Отображает информацию о корпусе.
        
        Args:
            panel: Панель деталей
            data: Данные корпуса
            complex_name: Название родительского комплекса
        """
        # Формируем заголовок и иерархию
        panel.title_label.setText(f"КОРПУС: {data.name}")
        hierarchy_text = f"(в составе комплекса: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_BUILDING)
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "building", hierarchy_text)
        
        # Устанавливаем статус
        panel.status_label.setText(DisplayHandlers._DEFAULT_STATUS)
        panel.set_status_style(None)
        
        # Устанавливаем поля
        panel.set_field("address", data.address)
        panel.set_field("description", data.description)
        panel.set_field("plan", DisplayHandlers._PLAN_BUILDING)
        
        # Очищаем лишние поля
        panel.set_field("owner", None)
        panel.set_field("tenant", None)
        panel.set_field("type", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        
        # Показываем сетку и нужные поля
        panel.show_info_grid()
        panel.show_fields("address", "description", "plan")
        
        log.info(f"Отображён корпус '{data.name}' (ID: {data.id})")
    
    @staticmethod
    def show_floor(panel: 'DetailsPanelBase', data: Floor, building_name: str, complex_name: str) -> None:
        """
        Отображает информацию об этаже.
        
        Args:
            panel: Панель деталей
            data: Данные этажа
            building_name: Название родительского корпуса
            complex_name: Название родительского комплекса
        """
        # Форматируем номер этажа
        floor_text = DisplayHandlers._format_floor_number(data.number)
        
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(f"ЭТАЖ: {floor_text}")
        hierarchy_text = f"(в составе корпуса: {building_name}, комплекс: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_FLOOR)
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "floor", hierarchy_text)
        
        # Устанавливаем статус
        panel.status_label.setText(DisplayHandlers._DEFAULT_STATUS)
        panel.set_status_style(None)
        
        # Устанавливаем поля
        panel.set_field("description", data.description)
        panel.set_field("plan", DisplayHandlers._PLAN_FLOOR)
        panel.set_field("type", DisplayHandlers._DEFAULT_FLOOR_TYPE)
        
        # Очищаем лишние поля
        panel.set_field("address", None)
        panel.set_field("owner", None)
        panel.set_field("tenant", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        
        # Показываем сетку и нужные поля
        panel.show_info_grid()
        panel.show_fields("description", "plan", "type")
        
        log.info(f"Отображён этаж {data.number} (ID: {data.id})")
    
    @staticmethod
    def show_room(panel: 'DetailsPanelBase', data: Room, floor_num: int, 
                  building_name: str, complex_name: str) -> None:
        """
        Отображает информацию о помещении.
        
        Args:
            panel: Панель деталей
            data: Данные помещения
            floor_num: Номер этажа
            building_name: Название родительского корпуса
            complex_name: Название родительского комплекса
        """
        # Устанавливаем заголовок
        panel.title_label.setText(f"ПОМЕЩЕНИЕ: {data.number}")
        
        # Формируем и устанавливаем иерархию
        hierarchy_text = DisplayHandlers._format_room_hierarchy(
            floor_num, building_name, complex_name
        )
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_ROOM)
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "room", hierarchy_text)
        
        # Устанавливаем статус
        status_text = FieldManager.format_status(data.status_code)
        panel.status_label.setText(status_text)
        panel.set_status_style(data.status_code)
        
        # Устанавливаем основные поля
        panel.set_field("address", FieldManager.format_area(data.area))
        panel.set_field("type", FieldManager.format_room_type(data.physical_type_id))
        panel.set_field("description", data.description or DisplayHandlers._DESCRIPTION_MISSING)
        panel.set_field("plan", None)  # Планировка пока не поддерживается
        
        # Определяем базовые поля для всех помещений
        base_fields = ["address", "type", "description", "plan"]
        
        # Обработка в зависимости от статуса
        if data.status_code == 'occupied':
            # Для занятых помещений добавляем поля аренды
            DisplayHandlers._set_occupied_room_fields(panel, data)
            
            # Показываем все поля
            panel.show_fields(*(base_fields + ["tenant", "contract", "valid_until", "rent"]))
            
            log.info(f"Отображено занятое помещение {data.number} (ID: {data.id})")
        else:
            # Для свободных и других статусов
            DisplayHandlers._clear_rental_fields(panel)
            
            # Показываем только базовые поля
            panel.show_fields(*base_fields)
            
            log.info(f"Отображено помещение {data.number} (ID: {data.id}), статус: {data.status_code}")
    
    # ===== Приватные методы для работы с помещениями =====
    
    @staticmethod
    def _set_occupied_room_fields(panel: 'DetailsPanelBase', data: Room) -> None:
        """
        Устанавливает поля для занятого помещения.
        
        Args:
            panel: Панель деталей
            data: Данные помещения
        """
        # TODO: брать реальные данные из БД
        panel.set_field("tenant", "Арендатор: ООО \"Ромашка\" (ИНН 7712345678)")
        panel.set_field("contract", "Договор: №А-2024-001 от 01.01.2024")
        panel.set_field("valid_until", "Действует до: 31.12.2025")
        panel.set_field("rent", "Арендная плата: 45 000 ₽/мес")
        
        # Очищаем поле владельца (не нужно для аренды)
        panel.set_field("owner", None)
    
    @staticmethod
    def _clear_rental_fields(panel: 'DetailsPanelBase') -> None:
        """
        Очищает поля аренды для свободного помещения.
        
        Args:
            panel: Панель деталей
        """
        panel.set_field("tenant", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        panel.set_field("owner", None)
		
# client/src/ui/details/field_manager.py
"""
Менеджер для форматирования и обработки полей информации.
Предоставляет статические методы для преобразования данных из БД
в человекочитаемый формат для отображения в панели деталей.
"""
from typing import Dict, Any, Optional, Union
from datetime import datetime

from src.utils.logger import get_logger
log = get_logger(__name__)


class FieldManager:
    """
    Управляет форматированием значений полей для отображения.
    
    Содержит методы для форматирования:
    - Статусов объектов
    - Типов помещений
    - Площади
    - Информации о владельце
    - Дат
    
    В будущем может быть расширен для получения данных из справочников БД.
    """
    
    # ===== Константы =====
    
    # Карта типов помещений (временная, потом будет из БД)
    ROOM_TYPE_MAP: Dict[int, str] = {
        1: "Офисное помещение",
        2: "Архив",
        3: "Склад",
        4: "Техническое помещение",
    }
    """Словарь для преобразования ID типа помещения в текстовое описание"""
    
    # Карта статусов
    STATUS_MAP: Dict[str, str] = {
        'free': 'СВОБОДНО',
        'occupied': 'ЗАНЯТО',
        'reserved': 'ЗАРЕЗЕРВИРОВАНО',
        'maintenance': 'РЕМОНТ'
    }
    """Словарь для преобразования кода статуса в текстовое описание"""
    
    # Значения по умолчанию
    DEFAULT_UNKNOWN_STATUS = "НЕИЗВЕСТНО"
    """Текст для неизвестного статуса"""
    
    DEFAULT_UNKNOWN_TYPE = "Неизвестный тип"
    """Текст для неизвестного типа помещения"""
    
    DEFAULT_AREA_FORMAT = "Площадь: {area} м²"
    """Шаблон для форматирования площади"""
    
    DEFAULT_AREA_MISSING = "Площадь не указана"
    """Текст при отсутствии информации о площади"""
    
    DEFAULT_OWNER_FORMAT = "ID владельца: {owner_id}"
    """Шаблон для форматирования информации о владельце"""
    
    DEFAULT_DATE_FORMAT = "%d.%m.%Y %H:%M"
    """Формат для отображения дат"""
    
    # ===== Публичные методы форматирования =====
    
    @staticmethod
    def format_status(status_code: Optional[str]) -> str:
        """
        Форматирует код статуса в человекочитаемый текст.
        
        Args:
            status_code: Код статуса ('free', 'occupied', и т.д.)
            
        Returns:
            str: Текстовое представление статуса
        """
        if status_code is None:
            return FieldManager.DEFAULT_UNKNOWN_STATUS
        
        formatted = FieldManager.STATUS_MAP.get(
            status_code, 
            status_code.upper() if status_code else FieldManager.DEFAULT_UNKNOWN_STATUS
        )
        
        log.debug(f"FieldManager: статус '{status_code}' -> '{formatted}'")
        return formatted
    
    @staticmethod
    def format_room_type(type_id: Optional[int]) -> str:
        """
        Форматирует ID типа помещения в текстовое описание.
        
        Args:
            type_id: ID типа помещения из справочника
            
        Returns:
            str: Название типа помещения
        """
        if type_id is None:
            return FieldManager.DEFAULT_UNKNOWN_TYPE
        
        formatted = FieldManager.ROOM_TYPE_MAP.get(
            type_id, 
            f"{FieldManager.DEFAULT_UNKNOWN_TYPE} (ID: {type_id})"
        )
        
        log.debug(f"FieldManager: тип помещения {type_id} -> '{formatted}'")
        return formatted
    
    @staticmethod
    def format_area(area: Optional[float]) -> str:
        """
        Форматирует значение площади.
        
        Args:
            area: Площадь в квадратных метрах
            
        Returns:
            str: Отформатированная строка с площадью
        """
        if area is None:
            return FieldManager.DEFAULT_AREA_MISSING
        
        formatted = FieldManager.DEFAULT_AREA_FORMAT.format(area=area)
        log.debug(f"FieldManager: площадь {area} м²")
        return formatted
    
    @staticmethod
    def format_owner(owner_id: Optional[int]) -> Optional[str]:
        """
        Форматирует информацию о владельце.
        
        Args:
            owner_id: ID владельца
            
        Returns:
            Optional[str]: Строка с информацией о владельце или None
        """
        if owner_id is None:
            return None
        
        formatted = FieldManager.DEFAULT_OWNER_FORMAT.format(owner_id=owner_id)
        log.debug(f"FieldManager: владелец ID {owner_id}")
        return formatted
    
    @staticmethod
    def format_datetime(dt: Optional[Union[str, datetime]]) -> Optional[str]:
        """
        Форматирует дату и время.
        
        Args:
            dt: Дата и время (строка ISO или объект datetime)
            
        Returns:
            Optional[str]: Отформатированная дата или None
        """
        if dt is None:
            return None
        
        try:
            if isinstance(dt, str):
                # Пробуем распарсить ISO формат
                if 'T' in dt:
                    # Берём только дату и время до минут
                    date_part = dt.split('T')[0]
                    time_part = dt.split('T')[1][:5]
                    formatted = f"{date_part} {time_part}"
                else:
                    formatted = dt
            elif hasattr(dt, 'strftime'):
                formatted = dt.strftime(FieldManager.DEFAULT_DATE_FORMAT)
            else:
                formatted = str(dt)
            
            log.debug(f"FieldManager: дата '{dt}' -> '{formatted}'")
            return formatted
            
        except Exception as error:
            log.error(f"FieldManager: ошибка форматирования даты '{dt}': {error}")
            return str(dt)
    
    @staticmethod
    def format_tenant(tenant_name: Optional[str], inn: Optional[str] = None) -> Optional[str]:
        """
        Форматирует информацию об арендаторе.
        
        Args:
            tenant_name: Название организации-арендатора
            inn: ИНН организации (опционально)
            
        Returns:
            Optional[str]: Отформатированная строка с информацией об арендаторе
        """
        if not tenant_name:
            return None
        
        if inn:
            formatted = f"Арендатор: {tenant_name} (ИНН {inn})"
        else:
            formatted = f"Арендатор: {tenant_name}"
        
        log.debug(f"FieldManager: арендатор '{formatted}'")
        return formatted
    
    @staticmethod
    def format_contract(contract_number: Optional[str], date_from: Optional[str] = None) -> Optional[str]:
        """
        Форматирует информацию о договоре.
        
        Args:
            contract_number: Номер договора
            date_from: Дата начала действия (опционально)
            
        Returns:
            Optional[str]: Отформатированная строка с информацией о договоре
        """
        if not contract_number:
            return None
        
        if date_from:
            formatted = f"Договор: №{contract_number} от {date_from}"
        else:
            formatted = f"Договор: №{contract_number}"
        
        log.debug(f"FieldManager: договор '{formatted}'")
        return formatted
    
    @staticmethod
    def format_valid_until(date_to: Optional[str]) -> Optional[str]:
        """
        Форматирует дату окончания действия договора.
        
        Args:
            date_to: Дата окончания
            
        Returns:
            Optional[str]: Отформатированная строка с датой
        """
        if not date_to:
            return None
        
        formatted = f"Действует до: {date_to}"
        log.debug(f"FieldManager: действует до '{formatted}'")
        return formatted
    
    @staticmethod
    def format_rent(amount: Optional[float], currency: str = "₽", period: str = "мес") -> Optional[str]:
        """
        Форматирует информацию об арендной плате.
        
        Args:
            amount: Сумма арендной платы
            currency: Валюта (по умолчанию ₽)
            period: Период (по умолчанию "мес")
            
        Returns:
            Optional[str]: Отформатированная строка с арендной платой
        """
        if amount is None:
            return None
        
        formatted = f"Арендная плата: {amount:,.0f} {currency}/{period}".replace(",", " ")
        log.debug(f"FieldManager: арендная плата '{formatted}'")
        return formatted
    
    # ===== Вспомогательные методы =====
    
    @staticmethod
    def get_available_room_types() -> Dict[int, str]:
        """
        Возвращает словарь доступных типов помещений.
        
        Returns:
            Dict[int, str]: Словарь {ID: название}
        """
        return FieldManager.ROOM_TYPE_MAP.copy()
    
    @staticmethod
    def get_available_statuses() -> Dict[str, str]:
        """
        Возвращает словарь доступных статусов.
        
        Returns:
            Dict[str, str]: Словарь {код: название}
        """
        return FieldManager.STATUS_MAP.copy()
    
    @staticmethod
    def is_valid_status(status_code: Optional[str]) -> bool:
        """
        Проверяет, является ли статус допустимым.
        
        Args:
            status_code: Код статуса для проверки
            
        Returns:
            bool: True если статус известен
        """
        return status_code in FieldManager.STATUS_MAP
		
# client/src/ui/details/header_widget.py
"""
Виджет шапки для панели детальной информации.
Содержит иконку объекта, заголовок, статус и строку иерархии.
Обеспечивает единообразное отображение верхней части панели для всех типов объектов.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional, Dict

from src.utils.logger import get_logger
log = get_logger(__name__)


class HeaderWidget(QWidget):
    """
    Шапка панели детальной информации.
    
    Состоит из двух строк:
    - Верхняя строка: иконка, заголовок, статус
    - Нижняя строка: иерархия (в составе...)
    
    Предоставляет методы для установки заголовка, статуса, иерархии
    и изменения внешнего вида статуса в зависимости от его значения.
    """
    
    # ===== Константы =====
    
    # Стили для всего виджета
    _WIDGET_STYLESHEET = """
        QWidget {
            background-color: #f5f5f5;
            border-bottom: 2px solid #d0d0d0;
        }
    """
    """Общий стиль виджета"""
    
    # Стили для иконки
    _ICON_STYLESHEET = "font-size: 24px;"
    """Стиль для иконки объекта"""
    
    # Базовый стиль для статуса
    _STATUS_BASE_STYLE = "padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;"
    """Базовая часть стиля статуса (без цвета)"""
    
    # Стили для разных статусов
    _STATUS_STYLES: Dict[str, str] = {
        'free': _STATUS_BASE_STYLE + "background-color: #c8e6c9; color: #2e7d32;",
        'occupied': _STATUS_BASE_STYLE + "background-color: #ffcdd2; color: #c62828;",
        'reserved': _STATUS_BASE_STYLE + "background-color: #fff9c4; color: #f57f17;",
        'maintenance': _STATUS_BASE_STYLE + "background-color: #ffecb3; color: #ff6f00;",
    }
    """Словарь стилей для каждого статуса"""
    
    _STATUS_DEFAULT_STYLE = _STATUS_BASE_STYLE + "background-color: #e0e0e0;"
    """Стиль по умолчанию для неизвестного статуса"""
    
    # Стиль для иерархии
    _HIERARCHY_STYLESHEET = "color: #666666; font-size: 11px;"
    """Стиль для текста иерархии"""
    
    # ===== Константы размеров =====
    _HEADER_HEIGHT = 80
    """Высота шапки в пикселях"""
    
    _CONTENT_MARGINS = (15, 5, 15, 5)
    """Отступы содержимого (слева, сверху, справа, снизу)"""
    
    _ICON_FONT_SIZE = 24
    """Размер шрифта для иконки в пикселях"""
    
    _TITLE_FONT_SIZE = 16
    """Размер шрифта для заголовка в пикселях"""
    
    _STATUS_FONT_SIZE = 12
    """Размер шрифта для статуса в пикселях"""
    
    _HIERARCHY_FONT_SIZE = 11
    """Размер шрифта для иерархии в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет шапки.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Настройка внешнего вида
        self._setup_appearance()
        
        # Создание UI
        self._init_ui()
        
        log.debug("HeaderWidget: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _setup_appearance(self) -> None:
        """
        Настраивает внешний вид виджета: стили и размер.
        """
        self.setStyleSheet(self._WIDGET_STYLESHEET)
        self.setFixedHeight(self._HEADER_HEIGHT)
    
    def _init_ui(self) -> None:
        """
        Инициализирует пользовательский интерфейс шапки.
        Создаёт layout, верхнюю и нижнюю строки.
        """
        # Основной вертикальный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*self._CONTENT_MARGINS)
        
        # Верхняя строка: иконка + заголовок + статус
        top_row = self._create_top_row()
        layout.addLayout(top_row)
        
        # Нижняя строка: иерархия
        self._hierarchy_label = self._create_hierarchy_label()
        layout.addWidget(self._hierarchy_label)
        
        log.debug("HeaderWidget: UI инициализирован")
    
    def _create_top_row(self) -> QHBoxLayout:
        """
        Создаёт верхнюю строку с иконкой, заголовком и статусом.
        
        Returns:
            QHBoxLayout: Layout верхней строки
        """
        top_row = QHBoxLayout()
        
        # Иконка
        self._icon_label = self._create_icon_label()
        top_row.addWidget(self._icon_label)
        
        # Заголовок (растягивается)
        self._title_label = self._create_title_label()
        top_row.addWidget(self._title_label, 1)
        
        # Статус
        self._status_label = self._create_status_label()
        top_row.addWidget(self._status_label)
        
        return top_row
    
    def _create_icon_label(self) -> QLabel:
        """
        Создаёт метку для иконки объекта.
        
        Returns:
            QLabel: Настроенная метка для иконки
        """
        label = QLabel("🏢")  # Иконка по умолчанию
        label.setStyleSheet(self._ICON_STYLESHEET)
        return label
    
    def _create_title_label(self) -> QLabel:
        """
        Создаёт метку для заголовка.
        
        Returns:
            QLabel: Настроенная метка для заголовка
        """
        label = QLabel("")
        
        # Настройка шрифта
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(self._TITLE_FONT_SIZE)
        label.setFont(title_font)
        
        return label
    
    def _create_status_label(self) -> QLabel:
        """
        Создаёт метку для статуса.
        
        Returns:
            QLabel: Настроенная метка для статуса
        """
        label = QLabel("")
        label.setStyleSheet(self._STATUS_DEFAULT_STYLE)
        return label
    
    def _create_hierarchy_label(self) -> QLabel:
        """
        Создаёт метку для отображения иерархии.
        
        Returns:
            QLabel: Настроенная метка для иерархии
        """
        label = QLabel("")
        label.setStyleSheet(self._HIERARCHY_STYLESHEET)
        label.setWordWrap(True)
        return label
    
    # ===== Геттеры =====
    
    @property
    def icon_label(self) -> QLabel:
        """
        Возвращает виджет иконки.
        
        Returns:
            QLabel: Виджет с иконкой
        """
        return self._icon_label
    
    @property
    def title_label(self) -> QLabel:
        """
        Возвращает виджет заголовка.
        
        Returns:
            QLabel: Виджет с заголовком
        """
        return self._title_label
    
    @property
    def status_label(self) -> QLabel:
        """
        Возвращает виджет статуса.
        
        Returns:
            QLabel: Виджет со статусом
        """
        return self._status_label
    
    @property
    def hierarchy_label(self) -> QLabel:
        """
        Возвращает виджет иерархии.
        
        Returns:
            QLabel: Виджет с текстом иерархии
        """
        return self._hierarchy_label
    
    # ===== Публичные методы =====
    
    def set_title(self, title: str) -> None:
        """
        Устанавливает заголовок.
        
        Args:
            title: Текст заголовка
        """
        self._title_label.setText(title)
        log.debug(f"HeaderWidget: заголовок установлен '{title}'")
    
    def set_icon(self, icon: str) -> None:
        """
        Устанавливает иконку.
        
        Args:
            icon: Символ иконки (эмодзи)
        """
        self._icon_label.setText(icon)
        log.debug(f"HeaderWidget: иконка установлена '{icon}'")
    
    def set_status(self, status: str) -> None:
        """
        Устанавливает текст статуса.
        
        Args:
            status: Текст статуса
        """
        self._status_label.setText(status)
        log.debug(f"HeaderWidget: статус установлен '{status}'")
    
    def set_hierarchy(self, hierarchy: str) -> None:
        """
        Устанавливает текст иерархии.
        
        Args:
            hierarchy: Текст иерархии (например, "в составе корпуса...")
        """
        self._hierarchy_label.setText(hierarchy)
        log.debug(f"HeaderWidget: иерархия установлена '{hierarchy}'")
    
    def set_status_style(self, status_code: Optional[str]) -> None:
        """
        Устанавливает стиль статуса в зависимости от кода.
        
        Args:
            status_code: Код статуса ('free', 'occupied', 'reserved', 'maintenance' или None)
        """
        style = self._STATUS_STYLES.get(status_code, self._STATUS_DEFAULT_STYLE)
        self._status_label.setStyleSheet(style)
        
        status_text = status_code if status_code else "default"
        log.debug(f"HeaderWidget: стиль статуса '{status_text}' применён")
    
    def clear(self) -> None:
        """
        Очищает все поля шапки.
        """
        self._title_label.setText("")
        self._icon_label.setText("🏢")  # Возвращаем иконку по умолчанию
        self._status_label.setText("")
        self._status_label.setStyleSheet(self._STATUS_DEFAULT_STYLE)
        self._hierarchy_label.setText("")
        
        log.debug("HeaderWidget: очищен")
    
    # ===== Методы для кастомизации =====
    
    def set_status_style_custom(self, stylesheet: str) -> None:
        """
        Устанавливает произвольный стиль для статуса.
        
        Args:
            stylesheet: QSS строка со стилями
        """
        self._status_label.setStyleSheet(stylesheet)
        log.debug("HeaderWidget: применён пользовательский стиль статуса")
		
# client/src/ui/details/info_grid.py
"""
Сетка с полями информации для панели деталей.
Предоставляет гибкую систему отображения пар "Лейбл: Значение"
с возможностью динамического показа/скрытия полей.
"""
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtCore import Qt
from typing import Dict, List, Optional, Tuple

from src.utils.logger import get_logger
log = get_logger(__name__)


class InfoGrid(QWidget):
    """
    Сетка для отображения информации в формате "Лейбл: Значение".
    
    Особенности:
    - Динамическое создание всех возможных полей
    - Возможность показа только нужных полей через show_only()
    - Автоматическая очистка значений через clear_all()
    - Поддержка переноса текста и выделения мышью
    - Получение списка видимых полей для тестирования
    """
    
    # ===== Константы =====
    
    # Определения всех возможных полей: (ключ, текст_лейбла)
    _FIELD_DEFINITIONS: List[Tuple[str, str]] = [
        ("address", "Адрес:"),
        ("owner", "Владелец:"),
        ("tenant", "Арендатор:"),
        ("description", "Описание:"),
        ("plan", "Планировка:"),
        ("type", "Тип:"),
        ("contract", "Договор:"),
        ("valid_until", "Действует до:"),
        ("rent", "Арендная плата:"),
    ]
    """Список всех возможных полей для отображения"""
    
    # Стили для лейблов
    _LABEL_STYLESHEET = "font-weight: bold; color: #666666;"
    """Стиль для текста лейблов"""
    
    _PLACEHOLDER_TEXT = "—"
    """Текст-заполнитель для пустых значений"""
    
    # ===== Константы layout =====
    _VERTICAL_SPACING = 8
    """Вертикальный отступ между строками в пикселях"""
    
    _HORIZONTAL_SPACING = 20
    """Горизонтальный отступ между лейблом и значением в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует сетку информации.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация данных
        self._fields: Dict[str, QLabel] = {}
        self._labels: Dict[str, QLabel] = {}
        
        # Создание UI
        self._init_grid()
        self._create_all_fields()
        
        log.debug("InfoGrid: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_grid(self) -> None:
        """
        Инициализирует сетку QGridLayout с базовыми настройками.
        """
        self._grid = QGridLayout(self)
        self._grid.setVerticalSpacing(self._VERTICAL_SPACING)
        self._grid.setHorizontalSpacing(self._HORIZONTAL_SPACING)
        self._grid.setColumnStretch(1, 1)  # Колонка со значениями растягивается
        
        log.debug("InfoGrid: layout инициализирован")
    
    def _create_all_fields(self) -> None:
        """
        Создаёт все предопределённые поля из _FIELD_DEFINITIONS.
        Для каждого поля создаётся пара (лейбл, значение).
        """
        for row, (key, label_text) in enumerate(self._FIELD_DEFINITIONS):
            self._create_field_row(row, key, label_text)
        
        log.debug(f"InfoGrid: создано {len(self._FIELD_DEFINITIONS)} полей")
    
    def _create_field_row(self, row: int, key: str, label_text: str) -> None:
        """
        Создаёт одну строку с лейблом и полем значения.
        
        Args:
            row: Номер строки в сетке
            key: Ключ поля для идентификации
            label_text: Текст лейбла
        """
        # Создаём лейбл
        label_widget = QLabel(label_text)
        label_widget.setStyleSheet(self._LABEL_STYLESHEET)
        label_widget.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        # Создаём поле значения
        value_widget = QLabel(self._PLACEHOLDER_TEXT)
        value_widget.setWordWrap(True)
        value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Добавляем в сетку
        self._grid.addWidget(label_widget, row, 0)
        self._grid.addWidget(value_widget, row, 1)
        
        # Сохраняем для доступа по ключу
        self._labels[key] = label_widget
        self._fields[key] = value_widget
    
    # ===== Геттеры =====
    
    @property
    def fields(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь всех полей значений.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_значения}
        """
        return self._fields.copy()
    
    @property
    def labels(self) -> Dict[str, QLabel]:
        """
        Возвращает словарь всех лейблов.
        
        Returns:
            Dict[str, QLabel]: Словарь {ключ: виджет_лейбла}
        """
        return self._labels.copy()
    
    @property
    def grid_layout(self) -> QGridLayout:
        """
        Возвращает сетку layout для дополнительной настройки.
        
        Returns:
            QGridLayout: Сетка расположения
        """
        return self._grid
    
    # ===== Публичные методы управления полями =====
    
    def clear_all(self) -> None:
        """
        Очищает все поля, устанавливая текст-заполнитель.
        """
        for field in self._fields.values():
            field.setText(self._PLACEHOLDER_TEXT)
        
        log.debug("InfoGrid: все поля очищены")
    
    def set_field(self, key: str, value: Optional[str]) -> None:
        """
        Устанавливает значение для указанного поля.
        
        Args:
            key: Ключ поля
            value: Новое значение (None или пустая строка заменяются на заполнитель)
        """
        if key not in self._fields:
            log.warning(f"InfoGrid: попытка установить неизвестное поле '{key}'")
            return
        
        # Проверяем значение
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self._fields[key].setText(self._PLACEHOLDER_TEXT)
            log.debug(f"InfoGrid: поле '{key}' очищено")
        else:
            self._fields[key].setText(str(value))
            log.debug(f"InfoGrid: поле '{key}' = '{value[:50]}...'")
    
    def show_only(self, *keys: str) -> None:
        """
        Показывает только указанные поля, скрывая все остальные.
        
        Args:
            *keys: Ключи полей, которые нужно показать
        """
        # Сначала скрываем все поля
        for key in self._fields:
            self._fields[key].setVisible(False)
            self._labels[key].setVisible(False)
        
        # Показываем только нужные
        visible_count = 0
        for key in keys:
            if key in self._fields:
                self._fields[key].setVisible(True)
                self._labels[key].setVisible(True)
                visible_count += 1
            else:
                log.warning(f"InfoGrid: попытка показать неизвестное поле '{key}'")
        
        # Логируем результат
        visible_fields = self.get_visible_fields()
        log.debug(f"InfoGrid: показано {visible_count} полей: {sorted(visible_fields)}")
    
    def show_all(self) -> None:
        """
        Показывает все поля (для отладки или специальных режимов).
        """
        for key in self._fields:
            self._fields[key].setVisible(True)
            self._labels[key].setVisible(True)
        
        log.debug("InfoGrid: показаны все поля")
    
    def hide_all(self) -> None:
        """
        Скрывает все поля.
        """
        for key in self._fields:
            self._fields[key].setVisible(False)
            self._labels[key].setVisible(False)
        
        log.debug("InfoGrid: скрыты все поля")
    
    # ===== Методы для проверки состояния =====
    
    def get_visible_fields(self) -> List[str]:
        """
        Возвращает список ключей видимых в данный момент полей.
        
        Returns:
            List[str]: Список ключей видимых полей
        """
        visible = [
            key for key, widget in self._fields.items()
            if widget.isVisible()
        ]
        return visible
    
    def is_field_visible(self, key: str) -> bool:
        """
        Проверяет, видимо ли указанное поле.
        
        Args:
            key: Ключ поля
            
        Returns:
            bool: True если поле видимо
        """
        if key not in self._fields:
            return False
        return self._fields[key].isVisible()
    
    def get_field_value(self, key: str) -> str:
        """
        Возвращает текущее значение поля.
        
        Args:
            key: Ключ поля
            
        Returns:
            str: Текст поля или пустая строка, если поле не найдено
        """
        if key not in self._fields:
            return ""
        return self._fields[key].text()
    
    # ===== Методы для тестирования =====
    
    def get_all_field_keys(self) -> List[str]:
        """
        Возвращает список всех возможных ключей полей.
        
        Returns:
            List[str]: Список всех ключей
        """
        return [key for key, _ in self._FIELD_DEFINITIONS]
    
    def get_field_count(self) -> int:
        """
        Возвращает общее количество полей.
        
        Returns:
            int: Количество полей
        """
        return len(self._fields)
		
# client/src/ui/details/placeholder.py
"""
Виджет-заглушка для панели детальной информации.
Отображается, когда в дереве не выбран ни один объект,
предлагая пользователю сделать выбор.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional

from src.utils.logger import get_logger
log = get_logger(__name__)


class PlaceholderWidget(QWidget):
    """
    Виджет-заглушка, отображаемый при отсутствии выбранного объекта.
    
    Содержит информационное сообщение с иконкой и стилизованной рамкой.
    Занимает всю доступную область правой панели.
    """
    
    # ===== Константы =====
    
    # Текст заглушки (можно менять для разных языков)
    _DEFAULT_TEXT = "🔍 Выберите объект в дереве слева\nдля просмотра детальной информации"
    """Текст по умолчанию для заглушки"""
    
    # Стили для текста
    _LABEL_STYLESHEET = """
        QLabel {
            color: #999999;
            font-size: 14px;
            padding: 40px;
            border: 2px dashed #cccccc;
            border-radius: 10px;
            margin: 20px;
        }
    """
    """Стили для текстовой метки"""
    
    # ===== Константы размеров =====
    _PADDING = 40
    """Внутренний отступ в пикселях"""
    
    _MARGIN = 20
    """Внешний отступ в пикселях"""
    
    _BORDER_WIDTH = 2
    """Толщина пунктирной рамки в пикселях"""
    
    _BORDER_RADIUS = 10
    """Радиус скругления рамки в пикселях"""
    
    _FONT_SIZE = 14
    """Размер шрифта в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет-заглушку.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация UI
        self._init_ui()
        
        log.debug("PlaceholderWidget: инициализирован")
    
    # ===== Приватные методы =====
    
    def _init_ui(self) -> None:
        """
        Инициализирует пользовательский интерфейс заглушки.
        Создаёт layout и текстовую метку с сообщением.
        """
        # Создаём layout с центрированием
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Создаём текстовую метку
        self._message_label = self._create_message_label()
        
        # Добавляем метку в layout
        layout.addWidget(self._message_label)
        
        log.debug("PlaceholderWidget: UI инициализирован")
    
    def _create_message_label(self) -> QLabel:
        """
        Создаёт и настраивает текстовую метку с сообщением.
        
        Returns:
            QLabel: Настроенная текстовая метка
        """
        label = QLabel(self._DEFAULT_TEXT)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)  # Разрешаем перенос строк
        label.setStyleSheet(self._LABEL_STYLESHEET)
        
        return label
    
    # ===== Геттеры и сеттеры =====
    
    @property
    def message_label(self) -> QLabel:
        """
        Возвращает виджет текстовой метки.
        
        Returns:
            QLabel: Виджет с текстом сообщения
        """
        return self._message_label
    
    @property
    def current_text(self) -> str:
        """
        Возвращает текущий текст заглушки.
        
        Returns:
            str: Текст сообщения
        """
        return self._message_label.text()
    
    def set_message(self, text: str) -> None:
        """
        Устанавливает новый текст для заглушки.
        
        Args:
            text: Новый текст сообщения
        """
        self._message_label.setText(text)
        log.debug(f"PlaceholderWidget: текст изменён на '{text}'")
    
    def reset_to_default(self) -> None:
        """
        Сбрасывает текст заглушки к значению по умолчанию.
        """
        self._message_label.setText(self._DEFAULT_TEXT)
        log.debug("PlaceholderWidget: текст сброшен к значению по умолчанию")
    
    # ===== Публичные методы =====
    
    def show_message(self, message: str) -> None:
        """
        Показывает пользовательское сообщение в заглушке.
        
        Args:
            message: Текст сообщения для отображения
        """
        self.set_message(message)
        self.show()
        log.info(f"PlaceholderWidget: показано сообщение '{message}'")
    
    def show_default(self) -> None:
        """
        Показывает стандартное сообщение-заглушку.
        """
        self.reset_to_default()
        self.show()
        log.debug("PlaceholderWidget: показано сообщение по умолчанию")
    
    # ===== Методы для кастомизации внешнего вида =====
    
    def set_style_property(self, property_name: str, value: str) -> None:
        """
        Устанавливает свойство стиля для метки.
        
        Args:
            property_name: Имя свойства (например, "color", "font-size")
            value: Значение свойства
        """
        current_style = self._message_label.styleSheet()
        # Простая замена - для сложных случаев лучше использовать QSS парсер
        new_style = f"{property_name}: {value};"
        
        # Добавляем новое свойство в существующий стиль
        if current_style:
            # Удаляем старое значение если есть
            lines = current_style.split(';')
            filtered_lines = [line for line in lines if property_name not in line]
            new_style = ';'.join(filtered_lines) + ';' + new_style
        else:
            new_style = self._LABEL_STYLESHEET + ';' + new_style
        
        self._message_label.setStyleSheet(new_style)
        log.debug(f"PlaceholderWidget: стиль обновлён - {property_name}: {value}")
		
# client/src/ui/details/tabs.py
"""
Модуль для создания и управления вкладками панели детальной информации.
Предоставляет виджет с тремя предопределёнными вкладками:
- Физика (статистика по физическим объектам)
- Юрики (информация о юридических лицах)
- Пожарка (данные пожарной безопасности)
"""
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional, List, Tuple

from src.utils.logger import get_logger
log = get_logger(__name__)


class DetailsTabs(QTabWidget):
    """
    Виджет вкладок для панели детальной информации.
    
    Содержит три предопределённые вкладки:
    - 📊 Физика - для отображения физических характеристик
    - ⚖️ Юрики - для информации о юридических лицах и арендаторах
    - 🔥 Пожарка - для данных пожарной безопасности и датчиков
    
    Каждая вкладка в текущей версии содержит заглушку с пояснительным текстом.
    В будущем будет заменена на реальные виджеты с данными.
    """
    
    # ===== Константы =====
    
    # Определения вкладок: (индекс, название, текст заглушки, иконка)
    _TABS_DEFINITIONS: List[Tuple[str, str, str]] = [
        ("📊 Физика", "Физика", "📊 Статистика по физике будет здесь"),
        ("⚖️ Юрики", "Юрики", "⚖️ Информация о юридических лицах будет здесь"),
        ("🔥 Пожарка", "Пожарка", "🔥 Данные пожарной безопасности будут здесь"),
    ]
    """Список кортежей (текст_вкладки, внутреннее_имя, текст_заглушки)"""
    
    # Стили для виджета вкладок
    _TAB_WIDGET_STYLESHEET = """
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            padding: 5px;
            margin-top: 5px;
        }
        QTabBar::tab {
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #2196F3;
        }
    """
    
    # Стили для текста-заглушки
    _PLACEHOLDER_STYLESHEET = """
        QLabel {
            color: #808080;
            padding: 40px;
            font-size: 12px;
        }
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет вкладок.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Настройка внешнего вида
        self._setup_appearance()
        
        # Создание вкладок
        self._create_all_tabs()
        
        log.debug("DetailsTabs: инициализирован")
    
    # ===== Приватные методы =====
    
    def _setup_appearance(self) -> None:
        """
        Настраивает внешний вид виджета вкладок.
        Применяет стили из констант.
        """
        self.setStyleSheet(self._TAB_WIDGET_STYLESHEET)
        log.debug("DetailsTabs: стили применены")
    
    def _create_all_tabs(self) -> None:
        """
        Создаёт все предопределённые вкладки.
        Для каждой вкладки из _TABS_DEFINITIONS создаёт виджет-заглушку.
        """
        for tab_text, internal_name, placeholder_text in self._TABS_DEFINITIONS:
            tab_widget = self._create_placeholder_tab(placeholder_text, internal_name)
            self.addTab(tab_widget, tab_text)
            
        log.info(f"DetailsTabs: создано {len(self._TABS_DEFINITIONS)} вкладок")
    
    def _create_placeholder_tab(self, text: str, internal_name: str) -> QWidget:
        """
        Создаёт виджет-заглушку для вкладки.
        
        Args:
            text: Текст для отображения в заглушке
            internal_name: Внутреннее имя вкладки (для логирования)
            
        Returns:
            QWidget: Виджет с заглушкой
        """
        # Создаём контейнер для вкладки
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Создаём текст-заглушку
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(self._PLACEHOLDER_STYLESHEET)
        
        # Добавляем в layout
        layout.addWidget(label)
        
        log.debug(f"DetailsTabs: создана вкладка-заглушка '{internal_name}'")
        
        return widget
    
    # ===== Публичные методы =====
    
    def set_tab_enabled(self, index: int, enabled: bool = True) -> None:
        """
        Включает или отключает вкладку по индексу.
        
        Args:
            index: Индекс вкладки (0, 1, 2)
            enabled: True - включить, False - отключить
        """
        self.setTabEnabled(index, enabled)
        status = "включена" if enabled else "отключена"
        log.debug(f"DetailsTabs: вкладка {index} {status}")
    
    def get_tab_count(self) -> int:
        """
        Возвращает количество вкладок.
        
        Returns:
            int: Количество вкладок
        """
        return self.count()
    
    def get_current_tab_index(self) -> int:
        """
        Возвращает индекс текущей выбранной вкладки.
        
        Returns:
            int: Индекс текущей вкладки
        """
        return self.currentIndex()
    
    def get_current_tab_text(self) -> str:
        """
        Возвращает текст текущей выбранной вкладки.
        
        Returns:
            str: Текст текущей вкладки или пустая строка
        """
        index = self.currentIndex()
        if 0 <= index < self.count():
            return self.tabText(index)
        return ""
    
    # ===== Методы для будущего расширения =====
    
    def set_tab_widget(self, index: int, widget: QWidget) -> None:
        """
        Заменяет виджет в указанной вкладке на новый.
        
        Args:
            index: Индекс вкладки
            widget: Новый виджет для вкладки
        """
        # Сохраняем текущий текст вкладки
        tab_text = self.tabText(index)
        
        # Удаляем старый виджет и добавляем новый
        self.removeTab(index)
        self.insertTab(index, widget, tab_text)
        
        log.info(f"DetailsTabs: виджет вкладки {index} заменён")
    
    def update_tab_text(self, index: int, new_text: str) -> None:
        """
        Обновляет текст указанной вкладки.
        
        Args:
            index: Индекс вкладки
            new_text: Новый текст для вкладки
        """
        if 0 <= index < self.count():
            self.setTabText(index, new_text)
            log.debug(f"DetailsTabs: текст вкладки {index} изменён на '{new_text}'")
			
# client/src/ui/main_window/components/__init__.py
"""
Компоненты пользовательского интерфейса главного окна.

Предоставляет:
- CentralWidget: центральный виджет с разделителем
- Toolbar: панель инструментов с меню обновления
- StatusBar: строка статуса с индикатором соединения
"""
from src.ui.main_window.components.central_widget import CentralWidget
from src.ui.main_window.components.toolbar import Toolbar
from src.ui.main_window.components.status_bar import StatusBar

__all__ = [
    "CentralWidget",
    "Toolbar",
    "StatusBar"
]

# client/src/ui/main_window/components/central_widget.py
"""
Модуль центрального виджета с разделителем.
Создаёт область для размещения дерева и панели деталей.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from typing import Optional

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class CentralWidget:
    """
    Компонент центрального виджета с разделителем.
    
    Предоставляет:
    - Создание центрального виджета
    - Настройку разделителя (QSplitter)
    - Методы для добавления виджетов в разделитель
    """
    
    # ===== Константы =====
    _SPLITTER_HANDLE_WIDTH = 5
    """Ширина разделителя в пикселях"""
    
    _SPLITTER_STYLE = """
        QSplitter::handle {
            background-color: #c0c0c0;
        }
        QSplitter::handle:hover {
            background-color: #808080;
        }
    """
    """Стили для разделителя"""
    
    _DEFAULT_SIZES = [300, 700]
    """Начальные размеры частей разделителя [левая, правая]"""
    
    def __init__(self, parent: QWidget) -> None:
        """
        Инициализирует центральный виджет.
        
        Args:
            parent: Родительский виджет (MainWindow)
        """
        self._parent = parent
        self._central_widget: Optional[QWidget] = None
        self._splitter: Optional[QSplitter] = None
        
        self._create_central_widget()
        
        log.debug("CentralWidget: инициализирован")
    
    # ===== Приватные методы =====
    
    def _create_central_widget(self) -> None:
        """Создаёт и настраивает центральный виджет."""
        # Создаём центральный виджет
        self._central_widget = QWidget(self._parent)
        self._central_widget.setVisible(True)
        self._parent.setCentralWidget(self._central_widget)
        
        # Создаём layout
        layout = QHBoxLayout(self._central_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Создаём разделитель
        self._create_splitter()
        layout.addWidget(self._splitter)
        
        log.debug("CentralWidget: центральный виджет создан")
    
    def _create_splitter(self) -> None:
        """Создаёт и настраивает разделитель."""
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setHandleWidth(self._SPLITTER_HANDLE_WIDTH)
        self._splitter.setVisible(True)
        self._splitter.setStyleSheet(self._SPLITTER_STYLE)
        
        log.debug("CentralWidget: разделитель создан")
    
    # ===== Геттеры =====
    
    @property
    def central_widget(self) -> QWidget:
        """
        Возвращает центральный виджет.
        
        Returns:
            QWidget: Центральный виджет
        """
        return self._central_widget
    
    @property
    def splitter(self) -> QSplitter:
        """
        Возвращает разделитель.
        
        Returns:
            QSplitter: Разделитель
        """
        return self._splitter
    
    # ===== Публичные методы =====
    
    def add_widgets(self, left_widget: QWidget, right_widget: QWidget) -> None:
        """
        Добавляет виджеты в разделитель.
        
        Args:
            left_widget: Левый виджет (дерево)
            right_widget: Правый виджет (панель деталей)
        """
        self._splitter.addWidget(left_widget)
        self._splitter.addWidget(right_widget)
        self._splitter.setSizes(self._DEFAULT_SIZES)
        
        log.debug(f"CentralWidget: виджеты добавлены в разделитель")
        log.debug(f"  splitter содержит {self._splitter.count()} виджетов")
    
    def is_visible(self) -> bool:
        """
        Проверяет видимость центрального виджета и разделителя.
        
        Returns:
            bool: True если все компоненты видимы
        """
        return (self._central_widget.isVisible() and 
                self._splitter.isVisible())
				
# client/src/ui/main_window/components/status_bar.py
"""
Модуль строки статуса главного окна.
Отображает текущее состояние приложения и соединения с сервером.
"""
from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtCore import QTimer
from typing import Optional

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class StatusBar:
    """
    Компонент строки статуса.
    
    Предоставляет:
    - Отображение сообщений о процессе
    - Постоянный индикатор соединения
    - Таймер для автоматического скрытия сообщений
    """
    
    # ===== Константы =====
    _DEFAULT_MESSAGE = "Готов к работе"
    """Сообщение по умолчанию"""
    
    _CONNECTION_CHECKING = "⚪ Соединение..."
    """Текст индикатора соединения при проверке"""
    
    _CONNECTION_ONLINE = "✅ Сервер доступен"
    """Текст индикатора при успешном соединении"""
    
    _CONNECTION_OFFLINE = "❌ Сервер недоступен"
    """Текст индикатора при отсутствии соединения"""
    
    _ONLINE_STYLE = "color: green;"
    """Стиль для статуса онлайн"""
    
    _OFFLINE_STYLE = "color: red;"
    """Стиль для статуса офлайн"""
    
    _MESSAGE_TIMEOUT_MS = 3000
    """Время отображения временных сообщений в миллисекундах"""
    
    def __init__(self, parent_window) -> None:
        """
        Инициализирует строку статуса.
        
        Args:
            parent_window: Родительское окно (MainWindow)
        """
        self._parent = parent_window
        self._status_bar: Optional[QStatusBar] = None
        self._connection_label: Optional[QLabel] = None
        self._message_timer: Optional[QTimer] = None
        
        self._create_status_bar()
        self._setup_message_timer()
        
        log.debug("StatusBar: инициализирована")
    
    # ===== Приватные методы =====
    
    def _create_status_bar(self) -> None:
        """Создаёт и настраивает строку статуса."""
        self._status_bar = QStatusBar()
        self._parent.setStatusBar(self._status_bar)
        self._status_bar.showMessage(self._DEFAULT_MESSAGE)
        
        self._create_connection_indicator()
        
        log.debug("StatusBar: строка статуса создана")
    
    def _create_connection_indicator(self) -> None:
        """Создаёт постоянный индикатор соединения."""
        self._connection_label = QLabel(self._CONNECTION_CHECKING)
        self._status_bar.addPermanentWidget(self._connection_label)
        
        log.debug("StatusBar: индикатор соединения создан")
    
    def _setup_message_timer(self) -> None:
        """Настраивает таймер для автоматического скрытия сообщений."""
        self._message_timer = QTimer()
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._clear_temporary_message)
        
        log.debug("StatusBar: таймер сообщений настроен")
    
    def _clear_temporary_message(self) -> None:
        """Очищает временное сообщение и возвращает стандартное."""
        self._status_bar.showMessage(self._DEFAULT_MESSAGE)
        log.debug("StatusBar: временное сообщение очищено")
    
    # ===== Геттеры =====
    
    @property
    def status_bar(self) -> QStatusBar:
        """Возвращает виджет строки статуса."""
        return self._status_bar
    
    @property
    def connection_label(self) -> QLabel:
        """Возвращает метку индикатора соединения."""
        return self._connection_label
    
    # ===== Публичные методы =====
    
    def show_message(self, message: str, timeout: int = 0) -> None:
        """
        Показывает сообщение в строке статуса.
        
        Args:
            message: Текст сообщения
            timeout: Время отображения в мс (0 - постоянно)
        """
        self._status_bar.showMessage(message, timeout)
        log.debug(f"StatusBar: показано сообщение '{message}'")
    
    def show_temporary_message(self, message: str) -> None:
        """
        Показывает временное сообщение (на 3 секунды).
        
        Args:
            message: Текст сообщения
        """
        self._status_bar.showMessage(message, self._MESSAGE_TIMEOUT_MS)
        log.debug(f"StatusBar: показано временное сообщение '{message}'")
    
    def set_connection_online(self) -> None:
        """Устанавливает индикатор соединения в состояние 'онлайн'."""
        self._connection_label.setText(self._CONNECTION_ONLINE)
        self._connection_label.setStyleSheet(self._ONLINE_STYLE)
        log.debug("StatusBar: соединение ONLINE")
    
    def set_connection_offline(self) -> None:
        """Устанавливает индикатор соединения в состояние 'офлайн'."""
        self._connection_label.setText(self._CONNECTION_OFFLINE)
        self._connection_label.setStyleSheet(self._OFFLINE_STYLE)
        log.debug("StatusBar: соединение OFFLINE")
    
    def set_connection_checking(self) -> None:
        """Устанавливает индикатор соединения в состояние 'проверка'."""
        self._connection_label.setText(self._CONNECTION_CHECKING)
        self._connection_label.setStyleSheet("")
        log.debug("StatusBar: проверка соединения")
    
    def clear(self) -> None:
        """Очищает строку статуса до состояния по умолчанию."""
        self._status_bar.showMessage(self._DEFAULT_MESSAGE)
        self.set_connection_checking()
        log.debug("StatusBar: очищена")
		
# client/src/ui/main_window/components/toolbar.py
"""
Модуль панели инструментов главного окна.
Содержит кнопку обновления с меню, индикатор статуса и счётчик объектов.
"""
from PySide6.QtWidgets import QToolBar, QPushButton
from PySide6.QtCore import QSize, Signal, QObject
from PySide6.QtGui import QAction
from typing import Optional

from src.ui.refresh_menu import RefreshMenu
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ToolbarSignals(QObject):
    """Сигналы для панели инструментов."""
    
    refresh_current = Signal()
    """Сигнал обновления текущего узла"""
    
    refresh_visible = Signal()
    """Сигнал обновления всех раскрытых узлов"""
    
    full_reset = Signal()
    """Сигнал полной перезагрузки"""


class Toolbar:
    """
    Компонент панели инструментов.
    
    Предоставляет:
    - Кнопку с меню для трёх уровней обновления
    - Индикатор статуса подключения
    - Счётчик объектов в кэше
    """
    
    # ===== Константы =====
    _ICON_SIZE = 16
    """Размер иконок в пикселях"""
    
    _TOOLBAR_NAME = "Панель инструментов"
    """Название панели инструментов"""
    
    _REFRESH_BUTTON_TEXT = "🔄 Обновить"
    """Текст кнопки обновления"""
    
    _REFRESH_BUTTON_TOOLTIP = "Выберите тип обновления (F5 - меню)"
    """Подсказка для кнопки обновления"""
    
    _STATUS_CHECKING = "⚪ Проверка..."
    """Текст при проверке статуса"""
    
    _COUNTER_DEFAULT = "📊 Объектов: -"
    """Текст счётчика по умолчанию"""
    
    def __init__(self, parent_window) -> None:
        """
        Инициализирует панель инструментов.
        
        Args:
            parent_window: Родительское окно (MainWindow)
        """
        self._parent = parent_window
        self._toolbar: Optional[QToolBar] = None
        self._refresh_menu: Optional[RefreshMenu] = None
        self._status_action: Optional[QAction] = None
        self._counter_action: Optional[QAction] = None
        
        self.signals = ToolbarSignals()
        
        self._create_toolbar()
        
        log.debug("Toolbar: инициализирован")
    
    # ===== Приватные методы =====
    
    def _create_toolbar(self) -> None:
        """Создаёт и настраивает панель инструментов."""
        self._toolbar = QToolBar(self._TOOLBAR_NAME, self._parent)
        self._toolbar.setMovable(False)
        self._toolbar.setIconSize(QSize(self._ICON_SIZE, self._ICON_SIZE))
        self._parent.addToolBar(self._toolbar)
        
        self._create_refresh_button()
        self._create_status_indicator()
        self._create_counter()
        
        log.debug("Toolbar: панель инструментов создана")
    
    def _create_refresh_button(self) -> None:
        """Создаёт кнопку обновления с выпадающим меню."""
        # Создаём меню обновления
        self._refresh_menu = RefreshMenu(self._parent)
        
        # Подключаем сигналы меню
        self._refresh_menu.refresh_current.connect(self.signals.refresh_current)
        self._refresh_menu.refresh_visible.connect(self.signals.refresh_visible)
        self._refresh_menu.full_reset.connect(self.signals.full_reset)
        
        # Создаём кнопку
        refresh_button = QPushButton(self._REFRESH_BUTTON_TEXT)
        refresh_button.setMenu(self._refresh_menu)
        refresh_button.setToolTip(self._REFRESH_BUTTON_TOOLTIP)
        
        self._toolbar.addWidget(refresh_button)
        self._toolbar.addSeparator()
        
        log.debug("Toolbar: кнопка обновления создана")
    
    def _create_status_indicator(self) -> None:
        """Создаёт индикатор статуса подключения."""
        self._status_action = QAction(self._STATUS_CHECKING, self._parent)
        self._status_action.setEnabled(False)
        self._toolbar.addAction(self._status_action)
        
        log.debug("Toolbar: индикатор статуса создан")
    
    def _create_counter(self) -> None:
        """Создаёт счётчик объектов."""
        self._counter_action = QAction(self._COUNTER_DEFAULT, self._parent)
        self._counter_action.setEnabled(False)
        self._toolbar.addAction(self._counter_action)
        
        log.debug("Toolbar: счётчик объектов создан")
    
    # ===== Геттеры =====
    
    @property
    def toolbar(self) -> QToolBar:
        """Возвращает виджет панели инструментов."""
        return self._toolbar
    
    @property
    def refresh_menu(self) -> RefreshMenu:
        """Возвращает меню обновления."""
        return self._refresh_menu
    
    @property
    def status_action(self) -> QAction:
        """Возвращает действие индикатора статуса."""
        return self._status_action
    
    @property
    def counter_action(self) -> QAction:
        """Возвращает действие счётчика объектов."""
        return self._counter_action
    
    # ===== Публичные методы =====
    
    def set_status_online(self) -> None:
        """Устанавливает статус 'Онлайн'."""
        self._status_action.setText("✅ Онлайн")
        log.debug("Toolbar: статус изменён на ONLINE")
    
    def set_status_offline(self) -> None:
        """Устанавливает статус 'Офлайн'."""
        self._status_action.setText("❌ Офлайн")
        log.debug("Toolbar: статус изменён на OFFLINE")
    
    def set_status_checking(self) -> None:
        """Устанавливает статус 'Проверка...'."""
        self._status_action.setText(self._STATUS_CHECKING)
        log.debug("Toolbar: статус изменён на CHECKING")
    
    def update_counter(self, count: int) -> None:
        """
        Обновляет счётчик объектов.
        
        Args:
            count: Количество объектов в кэше
        """
        self._counter_action.setText(f"📊 В кэше: {count} объектов")
        log.debug(f"Toolbar: счётчик обновлён: {count}")
		
# client/src/ui/main_window/controllers/__init__.py
"""
Контроллеры логики главного окна.

Предоставляет:
- RefreshController: управление обновлением данных (F5, Ctrl+F5, Ctrl+Shift+F5)
- DataController: обработка событий загрузки данных
- ConnectionController: проверка соединения с сервером
"""
from src.ui.main_window.controllers.refresh_controller import RefreshController
from src.ui.main_window.controllers.data_controller import DataController
from src.ui.main_window.controllers.connection_controller import ConnectionController

__all__ = [
    "RefreshController",
    "DataController",
    "ConnectionController"
]

# client/src/ui/main_window/controllers/connection_controller.py
"""
Контроллер проверки соединения с сервером.
Периодически проверяет доступность бекенда и обновляет статус.
"""
from PySide6.QtCore import QObject, QTimer, Slot

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ConnectionController(QObject):
    """
    Контроллер проверки соединения.
    
    Периодически проверяет доступность сервера и обновляет
    индикаторы статуса в панели инструментов и строке статуса.
    """
    
    # ===== Константы =====
    _CHECK_INTERVAL_MS = 30000
    """Интервал проверки соединения в миллисекундах (30 секунд)"""
    
    _INITIAL_CHECK_DELAY_MS = 1000
    """Задержка перед первой проверкой в миллисекундах"""
    
    def __init__(self, tree_view, toolbar, status_bar) -> None:
        """
        Инициализирует контроллер соединения.
        
        Args:
            tree_view: Виджет дерева (TreeView) для доступа к API
            toolbar: Панель инструментов (Toolbar)
            status_bar: Строка статуса (StatusBar)
        """
        super().__init__()
        
        self._tree_view = tree_view
        self._toolbar = toolbar
        self._status_bar = status_bar
        self._timer: QTimer = QTimer()
        
        self._setup_timer()
        
        log.debug("ConnectionController: инициализирован")
    
    # ===== Приватные методы =====
    
    def _setup_timer(self) -> None:
        """Настраивает таймер для периодической проверки."""
        self._timer.timeout.connect(self.check_connection)
        self._timer.start(self._CHECK_INTERVAL_MS)
        
        # Первая проверка с задержкой
        QTimer.singleShot(self._INITIAL_CHECK_DELAY_MS, self.check_connection)
        
        log.debug("ConnectionController: таймер настроен")
    
    def _is_connected(self) -> bool:
        """
        Проверяет доступность сервера.
        
        Returns:
            bool: True если сервер доступен
        """
        try:
            if hasattr(self._tree_view.api_client, 'check_connection'):
                return self._tree_view.api_client.check_connection()
            else:
                info = self._tree_view.api_client.get_server_info()
                return bool(info and 'message' in info)
        except Exception as error:
            log.debug(f"ConnectionController: ошибка при проверке: {error}")
            return False
    
    # ===== Публичные слоты =====
    
    @Slot()
    def check_connection(self) -> None:
        """Проверяет соединение и обновляет индикаторы."""
        if self._is_connected():
            self._toolbar.set_status_online()
            self._status_bar.set_connection_online()
            log.debug("ConnectionController: сервер доступен")
        else:
            self._toolbar.set_status_offline()
            self._status_bar.set_connection_offline()
            log.debug("ConnectionController: сервер недоступен")
    
    @Slot()
    def stop_checking(self) -> None:
        """Останавливает периодическую проверку."""
        self._timer.stop()
        log.debug("ConnectionController: проверка остановлена")
		
# client/src/ui/main_window/controllers/data_controller.py
"""
Контроллер обработки данных.
Отвечает за обработку сигналов загрузки данных и обновление интерфейса.
"""
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class DataController(QObject):
    """
    Контроллер обработки данных.
    
    Обрабатывает сигналы:
    - data_loading: начало загрузки данных
    - data_loaded: завершение загрузки
    - data_error: ошибка загрузки
    """
    
    def __init__(self, tree_view, status_bar, counter_action) -> None:
        """
        Инициализирует контроллер данных.
        
        Args:
            tree_view: Виджет дерева (TreeView)
            status_bar: Строка статуса (StatusBar)
            counter_action: Действие счётчика объектов (QAction)
        """
        super().__init__()
        
        self._tree_view = tree_view
        self._status_bar = status_bar
        self._counter_action = counter_action
        
        log.debug("DataController: инициализирован")
    
    # ===== Приватные методы =====
    
    def _update_counter(self) -> None:
        """Обновляет счётчик объектов в панели инструментов."""
        if hasattr(self._tree_view, 'cache'):
            stats = self._tree_view.cache.get_stats()
            self._counter_action.setText(f"📊 В кэше: {stats['size']} объектов")
            log.debug(f"DataController: счётчик обновлён: {stats['size']}")
    
    # ===== Публичные слоты =====
    
    @Slot(str, int)
    def on_data_loading(self, node_type: str, node_id: int) -> None:
        """
        Обрабатывает начало загрузки данных.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self._status_bar.show_temporary_message(
            f"📡 Загрузка {node_type} #{node_id}..."
        )
        log.debug(f"DataController: начало загрузки {node_type} #{node_id}")
    
    @Slot(str, int)
    def on_data_loaded(self, node_type: str, node_id: int) -> None:
        """
        Обрабатывает завершение загрузки данных.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self._status_bar.show_temporary_message(
            f"✅ Загружен {node_type} #{node_id}"
        )
        self._update_counter()
        log.debug(f"DataController: загрузка завершена {node_type} #{node_id}")
    
    @Slot(str, int, str)
    def on_data_error(self, node_type: str, node_id: int, error: str) -> None:
        """
        Обрабатывает ошибку загрузки данных.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        self._status_bar.show_temporary_message(
            f"❌ Ошибка загрузки {node_type} #{node_id}"
        )
        
        QMessageBox.warning(
            self._tree_view,
            "Ошибка загрузки",
            f"Не удалось загрузить {node_type} #{node_id}:\n{error}"
        )
        
        log.error(f"Ошибка загрузки {node_type} #{node_id}: {error}")
		
# client/src/ui/main_window/controllers/refresh_controller.py
"""
Контроллер обновления данных.
Управляет тремя уровнями обновления:
- Текущий узел (F5)
- Все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, Slot

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class RefreshController(QObject):
    """
    Контроллер обновления данных.
    
    Обрабатывает запросы на обновление разных уровней:
    - refresh_current: обновление текущего узла
    - refresh_visible: обновление всех раскрытых узлов
    - full_reset: полная перезагрузка с подтверждением
    """
    
    # ===== Константы =====
    _RESET_CONFIRMATION_TITLE = "Подтверждение"
    """Заголовок окна подтверждения"""
    
    _RESET_CONFIRMATION_TEXT = (
        "Вы уверены, что хотите выполнить полную перезагрузку?\n"
        "Все данные будут загружены заново."
    )
    """Текст подтверждения полной перезагрузки"""
    
    def __init__(self, tree_view, status_bar) -> None:
        """
        Инициализирует контроллер обновления.
        
        Args:
            tree_view: Виджет дерева (TreeView)
            status_bar: Строка статуса (StatusBar)
        """
        super().__init__()
        
        self._tree_view = tree_view
        self._status_bar = status_bar
        
        log.debug("RefreshController: инициализирован")
    
    # ===== Приватные методы =====
    
    def _confirm_full_reset(self) -> bool:
        """
        Запрашивает подтверждение полной перезагрузки.
        
        Returns:
            bool: True если пользователь подтвердил
        """
        reply = QMessageBox.question(
            self._tree_view,
            self._RESET_CONFIRMATION_TITLE,
            self._RESET_CONFIRMATION_TEXT,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        confirmed = reply == QMessageBox.Yes
        log.debug(f"RefreshController: подтверждение перезагрузки: {confirmed}")
        
        return confirmed
    
    # ===== Публичные слоты =====
    
    @Slot()
    def refresh_current(self) -> None:
        """Обновляет текущий выбранный узел."""
        selected = self._tree_view.get_selected_node_info()
        
        if selected:
            node_type, node_id, _ = selected
            self._status_bar.show_temporary_message(
                f"🔄 Обновление {node_type} #{node_id}..."
            )
            self._tree_view.refresh_current()
            log.info(f"Обновление текущего узла: {node_type} #{node_id}")
        else:
            self._status_bar.show_temporary_message(
                "⚠️ Нет выбранного узла для обновления"
            )
            log.debug("RefreshController: нет выбранного узла")
    
    @Slot()
    def refresh_visible(self) -> None:
        """Обновляет все раскрытые узлы."""
        self._status_bar.show_temporary_message(
            "🔄 Обновление всех раскрытых узлов..."
        )
        self._tree_view.refresh_visible()
        log.info("Обновление всех раскрытых узлов")
    
    @Slot()
    def full_reset(self) -> None:
        """Выполняет полную перезагрузку после подтверждения."""
        if self._confirm_full_reset():
            self._status_bar.show_temporary_message("🔄 Полная перезагрузка...")
            self._tree_view.full_reset()
            self._status_bar.show_temporary_message("✅ Полная перезагрузка выполнена")
            log.info("Полная перезагрузка выполнена")
			
# client/src/ui/main_window/__init__.py
"""
Пакет главного окна приложения.
Предоставляет компоненты для создания основного интерфейса с деревом и панелью деталей.
"""
from src.ui.main_window.main_window import MainWindow

__all__ = ["MainWindow"]

# client/src/ui/main_window/main_window.py
"""
Главное окно приложения Markoff.
Объединяет все компоненты и контроллеры для создания полноценного интерфейса
с деревом объектов и панелью детальной информации.
"""
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot, QTimer

from src.ui.tree import TreeView
from src.ui.details import DetailsPanel
from src.ui.main_window.components.central_widget import CentralWidget
from src.ui.main_window.components.toolbar import Toolbar
from src.ui.main_window.components.status_bar import StatusBar
from src.ui.main_window.shortcuts import ShortcutManager
from src.ui.main_window.controllers.refresh_controller import RefreshController
from src.ui.main_window.controllers.data_controller import DataController
from src.ui.main_window.controllers.connection_controller import ConnectionController
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    
    Компоновка:
    - Левая часть: дерево объектов (TreeView)
    - Правая часть: информационная панель (DetailsPanel)
    
    Панель инструментов:
    - Кнопка с меню для выбора типа обновления
    - Индикатор статуса подключения
    - Счётчик загруженных объектов
    
    Горячие клавиши:
    - F5: обновить текущий узел
    - Ctrl+F5: обновить все раскрытые узлы
    - Ctrl+Shift+F5: полная перезагрузка
    """
    
    # ===== Константы =====
    _WINDOW_TITLE = "Markoff - Управление помещениями"
    """Заголовок окна"""
    
    _MINIMUM_WIDTH = 1000
    """Минимальная ширина окна в пикселях"""
    
    _MINIMUM_HEIGHT = 700
    """Минимальная высота окна в пикселях"""
    
    def __init__(self) -> None:
        """Инициализирует главное окно."""
        super().__init__()
        
        # Настройка окна
        self._setup_window()
        
        # Создание компонентов UI
        self._create_components()
        
        # Создание контроллеров
        self._create_controllers()
        
        # Подключение сигналов
        self._connect_signals()
        
        log.success("MainWindow: создано")
    
    # ===== Приватные методы инициализации =====
    
    def _setup_window(self) -> None:
        """Настраивает параметры главного окна."""
        self.setWindowTitle(self._WINDOW_TITLE)
        self.setMinimumSize(self._MINIMUM_WIDTH, self._MINIMUM_HEIGHT)
        log.debug("MainWindow: параметры окна установлены")
    
    def _create_components(self) -> None:
        """Создаёт все компоненты пользовательского интерфейса."""
        # Создаём компоненты
        self._tree_view = TreeView(self)
        self._details_panel = DetailsPanel(self)
        
        # Создаём центральный виджет с разделителем
        self._central = CentralWidget(self)
        self._central.add_widgets(self._tree_view, self._details_panel)
        
        # Создаём панель инструментов
        self._toolbar = Toolbar(self)
        
        # Создаём строку статуса
        self._status_bar = StatusBar(self)
        
        # Создаём менеджер горячих клавиш
        self._shortcuts = ShortcutManager(self)
        
        log.debug("MainWindow: все компоненты созданы")
    
    def _create_controllers(self) -> None:
        """Создаёт все контроллеры для обработки логики."""
        # Контроллер обновления
        self._refresh_controller = RefreshController(
            self._tree_view,
            self._status_bar
        )
        
        # Контроллер данных
        self._data_controller = DataController(
            self._tree_view,
            self._status_bar,
            self._toolbar.counter_action
        )
        
        # Контроллер соединения
        self._connection_controller = ConnectionController(
            self._tree_view,
            self._toolbar,
            self._status_bar
        )
        
        log.debug("MainWindow: все контроллеры созданы")
    
    def _connect_signals(self) -> None:
        """Подключает все сигналы между компонентами."""
        
        # Сигнал выбора элемента в дереве -> панель деталей
        self._tree_view.item_selected.connect(
            self._details_panel.show_item_details
        )
        
        # Сигналы загрузки данных -> контроллер данных
        self._tree_view.data_loading.connect(
            self._data_controller.on_data_loading
        )
        self._tree_view.data_loaded.connect(
            self._data_controller.on_data_loaded
        )
        self._tree_view.data_error.connect(
            self._data_controller.on_data_error
        )
        
        # Сигналы от панели инструментов -> контроллер обновления
        self._toolbar.signals.refresh_current.connect(
            self._refresh_controller.refresh_current
        )
        self._toolbar.signals.refresh_visible.connect(
            self._refresh_controller.refresh_visible
        )
        self._toolbar.signals.full_reset.connect(
            self._refresh_controller.full_reset
        )
        
        # Сигналы от горячих клавиш -> контроллер обновления
        self._shortcuts.signals.refresh_current.connect(
            self._refresh_controller.refresh_current
        )
        self._shortcuts.signals.refresh_visible.connect(
            self._refresh_controller.refresh_visible
        )
        self._shortcuts.signals.full_reset.connect(
            self._refresh_controller.full_reset
        )
        
        log.debug("MainWindow: все сигналы подключены")
    
    # ===== Геттеры =====
    
    @property
    def tree_view(self) -> TreeView:
        """Возвращает виджет дерева."""
        return self._tree_view
    
    @property
    def details_panel(self) -> DetailsPanel:
        """Возвращает панель деталей."""
        return self._details_panel
    
    # ===== Обработчик закрытия =====
    
    def closeEvent(self, event) -> None:
        """
        Обрабатывает закрытие окна.
        Останавливает все контроллеры и очищает ресурсы.
        
        Args:
            event: Событие закрытия
        """
        log.info("Завершение работы...")
        
        # Останавливаем проверку соединения
        if hasattr(self, '_connection_controller'):
            self._connection_controller.stop_checking()
        
        # Очищаем кэш
        if hasattr(self._tree_view, 'cache'):
            self._tree_view.cache.clear()
            log.debug("MainWindow: кэш очищен")
        
        event.accept()
        log.success("Приложение завершено")
		
# client/src/ui/main_window/shortcuts.py
"""
Модуль управления горячими клавишами главного окна.
Определяет сочетания клавиш для основных действий.
"""
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ShortcutSignals(QObject):
    """Сигналы для горячих клавиш."""
    
    refresh_current = Signal()
    """Сигнал обновления текущего узла (F5)"""
    
    refresh_visible = Signal()
    """Сигнал обновления всех раскрытых узлов (Ctrl+F5)"""
    
    full_reset = Signal()
    """Сигнал полной перезагрузки (Ctrl+Shift+F5)"""


class ShortcutManager:
    """
    Менеджер горячих клавиш.
    
    Определяет и обрабатывает сочетания клавиш:
    - F5: обновить текущий узел
    - Ctrl+F5: обновить все раскрытые узлы
    - Ctrl+Shift+F5: полная перезагрузка
    """
    
    # ===== Константы =====
    _SHORTCUTS = {
        'refresh_current': QKeySequence.Refresh,  # F5
        'refresh_visible': QKeySequence(Qt.CTRL | Qt.Key_F5),
        'full_reset': QKeySequence(Qt.CTRL | Qt.SHIFT | Qt.Key_F5),
    }
    """Словарь сочетаний клавиш"""
    
    def __init__(self, parent: QMainWindow) -> None:
        """
        Инициализирует менеджер горячих клавиш.
        
        Args:
            parent: Родительское окно (MainWindow)
        """
        self._parent = parent
        self._actions = {}
        self.signals = ShortcutSignals()
        
        self._create_shortcuts()
        
        log.debug("ShortcutManager: инициализирован")
    
    # ===== Приватные методы =====
    
    def _create_shortcuts(self) -> None:
        """Создаёт все горячие клавиши."""
        self._create_refresh_current()
        self._create_refresh_visible()
        self._create_full_reset()
        
        log.debug("ShortcutManager: все горячие клавиши созданы")
    
    def _create_refresh_current(self) -> None:
        """Создаёт горячую клавишу F5 (обновить текущий узел)."""
        action = QAction(self._parent)
        action.setShortcut(self._SHORTCUTS['refresh_current'])
        action.triggered.connect(self.signals.refresh_current)
        self._parent.addAction(action)
        self._actions['refresh_current'] = action
        
        log.debug("ShortcutManager: создана клавиша F5")
    
    def _create_refresh_visible(self) -> None:
        """Создаёт горячую клавишу Ctrl+F5 (обновить все раскрытые)."""
        action = QAction(self._parent)
        action.setShortcut(self._SHORTCUTS['refresh_visible'])
        action.triggered.connect(self.signals.refresh_visible)
        self._parent.addAction(action)
        self._actions['refresh_visible'] = action
        
        log.debug("ShortcutManager: создана клавиша Ctrl+F5")
    
    def _create_full_reset(self) -> None:
        """Создаёт горячую клавишу Ctrl+Shift+F5 (полная перезагрузка)."""
        action = QAction(self._parent)
        action.setShortcut(self._SHORTCUTS['full_reset'])
        action.triggered.connect(self.signals.full_reset)
        self._parent.addAction(action)
        self._actions['full_reset'] = action
        
        log.debug("ShortcutManager: создана клавиша Ctrl+Shift+F5")
    
    # ===== Геттеры =====
    
    @property
    def actions(self) -> dict:
        """Возвращает словарь созданных действий."""
        return self._actions.copy()
    
    # ===== Публичные методы =====
    
    def enable_all(self) -> None:
        """Включает все горячие клавиши."""
        for action in self._actions.values():
            action.setEnabled(True)
        log.debug("ShortcutManager: все клавиши включены")
    
    def disable_all(self) -> None:
        """Отключает все горячие клавиши."""
        for action in self._actions.values():
            action.setEnabled(False)
        log.debug("ShortcutManager: все клавиши отключены")
		
# client/src/ui/tree/__init__.py
"""
Пакет компонентов дерева объектов
"""
from src.ui.tree.tree_view import TreeView

__all__ = ["TreeView"]

# client/src/ui/tree/base_tree.py
"""
Базовый класс для дерева объектов.
Предоставляет общую инициализацию пользовательского интерфейса,
заголовок с индикатором загрузки и базовые настройки QTreeView.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel, QProgressBar, QMessageBox
from PySide6.QtCore import Qt, Slot
from typing import Optional

from src.ui.tree_model import TreeModel
from src.core.cache import DataCache

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeViewBase(QWidget):
    """
    Базовый класс для виджета дерева объектов.
    
    Предоставляет:
    - Инициализацию пользовательского интерфейса
    - Заголовок с индикатором загрузки
    - Модель данных TreeModel
    - Базовые настройки QTreeView
    - Методы для управления индикатором загрузки
    
    Наследники могут расширять функциональность, добавляя:
    - Обработчики сигналов
    - Контекстное меню
    - Логику загрузки данных
    """
    
    # ===== Константы UI =====
    _DEFAULT_TITLE = "Объекты"
    """Заголовок по умолчанию"""
    
    _LOADING_TITLE = "Объекты (загрузка...)"
    """Заголовок во время загрузки"""
    
    _HEADER_STYLESHEET = """
        QLabel {
            background-color: #f0f0f0;
            padding: 8px;
            font-weight: bold;
            font-size: 14px;
            border-bottom: 1px solid #c0c0c0;
        }
    """
    """Стили для заголовка"""
    
    _PROGRESS_BAR_STYLESHEET = """
        QProgressBar {
            border: none;
            background-color: #f0f0f0;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
        }
    """
    """Стили для индикатора загрузки"""
    
    _TREE_VIEW_STYLESHEET = """
        QTreeView {
            background-color: white;
            border: none;
            outline: none;
        }
        QTreeView::item {
            padding: 4px;
            border-bottom: 1px solid #f0f0f0;
        }
        QTreeView::item:selected {
            background-color: #e3f2fd;
            color: black;
        }
        QTreeView::item:hover {
            background-color: #f5f5f5;
        }
    """
    """Стили для дерева"""
    
    # ===== Константы размеров =====
    _PROGRESS_BAR_HEIGHT = 3
    """Высота индикатора загрузки в пикселях"""
    
    _TREE_INDENTATION = 20
    """Отступ для дочерних элементов в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует базовый виджет дерева.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация UI
        self._init_ui()
        
        log.debug("TreeViewBase: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_ui(self) -> None:
        """
        Инициализирует пользовательский интерфейс.
        Создаёт layout, заголовок, модель и представление.
        """
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок с индикатором загрузки
        self._setup_header()
        
        # Создаём модель дерева
        self._model = TreeModel()
        
        # Создаём представление
        self._setup_tree_view()
        
        # Добавляем представление в layout
        layout.addWidget(self._tree_view)
        
        log.debug("TreeViewBase: UI инициализирован")
    
    def _setup_header(self) -> None:
        """
        Создаёт заголовок с индикатором загрузки.
        """
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        # Заголовок
        self._title_label = QLabel(self._DEFAULT_TITLE)
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setStyleSheet(self._HEADER_STYLESHEET)
        
        # Индикатор загрузки
        self._loading_bar = QProgressBar()
        self._loading_bar.setMaximum(0)
        self._loading_bar.setMinimum(0)
        self._loading_bar.setTextVisible(False)
        self._loading_bar.setFixedHeight(self._PROGRESS_BAR_HEIGHT)
        self._loading_bar.setStyleSheet(self._PROGRESS_BAR_STYLESHEET)
        self._loading_bar.hide()
        
        header_layout.addWidget(self._title_label)
        header_layout.addWidget(self._loading_bar)
        
        # Добавляем заголовок в основной layout
        if self.layout():
            self.layout().addLayout(header_layout)
    
    def _setup_tree_view(self) -> None:
        """
        Настраивает QTreeView: внешний вид, поведение и модель.
        """
        self._tree_view = QTreeView()
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setAlternatingRowColors(True)
        self._tree_view.setAnimated(True)
        self._tree_view.setIndentation(self._TREE_INDENTATION)
        self._tree_view.setExpandsOnDoubleClick(True)
        
        # Устанавливаем модель
        self._tree_view.setModel(self._model)
        
        # Применяем стили
        self._tree_view.setStyleSheet(self._TREE_VIEW_STYLESHEET)
        
        log.debug("TreeViewBase: QTreeView настроен")
    
    # ===== Геттеры =====
    
    @property
    def model(self) -> TreeModel:
        """
        Возвращает модель данных дерева.
        
        Returns:
            TreeModel: модель данных
        """
        return self._model
    
    @property
    def tree_view(self) -> QTreeView:
        """
        Возвращает виджет дерева.
        
        Returns:
            QTreeView: виджет для отображения дерева
        """
        return self._tree_view
    
    @property
    def title_label(self) -> QLabel:
        """
        Возвращает виджет заголовка.
        
        Returns:
            QLabel: виджет с заголовком
        """
        return self._title_label
    
    @property
    def loading_bar(self) -> QProgressBar:
        """
        Возвращает индикатор загрузки.
        
        Returns:
            QProgressBar: индикатор загрузки
        """
        return self._loading_bar
    
    # ===== Публичные методы =====
    
    def set_cache(self, cache: DataCache) -> None:
        """
        Устанавливает систему кэширования для модели.
        
        Args:
            cache: Система кэширования данных
        """
        self._model.set_cache(cache)
        log.debug("TreeViewBase: кэш передан модели")
    
    @Slot(bool)
    def show_loading(self, show: bool = True) -> None:
        """
        Управляет отображением индикатора загрузки.
        
        Args:
            show: True - показать индикатор, False - скрыть
        """
        if show:
            self._loading_bar.show()
            self._title_label.setText(self._LOADING_TITLE)
            log.debug("TreeViewBase: индикатор загрузки показан")
        else:
            self._loading_bar.hide()
            self._title_label.setText(self._DEFAULT_TITLE)
            log.debug("TreeViewBase: индикатор загрузки скрыт")
        
        # Принудительно обновляем отображение
        self._loading_bar.repaint()
    
    def update_title_count(self, count: int) -> None:
        """
        Обновляет заголовок с указанием количества элементов.
        
        Args:
            count: Количество элементов для отображения
        """
        self._title_label.setText(f"{self._DEFAULT_TITLE} ({count})")
        log.debug(f"TreeViewBase: заголовок обновлён, элементов: {count}")
    
    def _show_error(self, title: str, message: str) -> None:
        """
        Показывает диалоговое окно с ошибкой.
        
        Args:
            title: Заголовок окна
            message: Сообщение об ошибке
        """
        QMessageBox.warning(self, title, message)
        log.warning(f"Показано сообщение об ошибке: {title} - {message}")
    
    def reset_model(self) -> None:
        """
        Сбрасывает модель в исходное состояние.
        """
        self._model.reset()
        log.debug("TreeViewBase: модель сброшена")
		
# client/src/ui/tree/tree_loader.py
"""
Модуль для загрузки данных дерева.
Содержит логику загрузки иерархических данных:
- Загрузка комплексов (корневые узлы)
- Загрузка дочерних элементов при раскрытии узла
- Загрузка детальных данных при выборе узла
- Работа с кэшированием данных
"""
from PySide6.QtCore import QModelIndex, Slot, QTimer
from typing import Optional, Dict, Any, Callable, Union

from src.ui.tree_model import NodeType
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.core.api_client import ApiClient
from src.core.cache import DataCache

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeLoaderMixin:
    """
    Миксин для загрузки данных дерева.
    
    Предоставляет методы для загрузки данных на разных уровнях:
    - Загрузка корневых комплексов
    - Загрузка дочерних элементов (корпуса, этажи, помещения)
    - Загрузка детальных данных при выборе узла
    
    Требует наличия в родительском классе:
    - model: TreeModel - модель данных
    - cache: DataCache - система кэширования
    - api_client: ApiClient - клиент API
    - show_loading: метод для отображения индикатора загрузки
    - _show_error: метод для отображения ошибок
    - data_loading/data_loaded/data_error: сигналы (опционально)
    - item_selected: сигнал выбора элемента (опционально)
    """
    
    # ===== Константы =====
    _DETAILS_LOAD_DELAY_MS = 10
    """Задержка перед отправкой обновлённых данных после загрузки деталей"""
    
    _LOADING_FLAG_RESET_DELAY_MS = 100
    """Задержка сброса флага загрузки"""
    
    _CACHE_KEY_COMPLEXES_ALL = "complexes:all"
    """Ключ для кэширования всех комплексов"""
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_child_load_params(self, node) -> Optional[tuple]:
        """
        Определяет параметры для загрузки дочерних элементов.
        
        Args:
            node: Узел дерева (TreeNode)
            
        Returns:
            Кортеж (cache_key, load_func, child_type) или None
        """
        node_id = node.get_id()
        
        params_map = {
            NodeType.COMPLEX: (
                f"complex:{node_id}:buildings",
                self.api_client.get_buildings,
                NodeType.BUILDING
            ),
            NodeType.BUILDING: (
                f"building:{node_id}:floors",
                self.api_client.get_floors,
                NodeType.FLOOR
            ),
            NodeType.FLOOR: (
                f"floor:{node_id}:rooms",
                self.api_client.get_rooms,
                NodeType.ROOM
            )
        }
        
        return params_map.get(node.node_type)
    
    def _safe_emit_data_loading(self, node_type: NodeType, node_id: int) -> None:
        """
        Безопасно испускает сигнал начала загрузки.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        if hasattr(self, 'data_loading'):
            self.data_loading.emit(node_type.value, node_id)
    
    def _safe_emit_data_loaded(self, node_type: NodeType, node_id: int) -> None:
        """
        Безопасно испускает сигнал завершения загрузки.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        if hasattr(self, 'data_loaded'):
            self.data_loaded.emit(node_type.value, node_id)
    
    def _safe_emit_data_error(self, node_type: NodeType, node_id: int, error: str) -> None:
        """
        Безопасно испускает сигнал ошибки загрузки.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        if hasattr(self, 'data_error'):
            self.data_error.emit(node_type.value, node_id, error)
    
    def _safe_emit_item_selected(self, item_type: str, item_id: int, 
                                  item_data: Any, context: dict) -> None:
        """
        Безопасно испускает сигнал выбора элемента.
        
        Args:
            item_type: Тип элемента
            item_id: Идентификатор элемента
            item_data: Данные элемента
            context: Контекст иерархии
        """
        if hasattr(self, 'item_selected'):
            self.item_selected.emit(item_type, item_id, item_data, context)
    
    # ===== Публичные методы загрузки =====
    
    @Slot()
    def load_complexes(self) -> None:
        """
        Загружает список всех комплексов (корневые узлы дерева).
        
        Выполняет следующие действия:
        1. Показывает индикатор загрузки
        2. Проверяет наличие данных в кэше
        3. При отсутствии загружает с сервера
        4. Обновляет модель
        5. Обновляет заголовок с количеством
        6. Скрывает индикатор загрузки
        """
        # Проверяем наличие метода отображения загрузки
        if not hasattr(self, 'show_loading'):
            log.error("TreeLoader: отсутствует метод show_loading")
            return
        
        self.show_loading(True)
        log.info("Загрузка комплексов...")
        
        try:
            # Проверяем кэш
            cached_complexes = self.cache.get(self._CACHE_KEY_COMPLEXES_ALL)
            
            if cached_complexes is not None:
                complexes = cached_complexes
                log.cache(f"Комплексы загружены из кэша: {len(complexes)} шт.")
            else:
                # Загружаем с сервера
                complexes = self.api_client.get_complexes()
                # Сохраняем в кэш
                self.cache.set(self._CACHE_KEY_COMPLEXES_ALL, complexes)
                log.api(f"Комплексы загружены с сервера: {len(complexes)} шт.")
            
            # Обновляем модель
            self.model.set_complexes(complexes)
            
            # Обновляем заголовок, если есть
            if hasattr(self, 'title_label'):
                self.title_label.setText(f"Объекты ({len(complexes)})")
            
            log.success(f"Загружено {len(complexes)} комплексов")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка загрузки комплексов: {error_message}")
            
            if hasattr(self, '_show_error'):
                self._show_error("Ошибка загрузки комплексов", error_message)
            
        finally:
            self.show_loading(False)
    
    # ===== Загрузка дочерних элементов =====
    
    @Slot(QModelIndex)
    def _load_children(self, parent_index: QModelIndex) -> None:
        """
        Загружает дочерние элементы для указанного узла (ленивая загрузка).
        
        Args:
            parent_index: Индекс родительского узла в модели
        """
        # Получаем узел
        node = self.model._get_node(parent_index)
        if not node:
            log.warning("TreeLoader: попытка загрузить детей для несуществующего узла")
            return
        
        # Проверяем наличие дочерних элементов
        has_children = self.model.hasChildren(parent_index)
        
        # Если дети уже загружены или узел не может их иметь - выходим
        if node.loaded or not has_children:
            log.debug(f"Загрузка детей не требуется для {node.node_type.value} #{node.get_id()}")
            return
        
        # Определяем параметры загрузки
        load_params = self._get_child_load_params(node)
        if not load_params:
            log.warning(f"TreeLoader: неизвестный тип узла {node.node_type}")
            return
        
        cache_key, load_func, child_type = load_params
        node_type = node.node_type
        node_id = node.get_id()
        
        # Сигнализируем о начале загрузки
        self._safe_emit_data_loading(node_type, node_id)
        log.debug(f"Начало загрузки {child_type.value} для {node_type.value} #{node_id}")
        
        try:
            # Проверяем кэш
            children = self.cache.get(cache_key)
            
            if children is not None:
                log.cache(f"{child_type.value} загружены из кэша для {node_type.value} #{node_id}")
            else:
                # Загружаем с сервера
                log.api(f"Загрузка {child_type.value} для {node_type.value} #{node_id}")
                children = load_func(node_id)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
                log.cache(f"Данные сохранены в кэш: {cache_key}")
            
            # Добавляем в модель
            if children:
                self.model.add_children(parent_index, children, child_type)
                log.data(f"В модель добавлено {len(children)} {child_type.value}")
            
            # Сигнализируем о завершении загрузки
            self._safe_emit_data_loaded(node_type, node_id)
            log.debug(f"Загрузка {child_type.value} завершена")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка загрузки {child_type.value}: {error_message}")
            self._safe_emit_data_error(node_type, node_id, error_message)
    
    # ===== Загрузка детальных данных =====
    
    @Slot(str, int, QModelIndex, dict)
    def _load_details_if_needed(self, item_type: str, item_id: int, 
                                 index: QModelIndex, context: dict) -> None:
        """
        Загружает детальные данные для узла, если они отсутствуют в текущем объекте.
        
        Args:
            item_type: Тип элемента
            item_id: Идентификатор элемента
            index: Индекс узла в модели
            context: Контекст иерархии
        """
        # Устанавливаем флаг загрузки
        if hasattr(self, '_set_loading_flag'):
            self._set_loading_flag(True)
        
        try:
            # Получаем узел
            node = self.model._get_node(index)
            if not node:
                log.warning(f"TreeLoader: узел {item_type} #{item_id} не найден")
                return
            
            item_data = node.data
            
            # Загружаем детали в зависимости от типа
            if item_type == 'complex' and isinstance(item_data, Complex):
                self._load_complex_details(item_id, index, context, item_data)
                
            elif item_type == 'building' and isinstance(item_data, Building):
                self._load_building_details(item_id, index, context, item_data)
                
            elif item_type == 'floor' and isinstance(item_data, Floor):
                self._load_floor_details(item_id, index, context, item_data)
                
            elif item_type == 'room' and isinstance(item_data, Room):
                self._load_room_details(item_id, index, context, item_data)
                
        finally:
            # Сбрасываем флаг через задержку
            if hasattr(self, '_reset_loading_flag'):
                QTimer.singleShot(self._LOADING_FLAG_RESET_DELAY_MS, self._reset_loading_flag)
    
    def _load_complex_details(self, complex_id: int, index: QModelIndex, 
                               context: dict, current_data: Complex) -> None:
        """
        Загружает детальные данные для комплекса.
        
        Args:
            complex_id: Идентификатор комплекса
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные комплекса
        """
        # Проверяем, нужно ли загружать детали
        if current_data.address is not None and current_data.description is not None:
            log.debug(f"Детали комплекса #{complex_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей комплекса #{complex_id}")
        
        try:
            detailed_data = self.api_client.get_complex_detail(complex_id)
            
            if detailed_data:
                # Обновляем данные в узле
                node = self.model._get_node(index)
                if node:
                    node.update_data(detailed_data)
                    
                    # Сигнализируем об изменении данных
                    self.model.dataChanged.emit(index, index, [])
                    
                    # Отправляем обновлённые данные с задержкой
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'complex', complex_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали комплекса #{complex_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей комплекса #{complex_id}: {error}")
    
    def _load_building_details(self, building_id: int, index: QModelIndex,
                                context: dict, current_data: Building) -> None:
        """
        Загружает детальные данные для корпуса.
        
        Args:
            building_id: Идентификатор корпуса
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные корпуса
        """
        # Проверяем, нужно ли загружать детали
        if (current_data.description is not None and 
            current_data.address is not None):
            log.debug(f"Детали корпуса #{building_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей корпуса #{building_id}")
        
        try:
            detailed_data = self.api_client.get_building_detail(building_id)
            
            if detailed_data:
                node = self.model._get_node(index)
                if node:
                    node.update_data(detailed_data)
                    self.model.dataChanged.emit(index, index, [])
                    
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'building', building_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали корпуса #{building_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей корпуса #{building_id}: {error}")
    
    def _load_floor_details(self, floor_id: int, index: QModelIndex,
                             context: dict, current_data: Floor) -> None:
        """
        Загружает детальные данные для этажа.
        
        Args:
            floor_id: Идентификатор этажа
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные этажа
        """
        # Проверяем, нужно ли загружать детали
        if current_data.description is not None:
            log.debug(f"Детали этажа #{floor_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей этажа #{floor_id}")
        
        try:
            detailed_data = self.api_client.get_floor_detail(floor_id)
            
            if detailed_data:
                node = self.model._get_node(index)
                if node:
                    node.update_data(detailed_data)
                    self.model.dataChanged.emit(index, index, [])
                    
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'floor', floor_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали этажа #{floor_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей этажа #{floor_id}: {error}")
    
    def _load_room_details(self, room_id: int, index: QModelIndex,
                            context: dict, current_data: Room) -> None:
        """
        Загружает детальные данные для помещения.
        
        Args:
            room_id: Идентификатор помещения
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные помещения
        """
        # Проверяем, нужно ли загружать детали
        if (current_data.area is not None and 
            current_data.status_code is not None):
            log.debug(f"Детали помещения #{room_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей помещения #{room_id}")
        
        try:
            detailed_data = self.api_client.get_room_detail(room_id)
            
            if detailed_data:
                node = self.model._get_node(index)
                if node:
                    node.update_data(detailed_data)
                    self.model.dataChanged.emit(index, index, [])
                    
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'room', room_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали помещения #{room_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей помещения #{room_id}: {error}")
    
    # ===== Управление флагами =====
    
    @Slot()
    def _reset_loading_flag(self) -> None:
        """Сбрасывает флаг загрузки деталей."""
        if hasattr(self, '_set_loading_flag'):
            self._set_loading_flag(False)
            log.debug("Флаг загрузки сброшен")
    
    @Slot(str, int, object, dict)
    def _emit_updated_selection(self, item_type: str, item_id: int, 
                                 item_data: Any, context: dict) -> None:
        """
        Отправляет обновлённые данные о выделении.
        
        Args:
            item_type: Тип элемента
            item_id: Идентификатор элемента
            item_data: Данные элемента
            context: Контекст иерархии
        """
        self._safe_emit_item_selected(item_type, item_id, item_data, context)
        log.debug(f"Обновлённые данные отправлены для {item_type} #{item_id}")
		
# client/src/ui/tree/tree_menu.py
"""
Модуль для контекстного меню дерева.
Предоставляет функциональность контекстного меню для узлов дерева
с возможностью обновления выбранного узла.
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import QPoint, Slot, Qt, QModelIndex
from PySide6.QtGui import QAction
from typing import Dict, Optional

from src.ui.tree_model import NodeType, TreeNode

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeMenuMixin:
    """
    Миксин для контекстного меню дерева.
    
    Предоставляет контекстное меню с действиями для узлов дерева:
    - Обновление выбранного узла
    - (в будущем можно добавить другие действия)
    
    Требует наличия в родительском классе:
    - tree_view: QTreeView - виджет дерева
    - model: TreeModel - модель данных
    - _refresh_node: метод для обновления узла
    """
    
    # ===== Константы =====
    _MENU_ACTION_REFRESH = "🔄 Обновить {node_type}"
    """Шаблон текста для действия обновления в меню"""
    
    _NODE_TYPE_DISPLAY_NAMES: Dict[NodeType, str] = {
        NodeType.COMPLEX: "комплекс",
        NodeType.BUILDING: "корпус",
        NodeType.FLOOR: "этаж",
        NodeType.ROOM: "помещение"
    }
    """Отображаемые названия для типов узлов"""
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_node_display_name(self, node: TreeNode) -> str:
        """
        Возвращает отображаемое название для типа узла.
        
        Args:
            node: Узел дерева
            
        Returns:
            Строка с названием типа узла (например, "комплекс")
        """
        return self._NODE_TYPE_DISPLAY_NAMES.get(node.node_type, "объект")
    
    def _create_refresh_action(self, menu: QMenu, node: TreeNode, index: QModelIndex) -> QAction:
        """
        Создаёт действие для обновления узла в контекстном меню.
        
        Args:
            menu: Родительское меню
            node: Узел, для которого создаётся действие
            index: Индекс узла в модели
            
        Returns:
            Созданное действие QAction
        """
        # Получаем отображаемое название типа узла
        node_type_display = self._get_node_display_name(node)
        
        # Создаём действие с соответствующим текстом
        action_text = self._MENU_ACTION_REFRESH.format(node_type=node_type_display)
        refresh_action = QAction(action_text, menu)
        
        # Подключаем сигнал с правильным контекстом
        # Используем лямбду с захватом индекса для избежания проблем с замыканием
        refresh_action.triggered.connect(
            lambda checked=False, idx=index: self._refresh_node(idx, use_cache=False)
        )
        
        # Добавляем всплывающую подсказку
        refresh_action.setStatusTip(f"Обновить данные {node_type_display}")
        
        return refresh_action
    
    # ===== Публичные методы =====
    
    @Slot(QPoint)
    def _show_context_menu(self, position: QPoint) -> None:
        """
        Показывает контекстное меню для узла в указанной позиции.
        
        Args:
            position: Позиция курсора в координатах viewport
        """
        # Получаем индекс узла под курсором
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            log.debug("Контекстное меню: клик вне узла")
            return
        
        # Получаем узел по индексу
        node = self.model._get_node(index)
        if not node:
            log.warning("Контекстное меню: узел не найден по индексу")
            return
        
        # Создаём контекстное меню
        menu = QMenu(self.tree_view)
        
        # Добавляем действие для обновления узла
        refresh_action = self._create_refresh_action(menu, node, index)
        menu.addAction(refresh_action)
        
        # TODO: В будущем можно добавить другие действия:
        # - Копировать название
        # - Показать в проводнике
        # - Свойства
        # - и т.д.
        
        # Показываем меню в глобальных координатах
        global_position = self.tree_view.viewport().mapToGlobal(position)
        menu.exec(global_position)
        
        log.debug(f"Контекстное меню показано для {self._get_node_display_name(node)}")
		
# client/src/ui/tree/tree_selection.py
"""
Модуль для работы с выделением узлов и контекстом иерархии.
Предоставляет методы для получения информации о выбранных узлах,
восстановления выделения и сбора контекста из родительских элементов.
"""
from PySide6.QtCore import QModelIndex, Slot
from typing import Optional, Dict, Any, Tuple, Union

from src.ui.tree_model import NodeType, TreeNode

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeSelectionMixin:
    """
    Миксин для работы с выделением узлов и контекстом иерархии.
    
    Предоставляет функциональность:
    - Сбор контекста из родительских узлов
    - Получение информации о выбранном узле
    - Выбор узла по типу и идентификатору
    - Безопасное восстановление выделения
    - Восстановление родительского узла как запасной вариант
    
    Требует наличия в родительском классе:
    - model: TreeModel - модель данных
    - tree_view: QTreeView - виджет дерева
    - item_selected: Signal - сигнал выбора элемента (опционально)
    """
    
    # ===== Публичные методы =====
    
    def get_selected_node_info(self) -> Optional[Tuple[str, int, Any]]:
        """
        Получает информацию о текущем выбранном узле.
        
        Returns:
            Кортеж (тип_узла, идентификатор, данные) или None, если ничего не выбрано
        """
        # Проверяем наличие необходимых компонентов
        if not hasattr(self, 'tree_view') or not hasattr(self, 'model'):
            log.error("TreeSelection: отсутствуют tree_view или model")
            return None
        
        # Получаем индексы выбранных элементов
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return None
        
        # Берём первый выбранный индекс
        index = selected_indexes[0]
        node = self.model._get_node(index)
        
        if node is None:
            return None
        
        return (node.node_type.value, node.get_id(), node.data)
    
    def select_node(self, node_type: Union[str, NodeType], node_id: int) -> bool:
        """
        Выбирает узел по типу и идентификатору.
        
        Args:
            node_type: Тип узла (строка или NodeType)
            node_id: Идентификатор узла
            
        Returns:
            True, если узел найден и выбран, иначе False
        """
        # Проверяем наличие необходимых компонентов
        if not hasattr(self, 'model') or not hasattr(self, 'tree_view'):
            log.error("TreeSelection: отсутствуют model или tree_view")
            return False
        
        # Преобразуем тип в NodeType при необходимости
        if isinstance(node_type, str):
            try:
                node_type_enum = NodeType(node_type)
            except ValueError:
                log.error(f"TreeSelection: неверный тип узла '{node_type}'")
                return False
        else:
            node_type_enum = node_type
        
        # Получаем индекс узла
        index = self.model.get_index_by_id(node_type_enum, node_id)
        
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            log.debug(f"Узел {node_type} #{node_id} выбран")
            return True
        
        log.warning(f"Узел {node_type} #{node_id} не найден")
        return False
    
    # ===== Защищённые методы для работы с контекстом =====
    
    def _get_context_for_node(self, node: TreeNode) -> Dict[str, Any]:
        """
        Собирает контекст из родительских узлов.
        
        Проходит по цепочке родителей и собирает информацию:
        - Имя комплекса
        - Имя корпуса
        - Номер этажа
        
        Args:
            node: Узел, для которого собирается контекст
            
        Returns:
            Словарь с контекстом:
            {
                'complex_name': str или None,
                'building_name': str или None,
                'floor_num': int или None
            }
        """
        context = {
            'complex_name': None,
            'building_name': None,
            'floor_num': None
        }
        
        current_node = node
        while current_node is not None:
            # Проверяем тип текущего узла и извлекаем соответствующую информацию
            if current_node.node_type == NodeType.COMPLEX and current_node.data:
                context['complex_name'] = current_node.data.name
                log.debug(f"Найден комплекс: {current_node.data.name}")
                
            elif current_node.node_type == NodeType.BUILDING and current_node.data:
                context['building_name'] = current_node.data.name
                log.debug(f"Найден корпус: {current_node.data.name}")
                
            elif current_node.node_type == NodeType.FLOOR and current_node.data:
                context['floor_num'] = current_node.data.number
                log.debug(f"Найден этаж: {current_node.data.number}")
            
            # Переходим к родителю
            current_node = current_node.parent
        
        return context
    
    # ===== Приватные методы восстановления выделения =====
    
    @Slot(str, int, dict)
    def _restore_selection_safe(self, node_type: str, node_id: int, 
                                context: Optional[Dict] = None) -> None:
        """
        Безопасно восстанавливает выделение узла по его идентификатору.
        
        Пытается найти узел по типу и ID. Если узел найден:
        1. Устанавливает его как текущий
        2. Испускает сигнал item_selected с правильным контекстом
        
        Если узел не найден, пробует восстановить родительский узел.
        
        Args:
            node_type: Тип искомого узла
            node_id: Идентификатор искомого узла
            context: Контекст для восстановления (если None, будет собран заново)
        """
        try:
            # Преобразуем тип в NodeType
            try:
                node_type_enum = NodeType(node_type)
            except ValueError:
                log.error(f"Неверный тип узла при восстановлении: '{node_type}'")
                return
            
            # Получаем индекс узла
            index = self.model.get_index_by_id(node_type_enum, node_id)
            
            if index.isValid():
                node = self.model._get_node(index)
                if node and node.get_id() == node_id:
                    # Устанавливаем выделение
                    self.tree_view.setCurrentIndex(index)
                    
                    # Подготавливаем контекст
                    if context is None:
                        context = self._get_context_for_node(node)
                    
                    # Испускаем сигнал, если он доступен
                    if hasattr(self, 'item_selected'):
                        self.item_selected.emit(node_type, node_id, node.data, context)
                        log.info(f"Восстановлено выделение {node_type} #{node_id}")
                    else:
                        log.debug(f"Узел {node_type} #{node_id} найден, сигнал отсутствует")
                    
                    return
            
            # Узел не найден - пробуем восстановить родителя
            log.warning(f"Узел {node_type} #{node_id} не найден, ищем родителя")
            self._restore_parent_selection(node_type, node_id)
            
        except Exception as error:
            log.error(f"Ошибка при восстановлении выделения: {error}")
            import traceback
            traceback.print_exc()
    
    @Slot(str, int)
    def _restore_parent_selection(self, node_type: str, node_id: int) -> None:
        """
        Восстанавливает родительский узел, если целевой узел не найден.
        
        Используется как запасной вариант при восстановлении выделения.
        Определяет тип родителя и пытается выбрать первый доступный узел этого типа.
        
        Args:
            node_type: Тип искомого узла (для определения родителя)
            node_id: Идентификатор искомого узла (не используется, для совместимости)
        """
        try:
            # Определяем тип родителя на основе типа искомого узла
            parent_type_enum = None
            
            if node_type == NodeType.ROOM.value:
                parent_type_enum = NodeType.FLOOR
                log.debug("Ищем родительский этаж для комнаты")
                
            elif node_type == NodeType.FLOOR.value:
                parent_type_enum = NodeType.BUILDING
                log.debug("Ищем родительский корпус для этажа")
                
            elif node_type == NodeType.BUILDING.value:
                parent_type_enum = NodeType.COMPLEX
                log.debug("Ищем родительский комплекс для корпуса")
                
            else:
                log.warning(f"Для типа {node_type} нет родительского типа")
                return
            
            # Для комплекса выбираем первый в списке
            if parent_type_enum == NodeType.COMPLEX:
                index = self.model.index(0, 0)
                if index.isValid():
                    node = self.model._get_node(index)
                    if node:
                        self.tree_view.setCurrentIndex(index)
                        
                        # Собираем контекст
                        context = self._get_context_for_node(node)
                        
                        # Испускаем сигнал
                        if hasattr(self, 'item_selected'):
                            self.item_selected.emit(
                                NodeType.COMPLEX.value,
                                node.get_id(),
                                node.data,
                                context
                            )
                            log.info(f"Выбран комплекс #{node.get_id()} как запасной вариант")
                        
        except Exception as error:
            log.error(f"Ошибка при восстановлении родителя: {error}")
			
# client/src/ui/tree/tree_updater.py
"""
Модуль для обновления данных дерева.
Содержит логику трёх уровней обновления:
- Текущий узел (F5)
- Все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtCore import QModelIndex, Slot, QTimer
from typing import Optional, Dict, Any, Tuple

from src.ui.tree_model import NodeType

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeUpdaterMixin:
    """
    Миксин для обновления данных дерева.
    
    Предоставляет методы для обновления данных на разных уровнях:
    - refresh_current() - обновление текущего выбранного узла
    - refresh_visible() - обновление всех раскрытых узлов
    - full_reset() - полная перезагрузка всех данных
    
    Требует наличия в родительском классе:
    - model: TreeModel - модель данных
    - tree_view: QTreeView - виджет дерева
    - cache: DataCache - система кэширования
    - api_client: ApiClient - клиент API
    - data_error: Signal - сигнал ошибки
    """
    
    # ===== Константы =====
    _SELECTION_RESTORE_DELAY_MS = 100
    """Задержка восстановления выделения после обновления в миллисекундах"""
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_update_params(self, node) -> Optional[Tuple[str, Any, NodeType]]:
        """
        Определяет параметры для обновления узла.
        
        Args:
            node: Узел дерева (TreeNode)
            
        Returns:
            Кортеж (cache_key, load_func, child_type) или None, если тип не поддерживается
        """
        node_id = node.get_id()
        
        params_map = {
            NodeType.COMPLEX: (
                f"complex:{node_id}:buildings",
                self.api_client.get_buildings,
                NodeType.BUILDING
            ),
            NodeType.BUILDING: (
                f"building:{node_id}:floors",
                self.api_client.get_floors,
                NodeType.FLOOR
            ),
            NodeType.FLOOR: (
                f"floor:{node_id}:rooms",
                self.api_client.get_rooms,
                NodeType.ROOM
            )
        }
        
        return params_map.get(node.node_type)
    
    def _safe_emit_error(self, node_type: str, node_id: int, error: str) -> None:
        """
        Безопасно испускает сигнал ошибки, если он доступен.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        if hasattr(self, 'data_error'):
            self.data_error.emit(node_type, node_id, error)
    
    # ===== Публичные методы обновления =====
    
    @Slot()
    def refresh_current(self) -> None:
        """
        Обновляет текущий выбранный узел.
        
        Выполняет следующие действия:
        1. Получает информацию о выбранном узле
        2. Инвалидирует кэш дочерних элементов
        3. Загружает свежие данные
        4. Обновляет модель
        5. Восстанавливает выделение
        
        Горячая клавиша: F5
        """
        # Проверяем наличие необходимых методов
        if not hasattr(self, 'get_selected_node_info'):
            log.error("TreeUpdater: отсутствует метод get_selected_node_info")
            return
        
        # Получаем информацию о выбранном узле
        selected_info = self.get_selected_node_info()
        if not selected_info:
            log.info("TreeUpdater: нет выбранного узла для обновления")
            return
        
        node_type, node_id, _ = selected_info
        
        # Находим индекс узла в модели
        index = self.model.get_index_by_id(NodeType(node_type), node_id)
        if not index.isValid():
            log.warning(f"TreeUpdater: узел {node_type} #{node_id} не найден в модели")
            return
        
        # Получаем узел и его контекст
        node = self.model._get_node(index)
        if not node:
            return
        
        context = self._get_context_for_node(node)
        log.info(f"Обновление узла {node_type} #{node_id}")
        
        # Определяем параметры обновления
        params = self._get_update_params(node)
        if not params:
            log.warning(f"TreeUpdater: неподдерживаемый тип узла {node.node_type}")
            return
        
        cache_key, load_func, child_type = params
        
        # Блокируем сигналы выделения на время обновления
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            # Инвалидируем кэш дочерних элементов
            self.cache.remove(cache_key)
            
            # Загружаем свежие данные
            children = load_func(node_id)
            
            if children is not None:
                # Обновляем модель
                self.model.update_children(index, children, child_type)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
                log.success(f"Узел {node_type} #{node_id} обновлён")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка обновления {node_type} #{node_id}: {error_message}")
            self._safe_emit_error(node_type, node_id, error_message)
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение после задержки
        QTimer.singleShot(
            self._SELECTION_RESTORE_DELAY_MS,
            lambda: self._restore_selection_safe(node_type, node_id, context)
        )
    
    @Slot()
    def refresh_visible(self) -> None:
        """
        Обновляет все раскрытые узлы в дереве.
        
        Выполняет следующие действия:
        1. Получает список раскрытых узлов из кэша
        2. Запоминает текущий выбранный узел
        3. Обновляет каждый раскрытый узел
        4. Восстанавливает выделение
        
        Горячая клавиша: Ctrl+F5
        """
        # Получаем список раскрытых узлов
        expanded_nodes = self.cache.get_expanded_nodes()
        if not expanded_nodes:
            log.info("TreeUpdater: нет раскрытых узлов для обновления")
            return
        
        # Запоминаем текущий выбранный узел
        selected_info = self.get_selected_node_info()
        selected_type = None
        selected_id = None
        selected_context = None
        
        if selected_info:
            selected_type, selected_id, _ = selected_info
            index = self.model.get_index_by_id(NodeType(selected_type), selected_id)
            if index.isValid():
                node = self.model._get_node(index)
                if node:
                    selected_context = self._get_context_for_node(node)
            log.debug(f"Будет восстановлен узел: {selected_type} #{selected_id}")
        
        log.info(f"Обновление {len(expanded_nodes)} раскрытых узлов")
        
        # Блокируем сигналы выделения
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            # Обновляем каждый раскрытый узел
            for node_type, node_id in expanded_nodes:
                index = self.model.get_index_by_id(NodeType(node_type), node_id)
                if index.isValid():
                    self._refresh_node(index, use_cache=False)
            
            log.success(f"Обновление {len(expanded_nodes)} узлов завершено")
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение
        if selected_type and selected_id:
            QTimer.singleShot(
                self._SELECTION_RESTORE_DELAY_MS,
                lambda: self._restore_selection_safe(selected_type, selected_id, selected_context)
            )
    
    @Slot()
    def full_reset(self) -> None:
        """
        Выполняет полную перезагрузку всех данных.
        
        Действия:
        1. Очищает весь кэш
        2. Перезагружает комплексы
        3. Сбрасывает состояние дерева
        
        Горячая клавиша: Ctrl+Shift+F5
        """
        log.info("Полная перезагрузка данных")
        
        # Очищаем кэш
        self.cache.clear()
        
        # Перезагружаем корневые элементы
        self.load_complexes()
        
        log.success("Полная перезагрузка завершена")
    
    # ===== Защищённые методы обновления =====
    
    @Slot(QModelIndex, bool)
    def _refresh_node(self, index: QModelIndex, use_cache: bool = False) -> None:
        """
        Обновляет конкретный узел дерева.
        
        Args:
            index: Индекс обновляемого узла
            use_cache: Флаг использования кэша
                      True - использовать кэш (если есть)
                      False - принудительно загружать с сервера
        """
        # Получаем узел
        node = self.model._get_node(index)
        if not node:
            log.warning("TreeUpdater: попытка обновить несуществующий узел")
            return
        
        node_type = node.node_type.value
        node_id = node.get_id()
        
        # Определяем параметры обновления
        params = self._get_update_params(node)
        if not params:
            log.warning(f"TreeUpdater: неподдерживаемый тип узла {node.node_type}")
            return
        
        cache_key, load_func, child_type = params
        
        # Принудительно удаляем кэш, если не разрешено его использовать
        if not use_cache:
            self.cache.remove(cache_key)
            log.debug(f"Кэш {cache_key} инвалидирован")
        
        try:
            # Загружаем данные
            if use_cache:
                children = self.cache.get(cache_key)
                if children is None:
                    log.debug(f"Кэш пуст, загрузка с сервера для {node_type} #{node_id}")
                    children = load_func(node_id)
                    self.cache.set(cache_key, children)
            else:
                log.debug(f"Принудительная загрузка с сервера для {node_type} #{node_id}")
                children = load_func(node_id)
                self.cache.set(cache_key, children)
            
            # Обновляем модель
            if children is not None:
                self.model.update_children(index, children, child_type)
                log.debug(f"Модель обновлена для {node_type} #{node_id}")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка обновления {node_type} #{node_id}: {error_message}")
            self._safe_emit_error(node_type, node_id, error_message)
			
# client/src/ui/tree/tree_view.py
"""
Основной класс дерева объектов.
Объединяет все миксины и базовый класс для создания иерархического дерева
с поддержкой ленивой загрузки, кэширования и контекстного меню.
"""
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex, QPoint, QTimer, QItemSelection
from PySide6.QtWidgets import QWidget

from src.core.api_client import ApiClient
from src.core.cache import DataCache
from src.ui.tree.base_tree import TreeViewBase
from src.ui.tree.tree_selection import TreeSelectionMixin
from src.ui.tree.tree_loader import TreeLoaderMixin
from src.ui.tree.tree_updater import TreeUpdaterMixin
from src.ui.tree.tree_menu import TreeMenuMixin
from src.ui.tree_model import NodeType


from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeView(
    TreeViewBase,
    TreeSelectionMixin,
    TreeLoaderMixin,
    TreeUpdaterMixin,
    TreeMenuMixin
):
    """
    Виджет дерева объектов с поддержкой ленивой загрузки и кэширования.
    
    Предоставляет древовидное представление иерархии:
    Комплексы → Корпуса → Этажи → Помещения.
    
    Сигналы:
        item_selected: испускается при выборе элемента в дереве
        data_loading: начало загрузки данных для узла
        data_loaded: завершение загрузки данных
        data_error: ошибка загрузки данных
    """
    
    # ===== Сигналы =====
    item_selected = Signal(str, int, object, dict)
    """Сигнал выбора элемента (тип, идентификатор, данные, контекст)"""
    
    data_loading = Signal(str, int)
    """Сигнал начала загрузки данных для узла (тип, идентификатор)"""
    
    data_loaded = Signal(str, int)
    """Сигнал завершения загрузки данных для узла (тип, идентификатор)"""
    
    data_error = Signal(str, int, str)
    """Сигнал ошибки загрузки данных (тип, идентификатор, сообщение)"""
    
    # ===== Константы =====
    _LOADING_FLAG_RESET_DELAY_MS = 100
    """Задержка сброса флага загрузки в миллисекундах"""
    
    def __init__(self, parent: QWidget = None) -> None:
        """
        Инициализирует виджет дерева.
        
        Args:
            parent: Родительский виджет
        """
        # Инициализация базового класса
        super().__init__(parent)
        
        # Инициализация компонентов
        self._init_components()
        
        # Настройка сигналов
        self._connect_tree_signals()
        
        # Загрузка начальных данных
        self.load_complexes()
        
        log.success("TreeView: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_components(self) -> None:
        """
        Инициализация внутренних компонентов.
        Создаёт клиент API, кэш и устанавливает флаги состояния.
        """
        # Клиент для работы с API
        self._api_client = ApiClient()
        
        # Система кэширования данных
        self._cache = DataCache()
        
        # Передаём кэш в модель
        self.set_cache(self._cache)
        
        # Флаг блокировки обработки выделения во время загрузки
        self._is_loading_details = False
    
    def _connect_tree_signals(self) -> None:
        """
        Подключает сигналы дерева и модели к соответствующим обработчикам.
        """
        # Сигналы выделения
        selection_model = self.tree_view.selectionModel()
        selection_model.selectionChanged.connect(self._on_selection_changed)
        
        # Сигналы раскрытия/сворачивания узлов
        self.tree_view.expanded.connect(self._on_node_expanded)
        self.tree_view.collapsed.connect(self._on_node_collapsed)
        
        # Контекстное меню
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # Сигналы модели
        self.model.data_loading.connect(self._on_model_data_loading)
        self.model.data_loaded.connect(self._on_model_data_loaded)
        self.model.data_error.connect(self._on_model_data_error)
    
    # ===== Геттеры =====
    
    @property
    def api_client(self) -> ApiClient:
        """Возвращает клиент API."""
        return self._api_client
    
    @property
    def cache(self) -> DataCache:
        """Возвращает систему кэширования."""
        return self._cache
    
    @property
    def is_loading_details(self) -> bool:
        """
        Возвращает состояние загрузки деталей.
        
        Returns:
            True, если выполняется загрузка детальных данных
        """
        return self._is_loading_details
    
    # ===== Управление флагами =====
    
    def _set_loading_flag(self, value: bool) -> None:
        """
        Устанавливает флаг загрузки деталей.
        
        Args:
            value: Новое значение флага
        """
        self._is_loading_details = value
    
    @Slot()
    def _reset_loading_flag(self) -> None:
        """Сбрасывает флаг загрузки деталей."""
        self._set_loading_flag(False)
        log.debug("TreeView: флаг загрузки сброшен")
    
    # ===== Обработчики сигналов модели =====
    
    @Slot(NodeType, int)
    def _on_model_data_loading(self, node_type: NodeType, node_id: int) -> None:
        """
        Обрабатывает начало загрузки данных в модели.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self.data_loading.emit(node_type.value, node_id)
        log.debug(f"Модель начала загрузку {node_type.value} #{node_id}")
    
    @Slot(NodeType, int)
    def _on_model_data_loaded(self, node_type: NodeType, node_id: int) -> None:
        """
        Обрабатывает завершение загрузки данных в модели.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self.data_loaded.emit(node_type.value, node_id)
        log.debug(f"Модель завершила загрузку {node_type.value} #{node_id}")
    
    @Slot(NodeType, int, str)
    def _on_model_data_error(self, node_type: NodeType, node_id: int, error: str) -> None:
        """
        Обрабатывает ошибку загрузки данных в модели.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        self.data_error.emit(node_type.value, node_id, error)
        log.error(f"Ошибка загрузки {node_type.value} #{node_id}: {error}")
    
    # ===== Обработчики сигналов дерева =====
    
    @Slot(QModelIndex)
    def _on_node_expanded(self, index: QModelIndex) -> None:
        """
        Обрабатывает раскрытие узла для ленивой загрузки дочерних элементов.
        
        Args:
            index: Индекс раскрываемого узла
        """
        node = self.model._get_node(index)
        if not node:
            log.warning("TreeView: попытка раскрыть несуществующий узел")
            return
        
        # Сохраняем состояние раскрытого узла в кэше
        self._cache.mark_expanded(node.node_type.value, node.get_id())
        
        # Проверяем наличие дочерних элементов
        has_children = self.model.hasChildren(index)
        
        # Загружаем детей, если они ещё не загружены
        if not node.loaded and has_children:
            log.info(f"Раскрыт узел {node.node_type.value} #{node.get_id()}, загрузка детей")
            self._load_children(index)
    
    @Slot(QModelIndex)
    def _on_node_collapsed(self, index: QModelIndex) -> None:
        """
        Обрабатывает сворачивание узла.
        
        Args:
            index: Индекс сворачиваемого узла
        """
        node = self.model._get_node(index)
        if node:
            self._cache.mark_collapsed(node.node_type.value, node.get_id())
            log.debug(f"Свёрнут узел {node.node_type.value} #{node.get_id()}")
    
    @Slot(QItemSelection, QItemSelection)
    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        """
        Обрабатывает изменение выделения в дереве.
        
        Args:
            selected: Новые выбранные индексы
            deselected: Индексы, с которых снято выделение
        """
        # Игнорируем временные выделения во время загрузки
        if self._is_loading_details:
            log.debug("TreeView: выделение проигнорировано (идёт загрузка)")
            return
        
        indexes = selected.indexes()
        if not indexes:
            return
        
        index = indexes[0]
        node = self.model._get_node(index)
        if not node:
            return
        
        # Получаем данные выбранного узла
        item_type = node.node_type.value
        item_id = node.get_id()
        item_data = node.data
        context = self._get_context_for_node(node)
        
        # Отправляем сигнал с контекстом
        self.item_selected.emit(item_type, item_id, item_data, context)
        
        # Загружаем детальные данные при необходимости
        self._load_details_if_needed(item_type, item_id, index, context)
        
        log.info(f"Выбран {item_type} #{item_id}")
		
# client/src/ui/tree_model/__init__.py
"""
Пакет модели дерева для отображения иерархии объектов.
Предоставляет компоненты для создания и управления древовидными данными.

Основные компоненты:
- NodeType: Перечисление типов узлов
- TreeNode: Класс узла дерева
- TreeModel: Полноценная модель для QTreeView

Пример использования:
    model = TreeModel()
    model.set_cache(cache)
    model.set_complexes(complexes)
    tree_view.setModel(model)
"""
from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.ui.tree_model.tree_model import TreeModel

__all__ = [
    "NodeType",
    "TreeNode", 
    "TreeModel"
]

# client/src/ui/tree_model/node_types.py
"""
Модуль с определением типов узлов дерева.
Содержит перечисление NodeType для идентификации типа каждого узла в иерархии.
"""
from enum import Enum


class NodeType(Enum):
    """
    Типы узлов дерева объектов.
    
    Используется для идентификации типа каждого узла в иерархии:
    - COMPLEX: комплекс зданий (корневой уровень)
    - BUILDING: корпус в составе комплекса
    - FLOOR: этаж в составе корпуса
    - ROOM: помещение на этаже
    """
    COMPLEX = "complex"
    BUILDING = "building"
    FLOOR = "floor"
    ROOM = "room"
    
    def __str__(self) -> str:
        """Возвращает строковое представление типа."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'NodeType':
        """
        Создаёт NodeType из строкового значения.
        
        Args:
            value: Строковое представление типа
            
        Returns:
            NodeType: Соответствующий тип узла
            
        Raises:
            ValueError: Если строка не соответствует ни одному типу
        """
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Неизвестный тип узла: {value}")
		
# client/src/ui/tree_model/tree_model_base.py
"""
Базовый абстрактный класс для модели дерева.
Наследуется от QAbstractItemModel и определяет базовый интерфейс
для работы с иерархическими данными в Qt.
"""
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QFont, QBrush, QColor
from typing import Optional, Any

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModelBase(QAbstractItemModel):
    """
    Абстрактный базовый класс для модели дерева.
    
    Предоставляет:
    - Виртуальный корневой узел (_root_node)
    - Базовые методы QAbstractItemModel (index, parent, rowCount, columnCount)
    - Кастомные роли для данных (ItemIdRole, ItemTypeRole, ItemDataRole)
    - Сигналы для отслеживания загрузки данных
    - Методы для получения узла из индекса
    
    Наследники должны реализовать:
    - data() - получение данных для отображения
    - flags() - флаги элементов
    - hasChildren() - проверка наличия детей
    - Методы управления данными (set_complexes, add_children, update_children)
    """
    
    # ===== Кастомные роли для данных =====
    ItemIdRole = Qt.UserRole + 1
    """Роль для получения ID объекта"""
    
    ItemTypeRole = Qt.UserRole + 2
    """Роль для получения типа объекта (NodeType)"""
    
    ItemDataRole = Qt.UserRole + 3
    """Роль для получения сырых данных (модель)"""
    
    # ===== Сигналы =====
    data_loading = Signal(NodeType, int)
    """Сигнал начала загрузки данных для узла (тип, ID)"""
    
    data_loaded = Signal(NodeType, int)
    """Сигнал завершения загрузки данных для узла (тип, ID)"""
    
    data_error = Signal(NodeType, int, str)
    """Сигнал ошибки загрузки данных (тип, ID, сообщение)"""
    
    # ===== Константы для стилей =====
    _FONT_SIZE_COMPLEX_BOOST = 1
    """Увеличение размера шрифта для комплексов"""
    
    _COLOR_COMPLEX = QColor(0, 70, 130)
    """Цвет текста для комплексов (тёмно-синий)"""
    
    _COLOR_BUILDING = QColor(0, 100, 0)
    """Цвет текста для корпусов (тёмно-зелёный)"""
    
    _COLOR_FLOOR = QColor(100, 100, 100)
    """Цвет текста для этажей (серый)"""
    
    _COLOR_ROOM_OCCUPIED = QColor(200, 50, 50)
    """Цвет текста для занятых помещений (красный)"""
    
    _COLOR_ROOM_FREE = QColor(50, 150, 50)
    """Цвет текста для свободных помещений (зелёный)"""
    
    _COLOR_DEFAULT = QColor(0, 0, 0)
    """Цвет текста по умолчанию (чёрный)"""
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует базовую модель дерева.
        
        Args:
            parent: Родительский объект
        """
        super().__init__(parent)
        
        # Виртуальный корневой узел (не отображается)
        self._root_node = TreeNode(None, None)
        
        log.debug("TreeModelBase: инициализирован")
    
    # ===== Базовые методы QAbstractItemModel =====
    
    def index(self, row: int, column: int, 
              parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """
        Создаёт индекс для элемента по строке и колонке.
        
        Args:
            row: Строка (позиция среди siblings)
            column: Колонка (всегда 0 для дерева)
            parent: Родительский индекс
            
        Returns:
            QModelIndex: Индекс элемента или пустой индекс
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        parent_node = self._get_node(parent)
        if parent_node is None:
            return QModelIndex()
        
        child_node = parent_node.child_at(row)
        if child_node is None:
            return QModelIndex()
        
        return self.createIndex(row, column, child_node)
    
    def parent(self, index: QModelIndex) -> QModelIndex:
        """
        Возвращает родительский индекс для данного индекса.
        
        Args:
            index: Индекс элемента
            
        Returns:
            QModelIndex: Родительский индекс или пустой индекс
        """
        if not index.isValid():
            return QModelIndex()
        
        child_node = self._get_node(index)
        if child_node is None:
            return QModelIndex()
        
        parent_node = child_node.parent
        if parent_node is None or parent_node == self._root_node:
            return QModelIndex()
        
        return self.createIndex(parent_node.row(), 0, parent_node)
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Возвращает количество строк (дочерних элементов) для родителя.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            int: Количество дочерних элементов
        """
        parent_node = self._get_node(parent)
        if parent_node is None:
            return 0
        return parent_node.child_count()
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Возвращает количество колонок.
        
        Args:
            parent: Родительский индекс (не используется)
            
        Returns:
            int: Всегда 1 (одна колонка)
        """
        return 1
    
    def headerData(self, section: int, orientation: Qt.Orientation, 
                   role: int = Qt.DisplayRole) -> Optional[str]:
        """
        Возвращает заголовок для колонки.
        
        Args:
            section: Номер колонки
            orientation: Ориентация
            role: Роль данных
            
        Returns:
            Optional[str]: Заголовок или None
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Объекты"
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Возвращает флаги элемента.
        
        Args:
            index: Индекс элемента
            
        Returns:
            Qt.ItemFlags: Флаги элемента
        """
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    # ===== Вспомогательные методы =====
    
    def _get_node(self, index: QModelIndex) -> Optional[TreeNode]:
        """
        Получает узел из индекса.
        
        Args:
            index: Индекс элемента
            
        Returns:
            Optional[TreeNode]: Узел или корневой узел
        """
        if index.isValid():
            node = index.internalPointer()
            if isinstance(node, TreeNode):
                return node
        return self._root_node
    
    def _index_of_node(self, node: TreeNode) -> QModelIndex:
        """
        Создаёт QModelIndex для узла.
        
        Args:
            node: Узел
            
        Returns:
            QModelIndex: Индекс узла или пустой индекс
        """
        if node is None or node == self._root_node:
            return QModelIndex()
        return self.createIndex(node.row(), 0, node)
    
    # ===== Виртуальные методы для переопределения =====
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Возвращает данные для отображения.
        Должен быть переопределён в наследнике.
        
        Args:
            index: Индекс элемента
            role: Роль данных
            
        Returns:
            Any: Данные для указанной роли
        """
        raise NotImplementedError("Метод data должен быть реализован в наследнике")
    
    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        """
        Проверяет, может ли узел иметь дочерние элементы.
        Должен быть переопределён в наследнике.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            bool: True если узел может иметь детей
        """
        raise NotImplementedError("Метод hasChildren должен быть реализован в наследнике")
		
# client/src/ui/tree_model/tree_model_data.py
"""
Миксин для управления данными модели дерева.
Предоставляет методы для добавления, обновления и удаления узлов.
"""
from PySide6.QtCore import QModelIndex, Qt
from typing import List, Any, Dict

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModelDataMixin:
    """
    Миксин для управления данными модели дерева.
    
    Предоставляет методы:
    - set_complexes: установка корневых узлов (комплексов)
    - add_children: добавление дочерних узлов (первоначальная загрузка)
    - update_children: обновление дочерних узлов с сохранением существующих
    - reset: полный сброс модели
    
    Требует наличия в классе:
    - _root_node: TreeNode - корневой узел
    - _node_index: Dict - индекс узлов
    - _add_to_index: метод для добавления узла в индекс
    - _remove_from_index: метод для удаления узла из индекса
    - beginInsertRows/endInsertRows: методы Qt
    - beginRemoveRows/endRemoveRows: методы Qt
    - beginResetModel/endResetModel: методы Qt
    - dataChanged: сигнал Qt
    """
    
    # ===== Константы =====
    _LOG_COMPLEXES_LOADED = "Загружено {count} комплексов"
    """Шаблон сообщения о загрузке комплексов"""
    
    _LOG_CHILDREN_ADDED = "Добавлено {count} {type} к {parent_type} #{parent_id}"
    """Шаблон сообщения о добавлении детей"""
    
    _LOG_CHILDREN_UPDATED = "Обновлены дети {parent_type} #{parent_id}"
    """Шаблон сообщения об обновлении детей"""
    
    _LOG_RESET = "Модель сброшена"
    """Сообщение о сбросе модели"""
    
    def __init__(self, *args, **kwargs):
        """
        Инициализирует миксин управления данными.
        """
        super().__init__(*args, **kwargs)
        log.debug("TreeModelDataMixin: инициализирован")
    
    # ===== Публичные методы =====
    
    def set_complexes(self, complexes: List[Any]) -> None:
        """
        Устанавливает список комплексов (корневые узлы).
        
        Вызывается при инициализации и полной перезагрузке.
        
        Args:
            complexes: Список объектов Complex
        """
        self.beginResetModel()
        
        # Очищаем всё
        self._root_node.remove_all_children()
        self._clear_index()
        
        # Создаём узлы для комплексов
        for complex_data in complexes:
            node = TreeNode(complex_data, NodeType.COMPLEX, self._root_node)
            self._root_node.append_child(node)
            self._add_to_index(node)
        
        self.endResetModel()
        
        log.success(self._LOG_COMPLEXES_LOADED.format(count=len(complexes)))
    
    def add_children(self, parent_index: QModelIndex, 
                     children_data: List[Any], child_type: NodeType) -> None:
        """
        Добавляет новые дочерние узлы к родительскому (первоначальная загрузка).
        
        Args:
            parent_index: Индекс родительского узла
            children_data: Список данных для дочерних узлов
            child_type: Тип дочерних узлов
        """
        parent_node = self._get_node(parent_index)
        if parent_node is None or parent_node == self._root_node:
            log.error("Попытка добавить детей к несуществующему родителю")
            return
        
        # Начинаем вставку
        first_row = parent_node.child_count()
        last_row = first_row + len(children_data) - 1
        
        self.beginInsertRows(parent_index, first_row, last_row)
        
        # Создаём и добавляем дочерние узлы
        for data in children_data:
            child_node = TreeNode(data, child_type, parent_node)
            parent_node.append_child(child_node)
            self._add_to_index(child_node)
        
        # Помечаем, что дети загружены
        parent_node.loaded = True
        
        self.endInsertRows()
        
        log.data(self._LOG_CHILDREN_ADDED.format(
            count=len(children_data),
            type=child_type.value,
            parent_type=parent_node.node_type.value,
            parent_id=parent_node.get_id()
        ))
    
    def update_children(self, parent_index: QModelIndex, 
                        children_data: List[Any], child_type: NodeType) -> None:
        """
        Обновляет дочерние узлы, сохраняя существующие где возможно.
        
        Args:
            parent_index: Индекс родительского узла
            children_data: Новые данные для дочерних узлов
            child_type: Тип дочерних узлов
        """
        parent_node = self._get_node(parent_index)
        if parent_node is None or parent_node == self._root_node:
            log.error("Попытка обновить детей несуществующего родителя")
            return
        
        # Создаём словарь существующих детей по ID
        existing_children = {
            child.get_id(): (i, child) 
            for i, child in enumerate(parent_node.children)
        }
        
        # Создаём словарь новых данных по ID
        new_data_dict = {data.id: data for data in children_data}
        
        # Обновляем существующие узлы и удаляем те, которых больше нет
        for child_id, (row, child_node) in list(existing_children.items()):
            if child_id in new_data_dict:
                # Обновляем существующий узел новыми данными
                child_node.update_data(new_data_dict[child_id])
                
                # Сигнализируем об изменении данных
                child_index = self.index(row, 0, parent_index)
                self.dataChanged.emit(
                    child_index, child_index, 
                    [Qt.DisplayRole, Qt.ForegroundRole]
                )
                
                # Удаляем из словаря новых, чтобы не создавать дубликат
                del new_data_dict[child_id]
            else:
                # Элемент удалён - убираем его
                self.beginRemoveRows(parent_index, row, row)
                parent_node.children.pop(row)
                self._remove_from_index(child_node)
                self.endRemoveRows()
                
                # Перестраиваем словарь existing_children после удаления
                existing_children = {
                    child.get_id(): (i, child) 
                    for i, child in enumerate(parent_node.children)
                }
        
        # Добавляем новые элементы
        if new_data_dict:
            first_row = parent_node.child_count()
            last_row = first_row + len(new_data_dict) - 1
            self.beginInsertRows(parent_index, first_row, last_row)
            
            for data in new_data_dict.values():
                child_node = TreeNode(data, child_type, parent_node)
                parent_node.append_child(child_node)
                self._add_to_index(child_node)
            
            self.endInsertRows()
        
        # Помечаем, что дети загружены
        parent_node.loaded = True
        
        log.data(self._LOG_CHILDREN_UPDATED.format(
            parent_type=parent_node.node_type.value,
            parent_id=parent_node.get_id()
        ))
    
    def reset(self) -> None:
        """
        Выполняет полный сброс модели.
        Очищает все узлы и индекс.
        """
        self.beginResetModel()
        self._root_node.remove_all_children()
        self._clear_index()
        self.endResetModel()
        
        log.debug(self._LOG_RESET)
		
# client/src/ui/tree_model/tree_model_index.py
"""
Миксин для работы с индексацией узлов дерева.
Предоставляет быстрый доступ к узлам по их типу и идентификатору.
"""
from typing import Optional, Dict

from PySide6.QtCore import QModelIndex

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModelIndexMixin:
    """
    Миксин для индексации узлов дерева.
    
    Предоставляет:
    - Словарь _node_index для быстрого доступа к узлам по ключу
    - Метод _make_key для создания ключа из типа и ID
    - Метод get_node_by_id для получения узла по типу и ID
    - Метод get_index_by_id для получения QModelIndex по типу и ID
    
    Требует наличия в классе:
    - _root_node: TreeNode - корневой узел
    - _index_of_node: метод для получения индекса из узла
    """
    
    def __init__(self, *args, **kwargs):
        """
        Инициализирует миксин индексации.
        Создаёт пустой словарь для индексации узлов.
        """
        super().__init__(*args, **kwargs)
        
        # Словарь для быстрого доступа к узлам по ключу
        self._node_index: Dict[str, TreeNode] = {}
        
        log.debug("TreeModelIndexMixin: инициализирован")
    
    # ===== Приватные методы =====
    
    def _make_key(self, node_type: NodeType, node_id: int) -> str:
        """
        Создаёт ключ для доступа к узлу в индексе.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            str: Ключ в формате "тип:id"
        """
        return f"{node_type.value}:{node_id}"
    
    def _add_to_index(self, node: TreeNode) -> None:
        """
        Добавляет узел в индекс.
        
        Args:
            node: Узел для добавления
        """
        key = self._make_key(node.node_type, node.get_id())
        self._node_index[key] = node
        log.debug(f"Узел добавлен в индекс: {key}")
    
    def _remove_from_index(self, node: TreeNode) -> None:
        """
        Удаляет узел из индекса.
        
        Args:
            node: Узел для удаления
        """
        key = self._make_key(node.node_type, node.get_id())
        if key in self._node_index:
            del self._node_index[key]
            log.debug(f"Узел удалён из индекса: {key}")
    
    def _clear_index(self) -> None:
        """Очищает индекс узлов."""
        self._node_index.clear()
        log.debug("Индекс узлов очищен")
    
    # ===== Публичные методы =====
    
    def get_node_by_id(self, node_type: NodeType, node_id: int) -> Optional[TreeNode]:
        """
        Получает узел по типу и идентификатору.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            Optional[TreeNode]: Узел или None, если не найден
        """
        key = self._make_key(node_type, node_id)
        node = self._node_index.get(key)
        
        if node is None:
            log.debug(f"Узел не найден в индексе: {key}")
        else:
            log.debug(f"Узел найден в индексе: {key}")
        
        return node
    
    def get_index_by_id(self, node_type: NodeType, node_id: int) -> QModelIndex:
        """
        Получает QModelIndex для узла по типу и идентификатору.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            QModelIndex: Индекс узла или пустой индекс
        """
        node = self.get_node_by_id(node_type, node_id)
        if node:
            return self._index_of_node(node)
        return QModelIndex()
    
    def has_node(self, node_type: NodeType, node_id: int) -> bool:
        """
        Проверяет, существует ли узел с указанными типом и ID.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            bool: True если узел существует
        """
        key = self._make_key(node_type, node_id)
        return key in self._node_index
		
# client/src/ui/tree_model/tree_model.py
"""
Конкретная реализация модели дерева.
Объединяет все миксины и базовый класс для создания полноценной модели
с поддержкой индексации и управления данными.
"""
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QFont, QBrush
from typing import Any, Optional

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.ui.tree_model.tree_model_base import TreeModelBase
from src.ui.tree_model.tree_model_index import TreeModelIndexMixin
from src.ui.tree_model.tree_model_data import TreeModelDataMixin
from src.models.room import Room
from src.core.cache import DataCache
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModel(
    TreeModelBase,
    TreeModelIndexMixin,
    TreeModelDataMixin
):
    """
    Полноценная модель дерева объектов.
    
    Объединяет функциональность:
    - Базовые методы QAbstractItemModel (TreeModelBase)
    - Индексация узлов для быстрого доступа (TreeModelIndexMixin)
    - Управление данными (TreeModelDataMixin)
    
    Предоставляет:
    - Отображение иерархии комплексов, корпусов, этажей и помещений
    - Кастомные роли для доступа к данным узлов
    - Сигналы для отслеживания загрузки
    - Работу с системой кэширования
    """
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует модель дерева.
        
        Args:
            parent: Родительский объект
        """
        # Инициализация базовых классов
        super().__init__(parent)
        
        # Система кэширования (будет установлена извне)
        self._cache: Optional[DataCache] = None
        
        log.debug("TreeModel: инициализирована")
    
    # ===== Публичные методы =====
    
    def set_cache(self, cache: DataCache) -> None:
        """
        Устанавливает систему кэширования.
        
        Args:
            cache: Система кэширования данных
        """
        self._cache = cache
        log.debug("TreeModel: кэш установлен")
    
    # ===== Переопределение методов QAbstractItemModel =====
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Возвращает данные для отображения элемента.
        
        Args:
            index: Индекс элемента
            role: Роль данных
            
        Returns:
            Any: Данные для указанной роли или None
        """
        if not index.isValid():
            return None
        
        node = self._get_node(index)
        if node is None:
            return None
        
        # Обработка различных ролей
        if role == Qt.DisplayRole:
            return node.get_display_text()
        
        elif role == Qt.FontRole:
            return self._get_node_font(node)
        
        elif role == Qt.ForegroundRole:
            return self._get_node_color(node)
        
        elif role == self.ItemIdRole:
            return node.get_id()
        
        elif role == self.ItemTypeRole:
            return node.node_type.value
        
        elif role == self.ItemDataRole:
            return node.data
        
        return None
    
    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        """
        Определяет, может ли узел иметь дочерние элементы.
        
        Критерий: узел имеет детей ТОЛЬКО если счётчик в скобках > 0.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            bool: True если узел может иметь детей
        """
        parent_node = self._get_node(parent)
        
        # Корневой узел
        if parent_node is None or parent_node == self._root_node:
            return self._root_node.child_count() > 0
        
        # Комнаты никогда не имеют детей
        if parent_node.node_type == NodeType.ROOM:
            return False
        
        # Для остальных типов проверяем соответствующий счётчик
        return self._check_node_has_children(parent_node)
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_node_font(self, node: TreeNode) -> QFont:
        """
        Возвращает шрифт для узла в зависимости от его типа.
        
        Args:
            node: Узел дерева
            
        Returns:
            QFont: Настроенный шрифт
        """
        font = QFont()
        
        if node.node_type == NodeType.COMPLEX:
            font.setBold(True)
            font.setPointSize(font.pointSize() + self._FONT_SIZE_COMPLEX_BOOST)
        elif node.node_type == NodeType.BUILDING:
            font.setBold(True)
        
        return font
    
    def _get_node_color(self, node: TreeNode) -> QBrush:
        """
        Возвращает цвет для узла в зависимости от его типа и статуса.
        
        Args:
            node: Узел дерева
            
        Returns:
            QBrush: Цвет для отображения
        """
        if node.node_type == NodeType.COMPLEX:
            return QBrush(self._COLOR_COMPLEX)
        
        elif node.node_type == NodeType.BUILDING:
            return QBrush(self._COLOR_BUILDING)
        
        elif node.node_type == NodeType.FLOOR:
            return QBrush(self._COLOR_FLOOR)
        
        elif node.node_type == NodeType.ROOM and isinstance(node.data, Room):
            return self._get_room_color(node.data)
        
        return QBrush(self._COLOR_DEFAULT)
    
    def _get_room_color(self, room: Room) -> QBrush:
        """
        Возвращает цвет для помещения в зависимости от его статуса.
        
        Args:
            room: Данные помещения
            
        Returns:
            QBrush: Цвет для отображения
        """
        if room.status_code == 'occupied':
            return QBrush(self._COLOR_ROOM_OCCUPIED)
        elif room.status_code == 'free':
            return QBrush(self._COLOR_ROOM_FREE)
        
        return QBrush(self._COLOR_DEFAULT)
    
    def _check_node_has_children(self, node: TreeNode) -> bool:
        """
        Проверяет, может ли узел иметь детей на основе его данных.
        
        Args:
            node: Узел для проверки
            
        Returns:
            bool: True если узел может иметь детей
        """
        if node.node_type == NodeType.COMPLEX:
            if hasattr(node.data, 'buildings_count'):
                return node.data.buildings_count > 0
        
        elif node.node_type == NodeType.BUILDING:
            if hasattr(node.data, 'floors_count'):
                return node.data.floors_count > 0
        
        elif node.node_type == NodeType.FLOOR:
            if hasattr(node.data, 'rooms_count'):
                return node.data.rooms_count > 0
        
        return False
		
# client/src/ui/tree_model/tree_node.py
"""
Модуль с классом TreeNode, представляющим узел дерева.
Содержит данные, тип, связи с родителем и детьми, а также состояние загрузки.
"""
from typing import Optional, List, Any, TYPE_CHECKING

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.ui.tree_model.node_types import NodeType
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeNode:
    """
    Узел дерева, содержащий данные и связи с родительскими/дочерними узлами.
    
    Атрибуты:
        data: Модель данных (Complex, Building, Floor или Room)
        node_type: Тип узла (NodeType)
        parent: Родительский узел (None для корневого узла)
        children: Список дочерних узлов
        loaded: Флаг, указывающий, загружены ли дочерние элементы
        
    Методы:
        - append_child: Добавление дочернего узла
        - remove_child: Удаление конкретного ребёнка
        - remove_all_children: Удаление всех детей
        - child_at: Получение ребёнка по индексу
        - row: Получение индекса узла в родителе
        - child_count: Количество детей
        - get_display_text: Текст для отображения в дереве
        - get_id: Получение идентификатора узла
        - update_data: Обновление данных узла
    """
    
    # ===== Константы для форматирования текста =====
    _DISPLAY_FORMAT_BUILDING = "{name} ({count})"
    """Формат отображения корпуса с количеством этажей"""
    
    _DISPLAY_FORMAT_FLOOR = "{text} ({count})"
    """Формат отображения этажа с количеством помещений"""
    
    _DISPLAY_FORMAT_COMPLEX_WITH_COUNT = "{name} ({count})"
    """Формат отображения комплекса с количеством корпусов"""
    
    _FLOOR_TEXT_BASEMENT = "Подвал {num}"
    """Текст для подвального этажа"""
    
    _FLOOR_TEXT_GROUND = "Цокольный этаж"
    """Текст для цокольного этажа"""
    
    _FLOOR_TEXT_REGULAR = "Этаж {num}"
    """Текст для обычного этажа"""
    
    _UNKNOWN_TEXT = "???"
    """Текст для неизвестного типа узла"""
    
    def __init__(self, data: Any, node_type: NodeType, 
                 parent: Optional['TreeNode'] = None) -> None:
        """
        Инициализирует узел дерева.
        
        Args:
            data: Модель данных (Complex, Building, Floor или Room)
            node_type: Тип узла
            parent: Родительский узел (по умолчанию None)
        """
        self._data = data
        self._node_type = node_type
        self._parent = parent
        self._children: List['TreeNode'] = []
        self._loaded = False
        
        log.debug(f"TreeNode создан: {node_type} id={self.get_id()}")
    
    # ===== Геттеры =====
    
    @property
    def data(self) -> Any:
        """Возвращает данные узла."""
        return self._data
    
    @property
    def node_type(self) -> NodeType:
        """Возвращает тип узла."""
        return self._node_type
    
    @property
    def parent(self) -> Optional['TreeNode']:
        """Возвращает родительский узел."""
        return self._parent
    
    @property
    def children(self) -> List['TreeNode']:
        """Возвращает список дочерних узлов."""
        return self._children.copy()
    
    @property
    def loaded(self) -> bool:
        """
        Возвращает флаг загрузки дочерних элементов.
        
        Returns:
            True, если дочерние элементы загружены
        """
        return self._loaded
    
    @loaded.setter
    def loaded(self, value: bool) -> None:
        """
        Устанавливает флаг загрузки дочерних элементов.
        
        Args:
            value: Новое значение флага
        """
        self._loaded = value
    
    # ===== Публичные методы =====
    
    def append_child(self, child: 'TreeNode') -> None:
        """
        Добавляет дочерний узел.
        
        Args:
            child: Дочерний узел для добавления
        """
        self._children.append(child)
        log.debug(f"Дочерний узел добавлен к {self._node_type} #{self.get_id()}")
    
    def remove_child(self, child: 'TreeNode') -> bool:
        """
        Удаляет конкретного ребёнка.
        
        Args:
            child: Дочерний узел для удаления
            
        Returns:
            True, если узел был удалён, иначе False
        """
        if child in self._children:
            self._children.remove(child)
            log.debug(f"Дочерний узел удалён из {self._node_type} #{self.get_id()}")
            return True
        return False
    
    def remove_all_children(self) -> None:
        """Удаляет всех детей и сбрасывает флаг загрузки."""
        self._children.clear()
        self._loaded = False
        log.debug(f"Все дочерние узлы удалены из {self._node_type} #{self.get_id()}")
    
    def child_at(self, row: int) -> Optional['TreeNode']:
        """
        Возвращает ребёнка по индексу.
        
        Args:
            row: Индекс ребёнка
            
        Returns:
            TreeNode или None, если индекс вне диапазона
        """
        if 0 <= row < len(self._children):
            return self._children[row]
        return None
    
    def row(self) -> int:
        """
        Возвращает индекс этого узла в родителе.
        
        Returns:
            Индекс узла или 0, если узел не найден в списке детей родителя
        """
        if self._parent:
            try:
                return self._parent._children.index(self)
            except ValueError:
                log.warning(f"Узел {self._node_type} #{self.get_id()} не найден в родителе")
                return 0
        return 0
    
    def child_count(self) -> int:
        """
        Возвращает количество дочерних узлов.
        
        Returns:
            Количество детей
        """
        return len(self._children)
    
    def get_display_text(self) -> str:
        """
        Возвращает текст для отображения в дереве.
        
        Для каждого типа узла применяется своё форматирование:
        - Комплекс: название (количество корпусов)
        - Корпус: название (количество этажей)
        - Этаж: тип этажа (количество помещений)
        - Помещение: номер
        
        Returns:
            str: Отформатированный текст для отображения
        """
        if self._node_type == NodeType.COMPLEX and isinstance(self._data, Complex):
            return self._format_complex_text()
        
        elif self._node_type == NodeType.BUILDING and isinstance(self._data, Building):
            return self._format_building_text()
        
        elif self._node_type == NodeType.FLOOR and isinstance(self._data, Floor):
            return self._format_floor_text()
        
        elif self._node_type == NodeType.ROOM and isinstance(self._data, Room):
            return self._data.number
        
        log.warning(f"Неизвестный тип узла для отображения: {self._node_type}")
        return self._UNKNOWN_TEXT
    
    def get_id(self) -> int:
        """
        Возвращает идентификатор узла.
        
        Returns:
            ID узла или -1, если идентификатор отсутствует
        """
        if hasattr(self._data, 'id'):
            return self._data.id
        log.warning(f"Узел {self._node_type} не имеет атрибута id")
        return -1
    
    def update_data(self, new_data: Any) -> None:
        """
        Обновляет данные узла.
        
        Args:
            new_data: Новые данные для узла
        """
        self._data = new_data
        log.debug(f"Данные узла {self._node_type} #{self.get_id()} обновлены")
    
    # ===== Приватные методы форматирования =====
    
    def _format_complex_text(self) -> str:
        """Форматирует текст для комплекса."""
        data = self._data
        if data.buildings_count > 0:
            return self._DISPLAY_FORMAT_COMPLEX_WITH_COUNT.format(
                name=data.name, 
                count=data.buildings_count
            )
        return data.name
    
    def _format_building_text(self) -> str:
        """Форматирует текст для корпуса."""
        data = self._data
        if data.floors_count > 0:
            return self._DISPLAY_FORMAT_BUILDING.format(
                name=data.name, 
                count=data.floors_count
            )
        return data.name
    
    def _format_floor_text(self) -> str:
        """Форматирует текст для этажа."""
        data = self._data
        
        # Определяем текст этажа в зависимости от номера
        if data.number < 0:
            floor_text = self._FLOOR_TEXT_BASEMENT.format(num=abs(data.number))
        elif data.number == 0:
            floor_text = self._FLOOR_TEXT_GROUND
        else:
            floor_text = self._FLOOR_TEXT_REGULAR.format(num=data.number)
        
        # Добавляем количество помещений, если есть
        if data.rooms_count > 0:
            return self._DISPLAY_FORMAT_FLOOR.format(
                text=floor_text, 
                count=data.rooms_count
            )
        return floor_text
    
    # ===== Специальные методы =====
    
    def __repr__(self) -> str:
        """Возвращает строковое представление узла."""
        return f"TreeNode({self._node_type.value}, id={self.get_id()}, loaded={self._loaded})"
		
# client/src/ui/__init__.py
"""
Инициализатор пакета UI.
Экспортирует все основные компоненты интерфейса.
"""

# Импортируем из новых пакетов
from src.ui.tree import TreeView
from src.ui.details import DetailsPanel
from src.ui.main_window import MainWindow
from src.ui.refresh_menu import RefreshMenu

__all__ = [
    "TreeView",
    "DetailsPanel", 
    "MainWindow",
    "RefreshMenu"
]

# client/src/ui/refresh_menu.py
"""
Меню выбора типа обновления для дерева объектов.
Содержит три пункта с соответствующими горячими клавишами:
- Обновить текущий узел (F5)
- Обновить все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction
from typing import Optional

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class RefreshMenu(QMenu):
    """
    Выпадающее меню для выбора типа обновления данных.
    
    Предоставляет три действия:
    - refresh_current: обновление текущего выбранного узла
    - refresh_visible: обновление всех раскрытых узлов
    - full_reset: полная перезагрузка всех данных
    
    Каждое действие имеет свою горячую клавишу и всплывающую подсказку.
    """
    
    # ===== Сигналы =====
    refresh_current = Signal()
    """Сигнал обновления текущего узла"""
    
    refresh_visible = Signal()
    """Сигнал обновления всех раскрытых узлов"""
    
    full_reset = Signal()
    """Сигнал полной перезагрузки"""
    
    # ===== Константы =====
    _MENU_TITLE = "Обновить"
    """Заголовок меню"""
    
    # Тексты действий
    _ACTION_CURRENT_TEXT = "🔄 Обновить текущий узел"
    """Текст действия обновления текущего узла"""
    
    _ACTION_VISIBLE_TEXT = "🔄 Обновить все раскрытые"
    """Текст действия обновления всех раскрытых узлов"""
    
    _ACTION_RESET_TEXT = "🔄 Полная перезагрузка"
    """Текст действия полной перезагрузки"""
    
    # Подсказки
    _ACTION_CURRENT_TOOLTIP = "Обновить только выбранный узел (F5)"
    """Подсказка для обновления текущего узла"""
    
    _ACTION_VISIBLE_TOOLTIP = "Обновить все раскрытые узлы (Ctrl+F5)"
    """Подсказка для обновления всех раскрытых узлов"""
    
    _ACTION_RESET_TOOLTIP = "Полная перезагрузка всех данных (Ctrl+Shift+F5)"
    """Подсказка для полной перезагрузки"""
    
    # Горячие клавиши
    _SHORTCUT_CURRENT = "F5"
    """Горячая клавиша для обновления текущего узла"""
    
    _SHORTCUT_VISIBLE = "Ctrl+F5"
    """Горячая клавиша для обновления всех раскрытых узлов"""
    
    _SHORTCUT_RESET = "Ctrl+Shift+F5"
    """Горячая клавиша для полной перезагрузки"""
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует меню обновления.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(self._MENU_TITLE, parent)
        
        # Создание действий
        self._create_actions()
        
        # Добавление действий в меню
        self._populate_menu()
        
        log.success("RefreshMenu: создано")
    
    # ===== Приватные методы =====
    
    def _create_actions(self) -> None:
        """Создаёт все действия для меню."""
        self._create_current_action()
        self._create_visible_action()
        self._create_reset_action()
        
        log.debug("RefreshMenu: все действия созданы")
    
    def _create_current_action(self) -> None:
        """Создаёт действие для обновления текущего узла."""
        self._current_action = QAction(self._ACTION_CURRENT_TEXT, self)
        self._current_action.setShortcut(self._SHORTCUT_CURRENT)
        self._current_action.setToolTip(self._ACTION_CURRENT_TOOLTIP)
        self._current_action.triggered.connect(self.refresh_current.emit)
        
        log.debug("RefreshMenu: действие 'текущий узел' создано")
    
    def _create_visible_action(self) -> None:
        """Создаёт действие для обновления всех раскрытых узлов."""
        self._visible_action = QAction(self._ACTION_VISIBLE_TEXT, self)
        self._visible_action.setShortcut(self._SHORTCUT_VISIBLE)
        self._visible_action.setToolTip(self._ACTION_VISIBLE_TOOLTIP)
        self._visible_action.triggered.connect(self.refresh_visible.emit)
        
        log.debug("RefreshMenu: действие 'все раскрытые' создано")
    
    def _create_reset_action(self) -> None:
        """Создаёт действие для полной перезагрузки."""
        self._reset_action = QAction(self._ACTION_RESET_TEXT, self)
        self._reset_action.setShortcut(self._SHORTCUT_RESET)
        self._reset_action.setToolTip(self._ACTION_RESET_TOOLTIP)
        self._reset_action.triggered.connect(self.full_reset.emit)
        
        log.debug("RefreshMenu: действие 'полная перезагрузка' создано")
    
    def _populate_menu(self) -> None:
        """Заполняет меню созданными действиями."""
        self.addAction(self._current_action)
        self.addAction(self._visible_action)
        self.addSeparator()
        self.addAction(self._reset_action)
        
        log.debug("RefreshMenu: меню заполнено")
    
    # ===== Геттеры =====
    
    @property
    def current_action(self) -> QAction:
        """Возвращает действие обновления текущего узла."""
        return self._current_action
    
    @property
    def visible_action(self) -> QAction:
        """Возвращает действие обновления всех раскрытых узлов."""
        return self._visible_action
    
    @property
    def reset_action(self) -> QAction:
        """Возвращает действие полной перезагрузки."""
        return self._reset_action
    
    # ===== Публичные методы =====
    
    def set_actions_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает все действия меню.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._current_action.setEnabled(enabled)
        self._visible_action.setEnabled(enabled)
        self._reset_action.setEnabled(enabled)
        
        status = "включены" if enabled else "отключены"
        log.debug(f"RefreshMenu: все действия {status}")
    
    def set_current_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает действие обновления текущего узла.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._current_action.setEnabled(enabled)
        log.debug(f"RefreshMenu: действие 'текущий узел' {'включено' if enabled else 'отключено'}")
    
    def set_visible_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает действие обновления всех раскрытых узлов.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._visible_action.setEnabled(enabled)
        log.debug(f"RefreshMenu: действие 'все раскрытые' {'включено' if enabled else 'отключено'}")
    
    def set_reset_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает действие полной перезагрузки.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._reset_action.setEnabled(enabled)
        log.debug(f"RefreshMenu: действие 'полная перезагрузка' {'включено' if enabled else 'отключено'}")
		
# client/src/utils/__init__.py
"""
Утилиты для клиентского приложения
"""
from src.utils.logger import Logger

__all__ = ["Logger"]

# client/src/main.py
"""
Точка входа в клиентское приложение Markoff.
Создаёт главное окно, настраивает окружение и запускает event loop.
"""
import os
import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.logger import get_logger, Logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


# ===== Настройка окружения =====
# Убираем информационные сообщения Qt, оставляем предупреждения и ошибки
os.environ["QT_LOGGING_RULES"] = """
    qt.core.plugin.factoryloader.debug=false;
    qt.core.plugin.loader.debug=false;
    qt.core.library.debug=false;
    *.warning=true;
    *.critical=true;
"""

# Настройка логирования (уровень DEBUG для разработки)
Logger.set_level(Logger.DEBUG)
Logger.enable_colors(True)


def setup_application() -> QApplication:
    """
    Создаёт и настраивает экземпляр QApplication.
    
    Returns:
        QApplication: Настроенное приложение
    """
    app = QApplication(sys.argv)
    
    # Устанавливаем мета-информацию приложения
    app.setApplicationName("Markoff Client")
    app.setApplicationDisplayName("Markoff - Управление помещениями")
    app.setOrganizationName("Markoff")
    app.setOrganizationDomain("markoff.local")
    
    log.debug("QApplication создано и настроено")
    return app


def main() -> None:
    """
    Главная функция запуска приложения.
    
    Последовательность действий:
    1. Настройка окружения (QT_LOGGING_RULES)
    2. Создание QApplication
    3. Создание и отображение главного окна
    4. Запуск event loop
    """
    log.startup("Запуск приложения Markoff")
    
    try:
        # Создаём приложение
        app = setup_application()
        
        # Создаём и показываем главное окно
        window = MainWindow()
        window.show()
        
        log.success("Главное окно отображено")
        
        # Запускаем event loop
        exit_code = app.exec()
        
        log.shutdown(f"Приложение завершено с кодом {exit_code}")
        sys.exit(exit_code)
        
    except Exception as error:
        log.error(f"Критическая ошибка при запуске: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
	
	
# client/src/utils/logger.py
"""
Профессиональный, лёгкий и настраиваемый логгер для приложения Markoff.

Особенности:
- Уровни логирования: ERROR, WARNING, INFO, DEBUG
- Категории: API, CACHE, DATA (можно включать/отключать)
- Автоматическое определение имени модуля-источника
- Цветной вывод в терминал (автоматически определяется)
- Разделение форматирования и вывода (принцип единственной ответственности)
- Кэширование логгеров по модулям для производительности

Пример использования:
    from src.utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Сообщение")
    logger.error("Ошибка")
    logger.api("GET /api/data")
"""
from datetime import datetime
import sys
from typing import Optional, Set, Dict, TextIO


class LogFormatter:
    """
    Отвечает за форматирование сообщений лога.
    
    Добавляет временную метку, иконку, уровень, имя модуля и само сообщение.
    Поддерживает цветной вывод для терминалов.
    """
    
    # ===== Константы =====
    
    # Коды цветов ANSI
    _COLOR_CODES: Dict[str, str] = {
        "ERROR": "\033[91m",    # Красный
        "WARNING": "\033[93m",   # Жёлтый
        "INFO": "\033[94m",      # Синий
        "SUCCESS": "\033[92m",   # Зелёный
        "DEBUG": "\033[90m",     # Серый
        "API": "\033[96m",       # Голубой
        "CACHE": "\033[95m",     # Фиолетовый
        "DATA": "\033[36m",      # Бирюзовый
        "STARTUP": "\033[95m",   # Фиолетовый
        "SHUTDOWN": "\033[91m",  # Красный
        "RESET": "\033[0m",      # Сброс цвета
    }
    
    # Иконки для разных уровней и категорий
    _ICONS: Dict[str, str] = {
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "DEBUG": "🔧",
        "API": "📡",
        "DATA": "📦",
        "CACHE": "💾",
        "STARTUP": "🚀",
        "SHUTDOWN": "👋",
    }
    
    _TIMESTAMP_FORMAT = "%H:%M:%S.%f"
    """Формат временной метки"""
    
    _MODULE_WIDTH = 20
    """Максимальная ширина имени модуля для выравнивания"""
    
    _LEVEL_WIDTH = 7
    """Ширина поля уровня для выравнивания"""
    
    def __init__(self, use_colors: bool = False) -> None:
        """
        Инициализирует форматтер логов.
        
        Args:
            use_colors: Включать ли цветной вывод
        """
        self._use_colors = use_colors and sys.stdout.isatty()
        """Флаг использования цветов (только для терминала)"""
    
    def format(self, level: str, module: str, message: str) -> str:
        """
        Форматирует сообщение лога.
        
        Args:
            level: Уровень или категория (ERROR, INFO, API, и т.д.)
            module: Имя модуля-источника
            message: Текст сообщения
            
        Returns:
            str: Отформатированная строка лога
        """
        # Формируем временную метку
        timestamp = datetime.now().strftime(self._TIMESTAMP_FORMAT)[:-3]
        
        # Получаем иконку
        icon = self._ICONS.get(level, "•")
        
        # Укорачиваем имя модуля для выравнивания
        module_short = module.split(".")[-1][:self._MODULE_WIDTH]
        
        # Формируем строку лога
        log_line = (
            f"{timestamp} {icon} [{level:>{self._LEVEL_WIDTH}}] "
            f"[{module_short:<{self._MODULE_WIDTH}}] {message}"
        )
        
        # Добавляем цвета, если нужно
        if self._use_colors and level in self._COLOR_CODES:
            color = self._COLOR_CODES[level]
            reset = self._COLOR_CODES["RESET"]
            log_line = f"{color}{log_line}{reset}"
        
        return log_line


class LogOutput:
    """
    Отвечает за вывод отформатированных сообщений.
    
    Позволяет перенаправлять вывод в разные потоки (файл, консоль и т.д.)
    """
    
    def __init__(self, stream: TextIO = sys.stdout) -> None:
        """
        Инициализирует вывод логов.
        
        Args:
            stream: Поток для вывода (по умолчанию sys.stdout)
        """
        self._stream = stream
    
    def write(self, message: str) -> None:
        """
        Выводит сообщение в поток.
        
        Args:
            message: Сообщение для вывода
        """
        print(message, file=self._stream)
    
    def set_stream(self, stream: TextIO) -> None:
        """
        Изменяет поток вывода.
        
        Args:
            stream: Новый поток для вывода
        """
        self._stream = stream


class Logger:
    """
    Основной класс логгера для модулей приложения.
    
    Предоставляет методы для логирования с разными уровнями и категориями.
    Поддерживает глобальные настройки уровня и отключение категорий.
    
    Уровни (по возрастанию детализации):
    - ERROR: только ошибки
    - WARNING: ошибки и предупреждения
    - INFO: основная информация (по умолчанию)
    - DEBUG: отладочная информация
    
    Категории:
    - api: запросы к API
    - cache: операции с кэшем
    - data: работа с данными
    """
    
    # ===== Константы уровней =====
    ERROR = 1
    """Только критические ошибки"""
    
    WARNING = 2
    """Ошибки и предупреждения"""
    
    INFO = 3
    """Основная информация (по умолчанию)"""
    
    DEBUG = 4
    """Всё, включая отладочную информацию"""
    
    # ===== Константы категорий =====
    CATEGORIES = {"api", "cache", "data"}
    """Доступные категории логирования"""
    
    # ===== Глобальные настройки =====
    _level: int = INFO
    """Текущий уровень логирования"""
    
    _disabled_categories: Set[str] = set()
    """Множество отключённых категорий"""
    
    _formatter = LogFormatter(use_colors=False)
    """Форматтер сообщений"""
    
    _output = LogOutput()
    """Вывод сообщений"""
    
    _loggers: Dict[str, 'Logger'] = {}
    """Кэш созданных логгеров по именам модулей"""
    
    def __init__(self, module_name: str) -> None:
        """
        Инициализирует логгер для конкретного модуля.
        
        Args:
            module_name: Имя модуля (обычно __name__)
        """
        self._module_name = module_name
    
    @classmethod
    def get_logger(cls, module_name: str) -> 'Logger':
        """
        Возвращает или создаёт логгер для указанного модуля.
        
        Args:
            module_name: Имя модуля
            
        Returns:
            Logger: Экземпляр логгера
        """
        if module_name not in cls._loggers:
            cls._loggers[module_name] = Logger(module_name)
        return cls._loggers[module_name]
    
    # ===== Настройка логирования =====
    
    @classmethod
    def set_level(cls, level: int) -> None:
        """
        Устанавливает глобальный уровень логирования.
        
        Args:
            level: Уровень (Logger.ERROR, Logger.INFO и т.д.)
        """
        cls._level = level
    
    @classmethod
    def get_level(cls) -> int:
        """
        Возвращает текущий уровень логирования.
        
        Returns:
            int: Текущий уровень
        """
        return cls._level
    
    @classmethod
    def enable_colors(cls, enable: bool = True) -> None:
        """
        Включает или выключает цветной вывод.
        
        Args:
            enable: True - включить цвета, False - выключить
        """
        cls._formatter = LogFormatter(use_colors=enable)
    
    @classmethod
    def set_output_stream(cls, stream: TextIO) -> None:
        """
        Устанавливает поток для вывода логов.
        
        Args:
            stream: Поток вывода (sys.stdout, открытый файл и т.д.)
        """
        cls._output.set_stream(stream)
    
    @classmethod
    def disable_category(cls, category: str) -> None:
        """
        Отключает указанную категорию логирования.
        
        Args:
            category: Имя категории ('api', 'cache', 'data')
        """
        if category in cls.CATEGORIES:
            cls._disabled_categories.add(category)
    
    @classmethod
    def enable_category(cls, category: str) -> None:
        """
        Включает указанную категорию логирования.
        
        Args:
            category: Имя категории ('api', 'cache', 'data')
        """
        cls._disabled_categories.discard(category)
    
    @classmethod
    def is_category_enabled(cls, category: str) -> bool:
        """
        Проверяет, включена ли указанная категория.
        
        Args:
            category: Имя категории
            
        Returns:
            bool: True если категория включена
        """
        return category not in cls._disabled_categories
    
    @classmethod
    def is_debug_enabled(cls) -> bool:
        """
        Проверяет, включён ли DEBUG уровень.
        
        Returns:
            bool: True если DEBUG уровень активен
        """
        return cls._level >= cls.DEBUG
    
    # ===== Внутренние методы =====
    
    def _log(self, level_name: str, level_val: int, 
             message: str, category: Optional[str] = None) -> None:
        """
        Внутренний метод логирования.
        
        Args:
            level_name: Название уровня для отображения
            level_val: Числовое значение уровня
            message: Сообщение для логирования
            category: Категория (опционально)
        """
        # Проверяем уровень
        if level_val > self._level:
            return
        
        # Проверяем категорию
        if category and not self.is_category_enabled(category):
            return
        
        # Форматируем и выводим
        formatted = self._formatter.format(level_name, self._module_name, message)
        self._output.write(formatted)
    
    # ===== Основные уровни логирования =====
    
    def error(self, message: str) -> None:
        """
        Логирует ошибку (всегда показывается).
        
        Args:
            message: Сообщение об ошибке
        """
        self._log("ERROR", self.ERROR, message)
    
    def warning(self, message: str) -> None:
        """
        Логирует предупреждение.
        
        Args:
            message: Предупреждение
        """
        self._log("WARNING", self.WARNING, message)
    
    def info(self, message: str) -> None:
        """
        Логирует информационное сообщение.
        
        Args:
            message: Информация
        """
        self._log("INFO", self.INFO, message)
    
    def success(self, message: str) -> None:
        """
        Логирует сообщение об успехе (уровень INFO).
        
        Args:
            message: Сообщение об успехе
        """
        self._log("SUCCESS", self.INFO, message)
    
    def debug(self, message: str) -> None:
        """
        Логирует отладочное сообщение.
        
        Args:
            message: Отладочная информация
        """
        self._log("DEBUG", self.DEBUG, message)
    
    # ===== Категории =====
    
    def api(self, message: str) -> None:
        """
        Логирует сообщение категории API.
        
        Args:
            message: Информация о запросе к API
        """
        self._log("API", self.INFO, message, category="api")
    
    def data(self, message: str) -> None:
        """
        Логирует сообщение категории DATA.
        
        Args:
            message: Информация о работе с данными
        """
        self._log("DATA", self.INFO, message, category="data")
    
    def cache(self, message: str) -> None:
        """
        Логирует сообщение категории CACHE.
        
        Args:
            message: Информация о кэшировании
        """
        self._log("CACHE", self.INFO, message, category="cache")
    
    # ===== Специальные события =====
    
    def startup(self, message: str) -> None:
        """
        Логирует событие запуска приложения.
        
        Args:
            message: Информация о запуске
        """
        self._log("STARTUP", self.INFO, message)
    
    def shutdown(self, message: str) -> None:
        """
        Логирует событие завершения приложения.
        
        Args:
            message: Информация о завершении
        """
        self._log("SHUTDOWN", self.INFO, message)


# ===== Быстрый доступ =====

def get_logger(module_name: str) -> Logger:
    """
    Возвращает логгер для указанного модуля.
    
    Args:
        module_name: Имя модуля (обычно __name__)
        
    Returns:
        Logger: Экземпляр логгера
        
    Пример:
        logger = get_logger(__name__)
        logger.info("Сообщение")
    """
    return Logger.get_logger(module_name)
	
	
Твоя задача следовать следующему ТЗ и сделать рефакторин в действующее приложение:
## Техническое Задание: Клиентская часть Markoff
## MVP 3 — Событийно-ориентированная архитектура

### Введение и общая концепция

Данный документ описывает архитектуру клиентского приложения Markoff — десктопного инструмента для управления недвижимостью, работающего в связке с FastAPI бэкендом и PostgreSQL. Клиент реализован на PySide6 и представляет собой событийно-ориентированную систему с чёткими границами ответственности между слоями.

**Ключевая идея:** Приложение строится как реактивная система, где все компоненты общаются через центральную шину событий (Event Bus), данные хранятся в оптимизированном графе сущностей (Entity Graph) с индексами для быстрого доступа, а UI полностью отделён от бизнес-логики через слой контроллеров. Построение структур, удобных для отображения, вынесено в отдельный слой проекций с механизмом debounce для оптимизации производительности.

---

### 1. Общая архитектура клиента

Система состоит из шести основных слоёв, каждый со строго определённой зоной ответственности и направлением зависимостей (зависимости направлены внутрь, от UI к данным):

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (презентация)                  │
│  (Widgets: TreeView, DetailsPanel, MainWindow)              │
└─────────────────────────────┬───────────────────────────────┘
                              │ генерирует команды
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Controllers Layer (логика UI)                │
│  (TreeController, DetailsController, RefreshController)      │
└─────────────────────────────┬───────────────────────────────┘
                              │ подписываются на команды
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Event Bus (core/)                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │  UI Events  │    │System Events│    │Service Events   │  │
│  │  (команды)  │    │  (факты)    │    │(внутренние)     │  │
│  └─────────────┘    └─────────────┘    └─────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ генерируют факты
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Services Layer (бизнес-логика)              │
│  (DataLoader, ConnectionService)                             │
└─────────────────────────────┬───────────────────────────────┘
                              │ читают/пишут
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer (хранение)                      │
│  (Entity Graph с индексами)                                  │
└─────────────────────────────┬───────────────────────────────┘
                              │ оповещают об изменениях
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Projections Layer (представления)            │
│  (TreeProjection с debounce)                                 │
└─────────────────────────────┬───────────────────────────────┘
                              │ обновляют UI
                              └─────────────────────────────────┘
```

#### 1.1 Принципы взаимодействия слоёв

1. **UI Layer** генерирует только команды (`ui.node_selected`, `ui.refresh_requested`) и подписывается на факты (`sys.data_loaded`, `sys.connection_changed`) для обновления своего состояния. UI не содержит бизнес-логики.

2. **Controllers Layer** подписывается на команды пользователя, содержит логику, специфичную для конкретных компонентов (что делать при раскрытии узла, как обработать выбор и т.д.), и при необходимости вызывает сервисы.

3. **Event Bus** — центральная шина, через которую проходят все коммуникации. Обеспечивает слабую связанность компонентов.

4. **Services Layer** подписывается на команды от контроллеров, выполняет операции, требующие внешних ресурсов (HTTP-запросы, работа с файлами), и генерирует факты о результатах. Сервисы не знают о существовании UI.

5. **Data Layer** хранит все сущности в плоском виде с индексами для быстрого доступа по ID и по связям. Не содержит логики, только методы get/set.

6. **Projections Layer** подписывается на факты об изменениях данных, строит из плоского хранилища структуры, удобные для UI (деревья, списки), и обновляет соответствующие компоненты. Использует debounce для оптимизации производительности.

---

### 2. Сквозная инфраструктура

#### 2.1 Утилитарный логгер (utils/logger/)

Логгер вынесен в отдельный пакет на уровень выше клиента и бэкенда, что позволяет использовать его во всех частях проекта единообразно.

**Структура общего логгера:**
- Единый формат логов с временной меткой, иконкой, уровнем и именем модуля
- Поддержка уровней: ERROR, WARNING, INFO, DEBUG
- Категории: API, CACHE, DATA (можно включать/отключать независимо)
- Цветной вывод для терминала (автоматически определяется)
- Возможность перенаправления вывода в файл

**Использование в клиенте и бэкенде:**
```python
from utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Сообщение")
logger.error("Ошибка")
logger.api("GET /api/data")  # для API-запросов
```

---

### 3. Детальное описание компонентов

#### 3.1 Core Layer (ядро)

**3.1.1 Event Bus (core/event_bus.py)**

Центральный элемент системы — единая шина событий с тремя логическими каналами для разных типов сообщений. Реализован как синглтон для обеспечения единой точки входа.

**Каналы событий:**
- **UI Events (команды пользователя):** инициируются действиями пользователя в интерфейсе
- **System Events (факты):** уведомления о событиях в системе (данные загружены, ошибка и т.д.)
- **Service Events (внутренние):** коммуникация между сервисами (опционально)

**Типы событий:**
- `ui.node_selected(type, id)` — пользователь выбрал узел в дереве
- `ui.node_expanded(type, id)` — пользователь раскрыл узел
- `ui.node_collapsed(type, id)` — пользователь свернул узел
- `ui.refresh_requested(mode)` — запрос обновления (current/visible/full)
- `ui.tab_changed(index)` — переключение вкладки в панели деталей
- `sys.data_loading(type, id)` — началась загрузка данных
- `sys.data_loaded(type, id, data)` — данные успешно загружены
- `sys.data_error(type, id, error)` — ошибка загрузки
- `sys.connection_changed(is_online)` — изменилось состояние соединения
- `sys.cache_updated(entity_type, count)` — обновлён кэш

**Механизм работы:**
- Компоненты подписываются на определённые типы событий
- При возникновении события все подписчики получают уведомление
- События иммутабельны — после создания не могут быть изменены
- В debug-режиме все события логируются для отслеживания потока

#### 3.2 Data Layer (хранение данных)

**3.2.1 Entity Graph (data/entity_graph.py)**

Хранит все сущности в плоском виде с оптимизированными индексами для быстрого доступа. Не содержит бизнес-логики, только методы для работы с данными.

**Структура хранения:**
- Хранилище сущностей по типам: `complex`, `building`, `floor`, `room`
- Прямые индексы: для каждого типа и родителя хранится список ID дочерних элементов
- Обратные индексы: для каждого дочернего элемента хранится ID родителя

**Операции:**
- Добавление или обновление сущности с автоматическим обновлением индексов
- Получение сущности по типу и ID (O(1))
- Получение всех дочерних ID для родителя (O(1))
- Получение родителя для дочернего элемента (O(1))
- Получение всех ID данного типа

**Особенности:**
- Все операции атомарны и потокобезопасны (через RLock)
- Данные хранятся в виде готовых моделей (Complex, Building и т.д.)
- При обновлении сущности индексы перестраиваются автоматически

#### 3.3 Services Layer (бизнес-логика)

**3.3.1 Data Loader (services/data_loader.py)**

Сервис для загрузки данных с бэкенда. Подписывается на команды от контроллеров, взаимодействует с API и обновляет Entity Graph.

**Обязанности:**
- Проверка наличия данных в Entity Graph
- Выполнение HTTP-запросов через API-клиент при отсутствии данных
- Обновление графа полученными данными
- Генерация системных событий о результате операции

**Логика работы:**
1. Получает команду с типом узла и ID
2. Определяет, какие дочерние данные нужны (для комплекса — корпуса, для корпуса — этажи и т.д.)
3. Проверяет наличие в графе
4. При необходимости загружает через API
5. Обновляет граф (сохраняет сущности и обновляет индексы)
6. Генерирует событие `sys.data_loaded` с загруженными данными
7. В случае ошибки генерирует `sys.data_error`

**3.3.2 Connection Service (services/connection_service.py)**

Сервис для мониторинга соединения с бэкендом. Работает в фоновом режиме и оповещает систему об изменениях статуса.

**Обязанности:**
- Периодическая проверка доступности бэкенда через `/health` endpoint
- Генерация события `sys.connection_changed` при изменении статуса
- Реагирование на ручные запросы проверки соединения

**Механизм работы:**
- Запускает таймер с интервалом 30 секунд
- При каждом срабатывании выполняет проверку
- При изменении статуса генерирует событие
- UI-компоненты подписываются на это событие для обновления индикаторов

**3.3.3 API Client (services/api_client.py)**

HTTP-клиент для взаимодействия с бэкендом. Не содержит логики, только методы для выполнения запросов.

**Методы:**
- Получение списка комплексов
- Получение корпусов для комплекса
- Получение этажей для корпуса
- Получение помещений для этажа
- Получение детальной информации по конкретному объекту
- Проверка соединения

**Особенности:**
- Возвращает сырые данные (словари), преобразование в модели происходит в других слоях
- Все запросы логируются через категорию API
- Обрабатывает таймауты и сетевые ошибки

#### 3.4 Controllers Layer (логика UI)

Контроллеры — новый слой, отвечающий за логику, специфичную для конкретных компонентов UI. Каждый контроллер подписывается на определённые команды и реализует реакцию на них.

**3.4.1 Base Controller (controllers/base_controller.py)**

Базовый класс для всех контроллеров, предоставляющий:
- Автоматическую подписку на события при инициализации
- Единый механизм отписки для предотвращения утечек памяти
- Вспомогательные методы для работы с событиями

**3.4.2 Tree Controller (controllers/tree_controller.py)**

Управляет логикой дерева объектов.

**Обязанности:**
- Подписка на `ui.node_expanded` — при раскрытии узла проверяет, нужно ли загружать данные, и при необходимости вызывает DataLoader
- Подписка на `ui.node_selected` — при выборе узла проверяет наличие детальных данных и при необходимости загружает их
- Подписка на `sys.data_loaded` — при загрузке данных обновляет модель дерева через проекцию
- Подписка на `ui.refresh_requested` — обрабатывает запросы на обновление разных уровней

**Логика обновления:**
- При `refresh_requested('current')` — инвалидирует данные текущего узла и перезагружает
- При `refresh_requested('visible')` — инвалидирует все раскрытые узлы
- При `refresh_requested('full')` — очищает весь граф и перезагружает комплексы

**3.4.3 Details Controller (controllers/details_controller.py)**

Управляет панелью детальной информации.

**Обязанности:**
- Подписка на `sys.data_loaded` с детальными данными — передаёт данные в панель для отображения
- Подписка на `ui.tab_changed` — при переключении вкладки может инициировать загрузку соответствующих данных (в будущем)
- Подписка на `sys.data_error` — отображает ошибки в панели

**3.4.4 Refresh Controller (controllers/refresh_controller.py)**

Обрабатывает запросы на обновление от горячих клавиш и меню.

**Обязанности:**
- Подписка на команды от горячих клавиш (F5, Ctrl+F5, Ctrl+Shift+F5)
- Преобразование их в унифицированные `ui.refresh_requested` с соответствующим режимом
- Подписка на команды от меню обновления

**3.4.5 Connection Controller (controllers/connection_controller.py)**

Управляет отображением статуса соединения в UI.

**Обязанности:**
- Подписка на `sys.connection_changed`
- Обновление индикаторов в панели инструментов и строке статуса
- Блокировка/разблокировка элементов UI при потере соединения

#### 3.5 Projections Layer (построение представлений)

**3.5.1 Base Projection (projections/base_projection.py)**

Базовый класс для всех проекций с поддержкой debounce и кэширования.

**Механизм debounce:**
- При получении сигнала об изменении данных запускается таймер
- Если в течение заданного интервала (по умолчанию 50 мс) приходят новые сигналы, таймер перезапускается
- По истечении таймера выполняется перестроение проекции
- Это предотвращает многократное перестроение при массовых обновлениях

**Кэширование:**
- Проекция хранит результат последнего построения
- При запросе данных возвращает кэш, если данные не изменились
- Кэш сбрасывается только при реальных изменениях

**3.5.2 Tree Projection (projections/tree_projection.py)**

Строит из плоских данных Entity Graph иерархическое дерево для отображения в TreeView.

**Входные данные:** плоские сущности из графа с индексами связей
**Выходные данные:** готовая иерархическая структура вида:
```
[
  Complex {
    data: Complex,
    children: [
      Building {
        data: Building,
        children: [
          Floor {
            data: Floor,
            children: [Room, Room, ...]
          }
        ]
      }
    ]
  }
]
```

**Правила построения:**
1. Берёт все комплексы из графа
2. Для каждого комплекса находит корпуса через индекс `complex→buildings`
3. Для каждого корпуса находит этажи через индекс `building→floors`
4. Для каждого этажа находит помещения через индекс `floor→rooms`
5. Строит вложенную структуру без какой-либо дополнительной логики

**Особенности:**
- Не содержит условий или бизнес-логики — только группировка
- Перестраивается только при изменениях в графе (через debounce)
- Результат кэшируется до следующего изменения

#### 3.6 UI Layer (презентация)

**3.6.1 Tree Model (ui/tree_model/tree_model.py)**

Модель для QTreeView. Получает уже готовое дерево от TreeProjection и отвечает только за его отображение.

**Обязанности:**
- Предоставление данных для отображения через методы Qt
- Кастомизация внешнего вида (цвета, шрифты) в зависимости от типа узла и статуса
- Обработка запросов на раскрытие узлов (генерация `ui.node_expanded`)
- Обработка выбора узлов (генерация `ui.node_selected`)

**Важно:** Модель больше не управляет данными, не загружает их и не содержит бизнес-логики. Единственный способ изменить данные — вызвать метод `update_tree(new_tree)`.

**3.6.2 Tree View (ui/tree/tree_view.py)**

Визуальный компонент дерева. Содержит минимальную логику:

**Обязанности:**
- Отображение данных из TreeModel
- Проксирование событий мыши (клики, раскрытие, контекстное меню) в команды EventBus
- Применение стилей и настройка внешнего вида

**Генерируемые команды:**
- При раскрытии узла — `ui.node_expanded`
- При сворачивании — `ui.node_collapsed`
- При выборе — `ui.node_selected`
- При вызове контекстного меню — (обрабатывается локально)

**3.6.3 Details Panel (ui/details/details_panel.py)**

Панель детальной информации. Подписывается на события с данными и отображает их.

**Обязанности:**
- Подписка на `sys.data_loaded` с детальными данными (для комнат, этажей и т.д.)
- Отображение информации в зависимости от типа объекта
- Переключение вкладок (генерация `ui.tab_changed`)
- Отображение заглушки, когда ничего не выбрано

**Компоненты панели (переиспользуемые из предыдущей версии):**
- `header_widget.py` — шапка с иконкой, заголовком и статусом
- `info_grid.py` — сетка с парами "поле: значение"
- `placeholder.py` — заглушка для режима "ничего не выбрано"
- `tabs.py` — вкладки Физика/Юрики/Пожарка
- `field_manager.py` — форматирование полей (площадь, статус, тип)
- `display_handlers.py` — логика отображения для разных типов объектов

**3.6.4 Main Window (ui/main_window/main_window.py)**

Композиционный корень приложения. Собирает все компоненты вместе и настраивает подписки.

**Обязанности:**
- Создание всех UI-компонентов в правильном порядке
- Размещение их в окне (splitter, toolbar, status bar)
- Настройка горячих клавиш
- Инициализация сервисов, контроллеров и проекций
- Подписка на события для обновления статус-бара и других глобальных элементов

**Порядок инициализации:**
1. Event Bus (синглтон)
2. Entity Graph
3. Services (DataLoader, ConnectionService)
4. Controllers
5. Projections
6. UI компоненты
7. Настройка подписок между слоями

**Компоненты окна (переиспользуемые):**
- `central_widget.py` — разделитель с деревом и панелью
- `toolbar.py` — панель инструментов с кнопкой обновления
- `status_bar.py` — строка статуса с индикатором соединения
- `shortcuts.py` — горячие клавиши (F5, Ctrl+F5, Ctrl+Shift+F5)

---

### 4. Полные потоки данных

#### 4.1 Загрузка приложения (инициализация)

1. MainWindow создаёт Event Bus, Entity Graph, сервисы, контроллеры и проекции
2. После завершения инициализации генерируется команда `ui.refresh_requested('full')`
3. Контроллеры (в частности, RefreshController) получают команду и передают её в DataLoader
4. DataLoader запрашивает комплексы через API Client
5. API Client выполняет HTTP-запрос к `/physical/`
6. При успехе DataLoader обновляет Entity Graph, добавляя комплексы
7. DataLoader генерирует событие `sys.data_loaded('complex', ...)`
8. TreeProjection (подписан на все `sys.data_loaded`) получает событие и запускает debounce-таймер
9. Через 50 мс (если не было других событий) TreeProjection перестраивает дерево из графа
10. TreeProjection обновляет TreeModel через `update_tree()`
11. TreeView отображает комплексы

#### 4.2 Пользователь раскрывает комплекс

1. Пользователь кликает на значок "+" у комплекса в дереве
2. TreeView генерирует команду `ui.node_expanded('complex', 1)`
3. TreeController получает команду и проверяет, нужно ли загружать корпуса
4. При необходимости TreeController вызывает DataLoader с запросом корпусов для комплекса
5. DataLoader проверяет наличие корпусов в графе, при отсутствии загружает через API
6. DataLoader обновляет граф (добавляет корпуса и обновляет индексы)
7. DataLoader генерирует `sys.data_loaded('building', ...)`
8. TreeProjection перестраивает дерево (debounce)
9. TreeModel обновляется, TreeView отображает корпуса

#### 4.3 Пользователь выбирает помещение

1. Пользователь кликает на помещение в дереве
2. TreeView генерирует команду `ui.node_selected('room', 21)`
3. TreeController получает команду и проверяет наличие детальных данных в графе
4. При отсутствии вызывает DataLoader для загрузки деталей помещения
5. DataLoader загружает данные через API и обновляет граф
6. DataLoader генерирует `sys.data_loaded('room', 21, detailed_data)`
7. DetailsController получает событие и передаёт данные в DetailsPanel
8. DetailsPanel отображает детальную информацию о помещении

#### 4.4 Пользователь нажимает F5 (обновить текущий узел)

1. MainWindow перехватывает нажатие F5 через shortcuts
2. Генерируется команда `ui.refresh_requested('current')`
3. RefreshController получает команду и определяет текущий выбранный узел (через TreeController)
4. RefreshController инвалидирует данные для этого узла в Entity Graph
5. RefreshController инициирует перезагрузку через DataLoader
6. DataLoader загружает свежие данные и обновляет граф
7. Генерируется `sys.data_loaded`, проекция перестраивает дерево
8. UI обновляется с новыми данными

#### 4.5 Потеря соединения с бэкендом

1. ConnectionService периодически (каждые 30 с) проверяет `/health`
2. Один из запросов завершается ошибкой или таймаутом
3. ConnectionService генерирует `sys.connection_changed(False)`
4. ConnectionController получает событие и обновляет:
   - Индикатор в панели инструментов (становится красным)
   - Индикатор в строке статуса (становится красным)
   - Блокирует кнопки, требующие соединения
5. DataLoader при получении команд проверяет статус и либо ставит запросы в очередь, либо игнорирует
6. При восстановлении соединения генерируется `sys.connection_changed(True)`, UI возвращается в нормальный режим

---

### 5. Правила архитектуры (железобетонные)

#### 5.1 Правило команд и фактов
- UI генерирует только команды (запросы на действие)
- Сервисы генерируют только факты (сообщения о свершившихся событиях)
- Контроллеры могут и генерировать команды (в ответ на другие команды), и подписываться на факты
- Никто не генерирует "чужие" события

#### 5.2 Правило тупого хранилища
- Entity Graph не содержит логики — только методы get/set
- Всё, что сложнее "положить/достать" — в сервисы или контроллеры
- Граф не знает о событиях и не генерирует их

#### 5.3 Правило тупой проекции
- Проекция только строит структуру, не анализирует
- Нет условий "если пользователь админ", "если комната архивная"
- Проекция = группировка, ничего больше

#### 5.4 Правило debounce
- Любая операция, которая может вызываться >10 раз в секунду, должна иметь debounce
- Особенно это касается перестроения дерева и обновления UI
- Debounce через QTimer.singleShot с таймаутом 50-100 мс

#### 5.5 Правило контроллеров
- Контроллер создаётся для каждого логического блока UI (дерево, панель деталей)
- Контроллер содержит логику, специфичную для этого блока
- Контроллеры не знают друг о друге, только через события

#### 5.6 Правило иммутабельности событий
- События не изменяются после создания
- Все данные в событиях — копии или иммутабельные структуры
- Никто не может изменить событие после отправки

#### 5.7 Правило единого источника правды
- Entity Graph — единственный источник данных о сущностях
- Никакие другие компоненты не хранят копии данных (только для отображения)
- Проекции кэшируют результаты, но при изменении данных кэш сбрасывается

---

### 6. Обработка ошибок

#### 6.1 Ошибки API
- DataLoader перехватывает все исключения при HTTP-запросах
- Генерирует `sys.data_error` с типом узла, ID и сообщением об ошибке
- Контроллеры подписываются на эти события и могут:
  - Отобразить сообщение в статус-баре
  - Показать диалоговое окно с ошибкой
  - Обновить состояние UI (например, показать, что данные не загружены)
- Entity Graph НЕ обновляется при ошибках

#### 6.2 Ошибки соединения
- ConnectionService отслеживает потерю связи
- При обнаружении проблемы генерирует `sys.connection_changed(False)`
- Все сервисы должны проверять статус соединения перед запросами
- UI блокирует действия, требующие соединения (кнопки становятся неактивными)
- При восстановлении соединения UI разблокируется

#### 6.3 Ошибки в проекциях
- Проекции не должны падать — любая ошибка логируется через логгер, но не ломает UI
- При ошибке проекция возвращает последнее корректное состояние (из кэша)
- Таймер debounce сбрасывается, попытка повторится через некоторое время

#### 6.4 Ошибки в контроллерах
- Контроллеры должны обрабатывать все исключения в своих методах
- Критические ошибки логируются через логгер
- Пользователю показывается понятное сообщение через UI

---

### 7. Производительность и оптимизация

#### 7.1 Индексы в Entity Graph
- Доступ к любой сущности по ID — O(1) через хеш-таблицу
- Получение всех детей родителя — O(1) через готовый список индексов
- Построение дерева проекцией — O(N) только при изменениях

#### 7.2 Debounce для проекций
- 50 мс таймаут для накопления изменений
- При массовых обновлениях (загрузка этажа с 50 комнатами) — 1 перестроение вместо 50
- При быстрых кликах пользователя — UI остаётся отзывчивым

#### 7.3 Кэширование проекций
- Каждая проекция хранит результат последнего построения
- Если данные не менялись — отдаёт кэш без перестроения
- Кэш сбрасывается только при реальных изменениях в графе

#### 7.4 Ленивая загрузка
- Данные загружаются только при необходимости (раскрытии узла)
- Entity Graph заполняется постепенно, нет предзагрузки всего дерева
- Детальная информация загружается только при выборе объекта

#### 7.5 Минимизация обновлений UI
- Контроллеры обновляют UI только при реальных изменениях данных
- Используются сигналы Qt для эффективного обновления
- Избегается полная перерисовка без необходимости

---

### 8. Структура файлов проекта

```
Markoff_2.0/
├── utils/                              # Общие утилиты для всех частей проекта
│   └── logger/
│       ├── __init__.py
│       └── logger.py                    # Единый логгер для клиента и бэкенда
│
├── backend/                             # Бэкенд (FastAPI) — без изменений
│   └── ...
│
└── client/                              # Клиент (PySide6)
    ├── src/
    │   ├── core/                         # Ядро системы
    │   │   ├── __init__.py
    │   │   ├── event_bus.py                # Центральная шина событий
    │   │   └── events.py                    # Константы событий
    │   │
    │   ├── data/                           # Слой хранения данных
    │   │   ├── __init__.py
    │   │   └── entity_graph.py              # Граф сущностей с индексами
    │   │
    │   ├── services/                        # Слой бизнес-логики
    │   │   ├── __init__.py
    │   │   ├── api_client.py                 # HTTP-клиент для бэкенда
    │   │   ├── data_loader.py                 # Загрузка данных и обновление графа
    │   │   └── connection_service.py          # Мониторинг соединения
    │   │
    │   ├── controllers/                      # Слой логики UI
    │   │   ├── __init__.py
    │   │   ├── base_controller.py             # Базовый класс с подпиской
    │   │   ├── tree_controller.py              # Логика дерева
    │   │   ├── details_controller.py           # Логика панели деталей
    │   │   ├── refresh_controller.py           # Логика обновления
    │   │   └── connection_controller.py        # Логика статуса соединения
    │   │
    │   ├── projections/                      # Слой построения представлений
    │   │   ├── __init__.py
    │   │   ├── base_projection.py             # Базовый класс с debounce
    │   │   └── tree_projection.py              # Построение дерева из графа
    │   │
    │   ├── ui/                               # Презентационный слой
    │   │   ├── __init__.py
    │   │   │
    │   │   ├── main_window/                   # Главное окно
    │   │   │   ├── __init__.py
    │   │   │   ├── main_window.py              # Композиционный корень
    │   │   │   ├── components/
    │   │   │   │   ├── __init__.py
    │   │   │   │   ├── central_widget.py        # Разделитель
    │   │   │   │   ├── toolbar.py                # Панель инструментов
    │   │   │   │   └── status_bar.py             # Строка статуса
    │   │   │   └── shortcuts.py                  # Горячие клавиши
    │   │   │
    │   │   ├── tree_model/                     # Модель дерева
    │   │   │   ├── __init__.py
    │   │   │   └── tree_model.py                # QAbstractItemModel
    │   │   │
    │   │   ├── tree/                            # Компоненты дерева
    │   │   │   ├── __init__.py
    │   │   │   └── tree_view.py                  # QTreeView с событиями
    │   │   │
    │   │   └── details/                         # Панель детальной информации
    │   │       ├── __init__.py
    │   │       ├── details_panel.py              # Основная панель
    │   │       ├── header_widget.py              # Шапка
    │   │       ├── info_grid.py                  # Сетка полей
    │   │       ├── placeholder.py                # Заглушка
    │   │       ├── tabs.py                        # Вкладки
    │   │       ├── field_manager.py               # Форматирование полей
    │   │       └── display_handlers.py            # Отображение типов
    │   │
    │   └── models/                            # Модели данных (переиспользованные)
    │       ├── __init__.py
    │       ├── complex.py
    │       ├── building.py
    │       ├── floor.py
    │       └── room.py
    │
    ├── tests/                               # Тесты
    │   ├── core/
    │   │   └── test_event_bus.py
    │   ├── data/
    │   │   └── test_entity_graph.py
    │   ├── services/
    │   │   ├── test_data_loader.py
    │   │   └── test_connection_service.py
    │   ├── controllers/
    │   │   ├── test_tree_controller.py
    │   │   └── test_refresh_controller.py
    │   ├── projections/
    │   │   └── test_tree_projection.py
    │   └── ui/
    │       ├── test_tree_model.py
    │       └── test_details_panel.py
    │
    ├── requirements.txt
    └── main.py                              # Точка входа
```

---

### 9. Критерии готовности

1. **Event Bus** реализован как единый синглтон с тремя каналами, проходит тесты подписки и доставки событий
2. **Entity Graph** реализован с индексами и обратными связями, все операции имеют O(1) сложность
3. **DataLoader** корректно обрабатывает все команды загрузки, обновляет граф и генерирует факты
4. **ConnectionService** корректно отслеживает соединение и генерирует события при изменениях
5. **Контроллеры** правильно подписываются на события и реализуют свою логику
6. **TreeProjection** с debounce правильно строит дерево из графа при изменениях
7. **TreeModel** получает данные от проекции и корректно отображает их в TreeView
8. **TreeView** генерирует правильные команды при действиях пользователя
9. **DetailsPanel** правильно отображает информацию при получении событий с данными
10. **Все коммуникации** между слоями идут только через Event Bus
11. **Логирование** событий работает в debug-режиме, позволяя отслеживать поток
12. **Тесты** покрывают ключевые сценарии: загрузка, раскрытие, выбор, обновление, ошибки
13. **Производительность** не хуже предыдущей версии, UI остаётся отзывчивым
14. **Отсутствуют** прямые вызовы между несвязанными компонентами
15. **Код соответствует** правилам архитектуры (команды/факты, тупое хранилище, debounce и т.д.)

---

### 10. Заключение

Предложенная архитектура превращает клиентское приложение из набора связанных виджетов в **полноценную событийно-ориентированную систему с чёткими границами ответственности**. 

**Ключевые достижения:**
- UI полностью отделён от данных и логики через слой контроллеров
- Данные хранятся в оптимизированной для чтения структуре с O(1) доступом
- Проекции с debounce обеспечивают быструю адаптацию данных под нужды UI
- Event Bus гарантирует слабую связанность всех компонентов
- Единый логгер используется во всех частях проекта
- Система готова к масштабированию и добавлению новых фич без кардинальных переделок

Данная архитектура соответствует лучшим практикам разработки десктоп-приложений и обеспечивает долгосрочную поддерживаемость кода.