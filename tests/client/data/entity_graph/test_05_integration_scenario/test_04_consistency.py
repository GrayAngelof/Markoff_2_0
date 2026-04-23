"""
Тест: консистентность графа после различных операций.
Проверяет, что система остаётся консистентной.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Room, Building


def test_consistency_after_initial_build(full_graph):
    """Проверяет консистентность после создания иерархии."""
    graph = full_graph
    
    # Проверяем консистентность
    result = graph.check_consistency()
    assert result['consistent'] is True, f"Inconsistencies: {result['issues']}"


def test_consistency_after_updates(full_graph):
    """Проверяет консистентность после обновлений."""
    graph = full_graph
    
    # Серия обновлений
    # 1. Меняем родителя у комнаты
    updated_room = Room(id=1, number="101", floor_id=2, area=45.5, status_code="free")
    graph.add_or_update(updated_room)
    
    # 2. Меняем родителя у корпуса
    updated_building = Building(id=2, name="Корпус Б", complex_id=2, floors_count=1)
    graph.add_or_update(updated_building)
    
    # Проверяем консистентность
    result = graph.check_consistency()
    assert result['consistent'] is True, f"Inconsistencies: {result['issues']}"
    
    # Дополнительно проверяем, что связи обновились правильно
    assert graph.get_parent(ROOM, 1) == (FLOOR, 2)
    assert graph.get_parent(BUILDING, 2) == (COMPLEX, 2)


def test_consistency_after_invalidation(full_graph):
    """Проверяет консистентность после инвалидации."""
    graph = full_graph
    
    # Инвалидируем ветку
    graph.invalidate_branch(FLOOR, 1)
    
    # Инвалидация не должна влиять на структуру графа
    result = graph.check_consistency()
    assert result['consistent'] is True, f"Inconsistencies: {result['issues']}"
    
    # Проверяем, что связи сохранились
    assert graph.get_parent(ROOM, 1) == (FLOOR, 1)
    assert 1 in graph.get_children(FLOOR, 1)


def test_consistency_after_deletions(full_graph):
    """Проверяет консистентность после удалений."""
    graph = full_graph
    
    # Серия удалений
    graph.remove(ROOM, 1, cascade=False)     # удаляем комнату
    graph.remove(FLOOR, 2, cascade=True)     # удаляем этаж с комнатой
    graph.remove(BUILDING, 2, cascade=True)  # удаляем корпус с этажом
    
    # Проверяем консистентность
    result = graph.check_consistency()
    assert result['consistent'] is True, f"Inconsistencies: {result['issues']}"
    
    # Проверяем, что оставшиеся связи корректны
    # Complex 1 должен иметь только Building 1
    assert set(graph.get_children(COMPLEX, 1)) == {1}
    
    # Building 1 должен иметь только Floor 1 (Floor 2 удалён)
    assert set(graph.get_children(BUILDING, 1)) == {1}
    
    # Floor 1 должен иметь только Room 2 (Room 1 удалена)
    assert set(graph.get_children(FLOOR, 1)) == {2}


def test_consistency_after_mixed_operations(full_graph):
    """Проверяет консистентность после смешанных операций."""
    graph = full_graph
    
    # Комплексные операции
    # 1. Обновляем
    updated_room = Room(id=3, number="201-NEW", floor_id=2, area=40.0, status_code="maintenance")
    graph.add_or_update(updated_room)
    
    # 2. Инвалидируем
    graph.invalidate_branch(FLOOR, 1)
    
    # 3. Удаляем
    graph.remove(ROOM, 4, cascade=False)  # Room 301
    
    # 4. Перемещаем
    moved_building = Building(id=1, name="Корпус А (перемещён)", complex_id=2, floors_count=2)
    graph.add_or_update(moved_building)
    
    # Проверяем консистентность
    result = graph.check_consistency()
    assert result['consistent'] is True, f"Inconsistencies: {result['issues']}"
    
    # Проверяем финальное состояние
    # Building 1 теперь должен быть в Complex 2
    assert graph.get_parent(BUILDING, 1) == (COMPLEX, 2)
    assert 1 in graph.get_children(COMPLEX, 2)
    assert 1 not in graph.get_children(COMPLEX, 1)
    
    # Его дети должны остаться при нём
    assert set(graph.get_children(BUILDING, 1)) == {1, 2}


def test_consistency_after_clear(full_graph):
    """Проверяет консистентность после полной очистки."""
    graph = full_graph
    
    # Очищаем граф
    graph.clear()
    
    # Проверяем консистентность пустого графа
    result = graph.check_consistency()
    assert result['consistent'] is True
    
    # Проверяем, что все индексы пусты
    assert graph.get_stats()['total_entities'] == 0
    assert graph.get_all(COMPLEX) == []
    assert graph.get_all(BUILDING) == []
    assert graph.get_all(FLOOR) == []
    assert graph.get_all(ROOM) == []


def test_invariants_after_all_operations(full_graph):
    """Проверяет архитектурные инварианты после всех операций."""
    graph = full_graph
    
    # Выполняем серию операций
    graph.remove(ROOM, 1, cascade=False)
    graph.invalidate_branch(FLOOR, 2)
    graph.remove(FLOOR, 3, cascade=True)
    updated_building = Building(id=1, name="Обновлённый", complex_id=2, floors_count=2)
    graph.add_or_update(updated_building)
    
    # Проверяем Инвариант 1: симметричность связей
    for child_type in [BUILDING, FLOOR, ROOM]:
        parents = graph._relations._parents.get(child_type, {})
        for child_id, (parent_type, parent_id) in parents.items():
            children = graph._relations.get_children(parent_type, parent_id)
            assert child_id in children, f"Invariant 1 failed: {child_type}#{child_id}"
    
    # Проверяем Инвариант 2: сущности в store имеют индексы
    for node_type in [COMPLEX, BUILDING, FLOOR, ROOM]:
        for entity_id in graph._store.get_all_ids(node_type):
            # Для не-корней должен быть родитель
            if node_type != COMPLEX:
                parent = graph._relations.get_parent(node_type, entity_id)
                assert parent is not None, f"Invariant 2 failed: {node_type}#{entity_id}"
            
            # Должен быть флаг валидности
            assert graph._validity.is_valid(node_type, entity_id) in (True, False)
    
    # Проверяем Инвариант 3: все дети в children существуют в store
    for parent_type in [COMPLEX, BUILDING, FLOOR]:
        children_dict = graph._relations._children_set.get(parent_type, {})
        for parent_id, children in children_dict.items():
            for child_id in children:
                child_type = {
                    COMPLEX: BUILDING,
                    BUILDING: FLOOR,
                    FLOOR: ROOM
                }[parent_type]
                assert graph._store.has(child_type, child_id), \
                    f"Invariant 3 failed: {child_type}#{child_id} of {parent_type}#{parent_id}"