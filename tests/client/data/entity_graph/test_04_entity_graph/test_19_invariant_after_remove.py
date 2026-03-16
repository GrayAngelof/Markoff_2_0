"""
Инвариант 3: После удаления сущность полностью исчезает из системы.

После remove(entity):
- entity ∉ store
- entity ∉ relations (ни как родитель, ни как потомок)
- entity ∉ validity
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_invariant_after_remove_leaf(entity_graph):
    """Проверяет инвариант после удаления листового узла (комнаты)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act - удаляем комнату
    entity_graph.remove(ROOM, 1, cascade=False)
    
    # Assert - комната не в store
    assert entity_graph._store.has(ROOM, 1) is False
    
    # Не в relations (ни как потомок)
    assert entity_graph._relations.get_parent(ROOM, 1) is None
    
    # Не в children у родителя
    assert 1 not in entity_graph._relations.get_children(FLOOR, 1)
    
    # Не в validity
    assert entity_graph._validity.is_valid(ROOM, 1) is False


def test_invariant_after_remove_branch_without_cascade(entity_graph):
    """Проверяет, что при попытке удалить родителя без каскада - ничего не удаляется."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act - пытаемся удалить building без каскада (должно быть запрещено)
    result = entity_graph.remove(BUILDING, 1, cascade=False)
    
    # Assert - удаление не произошло
    assert result is False
    
    # Все сущности остались в store
    assert entity_graph._store.has(BUILDING, 1) is True
    assert entity_graph._store.has(FLOOR, 1) is True
    assert entity_graph._store.has(ROOM, 1) is True
    
    # Связи сохранились
    assert entity_graph._relations.get_parent(FLOOR, 1) == (BUILDING, 1)
    assert 1 in entity_graph._relations.get_children(BUILDING, 1)


def test_invariant_after_remove_branch_with_cascade(entity_graph):
    """Проверяет инвариант после каскадного удаления ветки."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act - каскадное удаление building
    entity_graph.remove(BUILDING, 1, cascade=True)
    
    # Assert - building и его потомки не в store
    assert entity_graph._store.has(BUILDING, 1) is False
    assert entity_graph._store.has(FLOOR, 1) is False
    assert entity_graph._store.has(ROOM, 1) is False
    
    # Нет в relations
    assert entity_graph._relations.get_parent(BUILDING, 1) is None
    assert entity_graph._relations.get_parent(FLOOR, 1) is None
    assert entity_graph._relations.get_parent(ROOM, 1) is None
    
    # Не в children у родителей
    assert 1 not in entity_graph._relations.get_children(COMPLEX, 1)
    assert 1 not in entity_graph._relations.get_children(BUILDING, 1)
    assert 1 not in entity_graph._relations.get_children(FLOOR, 1)
    
    # Не в validity
    assert entity_graph._validity.is_valid(BUILDING, 1) is False
    assert entity_graph._validity.is_valid(FLOOR, 1) is False
    assert entity_graph._validity.is_valid(ROOM, 1) is False
    
    # Комплекс должен остаться
    assert entity_graph._store.has(COMPLEX, 1) is True


def test_invariant_after_remove_complex_cascade(entity_graph):
    """Проверяет инвариант после каскадного удаления всего графа."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=2)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    floor_2 = Floor(id=2, number=2, building_id=1, rooms_count=1)
    floor_3 = Floor(id=3, number=1, building_id=2, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    room_2 = Room(id=2, number="201", floor_id=2, area=30.0)
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
    entity_graph.remove(COMPLEX, 1, cascade=True)
    
    # Assert - ничего не осталось в store
    assert entity_graph._store.size() == 0
    
    # Все индексы пусты
    relations = entity_graph._relations.get_all_relations()
    assert relations['children_set'] == {}
    assert relations['children_sorted'] == {}
    assert relations['parents'] == {}
    
    # validity пуст
    for node_type in [COMPLEX, BUILDING, FLOOR, ROOM]:
        assert entity_graph._validity.is_valid(node_type, 1) is False
        assert entity_graph._validity.is_valid(node_type, 2) is False
        assert entity_graph._validity.is_valid(node_type, 3) is False


def test_invariant_after_remove_and_reAdd(entity_graph):
    """Проверяет, что после удаления и повторного добавления всё работает."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act - удаляем и добавляем заново
    entity_graph.remove(BUILDING, 1, cascade=True)
    entity_graph.add_or_update(building_1)
    
    # Assert - building снова в store
    assert entity_graph._store.has(BUILDING, 1) is True
    
    # Связь восстановилась
    assert entity_graph._relations.get_parent(BUILDING, 1) == (COMPLEX, 1)
    assert 1 in entity_graph._relations.get_children(COMPLEX, 1)
    
    # Валидность восстановилась
    assert entity_graph._validity.is_valid(BUILDING, 1) is True


def test_invariant_after_remove_nonexistent(entity_graph):
    """Проверяет, что удаление несуществующей сущности не ломает инварианты."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Act - удаляем несуществующее
    result = entity_graph.remove(BUILDING, 999, cascade=True)
    
    # Assert
    assert result is False
    
    # Существующая сущность не пострадала
    assert entity_graph._store.has(COMPLEX, 1) is True
    assert entity_graph._validity.is_valid(COMPLEX, 1) is True
    assert entity_graph._relations.get_parent(COMPLEX, 1) is None