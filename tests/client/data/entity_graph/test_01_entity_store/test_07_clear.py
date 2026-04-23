"""
Тест: очистка хранилища.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_clear_empties_all_types(entity_store):
    """Проверяет, что clear() очищает все типы сущностей."""
    # Arrange - создаём по одной сущности каждого типа со ВСЕМИ обязательными полями
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    building_1 = Building(
        id=1, 
        name="Б1", 
        complex_id=1, 
        floors_count=3,  # Обязательное поле!
        description="Тестовый корпус"
    )
    
    floor_1 = Floor(
        id=1, 
        number=1, 
        building_id=1, 
        rooms_count=5,  # Обязательное поле!
        description="Тестовый этаж"
    )
    
    room_1 = Room(
        id=1, 
        number="101", 
        floor_id=1, 
        area=25.5,
        status_code="free"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(BUILDING, 1, building_1)
    entity_store.put(FLOOR, 1, floor_1)
    entity_store.put(ROOM, 1, room_1)
    
    # Act
    entity_store.clear()
    
    # Assert
    assert entity_store.size() == 0
    assert entity_store.get_all(COMPLEX) == []
    assert entity_store.get_all(BUILDING) == []
    assert entity_store.get_all(FLOOR) == []
    assert entity_store.get_all(ROOM) == []


def test_clear_on_empty_store(entity_store):
    """Проверяет, что clear() на пустом хранилище работает без ошибок."""
    # Act & Assert (не должно быть исключений)
    entity_store.clear()
    assert entity_store.size() == 0


def test_clear_after_remove(entity_store):
    """Проверяет clear() после удаления."""
    # Arrange - создаём и удаляем комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.remove(COMPLEX, 1)
    
    # Act
    entity_store.clear()
    
    # Assert
    assert entity_store.size() == 0


def test_clear_resets_timestamps(entity_store):
    """Проверяет, что clear() очищает временные метки."""
    # Arrange - создаём комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    
    # Проверяем, что timestamp есть
    assert entity_store.get_timestamp(COMPLEX, 1) is not None
    
    # Act
    entity_store.clear()
    
    # Assert
    assert entity_store.get_timestamp(COMPLEX, 1) is None


def test_clear_with_multiple_entities(entity_store):
    """Проверяет clear() с несколькими сущностями одного типа."""
    # Arrange - создаём несколько комплексов
    for i in range(1, 4):
        entity_store.put(
            COMPLEX, 
            i, 
            Complex(
                id=i, 
                name=f"К{i}", 
                buildings_count=i,  # Обязательное поле!
                address=f"А{i}"
            )
        )
    
    assert entity_store.size() == 3
    
    # Act
    entity_store.clear()
    
    # Assert
    assert entity_store.size() == 0
    for i in range(1, 4):
        assert entity_store.has(COMPLEX, i) is False


def test_clear_twice(entity_store):
    """Проверяет, что повторный clear() работает без ошибок."""
    # Arrange - создаём комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    
    # Act
    entity_store.clear()
    entity_store.clear()  # Второй раз
    
    # Assert
    assert entity_store.size() == 0