"""
Тест: валидность данных в графе.
Проверяет механизмы пометки сущностей как валидных/невалидных.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_is_valid_after_add(entity_graph):
    """Проверяет, что после добавления сущность становится валидной."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    
    # Act
    entity_graph.add_or_update(complex_1)
    
    # Assert
    assert entity_graph.is_valid(COMPLEX, 1) is True


def test_is_valid_for_nonexistent(entity_graph):
    """Проверяет is_valid для несуществующей сущности."""
    # Act & Assert
    assert entity_graph.is_valid(COMPLEX, 999) is False


def test_invalidate_entity(entity_graph):
    """Проверяет инвалидацию отдельной сущности."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    assert entity_graph.is_valid(COMPLEX, 1) is True
    
    # Act
    result = entity_graph.invalidate(COMPLEX, 1)
    
    # Assert
    assert result is True
    assert entity_graph.is_valid(COMPLEX, 1) is False


def test_invalidate_nonexistent(entity_graph):
    """Проверяет инвалидацию несуществующей сущности."""
    # Act
    result = entity_graph.invalidate(COMPLEX, 999)
    
    # Assert
    assert result is False


def test_invalidate_already_invalid(entity_graph):
    """Проверяет повторную инвалидацию уже невалидной сущности."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    entity_graph.invalidate(COMPLEX, 1)
    
    # Act
    result = entity_graph.invalidate(COMPLEX, 1)
    
    # Assert
    assert result is False  # Статус не изменился
    assert entity_graph.is_valid(COMPLEX, 1) is False


def test_validate_entity(entity_graph):
    """Проверяет повторную валидацию сущности."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    entity_graph.invalidate(COMPLEX, 1)
    assert entity_graph.is_valid(COMPLEX, 1) is False
    
    # Act
    entity_graph.validate(COMPLEX, 1)
    
    # Assert
    assert entity_graph.is_valid(COMPLEX, 1) is True


def test_validate_already_valid(entity_graph):
    """Проверяет валидацию уже валидной сущности (не должно быть ошибки)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    assert entity_graph.is_valid(COMPLEX, 1) is True
    
    # Act
    entity_graph.validate(COMPLEX, 1)  # Не должно быть исключений
    
    # Assert
    assert entity_graph.is_valid(COMPLEX, 1) is True


def test_validate_nonexistent(entity_graph):
    """Проверяет валидацию несуществующей сущности (не должно быть ошибки)."""
    # Act
    entity_graph.validate(COMPLEX, 999)  # Не должно быть исключений
    
    # Assert
    assert entity_graph.is_valid(COMPLEX, 999) is False


def test_invalidate_branch_root(entity_graph):
    """Проверяет инвалидацию всей ветки от корня."""
    # Arrange - создаём иерархию
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Все валидны после добавления
    assert entity_graph.is_valid(COMPLEX, 1) is True
    assert entity_graph.is_valid(BUILDING, 1) is True
    assert entity_graph.is_valid(FLOOR, 1) is True
    assert entity_graph.is_valid(ROOM, 1) is True
    
    # Act - инвалидируем комплекс (должен инвалидировать всю ветку)
    count = entity_graph.invalidate_branch(COMPLEX, 1)
    
    # Assert
    assert count == 4  # Все 4 сущности стали невалидными
    assert entity_graph.is_valid(COMPLEX, 1) is False
    assert entity_graph.is_valid(BUILDING, 1) is False
    assert entity_graph.is_valid(FLOOR, 1) is False
    assert entity_graph.is_valid(ROOM, 1) is False


def test_invalidate_branch_mid_level(entity_graph):
    """Проверяет инвалидацию ветки от среднего уровня."""
    # Arrange - создаём иерархию
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act - инвалидируем корпус (должен инвалидировать этаж и комнату)
    count = entity_graph.invalidate_branch(BUILDING, 1)
    
    # Assert
    assert count == 3  # building + floor + room
    assert entity_graph.is_valid(COMPLEX, 1) is True   # Комплекс должен остаться валидным
    assert entity_graph.is_valid(BUILDING, 1) is False
    assert entity_graph.is_valid(FLOOR, 1) is False
    assert entity_graph.is_valid(ROOM, 1) is False


