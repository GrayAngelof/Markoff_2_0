"""
Тест: удаление несуществующей сущности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building


def test_remove_nonexistent_complex(entity_graph):
    """Проверяет удаление несуществующего комплекса."""
    # Act
    result = entity_graph.remove(COMPLEX, 999)
    
    # Assert
    assert result is False


def test_remove_nonexistent_building(entity_graph):
    """Проверяет удаление несуществующего корпуса."""
    # Act
    result = entity_graph.remove(BUILDING, 999)
    
    # Assert
    assert result is False


def test_remove_nonexistent_floor(entity_graph):
    """Проверяет удаление несуществующего этажа."""
    # Act
    result = entity_graph.remove(FLOOR, 999)
    
    # Assert
    assert result is False


def test_remove_nonexistent_room(entity_graph):
    """Проверяет удаление несуществующей комнаты."""
    # Act
    result = entity_graph.remove(ROOM, 999)
    
    # Assert
    assert result is False


def test_remove_nonexistent_with_cascade(entity_graph):
    """Проверяет каскадное удаление несуществующей сущности."""
    # Act
    result = entity_graph.remove(COMPLEX, 999, cascade=True)
    
    # Assert
    assert result is False


def test_remove_nonexistent_after_real_ones(entity_graph):
    """Проверяет удаление несуществующей сущности, когда есть другие."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Act
    result = entity_graph.remove(COMPLEX, 999)
    
    # Assert
    assert result is False
    assert entity_graph.has_entity(COMPLEX, 1) is True  # Реальная сущность не пострадала


def test_remove_wrong_type(entity_graph):
    """Проверяет удаление с правильным ID, но неправильным типом."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Act - пытаемся удалить комплекс, но с типом BUILDING
    result = entity_graph.remove(BUILDING, 1)
    
    # Assert
    assert result is False  # Не должно удалиться
    assert entity_graph.has_entity(COMPLEX, 1) is True  # Комплекс должен остаться