# client/src/core/api_client.py
"""
Клиент для работы с backend API
Реальные HTTP запросы к FastAPI бекенду
Теперь поддерживает все уровни иерархии:
- Комплексы (GET /physical/)
- Корпуса (GET /physical/complexes/{complex_id}/buildings)
- Этажи (GET /physical/buildings/{building_id}/floors)
- Помещения (GET /physical/floors/{floor_id}/rooms)
"""
import os
import requests
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urljoin

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class ApiClient:
    """
    Клиент для взаимодействия с backend
    
    Получает URL backend из переменной окружения API_URL
    или использует localhost по умолчанию (для разработки)
    
    Принципы:
    1. Все методы возвращают готовые модели данных
    2. Ошибки API пробрасываются как исключения с понятными сообщениями
    3. Единый point-of-truth для всех API вызовов
    4. Детальное логирование для отладки
    """
    
    # Базовые эндпоинты API
    ENDPOINT_COMPLEXES = "/physical/"
    ENDPOINT_BUILDINGS = "/physical/complexes/{}/buildings"
    ENDPOINT_FLOORS = "/physical/buildings/{}/floors"
    ENDPOINT_ROOMS = "/physical/floors/{}/rooms"
    
    def __init__(self):
        """Инициализация клиента"""
        # Получаем URL из окружения (устанавливается в docker-compose)
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        # Убираем trailing slash если есть
        self.base_url = self.base_url.rstrip('/')
        
        # Создаём сессию для переиспользования соединений
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Markoff-Client/0.2.0',
            'Content-Type': 'application/json'
        })
        
        # Таймауты для запросов (в секундах)
        self.timeout = 10
        
        print(f"✅ API Client инициализирован с базовым URL: {self.base_url}")
    
    def _make_request(self, method: str, path: str, **kwargs) -> Any:
        """
        Внутренний метод для выполнения HTTP запросов
        
        Args:
            method: HTTP метод (GET, POST, etc.)
            path: путь относительно base_url
            **kwargs: дополнительные параметры для requests
            
        Returns:
            JSON ответ от сервера
            
        Raises:
            Exception: с описанием ошибки
        """
        # Формируем полный URL
        if path.startswith('http'):
            url = path
        else:
            url = urljoin(self.base_url + '/', path.lstrip('/'))
        
        # Устанавливаем таймаут по умолчанию, если не указан
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        try:
            print(f"📡 Запрос: {method} {url}")
            
            # Делаем запрос
            response = self.session.request(method, url, **kwargs)
            
            # Логируем статус
            print(f"📡 Статус: {response.status_code}")
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Проверяем, есть ли содержимое
            if response.status_code == 204 or not response.content:
                print("✅ Ответ: пустой (204 No Content)")
                return None
            
            # Парсим JSON
            data = response.json()
            
            # Логируем количество записей
            if isinstance(data, list):
                print(f"✅ Ответ получен: {len(data)} записей")
            elif isinstance(data, dict):
                print(f"✅ Ответ получен: словарь с {len(data)} ключами")
            else:
                print(f"✅ Ответ получен: {type(data).__name__}")
            
            return data
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Ошибка подключения к {url}: {e}")
            raise Exception(f"Не удалось подключиться к серверу по адресу {self.base_url}. Проверьте, запущен ли backend.")
            
        except requests.exceptions.Timeout:
            print(f"❌ Таймаут при запросе к {url}")
            raise Exception("Сервер не отвечает. Превышено время ожидания.")
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP ошибка: {e}")
            status_code = e.response.status_code if hasattr(e, 'response') else 0
            
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
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            raise Exception(f"Ошибка при выполнении запроса: {e}")
            
        except ValueError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            raise Exception("Сервер вернул некорректный JSON")
            
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            raise Exception(f"Непредвиденная ошибка: {e}")
    
    # ===== Методы для комплексов =====
    
    def get_complexes(self) -> List[Complex]:
        """
        Получить список всех комплексов
        
        Returns:
            List[Complex]: список комплексов
            
        Эндпоинт: GET /physical/
        """
        try:
            data = self._make_request('GET', self.ENDPOINT_COMPLEXES)
            
            if not data:
                print("⚠️ Сервер вернул пустой список комплексов")
                return []
            
            complexes = [Complex.from_dict(item) for item in data]
            
            print(f"📦 Загружено комплексов: {len(complexes)}")
            for c in complexes:
                print(f"  - {c.name} (корпусов: {c.buildings_count})")
            
            return complexes
            
        except Exception as e:
            print(f"❌ Ошибка загрузки комплексов: {e}")
            raise
    
    # ===== Методы для корпусов =====
    
    def get_buildings(self, complex_id: int) -> List[Building]:
        """
        Получить список корпусов для конкретного комплекса
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            List[Building]: список корпусов
            
        Эндпоинт: GET /physical/complexes/{complex_id}/buildings
        """
        try:
            endpoint = self.ENDPOINT_BUILDINGS.format(complex_id)
            print(f"🔍 Запрос корпусов для комплекса ID={complex_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                print(f"⚠️ Сервер вернул пустой список корпусов для комплекса {complex_id}")
                return []
            
            buildings = [Building.from_dict(item) for item in data]
            
            print(f"📦 Загружено корпусов: {len(buildings)}")
            for b in buildings:
                print(f"  - {b.name} (этажей: {b.floors_count})")
            
            return buildings
            
        except Exception as e:
            print(f"❌ Ошибка загрузки корпусов для комплекса {complex_id}: {e}")
            raise
    
    # ===== Методы для этажей =====
    
    def get_floors(self, building_id: int) -> List[Floor]:
        """
        Получить список этажей для конкретного корпуса
        
        Args:
            building_id: ID корпуса
            
        Returns:
            List[Floor]: список этажей (отсортированы по номеру)
            
        Эндпоинт: GET /physical/buildings/{building_id}/floors
        """
        try:
            endpoint = self.ENDPOINT_FLOORS.format(building_id)
            print(f"🔍 Запрос этажей для корпуса ID={building_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                print(f"⚠️ Сервер вернул пустой список этажей для корпуса {building_id}")
                return []
            
            floors = [Floor.from_dict(item) for item in data]
            
            # Сортировка по номеру этажа (на всякий случай, хотя бекенд уже сортирует)
            floors.sort(key=lambda x: x.number)
            
            print(f"📦 Загружено этажей: {len(floors)}")
            for f in floors:
                print(f"  - Этаж {f.number} (помещений: {f.rooms_count})")
            
            return floors
            
        except Exception as e:
            print(f"❌ Ошибка загрузки этажей для корпуса {building_id}: {e}")
            raise
    
    # ===== Методы для помещений =====
    
    def get_rooms(self, floor_id: int) -> List[Room]:
        """
        Получить список помещений для конкретного этажа
        
        Args:
            floor_id: ID этажа
            
        Returns:
            List[Room]: список помещений
            
        Эндпоинт: GET /physical/floors/{floor_id}/rooms
        """
        try:
            endpoint = self.ENDPOINT_ROOMS.format(floor_id)
            print(f"🔍 Запрос помещений для этажа ID={floor_id}")
            
            data = self._make_request('GET', endpoint)
            
            if not data:
                print(f"⚠️ Сервер вернул пустой список помещений для этажа {floor_id}")
                return []
            
            rooms = [Room.from_dict(item) for item in data]
            
            # Сортировка по номеру помещения (естественный порядок)
            # Для строк с числами нужно специальное сравнение
            rooms.sort(key=lambda x: self._natural_sort_key(x.number))
            
            print(f"📦 Загружено помещений: {len(rooms)}")
            for r in rooms[:5]:  # Показываем первые 5 для отладки
                status = f" [{r.status_code}]" if r.status_code else ""
                print(f"  - {r.number}{status}")
            if len(rooms) > 5:
                print(f"  - ... и ещё {len(rooms) - 5}")
            
            return rooms
            
        except Exception as e:
            print(f"❌ Ошибка загрузки помещений для этажа {floor_id}: {e}")
            raise
    
    # ===== Вспомогательные методы =====
    
    def _natural_sort_key(self, text: str) -> list:
        """
        Создаёт ключ для естественной сортировки строк с числами
        Например: "101", "101А", "102", "Б12" будут отсортированы правильно
        
        Args:
            text: строка для сортировки
            
        Returns:
            list: ключ для сравнения
        """
        import re
        return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', text)]
    
    def check_connection(self, silent: bool = False) -> bool:
        """
        Проверить соединение с сервером
        
        Args:
            silent: если True - не выводить логи в консоль
            
        Returns:
            bool: True если сервер доступен
        """
        try:
            # Используем /health эндпоинт вместо корневого
            if silent:
                # Временно отключаем вывод логов
                import contextlib
                import io
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    self._make_request('GET', '/health', timeout=3)
            else:
                self._make_request('GET', '/health', timeout=3)
            
            if not silent:
                print("✅ Соединение с сервером установлено")
            return True
        except Exception as e:
            if not silent:
                print(f"❌ Сервер недоступен: {e}")
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Получить информацию о сервере
        
        Returns:
            Dict: информация о версии и статусе
        """
        try:
            data = self._make_request('GET', '/')
            return data
        except Exception as e:
            print(f"❌ Не удалось получить информацию о сервере: {e}")
            return {}
    
    # ===== Методы для отладки =====
    
    def print_endpoints(self) -> None:
        """Выводит все доступные эндпоинты для отладки"""
        print("\n=== Доступные эндпоинты ===")
        print(f"Комплексы:   {self.base_url}{self.ENDPOINT_COMPLEXES}")
        print(f"Корпуса:     {self.base_url}{self.ENDPOINT_BUILDINGS.format('<complex_id>')}")
        print(f"Этажи:       {self.base_url}{self.ENDPOINT_FLOORS.format('<building_id>')}")
        print(f"Помещения:   {self.base_url}{self.ENDPOINT_ROOMS.format('<floor_id>')}")
        print(f"Health:      {self.base_url}/health")
        print(f"Root:        {self.base_url}/")
        print("===========================\n")