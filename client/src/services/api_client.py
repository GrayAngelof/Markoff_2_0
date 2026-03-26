# client/src/services/api_client.py
"""
ApiClient — фасад HTTP клиента.

Единственный публичный компонент API слоя.
Все HTTP запросы проходят через этот класс.

Ответственность:
- Выполнение запросов к API через HttpClient
- Преобразование JSON в модели через converters
- Логирование всех запросов через log.api()
- Сохранение traceback при ошибках

НЕ отвечает за:
- Формирование URL (это endpoints.py)
- Низкоуровневый HTTP (это HttpClient)
- Кэширование (это Data слой)

Важно: Все публичные методы возвращают модели (или списки моделей),
а не сырые словари. Исключения пробрасываются с сохранением traceback.
"""

from typing import List, Optional

from src.core.types.nodes import NodeID
from src.models import Complex, Building, Floor, Room, Counterparty, ResponsiblePerson

from src.services.api.http_client import HttpClient
from src.services.api.endpoints import Endpoints
from src.services.api.converters import (
    to_complex_list, to_building_list, to_floor_list, to_room_list,
    to_complex, to_building, to_floor, to_room,
    to_counterparty, to_responsible_person_list,
)
from src.services.api.errors import (
    ApiError, ConnectionError, NotFoundError, TimeoutError,
    ClientError, ServerError
)
from utils.logger import get_logger

log = get_logger(__name__)


