# client/src/models/room.py
"""
Модель данных для помещения (room) на стороне клиента.
Чистый DTO — только данные от API, никакой UI-логики.
"""
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


@dataclass(frozen=True, kw_only=True)
class Room(BaseDTO, DateTimeMixin):
    """
    Модель помещения (DTO).
    
    Соответствует RoomTreeResponse и RoomDetailResponse из бекенда.
    Содержит ТОЛЬКО данные, никаких методов форматирования или UI-логики.
    
    Поля:
        id: уникальный идентификатор (из BaseDTO)
        created_at: дата создания (из DateTimeMixin)
        updated_at: дата обновления (из DateTimeMixin)
        number: номер помещения (строка, может содержать буквы)
        floor_id: ID родительского этажа
        area: площадь помещения (опционально)
        status_code: код статуса ('free', 'occupied', 'reserved', 'maintenance')
        description: описание помещения (детали)
        physical_type_id: ID типа помещения (детали)
        max_tenants: максимальное количество арендаторов (детали)
    """
    # Тип узла для графа
    NODE_TYPE = "room"

    # Специфичные для помещения поля
    number: str
    floor_id: int
    area: Optional[float] = None
    status_code: Optional[str] = None
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    max_tenants: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        """
        Создаёт объект Room из словаря (ответ API).
        
        Args:
            data: словарь с данными от API
                Пример: {
                    "id": 101,
                    "number": "101",
                    "floor_id": 1,
                    "area": 45.5,
                    "status_code": "free"
                }
            
        Returns:
            Room: объект помещения
            
        Raises:
            ValueError: если отсутствует обязательное поле 'id' или 'floor_id'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")
        
        if 'floor_id' not in data:
            raise ValueError("Отсутствует обязательное поле 'floor_id' в ответе API")
        
        return cls(
            id=data['id'],
            number=data['number'],
            floor_id=data['floor_id'],
            area=data.get('area'),
            status_code=data.get('status_code'),
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            max_tenants=data.get('max_tenants'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at'))
        )