def test_invalidate_branch_leaf(entity_graph):
    """Проверяет инвалидацию листовой сущности (без детей)."""
    # Arrange - создаём иерархию
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Act - инвалидируем комнату (только себя)
    count = entity_graph.invalidate_branch(ROOM, 1)
    
    # Assert
    assert count == 1  # только room
    assert entity_graph.is_valid(COMPLEX, 1) is True
    assert entity_graph.is_valid(BUILDING, 1) is True
    assert entity_graph.is_valid(FLOOR, 1) is True
    assert entity_graph.is_valid(ROOM, 1) is False


def test_invalidate_branch_with_multiple_children(entity_graph):
    """Проверяет инвалидацию ветки с несколькими потомками."""
    # Arrange - создаём иерархию с несколькими ветками
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
    
    # Act - инвалидируем building_1 (должен инвалидировать только свою ветку)
    count = entity_graph.invalidate_branch(BUILDING, 1)
    
    # Assert
    assert count == 5  # building_1 + 2 floors + 2 rooms
    
    # Ветка building_1 должна быть невалидной
    assert entity_graph.is_valid(BUILDING, 1) is False
    assert entity_graph.is_valid(FLOOR, 1) is False
    assert entity_graph.is_valid(FLOOR, 2) is False
    assert entity_graph.is_valid(ROOM, 1) is False
    assert entity_graph.is_valid(ROOM, 2) is False
    
    # Ветка building_2 должна остаться валидной
    assert entity_graph.is_valid(COMPLEX, 1) is True
    assert entity_graph.is_valid(BUILDING, 2) is True
    assert entity_graph.is_valid(FLOOR, 3) is True
    assert entity_graph.is_valid(ROOM, 3) is True


def test_invalidate_branch_already_invalid(entity_graph):
    """Проверяет инвалидацию уже частично невалидной ветки."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Инвалидируем часть ветки вручную
    entity_graph.invalidate(FLOOR, 1)
    assert entity_graph.is_valid(FLOOR, 1) is False
    
    # Act - инвалидируем всю ветку от building
    count = entity_graph.invalidate_branch(BUILDING, 1)
    
    # Assert - должны инвалидироваться только те, что ещё были валидны
    assert count == 2  # building_1 и room_1 (floor_1 уже был невалидным)
    assert entity_graph.is_valid(BUILDING, 1) is False
    assert entity_graph.is_valid(FLOOR, 1) is False  # Уже было
    assert entity_graph.is_valid(ROOM, 1) is False
    assert entity_graph.is_valid(COMPLEX, 1) is True  # Не должно инвалидироваться


def test_validate_after_invalidate_branch(entity_graph):
    """Проверяет, что после инвалидации ветки можно повторно валидировать отдельные сущности."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    # Инвалидируем ветку
    entity_graph.invalidate_branch(BUILDING, 1)
    assert entity_graph.is_valid(BUILDING, 1) is False
    assert entity_graph.is_valid(FLOOR, 1) is False
    assert entity_graph.is_valid(ROOM, 1) is False
    
    # Act - валидируем отдельные сущности
    entity_graph.validate(BUILDING, 1)
    entity_graph.validate(ROOM, 1)
    
    # Assert
    assert entity_graph.is_valid(BUILDING, 1) is True
    assert entity_graph.is_valid(FLOOR, 1) is False  # Остался невалидным
    assert entity_graph.is_valid(ROOM, 1) is True


def test_add_updates_validity(entity_graph):
    """Проверяет, что add_or_update автоматически делает сущность валидной."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    entity_graph.invalidate(COMPLEX, 1)
    assert entity_graph.is_valid(COMPLEX, 1) is False
    
    # Act - повторное добавление той же сущности
    entity_graph.add_or_update(complex_1)
    
    # Assert - должна стать валидной
    assert entity_graph.is_valid(COMPLEX, 1) is True


def test_remove_updates_validity(entity_graph):
    """Проверяет, что после удаления сущность становится невалидной."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    assert entity_graph.is_valid(COMPLEX, 1) is True
    
    # Act
    entity_graph.remove(COMPLEX, 1)
    
    # Assert
    assert entity_graph.is_valid(COMPLEX, 1) is False


def test_clear_resets_validity(entity_graph):
    """Проверяет, что clear() сбрасывает все флаги валидности."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=1)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    entity_graph.clear()
    
    # Assert
    assert entity_graph.is_valid(COMPLEX, 1) is False
    assert entity_graph.is_valid(BUILDING, 1) is False