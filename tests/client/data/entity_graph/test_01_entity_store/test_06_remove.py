"""
Тест: удаление сущности из хранилища.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.models import Complex, Building


def test_remove_existing_entity(entity_store):
    """Проверяет, что remove() удаляет существующую сущность."""
    # Arrange - создаём комплекс со ВСЕМИ обязательными полями
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    
    # Act
    result = entity_store.remove(COMPLEX, 1)
    
    # Assert
    assert result is True
    assert entity_store.has(COMPLEX, 1) is False
    assert entity_store.size() == 0


def test_remove_nonexistent_entity(entity_store):
    """Проверяет, что remove() возвращает False для несуществующей сущности."""
    # Act
    result = entity_store.remove(COMPLEX, 999)
    
    # Assert
    assert result is False


def test_remove_only_specified_type(entity_store):
    """Проверяет, что remove() удаляет только сущность указанного типа."""
    # Arrange - создаём комплекс и корпус
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    building_1 = Building(
        id=1, 
        name="Б1", 
        complex_id=1, 
        floors_count=3,  # Обязательное поле!
        description="Тестовый корпус"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(BUILDING, 1, building_1)
    
    # Act
    result = entity_store.remove(COMPLEX, 1)
    
    # Assert
    assert result is True
    assert entity_store.has(COMPLEX, 1) is False
    assert entity_store.has(BUILDING, 1) is True  # Другой тип не должен удалиться
    assert entity_store.size() == 1


def test_remove_updates_size(entity_store):
    """Проверяет, что remove() правильно обновляет размер хранилища."""
    # Arrange - создаём три комплекса
    for i in range(1, 4):
        entity_store.put(
            COMPLEX, 
            i, 
            Complex(
                id=i, 
                name=f"К{i}", 
                buildings_count=i,  # Обязательное поле!
                address=f"А{i}"
            )
        )
    
    # Act
    entity_store.remove(COMPLEX, 2)
    
    # Assert
    assert entity_store.size() == 2
    assert entity_store.has(COMPLEX, 1) is True
    assert entity_store.has(COMPLEX, 3) is True


def test_remove_idempotent(entity_store):
    """Проверяет идемпотентность remove (повторный вызов возвращает False)."""
    # Arrange - создаём комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    
    # Act
    first_remove = entity_store.remove(COMPLEX, 1)
    second_remove = entity_store.remove(COMPLEX, 1)
    
    # Assert
    assert first_remove is True
    assert second_remove is False


def test_remove_with_multiple_types_same_id(entity_store):
    """Проверяет удаление разных типов с одинаковым ID."""
    # Arrange - создаём комплекс и корпус с ID=1
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    building_1 = Building(
        id=1, 
        name="Б1", 
        complex_id=1, 
        floors_count=3,  # Обязательное поле!
        description="Тестовый корпус"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(BUILDING, 1, building_1)
    
    # Act
    remove_complex = entity_store.remove(COMPLEX, 1)
    remove_building = entity_store.remove(BUILDING, 1)
    
    # Assert
    assert remove_complex is True
    assert remove_building is True
    assert entity_store.size() == 0
    assert entity_store.has(COMPLEX, 1) is False
    assert entity_store.has(BUILDING, 1) is False


def test_remove_from_empty_store(entity_store):
    """Проверяет remove() на пустом хранилище."""
    # Act
    result = entity_store.remove(COMPLEX, 1)
    
    # Assert
    assert result is False
    assert entity_store.size() == 0