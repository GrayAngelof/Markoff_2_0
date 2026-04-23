"""
Тест: получение всех сущностей определённого типа.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_get_all_complexes(entity_graph):
    """Проверяет получение всех комплексов."""
    # Arrange
    complex_1 = Complex(id=1, name="К1", buildings_count=2, address="А1")
    complex_2 = Complex(id=2, name="К2", buildings_count=3, address="А2")
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    
    # Act
    complexes = entity_graph.get_all(COMPLEX)
    
    # Assert
    assert len(complexes) == 2
    assert complex_1 in complexes
    assert complex_2 in complexes


def test_get_all_buildings(entity_graph, sample_hierarchy):
    """Проверяет получение всех корпусов."""
    # Act
    buildings = entity_graph.get_all(BUILDING)
    
    # Assert
    assert len(buildings) == 1
    assert buildings[0].id == 1
    assert buildings[0].name == "Корпус 1"


def test_get_all_floors(entity_graph, sample_hierarchy):
    """Проверяет получение всех этажей."""
    # Act
    floors = entity_graph.get_all(FLOOR)
    
    # Assert
    assert len(floors) == 1
    assert floors[0].id == 1
    assert floors[0].number == 1


def test_get_all_rooms(entity_graph, sample_hierarchy):
    """Проверяет получение всех комнат."""
    # Act
    rooms = entity_graph.get_all(ROOM)
    
    # Assert
    assert len(rooms) == 1
    assert rooms[0].id == 1
    assert rooms[0].number == "101"


def test_get_all_empty_type(entity_graph):
    """Проверяет получение всех сущностей для типа, которого нет."""
    # Act
    result = entity_graph.get_all(BUILDING)
    
    # Assert
    assert result == []


def test_get_all_after_add(entity_graph):
    """Проверяет get_all после добавления новых сущностей."""
    # Arrange
    entity_graph.add_or_update(Complex(id=1, name="К1", buildings_count=2, address="А1"))
    
    # Act
    before = entity_graph.get_all(COMPLEX)
    entity_graph.add_or_update(Complex(id=2, name="К2", buildings_count=3, address="А2"))
    after = entity_graph.get_all(COMPLEX)
    
    # Assert
    assert len(before) == 1
    assert len(after) == 2


def test_get_all_after_remove_with_cascade(entity_graph, sample_hierarchy):
    """Проверяет get_all после каскадного удаления."""
    # Act
    before = entity_graph.get_all(BUILDING)
    # Удаляем с каскадом, так как у building есть дети
    entity_graph.remove(BUILDING, 1, cascade=True)
    after = entity_graph.get_all(BUILDING)
    
    # Assert
    assert len(before) == 1
    assert len(after) == 0
    
    # Проверяем, что дети тоже удалились
    assert len(entity_graph.get_all(FLOOR)) == 0
    assert len(entity_graph.get_all(ROOM)) == 0
    
    # Комплекс должен остаться
    assert len(entity_graph.get_all(COMPLEX)) == 1


def test_get_all_after_remove_leaf(entity_graph, sample_hierarchy):
    """Проверяет get_all после удаления листового узла (без каскада)."""
    # Act
    before = entity_graph.get_all(ROOM)
    # Комната - лист, можно удалять без каскада
    entity_graph.remove(ROOM, 1, cascade=False)
    after = entity_graph.get_all(ROOM)
    
    # Assert
    assert len(before) == 1
    assert len(after) == 0
    
    # Проверяем, что родитель остался
    assert len(entity_graph.get_all(FLOOR)) == 1
    assert len(entity_graph.get_all(BUILDING)) == 1
    assert len(entity_graph.get_all(COMPLEX)) == 1