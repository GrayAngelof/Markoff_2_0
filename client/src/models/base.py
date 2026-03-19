# client/src/models/base.py
"""
Базовый класс для всех DTO моделей.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseDTO:
    """
    Базовый DTO с минимальным набором полей.
    
    frozen=True гарантирует, что объект нельзя изменить после создания.
    Это критически важно для кэширования и глобального состояния.
    
    Все модели должны наследовать этот класс.
    Дополнительные возможности добавляются через миксины.
    """
    
    id: int
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.id <= 0:
            raise ValueError(f"ID должен быть положительным числом, получено: {self.id}")
    
    def __repr__(self) -> str:
        """Базовый __repr__ для отладки"""
        return f"{self.__class__.__name__}(id={self.id})"