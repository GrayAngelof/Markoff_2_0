"""
Инвариант 1: Симметричность связей.

Если child -> parent (есть запись в parents),
то child ∈ children(parent) (должен быть в списке детей родителя).

Это базовый закон графа - связи всегда двунаправленные в индексах.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_invariant_after_add_complex_building(entity_graph):
    """Проверяет инвариант после добавления связи комплекс-корпус."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    # Act
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Assert - проверяем инвариант
    # Из parents следует наличие в children
    parent_info = entity_graph._relations.get_parent(BUILDING, 1)
    assert parent_info == (COMPLEX, 1)
    
    children = entity_graph._relations.get_children(COMPLEX, 1)
    assert 1 in children
    
    # Проверяем через оба представления RelationIndex
    assert 1 in entity_graph._relations._children_set[COMPLEX][1]
    assert 1 in entity_graph._relations._children_sorted[COMPLEX][1]


def test_invariant_after_add_building_floor(entity_graph):
    """Проверяет инвариант после добавления связи корпус-этаж."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=0)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    entity_graph.add_or_update(floor_1)
    
    # Assert
    parent_info = entity_graph._relations.get_parent(FLOOR, 1)
    assert parent_info == (BUILDING, 1)
    
    children = entity_graph._relations.get_children(BUILDING, 1)
    assert 1 in children


def test_invariant_after_add_floor_room(entity_graph):
    """Проверяет инвариант после добавления связи этаж-комната."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    
    # Act
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    entity_graph.add_or_update(room_1)
    
    # Assert
    parent_info = entity_graph._relations.get_parent(ROOM, 1)
    assert parent_info == (FLOOR, 1)
    
    children = entity_graph._relations.get_children(FLOOR, 1)
    assert 1 in children


def test_invariant_after_update_parent(entity_graph):
    """Проверяет, что инвариант сохраняется при смене родителя."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=2, name="Комплекс 2", buildings_count=1, address="Адрес 2")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    entity_graph.add_or_update(building_1)
    
    # Проверяем начальное состояние
    assert entity_graph._relations.get_parent(BUILDING, 1) == (COMPLEX, 1)
    assert 1 in entity_graph._relations.get_children(COMPLEX, 1)
    assert 1 not in entity_graph._relations.get_children(COMPLEX, 2)
    
    # Act - меняем родителя
    updated_building = Building(id=1, name="Корпус", complex_id=2, floors_count=3)
    entity_graph.add_or_update(updated_building)
    
    # Assert - инвариант сохранился для нового родителя
    assert entity_graph._relations.get_parent(BUILDING, 1) == (COMPLEX, 2)
    assert 1 in entity_graph._relations.get_children(COMPLEX, 2)
    
    # И для старого родителя связь разорвана
    assert 1 not in entity_graph._relations.get_children(COMPLEX, 1)


def test_invariant_after_remove_child(entity_graph):
    """Проверяет, что после удаления ребёнка инвариант сохраняется."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act - удаляем корпус
    entity_graph.remove(BUILDING, 1, cascade=True)
    
    # Assert - у building больше нет родителя
    assert entity_graph._relations.get_parent(BUILDING, 1) is None
    
    # У complex больше нет этого ребёнка
    assert 1 not in entity_graph._relations.get_children(COMPLEX, 1)


def test_invariant_for_multiple_children(entity_graph):
    """Проверяет инвариант для нескольких детей одного родителя."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=4)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    
    # Assert
    for building_id in [1, 2]:
        parent = entity_graph._relations.get_parent(BUILDING, building_id)
        assert parent == (COMPLEX, 1)
        assert building_id in entity_graph._relations.get_children(COMPLEX, 1)


def test_invariant_after_clear(entity_graph):
    """Проверяет, что после очистки графа инвариант выполняется тривиально."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    entity_graph.clear()
    
    # Assert - нет родителей, нет детей
    assert entity_graph._relations.get_parent(BUILDING, 1) is None
    assert entity_graph._relations.get_children(COMPLEX, 1) == []