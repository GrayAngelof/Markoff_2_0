"""
Тест: очистка индекса связей.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR
from client.src.data.graph.relation_index import RelationIndex


def test_clear_removes_all_relations(relation_index):
    """Проверяет, что clear() удаляет все связи."""
    # Arrange - создаём несколько связей
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.link(BUILDING, 2, COMPLEX, 100)
    relation_index.link(FLOOR, 10, BUILDING, 1)
    
    # Act
    relation_index.clear()
    
    # Assert - все связи должны исчезнуть
    assert relation_index.get_parent(BUILDING, 1) is None
    assert relation_index.get_parent(BUILDING, 2) is None
    assert relation_index.get_parent(FLOOR, 10) is None
    assert relation_index.get_children(COMPLEX, 100) == []
    assert relation_index.get_children(BUILDING, 1) == []


def test_clear_on_empty_index(relation_index):
    """Проверяет clear() на пустом индексе."""
    # Act & Assert (не должно быть исключений)
    relation_index.clear()
    
    # Проверяем новую структуру с двумя представлениями
    relations = relation_index.get_all_relations()
    assert relations['children_set'] == {}
    assert relations['children_sorted'] == {}
    assert relations['parents'] == {}


def test_clear_after_operations(relation_index):
    """Проверяет clear() после различных операций."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.unlink(BUILDING, 1)
    relation_index.link(BUILDING, 2, COMPLEX, 200)
    
    # Act
    relation_index.clear()
    
    # Assert - проверяем новую структуру
    relations = relation_index.get_all_relations()
    assert relations['children_set'] == {}
    assert relations['children_sorted'] == {}
    assert relations['parents'] == {}


def test_clear_twice(relation_index):
    """Проверяет повторный clear()."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    
    # Act
    relation_index.clear()
    relation_index.clear()  # Второй раз
    
    # Assert - проверяем новую структуру
    relations = relation_index.get_all_relations()
    assert relations['children_set'] == {}
    assert relations['children_sorted'] == {}
    assert relations['parents'] == {}


def test_clear_and_add_new(relation_index):
    """Проверяет, что после clear() можно создавать новые связи."""
    # Arrange
    relation_index.link(BUILDING, 1, COMPLEX, 100)
    relation_index.clear()
    
    # Act
    relation_index.link(BUILDING, 2, COMPLEX, 200)
    
    # Assert
    assert relation_index.get_parent(BUILDING, 2) == (COMPLEX, 200)
    assert relation_index.get_children(COMPLEX, 200) == [2]
    assert relation_index.get_parent(BUILDING, 1) is None
    
    # Проверяем, что оба представления обновились
    relations = relation_index.get_all_relations()
    
    # В get_all_relations() ключи формируются в нижнем регистре
    complex_key = f"{COMPLEX.value}#200"  # "complex#200"
    building_key = f"{BUILDING.value}#2"   # "building#2"
    
    # Проверяем children индексы
    assert complex_key in relations['children_set']
    assert complex_key in relations['children_sorted']
    assert relations['children_set'][complex_key] == [2]
    assert relations['children_sorted'][complex_key] == [2]
    
    # Проверяем parents индекс
    assert building_key in relations['parents']
    assert relations['parents'][building_key] == complex_key
    
    # Проверяем, что старые связи не восстановились
    old_complex_key = f"{COMPLEX.value}#100"
    old_building_key = f"{BUILDING.value}#1"
    assert old_complex_key not in relations['children_set']
    assert old_complex_key not in relations['children_sorted']
    assert old_building_key not in relations['parents']