# client/src/models/__init__.py
"""
Пакет моделей данных (DTO) для клиентского приложения.

Все модели — иммутабельные dataclasses с полным соответствием API бекенда.
Содержат ТОЛЬКО данные, никакой UI-логики или бизнес-логики.

Использование:
    from src.models import Complex, Building, Counterparty
    
    complex = Complex.from_dict(api_response)
    building = Building(id=1, name="Корпус А", complex_id=42)
"""

from .complex import Complex
from .building import Building
from .floor import Floor
from .room import Room

# Для обратной совместимости и удобства импорта
__all__ = [
    # Основные модели
    "Complex",
    "Building", 
    "Floor",
    "Room",
]