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
from utils.logger import get_logger


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