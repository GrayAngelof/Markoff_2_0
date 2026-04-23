"""
Тест: проверка существования сущности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.models import Complex, Building


def test_has_returns_true_for_existing(entity_store):
    """Проверяет, что has() возвращает True для существующей сущности."""
    # Arrange - создаём комплекс со ВСЕМИ обязательными полями
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    
    # Act
    result = entity_store.has(COMPLEX, 1)
    
    # Assert
    assert result is True


def test_has_returns_false_for_missing(entity_store):
    """Проверяет, что has() возвращает False для отсутствующей сущности."""
    # Act
    result = entity_store.has(COMPLEX, 999)
    
    # Assert
    assert result is False


def test_has_returns_false_for_wrong_type(entity_store):
    """Проверяет, что has() возвращает False для существующей сущности другого типа."""
    # Arrange - создаём комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    
    # Act - проверяем тот же ID, но другой тип
    result = entity_store.has(BUILDING, 1)
    
    # Assert
    assert result is False


def test_has_after_remove_returns_false(entity_store):
    """Проверяет, что после удаления has() возвращает False."""
    # Arrange - создаём и удаляем комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.remove(COMPLEX, 1)
    
    # Act
    result = entity_store.has(COMPLEX, 1)
    
    # Assert
    assert result is False


def test_has_after_clear_returns_false(entity_store):
    """Проверяет, что после очистки has() возвращает False."""
    # Arrange - создаём и очищаем хранилище
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.clear()
    
    # Act
    result = entity_store.has(COMPLEX, 1)
    
    # Assert
    assert result is False


def test_has_with_multiple_types(entity_store):
    """Проверяет has() для разных типов с одинаковыми ID."""
    # Arrange - создаём комплекс и корпус с одинаковым ID
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
    
    # Act & Assert
    assert entity_store.has(COMPLEX, 1) is True
    assert entity_store.has(BUILDING, 1) is True
    assert entity_store.has(COMPLEX, 2) is False
    assert entity_store.has(BUILDING, 2) is False


def test_has_with_different_ids_same_type(entity_store):
    """Проверяет has() для разных ID одного типа."""
    # Arrange - создаём два комплекса
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    complex_2 = Complex(
        id=2, 
        name="К2", 
        buildings_count=3,  # Обязательное поле!
        address="А2"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(COMPLEX, 2, complex_2)
    
    # Act & Assert
    assert entity_store.has(COMPLEX, 1) is True
    assert entity_store.has(COMPLEX, 2) is True
    assert entity_store.has(COMPLEX, 3) is False