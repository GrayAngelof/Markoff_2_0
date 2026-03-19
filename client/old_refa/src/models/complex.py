# client/src/models/complex.py
"""
Модель данных для комплекса на стороне клиента
Обновлена с учётом поля buildings_count от API
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Complex:
    """
    Модель комплекса для отображения в дереве
    
    Поля соответствуют ComplexTreeResponse из бекенда:
    - id: уникальный идентификатор
    - name: название комплекса (то, что показываем в дереве)
    - buildings_count: количество корпусов (для отображения в скобках)
    
    Дополнительные поля для детального просмотра:
    - description: описание комплекса
    - address: адрес комплекса
    - owner_id: ID владельца
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    name: str
    buildings_count: int = 0
    
    # Дополнительные поля (могут отсутствовать)
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Complex':
        """
        Создаёт объект Complex из словаря (ответ API)
        
        Args:
            data: словарь с данными от API
            Пример: {"id": 1, "name": "Фабрика Веретено", "buildings_count": 2}
            
        Returns:
            Complex: объект комплекса
        """
        return cls(
            id=data['id'],
            name=data['name'],
            buildings_count=data.get('buildings_count', 0),
            description=data.get('description'),
            address=data.get('address'),
            owner_id=data.get('owner_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения в дереве"""
        return self.name
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Complex(id={self.id}, name='{self.name}', buildings={self.buildings_count})"
    
    def display_name(self) -> str:
        """
        Имя для отображения в дереве с количеством корпусов
        Используется в tree_model.py
        """
        if self.buildings_count > 0:
            return f"{self.name} ({self.buildings_count})"
        return self.name