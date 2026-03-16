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


def test_get_children_returns_sorted_by_id(relation_index):
    """
    Проверяет, что get_children() возвращает детей, отсортированных по ID.
    
    Требование UI - дети должны отображаться в отсортированном порядке.
    """
    # Arrange
    ids = [3, 1, 4, 2]
    for i in ids:
        relation_index.link(BUILDING, i, COMPLEX, 100)
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert - UI ожидает сортировку по возрастанию ID
    assert children == [1, 2, 3, 4]


def test_get_children_sorted_with_large_numbers(relation_index):
    """Проверяет сортировку с большими числами."""
    # Arrange
    ids = [100, 5, 1000, 50, 1]
    for i in ids:
        relation_index.link(BUILDING, i, COMPLEX, 100)
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert - сортировка по возрастанию
    assert children == [1, 5, 50, 100, 1000]


def test_get_children_sorted_with_negative_ids(relation_index):
    """Проверяет сортировку с отрицательными ID."""
    # Arrange
    ids = [5, -1, 3, -10, 0]
    for i in ids:
        relation_index.link(BUILDING, i, COMPLEX, 100)
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert - отрицательные перед положительными, по возрастанию
    assert children == [-10, -1, 0, 3, 5]


def test_get_children_sorted_after_operations(relation_index):
    """Проверяет, что сортировка сохраняется после добавления и удаления."""
    # Arrange
    relation_index.link(BUILDING, 5, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    relation_index.link(BUILDING, 7, COMPLEX, 100)
    
    # Initially - должно быть отсортировано
    assert relation_index.get_children(COMPLEX, 100) == [2, 5, 7]
    
    # Act - добавляем и удаляем
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.unlink(BUILDING, 5)
    relation_index.link(BUILDING, 3, COMPLEX, 100)
    
    # Assert - результат должен быть отсортирован
    assert relation_index.get_children(COMPLEX, 100) == [1, 2, 3, 7]


def test_get_children_no_duplicates(relation_index):
    """Проверяет, что в результате нет дубликатов."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 1, COMPLEX, 100)  # повторная линковка
    
    # Act
    children = relation_index.get_children(COMPLEX, 100)
    
    # Assert - дубликатов быть не должно
    assert children == [1]
    assert len(children) == 1


def test_get_children_unordered_for_internal_use(relation_index):
    """
    Проверяет, что можно получить неупорядоченный список для внутренних операций.
    Это быстрее, когда порядок не важен.
    """
    # Arrange
    ids = [3, 1, 4, 2]
    for i in ids:
        relation_index.link(BUILDING, i, COMPLEX, 100)
    
    # Act - запрашиваем неупорядоченный список
    children_unordered = relation_index.get_children(COMPLEX, 100, ordered=False)
    children_ordered = relation_index.get_children(COMPLEX, 100, ordered=True)
    
    # Assert
    # Неупорядоченный может быть в любом порядке, но должен содержать все ID
    assert set(children_unordered) == {1, 2, 3, 4}
    assert len(children_unordered) == 4
    
    # Упорядоченный должен быть отсортирован
    assert children_ordered == [1, 2, 3, 4]