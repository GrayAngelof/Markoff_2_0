# client/src/models/complex.py
"""
Модель данных для комплекса на стороне клиента
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Complex:
    """
    Модель комплекса для клиента
    
    Содержит только те поля, которые нужны для отображения в дереве:
    - id: уникальный идентификатор
    - name: название комплекса (то, что показываем в дереве)
    
    Остальные поля (description, address, etc.) будем запрашивать
    только при необходимости, когда пользователь кликнет на комплекс
    """
    id: int
    name: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Complex':
        """
        Создаёт объект Complex из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            
        Returns:
            Complex: объект комплекса
        """
        return cls(
            id=data['id'],
            name=data['name']
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        return self.name