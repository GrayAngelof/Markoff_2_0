"""
Тест: проверка размера хранилища.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_size_empty_store(entity_store):
    """Проверяет size() для пустого хранилища."""
    # Act
    result = entity_store.size()
    
    # Assert
    assert result == 0


def test_size_after_puts(entity_store):
    """Проверяет size() после добавления сущностей."""
    # Arrange - создаём два комплекса со ВСЕМИ обязательными полями
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    complex_2 = Complex(
        id=2, 
        name="К2", 
        buildings_count=3,  # Обязательное поле!
        address="А2"
    )
    
    # Act
    entity_store.put(COMPLEX, 1, complex_1)
    assert entity_store.size() == 1
    
    entity_store.put(COMPLEX, 2, complex_2)
    assert entity_store.size() == 2


def test_size_after_remove(entity_store):
    """Проверяет size() после удаления."""
    # Arrange - создаём три комплекса
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
    
    # Act
    entity_store.remove(COMPLEX, 2)
    
    # Assert
    assert entity_store.size() == 2


def test_size_after_clear(entity_store):
    """Проверяет size() после очистки."""
    # Arrange - создаём три комплекса
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
    
    # Act
    entity_store.clear()
    
    # Assert
    assert entity_store.size() == 0


def test_size_counts_all_types(entity_store):
    """Проверяет, что size() считает все типы сущностей."""
    # Arrange - создаём сущности разных типов
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=1,  # Обязательное поле!
        address="А1"
    )
    
    building_1 = Building(
        id=1, 
        name="Б1", 
        complex_id=1, 
        floors_count=3,  # Обязательное поле!
        description="Тестовый корпус"
    )
    
    building_2 = Building(
        id=2, 
        name="Б2", 
        complex_id=1, 
        floors_count=4,  # Обязательное поле!
        description="Ещё один корпус"
    )
    
    floor_1 = Floor(
        id=1, 
        number=1, 
        building_id=1, 
        rooms_count=5,  # Обязательное поле!
        description="Первый этаж"
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
    entity_store.put(BUILDING, 2, building_2)
    entity_store.put(FLOOR, 1, floor_1)
    entity_store.put(ROOM, 1, room_1)
    
    # Act
    result = entity_store.size()
    
    # Assert
    assert result == 5  # 1 комплекс + 2 корпуса + 1 этаж + 1 комната


def test_size_with_duplicate_puts(entity_store):
    """Проверяет size() при повторном добавлении той же сущности."""
    # Arrange
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    # Act
    entity_store.put(COMPLEX, 1, complex_1)
    first_size = entity_store.size()
    
    entity_store.put(COMPLEX, 1, complex_1)  # Повторное добавление
    second_size = entity_store.size()
    
    # Assert
    assert first_size == 1
    assert second_size == 1  # Размер не должен увеличиться


def test_size_after_multiple_operations(entity_store):
    """Проверяет size() после последовательности операций."""
    # Arrange - создаём несколько сущностей
    complex_1 = Complex(id=1, name="К1", buildings_count=2, address="А1")
    complex_2 = Complex(id=2, name="К2", buildings_count=3, address="А2")
    building_1 = Building(id=1, name="Б1", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Б2", complex_id=1, floors_count=4)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=5)
    room_1 = Room(id=1, number="101", floor_id=1, area=25.5)
    
    # Act & Assert - последовательность операций
    assert entity_store.size() == 0
    
    entity_store.put(COMPLEX, 1, complex_1)
    assert entity_store.size() == 1
    
    entity_store.put(COMPLEX, 2, complex_2)
    assert entity_store.size() == 2
    
    entity_store.put(BUILDING, 1, building_1)
    assert entity_store.size() == 3
    
    entity_store.put(BUILDING, 2, building_2)
    assert entity_store.size() == 4
    
    entity_store.put(FLOOR, 1, floor_1)
    assert entity_store.size() == 5
    
    entity_store.put(ROOM, 1, room_1)
    assert entity_store.size() == 6
    
    entity_store.remove(BUILDING, 1)
    assert entity_store.size() == 5
    
    entity_store.remove(COMPLEX, 1)
    assert entity_store.size() == 4
    
    entity_store.clear()
    assert entity_store.size() == 0