"""
Тест: навигация по полной иерархии.
Проверяет все виды навигационных запросов.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM


def test_initial_hierarchy_structure(full_graph):
    """Проверяет, что иерархия создалась корректно."""
    graph = full_graph
    
    # Проверяем количество сущностей
    stats = graph.get_stats()
    assert stats['total_entities'] == 14  # 2+3+4+5
    
    # Проверяем наличие всех сущностей
    assert graph.has_entity(COMPLEX, 1) is True
    assert graph.has_entity(COMPLEX, 2) is True
    assert graph.has_entity(BUILDING, 1) is True
    assert graph.has_entity(BUILDING, 2) is True
    assert graph.has_entity(BUILDING, 3) is True
    assert graph.has_entity(FLOOR, 1) is True
    assert graph.has_entity(FLOOR, 2) is True
    assert graph.has_entity(FLOOR, 3) is True
    assert graph.has_entity(FLOOR, 4) is True
    assert graph.has_entity(ROOM, 1) is True
    assert graph.has_entity(ROOM, 2) is True
    assert graph.has_entity(ROOM, 3) is True
    assert graph.has_entity(ROOM, 4) is True
    assert graph.has_entity(ROOM, 5) is True


def test_top_down_navigation(full_graph):
    """Проверяет навигацию сверху вниз."""
    graph = full_graph
    
    # Complex 1 -> Buildings
    complex1_buildings = graph.get_children(COMPLEX, 1)
    assert set(complex1_buildings) == {1, 2}  # Building 1 и 2
    
    # Complex 2 -> Buildings
    complex2_buildings = graph.get_children(COMPLEX, 2)
    assert complex2_buildings == [3]  # Building 3
    
    # Building 1 -> Floors
    building1_floors = graph.get_children(BUILDING, 1)
    assert set(building1_floors) == {1, 2}  # Floor 1 и 2
    
    # Building 2 -> Floors
    building2_floors = graph.get_children(BUILDING, 2)
    assert building2_floors == [3]  # Floor 3
    
    # Building 3 -> Floors
    building3_floors = graph.get_children(BUILDING, 3)
    assert building3_floors == [4]  # Floor 4
    
    # Floor 1 -> Rooms
    floor1_rooms = graph.get_children(FLOOR, 1)
    assert set(floor1_rooms) == {1, 2}  # Room 101 и 102
    
    # Floor 2 -> Rooms
    floor2_rooms = graph.get_children(FLOOR, 2)
    assert floor2_rooms == [3]  # Room 201
    
    # Floor 3 -> Rooms
    floor3_rooms = graph.get_children(FLOOR, 3)
    assert floor3_rooms == [4]  # Room 301
    
    # Floor 4 -> Rooms
    floor4_rooms = graph.get_children(FLOOR, 4)
    assert floor4_rooms == [5]  # Room 401


def test_bottom_up_navigation(full_graph):
    """Проверяет навигацию снизу вверх."""
    graph = full_graph
    
    # Room 101 -> Floor -> Building -> Complex
    assert graph.get_parent(ROOM, 1) == (FLOOR, 1)
    assert graph.get_parent(FLOOR, 1) == (BUILDING, 1)
    assert graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    
    # Room 201 -> Floor -> Building -> Complex
    assert graph.get_parent(ROOM, 3) == (FLOOR, 2)
    assert graph.get_parent(FLOOR, 2) == (BUILDING, 1)
    assert graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    
    # Room 301 -> Floor -> Building -> Complex
    assert graph.get_parent(ROOM, 4) == (FLOOR, 3)
    assert graph.get_parent(FLOOR, 3) == (BUILDING, 2)
    assert graph.get_parent(BUILDING, 2) == (COMPLEX, 1)
    
    # Room 401 -> Floor -> Building -> Complex
    assert graph.get_parent(ROOM, 5) == (FLOOR, 4)
    assert graph.get_parent(FLOOR, 4) == (BUILDING, 3)
    assert graph.get_parent(BUILDING, 3) == (COMPLEX, 2)


def test_ancestors_query(full_graph):
    """Проверяет получение всех предков."""
    graph = full_graph
    
    # Предки Room 201 (id=3)
    ancestors = graph.get_ancestors(ROOM, 3)
    assert len(ancestors) == 3
    assert ancestors[0] == (FLOOR, 2)   # Непосредственный родитель
    assert ancestors[1] == (BUILDING, 1)
    assert ancestors[2] == (COMPLEX, 1)
    
    # Предки Floor 3
    ancestors = graph.get_ancestors(FLOOR, 3)
    assert len(ancestors) == 2
    assert ancestors[0] == (BUILDING, 2)
    assert ancestors[1] == (COMPLEX, 1)
    
    # Предки Building 3
    ancestors = graph.get_ancestors(BUILDING, 3)
    assert len(ancestors) == 1
    assert ancestors[0] == (COMPLEX, 2)


def test_descendants_query(full_graph):
    """Проверяет получение всех потомков."""
    graph = full_graph
    
    # Потомки Complex 1
    descendants = graph.get_descendants(COMPLEX, 1)
    assert len(descendants[BUILDING]) == 2  # Building 1,2
    assert len(descendants[FLOOR]) == 3     # Floors 1,2,3
    assert len(descendants[ROOM]) == 4      # Rooms 1,2,3,4
    
    # Потомки Building 1
    descendants = graph.get_descendants(BUILDING, 1)
    assert len(descendants[FLOOR]) == 2     # Floors 1,2
    assert len(descendants[ROOM]) == 3      # Rooms 1,2,3
    
    # Потомки Floor 1
    descendants = graph.get_descendants(FLOOR, 1)
    assert len(descendants[ROOM]) == 2      # Rooms 1,2


def test_find_by_parent(full_graph):
    """Проверяет поиск детей определённого типа."""
    graph = full_graph
    
    # Все корпуса комплекса 1
    buildings = graph.find_by_parent(COMPLEX, 1, BUILDING)
    assert len(buildings) == 2
    assert {b.id for b in buildings} == {1, 2}
    
    # Все этажи корпуса 1
    floors = graph.find_by_parent(BUILDING, 1, FLOOR)
    assert len(floors) == 2
    assert {f.id for f in floors} == {1, 2}
    
    # Все комнаты этажа 1
    rooms = graph.find_by_parent(FLOOR, 1, ROOM)
    assert len(rooms) == 2
    assert {r.id for r in rooms} == {1, 2}


def test_get_multiple_entities(full_graph):
    """Проверяет получение нескольких сущностей по списку ID."""
    graph = full_graph
    
    # Получаем несколько комнат
    rooms = graph.get_many(ROOM, [1, 3, 5])
    assert len(rooms) == 3
    assert {r.id for r in rooms} == {1, 3, 5}
    
    # Запрашиваем с несуществующим ID
    rooms = graph.get_many(ROOM, [1, 999, 3])
    assert len(rooms) == 2
    assert {r.id for r in rooms} == {1, 3}