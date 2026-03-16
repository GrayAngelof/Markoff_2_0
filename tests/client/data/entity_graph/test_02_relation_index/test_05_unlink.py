"""
Тест: удаление связи.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.data.graph.relation_index import RelationIndex


def test_unlink_removes_relation(relation_index):
    """Проверяет, что unlink() удаляет связь."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Act
    result = relation_index.unlink(BUILDING, 1)
    
    # Assert
    assert result is True
    assert relation_index.get_parent(BUILDING, 1) is None
    assert 1 not in relation_index.get_children(COMPLEX, 100)


def test_unlink_returns_false_for_nonexistent(relation_index):
    """Проверяет, что unlink() возвращает False для несуществующей связи."""
    # Act
    result = relation_index.unlink(BUILDING, 999)
    
    # Assert
    assert result is False


def test_unlink_only_removes_specified_child(relation_index):
    """Проверяет, что unlink() удаляет только указанного ребёнка."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    
    # Act
    relation_index.unlink(BUILDING, 1)
    
    # Assert
    assert relation_index.get_parent(BUILDING, 1) is None
    assert relation_index.get_parent(BUILDING, 2) == (COMPLEX, 100)
    assert relation_index.get_children(COMPLEX, 100) == [2]


def test_unlink_idempotent(relation_index):
    """Проверяет идемпотентность unlink."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Act
    first_unlink = relation_index.unlink(BUILDING, 1)
    second_unlink = relation_index.unlink(BUILDING, 1)
    
    # Assert
    assert first_unlink is True
    assert second_unlink is False


def test_unlink_after_relink(relation_index):
    """Проверяет unlink после перелинковки."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 1, COMPLEX, 200)  # перелинковка
    
    # Act
    result = relation_index.unlink(BUILDING, 1)
    
    # Assert
    assert result is True
    assert relation_index.get_parent(BUILDING, 1) is None
    assert 1 not in relation_index.get_children(COMPLEX, 100)
    assert 1 not in relation_index.get_children(COMPLEX, 200)