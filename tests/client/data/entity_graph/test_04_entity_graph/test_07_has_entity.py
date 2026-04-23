"""
Тест: проверка наличия сущности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_has_entity_true_for_existing(entity_graph, sample_hierarchy):
    """Проверяет, что has_entity возвращает True для существующей сущности."""
    # Act & Assert
    assert entity_graph.has_entity(COMPLEX, 1) is True
    assert entity_graph.has_entity(BUILDING, 1) is True
    assert entity_graph.has_entity(FLOOR, 1) is True
    assert entity_graph.has_entity(ROOM, 1) is True


def test_has_entity_false_for_nonexistent(entity_graph):
    """Проверяет, что has_entity возвращает False для несуществующей сущности."""
    # Act & Assert
    assert entity_graph.has_entity(COMPLEX, 999) is False
    assert entity_graph.has_entity(BUILDING, 999) is False
    assert entity_graph.has_entity(FLOOR, 999) is False
    assert entity_graph.has_entity(ROOM, 999) is False


def test_has_entity_wrong_type(entity_graph, sample_hierarchy):
    """Проверяет has_entity для существующей сущности, но с неправильным типом."""
    # Act
    result = entity_graph.has_entity(COMPLEX, 1)  # complex exists
    wrong_result = entity_graph.has_entity(BUILDING, 1)  # building also exists
    
    # Assert
    assert result is True
    assert wrong_result is True  # building с id 1 тоже существует


def test_has_entity_after_add(entity_graph):
    """Проверяет has_entity после добавления."""
    # Act
    entity_graph.add_or_update(Complex(id=1, name="К1", buildings_count=2, address="А1"))
    
    # Assert
    assert entity_graph.has_entity(COMPLEX, 1) is True


def test_has_entity_after_remove_with_cascade(entity_graph, sample_hierarchy):
    """Проверяет has_entity после каскадного удаления."""
    # Arrange
    assert entity_graph.has_entity(BUILDING, 1) is True
    assert entity_graph.has_entity(FLOOR, 1) is True
    assert entity_graph.has_entity(ROOM, 1) is True
    
    # Act - удаляем с каскадом, так как у building есть дети
    entity_graph.remove(BUILDING, 1, cascade=True)
    
    # Assert
    assert entity_graph.has_entity(BUILDING, 1) is False
    assert entity_graph.has_entity(FLOOR, 1) is False
    assert entity_graph.has_entity(ROOM, 1) is False
    assert entity_graph.has_entity(COMPLEX, 1) is True  # Комплекс должен остаться


def test_has_entity_after_remove_leaf(entity_graph, sample_hierarchy):
    """Проверяет has_entity после удаления листового узла."""
    # Arrange
    assert entity_graph.has_entity(ROOM, 1) is True
    
    # Act - комната - лист, можно удалять без каскада
    entity_graph.remove(ROOM, 1, cascade=False)
    
    # Assert
    assert entity_graph.has_entity(ROOM, 1) is False
    assert entity_graph.has_entity(FLOOR, 1) is True   # Родитель должен остаться
    assert entity_graph.has_entity(BUILDING, 1) is True
    assert entity_graph.has_entity(COMPLEX, 1) is True


def test_has_entity_after_clear(entity_graph, sample_hierarchy):
    """Проверяет has_entity после очистки графа."""
    # Act
    entity_graph.clear()
    
    # Assert
    assert entity_graph.has_entity(COMPLEX, 1) is False
    assert entity_graph.has_entity(BUILDING, 1) is False
    assert entity_graph.has_entity(FLOOR, 1) is False
    assert entity_graph.has_entity(ROOM, 1) is False