"""
Тест: навигация по графу - получение детей и родителей.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_get_children_of_complex(entity_graph):
    """Проверяет получение детей комплекса (корпуса)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=4)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    
    # Act
    children = entity_graph.get_children(COMPLEX, 1)
    
    # Assert
    assert len(children) == 2
    assert 1 in children
    assert 2 in children


def test_get_children_of_building(entity_graph):
    """Проверяет получение детей корпуса (этажи)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=2)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=0)
    floor_2 = Floor(id=2, number=2, building_id=1, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(floor_2)
    
    # Act
    children = entity_graph.get_children(BUILDING, 1)
    
    # Assert
    assert len(children) == 2
    assert 1 in children
    assert 2 in children


def test_get_children_of_floor(entity_graph):
    """Проверяет получение детей этажа (комнаты)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=2)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    room_2 = Room(id=2, number="102", floor_id=1, area=30.0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    entity_graph.add_or_update(room_2)
    
    # Act
    children = entity_graph.get_children(FLOOR, 1)
    
    # Assert
    assert len(children) == 2
    assert 1 in children
    assert 2 in children


def test_get_children_of_room(entity_graph):
    """Проверяет получение детей комнаты (пустой список, т.к. это лист)."""
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
    children = entity_graph.get_children(ROOM, 1)
    
    # Assert
    assert children == []


def test_get_children_nonexistent_parent(entity_graph):
    """Проверяет получение детей для несуществующего родителя."""
    # Act
    children = entity_graph.get_children(COMPLEX, 999)
    
    # Assert
    assert children == []


def test_get_children_returns_sorted_ids(entity_graph):
    """Проверяет, что get_children возвращает отсортированные ID (для UI)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=3, address="Адрес")
    
    # Добавляем корпуса в разном порядке
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(Building(id=3, name="Корпус В", complex_id=1, floors_count=1))
    entity_graph.add_or_update(Building(id=1, name="Корпус А", complex_id=1, floors_count=1))
    entity_graph.add_or_update(Building(id=2, name="Корпус Б", complex_id=1, floors_count=1))
    
    # Act
    children = entity_graph.get_children(COMPLEX, 1)
    
    # Assert - должны быть отсортированы по возрастанию
    assert children == [1, 2, 3]


def test_get_parent_of_building(entity_graph):
    """Проверяет получение родителя корпуса (комплекс)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    parent = entity_graph.get_parent(BUILDING, 1)
    
    # Assert
    assert parent is not None
    assert parent[0] == COMPLEX
    assert parent[1] == 1


def test_get_parent_of_floor(entity_graph):
    """Проверяет получение родителя этажа (корпус)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    
    # Act
    parent = entity_graph.get_parent(FLOOR, 1)
    
    # Assert
    assert parent is not None
    assert parent[0] == BUILDING
    assert parent[1] == 1


def test_get_parent_of_room(entity_graph):
    """Проверяет получение родителя комнаты (этаж)."""
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
    parent = entity_graph.get_parent(ROOM, 1)
    
    # Assert
    assert parent is not None
    assert parent[0] == FLOOR
    assert parent[1] == 1


def test_get_parent_of_complex(entity_graph):
    """Проверяет получение родителя комплекса (должен быть None, т.к. это корень)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Act
    parent = entity_graph.get_parent(COMPLEX, 1)
    
    # Assert
    assert parent is None


def test_get_parent_nonexistent_child(entity_graph):
    """Проверяет получение родителя для несуществующего потомка."""
    # Act
    parent = entity_graph.get_parent(BUILDING, 999)
    
    # Assert
    assert parent is None


def test_get_parent_after_update(entity_graph):
    """Проверяет, что родитель корректно обновляется при смене родителя."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=2, name="Комплекс 2", buildings_count=1, address="Адрес 2")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    entity_graph.add_or_update(building_1)
    
    # Проверяем начального родителя
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    
    # Act - меняем родителя
    updated_building = Building(id=1, name="Корпус", complex_id=2, floors_count=3)
    entity_graph.add_or_update(updated_building)
    
    # Assert
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 2)


def test_get_parent_after_remove(entity_graph):
    """Проверяет, что после удаления сущности родитель не находится."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.remove(BUILDING, 1)
    
    # Act
    parent = entity_graph.get_parent(BUILDING, 1)
    
    # Assert
    assert parent is None


def test_navigation_full_hierarchy(entity_graph):
    """Проверяет навигацию по полной иерархии во всех направлениях."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act & Assert - навигация сверху вниз
    assert entity_graph.get_children(COMPLEX, 1) == [1]
    assert entity_graph.get_children(BUILDING, 1) == [1]
    assert entity_graph.get_children(FLOOR, 1) == [1]
    assert entity_graph.get_children(ROOM, 1) == []
    
    # Act & Assert - навигация снизу вверх
    assert entity_graph.get_parent(ROOM, 1) == (FLOOR, 1)
    assert entity_graph.get_parent(FLOOR, 1) == (BUILDING, 1)
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    assert entity_graph.get_parent(COMPLEX, 1) is None


def test_get_children_with_multiple_parents(entity_graph):
    """Проверяет получение детей для нескольких родителей одновременно."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=2, name="Комплекс 2", buildings_count=1, address="Адрес 2")
    
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=4)
    building_3 = Building(id=3, name="Корпус В", complex_id=2, floors_count=5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    entity_graph.add_or_update(building_3)
    
    # Act & Assert
    assert set(entity_graph.get_children(COMPLEX, 1)) == {1, 2}
    assert entity_graph.get_children(COMPLEX, 2) == [3]
    assert entity_graph.get_children(COMPLEX, 3) == []