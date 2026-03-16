"""
Тест: удаление узла со всеми связями.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR
from client.src.data.graph.relation_index import RelationIndex


def test_remove_node_removes_all_relations(relation_index):
    """Проверяет, что remove_node() удаляет все связи узла."""
    # Arrange - создаём сложную структуру
    # COMPLEX 100 -> BUILDING 1 -> FLOOR 10
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(FLOOR, 10, BUILDING, 1)
    
    # Act - удаляем building 1
    relation_index.remove_node(BUILDING, 1)
    
    # Assert
    # У building 1 больше нет родителя
    assert relation_index.get_parent(BUILDING, 1) is None
    
    # У complex 100 больше нет building 1 в детях
    assert 1 not in relation_index.get_children(COMPLEX, 100)
    
    # У floor 10 больше нет родителя (связь тоже удалилась)
    assert relation_index.get_parent(FLOOR, 10) is None


def test_remove_node_leaf(relation_index):
    """Проверяет remove_node() для листового узла (без детей)."""
    # Arrange
    relation_index.link(FLOOR, 10, BUILDING, 1)
    
    # Act
    relation_index.remove_node(FLOOR, 10)
    
    # Assert
    assert relation_index.get_parent(FLOOR, 10) is None
    assert 10 not in relation_index.get_children(BUILDING, 1)


def test_remove_node_root(relation_index):
    """Проверяет remove_node() для корневого узла (без родителя)."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    
    # Act
    relation_index.remove_node(COMPLEX, 100)
    
    # Assert
    # У complex больше нет детей
    assert relation_index.get_children(COMPLEX, 100) == []
    
    # Дети осиротели
    assert relation_index.get_parent(BUILDING, 1) is None
    assert relation_index.get_parent(BUILDING, 2) is None


def test_remove_node_preserves_other_relations(relation_index):
    """Проверяет, что remove_node() не влияет на другие узлы."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    relation_index.link(FLOOR, 10, BUILDING, 1)
    relation_index.link(FLOOR, 20, BUILDING, 2)
    
    # Act - удаляем building 1
    relation_index.remove_node(BUILDING, 1)
    
    # Assert
    # Building 2 и его иерархия должны сохраниться
    assert relation_index.get_parent(BUILDING, 2) == (COMPLEX, 100)
    assert 2 in relation_index.get_children(COMPLEX, 100)
    assert relation_index.get_parent(FLOOR, 20) == (BUILDING, 2)
    assert 20 in relation_index.get_children(BUILDING, 2)
    
    # Building 1 и его иерархия должны быть удалены
    assert relation_index.get_parent(BUILDING, 1) is None
    assert 1 not in relation_index.get_children(COMPLEX, 100)
    assert relation_index.get_parent(FLOOR, 10) is None


def test_remove_node_nonexistent(relation_index):
    """Проверяет remove_node() для несуществующего узла."""
    # Act & Assert (не должно быть исключений)
    relation_index.remove_node(BUILDING, 999)
    # Индексы должны остаться в консистентном состоянии
    assert relation_index.get_all_relations() is not None