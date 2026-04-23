"""
Тест: добавление сущности в граф.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_add_complex_entity(entity_graph):
    """Проверяет добавление комплекса в граф."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    
    # Act
    result = entity_graph.add_or_update(complex_1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(COMPLEX, 1) is True
    assert entity_graph.get(COMPLEX, 1) is complex_1


def test_add_building_entity(entity_graph):
    """Проверяет добавление корпуса в граф."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=1, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    
    # Act
    result = entity_graph.add_or_update(building_1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(BUILDING, 1) is True
    assert entity_graph.get(BUILDING, 1) is building_1


def test_add_floor_entity(entity_graph):
    """Проверяет добавление этажа в граф."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=1, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    result = entity_graph.add_or_update(floor_1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(FLOOR, 1) is True
    assert entity_graph.get(FLOOR, 1) is floor_1


def test_add_room_entity(entity_graph):
    """Проверяет добавление комнаты в граф."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=1, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    
    # Act
    result = entity_graph.add_or_update(room_1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(ROOM, 1) is True
    assert entity_graph.get(ROOM, 1) is room_1


def test_add_entity_without_parent(entity_graph):
    """Проверяет добавление сущности без родителя (комплекс)."""
    # Act
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    result = entity_graph.add_or_update(complex_1)
    
    # Assert
    assert result is True
    assert entity_graph.get_parent(COMPLEX, 1) is None  # У комплекса нет родителя


def test_add_duplicate_entity(entity_graph):
    """Проверяет повторное добавление той же сущности."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    
    # Act
    first_add = entity_graph.add_or_update(complex_1)
    second_add = entity_graph.add_or_update(complex_1)  # Те же данные
    
    # Assert
    assert first_add is True
    assert second_add is False  # Не изменилась - должно быть проигнорировано
    assert entity_graph.has_entity(COMPLEX, 1) is True