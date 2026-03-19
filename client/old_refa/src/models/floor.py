# client/src/models/floor.py
"""
Модель данных для этажа (floor) на стороне клиента
Соответствует ответу от API /physical/buildings/{building_id}/floors
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Floor:
    """
    Модель этажа для отображения в дереве
    
    Поля соответствуют FloorTreeResponse из бекенда:
    - id: уникальный идентификатор этажа
    - number: номер этажа (целое число, может быть отрицательным)
    - building_id: ID родительского корпуса
    - rooms_count: количество помещений на этаже
    
    Дополнительные поля для детального просмотра:
    - description: описание этажа
    - physical_type_id: ID типа этажа
    - status_id: ID статуса
    - plan_image_url: URL плана этажа
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    number: int
    building_id: int
    rooms_count: int
    
    # Дополнительные поля
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    plan_image_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Floor':
        """
        Создаёт объект Floor из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 1, "number": 1, "building_id": 3, "rooms_count": 0}
            
        Returns:
            Floor: объект этажа
        """
        return cls(
            id=data['id'],
            number=data['number'],
            building_id=data['building_id'],
            rooms_count=data['rooms_count'],
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            status_id=data.get('status_id'),
            plan_image_url=data.get('plan_image_url'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        if self.number < 0:
            return f"Подвал {abs(self.number)}"
        elif self.number == 0:
            return "Цокольный этаж"
        else:
            return f"Этаж {self.number}"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Floor(id={self.id}, number={self.number}, building_id={self.building_id}, rooms={self.rooms_count})"