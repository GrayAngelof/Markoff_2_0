"""
Тест: получение родителя сущности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR
from client.src.data.graph.relation_index import RelationIndex


def test_get_parent_returns_parent_info(relation_index):
    """Проверяет, что get_parent() возвращает информацию о родителе."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Act
    parent = relation_index.get_parent(BUILDING, 1)
    
    # Assert
    assert parent == (COMPLEX, 100)


def test_get_parent_returns_none_for_orphan(relation_index):
    """Проверяет, что get_parent() возвращает None для сущности без родителя."""
    # Act
    parent = relation_index.get_parent(BUILDING, 999)
    
    # Assert
    assert parent is None


def test_get_parent_after_unlink(relation_index):
    """Проверяет, что после удаления связи get_parent() возвращает None."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.unlink(BUILDING, 1)
    
    # Act
    parent = relation_index.get_parent(BUILDING, 1)
    
    # Assert
    assert parent is None


def test_get_parent_for_different_types(relation_index):
    """Проверяет get_parent() для разных типов сущностей."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(FLOOR, 2, BUILDING, 1)
    
    # Act & Assert
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 100)
    assert relation_index.get_parent(FLOOR, 2) == (BUILDING, 1)


def test_get_parent_consistency(relation_index):
    """Проверяет консистентность get_parent() после множественных операций."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    
    # Act & Assert
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 100)
    assert relation_index.get_parent(BUILDING, 2) == (COMPLEX, 100)
    assert relation_index.get_parent(BUILDING, 3) is None