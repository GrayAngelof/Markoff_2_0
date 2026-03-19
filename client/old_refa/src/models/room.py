# client/src/models/room.py
"""
Модель данных для помещения (room) на стороне клиента
Соответствует ответу от API /physical/floors/{floor_id}/rooms
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Room:
    """
    Модель помещения для отображения в дереве
    
    Поля соответствуют RoomTreeResponse из бекенда:
    - id: уникальный идентификатор помещения
    - number: номер помещения (строка, может содержать буквы)
    - floor_id: ID родительского этажа
    - area: площадь помещения (опционально)
    - status_code: статус помещения (опционально)
    
    Дополнительные поля для детального просмотра:
    - description: описание помещения
    - physical_type_id: ID типа помещения
    - max_tenants: максимальное количество арендаторов
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    number: str
    floor_id: int
    area: Optional[float] = None
    status_code: Optional[str] = None
    
    # Дополнительные поля
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    max_tenants: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        """
        Создаёт объект Room из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 101, "number": "101", "floor_id": 1, 
                    "area": 45.5, "status_code": "free"}
            
        Returns:
            Room: объект помещения
        """
        return cls(
            id=data['id'],
            number=data['number'],
            floor_id=data['floor_id'],
            area=data.get('area'),
            status_code=data.get('status_code'),
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            max_tenants=data.get('max_tenants'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        return self.number
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Room(id={self.id}, number='{self.number}', floor_id={self.floor_id}, status={self.status_code})"
    
    def get_status_display(self) -> str:
        """
        Возвращает человекочитаемый статус помещения
        """
        status_map = {
            'free': 'Свободно',
            'occupied': 'Занято',
            'reserved': 'Зарезервировано',
            'maintenance': 'На обслуживании',
        }
        # ИСПРАВЛЕНО: проверяем на None
        if self.status_code is None:
            return 'Неизвестно'
        return status_map.get(self.status_code, self.status_code or 'Неизвестно')