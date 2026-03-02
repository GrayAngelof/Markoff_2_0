# backend/src/models/physical/complex.py
"""
Модель Complex для таблицы physical.complexes
Используем SQLModel для описания структуры таблицы и валидации данных

Важно: SQLModel объединяет ORM (SQLAlchemy) и валидацию (Pydantic)
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Complex(SQLModel, table=True):
    """
    Модель комплекса (таблица physical.complexes)
    
    Атрибуты класса:
    __tablename__: имя таблицы в базе данных
    __table_args__: дополнительные параметры таблицы (схема, индексы)
    
    Поля соответствуют колонкам в базе данных
    """
    
    __tablename__ = "complexes"
    __table_args__ = {"schema": "physical"}  # Таблица находится в схеме physical
    
    # ID комплекса (первичный ключ)
    # Используем int, но в базе это bigint
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Название комплекса - обязательное поле, уникальное
    name: str = Field(nullable=False, unique=True)
    
    # Описание - может быть пустым
    description: Optional[str] = Field(default=None)
    
    # Адрес - может быть пустым
    address: Optional[str] = Field(default=None)
    
    # ID владельца (связь с таблицей владельцев, но пока не реализуем)
    owner_id: Optional[int] = Field(default=None)
    
    # Даты создания и обновления
    # auto_now_add для created_at, auto_now для updated_at
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        """Pydantic конфигурация для схемы"""
        # Позволяет использовать объекты ORM в ответах API
        from_attributes = True