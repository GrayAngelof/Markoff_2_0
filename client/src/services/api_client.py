# client/src/services/api_client.py
"""
HTTP-клиент для взаимодействия с backend API.
Чистый клиент - только запросы, никакой логики.
Возвращает сырые словари, преобразование в модели происходит в DataLoader.
"""
import os
import requests
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ApiClient:
    """
    HTTP-клиент для backend API.
    
    Особенности:
    - Не содержит бизнес-логики
    - Возвращает сырые данные (dict)
    - Все ошибки пробрасываются как исключения
    - Детальное логирование каждого запроса
    """
    
    # ===== Эндпоинты физической структуры =====
    ENDPOINT_COMPLEXES = "/physical/"
    ENDPOINT_BUILDINGS = "/physical/complexes/{}/buildings"
    ENDPOINT_FLOORS = "/physical/buildings/{}/floors"
    ENDPOINT_ROOMS = "/physical/floors/{}/rooms"
    ENDPOINT_COMPLEX_DETAIL = "/physical/complexes/{}"
    ENDPOINT_BUILDING_DETAIL = "/physical/buildings/{}"
    ENDPOINT_FLOOR_DETAIL = "/physical/floors/{}"
    ENDPOINT_ROOM_DETAIL = "/physical/rooms/{}"
    
    # ===== Эндпоинты словарей и справочников =====
    ENDPOINT_COUNTERPARTIES = "/dictionary/counterparties"
    ENDPOINT_COUNTERPARTY_DETAIL = "/dictionary/counterparties/{}"
    ENDPOINT_COUNTERPARTY_PERSONS = "/dictionary/counterparties/{}/persons"
    ENDPOINT_COUNTERPARTY_TYPES = "/dictionary/counterparty-types"
    ENDPOINT_ROLE_CATALOG = "/dictionary/roles"
    ENDPOINT_BUILDING_STATUSES = "/dictionary/building-statuses"
    ENDPOINT_ROOM_STATUSES = "/dictionary/room-statuses"
    ENDPOINT_PHYSICAL_ROOM_TYPES = "/dictionary/physical-room-types"
    
    # ===== Системные эндпоинты =====
    ENDPOINT_HEALTH = "/health"
    ENDPOINT_SERVER_INFO = "/"
    
    # ===== Настройки =====
    DEFAULT_TIMEOUT = 10
    DEFAULT_USER_AGENT = "Markoff-Client/3.0"
    
    def __init__(self) -> None:
        """Инициализирует клиент API."""
        # Получаем URL из окружения
        self._base_url = os.getenv("API_URL", "http://localhost:8000").rstrip('/')
        
        # Сессия для переиспользования соединений
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
            'User-Agent': self.DEFAULT_USER_AGENT,
            'Content-Type': 'application/json'
        })
        
        log.info(f"ApiClient инициализирован с базовым URL: {self._base_url}")
    
    # ===== Приватные методы =====
    
    def _build_url(self, path: str) -> str:
        """Формирует полный URL из относительного пути."""
        if path.startswith('http'):
            return path
        return urljoin(self._base_url + '/', path.lstrip('/'))
    
    def _make_request(self, method: str, path: str, **kwargs) -> Any:
        """
        Внутренний метод выполнения запроса.
        
        Returns:
            dict или list: распарсенный JSON ответа
            
        Raises:
            Exception: с описанием ошибки
        """
        url = self._build_url(path)
        
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.DEFAULT_TIMEOUT
        
        log.api(f"{method} {url}")
        
        try:
            response = self._session.request(method, url, **kwargs)
            log.api(f"Статус: {response.status_code}")
            
            response.raise_for_status()
            
            if response.status_code == 204 or not response.content:
                return None
            
            data = response.json()
            
            # Логируем размер ответа
            if isinstance(data, list):
                log.api(f"Ответ: {len(data)} записей")
            elif isinstance(data, dict):
                log.api(f"Ответ: словарь с {len(data)} ключами")
            
            return data
            
        except requests.exceptions.ConnectionError as e:
            log.error(f"Ошибка подключения к {url}: {e}")
            raise Exception(f"Не удалось подключиться к серверу {self._base_url}")
            
        except requests.exceptions.Timeout:
            log.error(f"Таймаут при запросе к {url}")
            raise Exception("Сервер не отвечает (таймаут)")
            
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if hasattr(e, 'response') else 0
            log.error(f"HTTP ошибка {status} при запросе к {url}")
            
            if status == 404:
                raise Exception("Ресурс не найден (404)")
            elif status == 422:
                try:
                    details = e.response.json()
                    raise Exception(f"Ошибка валидации: {details}")
                except:
                    raise Exception("Ошибка валидации данных (422)")
            elif status == 500:
                raise Exception("Внутренняя ошибка сервера (500)")
            else:
                raise Exception(f"Ошибка сервера: HTTP {status}")
                
        except Exception as e:
            log.error(f"Неизвестная ошибка: {e}")
            raise
    
    # ===== Методы для физической структуры =====
    
    def get_complexes(self) -> List[dict]:
        """Получает список всех комплексов."""
        return self._make_request('GET', self.ENDPOINT_COMPLEXES)
    
    def get_buildings(self, complex_id: int, include_owner: bool = False) -> List[dict]:
        """
        Получает корпуса комплекса.
        
        Args:
            complex_id: ID комплекса
            include_owner: если True, включает данные о владельце
        """
        endpoint = self.ENDPOINT_BUILDINGS.format(complex_id)
        params = {'include': 'owner'} if include_owner else None
        return self._make_request('GET', endpoint, params=params)
    
    def get_floors(self, building_id: int) -> List[dict]:
        """Получает этажи корпуса."""
        endpoint = self.ENDPOINT_FLOORS.format(building_id)
        return self._make_request('GET', endpoint)
    
    def get_rooms(self, floor_id: int) -> List[dict]:
        """Получает помещения этажа."""
        endpoint = self.ENDPOINT_ROOMS.format(floor_id)
        return self._make_request('GET', endpoint)
    
    def get_complex_detail(self, complex_id: int, include_owner: bool = False) -> Optional[dict]:
        """
        Детальная информация о комплексе.
        
        Args:
            complex_id: ID комплекса
            include_owner: если True, включает данные о владельце
        """
        endpoint = self.ENDPOINT_COMPLEX_DETAIL.format(complex_id)
        params = {'include': 'owner'} if include_owner else None
        return self._make_request('GET', endpoint, params=params)
    
    def get_building_detail(self, building_id: int, include_owner: bool = False) -> Optional[dict]:
        """
        Детальная информация о корпусе.
        
        Args:
            building_id: ID корпуса
            include_owner: если True, включает данные о владельце
        """
        endpoint = self.ENDPOINT_BUILDING_DETAIL.format(building_id)
        params = {'include': 'owner'} if include_owner else None
        return self._make_request('GET', endpoint, params=params)
    
    def get_floor_detail(self, floor_id: int) -> Optional[dict]:
        """Детальная информация об этаже."""
        endpoint = self.ENDPOINT_FLOOR_DETAIL.format(floor_id)
        return self._make_request('GET', endpoint)
    
    def get_room_detail(self, room_id: int, include_tenant: bool = False) -> Optional[dict]:
        """
        Детальная информация о помещении.
        
        Args:
            room_id: ID помещения
            include_tenant: если True, включает данные об арендаторе
        """
        endpoint = self.ENDPOINT_ROOM_DETAIL.format(room_id)
        params = {'include': 'tenant'} if include_tenant else None
        return self._make_request('GET', endpoint, params=params)
    
    # ===== Методы для работы с контрагентами =====
    
    def get_counterparties(self, type_id: Optional[int] = None) -> List[dict]:
        """
        Получает список контрагентов.
        
        Args:
            type_id: если указан, фильтрует по типу контрагента
        """
        params = {}
        if type_id:
            params['type_id'] = type_id
        return self._make_request('GET', self.ENDPOINT_COUNTERPARTIES, params=params)
    
    def get_counterparty(self, counterparty_id: int) -> Optional[dict]:
        """Получает информацию о контрагенте по ID."""
        endpoint = self.ENDPOINT_COUNTERPARTY_DETAIL.format(counterparty_id)
        return self._make_request('GET', endpoint)
    
    def get_responsible_persons(self, counterparty_id: int) -> List[dict]:
        """Получает список ответственных лиц для контрагента."""
        endpoint = self.ENDPOINT_COUNTERPARTY_PERSONS.format(counterparty_id)
        return self._make_request('GET', endpoint)
    
    def get_landlords(self) -> List[dict]:
        """Получает список всех собственников/арендодателей."""
        # type_id = 1 для собственников (нужно уточнить в БД)
        return self.get_counterparties(type_id=1)
    
    def get_tenants(self) -> List[dict]:
        """Получает список всех арендаторов."""
        # type_id = 2 для арендаторов (нужно уточнить в БД)
        return self.get_counterparties(type_id=2)
    
    # ===== Методы для справочников =====
    
    def get_counterparty_types(self) -> List[dict]:
        """Получает список типов контрагентов."""
        return self._make_request('GET', self.ENDPOINT_COUNTERPARTY_TYPES)
    
    def get_role_catalog(self) -> List[dict]:
        """Получает каталог ролей."""
        return self._make_request('GET', self.ENDPOINT_ROLE_CATALOG)
    
    def get_building_statuses(self) -> List[dict]:
        """Получает список статусов зданий."""
        return self._make_request('GET', self.ENDPOINT_BUILDING_STATUSES)
    
    def get_room_statuses(self) -> List[dict]:
        """Получает список статусов помещений."""
        return self._make_request('GET', self.ENDPOINT_ROOM_STATUSES)
    
    def get_physical_room_types(self) -> List[dict]:
        """Получает список типов помещений."""
        return self._make_request('GET', self.ENDPOINT_PHYSICAL_ROOM_TYPES)
    
    # ===== Системные методы =====
    
    def check_connection(self) -> bool:
        """
        Проверяет соединение с сервером.
        
        Returns:
            bool: True если сервер доступен
        """
        try:
            self._make_request('GET', self.ENDPOINT_HEALTH, timeout=3)
            return True
        except:
            return False
    
    def get_server_info(self) -> dict:
        """Получает информацию о сервере."""
        try:
            return self._make_request('GET', self.ENDPOINT_SERVER_INFO)
        except:
            return {}