class ApiClient:
    """
    Фасад API клиента.
    
    Все методы логируют запросы через log.api() и сохраняют traceback.
    
    Пример использования:
        api = ApiClient()
        
        # Списочные методы
        complexes = api.get_complexes()
        buildings = api.get_buildings(42)
        
        # Детальные методы
        complex_detail = api.get_complex_detail(42)
        building_detail = api.get_building_detail(101)
        
        # Контрагенты
        owner = api.get_counterparty(1001)
        persons = api.get_responsible_persons(1001)
        
        # Мониторинг
        if api.check_connection():
            print("Server is online")
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Инициализирует API клиент.
        
        Args:
            base_url: Базовый URL сервера. Если не указан,
                     используется localhost:8000 или API_URL из окружения.
        """
        self._http = HttpClient(base_url)
        log.system(f"ApiClient инициализирован, базовый URL: {self._http._base_url}")
    
    # ===== Списочные методы =====
    
    def get_complexes(self) -> List[Complex]:
        """
        GET /physical/ → список всех комплексов.
        
        Returns:
            List[Complex]: Список комплексов (может быть пустым)
            
        Raises:
            ConnectionError: Сервер недоступен
            TimeoutError: Таймаут запроса
            ApiError: Другая ошибка API
        """
        try:
            data = self._http.get(Endpoints.complexes())
            result = to_complex_list(data) if data else []
            log.api(f"GET complexes: {len(result)} записей")
            return result
        except ConnectionError:
            log.error("Не удалось получить комплексы: сервер недоступен")
            raise
        except NotFoundError:
            # 404 на /physical/ — странно, но не фатально
            log.warning("GET complexes вернул 404, считаем список пустым")
            return []
        except Exception as e:
            log.error(f"Ошибка загрузки комплексов: {e}")
            raise ApiError(f"Failed to load complexes: {e}") from e
    
    def get_buildings(self, complex_id: NodeID) -> List[Building]:
        """
        GET /physical/complexes/{id}/buildings → список корпусов комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            List[Building]: Список корпусов (может быть пустым)
        """
        try:
            data = self._http.get(Endpoints.buildings(complex_id))
            result = to_building_list(data) if data else []
            log.api(f"GET buildings для комплекса {complex_id}: {len(result)} записей")
            return result
        except NotFoundError:
            # У комплекса может не быть корпусов
            log.debug(f"Нет корпусов для комплекса {complex_id}")
            return []
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке корпусов комплекса {complex_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки корпусов для комплекса {complex_id}: {e}")
            raise ApiError(f"Failed to load buildings for complex {complex_id}: {e}") from e
    
    def get_floors(self, building_id: NodeID) -> List[Floor]:
        """GET /physical/buildings/{id}/floors → список этажей корпуса."""
        try:
            data = self._http.get(Endpoints.floors(building_id))
            result = to_floor_list(data) if data else []
            log.api(f"GET floors для корпуса {building_id}: {len(result)} записей")
            return result
        except NotFoundError:
            log.debug(f"Нет этажей для корпуса {building_id}")
            return []
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке этажей корпуса {building_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки этажей для корпуса {building_id}: {e}")
            raise ApiError(f"Failed to load floors for building {building_id}: {e}") from e
    
    def get_rooms(self, floor_id: NodeID) -> List[Room]:
        """GET /physical/floors/{id}/rooms → список помещений этажа."""
        try:
            data = self._http.get(Endpoints.rooms(floor_id))
            result = to_room_list(data) if data else []
            log.api(f"GET rooms для этажа {floor_id}: {len(result)} записей")
            return result
        except NotFoundError:
            log.debug(f"Нет помещений для этажа {floor_id}")
            return []
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке помещений этажа {floor_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки помещений для этажа {floor_id}: {e}")
            raise ApiError(f"Failed to load rooms for floor {floor_id}: {e}") from e
    
    # ===== Детальные методы =====
    
    def get_complex_detail(self, complex_id: NodeID) -> Optional[Complex]:
        """
        GET /physical/complexes/{id} → детальная информация о комплексе.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            Optional[Complex]: Комплекс с деталями или None, если не найден
        """
        try:
            data = self._http.get(Endpoints.complex_detail(complex_id))
            result = to_complex(data)
            log.api(f"GET complex detail {complex_id}: успешно")
            return result
        except NotFoundError:
            log.info(f"Комплекс {complex_id} не найден")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке комплекса {complex_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки комплекса {complex_id}: {e}")
            raise ApiError(f"Failed to load complex detail {complex_id}: {e}") from e
    
    def get_building_detail(self, building_id: NodeID) -> Optional[Building]:
        """GET /physical/buildings/{id} → детальная информация о корпусе."""
        try:
            data = self._http.get(Endpoints.building_detail(building_id))
            result = to_building(data)
            log.api(f"GET building detail {building_id}: успешно")
            return result
        except NotFoundError:
            log.info(f"Корпус {building_id} не найден")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке корпуса {building_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки корпуса {building_id}: {e}")
            raise ApiError(f"Failed to load building detail {building_id}: {e}") from e
    
    def get_floor_detail(self, floor_id: NodeID) -> Optional[Floor]:
        """GET /physical/floors/{id} → детальная информация об этаже."""
        try:
            data = self._http.get(Endpoints.floor_detail(floor_id))
            result = to_floor(data)
            log.api(f"GET floor detail {floor_id}: успешно")
            return result
        except NotFoundError:
            log.info(f"Этаж {floor_id} не найден")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке этажа {floor_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки этажа {floor_id}: {e}")
            raise ApiError(f"Failed to load floor detail {floor_id}: {e}") from e
    
    def get_room_detail(self, room_id: NodeID) -> Optional[Room]:
        """GET /physical/rooms/{id} → детальная информация о помещении."""
        try:
            data = self._http.get(Endpoints.room_detail(room_id))
            result = to_room(data)
            log.api(f"GET room detail {room_id}: успешно")
            return result
        except NotFoundError:
            log.info(f"Помещение {room_id} не найдено")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке помещения {room_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки помещения {room_id}: {e}")
            raise ApiError(f"Failed to load room detail {room_id}: {e}") from e
    
    # ===== Контрагенты =====
    
    def get_counterparty(self, counterparty_id: NodeID) -> Optional[Counterparty]:
        """
        GET /counterparties/{id} → информация о контрагенте.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            Optional[Counterparty]: Контрагент или None, если не найден
        """
        try:
            data = self._http.get(Endpoints.counterparty(counterparty_id))
            result = to_counterparty(data)
            log.api(f"GET counterparty {counterparty_id}: успешно")
            return result
        except NotFoundError:
            log.debug(f"Контрагент {counterparty_id} не найден")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке контрагента {counterparty_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки контрагента {counterparty_id}: {e}")
            raise ApiError(f"Failed to load counterparty {counterparty_id}: {e}") from e
    
    def get_responsible_persons(self, counterparty_id: NodeID) -> List[ResponsiblePerson]:
        """
        GET /counterparties/{id}/persons → список ответственных лиц.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            List[ResponsiblePerson]: Список ответственных лиц (может быть пустым)
        """
        try:
            data = self._http.get(Endpoints.responsible_persons(counterparty_id))
            result = to_responsible_person_list(data) if data else []
            log.api(f"GET responsible persons для контрагента {counterparty_id}: {len(result)} записей")
            return result
        except NotFoundError:
            log.debug(f"Нет ответственных лиц для контрагента {counterparty_id}")
            return []
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке ответственных лиц для контрагента {counterparty_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки ответственных лиц: {e}")
            raise ApiError(f"Failed to load responsible persons: {e}") from e
    
    # ===== Мониторинг =====
    
    def check_connection(self, timeout: int = 3) -> bool:
        """
        Проверяет доступность сервера.
        
        Args:
            timeout: Таймаут в секундах (по умолчанию 3)
            
        Returns:
            bool: True если сервер доступен, False в противном случае
        """
        try:
            self._http.get(Endpoints.health(), timeout=timeout)
            log.link("Сервер доступен")
            return True
        except (ConnectionError, TimeoutError):
            log.error("Сервер недоступен")
            return False
        except Exception as e:
            log.error(f"Неожиданная ошибка при проверке соединения: {e}")
            return False
    
    def get_server_info(self) -> dict:
        """
        GET / → информация о сервере (версия, статус).
        
        Returns:
            dict: Информация о сервере или пустой словарь при ошибке
        """
        try:
            data = self._http.get(Endpoints.root())
            result = data if isinstance(data, dict) else {}
            log.api(f"GET server info: версия {result.get('version', 'unknown')}")
            return result
        except Exception as e:
            log.debug(f"Не удалось получить информацию о сервере: {e}")
            return {}
    
    # ===== Управление =====
    
    def close(self) -> None:
        """Закрывает HTTP сессию."""
        self._http.close()
        log.debug("ApiClient закрыт")
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает сессию при выходе из контекста."""
        self.close()