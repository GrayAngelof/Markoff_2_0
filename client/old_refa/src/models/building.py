# client/src/models/building.py (дополненная версия)
from dataclasses import dataclass
from typing import Optional
from src.models.counterparty import Counterparty  # новый импорт


@dataclass
class Building:
    """
    Модель корпуса для отображения в дереве
    
    Добавлено поле owner_id и owner для связи с владельцем
    """
    
    id: int
    name: str
    complex_id: int
    floors_count: int
    
    # Дополнительные поля
    description: Optional[str] = None
    address: Optional[str] = None
    status_id: Optional[int] = None
    owner_id: Optional[int] = None  # <-- НОВОЕ: ID владельца
    owner: Optional[Counterparty] = None  # <-- НОВОЕ: объект владельца (загружается отдельно)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Building':
        """Создаёт объект Building из словаря (ответ API)"""
        building = cls(
            id=data['id'],
            name=data['name'],
            complex_id=data['complex_id'],
            floors_count=data['floors_count'],
            description=data.get('description'),
            address=data.get('address'),
            status_id=data.get('status_id'),
            owner_id=data.get('owner_id'),  # <-- НОВОЕ
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
        
        # Если в данных есть вложенный объект owner, загружаем его
        if 'owner' in data and data['owner']:
            from src.models.counterparty import Counterparty
            building.owner = Counterparty.from_dict(data['owner'])
        
        return building
    
    def get_owner_display(self) -> str:
        """Возвращает название владельца для отображения"""
        if self.owner:
            return self.owner.short_name
        return "Владелец не указан"