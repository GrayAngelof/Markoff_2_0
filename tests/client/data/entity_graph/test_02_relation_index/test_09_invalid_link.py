"""
Тест: создание связи между сущностями.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.data.graph.relation_index import RelationIndex


def test_link_creates_parent_child_relation(relation_index):
    """Проверяет, что link() создаёт связь родитель-потомок."""
    # Act
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Assert
    parent = relation_index.get_parent(BUILDING, 1)
    assert parent is not None
    assert parent[0] == COMPLEX  # parent_type
    assert parent[1] == 100      # parent_id
    
    children = relation_index.get_children(COMPLEX, 100)
    assert 1 in children


def test_link_multiple_children_same_parent(relation_index):
    """Проверяет, что у родителя может быть несколько детей."""
    # Act
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    relation_index.link(BUILDING, 3, COMPLEX, 100)
    
    # Assert
    children = relation_index.get_children(COMPLEX, 100)
    assert len(children) == 3
    assert 1 in children
    assert 2 in children
    assert 3 in children


def test_link_only_allows_valid_child_types(relation_index):
    """
    Проверяет, что link() проверяет допустимость типов по схеме.
    Согласно схеме: BUILDING может быть потомком COMPLEX, а FLOOR - нет.
    """
    # Act - правильная связь
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Попытка создать неправильную связь
    relation_index.link(FLOOR, 2, COMPLEX, 100)  # Должно быть проигнорировано
    
    # Assert
    children = relation_index.get_children(COMPLEX, 100)
    assert len(children) == 1  # Только правильная связь
    assert 1 in children
    assert 2 not in children
    
    # Проверяем, что неправильная связь не создалась
    assert relation_index.get_parent(FLOOR, 2) is None


def test_link_updates_both_indexes(relation_index):
    """Проверяет, что link() обновляет и прямой и обратный индексы."""
    # Act
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Assert - проверяем оба направления
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 100)
    assert 1 in relation_index.get_children(COMPLEX, 100)


def test_link_with_different_parents(relation_index):
    """Проверяет создание связей для разных родителей."""
    # Act
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 200)
    
    # Assert
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 100)
    assert relation_index.get_parent(BUILDING, 2) == (COMPLEX, 200)
    
    children_100 = relation_index.get_children(COMPLEX, 100)
    children_200 = relation_index.get_children(COMPLEX, 200)
    
    assert 1 in children_100
    assert 2 not in children_100
    assert 2 in children_200
    assert 1 not in children_200


def test_link_same_type_valid_hierarchy(relation_index):
    """Проверяет создание связей для валидной иерархии."""
    # Act - создаём полную валидную иерархию
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(FLOOR, 10, BUILDING, 1)
    relation_index.link(ROOM, 100, FLOOR, 10)
    
    # Assert
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 100)
    assert relation_index.get_parent(FLOOR, 10) == (BUILDING, 1)
    assert relation_index.get_parent(ROOM, 100) == (FLOOR, 10)
    
    assert 1 in relation_index.get_children(COMPLEX, 100)
    assert 10 in relation_index.get_children(BUILDING, 1)
    assert 100 in relation_index.get_children(FLOOR, 10)