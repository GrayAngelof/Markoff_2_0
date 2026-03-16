"""
Тест: замена родителя (перелинковка).
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.data.graph.relation_index import RelationIndex


def test_link_updates_existing_relation(relation_index):
    """Проверяет, что link() корректно обновляет старую связь."""
    # Arrange - создаём связь с первым родителем
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Act - перелинковываем на нового родителя
    relation_index.link(BUILDING, 1, COMPLEX, 200)
    
    # Assert
    # Проверяем нового родителя
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 200)
    
    # Проверяем, что у старого родителя больше нет этого ребёнка
    old_parent_children = relation_index.get_children(COMPLEX, 100)
    assert 1 not in old_parent_children
    
    # Проверяем, что у нового родителя появился ребёнок
    new_parent_children = relation_index.get_children(COMPLEX, 200)
    assert 1 in new_parent_children


def test_relink_preserves_other_children(relation_index):
    """Проверяет, что при перелинковке другие дети не теряются."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    relation_index.link(BUILDING, 3, COMPLEX, 200)
    
    # Act - перелинковываем building 2 к новому родителю
    relation_index.link(BUILDING, 2, COMPLEX, 200)
    
    # Assert
    # Проверяем старого родителя
    old_parent_children = relation_index.get_children(COMPLEX, 100)
    assert set(old_parent_children) == {1}  # building 2 ушёл, building 1 остался
    
    # Проверяем нового родителя
    new_parent_children = relation_index.get_children(COMPLEX, 200)
    assert set(new_parent_children) == {2, 3}  # building 2 присоединился к building 3


def test_relink_to_same_parent_no_change(relation_index):
    """Проверяет, что перелинковка к тому же родителю не меняет состояние."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    before_children = relation_index.get_children(COMPLEX, 100).copy()
    
    # Act
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Assert
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 100)
    assert relation_index.get_children(COMPLEX, 100) == before_children


def test_relink_updates_both_indexes_atomically(relation_index):
    """Проверяет атомарность обновления индексов при перелинковке."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Act
    relation_index.link(BUILDING, 1, COMPLEX, 200)
    
    # Assert - проверяем, что все индексы консистентны
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 200)
    assert 1 not in relation_index.get_children(COMPLEX, 100)
    assert 1 in relation_index.get_children(COMPLEX, 200)


def test_relink_orphan_to_parent(relation_index):
    """Проверяет перелинковку сущности без родителя."""
    # Act - у building 1 нет родителя, линкуем
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Assert
    assert relation_index.get_parent(BUILDING, 1) == (COMPLEX, 100)
    assert 1 in relation_index.get_children(COMPLEX, 100)