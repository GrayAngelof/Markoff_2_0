"""
Тест: удаление в полной иерархии.
Проверяет все сценарии удаления.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM


def test_delete_leaf_without_cascade(full_graph):
    """Проверяет удаление листового узла (комнаты) без каскада."""
    graph = full_graph
    
    # Запоминаем состояние до удаления
    assert graph.has_entity(ROOM, 1) is True
    floor_id = graph.get_parent(ROOM, 1)[1]
    
    # Act - удаляем комнату (лист)
    result = graph.remove(ROOM, 1, cascade=False)
    
    # Assert
    assert result is True
    assert graph.has_entity(ROOM, 1) is False
    
    # Родитель должен остаться
    assert graph.has_entity(FLOOR, floor_id) is True
    assert 1 not in graph.get_children(FLOOR, floor_id)


def test_delete_parent_without_cascade_forbidden(full_graph):
    """Проверяет, что удаление родителя с детьми без каскада запрещено."""
    graph = full_graph
    
    # Пытаемся удалить этаж, у которого есть комнаты
    assert len(graph.get_children(FLOOR, 1)) == 2  # Есть дети
    
    # Act
    result = graph.remove(FLOOR, 1, cascade=False)
    
    # Assert
    assert result is False
    assert graph.has_entity(FLOOR, 1) is True
    assert graph.has_entity(ROOM, 1) is True
    assert graph.has_entity(ROOM, 2) is True


def test_delete_floor_with_cascade(full_graph):
    """Проверяет каскадное удаление этажа со всеми комнатами."""
    graph = full_graph
    
    # Запоминаем состояние до удаления
    building_id = graph.get_parent(FLOOR, 1)[1]
    rooms_on_floor = graph.get_children(FLOOR, 1)
    
    # Act - каскадное удаление этажа
    result = graph.remove(FLOOR, 1, cascade=True)
    
    # Assert
    assert result is True
    assert graph.has_entity(FLOOR, 1) is False
    
    # Все комнаты удалены
    for room_id in rooms_on_floor:
        assert graph.has_entity(ROOM, room_id) is False
    
    # Родитель (building) должен остаться
    assert graph.has_entity(BUILDING, building_id) is True
    assert 1 not in graph.get_children(BUILDING, building_id)


def test_delete_building_with_cascade(full_graph):
    """Проверяет каскадное удаление корпуса со всеми этажами и комнатами."""
    graph = full_graph
    
    # Запоминаем состояние до удаления
    complex_id = graph.get_parent(BUILDING, 1)[1]
    floors = graph.get_children(BUILDING, 1)
    all_rooms = []
    for floor_id in floors:
        all_rooms.extend(graph.get_children(FLOOR, floor_id))
    
    # Act - каскадное удаление корпуса
    result = graph.remove(BUILDING, 1, cascade=True)
    
    # Assert
    assert result is True
    assert graph.has_entity(BUILDING, 1) is False
    
    # Все этажи удалены
    for floor_id in floors:
        assert graph.has_entity(FLOOR, floor_id) is False
    
    # Все комнаты удалены
    for room_id in all_rooms:
        assert graph.has_entity(ROOM, room_id) is False
    
    # Родитель (complex) должен остаться
    assert graph.has_entity(COMPLEX, complex_id) is True
    assert 1 not in graph.get_children(COMPLEX, complex_id)
    
    # Другие ветки не пострадали
    assert graph.has_entity(BUILDING, 2) is True
    assert graph.has_entity(FLOOR, 3) is True
    assert graph.has_entity(ROOM, 4) is True


def test_delete_complex_with_cascade(full_graph):
    """Проверяет каскадное удаление комплекса со всей иерархией."""
    graph = full_graph
    
    # Запоминаем статистику
    stats_before = graph.get_stats()
    
    # Act - каскадное удаление Complex 2
    result = graph.remove(COMPLEX, 2, cascade=True)
    
    # Assert
    assert result is True
    assert graph.has_entity(COMPLEX, 2) is False
    assert graph.has_entity(BUILDING, 3) is False
    assert graph.has_entity(FLOOR, 4) is False
    assert graph.has_entity(ROOM, 5) is False
    
    # Complex 1 должен остаться нетронутым
    assert graph.has_entity(COMPLEX, 1) is True
    assert graph.has_entity(BUILDING, 1) is True
    assert graph.has_entity(BUILDING, 2) is True
    
    # Проверяем статистику (Complex 2 имел 4 сущности: сам + building + floor + room)
    stats_after = graph.get_stats()
    assert stats_after['total_entities'] == stats_before['total_entities'] - 4


def test_delete_nonexistent(full_graph):
    """Проверяет удаление несуществующей сущности."""
    graph = full_graph
    
    # Act
    result = graph.remove(ROOM, 999, cascade=True)
    
    # Assert
    assert result is False
    
    # Остальные сущности не пострадали
    assert graph.has_entity(COMPLEX, 1) is True
    assert graph.has_entity(ROOM, 1) is True


def test_delete_and_verify_invariants(full_graph):
    """Проверяет инварианты после серии удалений."""
    graph = full_graph
    
    # Серия удалений
    graph.remove(ROOM, 1, cascade=False)      # удаляем комнату
    graph.remove(FLOOR, 2, cascade=True)      # удаляем этаж с комнатой
    graph.remove(BUILDING, 2, cascade=True)   # удаляем корпус с этажом
    
    # Проверяем инварианты вручную
    # 1. Для каждого ребёнка в parents, он должен быть в children родителя
    for child_type in [BUILDING, FLOOR, ROOM]:
        parents = graph._relations._parents.get(child_type, {})
        for child_id, (parent_type, parent_id) in parents.items():
            children = graph._relations.get_children(parent_type, parent_id)
            assert child_id in children
    
    # 2. Все дети в children существуют в store
    for parent_type in [COMPLEX, BUILDING, FLOOR]:
        children_dict = graph._relations._children_set.get(parent_type, {})
        for parent_id, children in children_dict.items():
            for child_id in children:
                child_type = {
                    COMPLEX: BUILDING,
                    BUILDING: FLOOR,
                    FLOOR: ROOM
                }[parent_type]
                assert graph._store.has(child_type, child_id)