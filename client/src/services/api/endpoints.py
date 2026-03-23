# client/src/services/api/endpoints.py
"""
Константы эндпоинтов API бэкенда.

Все URL пути собраны в одном месте. Это позволяет:
- Легко менять API при обновлении бэкенда
- Избежать магических строк в коде
- IDE подсказывает доступные эндпоинты
"""

from core.types.nodes import NodeID


class Endpoints:
    """
    Все эндпоинты API в виде статических методов.
    
    Методы возвращают строки с путями, подставляя ID где необходимо.
    Формат: /physical/... для физической структуры,
            /counterparties/... для справочников.
    """
    
    # ===== Физическая структура =====
    
    @staticmethod
    def complexes() -> str:
        """Список всех комплексов."""
        return "/physical/"
    
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
    
    # ===== Справочники =====
    
    @staticmethod
    def counterparty(counterparty_id: NodeID) -> str:
        """Информация о контрагенте (юридическом лице)."""
        return f"/counterparties/{counterparty_id}"
    
    @staticmethod
    def responsible_persons(counterparty_id: NodeID) -> str:
        """Список ответственных лиц контрагента."""
        return f"/counterparties/{counterparty_id}/persons"
    
    # ===== Мониторинг =====
    
    @staticmethod
    def health() -> str:
        """Проверка здоровья сервера."""
        return "/health"
    
    @staticmethod
    def root() -> str:
        """Корневой эндпоинт (информация о сервере)."""
        return "/"