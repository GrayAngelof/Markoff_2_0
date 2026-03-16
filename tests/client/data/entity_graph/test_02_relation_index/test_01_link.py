"""
Тест: получение детей сущности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR
from client.src.data.graph.relation_index import RelationIndex


def test_get_children_returns_child_ids(relation_index):
    """Проверяет, что get_children() возвращает ID детей."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert
    assert len(children) == 2
    assert 1 in children
    assert 2 in children


def test_get_children_returns_empty_list_for_no_children(relation_index):
    """Проверяет, что get_children() возвращает пустой список, если нет детей."""
    # Act
    children = relation_index.get_children(COMPLEX, 999)
    
    # Assert
    assert children == []


def test_get_children_after_unlink(relation_index):
    """Проверяет, что после удаления связи ребёнок исчезает из списка детей."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    
    # Act
    relation_index.unlink(BUILDING, 1)
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert
    assert len(children) == 1
    assert 1 not in children
    assert 2 in children


def test_get_children_for_different_parents(relation_index):
    """Проверяет get_children() для разных родителей."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 200)
    relation_index.link(FLOOR, 3, BUILDING, 1)
    
    # Act & Assert
    assert set(relation_index.get_children(COMPLEX, 100)) == {1}
    assert set(relation_index.get_children(COMPLEX, 200)) == {2}
    assert set(relation_index.get_children(BUILDING, 1)) == {3}
    assert relation_index.get_children(BUILDING, 2) == []


def test_get_children_returns_sorted_order(relation_index):
    """Проверяет, что get_children() возвращает детей в отсортированном порядке."""
    # Arrange
    for i in [3, 1, 4, 2]:
        relation_index.link(BUILDING, i, COMPLEX, 100)
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert - индекс хранит детей в отсортированном порядке
    assert children == [1, 2, 3, 4]  # Сортировка по возрастанию


def test_get_children_sorted_with_large_numbers(relation_index):
    """Проверяет сортировку с большими числами."""
    # Arrange
    ids = [100, 5, 1000, 50, 1]
    for i in ids:
        relation_index.link(BUILDING, i, COMPLEX, 100)
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert
    assert children == sorted(ids)  # [1, 5, 50, 100, 1000]


def test_get_children_sorted_with_negative_ids(relation_index):
    """Проверяет сортировку с отрицательными ID (если такое возможно)."""
    # Arrange
    ids = [5, -1, 3, -10, 0]
    for i in ids:
        relation_index.link(BUILDING, i, COMPLEX, 100)
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert - отрицательные должны быть перед положительными
    assert children == sorted(ids)  # [-10, -1, 0, 3, 5]


def test_get_children_consistency_after_multiple_operations(relation_index):
    """Проверяет, что порядок остаётся отсортированным после операций."""
    # Arrange
    relation_index.link(BUILDING, 5, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    relation_index.link(BUILDING, 7, COMPLEX, 100)
    
    # Initially
    assert relation_index.get_children(COMPLEX, 100) == [2, 5, 7]
    
    # Act - добавляем и удаляем
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.unlink(BUILDING, 5)
    relation_index.link(BUILDING, 3, COMPLEX, 100)
    
    # Assert - всё ещё отсортировано
    assert relation_index.get_children(COMPLEX, 100) == [1, 2, 3, 7]