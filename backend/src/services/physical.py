# backend/src/services/physical.py
"""
Сервисный слой для работы с physical схемой
Содержит бизнес-логику работы с комплексами, зданиями и помещениями

Здесь реализована вся логика запросов к БД и обработки данных
Роутеры только вызывают эти функции
"""
from sqlmodel import Session, select
from typing import List

from ..models.physical import Complex

def get_all_complexes(db: Session) -> List[Complex]:
    """
    Получить список всех комплексов
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[Complex]: Список всех комплексов
        
    Бизнес-логика:
        - Пока просто получаем все записи
        - В будущем добавим фильтрацию, сортировку, пагинацию
        - Добавим подсчет количества зданий для каждого комплекса
    """
    # Формируем запрос: SELECT * FROM physical.complexes
    statement = select(Complex)
    
    # Выполняем запрос и возвращаем результат
    result = db.exec(statement)
    return result.all()