# backend/src/routers/physical.py
"""
Роутер для работы с physical данными
Только принимает HTTP запросы и возвращает ответы
Вся логика делегируется сервисному слою
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from ..core.deps import get_db
from ..services.physical import get_all_complexes
from ..models.physical import Complex

# Создаем роутер с префиксом /physical
router = APIRouter(prefix="/physical", tags=["physical"])

@router.get("/", response_model=List[Complex])
async def read_complexes(
    db: Session = Depends(get_db)
) -> List[Complex]:
    """
    Получить список всех комплексов
    
    Returns:
        List[Complex]: Массив комплексов
        
    HTTP статусы:
        200: Успешный ответ с данными
        500: Внутренняя ошибка сервера
        
    Примечание:
        response_model гарантирует, что ответ будет соответствовать
        схеме Complex (сериализация через Pydantic)
    """
    try:
        # Делегируем получение данных сервисному слою
        complexes = get_all_complexes(db)
        return complexes
    except Exception as e:
        # Логируем ошибку (в будущем добавим нормальное логирование)
        print(f"Error fetching complexes: {e}")
        # Возвращаем 500 ошибку
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )