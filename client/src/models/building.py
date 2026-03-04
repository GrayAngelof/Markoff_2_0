# client/src/models/building.py
"""
Модель данных для корпуса (building) на стороне клиента
Соответствует ответу от API /physical/complexes/{complex_id}/buildings
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Building:
    """
    Модель корпуса для отображения в дереве
    
    Поля соответствуют BuildingTreeResponse из бекенда:
    - id: уникальный идентификатор корпуса
    - name: название корпуса (например, "Корпус А")
    - complex_id: ID родительского комплекса
    - floors_count: количество этажей в корпусе
    
    Дополнительные поля для детального просмотра:
    - description: описание корпуса
    - address: адрес корпуса
    - status_id: ID статуса
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    name: str
    complex_id: int
    floors_count: int
    
    # Дополнительные поля
    description: Optional[str] = None
    address: Optional[str] = None
    status_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Building':
        """
        Создаёт объект Building из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 3, "name": "Корпус А", "complex_id": 1, "floors_count": 4}
            
        Returns:
            Building: объект корпуса
        """
        return cls(
            id=data['id'],
            name=data['name'],
            complex_id=data['complex_id'],
            floors_count=data['floors_count'],
            description=data.get('description'),
            address=data.get('address'),
            status_id=data.get('status_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        return self.name
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Building(id={self.id}, name='{self.name}', complex_id={self.complex_id}, floors={self.floors_count})"