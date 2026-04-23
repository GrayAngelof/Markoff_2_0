"""
Тест: получение всех ID сущностей определённого типа.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_get_all_ids_returns_all_ids(entity_store):
    """Проверяет, что get_all_ids() возвращает все ID типа."""
    # Arrange - создаём три комплекса со ВСЕМИ обязательными полями
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
    complex_3 = Complex(
        id=5, 
        name="К3", 
        buildings_count=1,  # Обязательное поле!
        address="А3"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(COMPLEX, 2, complex_2)
    entity_store.put(COMPLEX, 5, complex_3)
    
    # Act
    result = entity_store.get_all_ids(COMPLEX)
    
    # Assert
    assert len(result) == 3
    assert 1 in result
    assert 2 in result
    assert 5 in result


def test_get_all_ids_returns_empty_list_for_empty_type(entity_store):
    """Проверяет, что get_all_ids() возвращает пустой список для пустого типа."""
    # Act
    result = entity_store.get_all_ids(BUILDING)
    
    # Assert
    assert result == []


def test_get_all_ids_returns_sorted_order(entity_store):
    """Проверяет, что ID возвращаются в порядке добавления."""
    # Arrange
    ids = [3, 1, 4, 2]
    for i in ids:
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
    result = entity_store.get_all_ids(COMPLEX)
    
    # Assert
    assert result == ids  # Должен сохранять порядок вставки


def test_get_all_ids_only_for_type(entity_store):
    """Проверяет, что возвращаются ID только запрошенного типа."""
    # Arrange
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    building_1 = Building(
        id=10, 
        name="Б1", 
        complex_id=1, 
        floors_count=2,  # Обязательное поле!
        description="Тестовый корпус"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(BUILDING, 10, building_1)
    
    # Act
    complex_ids = entity_store.get_all_ids(COMPLEX)
    building_ids = entity_store.get_all_ids(BUILDING)
    
    # Assert
    assert complex_ids == [1]
    assert building_ids == [10]


def test_get_all_ids_with_mixed_types(entity_store):
    """Проверяет get_all_ids() для всех типов сущностей."""
    # Arrange - создаём по одной сущности каждого типа
    complex_1 = Complex(
        id=1, 
        name="Комплекс", 
        buildings_count=1,  # Обязательное поле!
        address="Адрес"
    )
    
    building_1 = Building(
        id=2, 
        name="Корпус", 
        complex_id=1, 
        floors_count=3,  # Обязательное поле!
        description="Описание корпуса"
    )
    
    floor_1 = Floor(
        id=3, 
        number=1, 
        building_id=2, 
        rooms_count=5,  # Обязательное поле!
        description="Описание этажа"
    )
    
    room_1 = Room(
        id=4, 
        number="101", 
        floor_id=3, 
        area=25.5,
        status_code="free"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(BUILDING, 2, building_1)
    entity_store.put(FLOOR, 3, floor_1)
    entity_store.put(ROOM, 4, room_1)
    
    # Act
    complex_ids = entity_store.get_all_ids(COMPLEX)
    building_ids = entity_store.get_all_ids(BUILDING)
    floor_ids = entity_store.get_all_ids(FLOOR)
    room_ids = entity_store.get_all_ids(ROOM)
    
    # Assert
    assert complex_ids == [1]
    assert building_ids == [2]
    assert floor_ids == [3]
    assert room_ids == [4]


def test_get_all_ids_after_remove(entity_store):
    """Проверяет, что get_all_ids() обновляется после удаления."""
    # Arrange
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
    result = entity_store.get_all_ids(COMPLEX)
    
    # Assert
    assert len(result) == 2
    assert 1 in result
    assert 3 in result
    assert 2 not in result