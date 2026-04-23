"""
Тест: инвалидация и валидация в полной иерархии.
Проверяет все сценарии работы с валидностью.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM


def test_initial_validity(full_graph):
    """Проверяет, что после добавления все сущности валидны."""
    graph = full_graph
    
    # Все сущности должны быть валидны
    assert graph.is_valid(COMPLEX, 1) is True
    assert graph.is_valid(COMPLEX, 2) is True
    assert graph.is_valid(BUILDING, 1) is True
    assert graph.is_valid(BUILDING, 2) is True
    assert graph.is_valid(BUILDING, 3) is True
    assert graph.is_valid(FLOOR, 1) is True
    assert graph.is_valid(FLOOR, 2) is True
    assert graph.is_valid(FLOOR, 3) is True
    assert graph.is_valid(FLOOR, 4) is True
    assert graph.is_valid(ROOM, 1) is True
    assert graph.is_valid(ROOM, 2) is True
    assert graph.is_valid(ROOM, 3) is True
    assert graph.is_valid(ROOM, 4) is True
    assert graph.is_valid(ROOM, 5) is True


def test_invalidate_single_entity(full_graph):
    """Проверяет инвалидацию отдельной сущности."""
    graph = full_graph
    
    # Инвалидируем комнату
    result = graph.invalidate(ROOM, 1)
    
    # Assert
    assert result is True
    assert graph.is_valid(ROOM, 1) is False
    
    # Родители и соседи не должны пострадать
    assert graph.is_valid(FLOOR, 1) is True
    assert graph.is_valid(ROOM, 2) is True
    
    # Повторная инвалидация ничего не меняет
    result = graph.invalidate(ROOM, 1)
    assert result is False
    assert graph.is_valid(ROOM, 1) is False


def test_invalidate_branch_floor(full_graph):
    """Проверяет инвалидацию ветки от этажа."""
    graph = full_graph
    
    # Инвалидируем этаж со всеми комнатами
    count = graph.invalidate_branch(FLOOR, 1)
    
    # Assert - должны инвалидироваться этаж и 2 комнаты
    assert count == 3
    assert graph.is_valid(FLOOR, 1) is False
    assert graph.is_valid(ROOM, 1) is False
    assert graph.is_valid(ROOM, 2) is False
    
    # Проверяем, что параллельные ветки не пострадали
    assert graph.is_valid(FLOOR, 2) is True
    assert graph.is_valid(ROOM, 3) is True
    assert graph.is_valid(BUILDING, 1) is True  # Родитель должен остаться валидным


def test_invalidate_branch_building(full_graph):
    """Проверяет инвалидацию ветки от корпуса."""
    graph = full_graph
    
    # Инвалидируем корпус со всей его иерархией
    count = graph.invalidate_branch(BUILDING, 1)
    
    # Building 1 имеет: 2 этажа + 3 комнаты = 5 + сам building = 6
    assert count == 6
    assert graph.is_valid(BUILDING, 1) is False
    assert graph.is_valid(FLOOR, 1) is False
    assert graph.is_valid(FLOOR, 2) is False
    assert graph.is_valid(ROOM, 1) is False
    assert graph.is_valid(ROOM, 2) is False
    assert graph.is_valid(ROOM, 3) is False
    
    # Другие ветки не пострадали
    assert graph.is_valid(BUILDING, 2) is True
    assert graph.is_valid(FLOOR, 3) is True
    assert graph.is_valid(ROOM, 4) is True
    
    # Родитель (complex) должен остаться валидным
    assert graph.is_valid(COMPLEX, 1) is True


def test_invalidate_branch_complex(full_graph):
    """Проверяет инвалидацию ветки от комплекса."""
    graph = full_graph
    
    # Инвалидируем комплекс со всей иерархией
    count = graph.invalidate_branch(COMPLEX, 1)
    
    # Complex 1 имеет: 2 building + 3 floors + 4 rooms = 9 + сам complex = 10
    assert count == 10
    assert graph.is_valid(COMPLEX, 1) is False
    assert graph.is_valid(BUILDING, 1) is False
    assert graph.is_valid(BUILDING, 2) is False
    assert graph.is_valid(FLOOR, 1) is False
    assert graph.is_valid(FLOOR, 2) is False
    assert graph.is_valid(FLOOR, 3) is False
    assert graph.is_valid(ROOM, 1) is False
    assert graph.is_valid(ROOM, 2) is False
    assert graph.is_valid(ROOM, 3) is False
    assert graph.is_valid(ROOM, 4) is False
    
    # Complex 2 должен остаться валидным
    assert graph.is_valid(COMPLEX, 2) is True
    assert graph.is_valid(BUILDING, 3) is True
    assert graph.is_valid(FLOOR, 4) is True
    assert graph.is_valid(ROOM, 5) is True


def test_validate_after_invalidation(full_graph):
    """Проверяет повторную валидацию после инвалидации."""
    graph = full_graph
    
    # Инвалидируем ветку
    graph.invalidate_branch(FLOOR, 1)
    assert graph.is_valid(FLOOR, 1) is False
    assert graph.is_valid(ROOM, 1) is False
    
    # Валидируем этаж
    graph.validate(FLOOR, 1)
    assert graph.is_valid(FLOOR, 1) is True
    
    # Комнаты должны остаться невалидными (валидация не каскадная)
    assert graph.is_valid(ROOM, 1) is False
    assert graph.is_valid(ROOM, 2) is False
    
    # Валидируем комнаты отдельно
    graph.validate(ROOM, 1)
    graph.validate(ROOM, 2)
    assert graph.is_valid(ROOM, 1) is True
    assert graph.is_valid(ROOM, 2) is True


def test_add_updates_validity(full_graph):
    """Проверяет, что add_or_update восстанавливает валидность."""
    graph = full_graph
    
    # Инвалидируем сущность
    graph.invalidate(ROOM, 1)
    assert graph.is_valid(ROOM, 1) is False
    
    # Обновляем сущность (те же данные)
    from client.src.models import Room
    same_room = Room(id=1, number="101", floor_id=1, area=45.5, status_code="free")
    graph.add_or_update(same_room)
    
    # Должна стать валидной
    assert graph.is_valid(ROOM, 1) is True


def test_remove_updates_validity(full_graph):
    """Проверяет, что после удаления сущность становится невалидной."""
    graph = full_graph
    
    # Удаляем комнату
    graph.remove(ROOM, 1, cascade=False)
    
    # Проверяем валидность
    assert graph.is_valid(ROOM, 1) is False
    # Родитель должен остаться валидным
    assert graph.is_valid(FLOOR, 1) is True