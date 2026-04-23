"""
Тест: получение сущности из графа.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.models import Complex, Building


def test_get_existing_entity(entity_graph, sample_hierarchy):
    """Проверяет получение существующей сущности."""
    # Act
    complex_1 = entity_graph.get(COMPLEX, 1)
    
    # Assert
    assert complex_1 is not None
    assert complex_1.id == 1
    assert complex_1.name == "Комплекс 1"


def test_get_nonexistent_entity(entity_graph):
    """Проверяет получение несуществующей сущности."""
    # Act
    result = entity_graph.get(COMPLEX, 999)
    
    # Assert
    assert result is None


def test_get_wrong_type(entity_graph, sample_hierarchy):
    """Проверяет получение сущности с неправильным типом."""
    # Act
    result = entity_graph.get(BUILDING, 1)  # complex id 1, но запрашиваем building
    
    # Assert
    assert result is not None  # Building с id 1 существует
    assert isinstance(result, Building)


def test_get_after_update(entity_graph):
    """Проверяет получение после обновления."""
    # Arrange
    complex_1 = Complex(id=1, name="Старое имя", buildings_count=2, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Act
    updated = Complex(id=1, name="Новое имя", buildings_count=3, address="Новый адрес")
    entity_graph.add_or_update(updated)
    result = entity_graph.get(COMPLEX, 1)
    
    # Assert
    assert result.name == "Новое имя"
    assert result.buildings_count == 3


def test_get_after_remove(entity_graph):
    """Проверяет получение после удаления."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    entity_graph.add_or_update(complex_1)
    entity_graph.remove(COMPLEX, 1)
    
    # Act
    result = entity_graph.get(COMPLEX, 1)
    
    # Assert
    assert result is None