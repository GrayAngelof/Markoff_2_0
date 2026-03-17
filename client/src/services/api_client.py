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
    
    # ===== Эндпоинты =====
    ENDPOINT_COMPLEXES = "/physical/"
    ENDPOINT_BUILDINGS = "/physical/complexes/{}/buildings"
    ENDPOINT_FLOORS = "/physical/buildings/{}/floors"
    ENDPOINT_ROOMS = "/physical/floors/{}/rooms"
    ENDPOINT_COMPLEX_DETAIL = "/physical/complexes/{}"
    ENDPOINT_BUILDING_DETAIL = "/physical/buildings/{}"
    ENDPOINT_FLOOR_DETAIL = "/physical/floors/{}"
    ENDPOINT_ROOM_DETAIL = "/physical/rooms/{}"
    ENDPOINT_HEALTH = "/health"
    
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
    
    # ===== Публичные методы =====
    
    def get_complexes(self) -> List[dict]:
        """Получает список всех комплексов."""
        return self._make_request('GET', self.ENDPOINT_COMPLEXES)
    
    def get_buildings(self, complex_id: int) -> List[dict]:
        """Получает корпуса комплекса."""
        endpoint = self.ENDPOINT_BUILDINGS.format(complex_id)
        return self._make_request('GET', endpoint)
    
    def get_floors(self, building_id: int) -> List[dict]:
        """Получает этажи корпуса."""
        endpoint = self.ENDPOINT_FLOORS.format(building_id)
        return self._make_request('GET', endpoint)
    
    def get_rooms(self, floor_id: int) -> List[dict]:
        """Получает помещения этажа."""
        endpoint = self.ENDPOINT_ROOMS.format(floor_id)
        return self._make_request('GET', endpoint)
    
    def get_complex_detail(self, complex_id: int) -> Optional[dict]:
        """Детальная информация о комплексе."""
        endpoint = self.ENDPOINT_COMPLEX_DETAIL.format(complex_id)
        return self._make_request('GET', endpoint)
    
    def get_building_detail(self, building_id: int) -> Optional[dict]:
        """Детальная информация о корпусе."""
        endpoint = self.ENDPOINT_BUILDING_DETAIL.format(building_id)
        return self._make_request('GET', endpoint)
    
    def get_floor_detail(self, floor_id: int) -> Optional[dict]:
        """Детальная информация об этаже."""
        endpoint = self.ENDPOINT_FLOOR_DETAIL.format(floor_id)
        return self._make_request('GET', endpoint)
    
    def get_room_detail(self, room_id: int) -> Optional[dict]:
        """Детальная информация о помещении."""
        endpoint = self.ENDPOINT_ROOM_DETAIL.format(room_id)
        return self._make_request('GET', endpoint)
    
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
            return self._make_request('GET', '/')
        except:
            return {}