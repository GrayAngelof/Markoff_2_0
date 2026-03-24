# client/src/models/floor.py
"""
Модель данных для этажа (floor) на стороне клиента.
Чистый DTO — только данные от API, никакой UI-логики.
"""
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


@dataclass(frozen=True, kw_only=True)
class Floor(BaseDTO, DateTimeMixin):
    """
    Модель этажа (DTO).
    
    Соответствует FloorTreeResponse и FloorDetailResponse из бекенда.
    Содержит ТОЛЬКО данные, никаких методов форматирования или UI-логики.
    
    Поля:
        id: уникальный идентификатор (из BaseDTO)
        created_at: дата создания (из DateTimeMixin)
        updated_at: дата обновления (из DateTimeMixin)
        number: номер этажа (целое число, может быть отрицательным)
        building_id: ID родительского корпуса
        rooms_count: количество помещений на этаже (для дерева)
        description: описание этажа (детали)
        physical_type_id: ID типа этажа (детали)
        status_id: ID статуса (детали)
        plan_image_url: URL плана этажа (детали)
    """
    # Тип узла для графа
    NODE_TYPE = "floor"

    # Специфичные для этажа поля
    number: int
    building_id: int
    rooms_count: int = 0
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    plan_image_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Floor':
        """
        Создаёт объект Floor из словаря (ответ API).
        
        Args:
            data: словарь с данными от API
                Пример: {"id": 1, "number": 1, "building_id": 3, "rooms_count": 0}
            
        Returns:
            Floor: объект этажа
            
        Raises:
            ValueError: если отсутствует обязательное поле 'id' или 'building_id'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")
        
        if 'building_id' not in data:
            raise ValueError("Отсутствует обязательное поле 'building_id' в ответе API")
        
        return cls(
            id=data['id'],
            number=data['number'],
            building_id=data['building_id'],
            rooms_count=data.get('rooms_count', 0),
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            status_id=data.get('status_id'),
            plan_image_url=data.get('plan_image_url'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at'))
        )