"""
Тест: проверка консистентности на корректных данных.
Граф должен быть консистентным после нормальных операций.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_consistency_empty_graph(entity_graph):
    """Проверяет консистентность пустого графа."""
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is True
    assert len(result['issues']) == 0


def test_consistency_single_entity(entity_graph):
    """Проверяет консистентность графа с одной сущностью."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is True
    assert len(result['issues']) == 0


def test_consistency_full_hierarchy(entity_graph):
    """Проверяет консистентность полной иерархии."""
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
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is True
    assert len(result['issues']) == 0


def test_consistency_multiple_branches(entity_graph):
    """Проверяет консистентность графа с несколькими ветками."""
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
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is True
    assert len(result['issues']) == 0


def test_consistency_after_updates(entity_graph):
    """Проверяет консистентность после обновлений."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Обновляем - меняем родителя
    complex_2 = Complex(id=2, name="Другой комплекс", buildings_count=1, address="Другой адрес")
    entity_graph.add_or_update(complex_2)
    
    updated_building = Building(id=1, name="Корпус", complex_id=2, floors_count=1)
    entity_graph.add_or_update(updated_building)
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is True
    assert len(result['issues']) == 0


def test_consistency_after_delete(entity_graph):
    """Проверяет консистентность после удаления."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.remove(BUILDING, 1, cascade=False)  # Building - лист после удаления?
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is True
    assert len(result['issues']) == 0