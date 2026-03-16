"""
Тест: каскадное удаление (удаление родителя вместе со всеми детьми).
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_remove_complex_cascade(entity_graph):
    """Проверяет каскадное удаление комплекса со всей иерархией."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=2)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    floor_2 = Floor(id=2, number=2, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    room_2 = Room(id=2, number="201", floor_id=2, area=30.0)
    
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=1)
    floor_3 = Floor(id=3, number=1, building_id=2, rooms_count=1)
    room_3 = Room(id=3, number="101", floor_id=3, area=35.0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(floor_2)
    entity_graph.add_or_update(floor_3)
    entity_graph.add_or_update(room_1)
    entity_graph.add_or_update(room_2)
    entity_graph.add_or_update(room_3)
    
    # Act - каскадное удаление комплекса
    result = entity_graph.remove(COMPLEX, 1, cascade=True)
    
    # Assert
    assert result is True
    
    # Все сущности должны быть удалены
    assert entity_graph.has_entity(COMPLEX, 1) is False
    assert entity_graph.has_entity(BUILDING, 1) is False
    assert entity_graph.has_entity(BUILDING, 2) is False
    assert entity_graph.has_entity(FLOOR, 1) is False
    assert entity_graph.has_entity(FLOOR, 2) is False
    assert entity_graph.has_entity(FLOOR, 3) is False
    assert entity_graph.has_entity(ROOM, 1) is False
    assert entity_graph.has_entity(ROOM, 2) is False
    assert entity_graph.has_entity(ROOM, 3) is False
    
    # Проверяем, что индексы связей тоже очищены
    assert entity_graph.get_children(COMPLEX, 1) == []
    assert entity_graph.get_parent(BUILDING, 1) is None


def test_remove_building_cascade(entity_graph):
    """Проверяет каскадное удаление корпуса со своими этажами и комнатами."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=2)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    floor_2 = Floor(id=2, number=2, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    room_2 = Room(id=2, number="201", floor_id=2, area=30.0)
    
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=1)
    floor_3 = Floor(id=3, number=1, building_id=2, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(floor_2)
    entity_graph.add_or_update(floor_3)
    entity_graph.add_or_update(room_1)
    entity_graph.add_or_update(room_2)
    
    # Act - каскадное удаление building_1
    result = entity_graph.remove(BUILDING, 1, cascade=True)
    
    # Assert
    assert result is True
    
    # Building_1 и его дети должны быть удалены
    assert entity_graph.has_entity(BUILDING, 1) is False
    assert entity_graph.has_entity(FLOOR, 1) is False
    assert entity_graph.has_entity(FLOOR, 2) is False
    assert entity_graph.has_entity(ROOM, 1) is False
    assert entity_graph.has_entity(ROOM, 2) is False
    
    # Building_2 и его дети должны остаться
    assert entity_graph.has_entity(COMPLEX, 1) is True
    assert entity_graph.has_entity(BUILDING, 2) is True
    assert entity_graph.has_entity(FLOOR, 3) is True
    
    # Проверяем связи
    assert entity_graph.get_children(COMPLEX, 1) == [2]  # Только building_2 остался
    assert entity_graph.get_parent(BUILDING, 2) == (COMPLEX, 1)
    assert entity_graph.get_parent(FLOOR, 3) == (BUILDING, 2)


def test_remove_floor_cascade(entity_graph):
    """Проверяет каскадное удаление этажа со своими комнатами."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=2)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=2)
    floor_2 = Floor(id=2, number=2, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    room_2 = Room(id=2, number="102", floor_id=1, area=30.0)
    room_3 = Room(id=3, number="201", floor_id=2, area=35.0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(floor_2)
    entity_graph.add_or_update(room_1)
    entity_graph.add_or_update(room_2)
    entity_graph.add_or_update(room_3)
    
    # Act - каскадное удаление floor_1
    result = entity_graph.remove(FLOOR, 1, cascade=True)
    
    # Assert
    assert result is True
    
    # Floor_1 и его комнаты должны быть удалены
    assert entity_graph.has_entity(FLOOR, 1) is False
    assert entity_graph.has_entity(ROOM, 1) is False
    assert entity_graph.has_entity(ROOM, 2) is False
    
    # Остальное должно сохраниться
    assert entity_graph.has_entity(COMPLEX, 1) is True
    assert entity_graph.has_entity(BUILDING, 1) is True
    assert entity_graph.has_entity(FLOOR, 2) is True
    assert entity_graph.has_entity(ROOM, 3) is True
    
    # Проверяем связи
    assert entity_graph.get_children(BUILDING, 1) == [2]  # Только floor_2 остался
    assert entity_graph.get_parent(FLOOR, 2) == (BUILDING, 1)
    assert entity_graph.get_parent(ROOM, 3) == (FLOOR, 2)


def test_remove_cascade_on_leaf(entity_graph):
    """Проверяет каскадное удаление на листовом узле (должно работать как обычное удаление)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act - каскадное удаление комнаты (листа)
    result = entity_graph.remove(ROOM, 1, cascade=True)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(ROOM, 1) is False
    assert entity_graph.has_entity(FLOOR, 1) is True  # Родитель должен остаться


def test_remove_cascade_twice(entity_graph):
    """Проверяет повторное каскадное удаление (должно возвращать False)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    first_remove = entity_graph.remove(COMPLEX, 1, cascade=True)
    second_remove = entity_graph.remove(COMPLEX, 1, cascade=True)
    
    # Assert
    assert first_remove is True
    assert second_remove is False