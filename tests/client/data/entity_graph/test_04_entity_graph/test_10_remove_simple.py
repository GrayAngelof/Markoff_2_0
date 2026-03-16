"""
Тест: простое удаление сущности (без каскада).
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_remove_complex(entity_graph):
    """Проверяет удаление комплекса."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    assert entity_graph.has_entity(COMPLEX, 1) is True
    
    # Act
    result = entity_graph.remove(COMPLEX, 1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(COMPLEX, 1) is False
    assert entity_graph.get(COMPLEX, 1) is None


def test_remove_building(entity_graph):
    """Проверяет удаление корпуса."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    assert entity_graph.has_entity(BUILDING, 1) is True
    
    # Act
    result = entity_graph.remove(BUILDING, 1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(BUILDING, 1) is False
    assert entity_graph.get(BUILDING, 1) is None
    
    # Комплекс должен остаться
    assert entity_graph.has_entity(COMPLEX, 1) is True


def test_remove_floor(entity_graph):
    """Проверяет удаление этажа."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    assert entity_graph.has_entity(FLOOR, 1) is True
    
    # Act
    result = entity_graph.remove(FLOOR, 1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(FLOOR, 1) is False
    
    # Вышестоящие должны остаться
    assert entity_graph.has_entity(COMPLEX, 1) is True
    assert entity_graph.has_entity(BUILDING, 1) is True


def test_remove_room(entity_graph):
    """Проверяет удаление комнаты."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    assert entity_graph.has_entity(ROOM, 1) is True
    
    # Act
    result = entity_graph.remove(ROOM, 1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(ROOM, 1) is False
    
    # Вышестоящие должны остаться
    assert entity_graph.has_entity(COMPLEX, 1) is True
    assert entity_graph.has_entity(BUILDING, 1) is True
    assert entity_graph.has_entity(FLOOR, 1) is True


def test_remove_updates_validity(entity_graph):
    """Проверяет, что после удаления сущность становится невалидной."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    assert entity_graph.is_valid(COMPLEX, 1) is True
    
    # Act
    entity_graph.remove(COMPLEX, 1)
    
    # Assert
    assert entity_graph.is_valid(COMPLEX, 1) is False