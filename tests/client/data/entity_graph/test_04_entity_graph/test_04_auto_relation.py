"""
Тест: автоматическое создание связей при добавлении сущности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_add_building_creates_relation(entity_graph):
    """Проверяет, что при добавлении корпуса создаётся связь с комплексом."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=1, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    
    # Act
    entity_graph.add_or_update(building_1)
    
    # Assert
    # Проверяем прямую связь
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    assert 1 in entity_graph.get_children(COMPLEX, 1)
    
    # Проверяем через граф
    children = entity_graph.get_children(COMPLEX, 1)
    assert children == [1]


def test_add_floor_creates_relation(entity_graph):
    """Проверяет, что при добавлении этажа создаётся связь с корпусом."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=1, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    entity_graph.add_or_update(floor_1)
    
    # Assert
    assert entity_graph.get_parent(FLOOR, 1) == (BUILDING, 1)
    assert 1 in entity_graph.get_children(BUILDING, 1)


def test_add_room_creates_relation(entity_graph):
    """Проверяет, что при добавлении комнаты создаётся связь с этажом."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=1, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    
    # Act
    entity_graph.add_or_update(room_1)
    
    # Assert
    assert entity_graph.get_parent(ROOM, 1) == (FLOOR, 1)
    assert 1 in entity_graph.get_children(FLOOR, 1)


def test_update_changes_relation(entity_graph):
    """Проверяет, что при обновлении родителя связь перестраивается."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=2, name="Комплекс 2", buildings_count=1, address="Адрес 2")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    entity_graph.add_or_update(building_1)
    
    # Проверяем начальную связь
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    assert 1 in entity_graph.get_children(COMPLEX, 1)
    assert 1 not in entity_graph.get_children(COMPLEX, 2)
    
    # Act - обновляем building с новым complex_id
    updated_building = Building(id=1, name="Корпус А", complex_id=2, floors_count=3)
    entity_graph.add_or_update(updated_building)
    
    # Assert
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 2)
    assert 1 not in entity_graph.get_children(COMPLEX, 1)
    assert 1 in entity_graph.get_children(COMPLEX, 2)


def test_add_without_parent_no_relation(entity_graph):
    """Проверяет, что у корневой сущности (комплекс) нет родителя."""
    # Act
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    entity_graph.add_or_update(complex_1)
    
    # Assert
    assert entity_graph.get_parent(COMPLEX, 1) is None


def test_full_hierarchy_relations(entity_graph):
    """Проверяет создание полной иерархии связей."""
    # Act
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Assert
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    assert entity_graph.get_parent(FLOOR, 1) == (BUILDING, 1)
    assert entity_graph.get_parent(ROOM, 1) == (FLOOR, 1)
    
    assert entity_graph.get_children(COMPLEX, 1) == [1]
    assert entity_graph.get_children(BUILDING, 1) == [1]
    assert entity_graph.get_children(FLOOR, 1) == [1]