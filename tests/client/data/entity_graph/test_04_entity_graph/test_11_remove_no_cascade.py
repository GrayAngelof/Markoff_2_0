"""
Тест: удаление без каскада (должно быть заблокировано, если есть дети).
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_remove_complex_with_children_no_cascade(entity_graph):
    """Проверяет удаление комплекса с детьми без каскада (должно быть запрещено)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    result = entity_graph.remove(COMPLEX, 1, cascade=False)
    
    # Assert
    assert result is False  # Не должно удалиться, т.к. есть дети
    assert entity_graph.has_entity(COMPLEX, 1) is True
    assert entity_graph.has_entity(BUILDING, 1) is True


def test_remove_building_with_children_no_cascade(entity_graph):
    """Проверяет удаление корпуса с детьми без каскада (должно быть запрещено)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    
    # Act
    result = entity_graph.remove(BUILDING, 1, cascade=False)
    
    # Assert
    assert result is False  # Не должно удалиться, т.к. есть дети
    assert entity_graph.has_entity(BUILDING, 1) is True
    assert entity_graph.has_entity(FLOOR, 1) is True
    assert entity_graph.has_entity(COMPLEX, 1) is True


def test_remove_floor_with_children_no_cascade(entity_graph):
    """Проверяет удаление этажа с детьми без каскада (должно быть запрещено)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act
    result = entity_graph.remove(FLOOR, 1, cascade=False)
    
    # Assert
    assert result is False  # Не должно удалиться, т.к. есть дети
    assert entity_graph.has_entity(FLOOR, 1) is True
    assert entity_graph.has_entity(ROOM, 1) is True


def test_remove_leaf_no_cascade_allowed(entity_graph):
    """Проверяет удаление листового узла (без детей) - должно работать и без каскада."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act - удаляем комнату (лист)
    result = entity_graph.remove(ROOM, 1, cascade=False)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(ROOM, 1) is False
    assert entity_graph.has_entity(FLOOR, 1) is True  # Родитель должен остаться


def test_remove_without_children_no_cascade(entity_graph):
    """Проверяет удаление узла без детей - должно работать без каскада."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=0, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Act
    result = entity_graph.remove(COMPLEX, 1, cascade=False)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(COMPLEX, 1) is False