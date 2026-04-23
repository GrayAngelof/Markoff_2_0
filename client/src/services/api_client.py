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

Важно: Все публичные методы возвращают модели (или списки моделей),
а не сырые словари. Исключения пробрасываются с сохранением traceback.

Разделение на Tree и Detail DTO:
- get_*_tree() — для дерева (минимальные данные)
- get_*_detail() — для панели деталей (полные данные)
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional

from src.core.types.nodes import NodeID
from src.models import (
    ComplexTreeDTO,
    ComplexDetailDTO,
    BuildingTreeDTO,
    BuildingDetailDTO,
    FloorTreeDTO,
    FloorDetailDTO,
    RoomTreeDTO,
    RoomDetailDTO,
)
from src.services.api.converters import (
    to_complex_tree_list,
    to_building_tree_list,
    to_floor_tree_list,
    to_room_tree_list,
    to_complex_detail,
    to_building_detail,
    to_floor_detail,
    to_room_detail,
)
from src.services.api.endpoints import Endpoints
from src.services.api.errors import (
    ApiError,
    ConnectionError,
    NotFoundError,
    TimeoutError,
)
from src.services.api.http_client import HttpClient
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class ApiClient:
    """
    Фасад API клиента.

    Все методы логируют запросы через log.api() и сохраняют traceback.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, base_url: Optional[str] = None) -> None:
        """Инициализирует API клиент."""
        log.info("Инициализация ApiClient")
        self._http = HttpClient(base_url)
        log.system(f"ApiClient инициализирован, базовый URL: {self._http._base_url}")

    def close(self) -> None:
        """Закрывает HTTP сессию."""
        self._http.close()
        log.debug("ApiClient закрыт")

    def __enter__(self) -> 'ApiClient':
        """Поддержка контекстного менеджера."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Закрывает сессию при выходе из контекста."""
        self.close()

    # ---- ДЕРЕВО (TREE) - МИНИМАЛЬНЫЕ ДАННЫЕ ----
    def get_complexes_tree(self) -> List[ComplexTreeDTO]:
        """GET /physical/ → список комплексов для дерева."""
        try:
            data = self._http.get(Endpoints.complexes())
            result = to_complex_tree_list(data) if data else []
            log.api(f"GET complexes tree: {len(result)} записей")
            return result
        except NotFoundError:
            log.warning("GET complexes tree вернул 404, считаем список пустым")
            return []
        except ConnectionError:
            log.error("Не удалось получить комплексы: сервер недоступен")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки комплексов: {e}")
            raise ApiError(f"Failed to load complexes tree: {e}") from e

    def get_buildings_tree(self, complex_id: NodeID) -> List[BuildingTreeDTO]:
        """GET /physical/complexes/{id}/buildings → список корпусов для дерева."""
        try:
            data = self._http.get(Endpoints.buildings(complex_id))
            result = to_building_tree_list(data) if data else []
            log.api(f"GET buildings tree для комплекса {complex_id}: {len(result)} записей")
            return result
        except NotFoundError:
            log.debug(f"Нет корпусов для комплекса {complex_id}")
            return []
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке корпусов комплекса {complex_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки корпусов для комплекса {complex_id}: {e}")
            raise ApiError(f"Failed to load buildings tree for complex {complex_id}: {e}") from e

    def get_floors_tree(self, building_id: NodeID) -> List[FloorTreeDTO]:
        """GET /physical/buildings/{id}/floors → список этажей для дерева."""
        try:
            data = self._http.get(Endpoints.floors(building_id))
            result = to_floor_tree_list(data) if data else []
            log.api(f"GET floors tree для корпуса {building_id}: {len(result)} записей")
            return result
        except NotFoundError:
            log.debug(f"Нет этажей для корпуса {building_id}")
            return []
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке этажей корпуса {building_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки этажей для корпуса {building_id}: {e}")
            raise ApiError(f"Failed to load floors tree for building {building_id}: {e}") from e

    def get_rooms_tree(self, floor_id: NodeID) -> List[RoomTreeDTO]:
        """GET /physical/floors/{id}/rooms → список помещений для дерева."""
        try:
            data = self._http.get(Endpoints.rooms(floor_id))
            result = to_room_tree_list(data) if data else []
            log.api(f"GET rooms tree для этажа {floor_id}: {len(result)} записей")
            return result
        except NotFoundError:
            log.debug(f"Нет помещений для этажа {floor_id}")
            return []
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке помещений этажа {floor_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки помещений для этажа {floor_id}: {e}")
            raise ApiError(f"Failed to load rooms tree for floor {floor_id}: {e}") from e

    # ---- ДЕТАЛИ (DETAIL) - ПОЛНЫЕ ДАННЫЕ ----
    def get_complex_detail(self, complex_id: NodeID) -> Optional[ComplexDetailDTO]:
        """GET /physical/complexes/{id} → детальная информация о комплексе."""
        try:
            data = self._http.get(Endpoints.complex_detail(complex_id))
            result = to_complex_detail(data)
            log.api(f"GET complex detail {complex_id}: успешно")
            return result
        except NotFoundError:
            log.error(f"Комплекс {complex_id} не найден")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке комплекса {complex_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки комплекса {complex_id}: {e}")
            raise ApiError(f"Failed to load complex detail {complex_id}: {e}") from e

    def get_building_detail(self, building_id: NodeID) -> Optional[BuildingDetailDTO]:
        """GET /physical/buildings/{id} → детальная информация о корпусе."""
        try:
            data = self._http.get(Endpoints.building_detail(building_id))
            result = to_building_detail(data)
            log.api(f"GET building detail {building_id}: успешно")
            return result
        except NotFoundError:
            log.error(f"Корпус {building_id} не найден")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке корпуса {building_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки корпуса {building_id}: {e}")
            raise ApiError(f"Failed to load building detail {building_id}: {e}") from e

    def get_floor_detail(self, floor_id: NodeID) -> Optional[FloorDetailDTO]:
        """GET /physical/floors/{id} → детальная информация об этаже."""
        try:
            data = self._http.get(Endpoints.floor_detail(floor_id))
            result = to_floor_detail(data)
            log.api(f"GET floor detail {floor_id}: успешно")
            return result
        except NotFoundError:
            log.error(f"Этаж {floor_id} не найден")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке этажа {floor_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки этажа {floor_id}: {e}")
            raise ApiError(f"Failed to load floor detail {floor_id}: {e}") from e

    def get_room_detail(self, room_id: NodeID) -> Optional[RoomDetailDTO]:
        """GET /physical/rooms/{id} → детальная информация о помещении."""
        try:
            data = self._http.get(Endpoints.room_detail(room_id))
            result = to_room_detail(data)
            log.api(f"GET room detail {room_id}: успешно")
            return result
        except NotFoundError:
            log.error(f"Помещение {room_id} не найдено")
            return None
        except ConnectionError:
            log.error(f"Сервер недоступен при загрузке помещения {room_id}")
            raise
        except Exception as e:
            log.error(f"Ошибка загрузки помещения {room_id}: {e}")
            raise ApiError(f"Failed to load room detail {room_id}: {e}") from e

    # ---- МОНИТОРИНГ ----
    def check_connection(self, timeout: int = 3) -> bool:
        """Проверяет доступность сервера."""
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
        """GET / → информация о сервере (версия, статус)."""
        try:
            data = self._http.get(Endpoints.root())
            result = data if isinstance(data, dict) else {}
            log.api(f"GET server info: версия {result.get('version', 'unknown')}")
            return result
        except Exception as e:
            log.error(f"Не удалось получить информацию о сервере: {e}")
            return {}