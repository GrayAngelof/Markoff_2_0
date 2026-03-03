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
    - number: номер этажа (целое число, может быть отрицательным для подвалов)
    - building_id: ID родительского корпуса
    - rooms_count: количество помещений на этаже (для отображения в скобках)
    
    Сортировка: по number (числовая, от меньшего к большему)
    """
    
    id: int
    number: int
    building_id: int
    rooms_count: int
    
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
            rooms_count=data['rooms_count']
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        # Для подвальных этажей добавляем пометку
        if self.number < 0:
            return f"Подвал {abs(self.number)}"
        elif self.number == 0:
            return "Цокольный этаж"
        else:
            return f"Этаж {self.number}"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Floor(id={self.id}, number={self.number}, building_id={self.building_id}, rooms={self.rooms_count})"