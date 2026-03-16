"""
Тест: получение сущности из хранилища.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_get_returns_existing_entity(entity_store, complex_entity):
    """Проверяет, что get() возвращает ранее сохранённый объект."""
    # Arrange
    entity_store.put(COMPLEX, 1, complex_entity)
    
    # Act
    result = entity_store.get(COMPLEX, 1)
    
    # Assert
    assert result is complex_entity
    assert result.id == 1


def test_get_returns_none_for_missing(entity_store):
    """Проверяет, что get() возвращает None для отсутствующей сущности."""
    # Act
    result = entity_store.get(COMPLEX, 999)
    
    # Assert
    assert result is None


def test_get_returns_none_for_wrong_type(entity_store, complex_entity):
    """Проверяет, что get() не находит сущность другого типа."""
    # Arrange
    entity_store.put(COMPLEX, 1, complex_entity)
    
    # Act
    result = entity_store.get(BUILDING, 1)
    
    # Assert
    assert result is None


def test_get_after_remove_returns_none(entity_store, complex_entity):
    """Проверяет, что после удаления get() возвращает None."""
    # Arrange
    entity_store.put(COMPLEX, 1, complex_entity)
    entity_store.remove(COMPLEX, 1)
    
    # Act
    result = entity_store.get(COMPLEX, 1)
    
    # Assert
    assert result is None


def test_get_is_thread_safe(entity_store, complex_entity):
    """Проверяет потокобезопасность (простая проверка)."""
    import threading
    
    # Arrange
    entity_store.put(COMPLEX, 1, complex_entity)
    results = []
    
    def get_entity():
        results.append(entity_store.get(COMPLEX, 1))
    
    # Act
    threads = [threading.Thread(target=get_entity) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Assert
    assert all(r is complex_entity for r in results)
    assert len(results) == 10