"""
Тест: проверка наличия детей.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.data.graph.relation_index import RelationIndex


def test_has_children_returns_true_when_children_exist(relation_index):
    """Проверяет, что has_children() возвращает True, если есть дети."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Act
    result = relation_index.has_children(COMPLEX, 100)
    
    # Assert
    assert result is True


def test_has_children_returns_false_when_no_children(relation_index):
    """Проверяет, что has_children() возвращает False, если нет детей."""
    # Act
    result = relation_index.has_children(COMPLEX, 999)
    
    # Assert
    assert result is False


def test_has_children_after_unlink(relation_index):
    """Проверяет has_children() после удаления ребёнка."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    assert relation_index.has_children(COMPLEX, 100) is True
    
    # Act
    relation_index.unlink(BUILDING, 1)
    
    # Assert
    assert relation_index.has_children(COMPLEX, 100) is False


def test_has_children_with_multiple_children(relation_index):
    """Проверяет has_children() с несколькими детьми."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    
    # Act & Assert
    assert relation_index.has_children(COMPLEX, 100) is True
    
    # Удаляем одного - всё ещё есть дети
    relation_index.unlink(BUILDING, 1)
    assert relation_index.has_children(COMPLEX, 100) is True
    
    # Удаляем последнего - детей нет
    relation_index.unlink(BUILDING, 2)
    assert relation_index.has_children(COMPLEX, 100) is False


def test_has_children_for_different_parents(relation_index):
    """Проверяет has_children() для разных родителей."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    # У COMPLEX, 200 нет детей
    
    # Act & Assert
    assert relation_index.has_children(COMPLEX, 100) is True
    assert relation_index.has_children(COMPLEX, 200) is False