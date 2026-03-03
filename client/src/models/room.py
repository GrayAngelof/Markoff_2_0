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
    - number: номер помещения (строка, может содержать буквы, например "101А")
    - floor_id: ID родительского этажа
    - area: площадь помещения (опционально, для отображения в деталях)
    - status_code: статус помещения (опционально, для цветовой индикации)
    
    Сортировка: по number (как строка, но с учётом естественного порядка)
    """
    
    id: int
    number: str
    floor_id: int
    area: Optional[float] = None
    status_code: Optional[str] = None
    
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
            area=data.get('area'),  # используем get, так как поля могут отсутствовать
            status_code=data.get('status_code')
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
        Для будущего использования в цветовой индикации
        """
        status_map = {
            'free': 'Свободно',
            'occupied': 'Занято',
            'reserved': 'Зарезервировано',
            'maintenance': 'На обслуживании',
        }
        return status_map.get(self.status_code, self.status_code or 'Неизвестно')