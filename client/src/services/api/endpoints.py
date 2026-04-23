# client/src/services/api/endpoints.py
"""
Константы эндпоинтов API бэкенда.

Все URL пути собраны в одном месте. Это позволяет:
- Легко менять API при обновлении бэкенда
- Избежать магических строк в коде
- IDE подсказывает доступные эндпоинты
"""

# ===== ИМПОРТЫ =====
from src.core.types.nodes import NodeID


# ===== ЭНДПОИНТЫ =====
class Endpoints:
    """
    Все эндпоинты API в виде статических методов.

    Формат: /physical... для физической структуры,
            /dictionary... для справочников.
    """

    # ---- Физическая структура ----
    @staticmethod
    def complexes() -> str:
        """Список всех комплексов."""
        return "/physical"

    @staticmethod
    def buildings(complex_id: NodeID) -> str:
        """Список корпусов комплекса."""
        return f"/physical/complexes/{complex_id}/buildings"

    @staticmethod
    def floors(building_id: NodeID) -> str:
        """Список этажей корпуса."""
        return f"/physical/buildings/{building_id}/floors"

    @staticmethod
    def rooms(floor_id: NodeID) -> str:
        """Список помещений этажа."""
        return f"/physical/floors/{floor_id}/rooms"

    @staticmethod
    def complex_detail(complex_id: NodeID) -> str:
        """Детальная информация о комплексе."""
        return f"/physical/complexes/{complex_id}"

    @staticmethod
    def building_detail(building_id: NodeID) -> str:
        """Детальная информация о корпусе."""
        return f"/physical/buildings/{building_id}"

    @staticmethod
    def floor_detail(floor_id: NodeID) -> str:
        """Детальная информация об этаже."""
        return f"/physical/floors/{floor_id}"

    @staticmethod
    def room_detail(room_id: NodeID) -> str:
        """Детальная информация о помещении."""
        return f"/physical/rooms/{room_id}"

    # ---- Справочники (dictionary) ----
    @staticmethod
    def building_statuses() -> str:
        """Справочник статусов зданий."""
        return "/dictionary/building-statuses"

    @staticmethod
    def room_statuses() -> str:
        """Справочник статусов помещений."""
        return "/dictionary/room-statuses"

    # ---- Мониторинг ----
    @staticmethod
    def health() -> str:
        """Проверка здоровья сервера."""
        return "/health"

    @staticmethod
    def root() -> str:
        """Корневой эндпоинт (информация о сервере)."""
        return "/"